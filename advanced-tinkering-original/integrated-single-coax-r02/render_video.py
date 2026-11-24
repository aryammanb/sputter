import importlib.util,json,math,struct,sys,time,wave,subprocess
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
import vtk,imageio_ffmpeg
from vtk.util.numpy_support import vtk_to_numpy

P=Path(__file__).resolve().parent;OUT=P/'video';OUT.mkdir(exist_ok=True)
spec=importlib.util.spec_from_file_location('base',P.parent/'render-full-assembly-video.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
m.renderer.RemoveAllViewProps();ren=m.renderer;window=m.window;camera=m.camera
W,H,PANEL,FPS=m.W,m.H,m.PANEL,15
chapters=json.loads((P/'video-chapters.json').read_text());metadata=json.loads((P/'render-parts.json').read_text());lookup={q['name']:q for q in metadata}
colors={'live':(.89,.49,.24),'ground':(.40,.60,.70),'insulator':(.92,.89,.76),'jacket':(.18,.21,.26),'water':(.12,.39,.77),'seal':(.09,.14,.12),'outermag':(.77,.23,.25),'centermag':(.22,.39,.77)}
records=[]
with (P/'integrated-mesh.bin').open('rb') as f:
 while name:=m.part_string(f):
  file=m.part_string(f);n=struct.unpack('<i',f.read(4))[0];v=np.frombuffer(f.read(n*36),'<f4').reshape(-1,3,3).astype(float);q=lookup[name];poly=m.polydata(v);mapper=vtk.vtkPolyDataMapper();mapper.SetInputData(poly);mapper.ScalarVisibilityOff();a=vtk.vtkActor();a.SetMapper(mapper);a.GetProperty().SetColor(*colors[q['net']]);a.GetProperty().SetAmbient(.24);a.GetProperty().SetDiffuse(.68);a.GetProperty().SetSpecular(.25);a.GetProperty().SetSpecularPower(30);ren.AddActor(a)
  records.append({'name':name,'file':file,'net':q['net'],'new':q['kind'].startswith('R02'),'poly':poly,'actor':a,'mapper':mapper,'variants':{'full':poly},'current':'full'})
assert len(records)==129
capture=m.capture
def sm(t):t=max(0,min(1,t));return t*t*(3-2*t)
def mode(index,u,r):
 f=r['file'];new=r['new'];show=True;half=False;trim=False
 shield=f in ['Groundshield Rohr.SLDPRT','Dunkelraumabschirmung.SLDPRT'] or (f.startswith('AT M3x6') or f.startswith('AT M4x8'))
 coax=new and any(s in f for s in ['coax','dielectric','RF center'])
 if index==1:
  show=new and not any(s in f for s in ['Boden -','service tube','Ground carrier','ground anchor','mounting screw','clamp nut','Copper terminal','M4x20','TE323086'])
  half=coax;trim=True
 elif index==2:
  show=(new and not any(s in f for s in ['Copper terminal','M4x20','TE323086','service tube'])) or f=='Isolator.SLDPRT'
  half=('Boden -' in f or f=='Isolator.SLDPRT' or coax);trim=True
 elif index==3:
  show=(new and not any(s in f for s in ['Boden -','Ground carrier','ground anchor','mounting screw','clamp nut','icotek','service tube'])) or f in ['Backplate.SLDPRT','Kuehlkoerper.SLDPRT','Magnet Joke.SLDPRT','Abstandshalter.SLDPRT'] or ('fitting' in f)
  half=f in ['Backplate.SLDPRT','Kuehlkoerper.SLDPRT','Magnet Joke.SLDPRT','Abstandshalter.SLDPRT'] or coax;trim=True
 elif index==4:
  show=not shield;half=(f in ['Backplate.SLDPRT','Kuehlkoerper.SLDPRT','Magnet Joke.SLDPRT','Abstandshalter.SLDPRT','Isolator.SLDPRT'] or 'Boden -' in f or 'service tube' in f or coax);trim=True
 elif index==5 and u<.55:
  half=f in ['Groundshield Rohr.SLDPRT','Dunkelraumabschirmung.SLDPRT','Backplate.SLDPRT','Kuehlkoerper.SLDPRT','Magnet Joke.SLDPRT','Abstandshalter.SLDPRT','Isolator.SLDPRT'] or 'Boden -' in f or 'service tube' in f or coax;trim=True
 return show,half,trim
def pose(index,u):
 focus=np.array([0.,-40.,0]);scale=88;az=1.22;el=.10
 if index==0:focus[1]=-147;scale=188;az=.7+.35*u
 if index==1:focus[1]=-53;focus[2]=-3;scale=36;az=1.5;el=.20
 if index==2:focus[1]=-54;focus[2]=-10;scale=36;az=1.50;el=.16
 if index==3:focus[1]=-32;focus[2]=9;scale=42;az=1.40;el=-.20
 if index==4:az=1.37;el=.12;scale=84
 if index==5:
  q=sm((u-.57)/.32);focus[1]=-40-107*q;scale=88+100*q;az=1.37-.45*q
 if index in [1,2,3,4]:az+=.12*math.sin(2*math.pi*u)
 direction=np.array([math.sin(az)*math.cos(el),math.sin(el),math.cos(az)*math.cos(el)]);camera.SetFocalPoint(*focus);camera.SetPosition(*(focus+1000*direction));camera.SetViewUp(0,1,0);camera.SetRoll(0);camera.SetParallelScale(scale);camera.SetClippingRange(500,1600)
def frame(index,t,duration):
 u=t/duration
 for r in records:
  show,half,trim=mode(index,u,r);a=r['actor'];a.SetVisibility(show)
  if not show:continue
  a.GetProperty().SetOpacity(.20 if index==3 and r['file'] in ['Magnet Joke.SLDPRT','Abstandshalter.SLDPRT','Kuehlkoerper.SLDPRT','Backplate.SLDPRT'] else (.45 if index==2 and r['file']=='Isolator.SLDPRT' else 1.))
  key=('half' if half else '')+('trim' if trim else '') or 'full'
  if key not in r['variants']:r['variants'][key]=m.clipped(r['poly'],half,trim)
  if r['current']!=key:r['mapper'].SetInputData(r['variants'][key]);r['current']=key
 pose(index,u);window.Render();capture.Modified();capture.Update();v=vtk_to_numpy(capture.GetOutput().GetPointData().GetScalars()).reshape(H,W-PANEL,3);im=Image.new('RGB',(W,H),'#101b2a');im.paste(Image.fromarray(np.flipud(v)),(PANEL,0));draw=ImageDraw.Draw(im);draw.rectangle((0,0,PANEL-1,H),fill='#1b2b3f')
 draw.text((28,30),'INTEGRATED SINGLE COAX / R02',font=m.TINY,fill='#adc6d8');y=m.wrap(draw,chapters[index]['title'],(28,100),395,m.TITLE,'#f0f6fa')+35
 for text in chapters[index]['bullets']:
  draw.ellipse((29,y+10,36,y+17),fill='#7fc6df');y=m.wrap(draw,text,(53,y),370,m.BODY,'#d9e7f1')+25
 for n,(net,label) in enumerate([('live','RF center / live head'),('ground','Shield / grounded body'),('insulator','Dielectric / PTFE'),('water','Coolant hoses')]):
  yy=780+n*37;draw.rectangle((29,yy+5,43,yy+21),fill=tuple(int(c*255) for c in colors[net]));draw.text((56,yy),label,font=m.TINY,fill='#d8e8f2')
 m.wrap(draw,'Mechanical integration study. Clamp and ring-lug shapes are catalogue-size representations.',(28,960),395,m.TINY,'#d9c586')
 def label(text,p,xy,net=None):
  ren.SetWorldPoint(*p,1);ren.WorldToDisplay();x,y,z=ren.GetDisplayPoint();x+=PANEL;y=H-y;c=tuple(int(v*255) for v in colors[net]) if net else '#dce9f4';draw.line((x,y,xy[0],xy[1]+15),fill=c,width=2);draw.ellipse((x-4,y-4,x+4,y+4),fill=c);box=draw.textbbox(xy,text,font=m.SMALL);draw.rectangle((box[0]-5,box[1]-4,box[2]+5,box[3]+4),fill='#101b2a');draw.text(xy,text,font=m.SMALL,fill='#e6eff6')
 if index==0:
  label('Original head stack retained',[0,-20,46],(1280,170));label('25.4 mm service tube',[12.7,-200,0],(1240,680));label('One continuous coax',[0,-300,-4.5],(650,925))
 elif index==1:
  label('Jacket ends here',[0,-53.5,-7.5],(530,190));label('9 mm exposed shield band',[1.85,-49,-7.5],(1240,170),'ground');label('Protected center / quarter-turn',[0,-39,-5.5],(1230,850),'insulator');label('Clamp sized for 3-6 mm shield',[5.9,-48.5,-4],(530,850),'ground')
 elif index==2:
  label('SKL3-6 catalogue envelope',[5.9,-48.5,-4],(1200,180),'ground');label('M3 clamp screw and nut',[0,-48.5,-14.3],(530,850),'ground');label('Ground carrier / saddle',[0,-56,-18],(1260,850),'ground');label('Blind M3 anchor in Boden',[0,-58,-22],(530,190),'ground')
 elif index==3:
  label('Copper stand-off through D8 passage',[0,-27,13.55],(1210,180),'live');label('Ring terminal behind the yoke',[0,-35.4,13.55],(530,850),'live');label('M4 x20 terminal screw',[0,-38,13.55],(1260,850),'live');label('Cable enters terminal barrel',[0,-36.565,1.33],(530,190),'live')
 elif index==4:
  label('Shield connection stays on Boden',[0,-49,-7.5],(530,850),'ground');label('Center connects to live Backplate',[0,-35.4,13.55],(1260,850),'live');label('Main PTFE isolation',[0,-43.5,37],(1280,170),'insulator');label('Coolant hoses retained',[10,-49,0],(530,190),'water')
 elif u<.55:
  label('Integrated head cutaway',[0,-35,13.55],(1260,850));label('Original water-seal joints retained',[18,-10,0],(530,170))
 else:label('129 component instances',[0,-20,45],(1250,170))
 draw.text((PANEL+28,30),'INTEGRATED STEP GEOMETRY / SOURCE PARTS + R02 PARTS / NOT A VOLTAGE OR COOLING QUALIFICATION',font=m.TINY,fill='#acc2d3')
 if index in [1,2,3,4] or (index==5 and u<.55):draw.text((PANEL+28,73),'SECTIONED / LONG SERVICE ROUTES CROPPED WHERE NEEDED',font=m.TINY,fill='#acc2d3')
 draw.text((PANEL+28,H-48),f'{index+1:02} / 06   '+chapters[index]['title'],font=m.TINY,fill='#b2c8d9');draw.rectangle((PANEL,H-8,W,H),fill='#283b4d');draw.rectangle((PANEL,H-8,PANEL+int((W-PANEL)*u),H),fill='#75bfdc');return np.asarray(im)
def stamp(t):
 n=round(t*1000);return f'{n//3600000:02}:{n//60000%60:02}:{n//1000%60:02},{n%1000:03}'
if __name__=='__main__':
 if 'preview' in sys.argv:
  for i in range(6):Image.fromarray(frame(i,13,20)).save(OUT/f'preview-{i:02}.jpg',quality=90)
  window.Finalize();print('Six integrated views ready');sys.exit()
 durations=[];chunks=[];params=None
 for i in range(6):
  with wave.open(str(OUT/f'voice-{i:02}.wav'),'rb') as f:p=f.getparams();raw=f.readframes(p.nframes)
  if params is None:params=p
  duration=math.ceil((p.nframes/p.framerate+1.8)*FPS)/FPS;durations.append(duration);lead=round(.5*p.framerate);tail=round(duration*p.framerate)-lead-p.nframes;chunks.append(bytes(lead*p.sampwidth*p.nchannels)+raw+bytes(tail*p.sampwidth*p.nchannels))
 with wave.open(str(OUT/'narration.wav'),'wb') as f:
  f.setparams(params)
  for q in chunks:f.writeframes(q)
 writer=imageio_ffmpeg.write_frames(str(OUT/'silent.mp4'),(W,H),fps=FPS,codec='libx264',quality=8,macro_block_size=1,output_params=['-preset','fast']);writer.send(None);elapsed=0;timeline=[];subs=[];start=time.perf_counter()
 for i,(ch,duration) in enumerate(zip(chapters,durations)):
  timeline.append((elapsed,ch['title']));ss=[s.strip()+'.' for s in ch['speech'].split('.') if s.strip()];length=sum(map(len,ss));t=elapsed+.5
  for s in ss:
   end=t+(duration-1.8)*len(s)/length;subs.append(f'{len(subs)+1}\n{stamp(t)} --> {stamp(end)}\n{s}\n');t=end
  for n in range(round(duration*FPS)):writer.send(frame(i,n/FPS,duration))
  elapsed+=duration;print(f'{i+1}/6 rendered: {ch["title"]} ({duration:.1f}s)',flush=True)
 writer.close();window.Finalize();(OUT/'subtitles.srt').write_text('\n'.join(subs));meta=';FFMETADATA1\ntitle=Integrated single coax magnetron R02\n';transcript=[]
 for i,(t,title) in enumerate(timeline):
  end=timeline[i+1][0] if i<5 else elapsed;meta+=f'[CHAPTER]\nTIMEBASE=1/1000\nSTART={round(t*1000)}\nEND={round(end*1000)}\ntitle={title}\n';transcript.extend([f'{int(t)//60}:{int(t)%60:02} {title}',chapters[i]['speech'],''])
 (OUT/'chapters.ffmeta').write_text(meta);(OUT/'Video transcript.txt').write_text('\n'.join(transcript));final=OUT/'Integrated single coax magnetron R02 - 3D assembly explanation.mp4'
 subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-y','-v','error','-i',str(OUT/'silent.mp4'),'-i',str(OUT/'narration.wav'),'-i',str(OUT/'subtitles.srt'),'-i',str(OUT/'chapters.ffmeta'),'-map','0:v','-map','1:a','-map','2:s','-map_metadata','3','-map_chapters','3','-c:v','copy','-c:a','aac','-b:a','160k','-c:s','mov_text','-movflags','+faststart',str(final)],check=True)
 (OUT/'Render summary.json').write_text(json.dumps({'runtime_seconds':elapsed,'chapters':6,'components':len(records),'resolution':[W,H],'fps':FPS,'render_seconds':time.perf_counter()-start,'video':str(final)},indent=2));print(f'COMPLETE {elapsed:.1f}s; render {time.perf_counter()-start:.1f}s',flush=True)
