from pathlib import Path
import json, math, csv, struct, time
import numpy as np
import cadquery as cq

P=Path(__file__).resolve().parent
ROOT=P.parents[2]
SRC=ROOT/'advanced-tinkering-original'/'balanced-twelve-stack-study'
V=cq.Vector
items=[]
def box(x,y,z,dx,dy,dz): return cq.Solid.makeBox(dx,dy,dz,V(x,y,z))
def cyl(r,h,p,d=(0,0,1)): return cq.Solid.makeCylinder(r,h,V(*p),V(*d))
def ann(ri,ro,h,p,d=(0,0,1)):return cyl(ro,h,p,d).cut(cyl(ri,h,p,d))
def bounds(s):
 b=s.BoundingBox(); return [b.xmin,b.ymin,b.zmin,b.xmax,b.ymax,b.zmax]
def add(name,s,role,color=(.62,.68,.73),note='',group='chamber'):
 assert s.isValid(),name
 items.append(dict(name=name,shape=s,role=role,color=color,note=note,group=group))
 return s
def rr(w,h,r,y,depth,z=150):
 return cq.Workplane('XZ',origin=(0,y,z)).rect(w,h).extrude(depth).edges('|Y').fillet(r).val()
def radial(shape,origin,direction):
 # z-axis primitive -> selected port outward direction.
 if direction==(0,1,0):shape=shape.rotate((0,0,0),(1,0,0),-90)
 elif direction==(1,0,0):shape=shape.rotate((0,0,0),(0,1,0),90)
 elif direction==(0,0,-1):shape=shape.rotate((0,0,0),(1,0,0),180)
 return shape.translate(origin)
def kf25(origin,direction,bore=22.225,length=40.132,neck=25.4):
 # Nominal ISO-KF envelope. Seal details and purchased CAD remain unqualified.
 ri=bore/2; rn=neck/2; ro=19.94
 prof=[(ri,0),(rn,0),(rn,length-7),(ro,length-3.5),(ro,length),(ri,length)]
 s=cq.Workplane('XZ').polyline(prof).close().revolve(360,(0,0),(0,1)).val()
 return radial(s,origin,direction)
def hexnut(x,y,z,height=5.5):
 return cq.Workplane('XY',origin=(x,y,z)).polygon(6,12.83).extrude(height).faces('>Z').workplane().hole(6.35).val()

# Coordinate system: internal floor z0, roof underside z300; front y-100.
# Source gun target face is +Y2; rotate source axis so the target faces downward.
target_face_source=2.0
target_z=141.0 # 100 mm above the actual 1 mm coupon, not stage surface.
gun_translation=target_z+target_face_source
raw=cq.importers.importStep(str(SRC/'Proposed twelve stack mechanical study.step')).val().Solids()
meta=json.loads((SRC/'parts.json').read_text())['new']
available=set(range(len(raw))); bb=[np.array(bounds(s)) for s in raw]
for i,q in enumerate(meta):
 goal=np.array(q['bbox_mm']);j=min(available,key=lambda j:np.linalg.norm(bb[j]-goal))
 assert max(abs(bb[j]-goal))<.8,(q['name'],bb[j],goal)
 available.remove(j)
 s=raw[j].rotate((0,0,0),(1,0,0),-90).translate((0,0,gun_translation))
 colors={'cooler':(.85,.45,.23),'closure':(.85,.45,.23),'outermag':(.14,.38,.78),'centermag':(.82,.23,.22),'target':(.76,.78,.79),'isolator':(.92,.88,.73),'cups':(.92,.88,.73),'hoses':(.13,.43,.82),'coax':(.18,.23,.29)}
 add(f'Gun {i+1:03} {q["role"]}',s,'gun_'+q['role'],colors.get(q['role'],(.48,.57,.64)),q['name'],'gun')
print('Imported and mapped all 141 latest gun solids',flush=True)

# Shell: walls share faces, not overlapping material.
rear=box(-110,100,0,220,10,300)
right=box(100,-100,0,10,200,300)
left=box(-110,-100,0,10,200,300)
ports=[('Rear upper gas inlet',(0,100,210),(0,1,0)),
       ('Rear lower left Pirani',(-50,100,90),(0,1,0)),
       ('Rear lower right Penning',(50,100,90),(0,1,0)),
       ('Right lower spare',(100,0,75),(1,0,0)),
       ('Right upper spare',(100,0,225),(1,0,0))]
