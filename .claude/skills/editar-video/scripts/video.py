#!/usr/bin/env python3
"""Herramientas de edición de video para la skill editar-video.

Subcomandos:
  preparar                         Instala faster-whisper y descarga el modelo.
  info VIDEO                       Duración, resolución, fps, audio.
  audio VIDEO [-o salida.wav]      Extrae el audio (wav 16 kHz mono por defecto, o mp3/m4a según extensión).
  transcribir VIDEO -d DIR [--vocabulario "cuádriceps, ..."]
                                   Audio + transcripción con tiempos por palabra.
                                   Escribe DIR/transcripcion.json, DIR/transcripcion.txt y DIR/audio.wav.
  cortar VIDEO CORTES.json -o OUT  Conserva solo los tramos de CORTES.json y los une.
  subtitulos TRANS.json -o OUT.srt [--cortes CORTES.json] [--palabras N]
                                   Genera SRT; con --cortes reubica los tiempos al video editado.
  quemar VIDEO SUBS.srt -o OUT     Incrusta subtítulos (estilo para vertical).

CORTES.json: lista de tramos A CONSERVAR, en segundos del video original:
  [{"inicio": 0.0, "fin": 4.2}, {"inicio": 6.8, "fin": 12.5}]
"""
import argparse, json, os, subprocess, sys

os.environ.setdefault("HF_HUB_DISABLE_XET", "1")  # descarga por CDN normal (red del entorno)
MODELO = os.environ.get("WHISPER_MODELO", "small")


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"Error ejecutando {' '.join(cmd[:3])}...:\n{r.stderr[-2000:]}")
    return r.stdout


def asegurar_whisper():
    try:
        import faster_whisper  # noqa: F401
    except ImportError:
        print("Instalando faster-whisper...", file=sys.stderr)
        subprocess.run([sys.executable, "-m", "pip", "install", "-q", "faster-whisper"], check=True)


def cargar_modelo(nombre):
    asegurar_whisper()
    from faster_whisper import WhisperModel
    return WhisperModel(nombre, device="cpu", compute_type="int8")


def fmt(t):
    m, s = divmod(t, 60)
    return f"{int(m):02d}:{s:05.2f}"


def info(video):
    d = json.loads(run(["ffprobe", "-v", "error", "-print_format", "json",
                        "-show_format", "-show_streams", video]))
    out = {"duracion": float(d["format"]["duration"])}
    for s in d["streams"]:
        if s["codec_type"] == "video":
            num, den = s["r_frame_rate"].split("/")
            out.update(ancho=s["width"], alto=s["height"], fps=round(int(num) / int(den), 2),
                       codec_video=s["codec_name"])
        elif s["codec_type"] == "audio":
            out.update(codec_audio=s["codec_name"], frecuencia=int(s["sample_rate"]))
    return out


def extraer_audio(video, salida):
    ext = os.path.splitext(salida)[1].lower()
    if ext == ".wav":
        args = ["-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le"]
    elif ext == ".mp3":
        args = ["-c:a", "libmp3lame", "-q:a", "2"]
    else:
        args = ["-c:a", "aac", "-b:a", "192k"]
    run(["ffmpeg", "-v", "error", "-y", "-i", video, "-vn", *args, salida])
    return salida


