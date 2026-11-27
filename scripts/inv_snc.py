import bpy, sys, collections, re
bpy.ops.wm.open_mainfile(filepath=sys.argv[1], load_ui=False)
col = bpy.data.collections['7: Nervous system & Sense organs']
def cadena(o):
    c=[];p=o.parent
    while p: c.append(p.name); p=p.parent
    return c
grupos=collections.defaultdict(list)
for o in col.objects:
    if o.type not in ('MESH','CURVE'): continue
    if o.type=='MESH' and not len(o.data.polygons): continue
    if re.search(r'\.(g|t|s|st|j)$', o.name): continue
    ch=cadena(o)
    clave=' > '.join(reversed(ch[:3])) if ch else '(sin padre)'
    grupos[clave].append((o.name,o.type,len(o.data.polygons) if o.type=='MESH' else 0))
for k,v in sorted(grupos.items(), key=lambda x:-len(x[1])):
    print(f'== {k}  ({len(v)})')
    print('   ', sorted({re.sub(r"\.(l|r)$","",n) for n,_,_ in v})[:80])
todos=[o.name for o in bpy.data.objects]
print('BRODMANN:', [n for n in todos if re.search(r'brodmann|area \d', n, re.I)][:30])
print('LOBULOS:', [n for n in todos if re.search(r'lobe', n, re.I)][:30])
