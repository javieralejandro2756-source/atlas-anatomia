"""Aplica revision_musculos.csv a musculos.json.

Uso: python aplicar_revision.py datos/musculos.json datos/revision_musculos.csv datos/musculos_revisado.json

Reglas (INSTRUCCIONES.md):
- Solo se aplican filas con `decision` no vacía.
  "aceptar"  -> se aplica `propuesta`.
  "rechazar" -> no se toca el dato; la fila deja de estar pendiente.
  otro texto -> sustituye a la propuesta y se aplica.
- alcance "fragmento": reemplaza texto_actual por la propuesta dentro del campo.
  alcance "campo completo": sustituye el campo entero.
  alcance "ficha": acciones estructurales (fusionar, mover, capturar). No se
  ejecutan automáticamente: se registran en el reporte para hacerlas a mano.
- Tras aplicar, `raices` se recalcula desde el texto de inervación.
  `raices_propuestas` solo pasa a `raices` si su fila "raíces faltantes" fue aceptada.
- Estado "verificado" solo si la ficha no tiene filas pendientes.
- Nunca se corrige nada sin fila decidida.
"""
import csv, json, re, sys, copy

ORDEN = ["C1","C2","C3","C4","C5","C6","C7","C8"] + [f"T{i}" for i in range(1,13)] + \
        [f"L{i}" for i in range(1,6)] + [f"S{i}" for i in range(1,6)] + ["Co1"]
IDX = {r: i for i, r in enumerate(ORDEN)}

def expandir(a, b):
    if a in IDX and b in IDX and IDX[a] <= IDX[b]:
        return ORDEN[IDX[a]:IDX[b] + 1]
    return []

def raices_desde_texto(texto):
    """Extrae raíces escritas como C5, C5-T1, C5–C7, (L2, L3). Rangos imposibles -> []."""
    if not texto:
        return []
    t = texto.replace("–", "-").replace("—", "-")
    encontradas = []
    for m in re.finditer(r"\b([CTLS])(\d{1,2})\s*(?:[-_]\s*([CTLS])?(\d{1,2}))?\b", t):
        a = m.group(1) + m.group(2)
        if m.group(4):
            b = (m.group(3) or m.group(1)) + m.group(4)
            encontradas += expandir(a, b)
        elif a in IDX:
            encontradas.append(a)
    vistas = []
    for r in sorted(set(encontradas), key=lambda r: IDX[r]):
        vistas.append(r)
    return vistas

def parse_lista_raices(texto):
    return [r.strip() for r in (texto or "").split(",") if r.strip() in IDX]

CAMPOS = {"origen","insercion","inervacion","irrigacion","funcion","nombre","raiz_principal"}

