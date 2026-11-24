import os
os.environ['OPENBLAS_NUM_THREADS']='2'
os.environ['OMP_NUM_THREADS']='2'
from pathlib import Path
import sys,json,time
import numpy as np
from scipy.sparse.linalg import cg
from skfem import MeshTet,Basis,ElementTetP1,BilinearForm,LinearForm,asm
from skfem.helpers import dot,grad
import pyamg
P=Path(__file__).resolve().parent
MU0=4*np.pi*1e-7
# Reference AISI1010 B(H), CERN DIRAC2012-02 via QuickField; actual yoke steel unknown.
BH=np.array([[0,0],[.576,166],[.680,199],[.792,240],[.895,289],[.992,347],[1.082,418],[1.164,502],[1.237,604],[1.302,726],[1.359,872],[1.407,1049],[1.449,1261],[1.517,1823],[1.545,2192],[1.595,3167],[1.646,4579],[1.702,6619],[1.768,9568],[1.805,11499],[1.843,13831],[1.883,16624],[1.924,19990],[1.964,24032],[2.002,28893],[2.038,34736],[2.071,41762],[2.100,50209],[2.125,60375],[2.146,72575],[2.165,87257],[2.187,104907],[2.214,126122],[2.246,151595]])
def steel_mu(b,scale):
 h=np.interp(b,BH[:,0],BH[:,1]);high=b>BH[-1,0];h[high]=BH[-1,1]+(b[high]-BH[-1,0])/MU0
 return np.clip(np.divide(b,MU0*h*scale,out=np.full_like(b,.576/(MU0*166*scale)),where=h>0),1,10000)
@BilinearForm
def stiffness(u,v,w):return w.mu*dot(grad(u),grad(v))
@LinearForm
def source(v,w):return w.br*v.grad[2]
@BilinearForm
def jacobian(u,v,w):
 return sum(w.tensor[i,j]*u.grad[i]*v.grad[j] for i in range(3) for j in range(3))
def constitutive(g,mat,scale):
 mu=np.ones(len(mat));mu[(mat==3)|(mat==4)]=1.05
 hs=np.linalg.norm(g[:,mat==2],axis=0)/MU0
 htable=BH[:,1]*scale
 bs=np.interp(hs,htable,BH[:,0]);high=hs>htable[-1];bs[high]=BH[-1,0]+MU0*(hs[high]-htable[-1])
 slopes=np.diff(BH[:,0])/np.diff(htable)
 j=np.clip(np.searchsorted(htable,hs,side='right')-1,0,len(slopes)-1)
 diff=slopes[j]/MU0;diff[high]=1
 mus=np.divide(bs,MU0*hs,out=np.full_like(hs,slopes[0]/MU0),where=hs>1e-12)
 mu[mat==2]=mus
 return mu,diff

