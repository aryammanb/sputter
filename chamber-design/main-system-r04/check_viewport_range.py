from pathlib import Path
P=Path(__file__).resolve().parent
src=(P/'check_viewport.py').read_text();exec(compile(src.split('results=[]')[0],str(P/'check_viewport.py'),'exec'))
results=[]
for gap in [75,100,150]:
 dz=gap-100
 for ez in [-20,0,20,40,60]:
  eye=np.array([0.,-400.,ez]);passed=clear=0
  for th in np.linspace(0,2*np.pi,72,endpoint=False):
   t=np.array([20*np.cos(th),20*np.sin(th),136.+dz]);direction=t-eye
   aperture=True
   for yy in [-146,-114]:
    v=eye+direction*((yy+400)/direction[1]);aperture &= v[0]**2+(v[2]-105)**2<35**2
   if not aperture:continue
   passed+=1;start=eye+direction*((-100+400)/direction[1]);points=vtk.vtkPoints();ids=vtk.vtkIdList();loc.IntersectWithLine(start-[0,0,dz],t-[0,0,dz],points,ids)
   if points.GetNumberOfPoints()==0:clear+=1
  results.append(dict(gap_mm=gap,eye_z_mm=ez,through_aperture=passed,clear_samples=clear,total_samples=72))
(P/'Viewport travel range check.json').write_text(json.dumps({'viewport_z_mm':105,'ring_radius_mm':20,'ring_below_target_mm':5,'eye_y_mm':-400,'results':results,'scope':'Geometric access only; assumes rigid axial gun movement, no plasma brightness or coating prediction.'},indent=2));print(results)
