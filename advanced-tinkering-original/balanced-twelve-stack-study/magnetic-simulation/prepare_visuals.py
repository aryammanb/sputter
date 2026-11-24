from pathlib import Path
import json,math
import numpy as np
from scipy.interpolate import RegularGridInterpolator
from analyze_field import Field,ME,E
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Circle,Rectangle
P=Path(__file__).resolve().parent
f=Field('fine_nominal');metrics=json.loads((P/'fine_nominal_metrics.json').read_text());s=np.load(P/'fine_nominal_samples.npz')
gridaxis=np.arange(-55,55.01,1.);gz=np.arange(2,65.01,1.)
xyz=np.stack(np.meshgrid(gridaxis,gridaxis,gz,indexing='ij'),axis=-1)
bgrid=f(xyz.reshape(-1,3)).reshape(len(gridaxis),len(gridaxis),len(gz),3).astype(np.float32)
np.savez_compressed(P/'visual_field_grid.npz',x=gridaxis,y=gridaxis,z=gz,B=bgrid)
interp=RegularGridInterpolator((gridaxis,gridaxis,gz),bgrid,bounds_error=False,fill_value=np.nan)
def trace(start):
 p=np.array(start,dtype=float);path=[p.copy()]
 for _ in range(1500):
  b=interp(p[None])[0];n=np.linalg.norm(b)
  if not np.isfinite(n) or n<1e-6:break
  k1=b/n;mid=p+.175*k1;b2=interp(mid[None])[0];n2=np.linalg.norm(b2)
  if not np.isfinite(n2) or n2<1e-6:break
  p=p+.35*b2/n2
  if p[2]<2.25 or p[2]>64 or abs(p[0])>54 or abs(p[1])>54:break
  path.append(p.copy())
 return np.array(path)
lines=[]
for theta in np.arange(0,360,30):
 for r in [4,6,9,13,17]:
  t=np.deg2rad(theta);path=trace([r*np.cos(t),r*np.sin(t),2.3])
  if len(path)>5:lines.append({'points':path.tolist(),'B_mT':(np.linalg.norm(interp(path),axis=1)*1000).tolist()})
(P/'fieldlines.json').write_text(json.dumps(lines,separators=(',',':')))
print('Grid and',len(lines),'fieldlines prepared',flush=True)
# Surface maps at several actual heights; these are magnetic fields, not plasma-density maps.
xy=np.linspace(-28,28,225);xx,yy=np.meshgrid(xy,xy);heights=np.array([.25,.5,1,2,3,5,8,10,15,20])
surface=[]
for h in heights:
 b=f(np.c_[xx.ravel(),yy.ravel(),np.full(xx.size,2+h)]).reshape(*xx.shape,3);surface.append(b)
sx=np.linspace(-42,42,281);sz=np.linspace(2.25,42,161);xxs,zzs=np.meshgrid(sx,sz)
section=f(np.c_[xxs.ravel(),np.zeros(xxs.size),zzs.ravel()]).reshape(*xxs.shape,3)
np.savez_compressed(P/'plot_data.npz',xy=xy,surface=np.array(surface),heights=heights,section_x=sx,section_z=sz,section_B=section)
# Target-thickness / pole-to-front-face sensitivity. The target is nonmagnetic, so its geometry does not change the magnetic PDE.
theta=np.linspace(0,2*np.pi,180,endpoint=False);r=np.linspace(2,25.4,400);sensitivity=[]
for thickness in [1,2,3,5]:
 p=np.stack(np.broadcast_arrays(r[None,:]*np.cos(theta[:,None]),r[None,:]*np.sin(theta[:,None]),thickness+.25),axis=-1);b=f(p.reshape(-1,3)).reshape(180,400,3)
 fields=[];radii=[]
 for i in range(180):
  idx=np.flatnonzero(b[i,:-1,2]*b[i,1:,2]<0)
  if len(idx):
   j=idx[0];root=np.interp(0,[b[i,j+1,2],b[i,j,2]],[r[j+1],r[j]]);radii.append(root);fields.append(np.interp(root,r,np.linalg.norm(b[i,:,:2],axis=1))*1000)
 sensitivity.append({'target_thickness_mm':thickness,'pole_tip_to_front_face_mm':thickness+2.5,'track_mean_Bparallel_mT':float(np.mean(fields)),'track_min_Bparallel_mT':float(np.min(fields)),'track_radius_mean_mm':float(np.mean(radii))})
