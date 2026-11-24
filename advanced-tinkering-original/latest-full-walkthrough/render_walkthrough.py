from pathlib import Path
import json,struct,math,sys,wave,subprocess,time,importlib.util
import numpy as np
from PIL import Image,ImageDraw
import vtk,imageio_ffmpeg
from vtk.util.numpy_support import vtk_to_numpy
P=Path(__file__).resolve().parent;R=P.parent
spec=importlib.util.spec_from_file_location('base',R/'render-full-assembly-video.py');b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
ren=b.renderer;win=b.window;cam=b.camera;ren.RemoveAllViewProps();W,H,PANEL,FPS=1920,1080,460,15
chapters=json.loads((P/'chapters.json').read_text());meta=json.loads((P/'parts.json').read_text());lookup={q['name']:q for q in meta}
records=[]
def color(q):
 k=q['role'];f=q['file']
 if k in ['cooler','closure']:return (.83,.49,.27)
 if k=='outermag':return (.2,.39,.77)
 if k=='centermag':return (.8,.22,.24)
 if k in ['cups','isolator']:return (.92,.89,.78)
 if k in ['waterseal','headseal','upper62','lower62','kfseal']:return (.09,.13,.11)
 if k=='hoses' or 'blue release' in f:return (.12,.4,.78)
 if k=='rfhot':return (.89,.48,.25)
 if k=='rfground':return (.35,.60,.70)
 if k=='coax':
  if 'jacket' in f:return (.18,.21,.25)
  if 'RF center' in f:return (.89,.48,.25)
  if 'shield' in f:return (.4,.62,.72)
  return (.94,.89,.72)
 if k=='yoke':return (.37,.43,.49)
 if k in ['shieldtube','darkcap','base','kftube']:return (.4,.57,.67)
 if k=='target':return (.69,.71,.73)
 return (.57,.64,.69)
with (P/'latest-mesh.bin').open('rb') as f:
 while name:=b.part_string(f):
  file=b.part_string(f);n=struct.unpack('<i',f.read(4))[0];v=np.frombuffer(f.read(n*36),'<f4').reshape(-1,3,3).astype(float);q=lookup[name];poly=b.polydata(v);mapper=vtk.vtkPolyDataMapper();mapper.SetInputData(poly);mapper.ScalarVisibilityOff();a=vtk.vtkActor();a.SetMapper(mapper);a.GetProperty().SetColor(*color(q));a.GetProperty().SetAmbient(.24);a.GetProperty().SetDiffuse(.69);a.GetProperty().SetSpecular(.25);a.GetProperty().SetSpecularPower(32);ren.AddActor(a)
  records.append({**q,'poly':poly,'mapper':mapper,'actor':a,'variants':{'full':poly},'current':'full','anchor':(v.min((0,1))+v.max((0,1)))/2})
