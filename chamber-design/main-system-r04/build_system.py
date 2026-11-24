from pathlib import Path
import json,math,struct,csv
import numpy as np
import cadquery as cq
P=Path(__file__).resolve().parent;B=P.parent/'full-system-r03';src=B/'build_system.py';env={'__file__':str(src),'__name__':'r04base'}
exec(compile(src.read_text().split("for title,da,sa in")[0],str(src),'exec'),env)
items=env['items'];V=cq.Vector
box,cyl,ann,bb,oriented=[env[k] for k in ['box','cyl','ann','bb','oriented']]
def add(name,s,role,color=(.6,.65,.7),note='',group='utilities'):
 assert s.isValid(),name
 items.append(dict(name=name,shape=s,role=role,color=color,note=note,group=group))
# Lower the entire viewport assembly, and remake the door cutout at the same nominal diameter.
vz=105;dz=vz-175
for q in items:
 if q['role']=='door_plate':
  s=box(-114,-132,-8,228,16,316).cut(cyl(35,20,(0,-134,vz),(0,1,0)))
  for i in range(6):
   a=i*math.pi/3;s=s.cut(cyl(2.1,10,(52*math.cos(a),-132,vz+52*math.sin(a)),(0,1,0)))
  q['shape']=s;q['note']+=' R04 viewport centre Z105, clear diameter70; sightline checked at default gap100.'
 elif q['role'] in ['viewport_seal','glass','door_screw','viewport_bezel']:q['shape']=q['shape'].translate((0,0,dz))

def route(name,segments,ro,ri,role,color,note):
 es=[cq.Edge.makeBezier([V(*p) for p in ps]) for ps in segments];path=cq.Wire.assembleEdges(es);start=segments[0][0];normal=np.array(segments[0][1])-start
 s=cq.Solid.sweep(cq.Wire.makeCircle(ro,V(*start),V(*normal)),[cq.Wire.makeCircle(ri,V(*start),V(*normal))] if ri else [],path,True,False)
 add(name,s,role,color,note);return path
blue=(.15,.48,.92);red=(.92,.28,.18)
# Actual six-mm tube fits the existing nominal six-mm socket. Insertion is a chosen illustration.
add('6 mm OD gas tube - seated end',ann(2,3,45.804,(0,344.196,210),(0,1,0)),'gas_insert',(.74,.84,.91),'OD6 ID4; socket mouthY360.196; nominal engagement16mm is illustrative, vendor insertion depth still required.')
gas=[[(0,390,210),(0,500,210),(170,530,330),(300,500,390)],[(300,500,390),(430,470,450),(500,430,440),(570,430,440)]]
route('Argon supply tube - 6 mm OD',gas,3,2,'gas_line',(.74,.84,.91),'Actual modeled OD6; material, pressure rating and regulator/push fitting compatibility to select.')
add('Representative argon cylinder',cyl(75,660,(650,430,-290)).fuse(cq.Solid.makeSphere(75,V(650,430,370)).intersect(box(570,350,370,160,160,75))), 'cylinder',(.18,.42,.54),'Representative cylinder only, not a supplier pressure-vessel model.')
add('Cylinder foot',ann(66,79,30,(650,430,-320)),'cylinder',(.23,.28,.32))
add('Cylinder valve',cyl(15,35,(650,430,420)).fuse(box(620,421,445,60,18,8)),'regulator',(.65,.52,.25))
add('Representative argon regulator',box(590,412,420,60,36,40).fuse(cyl(10,20,(570,430,440),(1,0,0))),'regulator',(.7,.57,.29))
for x in [605,640]:
 add('Regulator gauge '+str(x),cyl(22,12,(x,400,480),(0,-1,0)),'regulator',(.6,.65,.69))
 add('Regulator dial '+str(x),cyl(19,1,(x,387,480),(0,-1,0)),'regulator_dial',(.91,.94,.94))
# Two independent cooling systems, deliberately simple equipment envelopes.
for num,x,y in [(1,-500,-120),(2,600,-150)]:
 add('Cooling system '+str(num)+' cabinet',box(x,y,-320,220,240,350),'chiller'+str(num),(.23,.39,.51),'Representative envelope; cooling duty, pump flow and water quality not selected.')
 add('Cooling system '+str(num)+' display',box(x+40,y-2,-80,90,3,35),'chiller'+str(num),(.08,.16,.2))
 for z in range(-250,-120,15):add('Chiller '+str(num)+' vent '+str(z),box(x+25,y-3,z,170,3,3),'chiller'+str(num),(.1,.18,.23))
