import json, math, struct, runpy, wave, subprocess, sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg

OUT=Path(__file__).resolve().parent
ROOT=OUT.parent
helpers=runpy.run_path(str(ROOT/'render-video.py'))
rasterize,wrap,smooth=[helpers[k] for k in ['rasterize','wrap','smooth']]
scenes=json.loads((OUT/'scenes.json').read_text())
parts={}
with (ROOT/'RevB/actual-head-mesh.bin').open('rb') as f:
 while first:=f.read(1):
  n=first[0]&127;shift=7
  while first[0]&128:
   first=f.read(1);n|=(first[0]&127)<<shift;shift+=7
  name=f.read(n).decode();count=struct.unpack('<i',f.read(4))[0]
  v=np.frombuffer(f.read(count*36),'<f4').reshape(-1,3,3).astype(float)
  parts[name.split()[0]]=v
W,H,FPS=1600,900,15
def font(n,b=False):return ImageFont.truetype('C:/Windows/Fonts/'+('segoeuib.ttf' if b else 'segoeui.ttf'),n)
TITLE,BODY,SMALL,TINY=font(36,True),font(25),font(20),font(17)
GOLD='#ffcf5b';BLUE='#80dcff'

def frame(i,t,duration):
 u=t/duration
 if i==0: gap=46*smooth((u-.12)/.75);yaw=1.02;scale=8;center=np.array([-17.,0,0])
 elif i in [1,2,3]:gap=0;yaw=.15+.08*math.sin(u*math.pi);scale=8.7;center=np.array([1.,0,0])
 elif i==4:gap=46*(1-smooth((u-.08)/.74));yaw=1.02;scale=8;center=np.array([-17.,0,0])
 else:gap=0;yaw=.5+.45*smooth(u);scale=8.6;center=np.array([-3.,0,0])
 elevation=.20;origin=(1020,447)
 cy,sy=math.cos(yaw),math.sin(yaw);ce,se=math.cos(elevation),math.sin(elevation)
 def project(points):
  x,y,z=np.moveaxis(np.asarray(points)-center,-1,0);d=-x*cy+y*sy
  return np.stack((origin[0]+scale*(x*sy+y*cy),origin[1]-scale*(z*ce-d*se),d*ce+z*se),axis=-1)
 meshes=[];colors=[]
 for code in ['F01-001','F01-002']:
  if i in [1,2,3] and code=='F01-002':continue
  v=parts[code].copy()
  rgb=np.tile([217,143,90] if code=='F01-001' else [176,111,69],(len(v),1)).astype(float)
  if code=='F01-002':v[:,:,0]-=gap
  if code=='F01-001':
   floor=np.all(abs(v[:,:,0]-4)<1e-5,axis=1)&(np.linalg.norm(v.mean(1)[:,1:],axis=1)<29.1)
   if i in [1,2,3]:rgb[floor]=[45,150,200]
  meshes.append(v);colors.append(rgb)
 tri=project(np.concatenate(meshes));rgb=np.concatenate(colors)
 normal=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);normal/=np.maximum(np.linalg.norm(normal,axis=1,keepdims=True),1e-8)
 rgb=np.clip(rgb*(.48+.45*np.abs(normal@np.array([-.2,-.4,.89])))[:,None]+7,0,255).astype('uint8')
 im=Image.new('RGB',(W,H),'#101b2a');d=ImageDraw.Draw(im);d.rectangle((0,0,436,H),fill='#1b2b3f')
 d.text((30,28),'REV B / PROPOSED BRAZED JOINT',font=TINY,fill='#a9c2d7')
 y=wrap(d,scenes[i]['title'],(30,90),375,TITLE,'#f4f7fc')+35
 for txt in scenes[i]['bullets']:
  d.ellipse((31,y+10,38,y+17),fill=GOLD);y=wrap(d,txt,(52,y),350,BODY,'#d9e6f0')+24
 for yy,col,txt in [(650,'#d98f5a','Existing copper geometry'),(688,BLUE,'Water pocket / cover hidden'),(726,GOLD,'Proposed bonding regions')]:
  d.rectangle((30,yy+5,44,yy+19),fill=col);d.text((56,yy),txt,font=TINY,fill='#d4e4ef')
 wrap(d,'Concept overlay. Groove redesign and joining process still required.',(30,796),370,TINY,'#efcb77')
 im=Image.fromarray(rasterize(np.array(im),tri,rgb));d=ImageDraw.Draw(im)
 def line3(pts,color=GOLD,width=6):
  pp=project(np.asarray(pts));d.line([tuple(p[:2]) for p in pp],fill=color,width=width)
 def ring(y,z,r,frac=1):
  a=np.linspace(0,math.tau*max(.002,frac),160)
  line3(np.column_stack((np.full(len(a),-.15),y+r*np.cos(a),z+r*np.sin(a))))
 def label(txt,p,xy,col='#e5eff8'):
  q=project(np.array(p));d.line((q[0],q[1],xy[0],xy[1]+12),fill=col,width=2)
  d.ellipse((q[0]-4,q[1]-4,q[0]+4,q[1]+4),fill=col)
  d.rounded_rectangle((xy[0]-7,xy[1]-3,xy[0]+d.textlength(txt,font=SMALL)+7,xy[1]+29),radius=4,fill='#17283a');d.text(xy,txt,font=SMALL,fill=col)
 if i in [1,2,3,4,5]:
  ring(0,0,32,smooth(u*3) if i==1 else 1)
 if i in [2,3,4,5]:
  frac=smooth(u*3) if i==2 else 1
  ring(0,0,7.75,frac)
  for a in np.arange(6)*math.pi/3:ring(20*math.cos(a),20*math.sin(a),5.75,frac)
 if i in [3,4,5]:
  # Exposed divider land sections; the island bond closes the interrupted middle.
  for lo,hi in [(8.8,15.1),(24.9,31)]:line3([[0,lo,0],[0,hi,0]],GOLD,12)
 if i==0:
  label('Copper body',[0,-22,22],(1210,145),'#f4b982')
  label('Copper cover',[-gap,-26,-17],(535,715),'#f4b982')
 elif i==1:
  label('Continuous outer bond',[0,0,-32],(1120,770),GOLD)
  label('Water pocket',[4,-15,13],(510,155),BLUE)
 elif i==2:
  label('Bond around every dry well',[0,20,0],(1130,125),GOLD)
  label('Center well stays dry',[0,0,0],(490,240))
 elif i==3:
  label('Divider bond',[0,28,0],(1200,435),GOLD)
  d.text((650,115),'GOLD = PROPOSED BOND FOOTPRINT',font=SMALL,fill=GOLD)
 elif i==4:
  label('Cover approaches prepared body',[-gap,-20,-16],(600,730))
  d.text((550,110),'BOND HIGHLIGHTS SHOWN THROUGH COVER',font=SMALL,fill=GOLD)
 elif i==5:
  label('Rear access to dry magnet wells',[-3,-20,0],(545,165))
  label('Permanent body-to-cover joint',[0,0,-32],(1000,760),GOLD)
  d.text((550,110),'BURIED JOINT SHOWN AS AN X-RAY OVERLAY',font=SMALL,fill=GOLD)
 d.text((470,28),'EXISTING CAD MESH + PROPOSED JOINT OVERLAY / NO CAD CHANGES',font=TINY,fill='#aec2d4')
 d.text((475,850),f'{i+1:02} / 06    HOW THE JOINT BECOMES THE SEAL',font=TINY,fill='#b5cadd')
 d.rectangle((436,890,1599,899),fill='#2b3c4f');d.rectangle((436,890,436+round(1164*u),899),fill=GOLD)
 return np.asarray(im)

