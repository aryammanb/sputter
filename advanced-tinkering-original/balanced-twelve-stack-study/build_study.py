from pathlib import Path
import json, math, struct, csv
import numpy as np
import cadquery as cq

P=Path(__file__).resolve().parent
R=P.parent
BASE=R/'latest-full-walkthrough'
V=cq.Vector
def cyl(r,y,h,x=0,z=0): return cq.Solid.makeCylinder(r,h,V(x,y,z),V(0,1,0))
def ann(ri,ro,y,h): return cyl(ro,y,h).cut(cyl(ri,y-.01,h+.02))
def bbox(s):
 b=s.BoundingBox();return np.array([b.xmin,b.ymin,b.zmin,b.xmax,b.ymax,b.zmax])
def string(f):
 b=f.read(1)
 if not b:return None
 n=b[0]&127;shift=7
 while b[0]&128:
  b=f.read(1);n|=(b[0]&127)<<shift;shift+=7
 return f.read(n).decode()
def write_string(f,s):
 b=s.encode();n=len(b)
 while n>=128:f.write(bytes([(n&127)|128]));n>>=7
 f.write(bytes([n]));f.write(b)
meta=json.loads((BASE/'parts.json').read_text())
boxes=[]
with (BASE/'latest-mesh.bin').open('rb') as f:
 while string(f):
  string(f);n=struct.unpack('<i',f.read(4))[0];v=np.frombuffer(f.read(n*36),'<f4').reshape(-1,3)
  boxes.append(np.r_[v.min(0),v.max(0)])
solids=cq.importers.importStep(str(BASE/'Current magnetron R03 - complete study assembly.step')).val().Solids()
available=set(range(len(solids)));bounds=[bbox(s) for s in solids];old=[]
for q,box in zip(meta,boxes):
 j=min(available,key=lambda j:np.linalg.norm(bounds[j]-box));assert max(abs(bounds[j]-box))<.12
 available.remove(j);old.append({**q,'shape':solids[j],'changed':False})
print('Mapped latest 129-component baseline',flush=True)
plan=json.loads((R/'construction-plan.json').read_text())
positions=[(m['X'],m['Z']) for m in plan['Magnets']]
newpos=[(x*29/25,z*29/25) for x,z in positions]
proposed=[]
def add(q,shape=None,note=None,**kw):
 d={**q,**kw}
 if shape is not None:d.update(shape=shape,changed=True)
 if note:d['change_note']=note
 proposed.append(d)

