import json,math,sys,wave,subprocess,importlib.util
from pathlib import Path
import vtk,numpy as np,imageio_ffmpeg
from vtk.util.numpy_support import vtk_to_numpy
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('base',P.parent/'render-full-assembly-video.py');b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
ren=b.renderer;win=b.window;cam=b.camera;ren.RemoveAllViewProps()
colors={'ground':(.30,.55,.69),'ptfe':(.70,.73,.69),'live':(.92,.43,.16),'ceramic':(.94,.88,.65)}
data=json.loads((P/'geometry.json').read_text());chs=json.loads((P/'chapters.json').read_text());actors=[]
for q in data:
 v=np.array(q['vertices']);poly=b.polydata(v[np.array(q['faces'])]);mapper=vtk.vtkPolyDataMapper();mapper.SetInputData(b.clipped(poly,True,False));a=vtk.vtkActor();a.SetMapper(mapper);a.GetProperty().SetColor(*colors[q['role']]);a.GetProperty().SetAmbient(.25);a.GetProperty().SetDiffuse(.7);a.GetProperty().SetSpecular(.2);ren.AddActor(a);actors.append((a,mapper,poly))
def smooth(u):u=max(0,min(1,u));return u*u*(3-2*u)
def frame(i,u):
 exploded=i==1;moving=smooth(min(u/.15,(1-u)/.15)) if exploded else 0
 zs=[0,0,0,19,4,-10,-27];ys=[0,0,0,13,15.5,16,16]
 for j,(a,mapper,p) in enumerate(actors):
  a.SetVisibility(not exploded or j>=3)
  a.SetPosition(0,moving*ys[j],moving*zs[j]);mapper.SetInputData(p if exploded else b.clipped(p,True,False))
  a.GetProperty().SetOpacity(1)
 focus=np.array([0.,-40. if exploded else -54.,-5. if exploded else 0.]);scale=31.5 if exploded else 25
 direction=np.array([1.,-.20 if exploded else .08,.20+.06*math.sin(u*2*math.pi)])
 cam.SetFocalPoint(*focus);cam.SetPosition(*(focus+300*direction));cam.SetViewUp(0,1,0);cam.SetParallelScale(scale);cam.SetClippingRange(150,500)
 win.Render();b.capture.Modified();b.capture.Update();a=vtk_to_numpy(b.capture.GetOutput().GetPointData().GetScalars()).reshape(b.H,b.W-b.PANEL,3)
 im=Image.new('RGB',(b.W,b.H),'#101b2a');im.paste(Image.fromarray(np.flipud(a)),(b.PANEL,0));d=ImageDraw.Draw(im);d.rectangle((0,0,b.PANEL-1,b.H),fill='#1b2b3f')
 d.text((28,30),'SCREW ISOLATION / LOCAL CONCEPT',font=b.TINY,fill='#acc6da');y=b.wrap(d,chs[i]['title'],(28,100),395,b.TITLE,'#f0f6fa')+32
 for text in chs[i]['bullets']:
  d.ellipse((29,y+10,36,y+17),fill='#7fc6df');y=b.wrap(d,text,(53,y),370,b.BODY,'#d9e7f1')+24
 for n,(role,label) in enumerate([('live','Live metal: spacer + screw'),('ground','Grounded Boden'),('ceramic','Alumina insulation'),('ptfe','Existing PTFE seal ring')]):
  yy=790+n*36;d.rectangle((29,yy+4,43,yy+20),fill=tuple(int(c*255) for c in colors[role]));d.text((56,yy),label,font=b.TINY,fill='#d8e8f2')
 b.wrap(d,'Concept only. Not a released ceramic part, torque specification or voltage rating.',(28,965),395,b.TINY,'#ddca8b')
 def label(text,p,xy,j=None):
  pos=np.array(p,dtype=float)
  if j is not None:pos+=np.array([0,moving*ys[j],moving*zs[j]])
  ren.SetWorldPoint(*pos,1);ren.WorldToDisplay();x,y,_=ren.GetDisplayPoint();x+=b.PANEL;y=b.H-y;d.line((x,y,xy[0],xy[1]+15),fill='#b8cedc',width=2);d.ellipse((x-4,y-4,x+4,y+4),fill='#dceaf4');box=d.textbbox(xy,text,font=b.SMALL);d.rectangle((box[0]-5,box[1]-4,box[2]+5,box[3]+4),fill='#101b2a');d.text(xy,text,font=b.SMALL,fill='#edf3f7')
 if exploded:
  label('Alumina tube: shank insulation',[0,-57,2.8],(500,240),3)
  label('Alumina washer: head insulation',[0,-69.3,5.8],(500,940),4)
  label('Small metal load washer',[0,-70.75,3.5],(1130,940),5)
  label('Metal screw; no polymer threads',[0,-58,1.5],(1430,240),6)
 else:
  label('LIVE spacer: screw threads here',[0,-38,1.4],(1200,170))
  label('Main PTFE ring remains',[0,-43.5,5],(500,170))
  label('Ceramic tube around live shank',[0,-56,2.1],(1210,485))
  label('GROUNDED body',[0,-60,-6],(500,485))
  label('Ceramic washer on flat seat',[0,-69.25,4.5],(500,890))
  label('Head and metal washer remain LIVE',[0,-72.5,2.1],(1180,890))
 d.text((490,30),'ACTUAL SOURCE GEOMETRY CROPPED AROUND ONE FASTENER / PROPOSED CERAMIC PARTS',font=b.TINY,fill='#b2c9da')
 d.text((490,72),'SIDEWAYS EXPLODED VIEW / NOT A REMOVAL PATH' if exploded else 'SECTION THROUGH SCREW AXIS / THREAD HELIX OMITTED',font=b.TINY,fill='#b2c9da')
 d.text((490,1035),f'{i+1:02} / 03   '+chs[i]['title'],font=b.TINY,fill='#b2c9da');return np.asarray(im)
