import base64,json,math,struct,sys,time,wave,subprocess
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
import vtk,imageio_ffmpeg
from vtk.util.numpy_support import numpy_to_vtk,numpy_to_vtkIdTypeArray,vtk_to_numpy

P=Path(__file__).resolve().parent;OUT=P/'coax-video';OUT.mkdir(exist_ok=True)
W,H,PANEL,FPS=1920,1080,450,15
chapters=json.loads((P/'coax-video-chapters.json').read_text())
data=json.loads((P/'viewer-geometry.json').read_text())
colors={'live':(.94,.51,.23),'ground':(.34,.60,.73),'insulator':(.92,.89,.74),'jacket':(.21,.24,.29),'hose':(.12,.35,.69)}
ren=vtk.vtkRenderer();ren.SetBackground(.063,.106,.165)
win=vtk.vtkRenderWindow();win.SetOffScreenRendering(1);win.SetSize(W-PANEL,H);win.SetMultiSamples(4);win.AddRenderer(ren)
cam=ren.GetActiveCamera();cam.ParallelProjectionOn()
records=[]
def poly(v):
 v=np.asarray(v,dtype=float).reshape(-1,3,3);p=vtk.vtkPolyData();pts=vtk.vtkPoints();pts.SetData(numpy_to_vtk(v.reshape(-1,3),deep=True));p.SetPoints(pts);cells=vtk.vtkCellArray();cells.SetData(numpy_to_vtkIdTypeArray(np.arange(0,len(v)*3+1,3,dtype=np.int64),deep=True),numpy_to_vtkIdTypeArray(np.arange(len(v)*3,dtype=np.int64),deep=True));p.SetPolys(cells)
 c=vtk.vtkCleanPolyData();c.SetInputData(p);c.SetTolerance(1e-8);c.Update();n=vtk.vtkPolyDataNormals();n.SetInputConnection(c.GetOutputPort());n.SetFeatureAngle(35);n.ConsistencyOn();n.AutoOrientNormalsOn();n.Update();q=vtk.vtkPolyData();q.ShallowCopy(n.GetOutput());return q
def clip(p,normal=(0,0,-1),origin=(0,0,0)):
 planes=vtk.vtkPlaneCollection();plane=vtk.vtkPlane();plane.SetNormal(*normal);plane.SetOrigin(*origin);planes.AddItem(plane);c=vtk.vtkClipClosedSurface();c.SetInputData(p);c.SetClippingPlanes(planes);c.SetTolerance(1e-6);c.GenerateFacesOn();c.Update();q=vtk.vtkPolyData();q.ShallowCopy(c.GetOutput());return q
def add(v,net,model='main',moving=False,section=True,name='',flat=False):
 p=poly(v)
 if flat:p=clip(p,(0,1,0),(0,-2.65,0))
 m=vtk.vtkPolyDataMapper();m.SetInputData(p);m.ScalarVisibilityOff();a=vtk.vtkActor();a.SetMapper(m);a.GetProperty().SetColor(*colors[net]);a.GetProperty().SetAmbient(.27);a.GetProperty().SetSpecular(.27);a.GetProperty().SetSpecularPower(28);ren.AddActor(a)
 records.append({'actor':a,'poly':p,'half':clip(p) if section else p,'section':section,'net':net,'model':model,'moving':moving,'name':name});return a
def annulus(a,b,ro,ri=0,y=0,z=0,n=48):
 v=[]
 def pt(x,r,t):return [x,y+r*math.cos(t),z+r*math.sin(t)]
 def quad(q):v.extend([[q[0],q[1],q[2]],[q[0],q[2],q[3]]])
 for i in range(n):
  t=i*2*math.pi/n;s=(i+1)*2*math.pi/n
  quad([pt(a,ro,t),pt(b,ro,t),pt(b,ro,s),pt(a,ro,s)])
  if ri:quad([pt(a,ri,s),pt(b,ri,s),pt(b,ri,t),pt(a,ri,t)])
  quad([pt(a,ri,t),pt(a,ro,t),pt(a,ro,s),pt(a,ri,s)])
  quad([pt(b,ri,s),pt(b,ro,s),pt(b,ro,t),pt(b,ri,t)])
 return np.array(v)
