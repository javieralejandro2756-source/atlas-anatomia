---
name: editar-video
description: Edita videos que Javier sube (contenido de fisioterapia para redes, cabeza parlante, vertical u horizontal). Extrae el audio, transcribe en español con tiempos por palabra (faster-whisper), propone y aplica cortes de silencios, muletillas y tomas repetidas, y genera o incrusta subtítulos. Usar cuando suba un video o pida extraer audio, transcribir, recortar, quitar silencios/muletillas, subtitular o sacar un clip.
---

# Editar video

Herramienta: `scripts/video.py` (ffmpeg + faster-whisper, CPU). Ruta desde la raíz del repo:
`python3 .claude/skills/editar-video/scripts/video.py <subcomando> ...` — `--help` para todo.

## Flujo

1. **Localizar el video.** Si no da ruta, buscar el archivo subido más reciente:
   `find / -xdev \( -iname '*.mp4' -o -iname '*.mov' -o -iname '*.m4v' -o -iname '*.webm' \) -mmin -60 2>/dev/null | grep -v scratchpad`.
   Trabajar en una carpeta del scratchpad, nunca dentro del repo (los videos no se suben a git).
2. **`info VIDEO`** — duración, resolución, fps. Si dura > 10 min, avisar el tiempo estimado (~0.4× la duración con `small`).
3. **`transcribir VIDEO -d DIR --vocabulario "términos del tema"`** — siempre pasar los términos anatómicos/técnicos que probablemente diga (músculos, pruebas, ejercicios); mejora mucho el reconocimiento. Produce:
   - `DIR/transcripcion.txt`: segmentos con tiempos, pausas ≥ 0.7 s y palabras dudosas (conf < 0.5). Leer esto primero.
   - `DIR/transcripcion.json`: palabras con inicio/fin; usarlo para fijar los cortes exactos.
   - `DIR/audio.wav`: el audio extraído.
4. **Proponer cortes** (ver criterios) en una tabla breve: tramo eliminado, motivo, segundos ahorrados. Si Javier dijo "hazlo" o "edítalo", aplicar sin preguntar y reportar después.
5. **Escribir `DIR/cortes.json`** con los tramos A CONSERVAR (segundos del original) y ejecutar
   `cortar VIDEO DIR/cortes.json -o DIR/editado.mp4`.
6. **Verificar**: `transcribir DIR/editado.mp4 -d DIR/verif` y leer el texto: no debe haber palabras cortadas ni frases sin sentido. Corregir y repetir si hace falta.
7. **Subtítulos** (si los pide o es para Reels/TikTok/Shorts):
   `subtitulos DIR/transcripcion.json --cortes DIR/cortes.json -o DIR/subs.srt` y luego
   `quemar DIR/editado.mp4 DIR/subs.srt -o DIR/final.mp4`. Corregir en el `.srt` los términos mal transcritos antes de quemar.
8. **Entregar** con SendUserFile el video final (y el `.srt` si lo quiere aparte). Resumen: duración antes → después, qué se cortó.

Solo audio: `audio VIDEO -o salida.mp3` (o `.wav` / `.m4a`).

## Criterios de corte

- **Silencios**: dejar ≤ 0.25 s de aire antes y después de cada frase; pausas > 0.7 s se acortan. No pegar frases sin respiro: suena robótico.
- **Muletillas**: "este", "eh", "mmm", "o sea", "bueno" al inicio — cortar cuando no cargan sentido. Margen de 0.05 s alrededor de la palabra para no comer sílabas.
- **Tomas repetidas**: si repite una frase ("perdón, lo repito", reinicios), conservar la ÚLTIMA toma completa y eliminar la anterior junto con el comentario.
- **Arranque**: el primer tramo empieza en la primera palabra (gancho inmediato), sin respiraciones previas.
- **Contenido**: no cortar información técnica para ganar tiempo sin avisar. Si una afirmación clínica parece errónea, señalarla, no editarla en silencio.
- Unir tramos separados por < 0.15 s (evita microcortes).

## Notas técnicas

- Modelo por defecto `small` (variable `WHISPER_MODELO`; `medium` es más preciso y ~2.5× más lento). Primera ejecución descarga el modelo de Hugging Face; `preparar` lo hace por adelantado.
- Requiere red a Hugging Face (entorno cloud `atlas-anatomia`). Si la descarga da 403 del proxy, el entorno no tiene esos hosts.
- `cortar` recodifica (H.264 CRF 20, AAC 192k) con fundidos de 15 ms en cada unión para evitar clics.
- Los subtítulos usan bloques de ≤ 4 palabras (`--palabras N`), Inter negrita, contorno negro, abajo al centro.