def main(f_json, f_csv, f_out, f_reporte, f_cotejo="datos/cotejo.json"):
    fichas = json.load(open(f_json, encoding="utf-8"))
    por_id = {f["id"]: f for f in fichas}
    filas = list(csv.DictReader(open(f_csv, encoding="utf-8-sig")))

    aplicadas, rechazadas, fallidas, estructurales = [], [], [], []
    pendientes_por_id = {}
    raices_aceptadas = {}  # id -> lista

    for r in filas:
        dec = (r.get("decision") or "").strip()
        mid = r["id"]
        if not dec:
            if mid:
                pendientes_por_id.setdefault(mid, []).append(int(r["n"]))
            continue
        if dec.lower() == "rechazar":
            rechazadas.append(r["n"])
            continue
        valor = r["propuesta"] if dec.lower() == "aceptar" else dec

        if r["alcance"] == "ficha" or not mid:
            estructurales.append({"n": r["n"], "id": mid, "accion": valor, "propuesta": r["propuesta"]})
            continue
        f = por_id.get(mid)
        campo = r["campo"]
        if f is None or campo not in CAMPOS:
            fallidas.append({"n": r["n"], "motivo": "id o campo desconocido"})
            continue

        if campo == "raiz_principal":
            f["raiz_principal"] = parse_lista_raices(valor)
            aplicadas.append(r["n"])
            continue

        if r["tipo"] == "raíces faltantes":
            # la propuesta es una lista de raíces o una marca de segmentaria
            if "segmentaria" in valor.lower():
                f["inervacion_segmentaria"] = True
            else:
                raices_aceptadas[mid] = parse_lista_raices(valor)
            aplicadas.append(r["n"])
            continue

        if valor.startswith("(vaciar el campo"):
            valor = ""
        actual = f.get(campo) or ""
        if r["alcance"] == "fragmento":
            if r["texto_actual"] not in actual:
                fallidas.append({"n": r["n"], "motivo": f"texto_actual no encontrado en {mid}.{campo}"})
                pendientes_por_id.setdefault(mid, []).append(int(r["n"]))
                continue
            f[campo] = actual.replace(r["texto_actual"], valor, 1)
        else:
            f[campo] = valor
        aplicadas.append(r["n"])

    # Acciones de ficha: "conservar mXXX" (fusiona duplicados), "grupo", "estructura".
    hechas = []
    for e in estructurales:
        acc = e["accion"].strip().lower()
        if acc.startswith("conservar "):
            keep = acc.split()[1]
            ids = {e["id"]} | set(re.findall(r"m\d{3}", e["propuesta"]))
            otros = [i for i in ids if i != keep]
            if keep not in por_id or len(otros) != 1 or otros[0] not in por_id:
                fallidas.append({"n": e["n"], "motivo": "fusión ambigua"}); continue
            k, o = por_id[keep], por_id[otros[0]]
            for c in ("origen", "insercion", "inervacion", "irrigacion", "funcion"):
                if not (k.get(c) or "").strip() and (o.get(c) or "").strip():
                    k[c] = o[c]
            o["tipo"] = "fusionado"; o["fusionado_en"] = keep; k["duplicado_de"] = None
            hechas.append(e["n"])
        elif acc == "grupo":
            por_id[e["id"]]["tipo"] = "grupo de músculos"; hechas.append(e["n"])
        elif acc == "estructura":
            por_id[e["id"]]["tipo"] = "estructura"; hechas.append(e["n"])
    estructurales = [e for e in estructurales if e["n"] not in hechas]
    aplicadas += hechas

    # Regla B: "verificado" exige no tener filas pendientes Y haber sido cotejada con una fuente.
    try:
        cotejo = json.load(open(f_cotejo, encoding="utf-8"))
    except FileNotFoundError:
        cotejo = {}

    for f in fichas:
        f.setdefault("raiz_principal", [])
        f["raices"] = raices_desde_texto(f.get("inervacion"))
        if f["id"] in raices_aceptadas:
            f["raices"] = sorted(set(f["raices"]) | set(raices_aceptadas[f["id"]]), key=lambda x: IDX[x])
        f["filas_pendientes"] = sorted(pendientes_por_id.get(f["id"], []))
        f["fuente_cotejo"] = cotejo.get(f["id"], "")
        f["estado"] = "verificado" if (not f["filas_pendientes"] and f["fuente_cotejo"]) else "por revisar"
        if f.get("tipo") == "fusionado":
            f["estado"] = "fusionado"

    json.dump(fichas, open(f_out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    sin_ficha = sum(1 for r in filas if not (r.get("decision") or "").strip() and not r["id"])
    reporte = {
        "filas_total": len(filas),
        "aplicadas": len(aplicadas),
        "rechazadas": len(rechazadas),
        "estructurales_para_hacer_a_mano": estructurales,
        "fallidas": fallidas,
        "pendientes": sum(len(v) for v in pendientes_por_id.values()) + sin_ficha,
        "fichas_total": len(fichas),
        "fichas_verificadas": sum(1 for f in fichas if f["estado"] == "verificado"),
        "fichas_por_revisar": sum(1 for f in fichas if f["estado"] == "por revisar"),
        "fichas_fusionadas": sum(1 for f in fichas if f["estado"] == "fusionado"),
    }
    json.dump(reporte, open(f_reporte, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps({k: v for k, v in reporte.items() if k != "estructurales_para_hacer_a_mano"}, ensure_ascii=False, indent=1))

if __name__ == "__main__":
    main(*sys.argv[1:6])
