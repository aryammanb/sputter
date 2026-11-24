from pathlib import Path
import json,math
import numpy as np
import cadquery as cq
P=Path(__file__).resolve().parent;V=cq.Vector
meta=json.loads((P/'parts.json').read_text());report=json.loads((P/'Geometry verification.json').read_text())
def bbox(s):
 b=s.BoundingBox();return np.array([b.xmin,b.ymin,b.zmin,b.xmax,b.ymax,b.zmax])
def load(version,filename):
 solids=cq.importers.importStep(str(P/filename)).val().Solids();available=set(range(len(solids)));items=[];bounds=[bbox(s) for s in solids];volumes=[s.Volume() for s in solids]
 for q in meta[version]:
  box=np.array(q['bbox_mm']);j=min(available,key=lambda j:np.linalg.norm(bounds[j]-box)+abs(volumes[j]-q['volume_mm3'])*1e-5)
  # Meshing can enlarge OCC tolerance-based boxes; volume independently identifies the solid.
  assert max(abs(bounds[j]-box))<1.,(q['name'],bounds[j],box)
  assert abs(volumes[j]-q['volume_mm3'])<max(1e-4,q['volume_mm3']*1e-6)
  available.remove(j);s=solids[j];assert s.isValid();items.append({**q,'shape':s})
 assert not available
 print('Reimport validated',version,len(items),flush=True)
 return items
old=load('old','Original R03 comparison.step');new=load('new','Proposed twelve stack mechanical study.step')
byname={q['name']:q for q in old};bynew={q['name']:q for q in new};contacts=[]
for h in report['contacts_involving_changed_components']:
 a,b=h['a'],h['b'];basevolume=0
 if a in byname and b in byname:
  c=byname[a]['shape'].intersect(byname[b]['shape']);basevolume=c.Volume() if c.Solids() else 0
 d={**h,'baseline_volume_mm3':basevolume,'volume_change_mm3':h['volume_mm3']-basevolume}
 d['classification']='Inherited nominal screw/thread envelope' if abs(d['volume_change_mm3'])<1e-3 else 'REVIEW'
 # The replacement backplate uses straight minor bores. The source has a .25mm entry chamfer.
 expected_chamfer=math.pi*.25*((1.916**2+1.916*1.666+1.666**2)/3-1.666**2)
 if 'closure' in [h['role_a'],h['role_b']] and any(k in [h['role_a'],h['role_b']] for k in ['yokebolt','rfhot']) and abs(d['volume_change_mm3']-expected_chamfer)<1e-4:
  d['classification']='Nominal screw/thread envelope; source .25mm bore-entry chamfer omitted in replacement study solid'
 contacts.append(d)
assert not [h for h in contacts if h['classification']=='REVIEW'],contacts
def role(items,k):return next(q['shape'] for q in items if q['role']==k)
oldcool,oldclose=role(old,'cooler'),role(old,'closure')
newcool,newclose=role(new,'cooler'),role(new,'closure')
naive=cq.Solid.makeCylinder(10.5,20.5,V(0,-22.5,0),V(0,1,0))
naivefacts={}
for name,s in [('cooling_body',oldcool),('backplate',oldclose)]:
 c=s.intersect(naive);naivefacts[name+'_material_removed_by_D21_bore_mm3']=c.Volume()
def ann(ri,ro,y,h):
 return cq.Solid.makeCylinder(ro,h,V(0,y,0),V(0,1,0)).cut(cq.Solid.makeCylinder(ri,h+.02,V(0,y-.01,0),V(0,1,0)))
channel=ann(15.5,20.5,-9,7)
assert abs(channel.intersect(newcool).Volume())<1e-5
assert abs(newcool.BoundingBox().ymax-oldcool.BoundingBox().ymax)<1e-5
assert max(abs(bbox(newcool)-bbox(oldcool)))<1e-5
assert max(abs(bbox(newclose)-bbox(oldclose)))<1e-5
report.update(step_reimport_valid_solids={'old':len(old),'new':len(new)},contact_classification=contacts,unexplained_changed_component_interferences=0,naive_enlargement=naivefacts,outer_envelopes_preserved=True,new_annular_channel_volume_ml=channel.Volume()/1000,new_channel_solid_obstruction_mm3=channel.intersect(newcool).Volume(),nearest_outer_well_to_backplate_counterbore_land_mm=math.sqrt(29**2+31.5**2-2*29*31.5*math.cos(math.radians(15)))-3.2-2.85)
report['retained_component_instances']=sum(not q['changed'] for q in new)
report['changed_component_instances']=sum(q['changed'] for q in new)
(P/'Geometry verification.json').write_text(json.dumps(report,indent=2))
print(json.dumps({k:v for k,v in report.items() if k not in ['contacts_involving_changed_components','contact_classification']},indent=2),flush=True)