def solve(meshname,case='nominal'):
 start=time.perf_counter();d=np.load(P/(meshname+'_mesh.npz'));points=d['points'];tets=d['tets'];mat=d['materials']
 mesh=MeshTet(points.T,tets.T);basis=Basis(mesh,ElementTetP1(),intorder=1);vol=basis.dx.sum(axis=1)
 inside=np.setdiff1d(np.arange(basis.N),mesh.boundary_nodes());Br=np.zeros(len(tets));Br[mat==3]=1.30;Br[mat==4]=-1.30
 mu=np.ones(len(tets));mu[(mat==3)|(mat==4)]=1.05
 if case=='analytic':mu[:]=1
 elif case.startswith('linear'):mu[mat==2]=float(case[6:])
 else:mu[mat==2]=1500
 rhs=asm(source,basis,br=Br[:,None]);u=np.zeros(basis.N);history=[];oldair=None;converged=False
 nonlinear=case not in ['analytic'] and not case.startswith('linear')
 scale={'nominal':1.,'steel-soft':.5,'steel-hard':2.}.get(case,1.)
 for it in range(18 if nonlinear else 1):
  g=basis.interpolate(u).grad.mean(axis=2)
  if nonlinear:mu,differential=constitutive(g,mat,scale)
  A=asm(stiffness,basis,mu=mu[:,None]);res=rhs[inside]-(A@u)[inside];norm=float(np.linalg.norm(res)/np.linalg.norm(rhs[inside]))
  if norm<2e-7:converged=True;break
  if nonlinear:
   tensor=np.zeros((3,3,len(mat),1))
   for c in range(3):tensor[c,c,:,0]=mu
   s=mat==2;n=g[:,s];n=np.divide(n,np.linalg.norm(n,axis=0)[None,:],out=np.zeros_like(n),where=np.linalg.norm(n,axis=0)[None,:]>1e-15)
   for c in range(3):
    for j in range(3):tensor[c,j,s,0]+=(differential-mu[s])*n[c]*n[j]
   J=asm(jacobian,basis,tensor=tensor)
  else:J=A
  Ji=J[inside][:,inside].tocsr();ml=pyamg.smoothed_aggregation_solver(Ji,symmetry='symmetric',max_coarse=100)
  residual=[];du,info=cg(Ji,res,M=ml.aspreconditioner(),rtol=2e-9,atol=0,maxiter=500,callback=lambda x:residual.append(0));assert info==0,info
  alpha=1.
  for ls in range(12):
   trial=u.copy();trial[inside]+=alpha*du
   if not nonlinear:trialnorm=0.;break
   gt=basis.interpolate(trial).grad.mean(axis=2);mut,_=constitutive(gt,mat,scale);At=asm(stiffness,basis,mu=mut[:,None]);trialnorm=float(np.linalg.norm(rhs[inside]-(At@trial)[inside])/np.linalg.norm(rhs[inside]))
   if trialnorm<norm:break
   alpha*=.5
  assert trialnorm<norm,(norm,trialnorm)
  u=trial;rec={'iteration':it+1,'linear_iterations':len(residual),'linear_residual':float(np.linalg.norm(Ji@du-res)/np.linalg.norm(res)),'nonlinear_residual_before':norm,'nonlinear_residual_after':trialnorm,'line_search_alpha':alpha}
  history.append(rec);print(meshname,case,json.dumps(rec),flush=True)
  if not nonlinear or trialnorm<2e-7:converged=True;break
 g=basis.interpolate(u).grad.mean(axis=2)
 if nonlinear:mu,_=constitutive(g,mat,scale)
 B=-g*mu[None,:];B[2]+=Br;bmag=np.linalg.norm(B[:,mat==2],axis=0)
 assert converged,('nonlinear not converged',history[-1])
 # Air-side volume projection of the element field to mesh nodes, for smooth sampling above target.
 air=mat==1;weights=np.zeros(basis.N);nodal=np.zeros((basis.N,3))
 for j in range(4):
  np.add.at(weights,tets[air,j],vol[air])
  for c in range(3):np.add.at(nodal[:,c],tets[air,j],vol[air]*B[c,air])
 nodal=np.divide(nodal,weights[:,None],out=np.zeros_like(nodal),where=weights[:,None]>0)
 filename=meshname+'_'+case
 np.savez_compressed(P/(filename+'_field.npz'),points=points,tets=tets,materials=mat,potential=u,element_B=B.T,air_nodal_B=nodal,mu=mu,volumes=vol)
 report={'mesh':meshname,'case':case,'vertices':basis.N,'tetrahedra':len(tets),'converged':converged,'history':history,'seconds':time.perf_counter()-start,'material_volumes_mm3':{str(i):float(vol[mat==i].sum()) for i in [1,2,3,4]},'assumptions':{'magnet_Br_T':1.30,'magnet_recoil_mu_r':1.05 if case!='analytic' else 1.,'temperature_C':20,'target':'D50.8x2 nonmagnetic, mu_r=1','steel':'CERN reference AISI1010 curve; not specified actual yoke material','steel_H_scale':scale,'outer_boundary':'scalar potential zero at air-box boundary','potential_units':'T mm; u=mu0*phi','equation':'Integral(mu_r grad u dot grad v)=Integral(Br dot grad v)','coordinate_transform':'simulation(x,y,z)=CAD(x,-z,y)'},'steel_B_volume_percent_above_1p5T':float(100*vol[(mat==2)&(np.linalg.norm(B,axis=0)>1.5)].sum()/vol[mat==2].sum())}
 (P/(filename+'_solve.json')).write_text(json.dumps(report,indent=2,default=lambda x:x.item()));print('SAVED',filename,flush=True)
if __name__=='__main__':solve(sys.argv[1],sys.argv[2] if len(sys.argv)>2 else 'nominal')
