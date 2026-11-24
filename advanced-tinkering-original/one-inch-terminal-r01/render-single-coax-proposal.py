import importlib.util,json,math,subprocess,time,wave
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
from vtk.util.numpy_support import vtk_to_numpy
import imageio_ffmpeg

P=Path(__file__).resolve().parent;OUT=P/'single-coax-proposal';OUT.mkdir(exist_ok=True)
spec=importlib.util.spec_from_file_location('coax',P/'render-coax-video.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
native_names={'Boden.SLDPRT','Isolator.SLDPRT','Abstandshalter.SLDPRT','Backplate.SLDPRT','Kuehlkoerper.SLDPRT','Grounded service tube'}
for r in m.records:
 keep=r['model']=='head' and (r['name'] in native_names or r['name'].startswith('AT M4'))
 r['actor'].SetVisibility(keep)
 if keep:r['actor'].GetMapper().SetInputData(r['half'] if r['section'] else r['poly'])
first=len(m.records)
m.ring(-75,-14,2.5,1.85,'jacket',y=4.5,model='single',name='One continuous coax jacket')
m.ring(-75,-10,1.85,1.6,'ground',y=4.5,model='single',name='Outer shield')
m.ring(-12,-10,2.15,1.7,'ground',y=4.5,model='single',section=False,name='Proposed circumferential shield clamp')
# Wide foil strap conforms to the source cone: inner radius = axial X +30.
def prism_xy(points,z0,z1):
 v=[];a=[np.array([x,y,z0]) for x,y in points];b=[np.array([x,y,z1]) for x,y in points]
 for i in range(1,len(a)-1):v.extend([[a[0],a[i+1],a[i]],[b[0],b[i],b[i+1]]])
 for i in range(len(a)):
  j=(i+1)%len(a);v.extend([[a[i],a[j],b[j]],[a[i],b[j],b[i]]])
 return v
m.add(prism_xy([[-14,6.6],[-6,6.6],[-6,24],[-14,16]],-.4,.4),'ground',model='single',section=False,name='Wide ground strap')
# Bent saddle foot lies on the actual conical surface; the anchor crosses it normally.
xs=np.linspace(-14,-6,9);zs=np.linspace(-3,3,7);foot=[]
outer=np.array([[[x,math.sqrt((x+30)**2-z*z),z] for z in zs] for x in xs])
normal_grid=np.array([[[-1,p[1]/(p[0]+30),p[2]/(p[0]+30)] for p in row] for row in outer])/math.sqrt(2);inner=outer-.8*normal_grid
def fq(a,b,c,d):foot.extend([[a,b,c],[a,c,d]])
for i in range(len(xs)-1):
 for j in range(len(zs)-1):
  fq(outer[i,j],outer[i+1,j],outer[i+1,j+1],outer[i,j+1]);fq(inner[i,j+1],inner[i+1,j+1],inner[i+1,j],inner[i,j])
for i in range(len(xs)-1):
 for j in [0,len(zs)-1]:fq(outer[i,j],inner[i,j],inner[i+1,j],outer[i+1,j])
for j in range(len(zs)-1):
 for i in [0,len(xs)-1]:fq(outer[i,j],outer[i,j+1],inner[i,j+1],inner[i,j])
m.add(foot,'ground',model='single',section=False,name='Conforming ground saddle foot')
point=np.array([-10.,20.,0]);normal=np.array([-1.,1.,0])/math.sqrt(2)
m.add(m.sweep([point-2*normal,point+3.5*normal],1.5),'ground',model='single',section=False,name='Blind anchor nominal shaft')
m.add(m.sweep([point-4.5*normal,point-2*normal],2.75),'ground',model='single',section=False,name='Blind anchor screw head')
u=np.linspace(0,1,45)[:,None];a=np.array([-10.,4.5,0]);b=np.array([0.,4.5,0]);c=np.array([13.,16.2,0]);d=np.array([24.5,16.2,0]);curve=(1-u)**3*a+3*(1-u)**2*u*b+3*(1-u)*u**2*c+u**3*d
path=np.concatenate((np.array([[-75,4.5,0]]),curve))
m.add(m.sweep(path,1.6,.45),'insulator',model='single',name='Center conductor dielectric')
m.add(m.sweep(np.concatenate((path,[[27.25,16.2,0]])),.45),'live',model='single',section=False,name='RF center conductor')
m.ring(27.14,27.45,3.3,2.1,'live',y=13.55,model='single',section=False,name='Live terminal lug')
for r in m.records[first:]:
 r['actor'].SetVisibility(True);r['actor'].GetMapper().SetInputData(r['half'] if r['section'] else r['poly'])
 if r['name'] in ['Wide ground strap','Conforming ground saddle foot','Proposed circumferential shield clamp']:
  r['actor'].GetProperty().SetColor(.52,.76,.85);r['actor'].GetProperty().EdgeVisibilityOff()
 if r['name'].startswith('Blind anchor'):r['actor'].GetProperty().SetColor(.65,.74,.79)

chapters=[
 {'title':'One cable; two different terminations','bullets':['Coax enters the atmospheric tube directly','Outer shield bonds to grounded Boden','Insulated center reaches the live Backplate'], 'speech':'Here is the simpler proposal with one continuous coax cable. It enters through the atmospheric service tube. There is no additional S M A connector on the gun. The blue gray path is the grounded shield and structure. The orange path is the R F center conductor and live cathode assembly. The cream colored material provides electrical insulation. The two coolant hoses are hidden so we can inspect the electrical terminations.'},
 {'title':'Ground connection: shield to Boden','bullets':['Circumferential clamp on exposed shield','Short, wide strap to the grounded bottom body','New blind anchor stays inside the dry cavity'], 'speech':'At the grounded bottom body, expose a short section of the cable shield and capture it with a circumferential conductive clamp. A short, wide metal strap bonds that clamp to the inner surface of the grounded Boden. The proposed anchor is blind and stays inside the dry cavity; its final depth and position must be checked against the original holes and sealing surfaces. This is the shield connection. It does not attach to the live spacer or copper head.'},
 {'title':'RF connection: center to copper terminal','bullets':['Shield ends on the grounded side','Inner dielectric protects the continuing center','Ring lug connects at the separate live M4 terminal'], 'speech':'The center conductor continues beyond the shield termination with its dielectric protection intact. It curves through the open central space to the existing live terminal on the copper Backplate. A secure ring lug replaces a loose wire hook at that terminal. Only the short terminal connection is exposed. The main P T F E ring separates the live spacer from the grounded bottom body. This is a proposed mechanical route; conductor protection, R F voltage clearance and cable ratings still need final design.'}
]
(OUT/'chapters.json').write_text(json.dumps(chapters,indent=2))
font=m.font
def frame(index,u):
 focus=np.array([-1.,9.,0]);scale=66;direction=np.array([.32,.18,1])
 if index==1:focus=np.array([-10.,13.,0]);scale=23;direction=np.array([.30,.30,1])
 if index==2:focus=np.array([23.,16.,0]);scale=27;direction=np.array([.36,.15,1])
 direction[0]+=.035*math.sin(u*math.pi*2);direction/=np.linalg.norm(direction);m.cam.SetFocalPoint(*focus);m.cam.SetPosition(*(focus+350*direction));m.cam.SetViewUp(0,1,0);m.cam.SetParallelScale(scale);m.cam.SetClippingRange(100,650)
 m.win.Render();m.capture.Modified();m.capture.Update();v=vtk_to_numpy(m.capture.GetOutput().GetPointData().GetScalars()).reshape(m.H,m.W-m.PANEL,3)
 im=Image.new('RGB',(m.W,m.H),'#101b2a');im.paste(Image.fromarray(np.flipud(v)),(m.PANEL,0));draw=ImageDraw.Draw(im);draw.rectangle((0,0,m.PANEL-1,m.H),fill='#1b2b3f')
 draw.text((28,30),'SINGLE-COAX PROPOSAL',font=m.SMALL,fill='#b1cadc');y=m.wrap(draw,chapters[index]['title'],28,105,390,m.TITLE,'#f0f5fa')+35
 for text in chapters[index]['bullets']:draw.ellipse((29,y+10,36,y+17),fill='#82c5df');y=m.wrap(draw,text,52,y,365,m.BODY,'#d9e7f1')+26
 for i,(net,label) in enumerate([('live','RF center / live head'),('ground','Shield / grounded body'),('insulator','Dielectric / main PTFE ring')]):
  yy=790+i*43;draw.rectangle((29,yy+5,44,yy+22),fill=tuple(int(c*255) for c in m.colors[net]));draw.text((58,yy),label,font=m.SMALL,fill='#d9e7f1')
 m.wrap(draw,'Source CAD bodies; proposed clamps, strap and terminal route. Not an electrical qualification.',28,949,390,m.SMALL,'#c2d2df')
 def label(text,p,xy,net):
  m.ren.SetWorldPoint(*p,1);m.ren.WorldToDisplay();x,y,z=m.ren.GetDisplayPoint();x+=m.PANEL;y=m.H-y;color=tuple(int(c*255) for c in m.colors[net]);draw.line((x,y,xy[0],xy[1]+17),fill=color,width=2);draw.ellipse((x-4,y-4,x+4,y+4),fill=color);box=draw.textbbox(xy,text,font=m.LABEL);draw.rectangle((box[0]-5,box[1]-4,box[2]+5,box[3]+4),fill='#101b2a');draw.text(xy,text,font=m.LABEL,fill='#e6eff6')
 if index==0:
  label('GROUND: shield clamp + strap',[-10,12,0],(500,180),'ground');label('RF: terminal on copper Backplate',[27.25,16.2,0],(1200,850),'live');label('PTFE separates the two bodies',[7,38,0],(1260,160),'insulator');label('Single coax from matching box',[-60,4.5,0],(500,850),'ground')
 elif index==1:
  label('Clamp surrounds the exposed shield',[-11,6.5,0],(500,170),'ground');label('Wide strap contacts grounded Boden',[-8,22,0],(1230,850),'ground');label('Proposed blind ground anchor',[-8.2,18.2,0],(1220,180),'ground');label('Insulated RF center continues',[1,7,0],(500,850),'live')
 else:
  label('Separate live M4 terminal / ring lug',[27.25,16.2,0],(1130,185),'live');label('Dielectric remains around the center',[17,13.2,0],(500,850),'insulator');label('Live spacer and copper head',[34,28,0],(1270,850),'live')
 draw.text((m.PANEL+28,30),'3D CUTAWAY / COLORS SHOW ELECTRICAL NODES / GROUND SHIELD, MAGNETS AND HOSES HIDDEN',font=m.SMALL,fill='#acc2d3')
 draw.text((m.PANEL+28,m.H-48),f'{index+1:02} / 03   '+chapters[index]['title'],font=m.SMALL,fill='#b2c8d9');return np.asarray(im)

if __name__=='__main__':
 import sys
 if 'preview' in sys.argv:
  for i in range(3):Image.fromarray(frame(i,.5)).save(OUT/f'view-{i:02}.png')
  m.win.Finalize();print('Three proposal views ready');sys.exit()
 durations=[];chunks=[];params=None
 for i in range(3):
  with wave.open(str(OUT/f'voice-{i:02}.wav'),'rb') as f:p=f.getparams();raw=f.readframes(p.nframes)
  if params is None:params=p
  duration=math.ceil((p.nframes/p.framerate+1.8)*15)/15;durations.append(duration);lead=round(.5*p.framerate);tail=round(duration*p.framerate)-lead-p.nframes;chunks.append(bytes(lead*p.sampwidth*p.nchannels)+raw+bytes(tail*p.sampwidth*p.nchannels))
 with wave.open(str(OUT/'narration.wav'),'wb') as f:
  f.setparams(params)
  for chunk in chunks:f.writeframes(chunk)
 writer=imageio_ffmpeg.write_frames(str(OUT/'silent.mp4'),(m.W,m.H),fps=15,codec='libx264',quality=8,macro_block_size=1,output_params=['-preset','fast']);writer.send(None);elapsed=0;timeline=[]
 for i,d in enumerate(durations):
  timeline.append(elapsed)
  for n in range(round(d*15)):writer.send(frame(i,n/(d*15)))
  elapsed+=d;print('Rendered '+chapters[i]['title'],flush=True)
 writer.close();m.win.Finalize();meta=';FFMETADATA1\ntitle=Single coax - RF and ground termination proposal\n'
 for i,t in enumerate(timeline):meta+=f'[CHAPTER]\nTIMEBASE=1/1000\nSTART={round(t*1000)}\nEND={round((timeline[i+1] if i<2 else elapsed)*1000)}\ntitle={chapters[i]["title"]}\n'
 (OUT/'chapters.ffmeta').write_text(meta);video=OUT/'Single coax - RF and ground connection proposal.mp4'
 subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-y','-v','error','-i',str(OUT/'silent.mp4'),'-i',str(OUT/'narration.wav'),'-i',str(OUT/'chapters.ffmeta'),'-map','0:v','-map','1:a','-map_metadata','2','-map_chapters','2','-c:v','copy','-c:a','aac','-b:a','160k','-movflags','+faststart',str(video)],check=True)
 (OUT/'Render summary.json').write_text(json.dumps({'runtime_seconds':elapsed,'chapters':3,'video':str(video),'fps':15,'resolution':[m.W,m.H]},indent=2));print('COMPLETE '+str(elapsed),flush=True)
