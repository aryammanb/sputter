from pathlib import Path
import json,struct,math,wave,subprocess,time,sys
import numpy as np
from PIL import Image,ImageDraw,ImageFont
import vtk,imageio_ffmpeg
from vtk.util.numpy_support import numpy_to_vtk,numpy_to_vtkIdTypeArray,vtk_to_numpy
P=Path(__file__).resolve().parent;W,H,FPS=1600,900,12;LEFT=430
chapters=json.loads((P/'chapters.json').read_text());m=json.loads((P/'fine_nominal_metrics.json').read_text());samples=np.load(P/'fine_nominal_samples.npz');lines=json.loads((P/'fieldlines.json').read_text());sensitivity=json.loads((P/'target_thickness_sensitivity.json').read_text())
def font(n,b=False):return ImageFont.truetype('C:/Windows/Fonts/'+('segoeuib.ttf' if b else 'segoeui.ttf'),n)
TITLE=font(32,True);BODY=font(24);SMALL=font(19);BIG=font(48,True);METRIC=font(28,True)
renderer=vtk.vtkRenderer();renderer.SetBackground(.055,.085,.13);renderer.SetBackground2(.12,.18,.24);renderer.GradientBackgroundOn();window=vtk.vtkRenderWindow();window.SetOffScreenRendering(1);window.SetSize(1170,700);window.SetMultiSamples(0);window.AddRenderer(renderer)
def string(f):
 b=f.read(1)
 if not b:return None
 n=b[0]&127;shift=7
 while b[0]&128:b=f.read(1);n|=(b[0]&127)<<shift;shift+=7
 return f.read(n).decode()
def poly(a):
 out=vtk.vtkPolyData();points=vtk.vtkPoints();points.SetData(numpy_to_vtk(a.reshape(-1,3),deep=True));out.SetPoints(points);cells=vtk.vtkCellArray();cells.SetData(numpy_to_vtkIdTypeArray(np.arange(0,len(a)*3+1,3,dtype=np.int64),deep=True),numpy_to_vtkIdTypeArray(np.arange(len(a)*3,dtype=np.int64),deep=True));out.SetPolys(cells);return out
meta=json.loads((P.parent/'parts.json').read_text())
colors={'cooler':(.84,.47,.26),'closure':(.84,.47,.26),'yoke':(.43,.50,.57),'centermag':(.89,.25,.24),'outermag':(.17,.42,.86),'target':(.64,.75,.82)}
with (P.parent/'meshes.bin').open('rb') as f:
 while version:=string(f):
  idx=int(string(f));n=struct.unpack('<i',f.read(4))[0];raw=f.read(n*36)
  if version!='new':continue
  q=meta[version][idx];k=q['role']
  if k not in colors:continue
  a=np.frombuffer(raw,'<f4').reshape(-1,3).astype(float);a=a[:,[0,2,1]];a[:,1]*=-1;p=poly(a.reshape(-1,3,3));mapper=vtk.vtkPolyDataMapper();mapper.SetInputData(p);mapper.ScalarVisibilityOff();actor=vtk.vtkActor();actor.SetMapper(mapper);actor.GetProperty().SetColor(*colors[k]);actor.GetProperty().SetAmbient(.30);actor.GetProperty().SetDiffuse(.70);actor.GetProperty().SetOpacity(.08 if k in ['cooler','closure'] else .16 if k=='target' else 1);renderer.AddActor(actor)
