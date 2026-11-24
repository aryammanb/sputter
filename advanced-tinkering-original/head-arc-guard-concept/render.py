import json,math,sys,wave,subprocess,importlib.util
from pathlib import Path
import vtk,numpy as np,imageio_ffmpeg
from vtk.util.numpy_support import vtk_to_numpy
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('base',P.parent/'render-full-assembly-video.py');b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
ren=b.renderer;win=b.window;cam=b.camera;ren.RemoveAllViewProps()
colors={'ground':(.30,.55,.69),'ptfe':(.70,.73,.69),'live':(.92,.43,.16),'ceramic':(.94,.88,.65),'guard':(.40,.76,.60)}
old=json.loads((P.parent/'screw-isolation-concept'/'geometry.json').read_text());new=json.loads((P/'geometry.json').read_text());chs=json.loads((P/'chapters.json').read_text());sets=[]
def section(poly):
 planes=vtk.vtkPlaneCollection()
 for origin,normal in [((0,0,0),(-1,0,0)),((0,-64,0),(0,-1,0))]:
  p=vtk.vtkPlane();p.SetOrigin(*origin);p.SetNormal(*normal);planes.AddItem(p)
 c=vtk.vtkClipClosedSurface();c.SetInputData(poly);c.SetClippingPlanes(planes);c.GenerateFacesOn();c.SetTolerance(1e-5);c.Update();result=vtk.vtkPolyData();result.ShallowCopy(c.GetOutput());return result
for group in [old,new]:
 actors=[]
 for j,q in enumerate(group):
  v=np.array(q['vertices']);poly=b.polydata(v[np.array(q['faces'])]);mapper=vtk.vtkPolyDataMapper();mapper.SetInputData(section(poly));a=vtk.vtkActor();a.SetMapper(mapper);a.GetProperty().SetColor(*colors[q['role']]);a.GetProperty().SetAmbient(.26);a.GetProperty().SetDiffuse(.7);a.GetProperty().SetSpecular(.18);ren.AddActor(a);actors.append(a)
 sets.append(actors)
def project(p):
 ren.SetWorldPoint(*p,1);ren.WorldToDisplay();x,y,_=ren.GetDisplayPoint();return x+b.PANEL,b.H-y