assert len(records)==129
def sm(u):return b.smooth(u)
COPPER={'cooler','closure','waterseal','backbolts'}
MAG=COPPER|{'outermag','centermag','yoke','yokebolt'}
LIVE=MAG|{'spacer','headseal','headbolts'}
JOINT=LIVE|{'isolator','upper62','lower62','base','cups','basebolts'}
MOUNTED=JOINT|{'rfhot','rfground','coax','hoses','fittings','kftube','kfclamps','kfcenter','kfseal','kfbolts'}
ALL={r['role'] for r in records}
LAYER={'darkcap':205,'clamp':165,'target':130,'cooler':90,'waterseal':48,'closure':48,'outermag':8,'centermag':8,'yoke':-15,'spacer':-55,'headseal':-55,'upper62':-55,'isolator':-95,'lower62':-135,'base':-135,'cups':-135}
def scene(i,u,r):
 k=r['role'];pos=np.zeros(3);ori=np.zeros(3);origin=np.zeros(3);half=False;trim=i not in [0,1,10];opacity=1.;show=True
 if i==1:show=k in LAYER;pos[1]=LAYER.get(k,0)*sm(u/.3)
 elif i==2:
  show=k in ['cooler','closure'];pos[0]=52 if k=='cooler' else -52
  if k=='closure':origin=np.array([0,-15.75,0]);ori[0]=180
 elif i==3:
  show=k in COPPER|{'fittings'}
  if k=='closure':pos[1]=-28*(1-sm((u-.2)/.35))
  if k=='waterseal':pos[1]=-15*(1-sm(u/.25))
  if k=='backbolts':show=u>.45;pos[1]=-25*(1-sm((u-.45)/.24))
  if u>.69 and k in ['cooler','closure']:opacity=.16
 elif i==4:
  show=k in MAG
  if k in ['outermag','centermag','yoke']:pos[1]=-43*(1-sm((u-.08)/.7))
  if k=='yokebolt':pos[1]=-25*(1-sm((u-.68)/.25));show=u>.65
  half=k in ['cooler','closure']
 elif i==5:
  show=k in LIVE|{'isolator','upper62','lower62'}
  if k in ['spacer','headseal']:pos[1]=-58*(1-sm((u-.08)/.34))
  if k=='headseal':pos[1]+=12*(1-sm((u-.02)/.15))
  if k=='headbolts':pos[1]=-35*(1-sm((u-.35)/.23));show=u>.3
  if k in ['isolator','upper62','lower62']:show=u>.48;pos[1]=-38*(1-sm((u-.5)/.45))
  half=k in ['spacer'] and u<.5
 elif i==6:
  show=k in ['base','cups','basebolts','isolator','upper62','lower62','spacer']
  if k=='cups':pos[1]=-23*(1-sm((u-.03)/.4))
  if k=='basebolts':show=u>.43;pos[1]=-30*(1-sm((u-.45)/.38))
  half=k in ['base','isolator','spacer'] and u>.7
 elif i==7:
  show=k in MOUNTED and k not in ['backbolts','headbolts','basebolts','kfclamps','kfbolts','kfseal','kfcenter','cups']
  half=k in ['cooler','closure','yoke','spacer','isolator','base','kftube','coax']
  if k in ['cooler','closure','yoke','spacer']:opacity=.25
 elif i==8:
  show=k in MOUNTED;trim=u<.75
  if k in ['coax','hoses']:show=u>.5
  if k=='kftube':pos[1]=-42*(1-sm((u-.1)/.34))
  if k in ['kfseal','kfcenter']:pos[1]=-10*(1-sm(u/.2))
  if k=='kfclamps':pos[2]=(-1 if r['anchor'][2]<0 else 1)*25*(1-sm((u-.45)/.28))
  if k=='kfbolts':show=u>.7;pos[1]=-20*(1-sm((u-.72)/.23))
 elif i==9:
  trim=True
  if k=='target':pos[1]=32*(1-sm((u-.01)/.2))
  if k=='clamp':show=u>.18;pos[1]=45*(1-sm((u-.2)/.2))
  if k=='targetbolts':show=u>.35;pos[1]=32*(1-sm((u-.38)/.18))
  if k=='shieldtube':show=u>.50;pos[1]=95*(1-sm((u-.52)/.22))
  if k=='lowerbolts':show=u>.7;a=r['anchor'].copy();a[1]=0;pos=a/(np.linalg.norm(a) or 1)*14*(1-sm((u-.72)/.12))
  if k=='darkcap':show=u>.75;pos[1]=27*(1-sm((u-.77)/.13))
  if k=='upperbolts':show=u>.87;a=r['anchor'].copy();a[1]=0;pos=a/(np.linalg.norm(a) or 1)*10*(1-sm((u-.89)/.1))
 elif i==10:
  half=u<.57 and k in ['cooler','closure','spacer','isolator','base','kftube','shieldtube','darkcap','coax'];trim=u<.57
 return show,pos,ori,origin,half,trim,opacity