for name,origin,d in ports:
 hole=cyl(12.7,12,origin,d)
 if d==(0,1,0):rear=rear.cut(hole)
 else:right=right.cut(hole)
 add(name+' KF25 weld nipple',kf25(origin,d),'service_port',note='QF25-100-LF nominal envelope: OD39.88, bore22.225, length40.132. No attached gauge/MFC models.')
roof=box(-110,-116,300,220,226,10).cut(cyl(16.5,12,(0,0,299))).cut(cyl(3.4,12,(-65,0,299)))
floor=box(-110,-116,-10,220,226,10).cut(cyl(35,12,(0,0,-11)))
frame=box(-110,-116,0,220,16,300).cut(rr(180,270,8,-99,18))
groove=rr(198,288,12,-113.8,2.2).cut(rr(189,279,7.5,-113.7,2.4))
frame=frame.cut(groove)
for name,s in [('Rear wall',rear),('Right wall',right),('Left wall - reserved blank',left),('Roof plate',roof),('Floor plate',floor),('Front welded door frame',frame)]:
 add(name,s,'structure',note='10 mm walls/roof/floor and 16 mm front frame are nominal design choices; pressure/deflection/weld sizing not validated.')
gasket=rr(197.5,287.5,11.75,-113.8,2.2).cut(rr(189.5,279.5,7.75,-113.7,2.4))
add('Front door compressed gasket envelope',gasket,'door_seal',(.12,.18,.18),note='Rectangular compressed-cord envelope in 4.5 x 2.2 groove; final seal specification unqualified.')

# Door, viewport and hinge. All door-group parts rotate together about left hinge.
door=box(-114,-132,-8,228,16,316).cut(cyl(35,20,(0,-134,175),(0,1,0)))
for i in range(6):
 a=2*math.pi*i/6;x,z=52*math.cos(a),175+52*math.sin(a)
 door=door.cut(cyl(2.1,10,(x,-132,z),(0,1,0)))
add('Front door plate with viewport cutout',door,'door_plate',note='228 x 316 x 16, viewport clear70; closed inner face y-116.',group='door')
add('Viewport gasket envelope',ann(38,43,2,(0,-134,175),(0,1,0)),'viewport_seal',(.12,.18,.18),group='door',note='Reference gasket envelope; mounting/seal design pending.')
add('Viewport glass disc',cyl(47,6,(0,-140,175),(0,1,0)),'glass',(.36,.72,.83),group='door',note='D94 x6 nominal envelope; 70 clear aperture. Glass pressure/thermal rating NOT established.')
bezel=ann(35,57,6,(0,-146,175),(0,1,0))
for i in range(6):
 a=2*math.pi*i/6;x,z=52*math.cos(a),175+52*math.sin(a)
 bezel=bezel.cut(cyl(2.75,7,(x,-146.5,z),(0,1,0)))
 add(f'Viewport retainer screw {i+1}',cyl(2.5,14,(x,-146,z),(0,1,0)).fuse(cyl(4.5,4,(x,-150,z),(0,1,0))),'door_screw',group='door',note='Nominal M5 envelope; threads/preload not modeled.')
add('Viewport retaining bezel',bezel,'viewport_bezel',group='door')
add('Door pull handle',box(78,-153,130,8,21,8).fuse(box(78,-153,202,8,21,8),box(78,-161,130,8,8,80)),'door_handle',group='door')
for z in [65,235]:
 pin=cyl(3,40,(-118,-116,z-20))
 fixed=ann(3.2,6,11,(-118,-116,z-20)).fuse(ann(3.2,6,11,(-118,-116,z+9)),box(-118,-116,z-20,8,16,11),box(-118,-116,z+9,8,16,11))
 moving=ann(3.2,6,16,(-118,-116,z-8)).fuse(box(-118,-124,z-8,10,8,16))
 add(f'Hinge fixed barrel {z}',fixed,'hinge_fixed')
 add(f'Hinge pin {z}',pin,'hinge_pin',(.24,.3,.36))
 add(f'Hinge door leaf {z}',moving,'hinge_moving',group='door')
add('Latch body envelope',box(110,-128,142,14,12,16),'latch',group='door',note='Concept latch; exact procurement and mounting pending.')
add('Latch catch envelope',box(110,-116,144,12,12,12),'latch_catch')

# Bottom turbo mating flange: no fictitious supplier pump internals.
turbo_neck=ann(31.75,35,33,(0,0,-33))
turbo_flange=ann(31.75,47.5,12,(0,0,-45))
add('Bottom ISO63-K weld neck and flange',turbo_neck.fuse(turbo_flange),'turbo_flange',note='OD95 / bore63.5 / flange12, face z-45; nominal envelope. Clamp profile and backing groove simplified; purchased drawing pending.')
for x in [-85,85]:
 for y in [-75,75]:
  add(f'Support leg {x} {y}',box(x-8,y-8,-90,16,16,80),'support',(.28,.35,.4))

