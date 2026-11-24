from pathlib import Path
import json
import cadquery as cq
P=Path(__file__).resolve().parent;R=P.parent;V=cq.Vector
X,Z=38.2146818113899,10.239593130374201
def cyl(r,y,h):return cq.Solid.makeCylinder(r,h,V(0,y,0),V(0,1,0))
def ring(ro,ri,y,h):return cyl(ro,y,h).cut(cyl(ri,y-.1,h+.2))
crop=cq.Solid.makeBox(16,52,16,V(-8,-84,-8))
def source(name):return cq.importers.importStep(str(R/'source'/f'{name}.step')).val().translate((-X,0,-Z))
# Proposed M12x1 nominal minor bore; upper washer seat diameter12.
ground=source('Boden').cut(cyl(5.4585,-75,4.5)).cut(cyl(6,-70.5,2.5)).intersect(crop)
guard=ring(6,4,-78,8.5).cut(cyl(4.5,-71.1,1.7))
# Cap: nominal M9x1 threaded spigot, no helical threads modeled.
cap=cyl(5.8,-80,2).fuse(cyl(4.5,-78,2))
# Deliberate L-shaped pump-out route: two0.6mm bores intersect atY-79,Z2.
cap=cap.cut(cq.Solid.makeCylinder(.3,3.3,V(0,-79,2),V(0,1,0)))
cap=cap.cut(cq.Solid.makeCylinder(.3,4.5,V(0,-79,1.8),V(0,0,1)))
# Blind external driver slot, separated from cavity and vent.
cap=cap.cut(cq.Solid.makeBox(.8,.65,5,V(1.2,-80.1,-2.5)))
parts=[('Grounded Boden / stepped threaded pocket',ground,'ground'),('Main PTFE ring / retained',source('Isolator').intersect(crop),'ptfe'),('Live spacer / original thread',source('Abstandshalter').intersect(crop),'live'),('Alumina shank sleeve',ring(2.8,1.65,-68,22),'ceramic'),('Alumina bearing washer OD8p8',ring(4.4,1.65,-70.5,2.5),'ceramic'),('Metal bearing washer',ring(3.5,1.65,-71,.5),'live')]
screw=cyl(1.5,-71,35).fuse(cyl(2.75,-74,3)).cut(cyl(1.2,-74.1,1.6));parts.append(('Metal M3x35 screw / live',screw,'live'))
parts += [('PTFE non-load-bearing head guard',guard,'guard'),('PTFE vented removable cap',cap,'guard')]
colors={'ground':(.30,.55,.69),'ptfe':(.70,.73,.69),'live':(.92,.43,.16),'ceramic':(.94,.88,.65),'guard':(.40,.76,.60)}
a=cq.Assembly(name='Recessed live head with vented insulating guard');records=[];contacts=[]
for name,s,role in parts:
 assert s.isValid() and len(s.Solids())==1,name
 a.add(s,name=name.replace('/','-'),color=cq.Color(*colors[role]));v,f=s.tessellate(.035,.12)
 records.append({'name':name,'role':role,'vertices':[[round(t,5) for t in q.toTuple()] for q in v],'faces':f,'volume_mm3':s.Volume()})
for i,(n,s,r) in enumerate(parts):
 for m,t,k in parts[i+1:]:
  q=s.intersect(t);vol=q.Volume() if q.Solids() else 0
  if vol>1e-4:contacts.append({'a':n,'b':m,'volume_mm3':vol})
assert len(contacts)==3,contacts
assert all(('screw' in q['b'] and 'spacer' in q['a']) or ('guard' in q['b'] and 'Boden' in q['a']) or ('cap' in q['b'] and 'guard' in q['a']) for q in contacts),contacts
path=P/'Vented head guard - local mechanical concept.step';a.save(str(path));ss=cq.importers.importStep(str(path)).val().Solids();assert len(ss)==9 and all(s.isValid() for s in ss)
(P/'geometry.json').write_text(json.dumps(records))
report={'scope':'Local one-fastener mechanical visualization; not integrated into all twelve locations or electrically qualified.','valid_solids_on_reimport':9,'source_axis_global_xz_mm':[X,Z],'nominal_thread_contact_intersections':contacts,'metal_screw':'M3x35 retained, underheadY-71, lowest head pointY-74, nominal thread entry5mm including source chamfer.','bearing_washer':'Alumina OD10.4 ID3.3 thickness2.5, reduced OD to pass nominal M12x1 tap-minor bore10.917.','guard':'PTFE OD12 with8mm bore, Y-78 to-71.1. Concept external M12x1 engages Boden for2.9mm. Thread helices and reliefs not modeled. Guard is outside the screw clamp load path.','cap':'PTFE nominal M9x1 spigot, Y-78 to-76; head OD11.6 x2, Y-80 to-78. Threads not modeled. Blind driver slot.','nominal_min_guard_top_to_metal_washer_axial_gap_mm':.1,'guard_top_to_ceramic_bearing_washer_gap_mm':.6,'head_bottom_to_cap_top_axial_gap_mm':2,'head_recess_beyond_guard_lip_mm':4,'guard_lip_beyond_ground_face_mm':4,'cap_bottom_beyond_ground_face_mm':6,'radial_guard_wall_mm':2,'nominal_M9_thread_root_wall_mm':1.5,'vent':'Two intersecting0.6mm bores form90-degree route atY-79,Z2. No straight-through axial hole to head. Vent is not a seal or a qualified arc barrier.','limitations':'Guard thread engagement, tight fits and tolerances need redesign/review before manufacture; 0.1mm nominal washer gap is not a production tolerance. All twelve locations, shield clearance and pressure boundary wall need checks. Pressure, gas, RF waveform, peak voltage and DC bias are unspecified. No arc-free performance, field simulation or voltage rating claimed. PTFE guard can creep; retention/thermal cycling need qualification. Deposited coatings can bridge insulators. Main PTFE sealing ring remains loaded.'}
report.update({'bearing_washer':'Alumina OD8.8 ID3.3 thickness2.5; passes10.917 tap-minor bore and clears overlapping guard lip.','guard':'PTFE OD12, main bore8, upper lip bore9. Y-78 to-69.5. External M12x1 concept engages Boden for3.5mm; helices/reliefs not modeled. Guard is outside main clamping load path.','guard_overlap_around_ceramic_washer_axial_mm':1,'guard_to_ceramic_washer_radial_gap_mm':.1,'guard_top_to_ground_bearing_floor_axial_gap_mm':1.5,'minimum_nominal_guard_lip_wall_mm':1.5})
report.pop('nominal_min_guard_top_to_metal_washer_axial_gap_mm');report.pop('guard_top_to_ceramic_bearing_washer_gap_mm')
report['limitations']=report['limitations'].replace('0.1mm nominal washer gap','0.1mm nominal radial washer gap')
(P/'Geometry checks.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2),flush=True)
