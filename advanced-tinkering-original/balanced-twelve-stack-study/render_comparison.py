from pathlib import Path
import json,struct,math,wave,subprocess,time,sys
import numpy as np
import vtk,imageio_ffmpeg
from vtk.util.numpy_support import numpy_to_vtk,numpy_to_vtkIdTypeArray,vtk_to_numpy
from PIL import Image,ImageDraw,ImageFont
P=Path(__file__).resolve().parent;W,H,FPS=1600,900,10
meta=json.loads((P/'parts.json').read_text());chapters=json.loads((P/'chapters.json').read_text())
def font(n,bold=False):return ImageFont.truetype('C:/Windows/Fonts/'+('segoeuib.ttf' if bold else 'segoeui.ttf'),n)
TITLE=font(34,True);BODY=font(23);SMALL=font(18);LABEL=font(26,True)
window=vtk.vtkRenderWindow();window.SetOffScreenRendering(1);window.SetSize(W,620);window.SetMultiSamples(0)
renderers=[]
for i in range(2):
 r=vtk.vtkRenderer();r.SetViewport(i/2,0,(i+1)/2,1);r.SetBackground(.055,.085,.13);r.SetBackground2(.13,.18,.24);r.GradientBackgroundOn();window.AddRenderer(r);renderers.append(r)
def string(f):
 b=f.read(1)
 if not b:return None
 n=b[0]&127;shift=7
 while b[0]&128:b=f.read(1);n|=(b[0]&127)<<shift;shift+=7
 return f.read(n).decode()
def poly(a):
 out=vtk.vtkPolyData();points=vtk.vtkPoints();points.SetData(numpy_to_vtk(a.reshape(-1,3),deep=True));out.SetPoints(points)
 cells=vtk.vtkCellArray();cells.SetData(numpy_to_vtkIdTypeArray(np.arange(0,len(a)*3+1,3,dtype=np.int64),deep=True),numpy_to_vtkIdTypeArray(np.arange(len(a)*3,dtype=np.int64),deep=True));out.SetPolys(cells)
 clean=vtk.vtkCleanPolyData();clean.SetInputData(out);clean.Update();normals=vtk.vtkPolyDataNormals();normals.SetInputConnection(clean.GetOutputPort());normals.SetFeatureAngle(35);normals.Update();result=vtk.vtkPolyData();result.ShallowCopy(normals.GetOutput());return result
colors={'cooler':(.84,.48,.27),'closure':(.84,.48,.27),'centermag':(.90,.26,.25),'outermag':(.18,.45,.90),'yoke':(.42,.49,.58),'waterseal':(.14,.20,.19),'hoses':(.10,.40,.83),'target':(.72,.76,.80),'isolator':(.92,.88,.75),'cups':(.92,.88,.75),'fittings':(.25,.34,.42)}
records=[]
with (P/'meshes.bin').open('rb') as f:
 while version:=string(f):
  idx=int(string(f));n=struct.unpack('<i',f.read(4))[0];a=np.frombuffer(f.read(n*36),'<f4').reshape(-1,3,3);q=meta[version][idx];p=poly(a);mapper=vtk.vtkPolyDataMapper();mapper.SetInputData(p);mapper.ScalarVisibilityOff();actor=vtk.vtkActor();actor.SetMapper(mapper);actor.GetProperty().SetColor(*colors.get(q['role'],(.50,.62,.70)));actor.GetProperty().SetAmbient(.28);actor.GetProperty().SetDiffuse(.70);actor.GetProperty().SetSpecular(.25);actor.GetProperty().SetSpecularPower(35)
  renderers[version=='new'].AddActor(actor)
  clip=vtk.vtkClipClosedSurface();planes=vtk.vtkPlaneCollection();plane=vtk.vtkPlane();plane.SetNormal(0,0,-1);plane.SetOrigin(0,0,0);planes.AddItem(plane);clip.SetClippingPlanes(planes);clip.SetInputData(p);clip.Update();cut=vtk.vtkPolyData();cut.ShallowCopy(clip.GetOutput())
  records.append({**q,'version':version,'actor':actor,'mapper':mapper,'full':p,'cut':cut})
# Naive conversion uses the baseline shapes with the larger center discs on the right.
naive=[]
for q in records:
 if q['version']=='old' and q['role'] in ['cooler','closure','waterseal']:
  mapper=vtk.vtkPolyDataMapper();mapper.SetInputData(q['cut']);mapper.ScalarVisibilityOff();actor=vtk.vtkActor();actor.SetMapper(mapper);actor.GetProperty().SetColor(*colors[q['role']]);actor.GetProperty().SetAmbient(.35);renderers[1].AddActor(actor);naive.append(actor)
