from pathlib import Path
import json,sys,math
import numpy as np
from scipy.interpolate import RegularGridInterpolator
from scipy.optimize import brentq
import vtk
from vtk.util.numpy_support import numpy_to_vtk,numpy_to_vtkIdTypeArray,vtk_to_numpy
P=Path(__file__).resolve().parent;MU0=4*np.pi*1e-7;ME=9.1093837139e-31;E=1.602176634e-19
class Field:
 def __init__(self,name):
  self.name=name;d=np.load(P/(name+'_field.npz'));self.d=d
  grid=vtk.vtkUnstructuredGrid();pts=vtk.vtkPoints();pts.SetData(numpy_to_vtk(d['points'],deep=True));grid.SetPoints(pts)
  cells=vtk.vtkCellArray();cells.SetData(numpy_to_vtkIdTypeArray(np.arange(0,len(d['tets'])*4+1,4,dtype=np.int64),deep=True),numpy_to_vtkIdTypeArray(d['tets'].ravel().astype(np.int64),deep=True));grid.SetCells(vtk.VTK_TETRA,cells)
  a=numpy_to_vtk(d['air_nodal_B'],deep=True);a.SetName('B_T');grid.GetPointData().AddArray(a)
  a=numpy_to_vtk(d['element_B'],deep=True);a.SetName('B_element_T');grid.GetCellData().AddArray(a);self.grid=grid
 def __call__(self,coords,element=False):
  coords=np.asarray(coords);single=coords.ndim==1;coords=coords.reshape(-1,3)
  p=vtk.vtkPolyData();pts=vtk.vtkPoints();pts.SetData(numpy_to_vtk(coords,deep=True));p.SetPoints(pts)
  probe=vtk.vtkProbeFilter();probe.SetSourceData(self.grid);probe.SetInputData(p);probe.SetComputeTolerance(False);probe.SetTolerance(1e-4);probe.SetCellLocatorPrototype(vtk.vtkStaticCellLocator());probe.Update();out=probe.GetOutput();valid=vtk_to_numpy(out.GetPointData().GetArray('vtkValidPointMask'));assert valid.all(),coords[~valid.astype(bool)][:3]
  values=vtk_to_numpy(out.GetPointData().GetArray('B_element_T' if element else 'B_T')).copy();return values[0] if single else values

