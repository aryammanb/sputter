from pathlib import Path
import json,struct,csv,math
import numpy as np
import cadquery as cq
P=Path(__file__).resolve().parent;R=P.parent;OLD=R/'integrated-single-coax-r02';V=cq.Vector
metadata=json.loads((OLD/'render-parts.json').read_text(encoding='utf-8'))
source=cq.importers.importStep(str(OLD/'STEP delivery'/'Integrated single coax magnetron R02.step')).val().Solids();assert len(source)==129
def string(f):
 b=f.read(1)
 if not b:return None
 n=b[0]&127;shift=7
 while b[0]&128:b=f.read(1);n|=(b[0]&127)<<shift;shift+=7
 return f.read(n).decode()
boxes=[]
with (OLD/'integrated-mesh.bin').open('rb') as f:
 while string(f):
  string(f);n=struct.unpack('<i',f.read(4))[0];a=np.frombuffer(f.read(n*36),'<f4').reshape(-1,3);boxes.append(np.r_[a.min(0),a.max(0)])
def bbox(s):
 b=s.BoundingBox();return np.array([b.xmin,b.ymin,b.zmin,b.xmax,b.ymax,b.zmax])
available=set(range(129));items=[]
bounds=[bbox(s) for s in source]
for q,box in zip(metadata,boxes):
 j=min(available,key=lambda j:np.linalg.norm(bounds[j]-box));assert np.max(np.abs(bounds[j]-box))<.12,(q['name'],bounds[j],box);available.remove(j);items.append({**q,'shape':source[j]})
print('Mapped all129 source components',flush=True)
audit=json.loads((R/'native-assembly-audit.json').read_text(encoding='utf-8-sig'));poses={q['name']:q['transform'][9:12] for q in audit['components']}
cup=cq.importers.importStep(str(R/'single-piece-ptfe-r02'/'Single piece PTFE with outward lip - R02.step')).val();assert cup.isValid()
cup_positions=[];changed=[];new_shapes=[]
for q in items:
 if 'shoulder sleeve fitted' in q['file']:
  x,y,z=[v*1000 for v in poses[q['name']]];q['shape']=cup.translate((x,0,z));cup_positions.append((x,z));q.update(file='R03 One piece PTFE outward lip cup.STEP',kind='R03 proposed update',note='One-piece PTFE sleeve, shoulder, guard and radial lip; captured by metal screw. No arc-free rating.');changed.append(q['name']);new_shapes.append(q)
 elif q['name'].startswith('03') and 'M3x35' in q['file']:
  q['shape']=q['shape'].translate((0,-1,0));q.update(kind='R03 proposed update',note='Original M3x35 study screw moved1mm rearward for2.5mm PTFE bearing shoulder. Nominal source entry5.5mm includes chamfer.');changed.append(q['name']);new_shapes.append(q)
assert len(cup_positions)==12
base=next(q for q in items if 'R02 Boden' in q['file']);s=base['shape']
for x,z in cup_positions:s=s.cut(cq.Solid.makeCylinder(6,7,V(x,-75,z),V(0,1,0)))
assert s.isValid() and len(s.Solids())==1
print('Updated twelve cups, screws and base pockets',flush=True)
base.update(shape=s,file='R03 Boden - twelve D12 cup pockets.STEP',kind='R03 proposed update',note='R02 base and blind RF ground anchor retained; twelve screw head pockets enlarged to12mm, original seating floors retained.');changed.append(base['name']);new_shapes.append(base)
def role(q):
 f=q['file'];n=q['name']
 if 'One piece PTFE' in f:return 'cups'
 if 'R03 Boden' in f:return 'base'
 if 'service tube' in f:return 'kftube'
 if 'blue coolant hose' in f:return 'hoses'
 if any(t in f for t in ['Continuous coax','Continuous center','RF center conductor','Additional dielectric']):return 'coax'
 if any(t in f for t in ['Copper terminal','M4x20 live','TE323086']):return 'rfhot'
 if q['kind'].startswith('R02'):return 'rfground'
 if f in {'Kuehlkoerper.SLDPRT','Backplate.SLDPRT','Magnet Joke.SLDPRT','Abstandshalter.SLDPRT','Isolator.SLDPRT','Target Klemme.SLDPRT','Groundshield Rohr.SLDPRT','Dunkelraumabschirmung.SLDPRT'}:return {'Kuehlkoerper.SLDPRT':'cooler','Backplate.SLDPRT':'closure','Magnet Joke.SLDPRT':'yoke','Abstandshalter.SLDPRT':'spacer','Isolator.SLDPRT':'isolator','Target Klemme.SLDPRT':'clamp','Groundshield Rohr.SLDPRT':'shieldtube','Dunkelraumabschirmung.SLDPRT':'darkcap'}[f]
 for t,k in [('outer magnet','outermag'),('center magnet','centermag'),('O-ring ID14p5','waterseal'),('O-ring ID35x','waterseal'),('O-ring ID76x','headseal'),('M3x16','backbolts'),('M4x10','yokebolt'),('fitting','fittings'),('titanium target','target'),('M3x8','targetbolts'),('M3x6','upperbolts'),('flange clamp half','kfclamps'),('KF16 centering','kfcenter'),('KF16 O-ring','kfseal'),('M5x20','kfbolts'),('M4x8','lowerbolts')]:
  if t in f:return k
 if 'O-ring ID62x' in f:return 'upper62' if poses[n][1]*1000>-43 else 'lower62'
 if 'M3x35' in f:return 'basebolts' if n.startswith('03') else 'headbolts'
 raise ValueError(q)
