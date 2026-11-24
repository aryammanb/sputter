from pathlib import Path
import json,math,struct,csv,time
import numpy as np
import cadquery as cq
P=Path(__file__).resolve().parent;ROOT=P.parent.parent;V=cq.Vector
base=P.parent/'complete-chamber-r01'/'build_assembly.py'
env={'__file__':str(base),'__name__':'system_base'}
exec(compile(base.read_text().split('outparts=P/')[0],str(base),'exec'),env)
items=[q for q in env['items'] if q['role'] not in ['gun_adapter','gun_mount_clamp','gun_mount_seal','support']]
box,cyl,ann,kf25,rr=[env[k] for k in ['box','cyl','ann','kf25','rr']]
def add(name,s,role,color=(.62,.68,.73),note='',group='system'):
 assert s.isValid() or role=='backing_pump',name
 items.append(dict(name=name,shape=s,role=role,color=color,note=note,group=group));return s
def bb(s):
 b=s.BoundingBox();return [b.xmin,b.ymin,b.zmin,b.xmax,b.ymax,b.zmax]
def oriented(shape,origin,d):
 shape=shape.rotate((0,0,0),(0,0,1),0)
 # local +Z -> arbitrary axis
 z=V(0,0,1);d=V(*d)
 if d.z<-.999:shape=shape.rotate((0,0,0),(1,0,0),180)
 elif d.z<.999:
  axis=z.cross(d);angle=math.degrees(math.acos(d.z));shape=shape.rotate((0,0,0),axis.toTuple(),angle)
 return shape.translate(origin)
def tube(ri,ro,L,p,d):return ann(ri,ro,L,p,d)
def kf_terminal(p,d,size=25,L=12):
 ro,neck,ri=(19.94,12.7,11.1125) if size==25 else (15,9.525,8)
 s=ann(ri,ro,4.32,(0,0,0)).fuse(ann(ri,neck,L-4.32,(0,0,4.32)))
 return oriented(s,p,d)
def joint(name,p,d,size=25,group='system'):
 # p is centre of three-mm face-seal gap; nominal clamp envelope.
 ro=19.94 if size==25 else 15
 seal=oriented(ann(ro-8,ro-3,3,(0,0,-1.5)),p,d)
 add(name+' face seal',seal,'connection_seal',(.13,.19,.19),note='Nominal FKM/centering envelope, not supplier seal CAD.',group=group)
 ring=ann(ro+.1,ro+5.5,11,(0,0,-5.5))
 for side in [-1,1]:
  half=ring.intersect(box(-40 if side<0 else .35,-40,-7,39.65,80,14))
  add(name+(' clamp left' if side<0 else ' clamp right'),oriented(half,p,d),'kf_clamp',(.43,.52,.58),note='Split KF clamp outline; detailed purchased hardware/actuator simplified.',group=group)
def hex_prism(radius,L,p,d,bore=0):
 s=cq.Workplane('XY').polygon(6,2*radius).extrude(L).val()
 if bore:s=s.cut(cyl(bore,L+2,(0,0,-1)))
 return oriented(s,p,d)

# Refined fitting mechanism: order retained by the STEP assembly traversal.
fitmeta=json.loads((P.parent/'compression-fitting-r02'/'fitting-parts.json').read_text())
fits=cq.importers.importStep(str(P.parent/'compression-fitting-r02'/'Refined compression fitting - assembled.step')).val().Solids()
assert len(fits)==len(fitmeta)==11
for q,s in zip(fitmeta,fits):add(q['name'],s,'fit_'+q['role'],q['color'],q['note'],'fitting')
assert abs(bb(next(q['shape'] for q in items if q['role']=='fit_body'))[2]-333)<.01

# Independent stand carries chamber mass; turbo does not support the chamber.
add('System base plate',box(-150,-220,-320,800,740,6),'base_plate',(.26,.32,.37),note='Layout/support concept only; structural sizing not verified.')
for x in [-85,85]:
 for y in [-75,75]:add(f'Chamber riser {x} {y}',box(x-12.5,y-12.5,-314,25,25,304),'frame',(.31,.38,.43))