lut=vtk.vtkLookupTable();lut.SetNumberOfTableValues(256);lut.SetRange(0,150)
import matplotlib
for i,c in enumerate(matplotlib.colormaps['viridis'](np.linspace(0,1,256))):lut.SetTableValue(i,*c)
lut.Build();tracers=[]
for line in lines:
 points=np.array(line['points']);p=vtk.vtkPolyData();vp=vtk.vtkPoints();vp.SetData(numpy_to_vtk(points,deep=True));p.SetPoints(vp);cell=vtk.vtkPolyLine();cell.GetPointIds().SetNumberOfIds(len(points))
 for i in range(len(points)):cell.GetPointIds().SetId(i,i)
 cells=vtk.vtkCellArray();cells.InsertNextCell(cell);p.SetLines(cells);a=numpy_to_vtk(np.array(line['B_mT']),deep=True);a.SetName('B_mT');p.GetPointData().SetScalars(a)
 tube=vtk.vtkTubeFilter();tube.SetInputData(p);tube.SetRadius(.23);tube.SetNumberOfSides(6);mapper=vtk.vtkPolyDataMapper();mapper.SetInputConnection(tube.GetOutputPort());mapper.SetLookupTable(lut);mapper.SetScalarRange(0,150);actor=vtk.vtkActor();actor.SetMapper(mapper);renderer.AddActor(actor)
 sphere=vtk.vtkSphereSource();sphere.SetRadius(.38);sphere.SetThetaResolution(8);sphere.SetPhiResolution(6);mapper=vtk.vtkPolyDataMapper();mapper.SetInputConnection(sphere.GetOutputPort());dot=vtk.vtkActor();dot.SetMapper(mapper);dot.GetProperty().SetColor(.9,.96,.97);renderer.AddActor(dot);tracers.append((dot,points))
capture=vtk.vtkWindowToImageFilter();capture.SetInput(window);capture.SetInputBufferTypeToRGB();capture.ReadFrontBufferOff()
plots={1:Image.open(P/'Target field map.png').convert('RGB'),2:Image.open(P/'Field section.png').convert('RGB'),3:Image.open(P/'Racetrack uniformity.png').convert('RGB'),4:Image.open(P/'Field versus height.png').convert('RGB')}
def wrap(d,s,x,y,width,ft,fill):
 line=''
 for word in s.split():
  trial=(line+' '+word).strip()
  if d.textlength(trial,font=ft)>width and line:d.text((x,y),line,font=ft,fill=fill);y+=ft.size+9;line=word
  else:line=trial
 if line:d.text((x,y),line,font=ft,fill=fill);y+=ft.size+9
 return y