def frame(i,u):
 shift=-5*(1-min(1,u/.22)) if i==2 else (-5 if i==1 else 0)
 for k,actors in enumerate(sets):
  for j,a in enumerate(actors):a.SetVisibility(k==(0 if i==0 else 1));a.SetPosition(j*.0002,shift if j==8 else 0,0)
 focus=np.array([0.,-71.5 if i==0 else (-74 if i==1 else -73),0.]);scale=11.8 if i==0 else (15.2 if i==1 else 13.5)
 direction=np.array([1.,.05,.16+.025*math.sin(2*math.pi*u)]);cam.SetFocalPoint(*focus);cam.SetPosition(*(focus+300*direction));cam.SetViewUp(0,1,0);cam.SetParallelScale(scale);cam.SetClippingRange(150,500)
 win.Render();b.capture.Modified();b.capture.Update();a=vtk_to_numpy(b.capture.GetOutput().GetPointData().GetScalars()).reshape(b.H,b.W-b.PANEL,3)
 im=Image.new('RGB',(b.W,b.H),'#101b2a');im.paste(Image.fromarray(np.flipud(a)),(b.PANEL,0));d=ImageDraw.Draw(im);d.rectangle((0,0,b.PANEL-1,b.H),fill='#1b2b3f')
 d.text((28,30),'LIVE HEAD / ARC-GUARD CONCEPT',font=b.TINY,fill='#acc6da');y=b.wrap(d,chs[i]['title'],(28,100),395,b.TITLE,'#f0f6fa')+32
 for text in chs[i]['bullets']:
  d.ellipse((29,y+10,36,y+17),fill='#7fc6df');y=b.wrap(d,text,(53,y),370,b.BODY,'#d9e7f1')+24
 for n,(role,label) in enumerate([('live','Live metal screw and washer'),('ground','Grounded Boden'),('ceramic','Ceramic bearing insulation'),('guard','PTFE guard and cover')]):
  yy=790+n*36;d.rectangle((29,yy+4,43,yy+20),fill=tuple(int(c*255) for c in colors[role]));d.text((56,yy),label,font=b.TINY,fill='#d8e8f2')
 b.wrap(d,'Dimensional study. Not a discharge simulation or a rated anti-arcing assembly.',(28,965),395,b.TINY,'#ddca8b')
 def label(text,p,xy):
  x,y=project(p);d.line((x,y,xy[0],xy[1]+15),fill='#b8cedc',width=2);d.ellipse((x-4,y-4,x+4,y+4),fill='#dceaf4');box=d.textbbox(xy,text,font=b.SMALL);d.rectangle((box[0]-5,box[1]-4,box[2]+5,box[3]+4),fill='#101b2a');d.text(xy,text,font=b.SMALL,fill='#edf3f7')
 if i==0:
  label('Grounded pocket wall',[0,-73,6],(500,220));label('Exposed LIVE screw head',[0,-73,-2.75],(1280,870));label('Under-head insulation only',[0,-69.2,4.6],(1240,220))
  pts=[project([0,-73+(k%2-.5)*.35,2.75+(6-2.75)*k/10]) for k in range(11)];d.line(pts,fill='#ff6572',width=5)
  label('Reported problem gap',[0,-73,4.4],(500,870))
 else:
  label('Ground stays outside the guard',[0,-72,-7],(1280,220));label('PTFE wall surrounds live head',[0,-73,5],(500,220));label('Ceramic washer carries bearing load',[0,-69.2,-4.3],(1190,410))
  if i==1:
   label('Cap removed for tool access',[0,-79+shift,0],(500,910));label('LIVE head recessed inside',[0,-73,2],(1250,710))
  else:
   label('Removable insulating cap',[0,-79,-4],(1230,870));label('Offset pump-out vent',[0,-79,2.2],(500,870));label('Head remains metal and LIVE',[0,-73,2.2],(500,650))
 d.text((490,30),'LOCAL SECTION AT AN EXISTING FASTENER / SOURCE GEOMETRY + PROPOSED PARTS',font=b.TINY,fill='#b2c9da')
 d.text((490,72),'RED PATH IS ILLUSTRATIVE / NOT A DISCHARGE SIMULATION' if i==0 else 'THREADS REPRESENTED BY NOMINAL ENVELOPES / NOT MANUFACTURING DRAWINGS',font=b.TINY,fill='#b2c9da')
 d.text((490,1035),f'{i+1:02} / 03   '+chs[i]['title'],font=b.TINY,fill='#b2c9da');return np.asarray(im)
if __name__=='__main__':
 if 'preview' in sys.argv:
  ims=[]
  for i in range(3):
   im=Image.fromarray(frame(i,.65));im.save(P/f'View {i+1}.png');ims.append(im)
  poster=Image.new('RGB',(1920,900),'#101b2a');d=ImageDraw.Draw(poster)
  d.text((28,18),'PREVIOUS CONCEPT: EXPOSED LIVE HEAD',font=b.BODY,fill='#f0f6fa');d.text((988,18),'PROPOSED: INSULATING GUARD + VENTED CAP',font=b.BODY,fill='#f0f6fa')
  for j,i in enumerate([0,2]):poster.paste(ims[i].crop((460,95,1920,1020)).resize((960,730)),(960*j,72))
  d.text((28,825),'Orange = live metal     Blue = ground     Cream = ceramic     Green = insulating PTFE enclosure',font=b.BODY,fill='#d9e7f1')
  d.text((28,867),'Concept for reducing exposed-head discharge paths; RF/pressure testing and final dimensions still required.',font=b.TINY,fill='#ddca8b');poster.save(P/'Exposed head versus guarded head.png');win.Finalize();sys.exit()
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
 writer.close();win.Finalize();final=P/'Protecting the live screw head - 3D explanation.mp4'
 subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-y','-v','error','-i',str(P/'silent.mp4'),'-i',str(P/'Narration.wav'),'-map','0:v','-map','1:a','-c:v','copy','-c:a','aac','-b:a','160k','-movflags','+faststart',str(final)],check=True)
 (P/'Video summary.json').write_text(json.dumps({'video':str(final),'duration_seconds':sum(durations),'chapter_durations_seconds':durations,'fps':fps,'resolution':[1920,1080]},indent=2));print(str(final),flush=True)
