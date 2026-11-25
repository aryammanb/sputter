from pathlib import Path
import json,struct,math,wave,subprocess,re,time,sys
import numpy as np
import vtk,imageio_ffmpeg
from vtk.util.numpy_support import numpy_to_vtk,numpy_to_vtkIdTypeArray,vtk_to_numpy
from PIL import Image,ImageDraw,ImageFont
P=Path(__file__).resolve().parent;W,H,FPS,VW,VH=1600,900,8,1080,690
meta=json.loads((P/'parts.json').read_text());chs=json.loads((P/'chapters.json').read_text());dims=json.loads((P/'System dimension report.json').read_text())['dimensions_mm']
font=lambda n,b=False:ImageFont.truetype('C:/Windows/Fonts/'+('segoeuib.ttf' if b else 'segoeui.ttf'),n)
TITLE=font(31,True);BODY=font(23);SMALL=font(18);LABEL=font(23,True)
win=vtk.vtkRenderWindow();win.SetOffScreenRendering(1);win.SetSize(VW,VH);win.SetMultiSamples(0)
r=vtk.vtkRenderer();r.SetBackground(.045,.075,.115);r.SetBackground2(.14,.19,.25);r.GradientBackgroundOn();win.AddRenderer(r)
def poly(a):
 p=vtk.vtkPolyData();v=vtk.vtkPoints();v.SetData(numpy_to_vtk(a.reshape(-1,3),deep=True));p.SetPoints(v)
 cells=vtk.vtkCellArray();cells.SetData(numpy_to_vtkIdTypeArray(np.arange(0,len(a)*3+1,3,dtype=np.int64),deep=True),numpy_to_vtkIdTypeArray(np.arange(len(a)*3,dtype=np.int64),deep=True));p.SetPolys(cells)
 clean=vtk.vtkCleanPolyData();clean.SetInputData(p);clean.Update();norm=vtk.vtkPolyDataNormals();norm.SetInputConnection(clean.GetOutputPort());norm.SetFeatureAngle(35);norm.Update();out=vtk.vtkPolyData();out.ShallowCopy(norm.GetOutput());return out
records=[]
with (P/'mesh.bin').open('rb') as f:
 for q in meta:
  n=struct.unpack('<I',f.read(4))[0];a=np.frombuffer(f.read(n*36),'<f4').reshape(-1,3,3)
  m=vtk.vtkPolyDataMapper();m.SetInputData(poly(a));m.ScalarVisibilityOff();ac=vtk.vtkActor();ac.SetMapper(m);ac.GetProperty().SetColor(*q['color']);ac.GetProperty().SetAmbient(.3);ac.GetProperty().SetDiffuse(.68);ac.GetProperty().SetSpecular(.3);ac.GetProperty().SetSpecularPower(35);r.AddActor(ac);records.append(q|{'actor':ac})
particles=[]
for i in range(14):
 s=vtk.vtkSphereSource();s.SetRadius(3.2);s.SetThetaResolution(10);s.SetPhiResolution(8);m=vtk.vtkPolyDataMapper();m.SetInputConnection(s.GetOutputPort());a=vtk.vtkActor();a.SetMapper(m);a.GetProperty().SetColor(.22,.88,.95);a.GetProperty().LightingOff();r.AddActor(a);particles.append(a)

plasma_actors=[]
for j in range(3):
 source=vtk.vtkParametricTorus();source.SetRingRadius(20);source.SetCrossSectionRadius(1.5+j*1.0)
 ss=vtk.vtkParametricFunctionSource();ss.SetParametricFunction(source);ss.SetUResolution(64);ss.SetVResolution(16);ss.Update()
 mm=vtk.vtkPolyDataMapper();mm.SetInputConnection(ss.GetOutputPort());aa=vtk.vtkActor();aa.SetMapper(mm);aa.SetPosition(0,0,125+j*4);aa.GetProperty().SetColor(.85,.2,.9);aa.GetProperty().SetOpacity(.3-j*.07);aa.GetProperty().LightingOff();r.AddActor(aa);plasma_actors.append(aa)
deposition=[]
for j in range(40):
 ss=vtk.vtkSphereSource();ss.SetRadius(.8);ss.SetThetaResolution(8);ss.SetPhiResolution(6);mm=vtk.vtkPolyDataMapper();mm.SetInputConnection(ss.GetOutputPort());aa=vtk.vtkActor();aa.SetMapper(mm);aa.GetProperty().SetColor(.94,.78,.32);aa.GetProperty().LightingOff();r.AddActor(aa);deposition.append(aa)
