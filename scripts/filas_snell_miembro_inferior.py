"""Agrega al CSV de revisión las filas que salen de cotejar el miembro inferior
contra las tablas de Snell (Anatomía clínica por regiones, 10.a ed.).
Cada dato se leyó en la imagen de la tabla, no en el OCR. Idempotente: si ya
existen filas con tipo de Snell, no duplica."""
import csv, json, sys
CSV = "datos/revision_musculos.csv"
fichas = {f["id"]: f for f in json.load(open("datos/musculos.json", encoding="utf-8"))}

# id: (tabla, raíces Snell, raíz principal en negrita)
SNELL = {
 "m070": ("11-2", "L1, L2, L3", "L1, L2"), "m071": ("11-2", "L2, L3", "L2"),
 "m129": ("11-2", "L2, L3", "L2"), "m160": ("11-2", "L2, L3", "L2"),
 "m130": ("11-2", "L2, L3, L4", "L3, L4"), "m164": ("11-2", "L2, L3, L4", "L3, L4"),
 "m165": ("11-2", "L2, L3, L4", "L3, L4"), "m166": ("11-2", "L2, L3, L4", "L3, L4"),
 "m167": ("11-2", "L2, L3, L4", "L3, L4"),
 "m131": ("11-3", "L2, L3, L4", "L3, L4"), "m162": ("11-3", "L2, L3, L4", "L3, L4"),
 "m132": ("11-3", "L2, L3, L4", "L3, L4"), "m161": ("11-3", "L2, L3, L4", "L3, L4"),
 "m133": ("11-3", "L2, L3, L4", "L3, L4"), "m159": ("11-3", "L2, L3, L4", "L3, L4"),
 "m134": ("11-3", "L3, L4", "L4"), "m145": ("11-3", "L3, L4", "L4"),
 "m172": ("11-3", "L2, L3", "L3"),
 "m137": ("11-1", "L5, S1", "L5"), "m140": ("11-1", "L5, S1", "L5"),
 "m139": ("11-1", "L5, S1, S2", "S1, S2"), "m141": ("11-1", "L5, S1, S2", "S1"),
 "m146": ("11-1", "L5, S1", "S1"),
 "m168": ("11-4", "L5, S1, S2", "S1"), "m173": ("11-4", "L5, S1, S2", "S1"),
 "m169": ("11-4", "L5, S1, S2", "L5, S1"), "m170": ("11-4", "L5, S1, S2", "L5, S1"),
 "m185": ("11-5", "L4; S5 (así impreso)", "L4"), "m179": ("11-7", "L4; S5 (así impreso)", "L4"),
 "m183": ("11-6", "L5, S1, S2", "S1"), "m187": ("11-6", "L5, S1, S2", "S1"),
 "m174": ("11-7", "S1, S2", "S1"), "m175": ("11-7", "S1, S2", "S1"), "m177": ("11-7", "S1, S2", "S1"),
 "m178": ("11-7", "S1, S2", "S2"),
 "m180": ("11-7", "S2, S3", "S2"), "m182": ("11-7", "S2, S3", "S2"),
}
for i in ["m191","m192","m193","m194","m195","m196","m197","m198","m199","m200","m201","m202","m203","m204"]:
    SNELL[i] = ("11-8", "S2, S3", "S3")

# Discrepancias de raíz: (id, texto_actual en inervación, propuesta con las raíces de Snell, tabla, nota extra)
DIFS = [
 ("m162", "ciático (L4)", "ciático (L2-L4)", "11-4", "Snell da L2, L3, L4 a la porción isquiotibial. Moore suele dar L4; decide tú."),
 ("m161", "(L2-L3)", "(L2-L4)", "11-3", "Coincide con la fila 194 (m132)."),
 ("m159", "(L2-L3)", "(L2-L4)", "11-3", "Coincide con la fila 195 (m133)."),
 ("m138", "(L4-S1)", "(L4-L5)", "11-1", ""),
 ("m141", "(S1-S2)", "(L5-S2)", "11-1", ""),
 ("m180", "(L5-S2)", "(S2-S3)", "11-7", ""),
 ("m182", "(L5-S2)", "(S2-S3)", "11-7", ""),
 ("m186", "(L5)", "(L5-S1)", "11-5", ""),
 ("m183", "(L5-S1)", "(L5-S2)", "11-6", ""),
 ("m187", "(L5-S1)", "(L5-S2)", "11-6", ""),
 ("m189", "(L5-S1)", "(S1-S2)", "11-9", ""),
 ("m191", "(S1-S3)", "(S2-S3)", "11-8", ""),
 ("m193", "(S1-S3)", "(S2-S3)", "11-8", ""),
 ("m194", "(S1-S3)", "(S2-S3)", "11-8", ""),
 ("m195", "(S1-S3)", "(S2-S3)", "11-8", ""),
]
# Snell imprime "L4; S5": no se puede aplicar; queda sin propuesta.
SIN_PROPUESTA = [("m185", "(L4-L5)", "11-5"), ("m179", "(L4-L5)", "11-7")]

filas = list(csv.DictReader(open(CSV, encoding="utf-8-sig")))
if any(r["tipo"].startswith("Snell") for r in filas):
    sys.exit("Las filas de Snell ya están en el CSV.")
campos = list(filas[0].keys())
n = max(int(r["n"]) for r in filas)
nuevas = []
def fila(mid, campo, tipo, actual, alcance, prop, conf, nota):
    global n; n += 1
    f = fichas[mid]
    nuevas.append({"n": n, "id": mid, "musculo": f["nombre"], "region": f["region"], "campo": campo,
                   "tipo": tipo, "texto_actual": actual, "alcance": alcance, "propuesta": prop,
                   "confianza": conf, "nota": nota, "decision": ""})

for mid, actual, prop, tabla, extra in DIFS:
    assert actual in fichas[mid]["inervacion"], (mid, actual)
    fila(mid, "inervacion", "Snell: raíz difiere", actual, "fragmento", prop, "alta",
         f"Tu ficha: {actual}. Snell tabla {tabla}: {SNELL.get(mid, (tabla, prop))[1]}. {extra}".strip())
for mid, actual, tabla in SIN_PROPUESTA:
    fila(mid, "inervacion", "Snell: raíz difiere", actual, "fragmento", "", "",
         f"Snell tabla {tabla} imprime «L4; S5». S5 no es plausible (parece errata por L5). Sin propuesta: escribe tu decisión.")
for mid, (tabla, raices, principal) in SNELL.items():
    nota = f"Snell tabla {tabla}, raíz en negrita."
    if mid == "m178":
        nota += " En la imagen S2 aparece en negrita cursiva."
    fila(mid, "raiz_principal", "Snell: raíz principal", "", "campo completo", principal, "alta", nota)

with open(CSV, "w", encoding="utf-8-sig", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=campos); w.writeheader(); w.writerows(filas + nuevas)
print("filas nuevas:", len(nuevas), "total:", len(filas) + len(nuevas))
