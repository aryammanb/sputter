from pathlib import Path
import cadquery as cq,json
B=Path('advanced-tinkering-original/source')
def bb(s):
 b=s.BoundingBox();return [round(v,4) for v in [b.xmin,b.ymin,b.zmin,b.xmax,b.ymax,b.zmax]]
for name in ['Target Klemme','Dunkelraumabschirmung']:
 s=cq.importers.importStep(str(B/(name+'.step'))).val();out=[]
 for f in s.Faces():
  typ=f.geomType();d={'type':typ,'bb':bb(f),'area':round(f.Area(),2)}
  if typ=='CYLINDER':d['radius']=round(f._geomAdaptor().Cylinder().Radius(),4)
  if typ in ['PLANE','CYLINDER']:out.append(d)
 print(name,json.dumps(out))
