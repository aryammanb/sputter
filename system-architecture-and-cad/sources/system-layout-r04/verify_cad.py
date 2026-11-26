from pathlib import Path
import json,csv,shutil,zipfile
import cadquery as cq
P=Path(__file__).resolve().parent;m=json.loads((P/'parts.json').read_text());d=json.loads((P/'System dimension report.json').read_text());checks={}
for title in ['Complete sputter system R04','Complete sputter system R04 - loading']:
 solids=cq.importers.importStep(str(P/(title+'.step'))).val().Solids();assert len(solids)==d['solids'];bad=[i for i,s in enumerate(solids) if not s.isValid()];assert len(bad)==1
 groups=[];idx=0
 for q in m:groups.append(solids[idx:idx+q['solid_count']]);idx+=q['solid_count']
 invalid_names=[q['name'] for q,ss in zip(m,groups) if any(not s.isValid() for s in ss)];assert all('RV3' in s for s in invalid_names)
 checks[title]={'solids':len(solids),'valid':len(solids)-1,'known_invalid_supplier_reference':invalid_names}
 if title=='Complete sputter system R04':
  maps={q['role']:ss[0] for q,ss in zip(m,groups) if q['role'] in ['gas_insert','push_body','push_collet','glass','door_plate']}
  insert=maps['gas_insert'];b=insert.BoundingBox();assert abs(b.xlen-6)<.0001 and abs(b.zlen-6)<.0001
  overlaps={k:insert.intersect(maps[k]).Volume() for k in ['push_body','push_collet']};assert max(overlaps.values())<1e-5
  checks['6mm_tube']={'OD_mm':b.xlen,'ID_mm':4,'end_y_mm':b.ymin,'socket_mouth_y_mm':360.196,'engagement_mm':360.196-b.ymin,'insertion_scope':'16mm is provisional; supplier depth pending','fitting_overlap_mm3':overlaps}
  g=maps['glass'].BoundingBox();assert abs((g.zmin+g.zmax)/2-105)<.001
  checks['viewport']={'centre_z_mm':105,'clear_diameter_mm':70,'glass_disc_centre_verified':True,'ray_check_file':'Near-face ray check.json','scope':'Nominal gap100 only; geometric ring, not predicted plasma luminosity.'}
  out=P/'Separate assemblies';out.mkdir(exist_ok=True)
  for name,predicate in [('External utilities',lambda q:q['group']=='utilities'),('Revised front door',lambda q:q['group']=='door')]:
   a=cq.Assembly(name=name)
   for n,(q,ss) in enumerate(zip(m,groups)):
    if predicate(q):a.add(cq.Compound.makeCompound(ss),name=str(n)+'_'+q['name'],color=cq.Color(*q['color']))
   a.save(str(out/(name+'.step')))
 print('Checked',title,checks[title],flush=True)
(P/'CAD verification.json').write_text(json.dumps(checks,indent=2))
with (P/'Dimension schedule.csv').open('w',newline='',encoding='utf-8-sig') as f:
 w=csv.writer(f);w.writerow(['Dimension','Nominal value','Units / scope'])
 for k,v in d['dimensions_mm'].items():
  if k!='hose_path_samples':w.writerow([k,json.dumps(v),'mm unless specified; reference/provisional status in parts list'])
S=P/'Separate assemblies';assert (S/'Latest twelve-stack gun.step').is_file()  # Retained R04 snapshot input.
for name in ['Refined compression fitting - assembled.step','Refined compression fitting - exploded.step']:shutil.copy2(P.parents[2]/'archive/chamber-design/compression-fitting-r02'/name,S/name)
for name in ['Bent shutter.step','Top plate.step','Substrate stage.step']:shutil.copy2(P.parents[2]/'archive/chamber-design/complete-chamber-r01'/'Separate parts'/name,S/name)
shutil.copy2(P.parents[2]/'archive/chamber-design/complete-chamber-r01'/'Dimension and clearance report.json',P/'Inherited internal clearance checks.json')
shutil.copy2(P.parents[2]/'archive/chamber-design/full-system-r03'/'Purchased component references.csv',P/'Purchased component references.csv')
print('CAD verification and separate assemblies complete',flush=True)
