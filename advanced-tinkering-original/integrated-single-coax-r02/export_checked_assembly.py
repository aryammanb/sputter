from pathlib import Path
import json,math,struct,csv,zipfile
import cadquery as cq
import numpy as np
from OCP.BRepExtrema import BRepExtrema_DistShapeShape

P=Path(__file__).resolve().parent;ROOT=P.parent;DEL=P/'STEP delivery';DEL.mkdir(exist_ok=True)
audit=json.loads((ROOT/'native-assembly-audit.json').read_text(encoding='utf-8-sig'))
report=json.loads((P/'geometry-verification.json').read_text());parts=report['new_parts'];removed=set(report['removed_source_components'])
log=json.loads((ROOT/'generated-parts.json').read_text(encoding='utf-8-sig'))
bounds={Path(x['path']).name:x['box_m'] for x in log}
original=json.loads((ROOT/'original-geometry.json').read_text(encoding='utf-8-sig'))
for q in original:bounds[q['name']+'.SLDPRT']=q['bodies'][0]['box_m']
source=cq.importers.importStep(str(ROOT/'Advanced Tinkering magnetron - full reconstruction.step')).val().Solids()
available=set(range(len(source)));items=[]
def net(file):
 if file in ['Backplate.SLDPRT','Kuehlkoerper.SLDPRT','Abstandshalter.SLDPRT','Magnet Joke.SLDPRT','Target Klemme.SLDPRT'] or any(s in file for s in ['M3x16','M3x35','M3x8','M4x10','titanium target','fitting body']):return 'live'
 if file=='Isolator.SLDPRT' or 'PTFE' in file or 'blue release' in file:return 'insulator'
 if 'blue coolant hose' in file:return 'water'
 if 'O-ring' in file:return 'seal'
 if 'outer magnet' in file:return 'outermag'
 if 'center magnet' in file:return 'centermag'
 return 'ground'
for c in audit['components']:
 file=Path(c['path']).name;t=c['transform'];pos=np.array(t[9:12])*1000
 if file in bounds:
  b=np.array(bounds[file]);local=(b[:3]+b[3:])/2*1000;pos=local@np.array(t[:9]).reshape(3,3)+pos
 choices=[i for i in available if abs(source[i].Volume()-c['volume_mm3'])<max(.01,c['volume_mm3']*.001)]
 assert choices,c['name'];i=min(choices,key=lambda i:np.linalg.norm(np.array(source[i].Center().toTuple())-pos));available.remove(i)
 if c['name'] in removed:continue
 items.append({'name':c['name'],'file':file,'shape':source[i],'net':net(file),'kind':'source retained','note':'Source geometry retained; original reconstruction assumptions still apply.'})
assert not available
for q in parts:
 s=cq.importers.importStep(q['step']).val();assert s.isValid() and len(s.Solids())==1
 items.append({'name':q['name'],'file':q['name']+'.SLDPRT','shape':s,'net':q['net'],'kind':'R02 new / modified','note':q['note']})
assert len(items)==129
colors={'live':(.88,.50,.25),'ground':(.48,.63,.71),'insulator':(.92,.89,.78),'jacket':(.20,.23,.28),'water':(.12,.39,.75),'seal':(.11,.15,.13),'outermag':(.78,.23,.25),'centermag':(.23,.4,.76)}
assembly=cq.Assembly(name='Integrated single coax magnetron R02')
for i,q in enumerate(items):assembly.add(q['shape'],name=f'{i+1:03}_'+q['file'].replace('.SLDPRT','').replace(' ','_'),color=cq.Color(*colors[q['net']]))
path=DEL/'Integrated single coax magnetron R02.step'
assembly.save(str(path))
reopened=cq.importers.importStep(str(path)).val().Solids();assert len(reopened)==129 and all(q.isValid() for q in reopened)
v0=sum(q['shape'].Volume() for q in items);v1=sum(q.Volume() for q in reopened);assert abs(v0-v1)<v0*1e-7
def string(f,s):
 b=s.encode();n=len(b)
 while n>=128:f.write(bytes([(n&127)|128]));n>>=7
 f.write(bytes([n]));f.write(b)
tris=0
with (P/'integrated-mesh.bin').open('wb') as f:
 for q in items:
  vertices,faces=q['shape'].tessellate(.10,.25);v=np.array([a.toTuple() for a in vertices]);a=v[np.array(faces)].astype('<f4');string(f,q['name']);string(f,q['file']);f.write(struct.pack('<i',len(a)));f.write(a.tobytes());tris+=len(a)
with (DEL/'Assembly BOM and limits.csv').open('w',newline='',encoding='utf-8-sig') as f:
 w=csv.writer(f);w.writerow(['Instance','Part','Electrical/display role','Evidence','Details'])
 for q in items:w.writerow([q['name'],q['file'],q['net'],q['kind'],q['note']])
live=[q for q in items if q['net']=='live'];ground=[q for q in items if q['net']=='ground']
minimum=(float('inf'),None,None)
# Check all new live/ground metal combinations and retained principal metal bodies.
focus=[q for q in items if q['kind'].startswith('R02')]
for a in focus:
 if a['net'] not in ['live','ground']:continue
 others=ground if a['net']=='live' else live
 for b in others:
  dist=BRepExtrema_DistShapeShape(a['shape'].wrapped,b['shape'].wrapped);dist.Perform();d=dist.Value()
  if d<minimum[0]:minimum=(d,a['file'],b['file'])
  assert d>1e-5,('Metal short',a['file'],b['file'],d)
status={'format':'STEP assembly with named/color-coded component instances','components':129,'valid_solids_on_reimport':129,'triangle_count':tris,'volume_before_mm3':v0,'volume_after_reimport_mm3':v1,'new_to_opposite_metal_node_minimum_distance_mm':minimum[0],'minimum_pair':minimum[1:],'minimum_note':'Includes the coax dielectric wall; this is a geometric separation, not a voltage rating or air-clearance qualification.','solidworks_native_conversion':'Not completed; both running SolidWorks instances were unresponsive. Supplied STEP assembly and individual new STEP parts remain available.','scope':'Mechanical integration study; reference clamp/lug geometry is dimensioned from catalogue data, not certified vendor CAD.'}
(P/'STEP-verification.json').write_text(json.dumps(status,indent=2))
for q in parts:
 target=DEL/Path(q['step']).name;target.write_bytes(Path(q['step']).read_bytes())
(P/'render-parts.json').write_text(json.dumps([{k:v for k,v in q.items() if k!='shape'} for q in items],indent=2))
print(json.dumps(status,indent=2),flush=True)