def ring(a,b,ro,ri,net,**kw):return add(annulus(a,b,ro,ri,kw.pop('y',0),kw.pop('z',0),kw.pop('n',48)),net,**kw)
def sweep(path,ro,ri=0,n=20):
 path=np.asarray(path);v=[]
 tangent=np.gradient(path,axis=0);tangent/=np.linalg.norm(tangent,axis=1)[:,None];side=np.column_stack((-tangent[:,1],tangent[:,0],np.zeros(len(path))))
 def pts(r):return np.array([[p+r*(math.cos(a)*s+math.sin(a)*np.array([0,0,1])) for a in np.arange(n)*2*np.pi/n] for p,s in zip(path,side)])
 outer=pts(ro);inner=pts(ri)
 def q(a,b,c,d):v.extend([[a,b,c],[a,c,d]])
 for j in range(len(path)-1):
  for i in range(n):
   k=(i+1)%n;q(outer[j,i],outer[j+1,i],outer[j+1,k],outer[j,k])
   if ri:q(inner[j,k],inner[j+1,k],inner[j+1,i],inner[j,i])
 for j in [0,len(path)-1]:
  for i in range(n):k=(i+1)%n;q(inner[j,i],outer[j,i],outer[j,k],inner[j,k])
 return v

# The plate and guides come from the native one-inch terminal subassembly.
for d in data['terminal']:
 v=np.frombuffer(base64.b64decode(d['data']),'<i2').astype(float).reshape(-1,3,3)/100
 add(v,d['net'],section=d['name']=='02',name='Native terminal '+d['name'])
ring(-55,0,12.7,11.2,'ground',y=-4.5,name='Tube section')
for z in [-5.4,5.4]:ring(-55,17,3,2,'hose',y=-8.1,z=z,section=False,name='Hose allowance')
# Internal coax and its two concentric conductors.
ring(-55,-18,2.5,1.85,'jacket',name='Internal jacket')
ring(-55,-10,1.85,1.6,'ground',name='Internal shield')
ring(-55,-10,1.6,.45,'insulator',name='Internal cable dielectric')
ring(-55,-10,.45,0,'live',section=False,name='Internal center conductor')
# Illustrative jack internals. These are explanatory profiles, not manufacturer CAD.
ring(-18,-10,3.24,1.85,'ground',name='Rear crimp ferrule')
ring(-10,0,3.175,2.05,'ground',name='Rear connector body')
ring(-3,0,4.619,3.175,'ground',n=6,name='Rear shoulder')
ring(0,11.4,3.175,2.05,'ground',name='Socket shell',flat=True)
ring(2,2.5,5.1,3.3,'ground',name='Mounting washer')
ring(2.5,4.1,4.619,3.25,'ground',n=6,name='Retaining nut')
ring(-10,11.4,2.05,.7,'insulator',name='Socket dielectric')
ring(-10,7.5,.7,0,'live',section=False,name='Female rear contact')
ring(7.5,11.4,.7,.45,'live',section=True,name='Female receptacle')
# External plug. Coupling nut surrounds the jack threads without touching the center contact.
ring(11.4,25,3.175,2.05,'ground',moving=True,name='Male outer contact')
coupling=ring(7.4,18,4.62,3.3,'ground',moving=True,n=6,name='Coupling nut')
ring(18,25,3.5,3.175,'ground',moving=True,name='Plug rear body')
ring(11.4,25,2.05,.45,'insulator',moving=True,name='Male dielectric')
ring(8,25,.45,0,'live',moving=True,section=False,name='Male center pin')
ring(25,28,3,1.85,'ground',moving=True,name='External cable ferrule')
ring(25,55,1.85,1.6,'ground',moving=True,name='External shield')
ring(25,55,1.6,.45,'insulator',moving=True,name='External cable dielectric')
ring(25,55,.45,0,'live',moving=True,section=False,name='External center')
ring(28,55,2.5,1.85,'jacket',moving=True,name='External jacket')

# Decimated original head bodies; colors identify electrical nodes rather than materials.
for d in data['head']:
 v=np.frombuffer(base64.b64decode(d['data']),'<i2').astype(float).reshape(-1,3,3)/100
 add(v,d['net'],model='head',section=not d['name'].startswith('AT M4'),name=d['name'])