for y in [-75,75]:add(f'Chamber support lower tie {y}',box(-97.5,y-12.5,-314,195,25,25),'frame',(.31,.38,.43))

# EXT70 exterior reconstructed from Edwards B722-01-880 Issue K figure4.
tz=-48.0
prof=[(0,-124.45),(47,-124.45),(47,-62),(35,-38),(35,-12),(47.5,-12),(47.5,0),(0,0)]
shell=cq.Workplane('XZ').polyline(prof).close().revolve(360,(0,0),(0,1)).val().cut(cyl(31.75,75,(0,0,-75)))
shell=shell.cut(cyl(8,70,(0,0,-124.45),(1,0,0)))
add('EXT70 reference pump housing and ISO63 inlet',shell.translate((0,0,tz)),'turbo_body',(.57,.64,.69),note='Reconstructed external envelope: D95 inlet, D94 body, 157.05 overall incl base. Internal pump geometry omitted.')
add('EXT70 lower motor core',cyl(40.5,32.6,(0,0,tz-157.05)),'turbo_core',(.32,.39,.44))
for z in [-153.5,-146,-138.5,-131]:add(f'EXT70 cooling fin {z}',ann(40.5,47,3.5,(0,0,tz+z)),'turbo_fin',(.58,.64,.67))
out_z=tz-124.45
outlet=tube(8,9.525,20,(40,0,out_z),(1,0,0)).fuse(tube(8,15,4.32,(58.68,0,out_z),(1,0,0)))
add('EXT70 native KF16 backing outlet',outlet,'turbo_outlet',note='Standard EXT70 manual specifies DN16NW. KF25 hose is attached through a reducer adapter.')
vent=cyl(7,9,(0,-47,tz-74),(0,-1,0)).fuse(cyl(10,6,(0,-56,tz-74),(0,-1,0)))
add('EXT70 vent valve exterior',vent,'turbo_vent',(.31,.37,.42),note='Reference exterior detail; actual vent valve not selected.')
add('EXT70 electrical connector exterior',cyl(11,9,(0,-47,tz-108),(0,-1,0)),'turbo_connector',(.25,.29,.34))
for sign in [-1,1]:add(f'EXT70 cooling stub {sign}',cyl(3.5,22,(32*sign,-35,tz-133),(sign,0,0)),'turbo_cooling',(.66,.57,.35))
add('ISO63 chamber to turbo face seal',ann(32,37,3,(0,0,-48)),'iso_seal',(.12,.19,.18))
for i in range(4):
 a=45+i*90
 claw=box(45,-4,-66,20,8,6).fuse(box(45,-4,-33,20,8,6),box(58,-4,-60,7,8,27))
 claw=claw.cut(cyl(3.3,40,(61,0,-67)))
 screw=cyl(3,39,(61,0,-66)).fuse(hex_prism(5.5,4,(61,0,-70),(0,0,1),0))
 add(f'ISO63 double claw clamp {i+1}',claw.rotate((0,0,0),(0,0,1),a),'iso_clamp',(.38,.46,.51),note='Four clamp positions. Geometry envelope only; rated fixing and rotor-failure torque requirements not verified.')
 add(f'ISO63 clamp screw {i+1}',screw.rotate((0,0,0),(0,0,1),a),'iso_screw',(.58,.63,.67))

# Native KF16 -> KF25 transition so the requested foreline hose is KF25.
joint('Turbo KF16 outlet joint',(64.5,0,out_z),(1,0,0),16)
red=kf_terminal((66,0,out_z),(1,0,0),16,12)
red=red.fuse(tube(8,10,19,(78,0,out_z),(1,0,0)),kf_terminal((104,0,out_z),(-1,0,0),25,12))
add('KF16 to KF25 foreline adapter',red,'foreline_adapter',note='Reference 38mm face-to-face transition; supplier dimensions to confirm. Omit if actual EXT70 has a confirmed KF25 outlet.')
joint('KF25 turbo hose joint',(105.5,0,out_z),(1,0,0))
add('KF25 hose turbo-end termination',kf_terminal((107,0,out_z),(1,0,0),25,10),'hose_end')