# Roof gun connection, deliberately identifying the outstanding through-bore issue.
add('Roof KF25 gun weld flange - bore to verify',kf25((0,0,300),(0,0,1),bore=27,length=30,neck=33),'gun_mount',(.83,.58,.26),note='Nominal KF25 OD39.88 with proposed27 through bore. Not a verified off-the-shelf mating flange; standard weld stub/ring can block25.4 tube.')
add('Gun joint seal space - unresolved reference',ann(13,16,3,(0,0,330)),'gun_mount_seal',(.55,.3,.13),note='Placeholder only; actual KF25 centering seal must be verified for25.4 pass-through.')
adapter=ann(12.95,19.94,4,(0,0,333)).fuse(ann(12.95,17.5,32,(0,0,337)),ann(12.95,21,14.8,(0,0,369)))
add('QF25XVC100 reference compression adapter',adapter,'gun_adapter',(.83,.58,.26),note='50.8 long and40 flange OD from catalogue; body/knob envelope illustrative. Minimum through bore25.9 assumed from A dimension; controlled drawing required. eBay purchase planned.')
add('Gun KF25 clamp envelope',ann(20.1,24.5,10,(0,0,326)),'gun_mount_clamp',(.38,.46,.53),note='Simplified annular clamp envelope; no actuator detail.')

# Stage and 1 mm coupon: actual target-to-substrate datum is coupon TOP at z41.
stage=cyl(45,6,(0,0,34))
add('Removable substrate stage D90 x6',stage,'stage',(.55,.62,.68),note='Top z40, undersidez34. Four supports at (+/-29,+/-29), fully below plate and outside central turbo opening.')
for x in [-29,29]:
 for y in [-29,29]:
  add(f'Stage support {x} {y}',cyl(3,34,(x,y,0)),'stage_support')
add('Reference substrate 50 x50 x1',box(-25,-25,40,50,50,1),'substrate',(.25,.48,.73),note='Sample design assumption; top surface z41 is deposition-distance datum.')
baffle=cyl(52,1.5,(0,0,18))
for x in [-29,29]:
 for y in [-29,29]:baffle=baffle.cut(cyl(3.5,3,(x,y,17)))
add('Removable pump deposition baffle D104 x1.5',baffle,'pump_baffle',(.37,.44,.5),note='Baffle topz19.5; four7 clearance bores. Reduces direct line of sight; conductance and full interception not validated.')
for x,y in [(-44,0),(44,0)]:add(f'Baffle spacer {x}',cyl(2.5,18,(x,y,0)),'baffle_support')

# Shutter is one bent 1 mm sheet with genuine R2 internal / R3 external bends.
w=cq.Workplane('XZ',origin=(-65,8,0)).moveTo(8,294).lineTo(-19,294)
w=w.threePointArc((-21.1213203436,293.1213203436),(-22,291)).lineTo(-22,56)
w=w.threePointArc((-21.1213203436,53.8786796564),(-19,53)).lineTo(37,53).lineTo(37,54).lineTo(-19,54)
w=w.threePointArc((-20.4142135624,54.5857864376),(-21,56)).lineTo(-21,291)
w=w.threePointArc((-20.4142135624,292.4142135624),(-19,293)).lineTo(8,293).close()
shutter=w.extrude(16).val().fuse(box(-28,-28,53,56,56,1)).clean().cut(cyl(3.3,3,(-65,0,292)))
add('One piece bent shutter - CLOSED',shutter,'shutter',(.20,.65,.61),note='t1; inside bendsR2; upper flatz293..294; bladez53..54; pivot(-65,0); blade56square; closed centre(0,0).',group='shutter')
shaft=cyl(3.175,31.75,(-65,0,280.65)).fuse(cyl(8,3,(-65,0,312.4)),cyl(6.35,9,(-65,0,315.4)))
add('99607A246 thumb screw nominal envelope',shaft,'shutter_screw',(.38,.44,.5),group='shutter',note='1/4-28 x1.25in under-head assumption; collar/head geometry illustrative, threads not modeled. Verify McMaster drawing.')
for z in [287.5,294]:add(f'Shutter aluminum nut {z}',hexnut(-65,0,z),'shutter_nut',(.64,.7,.75),group='shutter',note='1/4-28 nominal nut envelope; not supplier CAD.')
add('Shutter underside thrust washer',ann(3.3,8,.5,(-65,0,299.5)),'shutter_washer',group='shutter')
add('6540K248 shutter face seal envelope',ann(3.175,6.35,2.4,(-65,0,310)),'shutter_seal',(.11,.17,.17),note='Nominal1/4ID x1/2OD x1/8 free section from supplied text; compressed axial envelope2.4. No qualified rotating seal gland.')

