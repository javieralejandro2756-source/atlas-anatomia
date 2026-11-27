import bpy, sys, collections
bpy.ops.wm.open_mainfile(filepath=sys.argv[1], load_ui=False)
c=bpy.data.collections['7: Nervous system & Sense organs']
cur=[o for o in c.objects if o.type=='CURVE']
print('nervios curva', len(cur), 'con grosor', sum(1 for o in cur if o.data.bevel_depth>0 or o.data.bevel_object), 'ejemplo bevel', cur[0].data.bevel_depth, cur[0].data.bevel_mode)
pn=[o.name for o in cur]
for k in ['Femoral nerve','Sciatic nerve','Tibial nerve','Obturator nerve','Common fibular nerve','Median nerve','Ulnar nerve','Radial nerve','Musculocutaneous nerve','Axillary nerve','Lumbar plexus','Sacral plexus']:
  print(k, [n for n in pn if n.startswith(k)][:4])
print('raices', [n for n in pn if 'spinal nerve' in n.lower() or n.startswith(('C5','L4','Fifth','Anterior ramus'))][:20])
tc=collections.Counter()
for o in bpy.data.objects:
  s=o.name.rsplit('.',1)[-1] if '.' in o.name else ''
  tc[(s,o.type)]+=1
print(tc.most_common(25))
# ejemplo de .j / .g / .i / .s en huesos
sk=bpy.data.collections['1: Skeletal system']
for suf in ['j','i','g','s','l','r']:
  ej=[o for o in sk.objects if o.name.endswith('.'+suf) and o.type=='MESH'][:3]
  print(suf,[(o.name,len(o.data.polygons),o.hide_viewport,o.hide_get(), o.parent.name if o.parent else None) for o in ej])
mu=bpy.data.collections['4: Muscular system']
for suf in ['j','g','l']:
  ej=[o for o in mu.objects if o.name.endswith('.'+suf) and o.type=='MESH'][:4]
  print('mus',suf,[(o.name,len(o.data.polygons), o.parent.name if o.parent else None) for o in ej])
