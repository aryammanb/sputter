from pathlib import Path
import json,math,struct,csv
import cadquery as cq
import numpy as np
P=Path(__file__).resolve().parent
V=cq.Vector
parts=[]
def cyl(r,h,z=0,x=0,y=0):return cq.Solid.makeCylinder(r,h,V(x,y,z),V(0,0,1))
def ann(ri,ro,h,z=0):return cyl(ro,h,z).cut(cyl(ri,h,z))
def box(x,y,z,dx,dy,dz):return cq.Solid.makeBox(dx,dy,dz,V(x,y,z))
def add(name,s,role,color,note):
 assert s.isValid(),name
 parts.append(dict(name=name,shape=s,role=role,color=color,note=note))
def helix_profile(radius,pitch,height,z,width,crest):
 path=cq.Wire.makeHelix(pitch,height,radius)
 prof=cq.Workplane('XZ').polyline([(radius-.12,-width/2),(crest,0),(radius-.12,width/2)]).close()
 return prof.sweep(cq.Workplane(obj=path),isFrenet=True).val().translate((0,0,z))

# Overall catalogue reference: KF25 flange OD39.88, body/cap assembly50.8 long,
# tube25.4 OD. All detailed thread/seat dimensions below are explanatory design.
body=ann(12.95,19.94,4).fuse(ann(12.95,19,20,4),ann(12.95,17.9,19,24))
male=helix_profile(17.9,2,20,23,1.15,18.5).intersect(cyl(19,19,24))
body=body.fuse(male).clean().cut(cyl(16.1,5,39.8))
print('External helical body thread built',flush=True)
cap=ann(18.0,22,11.7,32).fuse(ann(12.95,22,7.1,43.7))
female_cut=helix_profile(17.9,2,16,29,1.55,18.8)
cap=cap.cut(female_cut).clean()
for i in range(48):
 a=2*math.pi*i/48
 cap=cap.cut(cyl(.38,15,35.8,22*math.cos(a),22*math.sin(a)))
cap=cap.clean()
print('Separate female-threaded cap built',flush=True)
follower=ann(12.9,16,1.8,41.9)
def seal_shape(compression=1):
 # Preserve elliptical section area while illustrating axial squeeze. Not a seal simulation.
 rz=(2.62-.52*compression)/2;rx=1.31**2/rz
 rm=12.7+rx;zc=39.8+rz
 return cq.Workplane('XZ').moveTo(rm,zc).ellipse(rx,rz).revolve(360,(0,0),(0,1)).val()
seal=seal_shape(1)
add('Adapter body with male thread',body.translate((0,0,333)),'body',(.56,.66,.74),'Catalogue envelope reference; male helix pitch2, major37 are illustrative, not manufacturer thread specification.')
add('Threaded cap - separate moving part',cap.translate((0,0,333)),'cap',(.72,.77,.8),'Female helix matched to illustrative2mm pitch. 4mm lift corresponds to two turns. Cap OD44 and details illustrative.')
add('Compression follower',follower.translate((0,0,333)),'follower',(.88,.66,.25),'Illustrative force-transmitting follower; actual supplier cross-section unverified.')
add('Tube compression O ring',seal.translate((0,0,333)),'tube_seal',(.13,.65,.42),'O-V120 free nominal25.07ID x2.62 section; installed/compressed geometry is explanatory, not validated seal design.')
add('KF face seal / centering space',ann(13,16,3,330),'kf_seal',(.16,.22,.26),'KF face seal separate from tube O-ring. Through-bore and actual centering-ring fit remain unresolved.')

# Opening two-piece KF clamp with hinge and separate wing screw.
ring=ann(20.05,25.5,12,326)
# Internal relieved middle band, leaving retaining lips at top/bottom.
ring=ring.cut(ann(20.05,22.2,7,328.5))
left=ring.intersect(box(-40,-40,324,39.6,80,18)).fuse(box(-12,-34,327,11.6,12,10),box(-7,20,327,6.6,10,10))
right=ring.intersect(box(.4,-40,324,40,80,18)).fuse(box(.4,-34,327,11.6,12,10),box(.4,20,327,6.6,10,10))
bolt=cq.Solid.makeCylinder(2,32,V(-16,-29,332),V(1,0,0))
for name,s,role in [('KF clamp left jaw',left,'clamp_left'),('KF clamp right jaw',right,'clamp_right')]:
 s=s.cut(cq.Solid.makeCylinder(2.3,40,V(-20,-29,332),V(1,0,0)))
 add(name,s,role,(.4,.49,.57),'Functional split-clamp illustration; purchased clamp profile, hinge and fastener dimensions not qualified.')
