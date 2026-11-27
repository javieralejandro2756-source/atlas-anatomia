import bpy, sys, re, json
bpy.ops.wm.open_mainfile(filepath=sys.argv[1], load_ui=False)
nv=[o.name for o in bpy.data.objects if o.type=='CURVE' and any(c.name.startswith('7:') for c in o.users_collection)]
print('plexo', [n for n in nv if 'plexus' in n.lower()][:20])
print('ramos/raices', [n for n in nv if re.search(r'(ramus|root|cervical nerve|lumbar nerve|sacral nerve|thoracic nerve|spinal nerve|\b[CTLS]\d)', n, re.I)][:40])
mu=[o for o in bpy.data.collections['4: Muscular system'].objects if o.type=='MESH' and len(o.data.polygons)>0]
base=sorted({re.sub(r'\.(l|r|j)$','',o.name) for o in mu})
ins=[o for o in bpy.data.collections['2: Muscular insertions'].objects]
ib=sorted({re.sub(r'\.[oe]\d?[lr]$','',o.name) for o in ins})
print('mallas musculo con geometria', len(mu), 'nombres unicos', len(base), 'tris', sum(len(p.vertices)-2 for o in mu for p in o.data.polygons))
print('musculos con zona origen/insercion', len(ib), 'de', len(base))
json.dump({'musculos':base,'con_zonas':ib,'nervios':sorted({re.sub(r'\.(l|r)$','',n) for n in nv})}, open('/home/user/atlas/datos/nombres_atlas.json','w'), indent=0)
