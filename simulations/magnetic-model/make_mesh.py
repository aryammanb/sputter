from pathlib import Path
import sys,json,time
import numpy as np
import gmsh
P=Path(__file__).resolve().parent;P.mkdir(exist_ok=True)
name=sys.argv[1] if len(sys.argv)>1 else 'coarse'
near=float(sys.argv[2]) if len(sys.argv)>2 else 1.8
L=float(sys.argv[3]) if len(sys.argv)>3 else 80
start=time.perf_counter();gmsh.initialize();gmsh.option.setNumber('General.Terminal',1);gmsh.option.setNumber('General.NumThreads',2)
gmsh.model.add('Twelve stack candidate / magnetic circuit');o=gmsh.model.occ
air=o.addBox(-L,-L,-L,2*L,2*L,2*L)
# Import the actual proposed yoke; rotate CAD Y axis onto simulation Z.
yoke=o.importShapes(str(P/'yoke.step'))
assert len(yoke)==1 and yoke[0][0]==3
o.rotate(yoke,0,0,0,1,0,0,np.pi/2)
center=o.addCylinder(0,0,-22.5,0,0,20,10)
outer=[]
for i in range(12):
 a=i*np.pi/6;outer.append(o.addCylinder(29*np.cos(a),29*np.sin(a),-22.5,0,0,20,3))
# Nonmagnetic target is an explicit region to resolve its sputtering surface.
target=o.addCylinder(0,0,0,0,0,2,25.4)
tools=yoke+[(3,center)]+[(3,t) for t in outer]+[(3,target)]
fragments,mapping=o.fragment([(3,air)],tools);o.synchronize()
groups={1:[],2:[],3:[],4:[]}
# 1 air/copper/water/nonmagnetic structure, 2 steel, 3 center N, 4 outer S.
for v in mapping[1]:
 if v[0]==3:groups[2].append(v[1])
for v in mapping[2]:
 if v[0]==3:groups[3].append(v[1])
for group in mapping[3:15]:
 for v in group:
  if v[0]==3:groups[4].append(v[1])
claimed=set(groups[2]+groups[3]+groups[4])
groups[1]=[v[1] for v in fragments if v[0]==3 and v[1] not in claimed]
for tag,entities in groups.items():gmsh.model.addPhysicalGroup(3,entities,tag)
surfaces=list({t for d,t in gmsh.model.getBoundary([(3,t) for tag in [2,3,4] for t in groups[tag]],oriented=False) if d==2})
f=gmsh.model.mesh.field
dist=f.add('Distance');f.setNumbers(dist,'SurfacesList',surfaces);f.setNumber(dist,'Sampling',60)
threshold=f.add('Threshold');f.setNumber(threshold,'InField',dist);f.setNumber(threshold,'SizeMin',near);f.setNumber(threshold,'SizeMax',12);f.setNumber(threshold,'DistMin',4);f.setNumber(threshold,'DistMax',32)
box=f.add('Box');f.setNumber(box,'VIn',near);f.setNumber(box,'VOut',12)
for key,val in {'XMin':-34,'XMax':34,'YMin':-34,'YMax':34,'ZMin':0,'ZMax':18,'Thickness':8}.items():f.setNumber(box,key,val)
minimum=f.add('Min');f.setNumbers(minimum,'FieldsList',[threshold,box]);f.setAsBackgroundMesh(minimum)
gmsh.option.setNumber('Mesh.MeshSizeExtendFromBoundary',0);gmsh.option.setNumber('Mesh.MeshSizeFromPoints',0);gmsh.option.setNumber('Mesh.MeshSizeFromCurvature',0)
gmsh.option.setNumber('Mesh.Algorithm3D',1);gmsh.option.setNumber('Mesh.Optimize',1)
gmsh.model.mesh.generate(3)
node_tags,coords,_=gmsh.model.mesh.getNodes();order=np.argsort(node_tags);node_tags=node_tags[order];points=coords.reshape(-1,3)[order]
tets=[];materials=[]
for mat,entities in groups.items():
 for tag in entities:
  types,elemids,nodes=gmsh.model.mesh.getElements(3,tag)
  for typ,ids,n in zip(types,elemids,nodes):
   assert typ==4,typ
   tets.append(np.searchsorted(node_tags,np.asarray(n).reshape(-1,4)));materials.extend([mat]*len(ids))
tets=np.vstack(tets);materials=np.array(materials,dtype=np.int8)
np.savez_compressed(P/(name+'_mesh.npz'),points=points,tets=tets,materials=materials,L=L,near=near)
gmsh.write(str(P/(name+'.msh')));gmsh.finalize()
report={'name':name,'near_size_mm':near,'outer_boundary_halfwidth_mm':L,'vertices':len(points),'tetrahedra':len(tets),'material_tetrahedra':{str(k):int(sum(materials==k)) for k in groups},'seconds':time.perf_counter()-start,'geometry':'Exact proposed yoke STEP;13 contiguous magnet cylinders representing26 stacked discs; nonmagnetic target D50.8x2. CAD Y -> simulation Z. Nonmagnetic copper/water/insulation have mu_r=1 and are magnetostatically part of surrounding domain.'}
(P/(name+'_mesh.json')).write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2),flush=True)
