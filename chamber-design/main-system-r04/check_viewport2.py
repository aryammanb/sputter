from pathlib import Path
import json,struct,numpy as np,vtk
from vtk.util.numpy_support import numpy_to_vtk,numpy_to_vtkIdTypeArray
P=Path(__file__).resolve().parent;B=P.parent/'full-system-r03';meta=json.loads((B/'parts.json').read_text());aa=[]
with (B/'mesh.bin').open('rb') as f:
 for q in meta:
  n=struct.unpack('<I',f.read(4))[0];a=np.frombuffer(f.read(n*36),'<f4').reshape(-1,3,3)
  if q['group']=='gun':aa.append(a)
a=np.concatenate(aa);pd=vtk.vtkPolyData();pts=vtk.vtkPoints();pts.SetData(numpy_to_vtk(a.reshape(-1,3),deep=True));pd.SetPoints(pts);cells=vtk.vtkCellArray();cells.SetData(numpy_to_vtkIdTypeArray(np.arange(0,len(a)*3+1,3,dtype=np.int64)),numpy_to_vtkIdTypeArray(np.arange(len(a)*3,dtype=np.int64)));pd.SetPolys(cells);loc=vtk.vtkOBBTree();loc.SetDataSet(pd);loc.BuildLocator()
results=[]
for vz in [175,140,125,115,105]:
 for ez in [80,100,120,140,160,175]:
  eye=np.array([0.,-400.,ez]);visible=0;aperture=0
  for th in np.linspace(0,2*np.pi,72,endpoint=False):
   target=np.array([20*np.cos(th),20*np.sin(th),125.]);d=target-eye
   ok=True
   for yy in [-146,-114]:
    p=eye+d*((yy-eye[1])/d[1]);ok &= p[0]**2+(p[2]-vz)**2<35**2
   if not ok:continue
   aperture+=1;start=eye+d*((-100-eye[1])/d[1]);points=vtk.vtkPoints();ids=vtk.vtkIdList();loc.IntersectWithLine(start,target,points,ids)
   if points.GetNumberOfPoints()==0:visible+=1
  results.append(dict(viewport_z=vz,eye_z=ez,ring_samples=72,through_aperture=aperture,unobstructed=visible))
(P/'Viewport ray check.json').write_text(json.dumps({'target_face_z':141,'illustrative_observation_ring':{'radius':20,'z':125},'eye_y':-400,'results':results,'method':'72 rays to a geometric observation ring, triangle intersection against all gun solids, both aperture end planes; not a plasma-brightness prediction.'},indent=2))
print(results)
print([(q['name'],q['role'],q['bbox_mm']) for q in meta if q['group']=='gun' and ('jacket' in q['name'].lower() or 'coax' in q['name'].lower())])

