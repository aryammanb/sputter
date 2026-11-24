from pathlib import Path
import json
import cadquery as cq
P=Path(__file__).resolve().parent;P.mkdir(exist_ok=True);R=P.parent
V=cq.Vector;X,Z=38.2146818113899,10.239593130374201
def cyl(r,y,h):return cq.Solid.makeCylinder(r,h,V(0,y,0),V(0,1,0))
def ring(ro,ri,y,h):return cyl(ro,y,h).cut(cyl(ri,y-.1,h+.2))
crop=cq.Solid.makeBox(16,47,16,V(-8,-79,-8))
def source(name):return cq.importers.importStep(str(R/'source'/f'{name}.step')).val().translate((-X,0,-Z))
ground=source('Boden').cut(cyl(6,-75,7)).intersect(crop)
parts=[('Grounded Boden / enlarged head pocket',ground,'ground'),('Main PTFE sealing ring / retained',source('Isolator').intersect(crop),'ptfe'),('Live steel spacer / original tapped bore',source('Abstandshalter').intersect(crop),'live'),('Alumina shank sleeve',ring(2.8,1.65,-68,22),'ceramic'),('Alumina load washer',ring(5.8,1.65,-70.5,2.5),'ceramic'),('Metal load-spreading washer',ring(3.5,1.65,-71,.5),'live')]
screw=cyl(1.5,-71,35).fuse(cyl(2.75,-74,3))
# Socket is a representative round recess; threads omitted.
screw=screw.cut(cyl(1.2,-74.1,1.6));parts.append(('Metal M3x35 screw / live',screw,'live'))
colors={'ground':(.30,.55,.69),'ptfe':(.76,.77,.71),'live':(.92,.43,.16),'ceramic':(.94,.88,.65)}
a=cq.Assembly(name='Metal screw with ceramic isolation - local concept');records=[];contacts=[]
for name,s,role in parts:
 assert s.isValid() and len(s.Solids())==1,name
 a.add(s,name=name.replace('/','-'),color=cq.Color(*colors[role]))
 v,f=s.tessellate(.045,.15)
 records.append({'name':name,'role':role,'vertices':[[round(t,5) for t in p.toTuple()] for p in v],'faces':f,'volume_mm3':s.Volume()})
for i,(n,s,r) in enumerate(parts):
 for m,t,k in parts[i+1:]:
  q=s.intersect(t);vol=q.Volume() if q.Solids() else 0
  if vol>1e-4:contacts.append({'a':n,'b':m,'volume_mm3':vol})
assert len(contacts)==1 and 'spacer' in contacts[0]['a'] and 'screw' in contacts[0]['b'],contacts
a.save(str(P/'Metal screw with ceramic isolation - local concept.step'))
re=cq.importers.importStep(str(P/'Metal screw with ceramic isolation - local concept.step')).val().Solids();assert len(re)==7 and all(s.isValid() for s in re)
(P/'geometry.json').write_text(json.dumps(records))
report={'scope':'Local concept at one existing fastener; source bodies cropped. Not a full gun revision or released machining design.','source_bolt_axis_global_mm':[X,Z],'source_head_counterbore_diameter_mm':8,'proposed_head_counterbore_diameter_mm':12,'sleeve_OD_ID_length_mm':[5.6,3.3,22],'alumina_washer_OD_ID_thickness_mm':[11.6,3.3,2.5],'metal_washer_OD_ID_thickness_mm':[7,3.3,.5],'screw':'Metal M3x35, unchanged nominal length; head moved 1.5mm rearward by proposed bearing stack.','nominal_thread_entry_y_mm':-41,'screw_tip_y_mm':-36,'nominal_engagement_mm':5,'check_notes':'5mm entry depth includes source entry chamfer; full-thread effective engagement and strength must be verified. Thread helix omitted. Sleeve ends at grounded-body exit; main PTFE bore provides remaining insulation toward live spacer.','valid_solids_on_step_reimport':7,'contacts':contacts,'limitations':'Alumina grade, tolerances, seat flatness, ceramic stress, preload, RF clearance, thermal expansion and shielding need engineering verification. Main PTFE seal ring remains loaded; this does not eliminate its creep. All twelve locations require full-assembly checks before implementation. Ceramic tube is not a threaded fastener.'}
(P/'Geometry checks.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2),flush=True)