if __name__=='__main__':
 if 'preview' in sys.argv:
  for i in range(3):Image.fromarray(frame(i,.5)).save(P/f'View {i+1}.png')
  win.Finalize();sys.exit()
 fps=15;durations=[];audio=[];params=None
 for i in range(3):
  with wave.open(str(P/f'voice-{i}.wav'),'rb') as f:p=f.getparams();raw=f.readframes(p.nframes)
  params=p;dur=math.ceil((p.nframes/p.framerate+1.5)*fps)/fps;durations.append(dur);audio.append(bytes(round(.5*p.framerate)*2)+raw+bytes((round(dur*p.framerate)-round(.5*p.framerate)-p.nframes)*2))
 with wave.open(str(P/'Narration.wav'),'wb') as f:
  f.setparams(params)
  for q in audio:f.writeframes(q)
 writer=imageio_ffmpeg.write_frames(str(P/'silent.mp4'),(1920,1080),fps=fps,codec='libx264',quality=8,macro_block_size=1,output_params=['-preset','fast']);writer.send(None)
 for i,dur in enumerate(durations):
  for n in range(round(dur*fps)):writer.send(frame(i,n/(round(dur*fps)-1)))
  print(f'{i+1}/3 rendered ({dur:.1f}s)',flush=True)
 writer.close();win.Finalize();final=P/'Metal screws with ceramic isolation - 3D explanation.mp4'
 subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-y','-v','error','-i',str(P/'silent.mp4'),'-i',str(P/'Narration.wav'),'-map','0:v','-map','1:a','-c:v','copy','-c:a','aac','-b:a','160k','-movflags','+faststart',str(final)],check=True)
 (P/'Video summary.json').write_text(json.dumps({'video':str(final),'duration_seconds':sum(durations),'chapter_durations_seconds':durations,'fps':fps,'resolution':[1920,1080]},indent=2));print(str(final),flush=True)