# Imported real supplier RV3 CAD, not an invented mechanical-pump silhouette.
rv_file=P/'Supplier references'/'Edwards RV3 - healed reference.step'
if not rv_file.exists():rv_file=P/'Supplier references'/'Edwards RV3 - IdealVac P101919.step'
rv=cq.importers.importStep(str(rv_file)).val()
rv_offset=(430,377.5,-212)
rv=rv.translate(rv_offset)
add('Edwards RV3 - imported supplier STEP',rv,'backing_pump',(.22,.43,.57),note='IdealVac P101919 STEP, representing Edwards RV3. Layout reference, not a confirmed pump purchase. Source has pre-existing topology defects; retained as supplier visual/reference geometry, not a manufacturing solid.')
inlet=(393,325,-83.6)
joint('RV3 inlet KF25 hose joint',(393,325,-82.1),(0,0,1))
add('KF25 hose RV3-end termination',kf_terminal((393,325,-80.6),(0,0,1),25,14.6),'hose_end')

points=[V(117,0,out_z)]
control_sets=[[(117,0,out_z),(200,0,out_z),(260,0,-100),(270,100,-20)],
 [(270,100,-20),(280,200,60),(320,290,60),(355,290,50)],
 [(355,290,50),(390,290,40),(393,325,-10),(393,325,-66)]]
path=cq.Wire.assembleEdges([cq.Edge.makeBezier([V(*p) for p in controls]) for controls in control_sets])
plane=cq.Plane(origin=points[0],normal=V(1,0,0),xDir=V(0,1,0))
hose=cq.Workplane(plane).circle(13.5).circle(11.1125).sweep(path,isFrenet=False).val()
add('KF25 flexible backing hose - routed core',hose,'hose',(.53,.59,.62),note='Nominal bore22.225 / coreOD27. Routing and bend radius are layout assumptions; select actual hose after checking minimum bend radius.')
ribs=[]
for u in np.linspace(.015,.985,64):
 pt=path.positionAt(float(u));tan=path.tangentAt(float(u));ribs.append(tube(13.3,16,1.8,(pt-tan*.9).toTuple(),tan.toTuple()))
add('KF25 backing hose corrugations',cq.Compound.makeCompound(ribs),'hose_ribs',(.69,.73,.75),note='64 nominal corrugation ribs for visual/reference routing only.')
print('Turbo, ISO clamps, supplier RV3 and KF25 hose built',flush=True)

# Rear gauges: protective90-degree elbows, gauges projecting down and away from deposition.
def gauge_elbow(x):
 es=[cq.Edge.makeLine(V(x,147.452,90),V(x,160,90)),cq.Edge.makeThreePointArc(V(x,160,90),V(x,177.6776695,82.6776695),V(x,185,65)),cq.Edge.makeLine(V(x,185,65),V(x,185,59.32))]
 pa=cq.Wire.assembleEdges(es);pl=cq.Plane(origin=V(x,147.452,90),normal=V(0,1,0),xDir=V(1,0,0))
 s=cq.Workplane(pl).circle(12.7).circle(11.1125).sweep(pa,isFrenet=False).val()
 return s.fuse(kf_terminal((x,143.132,90),(0,1,0),25,4.32),kf_terminal((x,185,55),(0,0,1),25,4.32))