for q in items:q['role']=role(q)
assert len(items)==129 and all(q['shape'].isValid() and len(q['shape'].Solids())==1 for q in items)
colors={'cooler':(.83,.49,.27),'closure':(.83,.49,.27),'outermag':(.22,.4,.78),'centermag':(.78,.22,.23),'cups':(.91,.88,.77),'isolator':(.88,.86,.77),'coax':(.25,.28,.31),'rfhot':(.88,.48,.25),'rfground':(.4,.6,.7),'hoses':(.12,.4,.78)}
assembly=cq.Assembly(name='Current magnetron R03 - walkthrough assembly')
for i,q in enumerate(items):assembly.add(q['shape'],name=f'{i+1:03}_'+q['file'].replace(' ','_').replace('.SLDPRT','').replace('.STEP',''),color=cq.Color(*colors.get(q['role'],(.54,.62,.68))))
out=P/'Current magnetron R03 - complete study assembly.step';assembly.save(str(out));re=cq.importers.importStep(str(out)).val().Solids();assert len(re)==129 and all(s.isValid() for s in re)
v0=sum(q['shape'].Volume() for q in items);v1=sum(s.Volume() for s in re);assert abs(v0-v1)<v0*1e-7
print('Full STEP assembly reimported:129 valid solids',flush=True)
def write_string(f,s):
 b=s.encode();n=len(b)
 while n>=128:f.write(bytes([(n&127)|128]));n>>=7
 f.write(bytes([n]));f.write(b)
triangles=0
with (P/'latest-mesh.bin').open('wb') as f:
 for q in items:
  vs,fs=q['shape'].tessellate(.10,.25);v=np.array([p.toTuple() for p in vs]);a=v[np.array(fs)].astype('<f4');write_string(f,q['name']);write_string(f,q['file']);f.write(struct.pack('<i',len(a)));f.write(a.tobytes());triangles+=len(a)
def overlap(a,b):
 a=bbox(a);b=bbox(b);return all(a[i]<b[i+3]-1e-6 and b[i]<a[i+3]-1e-6 for i in range(3))
hits=[]
for q in new_shapes:
 if q is base:continue # Subtractive changes cannot add source contacts.
 for t in items:
  if q is t or t in new_shapes and items.index(t)<items.index(q):continue
  if not overlap(q['shape'],t['shape']):continue
  c=q['shape'].intersect(t['shape']);v=c.Volume() if c.Solids() else 0
  if v>1e-4:hits.append({'a':q['name'],'b':t['name'],'volume_mm3':v,'expected_nominal_thread':q['role']=='basebolts' and t['role']=='spacer'})
assert len(hits)==12 and all(q['expected_nominal_thread'] for q in hits),hits
metadata=[{k:v for k,v in q.items() if k!='shape'} for q in items];(P/'parts.json').write_text(json.dumps(metadata,indent=2))
with (P/'Current assembly BOM.csv').open('w',newline='',encoding='utf-8-sig') as f:
 w=csv.writer(f);w.writerow(['Instance','Part','Role','Evidence','Notes'])
 for q in items:w.writerow([q['name'],q['file'],q['role'],q['kind'],q['note']])
report={'components':129,'valid_solids_on_step_reimport':129,'changed_instances_from_single_coax_R02':len(changed),'new_screw_insulators':12,'modified_base_counterbores':12,'base_screws_repositioned':12,'triangles':triangles,'volume_relative_difference':abs(v0-v1)/v0,'new_contacts':hits,'scope':'Latest combined mechanical study for video: original geometry plus R02 single coax and one-piece outward-lip PTFE proposal. Not a released or RF-qualified gun. Source target thickness, utility fitting/tube references and gland uncertainty remain.','native_solidworks':'Not supplied for this combined revision; STEP exchange assembly supplied.'}
(P/'Assembly verification.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k!='new_contacts'},indent=2),flush=True)
