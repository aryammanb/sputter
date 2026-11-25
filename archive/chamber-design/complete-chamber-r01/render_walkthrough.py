from pathlib import Path
import json,struct,math,wave,subprocess,time,sys,re
import numpy as np
import vtk,imageio_ffmpeg
from vtk.util.numpy_support import numpy_to_vtk,numpy_to_vtkIdTypeArray,vtk_to_numpy
from PIL import Image,ImageDraw,ImageFont

P=Path(__file__).resolve().parent
W,H,FPS=1600,900,8
VW,VH=1080,690
meta=json.loads((P/'parts.json').read_text());chapters=json.loads((P/'chapters.json').read_text())
font=lambda n,b=False:ImageFont.truetype('C:/Windows/Fonts/'+('segoeuib.ttf' if b else 'segoeui.ttf'),n)
TITLE=font(33,True);LABEL=font(23,True);BODY=font(23);SMALL=font(18)
win=vtk.vtkRenderWindow();win.SetOffScreenRendering(1);win.SetSize(VW,VH);win.SetMultiSamples(0)
r=vtk.vtkRenderer();r.SetBackground(.045,.075,.115);r.SetBackground2(.13,.18,.23);r.GradientBackgroundOn();win.AddRenderer(r)
records=[]
def poly(a):
 p=vtk.vtkPolyData();v=vtk.vtkPoints();v.SetData(numpy_to_vtk(a.reshape(-1,3),deep=True));p.SetPoints(v)
 cells=vtk.vtkCellArray();cells.SetData(numpy_to_vtkIdTypeArray(np.arange(0,len(a)*3+1,3,dtype=np.int64),deep=True),numpy_to_vtkIdTypeArray(np.arange(len(a)*3,dtype=np.int64),deep=True));p.SetPolys(cells)
 clean=vtk.vtkCleanPolyData();clean.SetInputData(p);clean.Update()
 norm=vtk.vtkPolyDataNormals();norm.SetInputConnection(clean.GetOutputPort());norm.SetFeatureAngle(35);norm.Update()
 out=vtk.vtkPolyData();out.ShallowCopy(norm.GetOutput());return out
with (P/'mesh.bin').open('rb') as f:
 for q in meta:
  n=struct.unpack('<I',f.read(4))[0];a=np.frombuffer(f.read(n*36),'<f4').reshape(-1,3,3)
  mapper=vtk.vtkPolyDataMapper();mapper.SetInputData(poly(a));mapper.ScalarVisibilityOff()
  actor=vtk.vtkActor();actor.SetMapper(mapper);actor.GetProperty().SetColor(*q['color']);actor.GetProperty().SetAmbient(.30);actor.GetProperty().SetDiffuse(.68);actor.GetProperty().SetSpecular(.32);actor.GetProperty().SetSpecularPower(40)
  r.AddActor(actor);records.append(q|{'actor':actor})

annotations=[]
def line(a,b,color=(.95,.74,.3)):
 source=vtk.vtkLineSource();source.SetPoint1(*a);source.SetPoint2(*b);source.Update()
 m=vtk.vtkPolyDataMapper();m.SetInputConnection(source.GetOutputPort());ac=vtk.vtkActor();ac.SetMapper(m);ac.GetProperty().SetColor(*color);ac.GetProperty().SetLineWidth(2);ac.GetProperty().LightingOff();r.AddActor(ac);annotations.append(ac)
def label(pos,text,color=(.98,.83,.47)):
 a=vtk.vtkBillboardTextActor3D();a.SetInput(text);a.SetPosition(*pos);a.GetTextProperty().SetFontSize(19);a.GetTextProperty().SetColor(*color);a.GetTextProperty().SetBold(1);a.GetTextProperty().SetJustificationToCentered();r.AddActor(a);annotations.append(a)
def dimension(a,b,text,offset=(0,0,0)):
 line(a,b)
 for pt in [a,b]:line((pt[0]-3,pt[1],pt[2]),(pt[0]+3,pt[1],pt[2]))
 label(tuple((a[j]+b[j])/2+offset[j] for j in range(3)),text)

capture=vtk.vtkWindowToImageFilter();capture.SetInput(win);capture.SetInputBufferTypeToRGB();capture.ReadFrontBufferOff()
last=None
def wrap(d,text,x,y,width,ft,fill):
 words=text.split();ln=''
 for word in words:
  test=(ln+' '+word).strip()
  if d.textlength(test,font=ft)>width and ln:d.text((x,y),ln,font=ft,fill=fill);y+=ft.size+8;ln=word
  else:ln=test
 if ln:d.text((x,y),ln,font=ft,fill=fill);y+=ft.size+8
 return y