wing=box(13,-35,330.8,3,12,2.4).fuse(cq.Solid.makeCylinder(4,4,V(12,-29,332),V(1,0,0))).cut(cq.Solid.makeCylinder(2,6,V(11,-29,332),V(1,0,0)))
add('KF clamp wing screw',bolt,'clamp_bolt',(.55,.6,.65),'Illustrative clamp fastener; independent of compression cap.')
add('KF clamp wing nut',wing,'clamp_wing',(.68,.73,.77),'Turns to secure KF flange joint, not to grip gun tube.')
add('KF clamp hinge pin',cyl(1.8,14,325,0,25),'clamp_pin',(.55,.6,.65),'Hinge axis for opening clamp jaws.')
# Cap index line makes its rotation visible even at full turns.
add('Cap rotation index mark',box(20.9,-.7,379,1.3,1.4,4),'cap_mark',(.98,.73,.25),'Visual index mark only, not an extra purchased component.')

def save(name,exploded=False):
 a=cq.Assembly(name=name)
 for i,q in enumerate(parts):
  s=q['shape'];r=q['role']
  if exploded:
   dz={'cap':35,'cap_mark':35,'follower':20,'tube_seal':10}.get(r,0)
   s=s.translate((0,0,dz))
  a.add(s,name=f'{i:02}_{q["name"]}',color=cq.Color(*q['color']))
 a.save(str(P/(name+'.step')))
save('Refined compression fitting - assembled')
save('Refined compression fitting - exploded',True)
for q in parts:
 if q['role'] in ['body','cap','follower','tube_seal']:cq.exporters.export(q['shape'],str(P/(q['role']+'.step')))

# Render meshes include both complete and stationary-section versions.
serial=[]
with (P/'fitting-mesh.bin').open('wb') as f:
 for q in parts:
  for state in ['full','section']:
   s=q['shape']
   if state=='section' and q['role'] in ['body','cap','follower','tube_seal','kf_seal']:
    s=s.cut(box(-50,-50,320,100,50,120))
   vs,fs=s.tessellate(.12,.2);a=np.array([v.toTuple() for v in vs],dtype=np.float32)[np.array(fs)].astype('<f4')
   f.write(struct.pack('<I',len(a)));f.write(a.tobytes())
  serial.append({k:v for k,v in q.items() if k!='shape'})
(P/'fitting-parts.json').write_text(json.dumps(serial,indent=2))
report={'catalogue_reference':{'part':'QF25XVC100','tube_OD':25.4,'KF_flange_OD':39.88,'overall_length':50.8},
 'illustrative_details':{'thread_pitch':2,'male_thread_major_diameter':37,'cap_OD':44,'cap_loosen_lift':4,'cap_turns_for_4mm':2,'seal_axial_compression':.52},
 'checks':{'all_shapes_valid':all(q['shape'].isValid() for q in parts),'body_cap_overlap_mm3':body.intersect(cap).Volume(),'tube_clearance_in_body_diameter':25.9-25.4},
 'scope':'Mechanism illustration, not controlled supplier CAD. Detailed thread, seal seat and clamp geometry need supplier verification.'}
(P/'Fitting geometry checks.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report['checks']),flush=True)

# Refine chamber CAD as a separate revision; leave the approved walkthrough untouched.
src=P.parent/'complete-chamber-r01'/'build_assembly.py'
code=src.read_text().split('outparts=P/')[0]
env={'__file__':str(src),'__name__':'chamber_build_for_fitting_refinement'}
exec(compile(code,str(src),'exec'),env)
old=env['items'];remaining=[q for q in old if q['role'] not in ['gun_adapter','gun_mount_clamp','gun_mount_seal']]
for q in parts:remaining.append(q|{'group':'fitting'})
for title,da,sa in [('Chamber R02 - refined fitting door closed',0,0),('Chamber R02 - refined fitting door open',-110,80)]:
 assembly=cq.Assembly(name=title)
 for i,q in enumerate(remaining):
  s=q['shape'] if q['group']=='fitting' else env['state_shape'](q,da,sa)
  assembly.add(s,name=f'{i:03}_{q["name"].replace("/","_")}',color=cq.Color(*q['color']))
 assembly.save(str(P/(title+'.step')))
print('Updated chamber CAD exported with separate fitting mechanism',flush=True)
