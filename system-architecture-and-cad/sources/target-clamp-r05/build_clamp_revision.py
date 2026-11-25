from pathlib import Path
import json,math,struct,csv,shutil
import numpy as np
import cadquery as cq
from OCP.BRepExtrema import BRepExtrema_DistShapeShape
P=Path(__file__).resolve().parent;ROOT=P.parents[2];B=P.parent/'system-layout-r04';V=cq.Vector
source=ROOT/'advanced-tinkering-original/source';oldclamp=cq.importers.importStep(str(source/'Target Klemme.step')).val();cooler=cq.importers.importStep(str(ROOT/'advanced-tinkering-original/balanced-twelve-stack-study/Proposed cooler.step')).val();cap=cq.importers.importStep(str(source/'Dunkelraumabschirmung.step')).val()
def cyl(r,y,h):return cq.Solid.makeCylinder(r,h,V(0,y,0),V(0,1,0))
def bb(s):
 b=s.BoundingBox();return [b.xmin,b.ymin,b.zmin,b.xmax,b.ymax,b.zmax]
def distance(a,b):d=BRepExtrema_DistShapeShape(a.wrapped,b.wrapped);d.Perform();return d.Value()
# Keep the outer body, rear register and all twelve counterbored mounting holes.
# Replace only the central pressure lip. The contact chamfer, aperture and bearing width are preserved.
profile=[(35.35,3.175),(24.15,3.175),(23.9,3.425),(23.9,4.175),(24.725,5.0),(35.35,5.0)]
web=cq.Workplane('XY').polyline(profile).close().revolve(360,(0,0),(0,1)).val()
newclamp=oldclamp.cut(cyl(35.25,1.999,3.101)).fuse(web).clean();assert newclamp.isValid() and len(newclamp.Solids())==1
newtarget=cyl(25.4,0,3.175);oldtarget=cyl(25.4,0,2)
# Contact is nominal tangency, not an interference preload model.
contact=cq.Face.makeFromWires(cq.Wire.makeCircle(25.4,V(0,3.175,0),V(0,1,0))).intersect(newclamp)
checks={'old_clamp_thick_target_overlap_mm3':oldclamp.intersect(newtarget).Volume(),'new_clamp_target_overlap_mm3':newclamp.intersect(newtarget).Volume(),'new_clamp_cooler_overlap_mm3':newclamp.intersect(cooler).Volume(),'new_clamp_dark_cap_overlap_mm3':newclamp.intersect(cap).Volume(),'old_clamp_to_cap_distance_mm':distance(oldclamp,cap),'new_clamp_to_cap_distance_mm':distance(newclamp,cap),'target_clamp_contact_area_mm2':contact.Area()}
assert checks['old_clamp_thick_target_overlap_mm3']>200
assert max(checks[k] for k in ['new_clamp_target_overlap_mm3','new_clamp_cooler_overlap_mm3','new_clamp_dark_cap_overlap_mm3'])<1e-6
assert abs(checks['new_clamp_to_cap_distance_mm']-checks['old_clamp_to_cap_distance_mm'])<1e-6
assert checks['target_clamp_contact_area_mm2']>180
# The original outer ring, hole positions, counterbores and seats are geometrically identical.
outer=cyl(60,-4,10).cut(cyl(35.5,-4.1,10.2));a=oldclamp.intersect(outer);b=newclamp.intersect(outer);checks['outer_mounting_region_difference_mm3']=a.cut(b).Volume()+b.cut(a).Volume();assert checks['outer_mounting_region_difference_mm3']<1e-6
cq.exporters.export(newclamp,str(P/'Target clamp R05 - 3.175mm target.step'));cq.exporters.export(newtarget,str(P/'Aluminium target D50.8 x3.175.step'))
fit=cq.Assembly(name='Revised target clamp and target');fit.add(cooler,name='Existing copper cooling body',color=cq.Color(.8,.36,.13));fit.add(newclamp,name='Target clamp R05',color=cq.Color(.62,.67,.72));fit.add(newtarget,name='Aluminium target 3.175mm',color=cq.Color(.81,.84,.88));fit.save(str(P/'Clamp R05 fit assembly.step'))
print('Clamp rebuilt and nominal interference checks passed',checks,flush=True)
# Bring the revision into the complete chamber, preserving the checked R04 door and utilities.
meta=json.loads((B/'parts.json').read_text());solids=cq.importers.importStep(str(B/'Complete sputter system R04.step')).val().Solids();items=[];k=0
for q in meta:
 ss=solids[k:k+q['solid_count']];k+=q['solid_count'];items.append(q|{'shape':ss[0] if len(ss)==1 else cq.Compound.makeCompound(ss)})