def camera_pose(i,u):
 focus=np.array([0.,-28.,0]);scale=84;az=.9+.08*math.sin(2*math.pi*u);el=.18;roll=0
 if i==0:focus[1]=-143;scale=190;az=.7+.45*u
 elif i==1:focus[1]=0;scale=195;az=.87;el=.13;roll=90
 elif i==2:focus[1]=-13;scale=85;az=.18;el=-1.12
 elif i==3:focus[1]=-15;scale=64;az=.5;el=-1.02
 elif i==4:focus[1]=-30;scale=84;az=1.18;el=.15
 elif i==5:focus[1]=-48;scale=117;az=1.0;el=-.2
 elif i==6:focus[1]=-64;scale=67;az=1.15;el=-.63
 elif i==7:q=sm((u-.4)/.3);focus[1]=-40-3*q;scale=74-24*q;az=1.35;el=.08
 elif i==8:
  q=sm((u-.74)/.22);focus[1]=-82-61*q;scale=105+85*q;az=.9;el=-.20
 elif i==9:focus[1]=-10;scale=120;az=.8+.2*u;el=.3
 elif i==10:
  q=sm((u-.6)/.3);focus[1]=-40-103*q;scale=84+106*q;az=1.2+.4*q;el=.16+.24*q
 direction=np.array([math.sin(az)*math.cos(el),math.sin(el),math.cos(az)*math.cos(el)]);cam.SetFocalPoint(*focus);cam.SetPosition(*(focus+1000*direction));cam.SetViewUp(0,1,0);cam.SetParallelScale(scale);cam.SetRoll(roll);cam.SetClippingRange(500,1600)
flow_lines=[b.flow_actor(path,(.2,.85,.97),.38) for path in b.flow_paths];flow_dots=[]
for path in b.flow_paths:
 for j in range(6):
  s=vtk.vtkSphereSource();s.SetRadius(.65);s.SetThetaResolution(10);s.SetPhiResolution(8);m=vtk.vtkPolyDataMapper();m.SetInputConnection(s.GetOutputPort());a=vtk.vtkActor();a.SetMapper(m);a.GetProperty().SetColor(.95,1,1);a.GetProperty().SetAmbient(.9);ren.AddActor(a);flow_dots.append((a,path,j))