film_source=vtk.vtkCubeSource();film_source.SetBounds(-25,25,-25,25,41,41.6);fm=vtk.vtkPolyDataMapper();fm.SetInputConnection(film_source.GetOutputPort());film=vtk.vtkActor();film.SetMapper(fm);film.GetProperty().SetColor(.85,.6,.25);r.AddActor(film)

annotations=[]
def label(pos,s):
 a=vtk.vtkBillboardTextActor3D();a.SetInput(s);a.SetPosition(*pos);a.GetTextProperty().SetFontSize(18);a.GetTextProperty().SetBold(1);a.GetTextProperty().SetColor(.98,.8,.43);a.GetTextProperty().SetJustificationToCentered();r.AddActor(a);annotations.append(a)
def line(a,b):
 s=vtk.vtkLineSource();s.SetPoint1(*a);s.SetPoint2(*b);m=vtk.vtkPolyDataMapper();m.SetInputConnection(s.GetOutputPort());ac=vtk.vtkActor();ac.SetMapper(m);ac.GetProperty().SetColor(.98,.8,.43);ac.GetProperty().SetLineWidth(2);ac.GetProperty().LightingOff();r.AddActor(ac);annotations.append(ac)
def dimension(a,b,s,offset=(0,0,0)):
 line(a,b)
 for p in [a,b]:line((p[0]-3,p[1],p[2]),(p[0]+3,p[1],p[2]))
 label(tuple((a[i]+b[i])/2+offset[i] for i in range(3)),s)
def smooth(u):u=max(0,min(1,u));return u*u*(3-2*u)
def wrap(d,s,x,y,w,ft,fill):
 ln=''
 for word in s.split():
  t=(ln+' '+word).strip()
  if d.textlength(t,font=ft)>w and ln:d.text((x,y),ln,font=ft,fill=fill);y+=ft.size+8;ln=word
  else:ln=t
 if ln:d.text((x,y),ln,font=ft,fill=fill);y+=ft.size+8
 return y
