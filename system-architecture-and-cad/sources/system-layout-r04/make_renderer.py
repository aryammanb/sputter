from pathlib import Path
P=Path(__file__).resolve().parent;B=P.parents[2]/'archive/chamber-design/full-system-r03';s=(B/'render_system.py').read_text();s=s.replace("if 'preview' in sys.argv:","if 'preview' in sys.argv:")
# Reuse the original camera and dimension code for established system views.
s=s.replace("for q in records:\n  ac=q", "for q in records:\n  ac=q")
needle="  ac.SetUserTransform(tr);ac.SetVisibility(show);ac.GetProperty().SetOpacity(opacity)"
custom='''  ac.GetMapper().RemoveAllClippingPlanes()
  if view in ['gun_explode','gun_cooling','magnets','gun_electrical']:
   show=group=='gun'; opacity=1
   if role.endswith(('bolts','bolt','cups')):show=False
   if view=='gun_explode':
    ex=smooth(min(1,u*3))
    if role=='gun_darkcap':tr.Translate(110*ex,0,-20*ex)
    elif role=='gun_shieldtube':tr.Translate(150*ex,0,0)
    elif role in ['gun_target','gun_clamp']:tr.Translate(0,0,(-55 if role=='gun_target' else -32)*ex)
    elif role in ['gun_yoke','gun_closure','gun_spacer','gun_isolator','gun_base']:tr.Translate(0,0,{'gun_yoke':32,'gun_closure':55,'gun_spacer':80,'gun_isolator':105,'gun_base':130}[role]*ex)
    elif role in ['gun_centermag','gun_outermag']:tr.Translate(0,0,18*ex)
    elif role in ['gun_kftube','gun_hoses','gun_coax','gun_rfground','gun_rfhot']:tr.Translate(-140*ex,0,50*ex)
   if view=='gun_cooling':
    show=role in ['gun_target','gun_clamp','gun_cooler','gun_closure','gun_waterseal','gun_fittings','gun_centermag','gun_outermag']
    pl=vtk.vtkPlane();pl.SetOrigin(0,0,0);pl.SetNormal(1,0,0);ac.GetMapper().AddClippingPlane(pl)
   if view=='magnets':
    show=role in ['gun_centermag','gun_outermag','gun_yoke','gun_cooler','gun_target']
    if role in ['gun_cooler','gun_target']:opacity=.12
    if role=='gun_yoke':opacity=.35
   if view=='gun_electrical':
    if role in ['gun_shieldtube','gun_kftube','gun_base']:opacity=.13
    if role in ['gun_darkcap']:show=False
  if view in ['gas_supply','tube_insert']:
   show=role in mfc_roles|{'gas_insert','gas_line','cylinder','regulator','regulator_dial'}
   if view=='tube_insert':
    show=role in mfc_roles|{'gas_insert'}
    if role=='gas_insert':tr.Translate(0,24*(1-smooth(u*2)),0)
    if role in ['push_body','push_collet']:opacity=.3
  if view in ['cooling1','cooling2','power_view']:
   show=True
   if group!='utilities' and group not in ['gun','fitting']:opacity=.2
   wanted={'cooling1':{'chiller1','gun_water'},'cooling2':{'chiller2','turbo_water'},'power_view':{'power','power_display','matching','power_cable','earth'}}[view]
   if group=='utilities' and role not in wanted:opacity=.08
  if view in ['viewport','plasma','demo_closed','demo_open']:
   if view=='viewport':show=group in ['gun','door'] or role in ['front_frame','substrate','stage','shutter_blade'];opacity=.18 if role=='glass' else 1
   else:
    show=group in ['gun','shutter'] or role in ['stage','substrate','stage_support']
    if role in ['gun_shieldtube','gun_darkcap']:opacity=.25
    if group=='shutter':
     angle=80*smooth(u*2) if view=='demo_open' else 0
     tr.Identity();tr.Translate(-65,0,0);tr.RotateZ(angle);tr.Translate(65,0,0)
  ac.SetUserTransform(tr);ac.SetVisibility(show);ac.GetProperty().SetOpacity(opacity)'''