def frame(i,t,duration):
 u=t/duration
 for r in records:
  show,pos,ori,origin,half,trim,opacity=scene(i,u,r);a=r['actor'];a.SetVisibility(show)
  if not show:continue
  key=('half' if half else '')+('trim' if trim else '') or 'full'
  if key not in r['variants']:r['variants'][key]=b.clipped(r['poly'],half,trim)
  if key!=r['current']:r['mapper'].SetInputData(r['variants'][key]);r['current']=key
  a.SetPosition(*pos);a.SetOrientation(*ori);a.SetOrigin(*origin);a.GetProperty().SetOpacity(opacity)
 flow=i==3 and u>.70
 for a in flow_lines:a.SetVisibility(flow)
 for a,path,j in flow_dots:
  a.SetVisibility(flow)
  if flow:
   x=((t*.12+j/6)%1)*(len(path)-1);k=int(x);a.SetPosition(*(path[k]*(1-x+k)+path[min(k+1,len(path)-1)]*(x-k)))
 camera_pose(i,u);win.Render();b.capture.Modified();b.capture.Update();a=vtk_to_numpy(b.capture.GetOutput().GetPointData().GetScalars()).reshape(H,W-PANEL,3);im=Image.new('RGB',(W,H),'#101b2a');im.paste(Image.fromarray(np.flipud(a)),(PANEL,0));d=ImageDraw.Draw(im);d.rectangle((0,0,PANEL-1,H),fill='#1b2b3f')
 d.text((28,30),'CURRENT MAGNETRON / R03 WALKTHROUGH',font=b.TINY,fill='#aac4d7');y=b.wrap(d,chapters[i]['title'],(28,100),395,b.TITLE,'#f0f6fa')+32
 for text in chapters[i]['bullets']:
  d.ellipse((29,y+10,36,y+17),fill='#7fc6df');y=b.wrap(d,text,(53,y),370,b.BODY,'#d9e7f1')+24
 for j,(c,txt) in enumerate([((.83,.49,.27),'Copper cooling parts'),((.91,.88,.77),'PTFE insulation'),((.4,.57,.67),'Grounded body / shields'),((.2,.39,.77),'Outer magnets: S toward target')]):
  yy=790+j*36;d.rectangle((29,yy+5,43,yy+21),fill=tuple(round(x*255) for x in c));d.text((56,yy),txt,font=b.TINY,fill='#d8e8f2')
 b.wrap(d,'Combined mechanical study. Reference fittings and proposed changes are not operating ratings.',(28,965),395,b.TINY,'#ddca8b')
 def label(text,p,xy):
  ren.SetWorldPoint(*p,1);ren.WorldToDisplay();x,y,_=ren.GetDisplayPoint();x+=PANEL;y=H-y;d.line((x,y,xy[0],xy[1]+15),fill='#afcada',width=2);d.ellipse((x-4,y-4,x+4,y+4),fill='#dceaf4');box=d.textbbox(xy,text,font=b.SMALL);d.rectangle((box[0]-5,box[1]-4,box[2]+5,box[3]+4),fill='#101b2a');d.text(xy,text,font=b.SMALL,fill='#eaf2f7')
 if i==0:label('Two-inch target end',[0,2,25],(1280,180));label('One-inch service tube',[12.7,-200,0],(1240,700))
 elif i==1:
  e=sm(u/.3);label('Target and grounded front shield',[0,180*e,0],(500,180));label('Copper and magnet pack',[0,-15,0],(1110,180));label('PTFE isolation and Boden',[0,-60-120*e,0],(1250,850))
 elif i==2:label('Cooling body / channel and blind wells',[52,-9,14],(1100,190));label('Copper backplate / matching face',[-52,-15,0],(500,850))
 elif i==3:label('Annular water passage',[0,-5,13.55],(1260,180));label('Opposed coolant connections',[13.55,-30,0],(500,850))
 elif i==4:label('Twelve outer rods',[25,-12,0],(1250,180));label('Two center discs',[0,-12,0],(500,180));label('Steel return yoke',[15,-24-43*(1-sm((u-.08)/.7)),0],(1250,850))
 elif i==5:label('76 mm outer head seal',[38,-12,0],(1250,180));label('Main PTFE sealing ring',[40,-43.5-38*(1-sm((u-.5)/.45)),0],(500,850))
 elif i==6:label('Twelve integral PTFE cups',[38.2147,-77,10.2396],(1220,850));label('Grounded Boden',[0,-60,40],(1250,180));label('Live spacer / insulated base screws',[38,-40,10],(500,180))
 elif i==7:label('Shield clamp bonds to ground',[0,-48.5,-7.5],(500,850));label('Protected center to live backplate',[0,-35.5,13.55],(1220,850));label('Coolant hoses beside coax',[8,-50,0],(1250,180))
 elif i==8:label('KF16-style flange and clamp',[0,-78,15],(1250,180));label('25.4 mm OD main tube',[12.7,-105 if u<.75 else -200,0],(1250,850))
 elif i==9:label('Target and retaining ring',[0,2,25],(1250,180));label('Grounded outer shield',[48,-30,0],(1250,850))
 elif u<.57:label('Live cooled cathode',[0,-15,30],(1250,180));label('Grounded body and dry service space',[0,-70,15],(500,850))
 else:label('Complete129-instance combined assembly',[0,-25,45],(1180,180))
 d.text((PANEL+28,30),'ACTUAL CAD SOLIDS / ORIGINAL PARTS + LATEST PROPOSED UPDATES',font=b.TINY,fill='#acc5d7')
 if flow:d.text((PANEL+28,73),'FLOW MARKERS ARE SCHEMATIC / NO CFD OR THERMAL RESULT',font=b.TINY,fill='#b2cadb')
 elif i in [1,3,4,5,6,7,8,9] or i==10 and u<.57:d.text((PANEL+28,73),'EXPLODED / SECTIONED WHERE NEEDED FOR INSPECTION',font=b.TINY,fill='#b2cadb')
 d.text((PANEL+28,H-48),f'{i+1:02} / 11   '+chapters[i]['title'],font=b.TINY,fill='#b2c8d9');d.rectangle((PANEL,H-8,W,H),fill='#283b4d');d.rectangle((PANEL,H-8,PANEL+int((W-PANEL)*u),H),fill='#75bfdc');return np.asarray(im)
def stamp(t):
 n=round(t*1000);return f'{n//3600000:02}:{n//60000%60:02}:{n//1000%60:02},{n%1000:03}'