for x,typ,diam,length in [(-50,'Pirani',44,74),(50,'Penning',58,94)]:
 add(typ+' protective KF25 elbow',gauge_elbow(x),'gauge_elbow',note='Reference R25 centreline elbow. Protects sensor from direct target line of sight; actual orientation per selected gauge manual.')
 joint(typ+' rear port joint',(x,141.632,90),(0,1,0))
 joint(typ+' gauge joint',(x,185,53.5),(0,0,1))
 gf=kf_terminal((x,185,52),(0,0,-1),25,12)
 add(typ+' KF25 sensor stem',gf,'gauge_stem')
 body=cyl(diam/2,length,(x,185,40-length))
 add(typ+' gauge reference housing',body,'gauge_'+typ.lower(),(.24,.49,.64) if typ=='Pirani' else (.39,.42,.57),note=f'Generic {typ} sensor envelope, D{diam} x{length}; exact make/model not supplied. Not a metrology or magnetic-clearance qualification.')
 for z in [40-length+4,36]:add(typ+f' housing band {z}',ann(diam/2,diam/2+1.5,3,(x,185,z)),'gauge_band',(.65,.69,.72))
 add(typ+' electrical connector',cyl(6,11,(x,185,29-length)),'gauge_connector',(.16,.2,.24))

# MFC output: KF25 female VCR adapter onto male-VCR MFC.
joint('MFC chamber KF25 joint',(0,141.632,210),(0,1,0))
adapter=kf_terminal((0,143.132,210),(0,1,0),25,12)
adapter=adapter.fuse(tube(2.3,6.35,22.544,(0,155.132,210),(0,1,0)))
add('KF25 to quarter-inch female VCR adapter body',adapter,'mfc_out_adapter',note='Functional reference envelope; nominal total face-to-face34.544 per ANCORP1.36in configuration, supplier selection pending.')
add('MFC outlet female VCR swivel nut',hex_prism(10.5,15,(0,164.676,210),(0,1,0),6.5),'vcr_out_nut',(.68,.72,.75),note='Female mating connection around MFC male face seal; external thread detail simplified.')
add('MFC outlet VCR metal gasket',tube(2.3,5.5,.76,(0,177.676,210),(0,1,0)),'vcr_gasket',(.75,.7,.48),note='Nominal visual gasket envelope; actual gasket specification per fittings.')
mfc_out=178.436;mfc_in=mfc_out+124;body0=mfc_out+23.9
basebody=box(-19,body0,197.3,38,76.2,25.4)
for y in [body0+19.05,body0+57.15]:basebody=basebody.cut(cyl(1.65,5,(0,y,197.3)))
add('MFC stainless flow body',basebody,'mfc_body',(.61,.66,.69),note='HORIBA SEC-E440J-style reference: VCR face-to-face124, body76.2, width38, nominal height115. Ports male VCR on both ends as instructed.')
add('MFC electronics housing',box(-19,body0,222.7,38,76.2,77.6),'mfc_electronics',(.4,.47,.52))
for name,p,d in [('outlet',(0,mfc_out,210),(0,1,0)),('inlet',(0,mfc_in,210),(0,-1,0))]:
 add('MFC male VCR '+name,tube(2.3,5.55,23.9,p,d),'mfc_male_vcr',note='Nominal quarter-inch male VCR port; supplier face/bead/thread tolerances not modeled.')
add('MFC top signal connector',box(-14,body0+22,300.3,28,14,12),'mfc_signal',(.18,.23,.29))
# MFC bracket supports mass independently of the chamber connection.
bracket=box(-30,110,194.8,60,177,2.5).cut(box(-22,110,194.7,44,85,3))
for y in [body0+19.05,body0+57.15]:bracket=bracket.cut(cyl(2.25,4,(0,y,194)))
add('Rear MFC support shelf',bracket,'mfc_bracket',(.35,.43,.48),note='Mounting layout only; bracket load/weld/fasteners not validated.')
assert bracket.intersect(adapter).Volume()<.0001,'MFC shelf obstructs KF/VCR adapter'
for x in [-30,27.5]:
 add(f'MFC shelf gusset {x}',cq.Workplane('YZ',origin=(x,0,0)).polyline([(110,165),(110,194.8),(175,194.8)]).close().extrude(2.5).val(),'mfc_bracket')
