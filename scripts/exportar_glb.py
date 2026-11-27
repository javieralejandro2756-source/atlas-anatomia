"""Exporta Z-Anatomy a glTF (.glb) con Draco: un archivo por región y sistema.

Uso: python exportar_glb.py <Startup.blend> <carpeta_salida>

- Una malla por estructura, con su nombre anatómico (inglés, como en el .blend).
- Sistemas: huesos, musculos, ligamentos, nervios, inserciones, fascias.
- Regiones: miembro-inferior, miembro-superior, tronco, cabeza-cuello.
- Simplificación (Decimate) por sistema para que corra en una MacBook Air 2017.
- No se dibuja ni se inventa geometría: solo se copia, se simplifica y se exporta.
- Se excluyen el sistema nervioso central, vísceras, vasos y los modelos con licencia NC
  (oído interno y riñón), que además quedan fuera del alcance.
Escribe manifest.json con cada malla: archivo, sistema, región, lado, triángulos y caja.
"""
import bpy, sys, json, os, re, math
from mathutils import Vector

blend, out = sys.argv[1], sys.argv[2]
PERFIL = sys.argv[3] if len(sys.argv) > 3 else "mac"   # "mac" (ligero) o "iphone" (alta calidad)
os.makedirs(out, exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=blend, load_ui=False)

# Proporción de triángulos que se conserva por sistema y mínimo por malla.
PERFILES = {
    # MacBook Air 2017 (Intel HD 6000): ~1,2 M triángulos en total.
    "mac": {"ratio": {"snc": 0.35, "musculos": 0.2, "huesos": 0.3, "ligamentos": 0.4, "inserciones": 0.12, "fascias": 0.15, "nervios": 1.0},
            "min_tris": 250, "curva_res": 3, "curva_bevel": 1},
    # iPhone 16 Pro Max (A18 Pro): detalle alto, se carga por región.
    # Músculos, huesos y ligamentos a resolución completa del atlas (sin simplificar).
    "iphone": {"ratio": {"snc": 1.0, "musculos": 1.0, "huesos": 1.0, "ligamentos": 1.0, "inserciones": 0.5, "fascias": 0.6, "nervios": 1.0},
               "min_tris": 600, "curva_res": 8, "curva_bevel": 3, "normales_bits": 12},
}
RATIO = PERFILES[PERFIL]["ratio"]
MIN_TRIS = PERFILES[PERFIL]["min_tris"]

def cadena(o):
    c, p = [], o.parent
    while p:
        c.append(p.name.lower()); p = p.parent
    return c

def sistema_de(o):
    cols = [c.name for c in o.users_collection]
    ch = " ".join(cadena(o))
    if "2: Muscular insertions" in cols:
        return "inserciones"
    if "4: Muscular system" in cols:
        if any(k in ch for k in ("fascia", "bursae", "tendon sheaths")):
            return "fascias"
        return "musculos"
    if "1: Skeletal system" in cols:
        return "huesos"
    if "3: Joints" in cols:
        return "ligamentos"
    if "7: Nervous system & Sense organs" in cols and o.type == "CURVE" and "peripheral nervous system" in ch:
        return "nervios"
    if "7: Nervous system & Sense organs" in cols and ("central nervous system" in ch or "eye.g" in ch):
        if "internal ear" in ch:
            return None  # oído interno: modelo con licencia no comercial, no se exporta
        return "snc"
    return None

# Calibración de regiones con los huesos de referencia.
def caja(o):
    pts = [o.matrix_world @ Vector(c) for c in o.bound_box]
    lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    return lo, hi

def buscar(prefijo):
    return [o for o in bpy.data.objects if o.type == "MESH" and o.name.startswith(prefijo) and len(o.data.polygons)]

femur_top = max(caja(o)[1].z for o in buscar("Femur"))
costillas = [o for o in bpy.data.objects if o.type == "MESH" and re.match(r"^(\d+\w*|First|Second|Third|Fourth|Fifth|Sixth|Seventh|Eighth|Ninth|Tenth|Eleventh|Twelfth) rib", o.name) and len(o.data.polygons)]
torax_x = max(max(abs(caja(o)[0].x), abs(caja(o)[1].x)) for o in costillas) if costillas else None
manubrio_top = max(caja(o)[1].z for o in buscar("Manubrium")) if buscar("Manubrium") else None
CAL = {"femur_top": femur_top, "torax_x": torax_x, "manubrio_top": manubrio_top}
print("calibración", CAL)

PALABRAS = [
    ("miembro-inferior", ("lower limb", "pelvic girdle", "free lower")),
    ("miembro-superior", ("upper limb", "pectoral girdle", "free upper")),
    ("cabeza-cuello", ("head", "cranium", "cranial", "neck", "cervical", "teeth", "tooth", "ossicles", "laryn", "nasal", "mandible", "hyoid", "skull", "temporomandibular")),
    ("tronco", ("thorax", "thoracic", "abdomen", "abdominal", "dorsal", "epaxial", "hypaxial", "pelvis", "lumbar", "vertebral", "sacrum", "costal", "thoracolumbar")),
]

