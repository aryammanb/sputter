import json
from pathlib import Path
import cadquery as cq
P=Path(__file__).resolve().parent;R=P.parent
ss=cq.importers.importStep(str(P/'Vented head guard - local mechanical concept.step')).val().Solids()
g=json.loads((P/'geometry.json').read_text());parts={}
for role in ['PTFE non-load-bearing head guard','PTFE vented removable cap']:
 q=next(q for q in g if q['name']==role);parts[role]=min(ss,key=lambda s:abs(s.Volume()-q['volume_mm3']))
original=cq.importers.importStep(str(R/'Advanced Tinkering magnetron - full reconstruction.step')).val().Solids()
audit=json.loads((R/'native-assembly-audit.json').read_text(encoding='utf-8-sig'))
places=[q for q in audit['components'] if q['name'].startswith('03') and 'shoulder sleeve' in q['name']];assert len(places)==12
def overlaps(a,b):
 a=a.BoundingBox();b=b.BoundingBox()
 return all(getattr(a,axis+'min')<getattr(b,axis+'max')-1e-6 and getattr(b,axis+'min')<getattr(a,axis+'max')-1e-6 for axis in ['x','y','z'])
hits=[]
for place in places:
 x,y,z=[q*1000 for q in place['transform'][9:12]]
 for name,shape in parts.items():
  s=shape.translate((x,0,z))
  for i,t in enumerate(original):
   if abs(t.Volume()-157043.93307247563)<1 and abs(t.BoundingBox().ymin+74)<.001 and abs(t.BoundingBox().ymax+46)<.001:continue # Exported Boden mass differs slightly from native; its pocket is intentionally redesigned.
   if not overlaps(s,t):continue
   common=s.intersect(t);v=common.Volume() if common.Solids() else 0
   if v>1e-4:hits.append({'position':place['name'],'new':name,'source_solid_index':i,'volume_mm3':v})
report={'guard_positions_checked':12,'new_guard_and_cap_solids_checked':24,'excluded':'Original Boden; proposed pocket replacement and thread contact require separate machining design.','unwanted_intersections':hits,'scope':'Checks external guard/cap envelopes against original reconstructed assembly. Does not check changed counterbore walls, threads, tolerances, RF performance or assembly access.'}
(P/'Guard envelope checks.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2),flush=True)
