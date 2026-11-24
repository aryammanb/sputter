from pathlib import Path
import json
import cadquery as cq
P=Path(__file__).resolve().parent;R=P.parent;V=cq.Vector
def cyl(r,y,h):return cq.Solid.makeCylinder(r,h,V(0,y,0),V(0,1,0))
def ring(ro,ri,y,h):return cyl(ro,y,h).cut(cyl(ri,y-.01,h+.02))
part=ring(2.8,1.65,-68,22).fuse(ring(5.8,1.65,-70.5,2.5)).fuse(ring(5.8,4,-78,7.5)).fuse(ring(8.8,4,-78,2)).clean()
assert part.isValid() and len(part.Solids())==1
cq.exporters.export(part,str(P/'Single piece PTFE with outward lip - R02.step'))
X,Z=38.2146818113899,10.239593130374201
crop=cq.Solid.makeBox(20,48,20,V(-10,-80,-10))
def source(name):return cq.importers.importStep(str(R/'source'/f'{name}.step')).val().translate((-X,0,-Z))
ground=source('Boden').cut(cyl(6,-75,7)).intersect(crop)
bolt=cyl(1.5,-70.5,35).fuse(cyl(2.75,-73.5,3)).cut(cyl(1.2,-73.6,1.6))
parts=[('Single PTFE part','ptfe',part),('Grounded Boden','ground',ground),('Metal screw / live','live',bolt),('Live steel spacer','live',source('Abstandshalter').intersect(crop)),('Main PTFE seal ring','main',source('Isolator').intersect(crop))]
half=cq.Solid.makeBox(50,100,100,V(-50,-100,-50))
records=[]
def mesh(s):
 v,f=s.tessellate(.08,.25)
 return {'v':[[round(p.x,4),round(p.y+62,4),round(p.z,4)] for p in v],'f':f}
for name,role,s in parts:
 assert s.isValid() and len(s.Solids())==1,name
 records.append({'name':name,'role':role,'full':mesh(s),'section':mesh(s.intersect(half))})
contacts=[]
for i,(n,r,s) in enumerate(parts):
 for m,k,t in parts[i+1:]:
  c=s.intersect(t);vol=c.Volume() if c.Solids() else 0
  if vol>1e-4:contacts.append({'a':n,'b':m,'volume_mm3':vol})
assert len(contacts)==1 and contacts[0]['a']=='Metal screw / live' and contacts[0]['b']=='Live steel spacer',contacts
dest=Path('C:/Users/Aryamman/.codex/visualizations/2026/11/19/01a1f594-d837-7b70-8c70-7c7ffe09a027');dest.mkdir(parents=True,exist_ok=True)
(dest/'single-ptfe-outward-lip-geometry.json').write_text(json.dumps(records,separators=(',',':')))
report={'scope':'One-piece captured PTFE sleeve, bearing shoulder and guard wall. Local concept only; not released manufacture or RF qualification.','single_part_valid_solids':1,'cup_OD_mm':11.6,'cup_ID_mm':8,'sleeve_OD_ID_length_mm':[5.6,3.3,22],'bearing_floor_thickness_mm':2.5,'overall_length_mm':32,'ground_pocket_diameter_mm':12,'head_recess_from_cup_mouth_mm':4.5,'metal_screw':'M3x35 study, 5.5mm nominal entry into source spacer including chamfer.','retention':'Metal head bears directly on integral PTFE shoulder; shoulder seats on grounded pocket floor. No guard retention thread.','nominal_thread_contacts':contacts,'limits':'PTFE creep, preload, local stress, thermal fits, full-assembly clearance and RF insulation remain to verify. Open tool-access end shown; no cap or arc-free performance claimed.'}
report.update({'scope':'R02 one-piece captured PTFE sleeve, bearing shoulder, guard wall and outward lip. Local concept only; not released manufacture or RF qualification.','revision':'R02 outward lip','outward_lip_OD_mm':17.6,'outward_lip_radial_projection_beyond_cup_mm':3,'outward_lip_thickness_mm':2,'outward_lip_nearest_face_to_ground_face_axial_gap_mm':2,'outward_lip_overlap_beyond_12mm_pocket_edge_radial_mm':2.8,'installation':'Sleeve and cup insert through existing proposed bores from the head side; larger outward lip stays outside the hole. Integral shoulder is captured by metal head.','guard_projects_beyond_ground_face_before_lip_mm':2})
reopened=cq.importers.importStep(str(P/'Single piece PTFE with outward lip - R02.step')).val().Solids();assert len(reopened)==1 and reopened[0].isValid();assert abs(reopened[0].Volume()-part.Volume())<part.Volume()*1e-8
a=cq.Assembly(name='R02 outward lip - local section context')
for n,r,s in parts:a.add(s,name=n.replace('/','-'))
a.save(str(P/'Single piece PTFE outward lip - local context R02.step'))
source=cq.importers.importStep(str(R/'Advanced Tinkering magnetron - full reconstruction.step')).val().Solids();audit=json.loads((R/'native-assembly-audit.json').read_text(encoding='utf-8-sig'))
lip=ring(8.8,5.8,-78,2)
places=[q for q in audit['components'] if q['name'].startswith('03') and 'shoulder sleeve' in q['name']];assert len(places)==12
def overlap(a,b):
 a=a.BoundingBox();b=b.BoundingBox();return all(getattr(a,k+'min')<getattr(b,k+'max')-1e-6 and getattr(b,k+'min')<getattr(a,k+'max')-1e-6 for k in ['x','y','z'])
hits=[]
for q in places:
 x,y,z=[v*1000 for v in q['transform'][9:12]];s=lip.translate((x,0,z))
 for i,t in enumerate(source):
  if not overlap(s,t):continue
  c=s.intersect(t);v=c.Volume() if c.Solids() else 0
  if v>1e-4:hits.append({'position':q['name'],'source_solid_index':i,'volume_mm3':v})
report.update({'valid_solid_on_part_step_reimport':True,'added_lip_envelope_positions_checked':12,'added_lip_intersections_with_source':hits,'adjacent_lip_edge_gap_mm':2*39.5625*__import__('math').sin(__import__('math').pi/12)-17.6})
assert not hits,hits
(P/'Geometry verification.json').write_text(json.dumps(report,indent=2));print(json.dumps({'part_valid':True,'added_lip_hits':hits,'mesh_bytes':(dest/'single-ptfe-outward-lip-geometry.json').stat().st_size,'contacts':contacts},indent=2))
