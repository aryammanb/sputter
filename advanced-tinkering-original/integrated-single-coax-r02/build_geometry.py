"""R02 mechanical integration. Original source files remain immutable."""
from pathlib import Path
import json,math,shutil,struct
import cadquery as cq
from OCP.BRepExtrema import BRepExtrema_DistShapeShape

P=Path(__file__).resolve().parent;ROOT=P.parent
GEN=P/'generated';GEN.mkdir(exist_ok=True);DEL=P/'SolidWorks delivery';DEL.mkdir(exist_ok=True)
audit=json.loads((ROOT/'native-assembly-audit.json').read_text(encoding='utf-8-sig'))
V=cq.Vector
parts=[];shapes={}
def cyl(r,h,p,d):return cq.Solid.makeCylinder(r,h,V(*p),V(*d))
def ann(r,ri,h,p,d):return cyl(r,h,p,d).cut(cyl(ri,h,p,d)) if ri else cyl(r,h,p,d)
def box(x,y,z,dx,dy,dz):return cq.Solid.makeBox(dx,dy,dz,V(x,y,z))
def prism(points,vector):return cq.Solid.extrudeLinear(cq.Wire.makePolygon([V(*p) for p in points]+[V(*points[0])]),[],V(*vector))
def distance(a,b):q=BRepExtrema_DistShapeShape(a.wrapped,b.wrapped);q.Perform();return q.Value()
def overlap(a,b):
 A=a.BoundingBox();B=b.BoundingBox()
 return all(getattr(A,k+'min')<=getattr(B,k+'max')+1e-6 and getattr(B,k+'min')<=getattr(A,k+'max')+1e-6 for k in ['x','y','z'])
def source(name):return cq.importers.importStep(str(ROOT/'source'/f'{name}.step')).val()
def save(name,shape,net,note):
 cleaned=shape.clean()
 if cleaned.isValid():shape=cleaned
 assert shape.isValid(),name
 ss=shape.Solids();assert len(ss)==1,(name,len(ss))
 path=GEN/(name+'.step');cq.exporters.export(shape,str(path));shapes[name]=shape
 parts.append({'name':name,'step':str(path.resolve()),'net':net,'note':note,'volume_mm3':shape.Volume(),'valid':shape.isValid()});print('Created '+name,flush=True);return shape

boden=source('Boden');yoke=source('Magnet Joke');cu=source('Backplate')
# Ground bracket and its blind internal anchor. Surface normal points into the Boden.
anchor=V(0,-58,-22);normal=V(0,-1/math.sqrt(2),-1/math.sqrt(2))
drill=cyl(1.25,5,(anchor-normal*1).toTuple(),normal.toTuple())
bmod=boden.cut(drill,tol=1e-5).fix()
save('R02 Boden - internal blind ground anchor',bmod,'ground','Original Boden with one nominal2.5mm blind M3 pilot,4mm along internal cone normal. No thread helix. Original seals unchanged. Anchor depth/torque require release review.')
inside=[]
for t in [i*.25 for i in range(1,201)]:
 if not boden.isInside(anchor+normal*t,1e-5):break
 inside.append(t)
remaining_axis=max(inside)-4

# KF16 capture geometry preserved; larger tube starts beyond the existing clamp halves.
profile=[(-78,8.6),(-80.5,8.6),(-80.5,8),(-95,8),(-103,11.2),(-278,11.2),(-278,12.7),(-103,12.7),(-95,10),(-82.339745962,10),(-81,15),(-78,15)]
tube=cq.Workplane('XY').polyline([(r,y) for y,r in profile]).close().revolve(360,(0,0),(0,1)).val()
save('R02 KF16 neck to one inch service tube',tube,'ground','D30 KF16 capture retained through D20x16 neck toY-95. Taper to25.4OD22.4ID byY-103; service endY-278. Length reference only; finish smooth for sliding gland. Chamber gland not modeled.')