(P/'target_thickness_sensitivity.json').write_text(json.dumps(sensitivity,indent=2))
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':13,'figure.facecolor':'#101b2c','axes.facecolor':'#14243a','axes.edgecolor':'#7890a8','text.color':'#edf4fc','axes.labelcolor':'#d9e7f6','xtick.color':'#bed0e4','ytick.color':'#bed0e4','grid.color':'#33485e','savefig.facecolor':'#101b2c'})
def save(fig,name):fig.savefig(P/name,dpi=150,bbox_inches='tight');plt.close(fig)
fig,ax=plt.subplots(figsize=(8,7));b=surface[0];bp=np.linalg.norm(b[:,:,:2],axis=2)*1000;masked=np.ma.array(bp,mask=xx**2+yy**2>25.4**2);im=ax.pcolormesh(xy,xy,masked,cmap='viridis',vmin=0,vmax=200,shading='auto');ax.contour(xy,xy,b[:,:,2],levels=[0],colors=['#ffb968'],linewidths=2);ax.add_patch(Circle((0,0),25.4,fill=False,edgecolor='#e7eef6',lw=1.5));ax.set(aspect='equal',xlabel='x (mm)',ylabel='y (mm)',title='Parallel magnetic field, 0.25 mm above target');fig.colorbar(im,ax=ax,label='B parallel (mT)');save(fig,'Target field map.png')
fig,ax=plt.subplots(figsize=(11,5));bp=np.abs(section[:,:,0])*1000;im=ax.pcolormesh(sx,sz-2,bp,cmap='viridis',vmin=0,vmax=100,shading='auto');ax.streamplot(sx,sz-2,section[:,:,0],section[:,:,2],density=1.15,color='#ddeeff',linewidth=.7,arrowsize=.75);ax.plot([-25.4,25.4],[0,0],lw=5,color='#a6b6c5');ax.set(xlabel='x (mm), cut through outer pole centers',ylabel='Height above target (mm)',ylim=(0,40),title='Field geometry above target: FEM section at y = 0');fig.colorbar(im,ax=ax,label='|Bx| (mT)');save(fig,'Field section.png')
fig,ax=plt.subplots(figsize=(10,4));angle=np.rad2deg(s['theta']);bt=s['track_B']*1000;ax.plot(angle,bt,color='#7ddfc9',lw=2);ax.axhspan(20,50,color='#8faac7',alpha=.18,label='Common 20-50 mT reference; not a pass/fail limit');ax.set(xlim=(0,360),ylim=(0,110),xlabel='Angle around target (degrees)',ylabel='B parallel at Bnormal=0 (mT)',title='Circumferential variation on candidate racetrack');ax.grid(alpha=.4);ax.legend(loc='lower right');save(fig,'Racetrack uniformity.png')
fig,ax=plt.subplots(figsize=(9,5));hm=metrics['height_scan'];ax.plot(hm['above_target_mm'],hm['Bparallel_mean_mT'],'o-',color='#7ddfc9',label='Mean at r =20 mm');ax.plot(hm['above_target_mm'],hm['Bparallel_min_mT'],'--',color='#ffbe7c',label='Weakest angle');ax.axhspan(20,50,color='#8faac7',alpha=.18);ax.set(xlabel='Height above target (mm)',ylabel='B parallel (mT)',ylim=(0,105),title='Field decays with height; strongest confinement is near target');ax.grid(alpha=.4);ax.legend();save(fig,'Field versus height.png')
print('Scientific figures and thickness sensitivity prepared',flush=True)