ring(-65,-24,10,8,'ground',model='head',name='Grounded service tube')
ring(-65,-35,2.5,1.85,'jacket',y=4.5,model='head',name='Head cable jacket')
ring(-65,-33,1.85,1.6,'ground',y=4.5,model='head',name='Head shield')
ring(-34,-32,2.1,1.7,'ground',y=4.5,model='head',name='Concept shield clamp')
add(sweep([[-33,6.4,0],[-33,8.2,0]],.5),'ground',model='head',section=False,name='Concept shield bond')
u=np.linspace(0,1,45)[:,None];a=np.array([-33.,4.5,0]);b=np.array([-7.,4.5,0]);c=np.array([11.,16.2,0]);d=np.array([24.5,16.2,0]);curve=(1-u)**3*a+3*(1-u)**2*u*b+3*(1-u)*u**2*c+u**3*d
path=np.concatenate((np.array([[-65,4.5,0]]),curve))
add(sweep(path,1.6,.45),'insulator',model='head',name='Protected center dielectric')
wire=np.concatenate((path,np.array([[27.25,16.2,0]])))
add(sweep(wire,.45),'live',model='head',section=False,name='Center to live lug')
ring(27.14,27.45,3.3,2.1,'live',y=13.55,model='head',section=False,name='Concept live lug')

capture=vtk.vtkWindowToImageFilter();capture.SetInput(win);capture.SetInputBufferTypeToRGB();capture.ReadFrontBufferOff();capture.ShouldRerenderOff()
font=lambda n,b=False:ImageFont.truetype('C:/Windows/Fonts/'+('segoeuib.ttf' if b else 'segoeui.ttf'),n)
TITLE,BODY,LABEL,SMALL=font(40,True),font(28),font(25),font(19)
def smooth(t):t=max(0,min(1,t));return t*t*(3-2*t)
def wrap(draw,text,x,y,width,ft,color):
 line=''
 for word in text.split():
  q=(line+' '+word).strip()
  if line and draw.textlength(q,font=ft)>width:draw.text((x,y),line,font=ft,fill=color);y+=ft.size+10;line=word
  else:line=q
 draw.text((x,y),line,font=ft,fill=color);return y+ft.size+10
