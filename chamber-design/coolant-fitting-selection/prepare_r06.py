from pathlib import Path
import cadquery as cq,json,math
P=Path('chamber-design/coolant-fitting-r06');P.mkdir(exist_ok=True);(P/'STEP parts').mkdir(exist_ok=True)
B=Path('chamber-design/target-clamp-r05');meta=json.loads((B/'parts.json').read_text(encoding='utf-8'));ss=cq.importers.importStep(str(B/'Complete sputter system R05.step')).val().Solids();items=[];k=0
for q in meta:
 a=ss[k:k+q['solid_count']];k+=q['solid_count'];items.append(q|{'shape':a[0] if len(a)==1 else cq.Compound.makeCompound(a)})
V=cq.Vector
def cyl(r,y,h,x=0):return cq.Solid.makeCylinder(r,h,V(x,y,0),V(0,1,0))
def nat(s):return s.translate((0,0,-144.175)).rotate((0,0,0),(1,0,0),90)
def world(s):return s.rotate((0,0,0),(1,0,0),-90).translate((0,0,144.175))
closure=next(q for q in items if q['role']=='gun_closure');old=nat(closure['shape']);blank=old
for x in [-18,18]:blank=blank.fuse(cyl(3.975,-22.5,10,x),cyl(2.5,-12.5,3.5,x)).clean()
assert blank.isValid()
expected=blank
for x in [-18,18]:expected=expected.cut(cyl(1.5,-22.6,13.7,x),cyl(2.1,-22.6,5.1,x)).clean()
cq.exporters.export(blank,str(P/'Backplate port blank.step'));cq.exporters.export(expected,str(P/'Backplate R06 expected.step'));closure['shape']=world(expected);closure['name']='Gun copper backplate R06 M5 coolant ports';closure['note']='Two M5x0.8 gasket-sealed ports at X+/-18. Native SolidWorks features: D3 flow passage through; D4.2 tap drill5mm; M5x0.8 full thread4mm callout. OldD7.95 counterbores removed. Tapped thread represented by minor bore, not helical teeth.'
# Compact purchased fitting external dimensions; internal detail is representative.
for q in items:
 if q['role']=='gun_fittings':
  x=(q['bbox_mm'][0]+q['bbox_mm'][3])/2
  if 'collar' in q['note'].lower():s=cyl(4.5,-36.6,.8,x).cut(cyl(2,-36.7,1,x));q['name']='SMC KQG2S04-M5 release ring '+str(round(x))
  else:
   s=cyl(4.5,-35.8,13.3,x).fuse(cyl(2.5,-22.5,3,x)).cut(cyl(1,-36.7,17.3,x),cyl(2,-36.7,12.7,x)).clean();q['name']='SMC KQG2S04-M5 body '+str(round(x))
  q['shape']=world(s);q['note']='Purchased fitting envelope: OD9, overall17.1, above-seat14.1, M5x0.8, internal2mmhex. External dimensions fromSMC; hidden internal valve/seal details not manufacturer CAD. Assembly gasket compression atseat is represented, notqualified.'
 if q['role']=='gun_hoses':
  oldn=nat(q['shape']);x=18 if oldn.Center().x>0 else -18;sg=1 if x>0 else -1
  # Keep existing bend envelope to preserve surrounding clearances; extend straight insertion to new socket.
  # Old hose startsY-29.5, selected socket insertion end isY-24.0.
  s=oldn.fuse(cyl(2,-29.6,5.6,x).cut(cyl(1.25,-29.7,5.8,x))).clean();q['shape']=world(s);q['note']='4mmOD/2.5mmID coolant tube extended toY-24.0, giving12.6mm nominal insertion fromcolletY-36.6. Existing bend retained; supplier tubing bend-radius qualification remainspending.'
# Validate changed parts against gun solids, classifying nominal tap engagement.
changed=[q for q in items if q['role'] in ['gun_closure','gun_fittings','gun_hoses']];gun=[q for q in items if q['group']=='gun'];hits=[]
for a in changed:
 for b in gun:
  if a is b:continue
  boxa=a['shape'].BoundingBox();boxb=b['shape'].BoundingBox()
  if any([boxa.xmax<boxb.xmin,boxb.xmax<boxa.xmin,boxa.ymax<boxb.ymin,boxb.ymax<boxa.ymin,boxa.zmax<boxb.zmin,boxb.zmax<boxa.zmin]):continue
  v=a['shape'].intersect(b['shape']).Volume()
  if v>.001:hits.append({'a':a['name'],'b':b['name'],'roles':[a['role'],b['role']],'volume_mm3':v})
print('Changed-part overlaps',json.dumps(hits),flush=True)
# Native SolidWorks assemblies use each component shape in local gun coordinates or complete-system coordinates.
plan={'parts':[],'gun':[],'system':[],'backplate_expected_volume_mm3':expected.Volume(),'backplate_blank_volume_mm3':blank.Volume(),'interferences':hits}
for i,q in enumerate(items):
 # Omit known-invalid RV3 supplier reference only from native import; retained in fullSTEP asreference.
 if q['role']=='backing_pump' and not q['shape'].isValid():continue
 s=nat(q['shape']) if q['group']=='gun' else q['shape'];key=f'{i:03d}';stem=key+' '+''.join(c if c.isalnum() or c in ' -_' else '_' for c in q['name'])[:85];step=P/'STEP parts'/(stem+'.step');cq.exporters.export(s,str(step));plan['parts'].append({'name':stem,'step':str(step.resolve()),'role':q['role'],'note':q['note'],'color':q.get('color',[.6,.65,.7]),'volume_mm3':s.Volume(),'bodies':len(s.Solids())})
 plan['system'].append({'part':stem,'gun':q['group']=='gun'})
 if q['group']=='gun':plan['gun'].append({'part':stem})
ass=cq.Assembly(name='Sputter system R06 coolant fitting revision');ga=cq.Assembly(name='Magnetron R06 coolant fitting revision')
for i,q in enumerate(items):
 ass.add(q['shape'],name=f'P{i:03d}',color=cq.Color(*q.get('color',[.6,.65,.7])))
 if q['group']=='gun':ga.add(nat(q['shape']),name=f'P{i:03d}',color=cq.Color(*q.get('color',[.6,.65,.7])))
ass.save(str(P/'Complete sputter system R06.step'));ga.save(str(P/'Magnetron R06.step'));(P/'SolidWorks build plan.json').write_text(json.dumps(plan,indent=2),encoding='utf-8');(P/'R06 component register.json').write_text(json.dumps([{k:v for k,v in q.items() if k!='shape'} for q in items],indent=2),encoding='utf-8');print('Prepared',len(plan['parts']),'parts; gun',len(plan['gun']),flush=True)
