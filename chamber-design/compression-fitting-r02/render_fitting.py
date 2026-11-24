from pathlib import Path
import json,struct,math,wave,subprocess,re,time,sys
import vtk,imageio_ffmpeg,numpy as np
from vtk.util.numpy_support import numpy_to_vtk,numpy_to_vtkIdTypeArray,vtk_to_numpy
from PIL import Image,ImageDraw,ImageFont
P=Path(__file__).resolve().parent;OLD=P.parent/'complete-chamber-r01'
W,H,FPS,VW,VH=1600,900,12,1080,690
chs=json.loads((P/'chapters.json').read_text())
font=lambda n,b=False:ImageFont.truetype('C:/Windows/Fonts/'+('segoeuib.ttf' if b else 'segoeui.ttf'),n)
TITLE=font(32,True);BODY=font(25);SMALL=font(18);LABEL=font(24,True)
win=vtk.vtkRenderWindow();win.SetOffScreenRendering(1);win.SetSize(VW,VH);win.SetMultiSamples(0)
r=vtk.vtkRenderer();r.SetBackground(.045,.075,.115);r.SetBackground2(.14,.19,.25);r.GradientBackgroundOn();win.AddRenderer(r)
def mesh(a):
 p=vtk.vtkPolyData();v=vtk.vtkPoints();v.SetData(numpy_to_vtk(a.reshape(-1,3),deep=True));p.SetPoints(v)
 cells=vtk.vtkCellArray();cells.SetData(numpy_to_vtkIdTypeArray(np.arange(0,len(a)*3+1,3,dtype=np.int64),deep=True),numpy_to_vtkIdTypeArray(np.arange(len(a)*3,dtype=np.int64),deep=True));p.SetPolys(cells)
 return p
def actor(p,color):
 clean=vtk.vtkCleanPolyData();clean.SetInputData(p);clean.Update();norm=vtk.vtkPolyDataNormals();norm.SetInputConnection(clean.GetOutputPort());norm.SetFeatureAngle(35);norm.Update()
 m=vtk.vtkPolyDataMapper();m.SetInputConnection(norm.GetOutputPort());m.ScalarVisibilityOff();a=vtk.vtkActor();a.SetMapper(m);a.GetProperty().SetColor(*color);a.GetProperty().SetAmbient(.3);a.GetProperty().SetDiffuse(.68);a.GetProperty().SetSpecular(.3);a.GetProperty().SetSpecularPower(40);r.AddActor(a);return a
old=[]
with (OLD/'mesh.bin').open('rb') as f:
 for q in json.loads((OLD/'parts.json').read_text()):
  n=struct.unpack('<I',f.read(4))[0];a=np.frombuffer(f.read(n*36),'<f4').reshape(-1,3,3)
  if q['group']=='gun' or q['name'] in ['Roof plate','Floor plate'] or q['role'] in ['stage','substrate','stage_support','gun_mount']:
   old.append(q|{'actor':actor(mesh(a),q['color'])})
parts=[]
with (P/'fitting-mesh.bin').open('rb') as f:
 for q in json.loads((P/'fitting-parts.json').read_text()):
  states={}
  for state in ['full','section']:
   n=struct.unpack('<I',f.read(4))[0];a=np.frombuffer(f.read(n*36),'<f4').reshape(-1,3,3);p=mesh(a)
   states[state]={'actor':actor(p,q['color']),'poly':p,'points':a.reshape(-1,3).copy()}
  parts.append(q|{'states':states})
capture=vtk.vtkWindowToImageFilter();capture.SetInput(win);capture.SetInputBufferTypeToRGB();capture.ReadFrontBufferOff()
def smooth(u):return u*u*(3-2*u)
def interp(u,points):
 for j in range(1,len(points)):
  if u<=points[j][0]:
   a,v=points[j-1];b,w=points[j];return v+(w-v)*smooth((u-a)/(b-a))
 return points[-1][1]
def wrap(d,s,x,y,width,ft,fill):
 ln=''
 for w in s.split():
  t=(ln+' '+w).strip()
  if d.textlength(t,font=ft)>width and ln:d.text((x,y),ln,font=ft,fill=fill);y+=ft.size+9;ln=w
  else:ln=t
 if ln:d.text((x,y),ln,font=ft,fill=fill);y+=ft.size+9
 return y