def transcribir(video, carpeta, modelo, idioma, vocabulario=""):
    os.makedirs(carpeta, exist_ok=True)
    wav = extraer_audio(video, os.path.join(carpeta, "audio.wav"))
    m = cargar_modelo(modelo)
    import wave, numpy as np  # se lee el wav directo: evita depender de la versión de PyAV
    with wave.open(wav) as w:
        muestras = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
    segs, meta = m.transcribe(muestras, language=idioma, word_timestamps=True,
                              vad_filter=False, condition_on_previous_text=False,
                              initial_prompt=("Este, eh, mmm, o sea, bueno. " + vocabulario).strip())  # muletillas + términos técnicos
    resultado = {"video": os.path.abspath(video), "duracion": meta.duration,
                 "idioma": meta.language, "segmentos": []}
    for s in segs:
        resultado["segmentos"].append({
            "inicio": round(s.start, 2), "fin": round(s.end, 2), "texto": s.text.strip(),
            "palabras": [{"p": w.word.strip(), "i": round(w.start, 2), "f": round(w.end, 2),
                          "conf": round(w.probability, 2)} for w in (s.words or [])]})
    with open(os.path.join(carpeta, "transcripcion.json"), "w", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=1)

    # Vista legible: segmentos + pausas largas + palabras con baja confianza
    lineas, ultimo = [], 0.0
    for s in resultado["segmentos"]:
        if s["inicio"] - ultimo >= 0.7:
            lineas.append(f"   ··· pausa {s['inicio'] - ultimo:.1f}s [{fmt(ultimo)}–{fmt(s['inicio'])}]")
        dudosas = [w["p"] for w in s["palabras"] if w["conf"] < 0.5]
        extra = f"   (dudosas: {', '.join(dudosas)})" if dudosas else ""
        lineas.append(f"[{fmt(s['inicio'])}–{fmt(s['fin'])}] {s['texto']}{extra}")
        ultimo = s["fin"]
    if resultado["duracion"] - ultimo >= 0.7:
        lineas.append(f"   ··· pausa final {resultado['duracion'] - ultimo:.1f}s")
    txt = "\n".join(lineas)
    with open(os.path.join(carpeta, "transcripcion.txt"), "w", encoding="utf-8") as f:
        f.write(txt + "\n")
    print(txt)


def leer_cortes(ruta, duracion=None):
    with open(ruta, encoding="utf-8") as f:
        cortes = sorted(json.load(f), key=lambda c: c["inicio"])
    for c in cortes:
        if c["fin"] <= c["inicio"]:
            sys.exit(f"Tramo inválido: {c}")
        if duracion:
            c["fin"] = min(c["fin"], duracion)
    return cortes


def cortar(video, ruta_cortes, salida, crf):
    meta = info(video)
    cortes = leer_cortes(ruta_cortes, meta["duracion"])
    tiene_audio = "codec_audio" in meta
    partes, etiquetas = [], ""
    for n, c in enumerate(cortes):
        a, b = c["inicio"], c["fin"]
        partes.append(f"[0:v]trim={a}:{b},setpts=PTS-STARTPTS[v{n}]")
        if tiene_audio:  # fundido de 15 ms para evitar clics en las uniones
            fd = min(0.015, (b - a) / 4)
            partes.append(f"[0:a]atrim={a}:{b},asetpts=PTS-STARTPTS,"
                          f"afade=t=in:d={fd},afade=t=out:st={b - a - fd}:d={fd}[a{n}]")
        etiquetas += f"[v{n}]" + (f"[a{n}]" if tiene_audio else "")
    partes.append(f"{etiquetas}concat=n={len(cortes)}:v=1:a={1 if tiene_audio else 0}"
                  + ("[v][a]" if tiene_audio else "[v]"))
    cmd = ["ffmpeg", "-v", "error", "-y", "-i", video, "-filter_complex", ";".join(partes),
           "-map", "[v]", "-c:v", "libx264", "-preset", "medium", "-crf", str(crf),
           "-pix_fmt", "yuv420p", "-movflags", "+faststart"]
    if tiene_audio:
        cmd += ["-map", "[a]", "-c:a", "aac", "-b:a", "192k"]
    run(cmd + [salida])
    total = sum(c["fin"] - c["inicio"] for c in cortes)
    print(f"{salida}: {len(cortes)} tramos, {meta['duracion']:.1f}s → {total:.1f}s")


def a_tiempo_editado(t, cortes):
    """Convierte un tiempo del original al video editado; None si cae en un tramo eliminado."""
    acumulado = 0.0
    for c in cortes:
        if c["inicio"] <= t <= c["fin"]:
            return acumulado + t - c["inicio"]
        acumulado += c["fin"] - c["inicio"]
    return None