if __name__=='__main__':
 if 'preview' in sys.argv:
  for i in range(6):Image.fromarray(frame(i,5,10)).save(OUT/f'preview-{i}.png')
  sys.exit()
 chunks=[];durations=[];params=None
 for i in range(6):
  with wave.open(str(OUT/f'voice-{i}.wav'),'rb') as f:
   p=f.getparams();raw=f.readframes(p.nframes)
  if params is None:params=p
  dur=math.ceil((p.nframes/p.framerate+1.2)*FPS)/FPS;durations.append(dur)
  lead=round(.4*p.framerate);tail=round(dur*p.framerate)-lead-p.nframes
  chunks.append(bytes(lead*p.sampwidth*p.nchannels)+raw+bytes(tail*p.sampwidth*p.nchannels))
 with wave.open(str(OUT/'narration.wav'),'wb') as f:
  f.setparams(params)
  for chunk in chunks:f.writeframes(chunk)
 writer=imageio_ffmpeg.write_frames(str(OUT/'silent.mp4'),(W,H),fps=FPS,codec='libx264',quality=8,macro_block_size=1);writer.send(None)
 for i,dur in enumerate(durations):
  for n in range(round(dur*FPS)):writer.send(frame(i,n/FPS,dur))
  print(f'Scene {i+1}/6 complete ({dur:.1f}s)',flush=True)
 writer.close()
 final=OUT/'Copper water-channel joint - explained.mp4'
 subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-y','-v','error','-i',str(OUT/'silent.mp4'),'-i',str(OUT/'narration.wav'),'-c:v','copy','-c:a','aac','-b:a','160k','-movflags','+faststart',str(final)],check=True)
 print(f'COMPLETE: {sum(durations):.1f}s | {final}',flush=True)