for q in old:
 s=q['shape'];k=q['role'];b=bbox(s)
 if k=='cooler':
  # Fill only the original internal pockets, preserving the external envelope and fixing interfaces.
  s=s.fuse(ann(11.0,16.1,-9,7),cyl(6.8,-9,7),*[cyl(4.8,-9,7,x,z) for x,z in positions]).clean()
  s=s.cut(ann(15.5,20.5,-9,7),cyl(10.5,-9,7),*[cyl(3.2,-9,7,x,z) for x,z in newpos]).clean()
  add(q,s,'Center blind well D13 -> D21; outer wells D9 -> D6.4 and PCD50 -> PCD58; coolant annulus R11.05..16.05 -> R15.5..20.5. Original outer envelope and mounting holes retained.')
 elif k=='closure':
  s=cyl(35.75,-22.5,13.5)
  s=cq.Workplane(obj=s).edges().chamfer(.25).val()
  s=s.cut(cyl(10.5,-22.6,13.7),*[cyl(3.2,-22.6,13.7,x,z) for x,z in newpos])
  for m in plan['BackplateScrews']:
   x,z=m['X'],m['Z'];s=s.cut(cyl(1.65,-22.6,13.7,x,z),cyl(2.85,-22.6,4.1,x,z))
  for x in [-18,18]:
   s=s.cut(cyl(2.5,-22.6,13.7,x),cyl(3.975,-22.6,10.1,x))
  for z in [-13.55,13.55]:s=s.cut(cyl(1.666,-22.6,8.1,0,z))
  for ri in [11.5,21.5]:s=s.cut(ann(ri,ri+2.85,-10.45,1.55))
  s=s.clean()
  add(q,s,'Replacement copper backplate: same OD71.5, thickness13.5 and screw patterns; D21 center, D6.4 outer wells PCD58; glands ID23x2 and ID43x2; coolant axes X +/-18 instead of +/-13.55. Threads remain nominal envelopes.')
 elif k=='yoke':
  s=s.fuse(*[cyl(7.3,-32.5,10,x) for x in [-13.55,13.55]]).clean()
  s=s.cut(*[cyl(7,-32.6,10.2,x) for x in [-18,18]]).clean()
  add(q,s,'Coolant fitting clearance holes moved X +/-13.55 -> +/-18. OD71.5, thickness10 and attachment holes retained. Magnetic saturation not assessed.')
 elif k=='outermag':
  x,z=(b[0]+b[3])/2,(b[2]+b[5])/2;x*=29/25;z*=29/25
  for j in range(2):add(q,cyl(3,-22.5+j*10,10,x,z),'Two stock axially magnetized D6x10 N42 discs per outer stack.',name=q['name']+f' / stack disc {j+1}',file='Proposed outer D6x10 N42.step')
 elif k=='centermag':
  add(q,cyl(10,b[1],10),'Stock axially magnetized D20x10 N42 disc; two discs give original20mm pack length.',file='Proposed center D20x10 N42.step')
 elif k=='waterseal':
  inner='14p5' in q['file'];ri=11.5 if inner else 21.5;rm=ri+1.425
  # Installed shape: area-equivalent elliptical section inside the retained 2.85 x 1.45 gland.
  rx=1/.725
  s=cq.Workplane('XY').moveTo(rm,-9.725).ellipse(rx,.725).revolve(360,(0,0),(0,1)).val()
  add(q,s,'Illustrative compressed FKM ring; nominal free ID23x2' if inner else 'Illustrative compressed FKM ring; nominal free ID43x2',file='Proposed inner ID23x2 seal.step' if inner else 'Proposed outer ID43x2 seal.step')
 elif k=='fittings':
  center=(b[0]+b[3])/2;dx=4.45*(1 if center>0 else -1)
  add(q,s.translate((dx,0,0)),'Existing reference fitting envelope moved outward4.45mm; actual fitting identity and engagement remain unconfirmed.')
 elif k=='hoses':
  sign=1 if (b[0]+b[3])>0 else -1
  a=V(18*sign,-29.5,0);b1=V(18*sign,-38,0);b2=V(3*sign,-63,0)
  bend=cq.Edge.makeSpline([b1,V(15*sign,-46,0),V(6*sign,-55,0),b2],tangents=[V(0,-1,0),V(0,-1,0)])
  path=cq.Wire.assembleEdges([cq.Edge.makeLine(a,b1),bend,cq.Edge.makeLine(b2,V(3*sign,-300,0))])
  plane=cq.Plane(origin=a,normal=V(0,-1,0),xDir=V(1,0,0))
  s=cq.Workplane(plane).circle(2).circle(1.25).sweep(path,isFrenet=False).val()
  add(q,s,'Illustrative hose upper route revised for X +/-18 fittings; lower tube route X +/-3 retained. OD4 ID2.5 retained; purchased hose bend radius not validated.')
 else:add(q)

print('Constructed proposed cooling head and 26 magnets',flush=True)
assert len(proposed)==141
for q in proposed:
 assert q['shape'].isValid() and len(q['shape'].Solids())==1,(q['name'],len(q['shape'].Solids()))
print('All141 component solids valid',flush=True)
# Flexible routes are left out of the geometric fit claim until replaced below after inspection.
for q in proposed:
 if q['role'] in ['hoses','fittings']:
  print(q['role'],q['file'],bbox(q['shape']).round(3).tolist(),flush=True)