for y in [body0+19.05,body0+57.15]:
 add(f'MFC mount screw {y}',cyl(2,7,(0,y,191.3)).fuse(cyl(3.5,2,(0,y,189.3))),'mfc_mount_screw',note='Nominal M4 envelope.')

# Upstream chain ends at a6mm push-to-connect collet. No cylinder/regulator/tubing added.
add('MFC inlet VCR metal gasket',tube(2.3,5.5,.76,(0,mfc_in,210),(0,1,0)),'vcr_gasket',(.75,.7,.48))
add('MFC inlet female VCR swivel nut',hex_prism(10.5,16,(0,mfc_in-2,210),(0,1,0),5.65),'vcr_in_nut',(.68,.72,.75))
up_start=mfc_in+.76
vcrnpt=tube(2.3,6.2,18,(0,up_start+2,210),(0,1,0)).fuse(hex_prism(9.8,22,(0,up_start+14,210),(0,1,0),3))
vcrnpt=vcrnpt.cut(cyl(5.9,9,(0,up_start+27,210),(0,1,0)))
add('Female VCR to quarter-inch female NPT adapter',vcrnpt,'vcr_npt_adapter',note='Adapter-assembly reference from prior chat; SS-4-WVCR-7-4 cited body requires compatible swivel nut/gland. End geometry illustrative.')
pushbase=up_start+36
push=tube(3,6.6,9,(0,pushbase-8,210),(0,1,0)).fuse(hex_prism(9.25,8,(0,pushbase,210),(0,1,0),3),tube(3,7.5,10,(0,pushbase+8,210),(0,1,0)))
add('Quarter-inch male NPT to6mm push fitting body',push,'push_body',(.72,.61,.34),note='6mm OD tube x1/4 male NPT interface; Amazon B09H4RL894 selected in prior chat. Parker W68LF-6M-4 was reference. Pressure/gas compatibility not verified.')
add('6mm push fitting release collet',tube(3,6.7,3,(0,pushbase+18,210),(0,1,0)),'push_collet',(.16,.43,.72),note='Gas-supply boundary of this model. No tube beyond push fitting.')

# Blank right spare ports with removable KF25 caps.
for z in [75,225]:
 joint(f'Right spare {z}',(141.632,0,z),(1,0,0))
 add(f'Right spare KF25 blank cap {z}',oriented(cyl(19.94,4.32,(0,0,0)),(143.132,0,z),(1,0,0)),'blank_cap',(.62,.68,.72))

print('Rear gauges and complete MFC chain through push fitting built',len(items),'instances',flush=True)
def state(q,door=0,shutter=0,gap=100):
 s=q['shape']
 if q['group']=='gun':s=s.translate((0,0,gap-100))
 if q['group']=='door':s=s.rotate((-118,-116,0),(-118,-116,1),door)
 if q['group']=='shutter':s=s.rotate((-65,0,0),(-65,0,1),shutter)
 return s

for title,da,sa in [('Full sputter system R03 - closed',0,0),('Full sputter system R03 - loading',-110,80)]:
 a=cq.Assembly(name=title)
 for i,q in enumerate(items):a.add(state(q,da,sa),name=f'{i:03}_{q["name"].replace("/","_")}',color=cq.Color(*q['color']))
 a.save(str(P/(title+'.step')));print('Exported',title,flush=True)
out=P/'Separate assemblies';out.mkdir(exist_ok=True)
for title,roles in [('Turbo and ISO63 connection',{'turbo_body','turbo_core','turbo_fin','turbo_outlet','turbo_vent','turbo_connector','turbo_cooling','iso_seal','iso_clamp','iso_screw','foreline_adapter'}),('MFC and adapters to push fitting',{'mfc_out_adapter','vcr_out_nut','vcr_gasket','mfc_body','mfc_electronics','mfc_male_vcr','mfc_signal','mfc_bracket','mfc_mount_screw','vcr_in_nut','vcr_npt_adapter','push_body','push_collet'}),('Gauge installation',{'gauge_elbow','gauge_stem','gauge_pirani','gauge_penning','gauge_band','gauge_connector'}),('Backing pump and KF25 hose',{'backing_pump','hose','hose_ribs','hose_end','foreline_adapter'})]:
 a=cq.Assembly(name=title)
 for i,q in enumerate(items):
  if q['role'] in roles:a.add(q['shape'],name=f'{i:03}_{q["name"]}',color=cq.Color(*q['color']))
 a.save(str(out/(title+'.step')))