def metrics(name):
 f=Field(name);theta=np.linspace(0,2*np.pi,360,endpoint=False);r=np.linspace(2,25.4,469);z=2.25
 points=np.stack(np.broadcast_arrays(r[None,:]*np.cos(theta[:,None]),r[None,:]*np.sin(theta[:,None]),z),axis=-1)
 b=f(points.reshape(-1,3)).reshape(len(theta),len(r),3);parallel=np.linalg.norm(b[:,:,:2],axis=2)
 roots=[];btrack=[];peak=[]
 for i in range(len(theta)):
  j=np.flatnonzero(b[i,:-1,2]*b[i,1:,2]<0)
  if len(j):
   j=j[0];root=np.interp(0,[b[i,j+1,2],b[i,j,2]],[r[j+1],r[j]])
   roots.append(root);btrack.append(float(np.interp(root,r,parallel[i])))
  peak.append(float(parallel[i].max()))
 roots=np.array(roots);btrack=np.array(btrack);assert len(roots)==360,('missing annular Bz zero',len(roots))
 trackradius=float(roots.mean());height=np.array([.25,1,2,3,5,8,10,15,20,30,40])
 hp=np.stack(np.broadcast_arrays(trackradius*np.cos(theta[:,None]),trackradius*np.sin(theta[:,None]),2+height[None,:]),axis=-1)
 hb=f(hp.reshape(-1,3)).reshape(360,len(height),3);hparallel=np.linalg.norm(hb[:,:,:2],axis=2)
 axisz=np.linspace(2.1,70,680);axis=f(np.c_[axisz*0,axisz*0,axisz]);zc=np.flatnonzero(axis[:-1,2]*axis[1:,2]<0)
 nulls=[float(np.interp(0,[axis[j+1,2],axis[j,2]],[axisz[j+1],axisz[j]]))-2 for j in zc]
 # Signed normal flux through target disk, and a larger diagnostic disk. Not a global balance certificate.
 flux={}
 for radius in [25.4,40]:
  nr=200;nt=360;rr=(np.arange(nr)+.5)*radius/nr;tt=(np.arange(nt)+.5)*2*np.pi/nt
  p=np.stack(np.broadcast_arrays(rr[None,:]*np.cos(tt[:,None]),rr[None,:]*np.sin(tt[:,None]),z),axis=-1)
  bz=f(p.reshape(-1,3))[:,2].reshape(nt,nr);area=rr[None,:]*(radius/nr)*(2*np.pi/nt)*1e-6
  pos=float(np.sum(np.maximum(bz,0)*area));neg=float(np.sum(-np.minimum(bz,0)*area));flux[str(radius)]={'positive_Wb':pos,'negative_Wb':neg,'negative_to_positive':neg/pos}
 steel=f.d['materials']==2;mag=np.linalg.norm(f.d['element_B'][steel],axis=1);vol=f.d['volumes'][steel]
 result={'name':name,'sampling_height_above_target_mm':.25,'racetrack_Bz_zero':{'angles_with_crossing':len(roots),'radius_mean_mm':trackradius,'radius_min_mm':float(roots.min()),'radius_max_mm':float(roots.max()),'Bparallel_mean_mT':float(btrack.mean()*1000),'Bparallel_min_mT':float(btrack.min()*1000),'Bparallel_max_mT':float(btrack.max()*1000),'peak_to_peak_over_mean_percent':float(100*np.ptp(btrack)/btrack.mean()),'target_edge_margin_min_mm':float(25.4-roots.max()),'fraction_above_20mT':float(np.mean(btrack>=.020))},'radial_peak_Bparallel_mean_mT':float(np.mean(peak)*1000),'height_scan':{'above_target_mm':height.tolist(),'Bparallel_mean_mT':(hparallel.mean(axis=0)*1000).tolist(),'Bparallel_min_mT':(hparallel.min(axis=0)*1000).tolist()},'axis_Bz_sign_change_height_mm':nulls,'flux_at_z2p25':flux,'yoke':{'B_max_T':float(mag.max()),'B_volume_weighted_mean_T':float(np.sum(mag*vol)/sum(vol)),'B_p99_T':float(np.quantile(mag,.99))},'electron_gyroradius_mm_at_weakest_track_field':{str(ev):float(np.sqrt(2*ME*ev*E)/(E*btrack.min())*1000) for ev in [5,10,20,100]},'electron_cyclotron_frequency_GHz_min':float(E*btrack.min()/ME/(2*np.pi)*1e-9)}
 result['balance_classification']='Not certified. Surface racetrack, field strength and near-target magnetization assessed; no universal balance coefficient or pole-face flux claim is made. Axis scan is domain limited.'
 np.savez_compressed(P/(name+'_samples.npz'),theta=theta,r=r,b=b,track_r=roots,track_B=btrack,height=height,height_B=hb,axis_z=axisz,axis_B=axis)
 (P/(name+'_metrics.json')).write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2),flush=True)
 return result

def analytic_check(name):
 import magpylib as magpy
 f=Field(name);sources=[magpy.magnet.Cylinder(position=(0,0,-.0125),dimension=(.020,.020),polarization=(0,0,1.3))]
 for i in range(12):
  t=i*np.pi/6;sources.append(magpy.magnet.Cylinder(position=(.029*np.cos(t),.029*np.sin(t),-.0125),dimension=(.006,.020),polarization=(0,0,-1.3)))
 exact=magpy.Collection(sources);rr=np.linspace(10,24,50);tt=np.linspace(0,2*np.pi,48,endpoint=False);zz=np.array([2.25,4,7,12])
 r,t,z=np.meshgrid(rr,tt,zz,indexing='ij');p=np.c_[r.ravel()*np.cos(t.ravel()),r.ravel()*np.sin(t.ravel()),z.ravel()]
 numerical=f(p);reference=exact.getB(p*.001);err=np.linalg.norm(numerical-reference,axis=1);den=np.linalg.norm(reference,axis=1)
 report={'case':name,'comparison':'same13 cylindrical magnets in free space, mu_r=1 everywhere, no steel response','sample_points':len(p),'vector_relative_L2_error':float(np.linalg.norm(numerical-reference)/np.linalg.norm(reference)),'pointwise_relative_error_median':float(np.median(err/den)),'pointwise_relative_error_p95':float(np.quantile(err/den,.95)),'absolute_vector_error_p95_mT':float(np.quantile(err,.95)*1000),'reference_solver':'Magpylib6.3 analytical finite cylinder fields in SI units'}
 (P/(name+'_analytic_validation.json')).write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2),flush=True)

if __name__=='__main__':
 if sys.argv[1]=='validate':analytic_check(sys.argv[2])
 else:metrics(sys.argv[1])
