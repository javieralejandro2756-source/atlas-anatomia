"""Liga cada malla de músculo de Z-Anatomy con su ficha de musculos_revisado.json.

Uso: python ligar_mallas.py
Entradas: app/public/modelos/manifest.json, app/public/modelos/nombres.json, datos/musculos_revisado.json
Salidas:
  app/public/datos/fichas.json   fichas que muestra la app (sin las fusionadas)
  app/public/datos/mapeo.json    nombre base de malla -> [ids de ficha]
  datos/ligado_reporte.json      mallas sin ficha y fichas sin malla

Reglas: coincidencia exacta del nombre en español (TA2 de Z-Anatomy vs. nombre de la ficha,
sin acentos ni artículos) o una entrada de MANUAL revisada a mano. No se fuerzan coincidencias dudosas.
"""
import json, re, unicodedata, os

AQUI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ruta = lambda *p: os.path.join(AQUI, *p)

manifest = json.load(open(ruta("app/public/modelos/manifest.json"), encoding="utf-8"))
nombres = json.load(open(ruta("app/public/modelos/nombres.json"), encoding="utf-8"))
fichas = json.load(open(ruta("datos/musculos_revisado.json"), encoding="utf-8"))

# Revisado a mano: el nombre de la ficha no coincide literalmente con el de TA2,
# pero la malla es inequívocamente ese músculo.
MANUAL = {
    "m139": ["Gluteus maximus muscle"],
    "m140": ["Gluteus minimus muscle"],
    "m182": ["Flexor hallucis longus"],
    "m183": ["Fibularis longus muscle"],
    "m186": ["Extensor hallucis longus"],
    "m187": ["Fibularis brevis muscle"],
    "m188": ["Fibularis tertius muscle"],
    "m190": ["Extensor hallucis brevis"],
    "m192": ["Abductor digiti minimi of foot"],
    "m194": ["Abductor hallucis"],
    "m195": ["Medial head of flexor hallucis brevis", "Lateral head of flexor hallucis brevis"],
    "m196": ["Lumbrical muscles of foot"],
    "m197": ["Oblique head of adductor hallucis"],
    "m198": ["Transverse head of adductor hallucis"],
    "m199": ["Plantar interossei muscles"],
    "m200": ["Flexor digiti minimi of foot"],
    # Z-Anatomy trae los cuatro interóseos dorsales del pie en una sola malla:
    # la malla se liga a las cuatro fichas (relación de grupo, no una suposición).
    "m201": ["Dorsal interossei muscles of foot"],
    "m202": ["Dorsal interossei muscles of foot"],
    "m203": ["Dorsal interossei muscles of foot"],
    "m204": ["Dorsal interossei muscles of foot"],
}

def base(n):
    return re.sub(r"\.(l|r|j|[oe]\d*[lr])$", "", n).strip()

def norm(s):
    s = unicodedata.normalize("NFD", s.lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    s = re.sub(r"\b(musculo|musculos|del|de|la|el|los|las|o)\b", " ", s)
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    return " ".join(s.split())

mallas_musculo = sorted({base(x["nombre"]) for x in manifest["mallas"] if x["sistema"] == "musculos"})
es_norm = {b: norm(nombres[b]["es"]) for b in mallas_musculo if b in nombres}

mapeo = {}
fichas_sin_malla = []
for f in fichas:
    if f.get("tipo") not in ("músculo",):
        continue
    if f["id"] in MANUAL:
        hits = [b for b in MANUAL[f["id"]] if b in mallas_musculo]
    else:
        n = norm(f["nombre"])
        hits = [b for b, e in es_norm.items() if e == n]
    if not hits:
        fichas_sin_malla.append({"id": f["id"], "nombre": f["nombre"], "region": f["region"]})
    for b in hits:
        mapeo.setdefault(b, [])
        if f["id"] not in mapeo[b]:
            mapeo[b].append(f["id"])

mallas_sin_ficha = [b for b in mallas_musculo if b not in mapeo]

campos = ["id", "nombre", "region", "origen", "insercion", "inervacion", "raices", "raiz_principal",
          "pares_craneales", "inervacion_segmentaria", "irrigacion", "funcion", "estado", "fuente_cotejo",
          "filas_pendientes", "tipo"]
salida = [{k: f.get(k) for k in campos} for f in fichas if f.get("tipo") != "fusionado"]

os.makedirs(ruta("app/public/datos"), exist_ok=True)
json.dump(salida, open(ruta("app/public/datos/fichas.json"), "w", encoding="utf-8"), ensure_ascii=False)
json.dump(mapeo, open(ruta("app/public/datos/mapeo.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=0)
json.dump({"mallas_sin_ficha": mallas_sin_ficha, "fichas_sin_malla": fichas_sin_malla},
          open(ruta("datos/ligado_reporte.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

print(f"mallas de músculo: {len(mallas_musculo)} | ligadas: {len(mapeo)} | sin ficha: {len(mallas_sin_ficha)}")
print(f"fichas de músculo sin malla: {len(fichas_sin_malla)}")