# Actual mesh/solid data for the rendered walkthrough and CAD review.
serial=[]
with (P/'mesh.bin').open('wb') as f:
 for i,q in enumerate(items):
  vs,fs=q['shape'].tessellate(.25,.32);a=np.array([v.toTuple() for v in vs],dtype=np.float32)[np.array(fs)].astype('<f4')
  f.write(struct.pack('<I',len(a)));f.write(a.tobytes())
  serial.append({k:v for k,v in q.items() if k!='shape'}|{'bbox_mm':bb(q['shape']),'volume_mm3':q['shape'].Volume(),'solid_count':len(q['shape'].Solids())})
  if i%60==0:print('Meshed',i,'/',len(items),flush=True)
(P/'parts.json').write_text(json.dumps(serial,indent=2))
with (P/'System parts list.csv').open('w',newline='',encoding='utf-8-sig') as f:
 w=csv.writer(f);w.writerow(['Instance','Group','Role','Reference / scope','Volume mm3'])
 for q in serial:w.writerow([q['name'],q['group'],q['role'],q['note'],q['volume_mm3']])
report={'instances':len(items),'solids':sum(q['solid_count'] for q in serial),'all_shapes_valid':all(q['shape'].isValid() for q in items),
 'dimensions_mm':{'chamber_internal':[200,200,300],'stage_D_thickness':[90,6],'substrate':[50,50,1],'target_substrate_gap':[75,150],'shutter_substrate_gap':12,
 'EXT70_reference_height':157.05,'EXT70_inlet_face_z':tz,'EXT70_bottom_z':tz-157.05,'EXT70_native_outlet':'KF16, adapted to KF25','turbo_outlet_centre_z':out_z,
 'RV3_import_bbox_mm':bb(rv),'RV3_inlet_centre':inlet,'RV3_placement_translation':rv_offset,'hose_centreline_length':path.Length(),
 'hose_path_samples':[path.positionAt(float(u)).toTuple() for u in np.linspace(0,1,121)],
 'MFC_VCR_face_to_face':124,'MFC_body_width':38,'MFC_reference_height':115,'MFC_output_face_y':mfc_out,'MFC_inlet_face_y':mfc_in,
 'push_socket_face_y':pushbase+21,'MFC_gas_axis_z':210,'gauge_centres_x':[-50,50],'gauge_elbow_radius':25},
 'references':{'RV3_supplier_STEP':'https://www.idealvac.com/files/cad/P101919.step','EXT70_manual':'https://mmrc.caltech.edu/Vacuum/Edwards/EXPT%20Pumping%20Station/EXT70%20EXT250%20-%20B72201880%20-%20Instruction%20manual.pdf',
 'MFC_reference':'https://static.horiba.com/fileadmin/Horiba/Semiconductor/Resources/Manual_Downloads/others/I030106200.pdf',
 'VCR_NPT_reference':'https://products.swagelok.com/en/c/straights/p/SS-4-WVCR-7-4','push_fitting_selected':'https://www.amazon.in/dp/B09H4RL894'},
 'scope':'System mechanical layout. Supplier RV3 CAD imported; turbo exterior from manual; gauges/adapters/reference fitting internals illustrative. Existing chamber seal/pressure/gun qualification limitations retained.'}
(P/'System dimension report.json').write_text(json.dumps(report,indent=2))
print(json.dumps({'instances':len(items),'solids':report['solids'],'hose_length':path.Length(),'push_end_y':pushbase+21}),flush=True)