# Actual catalogue clamp envelope; formed spring path is representative, not supplier CAD.
yc=-48.5;y0=yc-4
base=box(-5.9,y0,-1.5,11.8,8,.5).cut(cyl(1.6,2,(0,yc,-2),(0,0,1)))
left=[(-5.9,-1),(-5.9,8),(-4.2,12.1),(-2.0,12.1),(-1.675,4.5),(-2.025,4.5),(-2.35,11.75),(-3.97,11.75),(-5.55,7.92),(-5.55,-1)]
left_s=prism([(x,y0,z) for x,z in left],(0,8,0))
right_s=prism([(-x,y0,z) for x,z in left],(0,8,0))
clamp=base.fuse(left_s).fuse(right_s).translate((0,0,-12))
save('REF icotek SKL3-6 36202 installed study',clamp,'ground','Published envelope8x11.8x13.6mm,3-6mm shield range,3.2mm mounting hole. Formed spring shape is representative. Nominal jaw overlap represents spring contact; not a spring simulation or certified vendor model.')

# Ground carrier: clamp landing, folded wide tab and conformal saddle on inner cone.
landing=box(-6.2,yc-4.5,-14.3,12.4,9,.8)
tab=prism([(-4,yc-4.5,-14.3),(-4,yc-4.5,-13.5),(-4,-58,-21.1),(-4,-58,-22)],(8,0,0))
outer=cq.Solid.makeCone(18,26,8,V(0,-62,0),V(0,1,0));inner=cq.Solid.makeCone(18-1.13137085,26-1.13137085,8,V(0,-62,0),V(0,1,0))
foot=outer.cut(inner).intersect(box(-4,-62,-30,8,8,20))
carrier=landing.fuse(tab).fuse(foot)
carrier=carrier.fuse(cyl(3.5,2,(anchor-normal*2.6).toTuple(),normal.toTuple()))
carrier=carrier.cut(cyl(1.6,4,(0,yc,-16),(0,0,1))).cut(cyl(1.6,7,(anchor-normal*3).toTuple(),normal.toTuple()))
carrier=carrier.cut(cyl(2.9,3.4,(anchor-normal*6).toTuple(),normal.toTuple()))
save('R02 Ground carrier and conformal saddle',carrier,'ground','Custom conductive carrier,0.8mm nominal thickness,12.4x9 landing and8mm tab. Saddle follows original Boden inner cone; flat anchor pad and5.8mm head-access relief. Two3.2mm clearance holes. Material and surface preparation to qualify.')

# Two fasteners, threads represented at nominal major diameter.
mount=cyl(2.75,3,(0,yc,-17.3),(0,0,1)).fuse(cyl(1.5,4,(0,yc,-14.3),(0,0,1)))
save('R02 M3x4 clamp mounting screw',mount,'ground','Simplified nominal M3x4 socket-head screw; no hex socket or thread helix.')
nut=ann(2.75,1.55,2.4,(0,yc,-13),(0,0,1))
save('R02 M3 clamp nut envelope',nut,'ground','Round circumscribed packaging envelope forM3 nut; no thread helix.')
headpoint=anchor-normal*2.6
anchor_screw=cyl(2.75,3,(headpoint-normal*3).toTuple(),normal.toTuple()).fuse(cyl(1.5,6,headpoint.toTuple(),normal.toTuple()))
save('R02 M3x6 blind ground anchor screw',anchor_screw,'ground','Nominal6mm under-head length through2.6mm carrier seat into Boden pilot:3.4mm nominal engagement,0.6mm margin to4mm pilot bottom. Intentional nominal shaft/thread-minor overlap. Torque and engagement need release review.')

# Bring live terminal behind the yoke, avoiding a slot through the magnetic return plate.
stand=ann(3.25,2.15,12.5,(0,-35,13.55),(0,1,0))
save('R02 Copper terminal stand-off D6p5 L12p5',stand,'live','OD6.5 ID4.3x12.5; passes existing yokeD8 terminal passage and contacts copper Backplate atY-22.5. Rear faceY-35.')
under=-35.79
terminal_screw=cyl(3.5,4,(0,under-4,13.55),(0,1,0)).fuse(cyl(2,20,(0,under,13.55),(0,1,0)))
save('R02 M4x20 live terminal screw',terminal_screw,'live','Nominal socket head and major shaft. UnderheadY-35.79, tipY-15.79;6.71mm nominal copper engagement and1.29mm margin to source thread-bore endY-14.5. No thread strength qualification.')