def frame(i,u):
 view=chs[i]['view'];gap=100.;bodylift=0.;caplift=4.;spin=0.;jaw=0.;expl=0.;section=view=='section';sealcomp=0.
 if view=='explode':expl=1.;jaw=38
 elif view=='seat':bodylift=35*(1-smooth(u));jaw=38
 elif view=='clamp':jaw=38*(1-smooth(min(1,u/.7)))
 elif view=='insert':gap=30+70*smooth(u)
 elif view=='adjust':gap=interp(u,[(0,100),(.25,75),(.7,150),(1,100)])
 elif view in ['tighten','section']:
  t=smooth(u);caplift=4*(1-t);spin=-720*t;sealcomp=max(0,1-caplift/.52)
 elif view=='repeat':
  caplift=interp(u,[(0,0),(.25,4),(.7,4),(1,0)])
  gap=interp(u,[(0,100),(.3,100),(.65,125),(1,125)]);spin=180*caplift;sealcomp=max(0,1-caplift/.52)
 for q in old:
  a=q['actor'];a.SetUserTransform(None);a.SetVisibility(True);a.GetProperty().SetOpacity(1)
  if q['group']=='gun':a.SetPosition(0,0,gap-100);a.SetVisibility(view not in ['explode','seat','clamp'])
  else:a.SetPosition(0,0,0)
  if q['name']=='Roof plate':a.GetProperty().SetOpacity(.30 if section else 1)
  if q['role'] in ['stage','substrate','stage_support'] or q['name']=='Floor plate':a.SetVisibility(view=='adjust')
 for q in parts:
  role=q['role']
  for state,s in q['states'].items():
   ac=s['actor'];ac.SetVisibility(state==('section' if section else 'full'));ac.SetUserTransform(None)
   tr=vtk.vtkTransform();dz=0
   if role in ['body','cap','cap_mark','follower','tube_seal']:dz=bodylift
   if role in ['cap','cap_mark']:
    dz+=35*expl if expl else caplift
    if not section:tr.RotateZ(spin)
   elif role=='follower':dz+=20*expl if expl else .52*(1-sealcomp)
   elif role=='tube_seal':dz+=10*expl
   if role=='clamp_left':tr.Translate(0,25,0);tr.RotateZ(-jaw);tr.Translate(0,-25,0)
   if role=='clamp_right':tr.Translate(0,25,0);tr.RotateZ(jaw);tr.Translate(0,-25,0)
   if role in ['clamp_bolt','clamp_wing']:ac.SetVisibility(state=='full' and jaw<2)
   if role=='clamp_wing' and view=='clamp':
    tr.Translate(0,-29,332);tr.RotateX(720*smooth(max(0,(u-.7)/.3)));tr.Translate(0,29,-332)
   tr.Translate(0,0,dz);ac.SetUserTransform(tr)
   if role=='tube_seal':
    pts=s['points'].copy();rad=np.hypot(pts[:,0],pts[:,1]);theta=np.arctan2(pts[:,1],pts[:,0])
    rz=(2.62-.52*sealcomp)/2;rx=1.31**2/rz;rm=12.7+rx
    oldrx=1.31**2/1.05;oldrm=12.7+oldrx
    nr=rm+(rad-oldrm)*rx/oldrx
    pts[:,0]=nr*np.cos(theta);pts[:,1]=nr*np.sin(theta);pts[:,2]=333+39.8+rz+(pts[:,2]-(333+40.85))*rz/1.05
    s['poly'].GetPoints().SetData(numpy_to_vtk(pts,deep=True));s['poly'].Modified()
 cam=r.GetActiveCamera();focus=np.array([0.,0.,355.]);scale=62;direction=np.array([.6,-1,.40])
 if view=='explode':focus[2]=370;scale=87
 if view=='seat':focus[2]=365;scale=88
 if view=='clamp':focus[2]=338;scale=48;direction=np.array([.8,-1,.5])
 if view=='insert':focus[2]=360;scale=76
 if view=='adjust':focus=np.array([0.,0.,245.]);scale=230;direction=np.array([.65,-1,.18])
 if view=='section':focus=np.array([0.,0.,370.]);scale=37;direction=np.array([.22,-1,.15])
 if view=='repeat':focus[2]=356;scale=72
 cam.SetViewUp(0,0,1);cam.SetFocalPoint(*focus);cam.SetPosition(*(focus+direction/np.linalg.norm(direction)*1000));cam.ParallelProjectionOn();cam.SetParallelScale(scale);r.ResetCameraClippingRange()
 win.Render();capture.Modified();capture.Update();arr=vtk_to_numpy(capture.GetOutput().GetPointData().GetScalars()).reshape(VH,VW,3)
 im=Image.new('RGB',(W,H),'#101a29');im.paste(Image.fromarray(np.flipud(arr)),(0,85));d=ImageDraw.Draw(im)
 d.text((24,18),f'{i+1:02}  {chs[i]["title"]}',font=TITLE,fill='#eef5fb');d.rectangle((1080,85,1600,775),fill='#152333')
 d.text((1110,115),'ASSEMBLY / OPERATION',font=LABEL,fill='#79ddc8');y=170
 for fact in chs[i]['facts']:
  d.ellipse((1107,y+9,1115,y+17),fill='#79d6c3');y=wrap(d,fact,1132,y,435,BODY,'#e2edf5')+25
 if view in ['tighten','section','repeat']:
  d.text((1110,620),f'Cap lift: {caplift:.2f} mm',font=LABEL,fill='#ffd27a')
  d.text((1110,665),f'Tube stays at chosen height',font=SMALL,fill='#d5e5ef')
 if view=='adjust':d.text((1110,620),f'Target gap: {gap:.1f} mm',font=LABEL,fill='#ffd27a')
 if view=='section':d.text((30,738),'SECTION: front half of fitting removed to expose the mechanism',font=SMALL,fill='#d6e4ef')
 d.text((28,797),'REFERENCE: QF25XVC100  |  Tube OD25.4 / KF flange OD39.88 / fitting length50.8 mm',font=SMALL,fill='#d8e4ee')
 d.text((28,833),'Thread pitch, follower, cap and seal-seat details are illustrative; verify purchased hardware. Adjust while vented.',font=SMALL,fill='#dcc69c')
 d.rectangle((0,H-6,int(W*u),H),fill='#78d6bf')
 return np.asarray(im)