if __name__=='__main__':
 if 'preview' in sys.argv:
  ims=[]
  for i in range(len(chapters)):
   u=.84 if i==3 else .64;im=Image.fromarray(frame(i,u*20,20));im.save(P/f'preview-{i:02}.jpg',quality=92);ims.append(im.resize((640,360)))
  sheet=Image.new('RGB',(1920,1440),'#101b2a')
  for i,im in enumerate(ims):sheet.paste(im,((i%3)*640,(i//3)*360))
  sheet.save(P/'Preview contact sheet.jpg');win.Finalize();print('Eleven walkthrough preview views ready');sys.exit()
 durations=[];chunks=[];params=None
 for i in range(len(chapters)):
  with wave.open(str(P/f'voice-{i:02}.wav'),'rb') as f:p=f.getparams();raw=f.readframes(p.nframes)
  if params is None:params=p
  duration=math.ceil((p.nframes/p.framerate+1.8)*FPS)/FPS;durations.append(duration);lead=round(.5*p.framerate);tail=round(duration*p.framerate)-lead-p.nframes;chunks.append(bytes(lead*p.sampwidth*p.nchannels)+raw+bytes(tail*p.sampwidth*p.nchannels))
 with wave.open(str(P/'narration.wav'),'wb') as f:
  f.setparams(params)
  for q in chunks:f.writeframes(q)
 writer=imageio_ffmpeg.write_frames(str(P/'silent.mp4'),(W,H),fps=FPS,codec='libx264',quality=8,macro_block_size=1,output_params=['-preset','fast']);writer.send(None);elapsed=0;timeline=[];subs=[];start=time.perf_counter()
 for i,(ch,duration) in enumerate(zip(chapters,durations)):
  timeline.append((elapsed,ch['title']));sentences=[s.strip()+'.' for s in ch['speech'].split('.') if s.strip()];length=sum(map(len,sentences));t=elapsed+.5
  for sentence in sentences:
   end=t+(duration-1.8)*len(sentence)/length;subs.append(f'{len(subs)+1}\n{stamp(t)} --> {stamp(end)}\n{sentence}\n');t=end
  for n in range(round(duration*FPS)):writer.send(frame(i,n/FPS,duration))
  elapsed+=duration;print(f'{i+1}/{len(chapters)} rendered: {ch["title"]} ({duration:.1f}s)',flush=True)
 writer.close();win.Finalize();(P/'subtitles.srt').write_text('\n'.join(subs),encoding='utf-8');metadata=';FFMETADATA1\ntitle=Current magnetron R03 - complete CAD walkthrough\n';transcript=[]
 for i,(t,title) in enumerate(timeline):
  end=timeline[i+1][0] if i<len(chapters)-1 else elapsed;metadata+=f'[CHAPTER]\nTIMEBASE=1/1000\nSTART={round(t*1000)}\nEND={round(end*1000)}\ntitle={title}\n';transcript.extend([f'{int(t)//60}:{int(t)%60:02} {title}',chapters[i]['speech'],''])
 (P/'chapters.ffmeta').write_text(metadata,encoding='utf-8');(P/'Walkthrough transcript.txt').write_text('\n'.join(transcript),encoding='utf-8');final=P/'Current magnetron R03 - full exploded walkthrough.mp4'
 subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-y','-v','error','-i',str(P/'silent.mp4'),'-i',str(P/'narration.wav'),'-i',str(P/'subtitles.srt'),'-i',str(P/'chapters.ffmeta'),'-map','0:v','-map','1:a','-map','2:s','-map_metadata','3','-map_chapters','3','-c:v','copy','-c:a','aac','-b:a','160k','-c:s','mov_text','-movflags','+faststart',str(final)],check=True)
 (P/'Render summary.json').write_text(json.dumps({'runtime_seconds':elapsed,'chapter_durations_seconds':durations,'timeline':timeline,'chapters':len(chapters),'components':len(records),'resolution':[W,H],'fps':FPS,'render_seconds':time.perf_counter()-start,'video':str(final)},indent=2));print(f'COMPLETE {elapsed:.1f}s; render {time.perf_counter()-start:.1f}s',flush=True)