# TE323086 style terminal: catalogue principal dimensions; barrel shape is a study profile.
eye=ann(4.37,2.17,.79,(0,under,13.55),(0,1,0))
neck=box(-2,under,16.5,4,.79,5.5)
barrel_y=-36.565;end_z=25.77
barrel=ann(1.565,.775,6,(0,barrel_y,end_z-6),(0,0,1))
lug=eye.fuse(neck).fuse(barrel).rotate((0,0,13.55),(0,1,13.55),180)
save('REF TE323086 M4 ring terminal study',lug,'live','Principal dimensions fromTE323086: length16.59,eyeOD8.74,eyeID4.34,tab0.79,barrelID1.55,22-16AWG. Neck/barrel formed details are representative; uncrimped bore is not a contact simulation. Barrel points toward cable entry, avoiding a return loop.')

# Single coax layers. Keep original source coolant hoses, and check them independently.
band_end=-44.5;jacket_end=-53.5
z_start=-4.5;z_clamp=-7.5;ya=-71.8;yb=-54.6;dy=yb-ya;dz=z_start-z_clamp;R=(dz*dz+dy*dy)/(4*dz);theta=2*math.atan(dz/dy)
pa=V(0,ya,z_start);pb=V(0,(ya+yb)/2,(z_start+z_clamp)/2);pc=V(0,yb,z_clamp)
arc1=cq.Edge.makeThreePointArc(pa,V(0,ya+R*math.sin(theta/2),z_start-R+R*math.cos(theta/2)),pb)
arc2=cq.Edge.makeThreePointArc(pb,V(0,yb-R*math.sin(theta/2),z_clamp+R-R*math.cos(theta/2)),pc)
lead=cq.Edge.makeLine(V(0,-310,z_start),pa)
def cablepath(end_y):return cq.Wire.assembleEdges([lead,arc1,arc2,cq.Edge.makeLine(pc,V(0,end_y,z_clamp))])
def swept(radius,inner,path,start=(0,-310,-4.5),normal=(0,1,0)):
 s=cq.Solid.sweep(cq.Wire.makeCircle(radius,V(*start),V(*normal)),[cq.Wire.makeCircle(inner,V(*start),V(*normal))] if inner else [],path,True,False)
 expected=math.pi*(radius**2-inner**2)*path.Length();assert abs(s.Volume()-expected)<max(.01,expected*.0001),(radius,inner,s.Volume(),expected)
 return s
save('R02 Continuous coax outer jacket',swept(2.5,1.85,cablepath(jacket_end)),'jacket','5mm overall cable study allowance. Smooth S offset after KF16 throat,minimum nominal cable centerline radius25.4mm. No second coax or gun-end SMA.')
save('R02 Continuous coax shield',swept(1.85,1.6,cablepath(band_end)),'ground','3.7mm shield OD and3.2mm dielectric allowance. Exposed shield bandY-53.5 to-44.5; spring clamp contact is nominal. Cable shield ends on ground side. Actual cable construction and RF rating pending.')
mouth=V(0,barrel_y,27.1-end_z);end=mouth-V(0,0,1)
r=7.5;turn_start=V(0,barrel_y-r,z_clamp);turn_end=V(0,barrel_y,0)
tail_line=cq.Edge.makeLine(V(0,band_end,z_clamp),turn_start)
turn=cq.Edge.makeThreePointArc(turn_start,V(0,barrel_y-r+r/math.sqrt(2),-r/math.sqrt(2)),turn_end)
tail_end=cq.Edge.makeLine(turn_end,end);tail_edges=[tail_line,turn,tail_end]
path=cq.Wire.assembleEdges(cablepath(band_end).Edges()+tail_edges)
dielectric=swept(1.6,.45,path)
save('R02 Continuous center dielectric',dielectric,'insulator','Continuous inner dielectric to1mm outside lug mouth; selected cable and bend suitability pending.')
last=cq.Edge.makeLine(end,mouth+V(0,0,4.5));wirepath=cq.Wire.assembleEdges(path.Edges()+[last])
save('R02 RF center conductor',swept(.45,0,wirepath),'live','0.9mm nominal center conductor; terminal insertion shown inside uncrimped lug. Actual crimp and electrical suitability not simulated.')
boot=swept(2,1.6,cq.Wire.assembleEdges(tail_edges),start=(0,band_end,z_clamp))
save('R02 Additional dielectric guard sleeve',boot,'insulator','Illustrative added dielectric guard beyond shield termination. Material, thickness, voltage rating and retention to qualify.')

