"""Genera nombres.json (español y latín) para cada malla a partir de TA2.csv de Z-Anatomy.
Uso: python nombres_ta2.py <TA2.csv> <manifest.json> <salida nombres.json>"""
import json, re, sys
ta2, man, out = sys.argv[1:4]
ta = {}
for line in open(ta2, encoding="utf-8-sig"):
    p = line.strip().strip('"').split(";")
    if len(p) >= 6:
        ta.setdefault(p[1].strip().lower(), {"la": p[2].strip(), "es": p[4].strip()})
m = json.load(open(man, encoding="utf-8"))
def base(n): return re.sub(r"\.(l|r|j|[oe]\d*[lr])$", "", n).strip()
res, falta = {}, set()
for x in m["mallas"]:
    b = base(x["nombre"]); k = b.strip("()[] ").lower()
    cands = [k, k.replace(" muscle", ""), k + " muscle", re.sub(r" \(.*\)\*?$", "", k), k.rstrip("*"), re.sub(r"\*", "", k)]
    hit = next((ta[c] for c in cands if c in ta), None)
    if hit: res[b] = hit
    else: falta.add(b)
json.dump(res, open(out, "w", encoding="utf-8"), ensure_ascii=False)
print("traducidos", len(res), "sin traducción", len(falta))