def frame(index,t,duration):
 u=t/duration;head=index>=5;cut=index>=2 or (index==1 and u>.20);gap=10 if index==0 else 16*(1-smooth((u-.10)/.56)) if index==1 else 0
 for r in records:
  a=r['actor'];a.SetVisibility(r['model']==('head' if head else 'main'))
  a.GetMapper().SetInputData(r['half'] if cut and r['section'] else r['poly']);a.SetPosition(gap if r['moving'] else 0,0,0);a.SetOrientation(0,0,0)
 coupling.SetOrientation(3*360*smooth((u-.67)/.26) if index==1 else 0,0,0)
 if head:focus=np.array([-1.,9.,0]);scale=65;direction=np.array([.32,.18,1])
 else:
  focus=np.array([3.,-1.,0]);scale=43;direction=np.array([.32,.22,1])
  if index==1:scale=29;focus=np.array([13.,0,0]);direction=np.array([.25,.22,1])
  if index==2:scale=14;focus=np.array([8.,0,0]);direction=np.array([.13,.22,1])
  if index==3:scale=17;focus=np.array([1.,0,0]);direction=np.array([.20+.08*math.sin(u*math.pi),.3,1])
  if index==4:scale=15;focus=np.array([-10.,0,0]);direction=np.array([-.15,.2,1])
 direction/=np.linalg.norm(direction);cam.SetFocalPoint(*focus);cam.SetPosition(*(focus+350*direction));cam.SetViewUp(0,1,0);cam.SetParallelScale(scale);cam.SetClippingRange(100,650)
 win.Render();capture.Modified();capture.Update();v=vtk_to_numpy(capture.GetOutput().GetPointData().GetScalars()).reshape(H,W-PANEL,3)
 im=Image.new('RGB',(W,H),'#101b2a');im.paste(Image.fromarray(np.flipud(v)),(PANEL,0));draw=ImageDraw.Draw(im);draw.rectangle((0,0,PANEL-1,H),fill='#1b2b3f')
 draw.text((28,30),'SMA / COAX / CATHODE',font=SMALL,fill='#adc5d8');y=wrap(draw,chapters[index]['title'],28,105,390,TITLE,'#f0f5fa')+35
 for text in chapters[index]['bullets']:
  draw.ellipse((29,y+10,36,y+17),fill='#83c7e1');y=wrap(draw,text,52,y,365,BODY,'#d9e7f1')+26
 for n,(net,text) in enumerate([('live','RF center / live cathode'),('ground','Shield / grounded structure'),('insulator','Solid dielectric / PTFE')]):
  yy=790+n*43;draw.rectangle((29,yy+5,44,yy+22),fill=tuple(int(c*255) for c in colors[net]));draw.text((58,yy),text,font=SMALL,fill='#d9e7f1')
 wrap(draw,'Colors identify electrical paths, not the original metal finishes.',28,949,390,SMALL,'#c1d1de')
 def label(text,p,xy,net=None):
  ren.SetWorldPoint(*p,1);ren.WorldToDisplay();x,y,z=ren.GetDisplayPoint();x+=PANEL;y=H-y;c=tuple(int(v*255) for v in colors[net]) if net else '#dce9f4'
  draw.line((x,y,xy[0],xy[1]+16),fill=c,width=2);draw.ellipse((x-4,y-4,x+4,y+4),fill=c);box=draw.textbbox(xy,text,font=LABEL);draw.rectangle((box[0]-6,box[1]-4,box[2]+6,box[3]+4),fill='#101b2a');draw.text(xy,text,font=LABEL,fill='#e6eff6')
 if index==0:
  label('External matchbox cable',[43+gap,0,2],(1260,200));label('Bulkhead SMA socket',[8,0,3],(1080,780));label('Internal coax',[-30,0,2],(540,190));label('Two coolant hoses',[12,-8.1,5.4],(1260,875))
 elif index==1:
  label('Male center pin',[8+gap,0,0],(1160,185),'live');label('Female socket',[11.4,0,0],(550,810),'live');label('Coupling nut rotates',[15+gap,4.3,0],(1210,865),'ground')
  text='PLUG APPROACHES' if u<.66 else 'COUPLING NUT TIGHTENS'
  draw.text((PANEL+30,112),text,font=SMALL,fill='#bcd2e2')
 elif index==2:
  label('Male pin inside female contact',[9,0,0],(1110,185),'live');label('To internal center conductor',[-8,0,0],(510,840),'live');label('Same RF electrical node',[21,0,0],(1280,850),'live')
 elif index==3:
  label('Connector dielectric',[4,1.4,0],(1200,170),'insulator');label('Coax dielectric',[-18,1.05,0],(510,840),'insulator');label('Outer shell is grounded',[7,-2.8,0],(1210,860),'ground')
 elif index==4:
  label('Center contact termination',[-10,0,0],(1190,170),'live');label('Shield-to-body termination',[-13,1.85,0],(1100,850),'ground');label('Internal cable dielectric',[-24,1.1,0],(510,850),'insulator')
 elif index==5:
  label('Proposed shield bond to ground',[-33,7.4,0],(510,190),'ground');label('Main PTFE isolation ring',[7,38,0],(1260,170),'insulator');label('Separate live terminal',[27.25,16.2,0],(1270,850),'live');label('Grounded bottom body',[-12,34,0],(510,850),'ground')
 else:
  label('Live cathode assembly',[40,30,0],(1260,190),'live');label('Insulated center route',[-3,10.5,0],(1260,870),'live');label('Shield returns to grounded structure',[-40,6.2,0],(500,855),'ground')
 note='SOURCE CAD HEAD / VIEW ROTATED / PROPOSED TERMINATION / SHIELDS AND MAGNETS HIDDEN' if head else 'NATIVE TERMINAL PLATE / ILLUSTRATIVE CONNECTOR INTERNALS / THREADS SIMPLIFIED'
 draw.text((PANEL+28,30),note,font=SMALL,fill='#a9bfd1')
 if cut:draw.text((PANEL+28,72),'CUTAWAY VIEW / NO ELECTRIC-FIELD OR VOLTAGE-RATING SIMULATION',font=SMALL,fill='#a9bfd1')
 draw.text((PANEL+28,H-48),f'{index+1:02} / {len(chapters):02}   '+chapters[index]['title'],font=SMALL,fill='#b2c8d9');draw.rectangle((PANEL,H-8,W,H),fill='#283b4d');draw.rectangle((PANEL,H-8,PANEL+int((W-PANEL)*u),H),fill='#76bfdc')
 return np.asarray(im)