shift=1.175;base_z=144.175
native_gun=[]
for q in items:
 if q['group']=='gun':
  native=q['shape'].translate((0,0,-143)).rotate((0,0,0),(1,0,0),90)
  if q['role']=='gun_clamp':native=newclamp;q['name']='Gun target clamp R05 for3.175mm aluminium';q['note']='Central pressure lip revised; contact shoulderY3.175; apertureD47.8; front envelopeY5 and outer screw interface retained.'
  if q['role']=='gun_target':native=newtarget;q['name']='Gun aluminium target D50.8 x3.175';q['color']=[.81,.84,.88];q['note']='Selected VritraTech99.99% aluminium,2in x0.125in. https://www.vritratech.com/store/product/aluminium-al-sputtering-target/'
  if q['role']=='gun_targetbolts':
   axis=next(f._geomAdaptor().Cylinder().Axis().Location() for f in native.Faces() if f.geomType()=='CYLINDER' and abs(f._geomAdaptor().Cylinder().Radius()-1.5)<.02)
   xx,zz=axis.X(),axis.Z();trim=cq.Solid.makeBox(8,.6,8,V(xx-4,-7.2,zz-4))
   shaft=cq.Solid.makeCylinder(1.5,2.3,V(xx,-8.8,zz),V(0,1,0));tip=cq.Solid.makeCone(1.3,1.5,.2,V(xx,-9,zz),V(0,1,0))
   native=native.cut(trim).fuse(shaft,tip).clean();assert native.isValid() and len(native.Solids())==1
   q['name']+=' R05 M3x10';q['note']='R05 nominal M3x10 replaces M3x8, same head seatY1; tipY-9. Verify full useful M3x0.5 thread toY-9 and pilot bottomY-10.'
  native_gun.append(q|{'shape':native})
  q['shape']=native.rotate((0,0,0),(1,0,0),-90).translate((0,0,base_z))
  q['note']+=' R05 default gun datum raised1.175mm to retain100mm target/substrate gap.'
# Refit the external flexible extensions to the raised gun ends; routing end at equipment unchanged.
def route(segments,ro,ri):
 path=cq.Wire.assembleEdges([cq.Edge.makeBezier([V(*p) for p in ps]) for ps in segments]);normal=np.array(segments[0][1])-segments[0][0];p=V(*segments[0][0]);return cq.Solid.sweep(cq.Wire.makeCircle(ro,p,V(*normal)),[cq.Wire.makeCircle(ri,p,V(*normal))] if ri else [],path,True,False)
for q in items:
 if q['role']=='gun_water':
  supply='supply' in q['name'];kk=0 if supply else 1;x=3 if supply else -3;yy=-40 if supply else -10
  q['shape']=route([[(x,0,444.175),(x,0,536.175+kk*14),(-180,yy,535+kk*14),(-230,yy,220)],[(-230,yy,220),(-250,yy,94),(-220,yy,-40),(-280,yy,-40)]],2,1.25);q['note']+=' R05 upper endpoint follows raised gun.'
 if q['name']=='Power cable to gun coax':
  q['shape']=route([[(0,-4.5,454.175),(0,-4.5,571.175),(180,-200,570),(250,-210,300)],[(250,-210,300),(320,-220,30),(430,-150,30),(430,-150,-80)]],2.5,0);q['note']+=' R05 upper endpoint follows raised gun; RF300W is selected source rating, not qualified gun rating.'
# Actual nominal fastener data from source geometry; no screw relocation is needed.
target_screws=[q for q in native_gun if q['role']=='gun_targetbolts'];screw=target_screws[0]['shape'];shafts=[]
for f in screw.Faces():
 if f.geomType()=='CYLINDER' and abs(f._geomAdaptor().Cylinder().Radius()-1.5)<.02:shafts.append(bb(f))