def region_de(o, sis):
    if sis == "snc":
        ch = " ".join(cadena(o))
        if "spinal cord" in ch or "spinal dura" in o.name.lower():
            lo, hi = caja(o)
            return "cabeza-cuello" if (lo.z + hi.z) / 2 > (manubrio_top or 0) else "tronco"
        return "cabeza-cuello"
    if sis != "nervios":
        ch = " ".join(cadena(o))
        for reg, keys in PALABRAS:
            if any(k in ch for k in keys):
                return reg
    n = o.name.lower()
    if re.search(r"\b(palmar|ulnar|median|radial|antebrachial|brachial|musculocutaneous|axillary)\b|of forearm", n):
        return "miembro-superior"
    if re.search(r"\b(plantar|fibular|tibial|sural|saphenous|femoral|sciatic)\b|of foot", n):
        return "miembro-inferior"
    lo, hi = caja(o)
    c = (lo + hi) / 2
    if torax_x and abs(c.x) > torax_x * 1.05 and c.z > femur_top * 0.6:
        return "miembro-superior"
    if c.z < femur_top:
        return "miembro-inferior"
    if manubrio_top and c.z > manubrio_top:
        return "cabeza-cuello"
    return "tronco"

def lado(nombre):
    m = re.search(r"\.([lr])$|\.[oe]\d?([lr])$", nombre)
    if not m:
        return "medial"
    return {"l": "izquierdo", "r": "derecho"}[m.group(1) or m.group(2)]

# Selección de objetos
grupos = {}
for o in bpy.data.objects:
    if o.type not in ("MESH", "CURVE"):
        continue
    if o.type == "MESH" and not len(o.data.polygons):
        continue
    if re.search(r"\.(g|t|s|st|j)$", o.name):
        continue  # etiquetas de texto y nodos de jerarquía, no estructuras
    sis = sistema_de(o)
    if not sis:
        continue
    if o.type == "CURVE":
        if not (o.data.bevel_depth > 0 or o.data.bevel_object):
            continue
        o.data.resolution_u = min(o.data.resolution_u, PERFILES[PERFIL]["curva_res"])
        o.data.bevel_resolution = PERFILES[PERFIL]["curva_bevel"]
    grupos.setdefault((region_de(o, sis), sis), []).append(o)

dg = bpy.context.evaluated_depsgraph_get()
manifest = {"calibracion": CAL, "archivos": {}, "mallas": []}
omitidas = []

for (reg, sis), objs in sorted(grupos.items()):
    esc = bpy.data.scenes.new(f"{reg}-{sis}")
    for o in objs:
        try:
            ev = o.evaluated_get(dg)
            me = bpy.data.meshes.new_from_object(ev, preserve_all_data_layers=False, depsgraph=dg)
        except Exception as e:
            omitidas.append({"nombre": o.name, "motivo": str(e)}); continue
        if not me or not len(me.polygons):
            omitidas.append({"nombre": o.name, "motivo": "sin geometría"}); continue
        me.transform(o.matrix_world)
        me.materials.clear()
        tris0 = sum(len(p.vertices) - 2 for p in me.polygons)
        nombre = o.name
        o.name = nombre + "#src"
        nuevo = bpy.data.objects.new(nombre, me)
        assert nuevo.name == nombre, (nuevo.name, nombre)
        nuevo["nombre"] = nombre  # el cargador de three.js limpia puntos y espacios del nombre; aquí queda intacto
        esc.collection.objects.link(nuevo)
        r = RATIO[sis]
        if r < 1 and tris0 > MIN_TRIS:
            ratio = max(r, MIN_TRIS / tris0)
            mod = nuevo.modifiers.new("dec", "DECIMATE"); mod.ratio = min(1.0, ratio)
        manifest["mallas"].append({"nombre": nombre, "archivo": f"{reg}-{sis}.glb", "sistema": sis,
                                   "region": reg, "lado": lado(nombre), "tris_original": tris0})
    if bpy.context.window:
        bpy.context.window.scene = esc
    else:
        raise SystemExit("sin ventana de contexto")
    ruta = os.path.join(out, f"{reg}-{sis}.glb")
    bpy.ops.export_scene.gltf(filepath=ruta, export_format="GLB", use_active_scene=True,
                              export_apply=True, export_materials="NONE", export_normals=True,
                              export_texcoords=False, export_yup=True, export_extras=True,
                              export_draco_mesh_compression_enable=True,
                              export_draco_mesh_compression_level=6,
                              export_draco_position_quantization=14,
                              export_draco_normal_quantization=PERFILES[PERFIL].get("normales_bits", 10))
    # triángulos finales
    dg2 = bpy.context.evaluated_depsgraph_get()
    tris = 0
    for ob in esc.collection.objects:
        m2 = ob.evaluated_get(dg2).to_mesh()
        t = sum(len(p.vertices) - 2 for p in m2.polygons); tris += t
        ob.evaluated_get(dg2).to_mesh_clear()
        for m in manifest["mallas"]:
            if m["archivo"] == f"{reg}-{sis}.glb" and m["nombre"] == ob.name:
                m["tris"] = t
    manifest["archivos"][f"{reg}-{sis}.glb"] = {"region": reg, "sistema": sis, "mallas": len(objs),
                                               "tris": tris, "bytes": os.path.getsize(ruta)}
    print(f"{reg}-{sis}.glb  mallas={len(objs)}  tris={tris}  bytes={os.path.getsize(ruta)}", flush=True)

manifest["omitidas"] = omitidas
json.dump(manifest, open(os.path.join(out, "manifest.json"), "w"), ensure_ascii=False, indent=1)
print("omitidas", len(omitidas))