def frame(i,u):
 global last
 ch=chapters[i];view=ch['view'];gap=100;angle=0;door=0
 if view=='door':door=-110*min(1,u*1.5)
 if view in ['mount','stage','travel','shutter','sweep']:door=-110
 if view=='closing':door=-110*(.5+.5*math.sin(2*math.pi*u))
 if view=='travel':gap=112.5-37.5*math.cos(2*math.pi*u)
 if view=='sweep':angle=40-40*math.cos(2*math.pi*u)
 for q in records:
  ac=q['actor'];role=q['role'];group=q['group'];name=q['name'];show=True;opacity=1
  ac.SetUserTransform(None)
  tr=vtk.vtkTransform()
  if group=='gun':tr.Translate(0,0,gap-100)
  elif group=='door':tr.Translate(-118,-116,0);tr.RotateZ(door);tr.Translate(118,116,0)
  elif group=='shutter':tr.Translate(-65,0,0);tr.RotateZ(angle);tr.Translate(65,0,0)
  ac.SetUserTransform(tr)
  if role=='glass':opacity=.32
  if view in ['stage','travel','shutter','sweep']:
   if role=='structure' and name!='Floor plate':show=False
   if group=='door' or role.startswith('hinge') or role in ['latch_catch','door_seal','support']:show=False
  if view=='mount':
   if role=='structure':show=name=='Roof plate';opacity=.24
   if group=='door' or role in ['door_seal','support'] or role.startswith('hinge'):show=False
  if view=='stage':
   if group=='gun' or group=='shutter' or role in ['shutter_seal','gun_mount','gun_mount_seal','gun_mount_clamp','gun_adapter']:show=False
  if view=='shutter':
   if group=='gun':show=False
   if role in ['gun_mount','gun_mount_seal','gun_mount_clamp','gun_adapter']:show=False
  if view=='sweep':
   if group=='gun' or role in ['gun_mount','gun_mount_seal','gun_mount_clamp','gun_adapter','shutter_seal','shutter_screw','shutter_nut','shutter_washer']:show=False
  ac.SetVisibility(show);ac.GetProperty().SetOpacity(opacity)
 for a in annotations:r.RemoveActor(a)
 annotations.clear()
 cam=r.GetActiveCamera();focus=np.array([0.,-10.,170.]);direction=np.array([.72,-1.,.48]);scale=285
 if view=='overview':direction=np.array([.78+.12*math.sin(2*math.pi*u),-1,.43]);scale=285
 elif view=='door':focus=np.array([-55.,-50.,165.]);scale=280;direction=np.array([.65,-1,.3])
 elif view=='rear':
  direction=np.array([.8,1,.4]);scale=270
  if u>.63:focus=np.array([0.,0.,30.]);direction=np.array([.65,.8,-.55]);scale=175
 elif view=='mount':focus=np.array([-20.,0.,325.]);scale=130;direction=np.array([.6,-1,.35])
 elif view=='stage':focus=np.array([0.,0.,33.]);scale=90;direction=np.array([.8,-1,.65]);dimension((58,-25,34),(58,-25,40),'6 mm',(10,-4,0));dimension((-58,-25,0),(-58,-25,40),'40 mm',(-14,0,0))
 elif view=='travel':focus=np.array([0.,0.,180.]);scale=240;direction=np.array([.6,-1,.15]);dimension((44,-42,41),(44,-42,41+gap),f'{gap:.1f} mm',(18,-8,0))
 elif view=='shutter':focus=np.array([-20.,0.,169.]);scale=170;direction=np.array([.25,-1,.12]);dimension((-97,-18,53.5),(-97,-18,293.5),'240 mm',(-18,-2,0));dimension((35,-35,41),(35,-35,53),'12 mm',(24,-8,-1))
 elif view=='sweep':focus=np.array([0.,0.,40.]);scale=125;direction=np.array([0,0,1.]);cam.SetViewUp(0,1,0)
 elif view=='closing':focus=np.array([-30.,-30.,170.]);scale=290;direction=np.array([.75,-1,.4])
 if view!='sweep':cam.SetViewUp(0,0,1)
 cam.SetFocalPoint(*focus);cam.SetPosition(*(focus+direction/np.linalg.norm(direction)*1000));cam.ParallelProjectionOn();cam.SetParallelScale(scale);r.ResetCameraClippingRange()
 win.Render();capture.Modified();capture.Update();arr=vtk_to_numpy(capture.GetOutput().GetPointData().GetScalars()).reshape(VH,VW,3)
 im=Image.new('RGB',(W,H),'#101a29');im.paste(Image.fromarray(np.flipud(arr)),(0,85));d=ImageDraw.Draw(im)
 d.text((26,18),f'{i+1:02}  {ch["title"]}',font=TITLE,fill='#edf5fb')
 d.rectangle((1080,85,1600,775),fill='#152333');d.text((1110,112),'MODEL DIMENSIONS',font=LABEL,fill='#7cddc9')
 y=165
 for fact in ch['facts']:
  d.ellipse((1107,y+8,1114,y+15),fill='#79d6c3');y=wrap(d,fact,1130,y,440,BODY,'#e3edf5')+18
 if view=='travel':d.text((1110,655),f'Gap now: {gap:.1f} mm',font=LABEL,fill='#ffd277')
 if view=='sweep':
  d.text((1110,655),f'Rotation: {angle:.1f} degrees',font=LABEL,fill='#ffd277')
  d.text((1110,693),'Top-down; gun hidden',font=SMALL,fill='#b6c7d6')
 if view in ['stage','travel','shutter']:d.text((30,746),'CUTAWAY VIEW: walls hidden to reveal actual CAD parts',font=SMALL,fill='#bcd0df')
 d.text((28,797),'NOMINAL CAD DIMENSIONS  |  mm unless stated  |  Reference substrate thickness: 1 mm',font=SMALL,fill='#d4e1ec')
 d.text((28,831),'Mechanical concept: supplier interfaces, seals and pressure strength require verification before fabrication.',font=SMALL,fill='#dcc69c')
 d.rectangle((0,H-6,int(W*u),H),fill='#77d5bf')
 return np.asarray(im)