capture=vtk.vtkWindowToImageFilter();capture.SetInput(window);capture.SetInputBufferTypeToRGB();capture.ReadFrontBufferOff()
HEAD={'cooler','closure','yoke','outermag','centermag','waterseal','target','clamp','backbolts','yokebolt','fittings'}
def wrap(d,s,x,y,width,ft,fill):
 words=s.split();line=''
 for w in words:
  test=(line+' '+w).strip()
  if d.textlength(test,font=ft)>width and line:d.text((x,y),line,font=ft,fill=fill);y+=ft.size+8;line=w
  else:line=test
 if line:d.text((x,y),line,font=ft,fill=fill);y+=ft.size+8
 return y
def frame(i,u):
 for a in naive:a.SetVisibility(i==2)
 for q in records:
  k=q['role'];a=q['actor'];version=q['version'];show=True;cut=False;dy=0;opacity=1
  if i==0:show=True
  elif i==6:
   show=k not in ['kftube','kfclamps','kfcenter','kfseal','kfbolts'];cut=k in ['cooler','closure','spacer','base','isolator','shieldtube','darkcap','coax'];
   if k=='hoses':show=False
  elif i==1:show=k in ['outermag','centermag','yoke'];dy=-6 if k=='yoke' else 0
  elif i==2:
   show=k in ['cooler','closure','waterseal','centermag'];cut=k in ['cooler','closure']
   if version=='new':show=k=='centermag'
  elif i==3:show=k=='cooler';cut=True
  elif i==4:show=k in ['closure','waterseal'];dy=13 if k=='waterseal' else 0
  elif i==5:show=k in ['yoke','fittings','hoses','rfhot','rfground','coax','spacer'];cut=k=='spacer';
  a.SetVisibility(show);a.SetPosition(0,dy,0);a.GetProperty().SetOpacity(opacity);q['mapper'].SetInputData(q['cut'] if cut else q['full'])
 for side,r in enumerate(renderers):
  cam=r.GetActiveCamera();focus=np.array([0.,-15.,0.]);scale=52;az=.50+.18*math.sin(u*math.pi*2);el=.48
  if i==0:focus[1]=-143;scale=190;el=.20
  elif i==6:focus[1]=-36;scale=73;el=.20
  elif i==1:scale=44;el=.95
  elif i==2:scale=30;focus[1]=-10;az=.08;el=.38
  elif i==3:scale=49;el=-.95;focus[1]=-5
  elif i==4:scale=43;el=1.25
  elif i==5:focus[1]=-42;scale=55;el=.25
  pos=focus+np.array([math.sin(az)*math.cos(el),math.sin(el),math.cos(az)*math.cos(el)])*240
  cam.SetPosition(*pos);cam.SetFocalPoint(*focus);cam.SetViewUp(0,1,0);cam.ParallelProjectionOn();cam.SetParallelScale(scale);r.ResetCameraClippingRange()
 window.Render();capture.Modified();capture.Update();a=vtk_to_numpy(capture.GetOutput().GetPointData().GetScalars()).reshape(620,W,3)
 im=Image.new('RGB',(W,H),'#101a29');im.paste(Image.fromarray(np.flipud(a)),(0,90));d=ImageDraw.Draw(im)
 d.text((30,15),f'{i+1:02}  '+chapters[i]['title'],font=TITLE,fill='#eef5fc')
 d.text((35,96),'EXISTING / R03',font=LABEL,fill='#d6e4f4');d.text((835,96),'NAIVE ENLARGEMENT / DOES NOT FIT' if i==2 else 'PROPOSED / TWELVE STACKS',font=LABEL,fill='#ffb49c' if i==2 else '#83dfcb')
 d.line((800,92,800,708),fill='#4a6075',width=2)
 if i in [0,6]:caps=['Original assembled envelope','Same interfaces; revised internal head']
 elif i==1:caps=['12 x D8x20 + 2 x D12x10 / N45','24 x D6x10 + 2 x D20x10 / N42']
 elif i==2:caps=['Old bore D13 / coolant starts R11.05','D21 bore removes the inner seal groove']
 elif i==3:caps=['Channel R11.05..16.05 / outer wells PCD50','Channel R15.5..20.5 / outer wells PCD58']
 elif i==4:caps=['Seals ID14.5x2 and ID35x2 / ports +/-13.55','Seals ID23x2 and ID43x2 / ports +/-18']
 else:caps=['Original yoke holes and fitting positions','Clearance holes, fittings and upper hoses move']
 for j,s in enumerate(caps):d.text((30+j*800,672),s,font=SMALL,fill='#e1edf6')
 y=732
 for s in chapters[i]['notes']:
  d.ellipse((34,y+8,42,y+16),fill='#76d6c0');y=wrap(d,s,58,y,1500,BODY,'#d6e4f3')+5
 d.text((32,867),'ACTUAL CAD GEOMETRY  |  MECHANICAL CONCEPT: MAGNETIC BALANCE, COOLING AND SEALS NOT QUALIFIED',font=SMALL,fill='#d9c697')
 d.rectangle((0,H-5,int(W*u),H),fill='#74d7c0');return np.asarray(im)