print('Built chamber, ports, door, stage and bent shutter',len(items),'components',flush=True)

def state_shape(q,door_angle=0,shutter_angle=0,gun_gap=100):
 s=q['shape']
 if q['group']=='gun':s=s.translate((0,0,gun_gap-100))
 if q['group']=='door':s=s.rotate((-118,-116,0),(-118,-116,1),door_angle)
 if q['group']=='shutter':s=s.rotate((-65,0,0),(-65,0,1),shutter_angle)
 return s

outparts=P/'Separate parts';outparts.mkdir(exist_ok=True)
for name,da,sa in [('Complete chamber - door closed shutter closed',0,0),('Complete chamber - door open shutter parked',-110,80)]:
 a=cq.Assembly(name=name)
 for i,q in enumerate(items):a.add(state_shape(q,da,sa),name=f'{i:03}_{q["name"].replace("/","_")}',color=cq.Color(*q['color']))
 a.save(str(P/(name+'.step')))
 print('Exported',name,flush=True)
for name,shape in [('Bent shutter',shutter),('Top plate',roof),('Substrate stage',stage),('Front door',door),('ISO63 turbo weld flange',turbo_neck.fuse(turbo_flange))]:cq.exporters.export(shape,str(outparts/(name+'.step')))

# Developed blank: neutral-axis K-factor is a fabrication assumption, not a measured bend allowance.
BA=math.pi/2*(2+.42);B1=27;B2=27+BA+235;L=27+2*BA+235+112;wide=L-56
flat=cq.Workplane('XY').polyline([(0,-8),(wide,-8),(wide,-28),(L,-28),(L,28),(wide,28),(wide,8),(0,8)]).close().extrude(1).faces('>Z').workplane(centerOption='CenterOfMass')
# Rebuild explicit hole at station8; export face projection to DXF.
flatshape=cq.Workplane('XY').polyline([(0,-8),(wide,-8),(wide,-28),(L,-28),(L,28),(wide,28),(wide,8),(0,8)]).close().extrude(1).val().cut(cyl(3.3,3,(8,0,-1)))
cq.exporters.export(flatshape,str(outparts/'Shutter developed blank - K0.42.step'))
cq.exporters.export(cq.Workplane('XY').add(max(flatshape.Faces(),key=lambda f:f.Center().z)).wires(),str(outparts/'Shutter blank reference.dxf'))

# Exact motion and clearance checks against NEW chamber geometry; inherited gun contacts excluded.
fixed=[q for q in items if q['group'] not in ['gun','shutter','door'] and q['role'] not in ['shutter_seal','gun_mount_seal','gun_mount_clamp']]
gun=[q for q in items if q['group']=='gun']
def bbox_overlap(a,b):return all(a[i]<b[i+3]-1e-6 and b[i]<a[i+3]-1e-6 for i in range(3))
def hits(shape,others):
 out=[];a=bounds(shape)
 for q,s,b in others:
  if bbox_overlap(a,b):
   c=shape.intersect(s);vol=c.Volume() if c.Solids() else 0
   if vol>.001:out.append({'part':q['name'],'overlap_mm3':vol})
 return out
fixed_cache=[(q,q['shape'],bounds(q['shape'])) for q in fixed]
gun_cache={gap:[(q,state_shape(q,gun_gap=gap),bounds(state_shape(q,gun_gap=gap))) for q in gun] for gap in [75,100,150]}
motion=[];wall_min=1e9
for angle in range(81):
 s=shutter.rotate((-65,0,0),(-65,0,1),angle);b=bounds(s)
 wall_min=min(wall_min,b[0]+100,100-b[3],b[1]+100,100-b[4])
 contacts=hits(s,fixed_cache)
 for gap in [75,100,150]:
  contacts+=hits(s,gun_cache[gap])
 if contacts:motion.append({'angle':angle,'contacts':contacts})
print('Shutter sweep checked 0..80 degrees at 1 degree increments',flush=True)
gunhits=[]
for gap in [75,100,150]:
 for q in gun:
  h=hits(state_shape(q,gun_gap=gap),[(o,s,b) for o,s,b in fixed_cache if o['role'] not in ['stage_support','baffle_support']])
  if h:gunhits.append({'gap':gap,'gun_part':q['name'],'contacts':h})