def srt_t(t):
    ms = int(round(t * 1000))
    h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def subtitulos(ruta_trans, salida, ruta_cortes, max_palabras):
    with open(ruta_trans, encoding="utf-8") as f:
        trans = json.load(f)
    cortes = leer_cortes(ruta_cortes) if ruta_cortes else None
    palabras = []
    for s in trans["segmentos"]:
        for w in s["palabras"]:
            mid = (w["i"] + w["f"]) / 2
            if cortes and a_tiempo_editado(mid, cortes) is None:
                continue
            i, f_ = w["i"], w["f"]
            if cortes:  # recorta la palabra al tramo que contiene su centro
                c = next(c for c in cortes if c["inicio"] <= mid <= c["fin"])
                i, f_ = max(i, c["inicio"]), min(f_, c["fin"])
                i, f_ = a_tiempo_editado(i, cortes), a_tiempo_editado(f_, cortes)
            palabras.append((w["p"], i, f_))
    bloques, actual = [], []
    for w in palabras:
        actual.append(w)
        if len(actual) >= max_palabras or w[0].endswith((".", "?", "!", ",")):
            bloques.append(actual); actual = []
    if actual:
        bloques.append(actual)
    with open(salida, "w", encoding="utf-8") as f:
        for n, b in enumerate(bloques, 1):
            fin = b[-1][2]
            if n < len(bloques):
                fin = min(fin + 0.3, bloques[n][0][1])  # sostiene el texto hasta el siguiente
            f.write(f"{n}\n{srt_t(b[0][1])} --> {srt_t(fin)}\n{' '.join(w[0] for w in b)}\n\n")
    print(f"{salida}: {len(bloques)} subtítulos")


def quemar(video, srt, salida, crf):
    meta = info(video)
    vertical = meta.get("alto", 0) > meta.get("ancho", 1)
    estilo = ("FontName=Inter,Bold=1,FontSize=" + ("14" if vertical else "20") +
              ",PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=1,Outline=2,"
              "Shadow=0,Alignment=2,MarginV=" + ("70" if vertical else "40"))
    ruta = srt.replace("\\", "/").replace(":", r"\:").replace("'", r"\'")
    run(["ffmpeg", "-v", "error", "-y", "-i", video, "-vf",
         f"subtitles='{ruta}':force_style='{estilo}'", "-c:v", "libx264", "-crf", str(crf),
         "-pix_fmt", "yuv420p", "-c:a", "copy", "-movflags", "+faststart", salida])
    print(salida)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = p.add_subparsers(dest="cmd", required=True)
    x = sp.add_parser("preparar"); x.add_argument("--modelo", default=MODELO)
    x = sp.add_parser("info"); x.add_argument("video")
    x = sp.add_parser("audio"); x.add_argument("video"); x.add_argument("-o", "--salida")
    x = sp.add_parser("transcribir"); x.add_argument("video"); x.add_argument("-d", "--dir", required=True)
    x.add_argument("--modelo", default=MODELO); x.add_argument("--idioma", default="es")
    x.add_argument("--vocabulario", default="", help="Términos que debe reconocer, p. ej. 'cuádriceps, isquiotibiales'")
    x = sp.add_parser("cortar"); x.add_argument("video"); x.add_argument("cortes")
    x.add_argument("-o", "--salida", required=True); x.add_argument("--crf", type=int, default=20)
    x = sp.add_parser("subtitulos"); x.add_argument("transcripcion"); x.add_argument("-o", "--salida", required=True)
    x.add_argument("--cortes"); x.add_argument("--palabras", type=int, default=4)
    x = sp.add_parser("quemar"); x.add_argument("video"); x.add_argument("srt")
    x.add_argument("-o", "--salida", required=True); x.add_argument("--crf", type=int, default=20)
    a = p.parse_args()

    if a.cmd == "preparar":
        cargar_modelo(a.modelo); print(f"Listo: faster-whisper + modelo '{a.modelo}'")
    elif a.cmd == "info":
        print(json.dumps(info(a.video), indent=1))
    elif a.cmd == "audio":
        print(extraer_audio(a.video, a.salida or os.path.splitext(a.video)[0] + ".wav"))
    elif a.cmd == "transcribir":
        transcribir(a.video, a.dir, a.modelo, a.idioma, a.vocabulario)
    elif a.cmd == "cortar":
        cortar(a.video, a.cortes, a.salida, a.crf)
    elif a.cmd == "subtitulos":
        subtitulos(a.transcripcion, a.salida, a.cortes, a.palabras)
    elif a.cmd == "quemar":
        quemar(a.video, a.srt, a.salida, a.crf)


if __name__ == "__main__":
    main()