def fit_image(im,box):
 im=im.copy();im.thumbnail((box[2]-box[0],box[3]-box[1]),Image.Resampling.LANCZOS);return im,(box[0]+(box[2]-box[0]-im.width)//2,box[1]+(box[3]-box[1]-im.height)//2)
def frame(i,u):
 im=Image.new('RGB',(W,H),'#101b2c');d=ImageDraw.Draw(im);d.rectangle((0,0,LEFT,H),fill='#18293d');title_end=wrap(d,chapters[i]['title'],26,33,LEFT-52,TITLE,'#eff6fc');y=max(190,title_end+40)
 for s in chapters[i]['bullets']:
  d.ellipse((27,y+10,34,y+17),fill='#7ddfc9');y=wrap(d,s,48,y,LEFT-72,BODY,'#d9e7f6')+25
 d.text((26,735),'PROPOSED CIRCUIT',font=SMALL,fill='#a7c1db');d.text((26,772),'3D magnetostatic FEM',font=BODY,fill='#dcebf7')
 if i==0:
  for j,(actor,p) in enumerate(tracers):actor.SetPosition(*p[int(((u*4+j*.137)%1)*(len(p)-1))])
  az=.2+u*2*np.pi;focus=np.array([0.,0.,10.]);cam=renderer.GetActiveCamera();cam.SetPosition(*(focus+np.array([160*np.cos(az),160*np.sin(az),95])));cam.SetFocalPoint(*focus);cam.SetViewUp(0,0,1);cam.ParallelProjectionOn();cam.SetParallelScale(62);renderer.ResetCameraClippingRange();window.Render();capture.Modified();capture.Update();a=vtk_to_numpy(capture.GetOutput().GetPointData().GetScalars()).reshape(700,1170,3);im.paste(Image.fromarray(np.flipud(a)),(LEFT,90));d=ImageDraw.Draw(im);d.text((LEFT+35,28),'CALCULATED FIELD LINES / ACTUAL YOKE GEOMETRY',font=METRIC,fill='#edf4fc');d.text((LEFT+35,800),'Tracers indicate field direction; they are not simulated plasma particles.',font=SMALL,fill='#bad0e5')
 elif i in plots:
  pic,pos=fit_image(plots[i],(LEFT+20,95,W-15,765));im.paste(pic,pos);d=ImageDraw.Draw(im)
  if i==1:
   d.text((LEFT+35,30),'Mean racetrack field 95 mT  /  weakest point 89.5 mT',font=METRIC,fill='#7ddfc9')
  elif i==2:d.text((LEFT+35,30),'Near-target confinement geometry; no plasma-density calculation',font=METRIC,fill='#7ddfc9')
  elif i==3:
   idx=int(u*(len(samples['track_B'])-1));value=samples['track_B'][idx]*1000;angle=np.rad2deg(samples['theta'][idx]);d.text((LEFT+35,35),f'Angle {angle:5.1f} deg     B parallel {value:5.1f} mT',font=METRIC,fill='#7ddfc9')
   # Moving dot samples the already plotted circumference curve.
   d.text((LEFT+35,785),'10.6% magnetic ripple is not a coating-uniformity prediction.',font=SMALL,fill='#bad0e5')
  elif i==4:
   d.text((LEFT+35,30),'At 89.5 mT: 10 eV ->0.12 mm   |   100 eV ->0.38 mm',font=METRIC,fill='#7ddfc9');d.text((LEFT+35,790),'Gyroradius uses perpendicular electron energy; no sheath or collision model.',font=SMALL,fill='#bad0e5')
 elif i==5:
  d.text((LEFT+45,35),'SPACING SENSITIVITY / NONMAGNETIC TARGET',font=METRIC,fill='#edf4fc');x0=LEFT+90;barwidth=820;y0=155
  for j,item in enumerate(sensitivity):
   yy=y0+j*140;value=item['track_mean_Bparallel_mT'];d.text((x0,yy),f"Target {item['target_thickness_mm']} mm  |  pole-to-face {item['pole_tip_to_front_face_mm']:.1f} mm",font=BODY,fill='#dce9f6');d.rectangle((x0,yy+45,x0+barwidth,yy+85),fill='#243b52');d.rectangle((x0,yy+45,x0+barwidth*value/120,yy+85),fill='#64cbb5');d.text((x0+barwidth+12,yy+42),f'{value:.0f} mT',font=METRIC,fill='#e4f4f6')
  d.text((x0,765),'Measured 0.25 mm above each assumed target face; same magnet pack.',font=SMALL,fill='#bad0e5')
 else:
  cards=[('95 mT','mean parallel field on ring'),('0.12 mm','10 eV electron gyroradius'),('0.4%','mean-field mesh change'),('2.3%','free-space analytical check error')]
  for j,(value,label) in enumerate(cards):
   x=LEFT+60+(j%2)*540;yy=90+(j//2)*185;d.text((x,yy),value,font=BIG,fill='#7ddfc9');wrap(d,label,x,yy+70,480,BODY,'#d6e7f7')
  wrap(d,'Magnetic-strength screening: POSITIVE',LEFT+60,510,1040,TITLE,'#8ae5cc');wrap(d,'Enough field to strongly magnetize electrons near the target. No evidence here that the copper gap makes it too weak.',LEFT+60,575,1010,BODY,'#d6e7f7');wrap(d,'Not established: ignition, plasma density, confinement time, erosion, or truly balanced topology.',LEFT+60,705,1010,BODY,'#f1d09a')
 d.text((LEFT+25,856),'STATIC MAGNETIC MODEL  |  ASSUMED N42 / REFERENCE AISI1010  |  NO SELF-CONSISTENT PLASMA',font=SMALL,fill='#d8c89c');d.text((27,850),f'{i+1:02} / 07',font=SMALL,fill='#aac2d9');d.rectangle((LEFT,H-6,LEFT+int((W-LEFT)*u),H),fill='#7ddfc9');return np.asarray(im)
def stamp(t):
 n=round(t*1000);return f'{n//3600000:02}:{n//60000%60:02}:{n//1000%60:02},{n%1000:03}'
if __name__=='__main__':
 if 'preview' in sys.argv:
  sheet=Image.new('RGB',(1600,1800),'#101b2c')
  for i in range(7):
   im=Image.fromarray(frame(i,.4));im.save(P/f'video-preview-{i:02}.png');sheet.paste(im.resize((800,450)),((i%2)*800,(i//2)*450))
  sheet.save(P/'Video contact sheet.jpg');window.Finalize();print('Previews ready');sys.exit()
 durations=[];chunks=[];params=None
 for i in range(7):
  with wave.open(str(P/f'voice-{i:02}.wav'),'rb') as f:p=f.getparams();raw=f.readframes(p.nframes)
  if params is None:params=p
  duration=math.ceil((p.nframes/p.framerate+1.7)*FPS)/FPS;durations.append(duration);lead=round(.4*p.framerate);tail=round(duration*p.framerate)-lead-p.nframes;chunks.append(bytes(lead*p.sampwidth*p.nchannels)+raw+bytes(tail*p.sampwidth*p.nchannels))
 with wave.open(str(P/'Narration.wav'),'wb') as f:
  f.setparams(params)
  for chunk in chunks:f.writeframes(chunk)
 writer=imageio_ffmpeg.write_frames(str(P/'silent.mp4'),(W,H),fps=FPS,codec='libx264',quality=8,macro_block_size=1,output_params=['-preset','fast']);writer.send(None);elapsed=0;timeline=[];subs=[];started=time.perf_counter()
 for i,duration in enumerate(durations):
  timeline.append((elapsed,chapters[i]['title']));sentences=[s.strip()+'.' for s in chapters[i]['speech'].split('.') if s.strip()];total=sum(map(len,sentences));t=elapsed+.4
  for sentence in sentences:
   end=t+(duration-1.7)*len(sentence)/total;subs.append(f'{len(subs)+1}\n{stamp(t)} --> {stamp(end)}\n{sentence}\n');t=end
  for n in range(round(duration*FPS)):writer.send(frame(i,n/(duration*FPS)))
  elapsed+=duration;print('Rendered',i+1,'of7',round(duration,1),'seconds',flush=True)
 writer.close();window.Finalize();(P/'Captions.srt').write_text('\n'.join(subs),encoding='utf-8');metadata=';FFMETADATA1\ntitle=Proposed magnetron magnetic circuit - 3D FEM results\n';transcript=[]
 for i,(t,title) in enumerate(timeline):
  end=timeline[i+1][0] if i+1<len(timeline) else elapsed;metadata+=f'[CHAPTER]\nTIMEBASE=1/1000\nSTART={round(t*1000)}\nEND={round(end*1000)}\ntitle={title}\n';transcript.extend([f'{int(t)//60}:{int(t)%60:02} {title}',chapters[i]['speech'],''])
 (P/'chapters.ffmeta').write_text(metadata);(P/'Video transcript.txt').write_text('\n'.join(transcript));final=P/'Magnetic circuit simulation - confinement assessment.mp4'
 subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-y','-v','error','-i',str(P/'silent.mp4'),'-i',str(P/'Narration.wav'),'-i',str(P/'Captions.srt'),'-i',str(P/'chapters.ffmeta'),'-map','0:v','-map','1:a','-map','2:s','-map_metadata','3','-map_chapters','3','-c:v','copy','-c:a','aac','-c:s','mov_text','-movflags','+faststart',str(final)],check=True)
 (P/'Video verification.json').write_text(json.dumps({'duration_seconds':elapsed,'chapters':timeline,'resolution':[W,H],'fps':FPS,'render_seconds':time.perf_counter()-started,'video':str(final)},indent=2));print('Simulation video complete',flush=True)
