"""Inventario del .blend de Z-Anatomy. Uso: python inventario_blend.py <ruta.blend> <salida.json>"""
import sys, json, collections
import bpy

ruta, salida = sys.argv[1], sys.argv[2]
bpy.ops.wm.open_mainfile(filepath=ruta, load_ui=False)

def arbol(col, prof=0, out=None):
    out = [] if out is None else out
    tipos = collections.Counter(o.type for o in col.objects)
    out.append({"prof": prof, "nombre": col.name, "objetos": len(col.objects),
                "objetos_recursivos": len(col.all_objects), "tipos": dict(tipos),
                "hijos": len(col.children)})
    for c in col.children:
        arbol(c, prof + 1, out)
    return out

escena = bpy.context.scene
cols = arbol(escena.collection)
objs = list(bpy.data.objects)
mallas = [o for o in objs if o.type == "MESH"]
tris = 0
for o in mallas:
    m = o.data
    tris += sum(len(p.vertices) - 2 for p in m.polygons)

# primer nivel de colecciones con su sistema
def colecciones_de(o):
    return [c.name for c in o.users_collection]

muestra = {}
for o in objs[:]:
    for c in o.users_collection:
        muestra.setdefault(c.name, [])
        if len(muestra[c.name]) < 15:
            muestra[c.name].append(o.name)

props = collections.Counter()
for o in objs:
    for k in o.keys():
        props[k] += 1

datos = {
    "version_archivo": bpy.data.version,
    "escenas": [s.name for s in bpy.data.scenes],
    "total_objetos": len(objs),
    "tipos_objeto": dict(collections.Counter(o.type for o in objs)),
    "mallas": len(mallas),
    "triangulos_totales": tris,
    "vertex_groups_en_mallas": sum(1 for o in mallas if o.vertex_groups),
    "mallas_con_atributos_color": sum(1 for o in mallas if len(o.data.color_attributes)),
    "materiales": len(bpy.data.materials),
    "textos": [t.name for t in bpy.data.texts][:50],
    "propiedades_custom": dict(props.most_common(30)),
    "colecciones": cols,
    "muestra_nombres": muestra,
    "objetos": [{"n": o.name, "t": o.type, "c": colecciones_de(o),
                 "tris": (sum(len(p.vertices) - 2 for p in o.data.polygons) if o.type == "MESH" else 0),
                 "mat": ([s.material.name for s in o.material_slots if s.material][:3] if o.type == "MESH" else []),
                 "hide": o.hide_get() if o.name in bpy.context.view_layer.objects else None,
                 "vg": [g.name for g in o.vertex_groups][:10] if o.type == "MESH" else []}
                for o in objs],
}
json.dump(datos, open(salida, "w"), ensure_ascii=False, indent=1)
print("ok", len(objs), len(mallas), tris)