checks['target_screws_count']=len(target_screws);checks['one_target_screw_shaft_bboxes']=shafts;checks['new_vs_old_screw_clamp_interference_difference_mm3']=max(abs(q['shape'].intersect(newclamp).Volume()-q['shape'].intersect(oldclamp).Volume()) for q in target_screws)
assert len(target_screws)==12 and checks['new_vs_old_screw_clamp_interference_difference_mm3']<1e-6
# Retained pilot cylindrical ranges areY-10..-3.25; calculate the overlap with the existing screw shaft.
if shafts:
 lo,hi=shafts[0][1],shafts[0][4];checks['nominal_straight_pilot_engagement_mm']=max(0,min(hi,-3.25)-max(lo,-10));checks['pilot_bottom_margin_mm']=bb(screw)[1]-(-10);checks['screw_physical_tip_y_mm']=bb(screw)[1];checks['screw_underhead_y_mm']=1;checks['previous_straight_pilot_engagement_mm']=3.55
checks['thread_scope']='Geometrical engagement against existing tap-drill envelopes only; no helical threads, torque or proof-load validation.'
for title,door,shutter in [('Complete sputter system R05',0,0),('Complete sputter system R05 - loading',-110,80)]:
 ass=cq.Assembly(name=title)
 for i,q in enumerate(items):
  ss=q['shape']
  if q['group']=='door':ss=ss.rotate((-118,-116,0),(-118,-116,1),door)
  if q['group']=='shutter':ss=ss.rotate((-65,0,0),(-65,0,1),shutter)
  ass.add(ss,name=f'{i:03}_'+q['name'].replace('/','_'),color=cq.Color(*q['color']))
 ass.save(str(P/(title+'.step')));print('Exported',title,flush=True)
gun=cq.Assembly(name='Latest magnetron R05 - aluminium3.175mm')
for i,q in enumerate(native_gun):gun.add(q['shape'],name=f'{i:03}_'+q['name'].replace('/','_'),color=cq.Color(*q['color']))
gun.save(str(P/'Latest magnetron R05 - aluminium3.175mm.step'))
serial=[]
with (P/'mesh.bin').open('wb') as f:
 for i,q in enumerate(items):
  sh=q['shape'];vs,fs=sh.tessellate(.3,.35);arr=np.array([v.toTuple() for v in vs],dtype=np.float32)[np.array(fs)].astype('<f4');f.write(struct.pack('<I',len(arr)));f.write(arr.tobytes());serial.append({k:v for k,v in q.items() if k!='shape'}|{'bbox_mm':bb(sh),'volume_mm3':sh.Volume(),'solid_count':len(sh.Solids()),'valid':sh.isValid()})
(P/'parts.json').write_text(json.dumps(serial,indent=2),encoding='utf-8')
dims={'target_diameter':50.8,'target_thickness':3.175,'clamp_OD':93.6,'clamp_front_y':5,'contact_shoulder_y':3.175,'lip_axial_depth':1.825,'minimum_aperture_diameter':47.8,'front_aperture_diameter':49.45,'contact_edge_chamfer':.25,'contact_inner_diameter':48.3,'target_contact_radial_band':1.25,'screw_spec':'M3 x10 (12 pieces)','screw_PCD':80,'screw_count':12,'screw_clearance_diameter':3.3,'counterbore_diameter':5.7,'counterbore_seat_y':1,'shield_minimum_clearance':checks['new_clamp_to_cap_distance_mm'],'gun_default_translation_z':base_z,'default_target_face_z':141,'substrate_top_z':41,'default_target_substrate_gap':100,'magnet_tip_to_target_front':5.675,'target_gap_min':75,'target_gap_max':150}
report={'dimensions_mm':dims,'checks':checks,'instances':len(items),'solids':sum(q['solid_count'] for q in serial),'invalid_references':[q['name'] for q in serial if not q['valid']],'supplier':{'url':'https://www.vritratech.com/store/product/aluminium-al-sputtering-target/','purity_percent':99.99,'base_INR':8300,'GST_INR':1494,'total_INR':9794,'price_checked':'2026-11-24'},'scope':'Geometric clamp redesign and assembly update; not a validated clamp preload, thermal or300W operating rating. Preserve original clamping float. Verify actual target dimensions/flatness before machining release. Old magnetic results assumed2mm target and are superseded for the target spacing.'}
(P/'Clamp redesign and verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
with (P/'R05 dimension schedule.csv').open('w',newline='',encoding='utf-8-sig') as f:
 w=csv.writer(f);w.writerow(['Dimension','Nominal value mm']);w.writerows(dims.items())
print(json.dumps({'done':True,'checks':checks,'dimensions':dims}),flush=True)
