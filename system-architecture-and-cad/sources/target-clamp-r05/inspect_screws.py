from pathlib import Path
import cadquery as cq,math
s=cq.importers.importStep('advanced-tinkering-original/balanced-twelve-stack-study/Proposed cooler.step').val()
for f in s.Faces():
 if f.geomType()=='CYLINDER':
  c=f._geomAdaptor().Cylinder();r=c.Radius();l=c.Axis().Location();b=f.BoundingBox()
  if 1.1<r<1.7 and abs(math.hypot(l.X(),l.Z())-40)<.1:print('cooler target screw pilot',r,'axis',l.X(),l.Z(),'Y',b.ymin,b.ymax)
