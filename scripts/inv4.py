import bpy, sys, collections
bpy.ops.wm.open_mainfile(filepath=sys.argv[1], load_ui=False)
def chain(o):
    c=[]; p=o.parent
    while p: c.append(p.name); p=p.parent
    return c
for col in ['4: Muscular system','1: Skeletal system','3: Joints','2: Muscular insertions','7: Nervous system & Sense organs']:
    tops=collections.Counter()
    for o in bpy.data.collections[col].objects:
        if o.type in('MESH','CURVE') and (o.type=='CURVE' or len(o.data.polygons)):
            ch=chain(o); tops[' > '.join(ch[-3:][::-1]) if ch else '(sin padre)']+=1
    print('==',col); [print('  ',n,k) for k,n in tops.most_common(40)]
import addon_utils
print([m.__name__ for m in addon_utils.modules() if 'gltf' in m.__name__])
from io_scene_gltf2.io.com import gltf2_io_draco_compression_extension as d
print('draco', d.dll_exists())