capture=vtk.vtkWindowToImageFilter();capture.SetInput(win);capture.SetInputBufferTypeToRGB();capture.ReadFrontBufferOff()
mfc_roles={'mfc_out_adapter','vcr_out_nut','vcr_gasket','mfc_body','mfc_electronics','mfc_male_vcr','mfc_signal','mfc_bracket','mfc_mount_screw','vcr_in_nut','vcr_npt_adapter','push_body','push_collet'}
turbo_roles={'turbo_body','turbo_core','turbo_fin','turbo_outlet','turbo_vent','turbo_connector','turbo_cooling','iso_seal','iso_clamp','iso_screw','foreline_adapter','turbo_flange','hose_end'}
hp=np.array(dims['hose_path_samples'])
def frame(i,u):
 ch=chs[i];view=ch['view'];da=-110*smooth(u*1.5) if view=='door' else 0;sa=0
 if view=='internals' and u>.65:sa=40-40*math.cos(2*math.pi*(u-.65)/.35)
 exploded=math.sin(math.pi*u)**2 if view=='gas_chain' else 0
 for q in records:
  ac=q['actor'];role=q['role'];name=q['name'];group=q['group'];show=True;opacity=1;tr=vtk.vtkTransform()
  if group=='door':tr.Translate(-118,-116,0);tr.RotateZ(da);tr.Translate(118,116,0)
  if group=='shutter':tr.Translate(-65,0,0);tr.RotateZ(sa);tr.Translate(65,0,0)
  if role=='glass':opacity=.32
  if view=='door' and role in ['backing_pump','hose','hose_ribs','hose_end','base_plate','frame']:show=False
  if view=='internals':
   show=group in ['gun','shutter','fitting'] or role in ['stage','substrate','stage_support','pump_baffle','baffle_support'] or name=='Floor plate'
   if u>.65 and group in ['gun','fitting']:show=False
  if view=='turbo':show=role in turbo_roles or name=='Floor plate'
  if view=='backing':
   show=role in turbo_roles|{'hose','hose_ribs','backing_pump','base_plate'}
   if role in ['hose','hose_ribs']:opacity=.27
  if view=='gauges':show=role.startswith('gauge_') or role in ['kf_clamp','connection_seal','service_port'] or name=='Rear wall'
  if view in ['mfc','gas_chain']:
   show=role in mfc_roles or name=='Rear wall' or 'MFC' in name or (role=='service_port' and 'gas' in name)
   if role in ['mfc_bracket','mfc_mount_screw'] and view=='gas_chain':show=False
   if view=='gas_chain':
    shift=0
    if role in ['mfc_out_adapter','vcr_out_nut']:shift=18
    if role=='vcr_gasket':shift=35 if 'outlet' in name else 85
    if role in ['mfc_body','mfc_electronics','mfc_male_vcr','mfc_signal']:shift=60
    if role in ['vcr_in_nut','vcr_npt_adapter']:shift=100
    if role in ['push_body','push_collet']:shift=140
    tr.Translate(0,shift*exploded,0)
   if view=='mfc' and role in ['mfc_body','mfc_out_adapter','mfc_male_vcr','vcr_npt_adapter','push_body']:opacity=.45
  ac.GetMapper().RemoveAllClippingPlanes()
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
  ac.SetUserTransform(tr);ac.SetVisibility(show);ac.GetProperty().SetOpacity(opacity)
 for a in annotations:r.RemoveActor(a)
 annotations.clear()
 for j,a in enumerate(particles):
  a.SetVisibility(view in ['backing','mfc'])
  t=(u*3+j/len(particles))%1
  if view=='backing':
   idx=t*(len(hp)-1);k=min(len(hp)-2,int(idx));pt=hp[k]*(1-(idx-k))+hp[k+1]*(idx-k);a.SetPosition(*pt)
  if view=='mfc':a.SetPosition(0,dims['push_socket_face_y']-(dims['push_socket_face_y']-110)*t,210);a.SetScale(.5)
  else:a.SetScale(1)
 cam=r.GetActiveCamera();focus=np.array([150.,125.,65.]);direction=np.array([.95,-1,.48]);scale=450
 if view=='overview':direction=np.array([.95,-1+.25*math.sin(2*math.pi*u),.48])
 elif view=='door':focus=np.array([-40.,-30.,165.]);direction=np.array([.7,-1,.28]);scale=280
 elif view=='internals':
  focus=np.array([-15.,0.,160.]);direction=np.array([.5,-1,.15]);scale=205
  if u<.3:
   focus=np.array([0.,0.,57.]);direction=np.array([.8,-1,.6]);scale=95
   dimension((58,-30,34),(58,-30,40),'6 mm',(13,-3,0));dimension((32,-35,41),(32,-35,53),'12 mm',(22,-5,0))
  elif u<.65:
   dimension((-98,-18,53.5),(-98,-18,293.5),'240 mm',(-20,0,0));dimension((45,-40,41),(45,-40,141),'100 mm',(15,-3,0))
  else:focus=np.array([0.,0.,40.]);direction=np.array([0.,0.,1.]);scale=125
 elif view=='turbo':focus=np.array([8.,0.,-110.]);direction=np.array([.9,-1,-.18 if u<.5 else .25]);scale=130
 elif view=='backing':focus=np.array([235.,190.,-125.]);direction=np.array([.9,-1,.75]);scale=310;label((393,325,-65),'RV3 INLET');label((95,0,-158),'TURBO OUTLET')
 elif view=='gauges':focus=np.array([0.,160.,70.]);direction=np.array([.5,1,.15]);scale=150;label((-50,185,-57),'PIRANI');label((50,185,-72),'PENNING')
 elif view=='mfc':focus=np.array([0.,235.,245.]);direction=np.array([.9,1,.25]);scale=145
 elif view=='gas_chain':focus=np.array([0.,290.+70*exploded,245.]);direction=np.array([1,.2,.3]);scale=190
 elif view=='closing':focus=np.array([140.,130.,60.]);direction=np.array([1.,1.,.55]);scale=460

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


 if view=='demo_open' and u>.4:
  v=smooth((u-.4)/.3);focus=np.array([0.,0.,105.-55*v]);scale=125-45*v;direction=np.array([.7-.2*v,-1.,-.05+1.05*v])
 cam.SetViewUp(0,1,0) if view=='internals' and u>.65 else cam.SetViewUp(0,0,1)
 cam.SetFocalPoint(*focus);cam.SetPosition(*(focus+direction/np.linalg.norm(direction)*1200));cam.ParallelProjectionOn();cam.SetParallelScale(scale);r.ResetCameraClippingRange()
 if view=='viewport':cam.ParallelProjectionOff();cam.SetPosition(0,-400,20);cam.SetFocalPoint(0,0,136);cam.SetViewAngle(35);r.ResetCameraClippingRange()
 win.Render();capture.Modified();capture.Update();arr=vtk_to_numpy(capture.GetOutput().GetPointData().GetScalars()).reshape(VH,VW,3)
 if ch['title']=='Magnetic circuit and calculated field' and u>.35:
  field=Image.open(P.parents[2]/'advanced-tinkering-original'/'balanced-twelve-stack-study'/'magnetic-simulation'/'Target field map.png').convert('RGB');field.thumbnail((VW,VH));bg=Image.new('RGB',(VW,VH),'#101a29');bg.paste(field,((VW-field.width)//2,(VH-field.height)//2));arr=np.flipud(np.array(bg))
 im=Image.new('RGB',(W,H),'#101a29');im.paste(Image.fromarray(np.flipud(arr)),(0,85));d=ImageDraw.Draw(im)
 d.text((25,18),ch['title'],font=TITLE,fill='#eef5fb');d.rectangle((1080,85,1600,775),fill='#152333');d.text((1110,115),'SYSTEM DESIGN',font=LABEL,fill='#7bddc8');y=168
 for fact in ch['facts']:
  d.ellipse((1107,y+8,1114,y+15),fill='#79d6c3');y=wrap(d,fact,1130,y,440,BODY,'#e2edf5')+18
 if view=='backing':
  d.text((1110,640),f'Hose route: {dims["hose_centreline_length"]:.1f} mm',font=LABEL,fill='#ffd27a')
  d.text((1110,682),'Gas-path illustration, not simulation',font=SMALL,fill='#cbdbe6')
 if view=='internals' and u>.65:d.text((1110,655),f'Shutter: {sa:.1f} degrees',font=LABEL,fill='#ffd27a')
 if view=='gas_chain':d.text((1110,655),'EXPLODED CONNECTION VIEW',font=LABEL,fill='#ffd27a')
 d.text((28,797),'COMPLETE SYSTEM R04  |  Nominal CAD dimensions; representative equipment and illustrative plasma identified.',font=SMALL,fill='#d5e3ed')
 d.text((28,833),'Design study: supplier interfaces, seals, structural loading and electrical/cooling controls remain to qualify.',font=SMALL,fill='#dcc69c')
 d.rectangle((0,H-6,int(W*u),H),fill='#79d6bf')
 return np.asarray(im)
def stamp(t):
 n=round(t*1000);return f'{n//3600000:02}:{n//60000%60:02}:{n//1000%60:02},{n%1000:03}'
if 'preview' in sys.argv:
 sheet=Image.new('RGB',(1600,450*math.ceil(len(chs)/2)),'#101a29')
 for i in range(len(chs)):
  im=Image.fromarray(frame(i,.42));im.save(P/f'preview-{i:02}.png');sheet.paste(im.resize((800,450)),((i%2)*800,(i//2)*450))
 sheet.save(P/'System walkthrough contact sheet.jpg');win.Finalize();print('Main video previews rendered');sys.exit()
durations=[];params=None;chunks=[]
for i in range(len(chs)):
 with wave.open(str(P/f'voice-{i:02}.wav'),'rb') as f:p=f.getparams();raw=f.readframes(p.nframes)
 if params is None:params=p
 duration=math.ceil((p.nframes/p.framerate+1.4)*FPS)/FPS;durations.append(duration);lead=round(.3*p.framerate);tail=round(duration*p.framerate)-lead-p.nframes;chunks.append(bytes(lead*p.sampwidth*p.nchannels)+raw+bytes(tail*p.sampwidth*p.nchannels))
with wave.open(str(P/'Narration.wav'),'wb') as f:
 f.setparams(params)
 for c in chunks:f.writeframes(c)
writer=imageio_ffmpeg.write_frames(str(P/'silent.mp4'),(W,H),fps=FPS,codec='libx264',quality=8,macro_block_size=1,output_params=['-preset','fast']);writer.send(None)
elapsed=0;timeline=[];subs=[];t0=time.perf_counter()
for i,duration in enumerate(durations):
 timeline.append((elapsed,chs[i]['title']));sentences=re.split(r'(?<=[.!?])\s+',chs[i]['speech']);count=sum(map(len,sentences));t=elapsed+.3
 for sentence in sentences:
  end=t+(duration-1.4)*len(sentence)/count;subs.append(f'{len(subs)+1}\n{stamp(t)} --> {stamp(end)}\n{sentence}\n');t=end
 for n in range(round(duration*FPS)):writer.send(frame(i,n/max(1,duration*FPS-1)))
 elapsed+=duration;print(f'Main chapter {i+1}/{len(chs)} rendered, elapsed {time.perf_counter()-t0:.0f}s',flush=True)
writer.close();win.Finalize();(P/'System captions.srt').write_text('\n'.join(subs),encoding='utf-8')
subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-y','-v','error','-i',str(P/'silent.mp4'),'-i',str(P/'Narration.wav'),'-map','0:v','-map','1:a','-c:v','copy','-c:a','aac','-movflags','+faststart',str(P/'System scenes.mp4')],check=True)
(P/'Scene timing.json').write_text(json.dumps({'duration_seconds':elapsed,'chapters':timeline,'durations':durations},indent=2))
print('System scenes rendered; ready to integrate fitting animation',flush=True)
