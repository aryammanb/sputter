from pathlib import Path
import json,struct,math
import numpy as np,cadquery as cq
P=Path(__file__).resolve().parent;m=json.loads((P/'parts.json').read_text());ss=cq.importers.importStep(str(P/'Complete sputter system R04.step')).val().Solids();items=[];k=0
for q in m:
 shapes=ss[k:k+q['solid_count']];k+=q['solid_count'];items.append(q|{'shape':cq.Compound.makeCompound(shapes) if len(shapes)>1 else shapes[0]})
V=cq.Vector
def cyl(rad,h,p,d=(0,0,1)):return cq.Solid.makeCylinder(rad,h,V(*p),V(*d))
door=cq.Solid.makeBox(228,16,316,V(-114,-132,-8)).cut(cyl(35,20,(0,-134,105),(0,1,0)))
for i in range(6):
 a=i*math.pi/3;door=door.cut(cyl(2.1,10,(52*math.cos(a),-132,105+52*math.sin(a)),(0,1,0)))
idx=next(i for i,q in enumerate(items) if q['role']=='door_plate');items[idx]['shape']=door;items[idx]['note']+=' Retainer pilot boresD4.2, depth10 from outer face, leave6mm solid backing; nominal tapped M5.'
for title,angle,shutter in [('Complete sputter system R04',0,0),('Complete sputter system R04 - loading',-110,80)]:
 a=cq.Assembly(name=title)
 for i,q in enumerate(items):
  shape=q['shape']
  if q['group']=='door':shape=shape.rotate((-118,-116,0),(-118,-116,1),angle)
  if q['group']=='shutter':shape=shape.rotate((-65,0,0),(-65,0,1),shutter)
  a.add(shape,name=f'{i:03}_'+q['name'].replace('/','_'),color=cq.Color(*q['color']))
 a.save(str(P/(title+'.step')));print('Updated blind-hole door:',title,flush=True)
a=cq.Assembly(name='Revised front door')
for i,q in enumerate(items):
 if q['group']=='door':a.add(q['shape'],name=str(i)+'_'+q['name'],color=cq.Color(*q['color']))
a.save(str(P/'Separate assemblies'/'Revised front door.step'))
# Update the actual display mesh and source, preserving all unchanged records.
old=P/'mesh.bin';chunks=[]
with old.open('rb') as f:
 for q in m:
  n=struct.unpack('<I',f.read(4))[0];chunks.append(f.read(n*36))
vs,fs=door.tessellate(.3,.35);ar=np.array([v.toTuple() for v in vs],dtype=np.float32)[np.array(fs)].astype('<f4');chunks[idx]=ar.tobytes()
with old.open('wb') as f:
 for data in chunks:f.write(struct.pack('<I',len(data)//36));f.write(data)
m[idx]['note']=items[idx]['note'];m[idx]['volume_mm3']=door.Volume();(P/'parts.json').write_text(json.dumps(m,indent=2))
p=P/'build_system.py';src=p.read_text().replace('cyl(2.1,20,(52*math.cos(a),-134,vz+52*math.sin(a))','cyl(2.1,10,(52*math.cos(a),-132,vz+52*math.sin(a))');p.write_text(src)
# A line along each screw axis stops atZ? Coordinates useY: blind endY-122, inner faceY-116.
assert door.isValid();assert all(door.isInside(V(52*math.cos(i*math.pi/3),-119,105+52*math.sin(i*math.pi/3)),1e-6) for i in range(6))
(P/'Door retainer bore check.json').write_text(json.dumps({'pilot_diameter_mm':4.2,'pilot_depth_mm':10,'door_thickness_mm':16,'remaining_solid_mm':6,'all_six_backings_checked_solid':True,'threads':'M5 nominal; actual tapping and screw engagement to detail'},indent=2))
print('All six retainer holes retain6mm solid backing',flush=True)