def stamp(t):
 n=round(t*1000);return f'{n//3600000:02}:{n//60000%60:02}:{n//1000%60:02},{n%1000:03}'
if __name__=='__main__':
 if 'preview' in sys.argv:
  for i in range(len(chapters)):Image.fromarray(frame(i,13,20)).save(OUT/f'preview-{i:02}.jpg',quality=90)
  for t in [1,8,19]:Image.fromarray(frame(1,t,20)).save(OUT/f'mating-{t:02}.jpg',quality=90)
  win.Finalize();print('Previews ready');sys.exit()
 durations=[];audio=[];params=None
 for i in range(len(chapters)):
  with wave.open(str(OUT/f'voice-{i:02}.wav'),'rb') as f:p=f.getparams();raw=f.readframes(p.nframes)
  if params is None:params=p
  assert p[:3]==params[:3]
  duration=math.ceil((p.nframes/p.framerate+1.8)*FPS)/FPS;durations.append(duration);lead=round(.5*p.framerate);tail=round(duration*p.framerate)-lead-p.nframes;audio.append(bytes(lead*p.sampwidth*p.nchannels)+raw+bytes(tail*p.sampwidth*p.nchannels))
 with wave.open(str(OUT/'narration.wav'),'wb') as f:
  f.setparams(params)
  for a in audio:f.writeframes(a)
 writer=imageio_ffmpeg.write_frames(str(OUT/'silent.mp4'),(W,H),fps=FPS,codec='libx264',quality=8,macro_block_size=1,output_params=['-preset','fast']);writer.send(None)
 start=time.perf_counter();elapsed=0;timeline=[];subs=[]
 for i,(ch,duration) in enumerate(zip(chapters,durations)):
  timeline.append((elapsed,ch['title']));ss=[s.strip()+'.' for s in ch['speech'].split('.') if s.strip()];total=sum(map(len,ss));t=elapsed+.5
  for s in ss:
   end=t+(duration-1.8)*len(s)/total;subs.append(f'{len(subs)+1}\n{stamp(t)} --> {stamp(end)}\n{s}\n');t=end
  for n in range(round(duration*FPS)):writer.send(frame(i,n/FPS,duration))
  elapsed+=duration;print(f'{i+1}/{len(chapters)} rendered: {ch["title"]} ({duration:.1f}s)',flush=True)
 writer.close();win.Finalize();(OUT/'subtitles.srt').write_text('\n'.join(subs));meta=';FFMETADATA1\ntitle=SMA coax connection and electrical isolation\n';text=[]
 for i,(t,title) in enumerate(timeline):
  end=timeline[i+1][0] if i+1<len(timeline) else elapsed;meta+=f'[CHAPTER]\nTIMEBASE=1/1000\nSTART={round(t*1000)}\nEND={round(end*1000)}\ntitle={title}\n';text.extend([f'{int(t)//60}:{int(t)%60:02} {title}',chapters[i]['speech'],''])
 (OUT/'chapters.ffmeta').write_text(meta);(OUT/'Video transcript.txt').write_text('\n'.join(text));final=OUT/'SMA coax mating and electrical isolation - 3D explanation.mp4'
 subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-y','-v','error','-i',str(OUT/'silent.mp4'),'-i',str(OUT/'narration.wav'),'-i',str(OUT/'subtitles.srt'),'-i',str(OUT/'chapters.ffmeta'),'-map','0:v','-map','1:a','-map','2:s','-map_metadata','3','-map_chapters','3','-c:v','copy','-c:a','aac','-b:a','160k','-c:s','mov_text','-movflags','+faststart',str(final)],check=True)
 (OUT/'Render summary.json').write_text(json.dumps({'runtime_seconds':elapsed,'chapters':len(chapters),'resolution':[W,H],'fps':FPS,'render_seconds':time.perf_counter()-start,'file':str(final)},indent=2));print(f'COMPLETE {elapsed:.1f}s;render {time.perf_counter()-start:.1f}s',flush=True)