def stamp(t):
 n=round(t*1000);return f'{n//3600000:02}:{n//60000%60:02}:{n//1000%60:02},{n%1000:03}'
if __name__=='__main__':
 if 'preview' in sys.argv:
  sheet=Image.new('RGB',(1600,1800),'#101a29')
  for i in range(len(chapters)):
   im=Image.fromarray(frame(i,.4));im.save(P/f'preview-{i:02}.png');sheet.paste(im.resize((800,450)),((i%2)*800,(i//2)*450))
  sheet.save(P/'Comparison contact sheet.jpg');window.Finalize();print('Seven previews rendered');sys.exit()
 durations=[];params=None;chunks=[]
 for i in range(len(chapters)):
  with wave.open(str(P/f'voice-{i:02}.wav'),'rb') as f:p=f.getparams();raw=f.readframes(p.nframes)
  if params is None:params=p
  duration=math.ceil((p.nframes/p.framerate+1.5)*FPS)/FPS;durations.append(duration);lead=round(.35*p.framerate);tail=round(duration*p.framerate)-lead-p.nframes;chunks.append(bytes(lead*p.sampwidth*p.nchannels)+raw+bytes(tail*p.sampwidth*p.nchannels))
 with wave.open(str(P/'Narration.wav'),'wb') as f:
  f.setparams(params)
  for chunk in chunks:f.writeframes(chunk)
 writer=imageio_ffmpeg.write_frames(str(P/'silent.mp4'),(W,H),fps=FPS,codec='libx264',quality=8,macro_block_size=1,output_params=['-preset','fast']);writer.send(None)
 timeline=[];subs=[];elapsed=0;started=time.perf_counter()
 for i,duration in enumerate(durations):
  timeline.append((elapsed,chapters[i]['title']));subs.append(f'{i+1}\n{stamp(elapsed)} --> {stamp(elapsed+duration)}\n'+chapters[i]['speech']+'\n')
  for n in range(round(duration*FPS)):writer.send(frame(i,n/(duration*FPS)))
  elapsed+=duration;print(f'Rendered chapter {i+1}/7, {duration:.1f}s',flush=True)
 writer.close();window.Finalize();(P/'Captions.srt').write_text('\n'.join(subs),encoding='utf-8')
 ffmeta=';FFMETADATA1\ntitle=Twelve stack magnetron - mechanical comparison\n'
 transcript=[]
 for i,(t,title) in enumerate(timeline):
  end=timeline[i+1][0] if i+1<len(timeline) else elapsed
  ffmeta+=f'[CHAPTER]\nTIMEBASE=1/1000\nSTART={round(t*1000)}\nEND={round(end*1000)}\ntitle={title}\n'
  transcript.extend([f'{int(t)//60}:{int(t)%60:02} {title}',chapters[i]['speech'],''])
 (P/'chapters.ffmeta').write_text(ffmeta);(P/'Video transcript.txt').write_text('\n'.join(transcript))
 final=P/'Twelve stack magnetron - mechanical comparison.mp4'
 subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-y','-v','error','-i',str(P/'silent.mp4'),'-i',str(P/'Narration.wav'),'-i',str(P/'Captions.srt'),'-i',str(P/'chapters.ffmeta'),'-map','0:v','-map','1:a','-map','2:s','-map_metadata','3','-map_chapters','3','-c:v','copy','-c:a','aac','-c:s','mov_text','-movflags','+faststart',str(final)],check=True)
 (P/'Video verification.json').write_text(json.dumps({'duration_seconds':elapsed,'chapters':timeline,'resolution':[W,H],'fps':FPS,'render_seconds':time.perf_counter()-started,'video':str(final)},indent=2));print('Completed comparison video',flush=True)