# Measured coordinate data and catalogue assumptions kept separate.
report={
 'status':'Nominal mechanical concept; not a fabrication release',
 'components':len(items),'gun_components':len(gun),'valid_solids':sum(len(q['shape'].Solids()) for q in items),
 'dimensions_mm':{'internal_chamber':[200,200,300],'internal_volume_litres':12,'wall_roof_floor_thickness':10,
 'roof_blank':[220,226,10],'front_frame_thickness':16,'door':[228,316,16],'door_clear_opening':[180,270],
 'viewport_clear_diameter':70,'viewport_glass_envelope':[94,6],'stage_diameter':90,'stage_thickness':6,'stage_top_z':40,
 'reference_substrate':[50,50,1],'substrate_top_z':41,'default_target_face_z':141,'target_substrate_gap_range':[75,150],
 'gun_vertical_travel':75,'shutter_pivot':[-65,0],'shutter_sheet_thickness':1,'shutter_inside_bend_radius':2,
 'shutter_blade':[56,56],'shutter_blade_bottom_z':53,'shutter_blade_top_z':54,'shutter_substrate_clearance':12,
 'shutter_flat_midplane_drop':240,'shutter_straight_vertical_length':235,'shutter_open_rotation_deg':80,
 'shutter_sample_cover_margin_per_side':3,'shutter_sample_open_clearance_y':65*math.sin(math.radians(80))-28*(math.sin(math.radians(80))+math.cos(math.radians(80)))-25,
 'shutter_min_wall_clearance_sampled_1deg':wall_min,'shutter_developed_length_K0p42':L,'shutter_developed_max_width':56,
 'shutter_flat_bend_allowance_each_K0p42':BA,'shutter_bend_tangent_stations':[27,27+BA,B2,B2+BA],
 'iso63_flange_OD':95,'iso63_port_bore':63.5,'iso63_mating_face_z':-45,'kf25_service_flange_OD':39.88,
 'gun_tube_projection_above_adapter_at_min_gap':(118+278)-383.8,
 'gun_straight_tube_start_at_max_gap_z':193+103,
 'rear_ports':[{'name':n,'centre':o} for n,o,d in ports if d==(0,1,0)],
 'right_spare_port_heights':[75,225]},
 'checks':{'all_shapes_valid':all(q['shape'].isValid() for q in items),'shutter_sweep_interferences':motion,
 'gun_at_75_100_150_gap_interferences':gunhits,
 'source_target_top_face_y':target_face_source,
 'new_structural_pressure_design_checked':False,'purchased_fittings_are_controlled_supplier_CAD':False},
 'unresolved':['Roof KF25 centering seal and mating flange must pass25.4 tube; standard parts can block it.',
 'Thumb screw journal/collar and O-ring gland must be checked; threaded rotating surface not qualified as a vacuum seal.',
 '10mm chamber panels, door, glass and welds require vacuum structural/sealing review.',
 'Pirani, Penning and MFC hardware not supplied; connection ports modeled only.',
 'No claimed deposition uniformity, pump-down time or pumping conductance validation.',
 'Latest gun internal inherited contacts and prior RF/cooling limitations retained.',
 'Blank development uses K0.42; supplier bend tooling must set production allowances.']}
assert not motion, motion
assert not gunhits,gunhits
(P/'Dimension and clearance report.json').write_text(json.dumps(report,indent=2))

serial=[]
with (P/'mesh.bin').open('wb') as f:
 for q in items:
  vs,fs=q['shape'].tessellate(.22,.3)
  a=np.array([v.toTuple() for v in vs],dtype=np.float32)[np.array(fs)].astype('<f4')
  f.write(struct.pack('<I',len(a)));f.write(a.tobytes())
  serial.append({k:v for k,v in q.items() if k!='shape'}|{'bbox_mm':bounds(q['shape']),'volume_mm3':q['shape'].Volume()})
(P/'parts.json').write_text(json.dumps(serial,indent=2))
with (P/'Assembly parts list.csv').open('w',newline='',encoding='utf-8-sig') as f:
 w=csv.writer(f);w.writerow(['Instance','Group','Role','Design notes','Volume mm3'])
 for q in serial:w.writerow([q['name'],q['group'],q['role'],q['note'],q['volume_mm3']])
print(json.dumps({'components':len(items),'sweep_wall_clearance':wall_min,'shutter_hits':len(motion),'gun_hits':len(gunhits),'blank_length':L}),flush=True)