# Existing gun hoses end at X+/-3,Y0,Z443; extensions use the same OD4/ID2.5.
for k,(x,yy,col) in enumerate([(3,-40,blue),(-3,-10,red)]):
 route('Gun cooling '+('supply' if k==0 else 'return'),[[(x,0,443),(x,0,535+k*14),(-180,yy,535+k*14),(-230,yy,220)], [(-230,yy,220),(-250,yy,94),(-220,yy,-40),(-280,yy,-40)]],2,1.25,'gun_water',col,'Representative flexible extension; nominal4mm OD matches current gun hoses. Service loop and bend/flow suitability not qualified.')
for k,(sx,ey,col) in enumerate([(54,-100,(.1,.78,.9)),(-54,-70,(.95,.68,.16))]):
 seg=([[(54,-35,-181),(150,-35,-181),(210,-100,-100),(340,-100,-100)],[(340,-100,-100),(430,-100,-100),(500,-100,-100),(600,-100,-100)]] if sx>0 else [[(-54,-35,-181),(-150,-35,-181),(-150,-190,-181),(90,-190,-150)],[(90,-190,-150),(330,-190,-119),(480,-70,-100),(600,-70,-100)]])
 route('Turbo cooling '+('supply' if k==0 else 'return'),seg,4.5,3,'turbo_water',col,'Nominal OD9/ID6 reinforced-hose reference loop; pump stub connections require selected hose/adapters, no supplier seating claim.')
# Electrical source, RF matching network and physical cable continuation.
add('Representative DC or RF power supply',box(300,-380,-320,260,160,180),'power',(.3,.33,.4),'Representative supply. DC option or RF option with suitable matching network; ratings and interlocks not selected.')
add('Power supply display',box(320,-383,-205,110,3,40),'power_display',(.08,.19,.23))
for x in [470,520]:add('Power control '+str(x),cyl(12,12,(x,-380,-190),(0,-1,0)),'power',(.65,.68,.7))
add('RF matching network - RF configuration only',box(330,-210,-170,190,100,90),'matching',(.44,.47,.52),'RF-only representative matching network. DC configuration bypasses this enclosure.')
route('RF supply to matching network cable', [[(430,-220,-160),(430,-200,-100),(430,-240,-80),(430,-210,-100)]],3,0,'power_cable',(.18,.19,.21),'Representative cable; connector, impedance and power rating pending.')
route('Power cable to gun coax', [[(0,-4.5,453),(0,-4.5,570),(180,-200,570),(250,-210,300)],[(250,-210,300),(320,-220,30),(430,-150,30),(430,-150,-80)]],2.5,0,'power_cable',(.19,.2,.23),'OD5 study allowance continues existing coax at(0,-4.5,453); RF shown via matching network, DC bypass described.')
route('Representative protective earth bond', [[(540,-380,-280),(570,-380,-280),(180,-180,-270),(110,-100,-80)]],2,0,'earth',(.45,.72,.17),'Representative protective bonding connection. Grounding/RF return scheme requires electrical design.')
# Exports retain exact previous component shapes, aside from explicitly revised viewport.
for title,door,shutter in [('Complete sputter system R04',0,0),('Complete sputter system R04 - loading',-110,80)]:
 a=cq.Assembly(name=title)
 for i,q in enumerate(items):a.add(env['state'](q,door,shutter),name=f'{i:03}_'+q['name'].replace('/','_'),color=cq.Color(*q['color']))
 a.save(str(P/(title+'.step')));print('Exported',title,flush=True)
serial=[]
with (P/'mesh.bin').open('wb') as f:
 for i,q in enumerate(items):
  vs,fs=q['shape'].tessellate(.3,.35);ar=np.array([v.toTuple() for v in vs],dtype=np.float32)[np.array(fs)].astype('<f4');f.write(struct.pack('<I',len(ar)));f.write(ar.tobytes())
  serial.append({k:v for k,v in q.items() if k!='shape'}|{'bbox_mm':bb(q['shape']),'volume_mm3':q['shape'].Volume(),'solid_count':len(q['shape'].Solids()),'valid':q['shape'].isValid()})
  if i%75==0:print('Meshed',i,flush=True)
(P/'parts.json').write_text(json.dumps(serial,indent=2))
r=json.loads((B/'System dimension report.json').read_text());r['dimensions_mm'].update(viewport_centre_z=105,viewport_clear_diameter=70,gas_tube_OD=6,gas_tube_ID=4,gas_tube_illustrative_insertion=16);r['instances']=len(items);r['solids']=sum(q['solid_count'] for q in serial);r['invalid_references']=[q['name'] for q in serial if not q['valid']];(P/'System dimension report.json').write_text(json.dumps(r,indent=2))
with (P/'System parts list.csv').open('w',newline='',encoding='utf-8-sig') as f:
 w=csv.writer(f);w.writerow(['Name','Role','Group','Scope / reference','Valid']);w.writerows([q['name'],q['role'],q['group'],q['note'],q['valid']] for q in serial)
print('R04 complete',len(items),'instances',r['solids'],'solids',flush=True)