def stamp(t):
 n=round(t*1000);return f'{n//3600000:02}:{n//60000%60:02}:{n//1000%60:02},{n%1000:03}'

if 'preview' in sys.argv:
 sheet=Image.new('RGB',(1600,2250),'#101a29')
 for i in range(len(chapters)):
  img=Image.fromarray(frame(i,.42));img.save(P/f'preview-{i:02}.png');sheet.paste(img.resize((800,450)),((i%2)*800,(i//2)*450))
 sheet.save(P/'Walkthrough contact sheet.jpg');win.Finalize();print('Nine scene previews rendered',flush=True);sys.exit()

durations=[];params=None;chunks=[]
for i in range(len(chapters)):
 with wave.open(str(P/f'voice-{i:02}.wav'),'rb') as f:p=f.getparams();raw=f.readframes(p.nframes)
 if params is None:params=p
 duration=math.ceil((p.nframes/p.framerate+1.4)*FPS)/FPS;durations.append(duration);lead=round(.3*p.framerate);tail=round(duration*p.framerate)-lead-p.nframes
 chunks.append(bytes(lead*p.sampwidth*p.nchannels)+raw+bytes(tail*p.sampwidth*p.nchannels))
with wave.open(str(P/'Narration.wav'),'wb') as f:
 f.setparams(params)
 for chunk in chunks:f.writeframes(chunk)
writer=imageio_ffmpeg.write_frames(str(P/'silent.mp4'),(W,H),fps=FPS,codec='libx264',quality=8,macro_block_size=1,output_params=['-preset','fast']);writer.send(None)
timeline=[];subs=[];elapsed=0;started=time.perf_counter()
for i,duration in enumerate(durations):
 timeline.append((elapsed,chapters[i]['title']))
 # Sentence subtitles timed in proportion to sentence length.
 sentences=re.split(r'(?<=[.!?])\s+',chapters[i]['speech']);count=sum(map(len,sentences));t=elapsed+.3
 for sentence in sentences:
  end=t+(duration-1.4)*len(sentence)/count
  subs.append(f'{len(subs)+1}\n{stamp(t)} --> {stamp(end)}\n{sentence}\n');t=end
 for n in range(round(duration*FPS)):writer.send(frame(i,n/max(1,duration*FPS-1)))
 elapsed+=duration;print(f'Rendered chapter {i+1}/9: {duration:.1f} seconds, total elapsed render {time.perf_counter()-started:.0f}s',flush=True)
writer.close();win.Finalize();(P/'Captions.srt').write_text('\n'.join(subs),encoding='utf-8')
ffmeta=';FFMETADATA1\ntitle=Sputter chamber R01 - dimensioned CAD walkthrough\n'
transcript=[]
for i,(t,title) in enumerate(timeline):
 end=timeline[i+1][0] if i+1<len(timeline) else elapsed
 ffmeta+=f'[CHAPTER]\nTIMEBASE=1/1000\nSTART={round(t*1000)}\nEND={round(end*1000)}\ntitle={title}\n'
 transcript.extend([f'{int(t)//60}:{int(t)%60:02} {title}',chapters[i]['speech'],''])
(P/'chapters.ffmeta').write_text(ffmeta);(P/'Video transcript.txt').write_text('\n'.join(transcript))
final=P/'Sputter chamber R01 - dimensioned walkthrough.mp4'
subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-y','-v','error','-i',str(P/'silent.mp4'),'-i',str(P/'Narration.wav'),'-i',str(P/'Captions.srt'),'-i',str(P/'chapters.ffmeta'),'-map','0:v','-map','1:a','-map','2:s','-map_metadata','3','-map_chapters','3','-c:v','copy','-c:a','aac','-c:s','mov_text','-movflags','+faststart',str(final)],check=True)
(P/'Video verification.json').write_text(json.dumps({'duration_seconds':elapsed,'chapters':timeline,'resolution':[W,H],'fps':FPS,'render_seconds':time.perf_counter()-started,'video':str(final)},indent=2))
print('Completed dimensioned walkthrough',flush=True)