s=s.replace(needle,custom)
# Add a visual-only annular glow and atom paths, never exported into engineering CAD.
insert='''
plasma_actors=[]
for j in range(3):
 source=vtk.vtkParametricTorus();source.SetRingRadius(20);source.SetCrossSectionRadius(1.5+j*1.0)
 ss=vtk.vtkParametricFunctionSource();ss.SetParametricFunction(source);ss.SetUResolution(64);ss.SetVResolution(16);ss.Update()
 mm=vtk.vtkPolyDataMapper();mm.SetInputConnection(ss.GetOutputPort());aa=vtk.vtkActor();aa.SetMapper(mm);aa.SetPosition(0,0,125+j*4);aa.GetProperty().SetColor(.85,.2,.9);aa.GetProperty().SetOpacity(.3-j*.07);aa.GetProperty().LightingOff();r.AddActor(aa);plasma_actors.append(aa)
deposition=[]
for j in range(40):
 ss=vtk.vtkSphereSource();ss.SetRadius(.8);ss.SetThetaResolution(8);ss.SetPhiResolution(6);mm=vtk.vtkPolyDataMapper();mm.SetInputConnection(ss.GetOutputPort());aa=vtk.vtkActor();aa.SetMapper(mm);aa.GetProperty().SetColor(.94,.78,.32);aa.GetProperty().LightingOff();r.AddActor(aa);deposition.append(aa)
film_source=vtk.vtkCubeSource();film_source.SetBounds(-25,25,-25,25,41,41.6);fm=vtk.vtkPolyDataMapper();fm.SetInputConnection(film_source.GetOutputPort());film=vtk.vtkActor();film.SetMapper(fm);film.GetProperty().SetColor(.85,.6,.25);r.AddActor(film)
'''
s=s.replace('annotations=[]',insert+'\nannotations=[]',1)
point=" cam.SetViewUp(0,1,0) if view=='internals' and u>.65 else cam.SetViewUp(0,0,1)"
cam='''
 if view in ['overview','closing']:focus=np.array([170.,140.,80.]);scale=680;direction=np.array([1.,-1.,.45]) if view=='overview' else np.array([1.,1.,.5])
 if view=='gun_explode':focus=np.array([0.,0.,215.]);scale=190;direction=np.array([.8,-1,.3])
 if view=='gun_cooling':focus=np.array([0.,0.,160.]);scale=70;direction=np.array([-1.,-.6,.45]);label((35,0,150),'SECTION THROUGH COOLING HEAD')
 if view=='magnets':focus=np.array([0.,0.,160.]);scale=67;direction=np.array([.4,-.7,-1.]);label((0,0,134),'N');label((29,0,134),'S')
 if view=='gun_electrical':focus=np.array([0.,0.,285.]);scale=190;direction=np.array([.7,-1,.2])
 if view=='gas_supply':focus=np.array([330.,340.,220.]);scale=520;direction=np.array([.8,1,.45]);label((650,430,250),'ARGON');label((0,240,325),'MFC')
 if view=='tube_insert':focus=np.array([0.,340.,210.]);scale=65;direction=np.array([1.,.25,.25]);dimension((0,344.196,223),(0,360.196,223),'16 mm illustrative',(0,0,8));label((0,390,213),'6 mm OD')
 if view=='cooling1':focus=np.array([-180.,0.,180.]);scale=500;direction=np.array([.8,-1,.2]);label((-400,-120,60),'COOLING SYSTEM 1')
 if view=='cooling2':focus=np.array([260.,-50.,-90.]);scale=510;direction=np.array([.8,-1,.5]);label((710,-150,60),'COOLING SYSTEM 2')
 if view=='power_view':focus=np.array([250.,-120.,130.]);scale=550;direction=np.array([.8,-1,.3]);label((430,-380,-110),'DC / RF SUPPLY');label((430,-210,-60),'RF MATCHING')
 if view=='viewport':focus=np.array([0.,0.,136.]);scale=125;direction=np.array([0.,-400.,-116.]);label((70,-140,100),'70 mm CLEAR')
 if view in ['plasma','demo_closed','demo_open']:focus=np.array([0.,0.,105.]);scale=125;direction=np.array([.7,-1,-.05]);label((40,0,123),'ILLUSTRATIVE PLASMA')
 for aa in plasma_actors:aa.SetVisibility(view in ['viewport','plasma','demo_closed','demo_open'])
 for j,aa in enumerate(deposition):
  aa.SetVisibility(view in ['plasma','demo_closed','demo_open']);t=(u*4+j/40)%1;angle=j*2.39996;start=np.array([20*math.cos(angle),20*math.sin(angle),136.]);end=np.array([22*math.sin(j*1.7),22*math.cos(j*2.1),54 if view=='demo_closed' else 42.]);aa.SetPosition(*(start*(1-t)+end*t))
 film.SetVisibility(view=='demo_open' and u>.4);film.GetProperty().SetOpacity(max(0,(u-.4)/.6))
'''
s=s.replace(point,cam+'\n'+point)
s=s.replace("if 'preview' in sys.argv:\n sheet=Image.new('RGB',(1600,2250)","if 'preview' in sys.argv:\n sheet=Image.new('RGB',(1600,450*math.ceil(len(chs)/2))")
s=s.replace('Nine system previews rendered','Main video previews rendered').replace("FULL SYSTEM R03  |  Exact nominal CAD dimensions; purchased reference geometry identified in parts list.","COMPLETE SYSTEM R04  |  Nominal CAD dimensions; representative equipment and illustrative plasma identified.")
s=s.replace("f'System chapter {i+1}/9", "f'Main chapter {i+1}/{len(chs)}")
s=s.replace("'Mechanical layout only: verify supplier interfaces, seals, pressure strength, controls and cooling before fabrication.'","'Design study: supplier interfaces, seals, structural loading and electrical/cooling controls remain to qualify.'")
s=s.replace("win.Render();capture.Modified()", "if view=='viewport':cam.ParallelProjectionOff();cam.SetPosition(0,-400,20);cam.SetFocalPoint(0,0,136);cam.SetViewAngle(35);r.ResetCameraClippingRange()\n win.Render();capture.Modified()")
s=s.replace("im=Image.new('RGB',(W,H)","if ch['title']=='Magnetic circuit and calculated field' and u>.35:\n  field=Image.open(P.parents[2]/'advanced-tinkering-original'/'balanced-twelve-stack-study'/'magnetic-simulation'/'Target field map.png').convert('RGB');field.thumbnail((VW,VH));bg=Image.new('RGB',(VW,VH),'#101a29');bg.paste(field,((VW-field.width)//2,(VH-field.height)//2));arr=np.flipud(np.array(bg))\n im=Image.new('RGB',(W,H)")
(P/'render_main.py').write_text(s)
# Modify existing integrator to add the proven compression animation after chapter two.
s=(B/'integrate_video.py').read_text().replace('Full sputter system R03 - integrated walkthrough.mp4','Complete sputter system R04 - main walkthrough.mp4').replace('Full sputter system R03 - integrated dimensioned walkthrough','Complete sputter system R04 - main walkthrough');(P/'integrate_video.py').write_text(s)