def stamp(t):
 n=round(t*1000);return f'{n//3600000:02}:{n//60000%60:02}:{n//1000%60:02},{n%1000:03}'
if 'preview' in sys.argv:
 sheet=Image.new('RGB',(1600,1800),'#101a29')
 for i in range(len(chs)):
  im=Image.fromarray(frame(i,.45));im.save(P/f'preview-{i:02}.png');sheet.paste(im.resize((800,450)),((i%2)*800,(i//2)*450))
 sheet.save(P/'Fitting animation contact sheet.jpg');win.Finalize();print('Previews rendered');sys.exit()
durations=[];params=None;chunks=[]
for i in range(len(chs)):
 with wave.open(str(P/f'voice-{i:02}.wav'),'rb') as f:p=f.getparams();raw=f.readframes(p.nframes)
 if params is None:params=p
 duration=math.ceil((p.nframes/p.framerate+1.3)*FPS)/FPS;durations.append(duration);lead=round(.3*p.framerate);tail=round(duration*p.framerate)-lead-p.nframes
 chunks.append(bytes(lead*p.sampwidth*p.nchannels)+raw+bytes(tail*p.sampwidth*p.nchannels))
with wave.open(str(P/'Narration.wav'),'wb') as f:
 f.setparams(params)
 for c in chunks:f.writeframes(c)
writer=imageio_ffmpeg.write_frames(str(P/'silent.mp4'),(W,H),fps=FPS,codec='libx264',quality=8,macro_block_size=1,output_params=['-preset','fast']);writer.send(None)
timeline=[];subs=[];elapsed=0;t0=time.perf_counter()
for i,duration in enumerate(durations):
 timeline.append((elapsed,chs[i]['title']));sentences=re.split(r'(?<=[.!?])\s+',chs[i]['speech']);nchars=sum(map(len,sentences));t=elapsed+.3
 for sentence in sentences:
  end=t+(duration-1.3)*len(sentence)/nchars;subs.append(f'{len(subs)+1}\n{stamp(t)} --> {stamp(end)}\n{sentence}\n');t=end
 for n in range(round(duration*FPS)):writer.send(frame(i,n/max(1,duration*FPS-1)))
 elapsed+=duration;print(f'Rendered fitting chapter {i+1}/{len(chs)}, render elapsed {time.perf_counter()-t0:.0f}s',flush=True)
writer.close();win.Finalize();(P/'Captions.srt').write_text('\n'.join(subs),encoding='utf-8')
fm=';FFMETADATA1\ntitle=Gun compression fitting - assembly and adjustment\n';trans=[]
for i,(t,title) in enumerate(timeline):
 end=timeline[i+1][0] if i+1<len(timeline) else elapsed
 fm+=f'[CHAPTER]\nTIMEBASE=1/1000\nSTART={round(t*1000)}\nEND={round(end*1000)}\ntitle={title}\n';trans += [f'{int(t)//60}:{int(t)%60:02} {title}',chs[i]['speech'],'']
(P/'chapters.ffmeta').write_text(fm);(P/'Video transcript.txt').write_text('\n'.join(trans))
final=P/'Gun compression fitting - assembly and adjustment.mp4'
subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-y','-v','error','-i',str(P/'silent.mp4'),'-i',str(P/'Narration.wav'),'-i',str(P/'Captions.srt'),'-i',str(P/'chapters.ffmeta'),'-map','0:v','-map','1:a','-map','2:s','-map_metadata','3','-map_chapters','3','-c:v','copy','-c:a','aac','-c:s','mov_text','-movflags','+faststart',str(final)],check=True)
(P/'Video verification.json').write_text(json.dumps({'duration_seconds':elapsed,'chapters':timeline,'fps':FPS,'resolution':[W,H],'video':str(final)},indent=2))
print('Standalone fitting animation completed',flush=True)