colors={'cooler':(.83,.46,.25),'closure':(.83,.46,.25),'outermag':(.15,.42,.85),'centermag':(.86,.24,.25),'yoke':(.43,.49,.57),'waterseal':(.12,.15,.16)}
for title,items in [('Original R03 comparison',old),('Proposed twelve stack mechanical study',proposed)]:
 asm=cq.Assembly(name=title)
 for i,q in enumerate(items):asm.add(q['shape'],name=f'{i:03}_{q["role"]}',color=cq.Color(*colors.get(q['role'],(.6,.66,.69))))
 asm.save(str(P/(title+'.step')))
with (P/'meshes.bin').open('wb') as f:
 for version,items in [('old',old),('new',proposed)]:
  for i,q in enumerate(items):
   vs,fs=q['shape'].tessellate(.13,.25);a=np.array([v.toTuple() for v in vs])[np.array(fs)].astype('<f4')
   write_string(f,version);write_string(f,str(i));f.write(struct.pack('<i',len(a)));f.write(a.tobytes())
serial={v:[{**{k:w for k,w in q.items() if k!='shape'},'bbox_mm':bbox(q['shape']).tolist(),'volume_mm3':q['shape'].Volume()} for q in items] for v,items in [('old',old),('new',proposed)]}
(P/'parts.json').write_text(json.dumps(serial,indent=2))
for q in proposed:
 if q['role'] in ['cooler','closure','yoke']:
  cq.exporters.export(q['shape'],str(P/('Proposed '+q['role']+'.step')))

def overlap(a,b):return all(a[i]<b[i+3]-1e-5 and b[i]<a[i+3]-1e-5 for i in range(3))
hits=[]
for i,q in enumerate(proposed):
 for j in range(i+1,len(proposed)):
  t=proposed[j]
  if not(q['changed'] or t['changed']) or not overlap(bbox(q['shape']),bbox(t['shape'])):continue
  c=q['shape'].intersect(t['shape']);vol=c.Volume() if c.Solids() else 0
  if vol>1e-4:hits.append({'a':q['name'],'b':t['name'],'role_a':q['role'],'role_b':t['role'],'volume_mm3':vol})
print('Changed-component contacts:',json.dumps(hits,indent=2),flush=True)
report={'baseline_components':len(old),'proposed_components':len(proposed),'valid_component_solids':len(proposed),'contacts_involving_changed_components':hits,'dimensions_mm':{'center_magnet_diameter':20,'center_bore_diameter':21,'outer_magnet_diameter':6,'outer_bore_diameter':6.4,'outer_pcd':58,'coolant_inner_radius':15.5,'coolant_outer_radius':20.5,'coolant_depth':7,'coolant_axes_x':[-18,18],'inner_seal_free_ID':23,'outer_seal_free_ID':43,'seal_cross_section':2,'gland_width':2.85,'gland_depth':1.45},'analytic_lands_mm':{'center_bore_to_inner_gland':11.5-10.5,'inner_gland_to_coolant':15.5-14.35,'coolant_to_outer_gland':21.5-20.5,'outer_gland_to_outer_well':29-3.2-24.35,'outer_well_to_backplate_edge':35.75-29-3.2,'center_bore_to_port_counterbore':18-3.975-10.5,'center_pole_to_yoke_port_clearance':18-7-10},'scope':'Mechanical concept; balance, cooling, pressure, seal reliability and RF performance not established.'}
(P/'Geometry verification.json').write_text(json.dumps(report,indent=2))
with (P/'Part change register.csv').open('w',newline='',encoding='utf-8-sig') as f:
 w=csv.writer(f);w.writerow(['Component','Role','Status','Change'])
 for q in proposed:w.writerow([q['name'],q['role'],'Modified or replaced' if q['changed'] else 'Retained',q.get('change_note','Geometry retained from latest R03 baseline')])
print('Study STEP assemblies, meshes and change register exported',flush=True)