# Source assembly solids support collision checks against every retained component.
print('Loading source full STEP for exact-shape checks...',flush=True)
original=cq.importers.importStep(str(ROOT/'Advanced Tinkering magnetron - full reconstruction.step')).val().Solids();assert len(original)==120,len(original)
remove=[]
for c in audit['components']:
 f=Path(c['path']).name;n=c['name']
 if f=='Boden.SLDPRT' or 'KF16 flanged tube' in f or 'HV copper conductor' in f or 'white HV cable' in f or 'wire hook' in f or (n.startswith('01') and 'M4x8' in f):remove.append(c)
assert len(remove)==6
excluded=set()
for c in remove:
 volume=c['volume_mm3'];pos=V(*[q*1000 for q in c['transform'][9:12]])
 choices=[(abs(s.Volume()-volume),i,s) for i,s in enumerate(original) if i not in excluded and abs(s.Volume()-volume)<max(.005,volume*1e-5)]
 assert choices,c['name']
 if len(choices)>1:choices.sort(key=lambda q:(q[2].Center()-pos).Length)
 selected=choices[0][1];excluded.add(selected)
retained=[s for i,s in enumerate(original) if i not in excluded]
assert len(retained)==114
all_new=list(shapes.items());hits=[];near=[]
for name,shape in all_new:
 if 'Boden -' in name:continue
 for i,s in enumerate(retained):
  if not overlap(shape,s):continue
  common=shape.intersect(s);volume=common.Volume() if common.Solids() else 0
  if volume>1e-4:hits.append({'new':name,'source_solid_index':i,'volume_mm3':volume,'source_volume_mm3':s.Volume(),'source_center':s.Center().toTuple()})
for i,(a,A) in enumerate(all_new):
 for b,B in all_new[i+1:]:
  if not overlap(A,B):continue
  common=A.intersect(B);volume=common.Volume() if common.Solids() else 0
  if volume>1e-4:hits.append({'new':a,'other_new':b,'volume_mm3':volume})

full=cq.Compound.makeCompound(retained+list(shapes.values()));cq.exporters.export(full,str(P/'Integrated single coax magnetron R02.step'))
# Manifest for a native flattened SolidWorks assembly, preserving original component transforms.
items=[]
removed_names={c['name'] for c in remove}
for c in audit['components']:
 if c['name'] in removed_names:continue
 src=ROOT/'SolidWorks delivery'/Path(c['path']).name
 assert src.exists(),src
 dst=DEL/src.name
 if not dst.exists():shutil.copy2(src,dst)
 items.append({'name':c['name'],'path':str(dst.resolve()),'transform':c['transform'],'kind':'retained'})
for part in parts:items.append({'name':part['name'],'path':str((DEL/(part['name']+'.SLDPRT')).resolve()),'step':part['step'],'transform':[1,0,0,0,1,0,0,0,1,0,0,0,1,0,0,0],'kind':'new','net':part['net']})
(P/'native-build-manifest.json').write_text(json.dumps({'items':items,'parts':parts},indent=2))
report={'original_solids':len(original),'removed_source_components':[c['name'] for c in remove],'retained_source_solids':len(retained),'new_solids':len(shapes),'total_solids':len(retained)+len(shapes),'new_parts':parts,'raw_new_interferences':hits,'anchor_axis_material_remaining_beyond_4mm_drill_mm':remaining_axis,'ring_lug_mouth_mm':mouth.toTuple(),'terminal_thread_engagement_mm':6.71,'terminal_bore_bottom_margin_mm':1.29,'status':'Mechanical integration study; inspect and resolve raw contacts before delivery. RF and cooling performance unqualified.'}
(P/'geometry-verification.json').write_text(json.dumps(report,indent=2));print(json.dumps({'new_parts':len(parts),'total_solids':report['total_solids'],'raw_contacts':hits,'anchor_remaining_axis_mm':remaining_axis},indent=2),flush=True)
