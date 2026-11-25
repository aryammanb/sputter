from pathlib import Path
import json,math
P=Path(__file__).resolve().parent;ROOT=P.parent.parent
src=(P.parent/'main-system-r04/check_viewport.py').read_text().split('results=[]')[0].replace("B=P.parent/'full-system-r03'","B=P")
exec(compile(src,str(P/'check_viewport_r05.py'),'exec'))
results=[]
for gap in [75,100,150]:
 dz=gap-100;eye=np.array([0.,-400.,20.]);passed=clear=0
 for th in np.linspace(0,2*np.pi,72,endpoint=False):
  t=np.array([20*np.cos(th),20*np.sin(th),136.+dz]);direction=t-eye;aperture=True
  for yy in [-146,-114]:
   v=eye+direction*((yy+400)/direction[1]);aperture &= v[0]**2+(v[2]-105)**2<35**2
  if not aperture:continue
  passed+=1;start=eye+direction*((-100+400)/direction[1]);points=vtk.vtkPoints();ids=vtk.vtkIdList();loc.IntersectWithLine(start-[0,0,dz],t-[0,0,dz],points,ids)
  if points.GetNumberOfPoints()==0:clear+=1
 results.append(dict(gap_mm=gap,ring_samples=72,through_window=passed,unobstructed=clear))
(P/'R05 viewport check.json').write_text(json.dumps({'eye_mm':[0,-400,20],'window_centre_z_mm':105,'clear_aperture_mm':70,'observation_ring_radius_mm':20,'ring_below_target_mm':5,'results':results,'scope':'Geometric access only. No plasma brightness or coating prediction.'},indent=2),encoding='utf-8');assert all(x['unobstructed']>0 for x in results);print(results)
