from pathlib import Path
import struct,json,math,sys,wave,subprocess
import numpy as np
import vtk,imageio_ffmpeg
from vtk.util.numpy_support import numpy_to_vtk,numpy_to_vtkIdTypeArray,vtk_to_numpy
from PIL import Image,ImageDraw,ImageFont
P=Path(__file__).resolve().parent;S=P.parent/'balanced-twelve-stack-study'
W,H,PANEL,FPS=1600,900,436,15
scenes=json.loads((P/'scenes.json').read_text());meta=json.loads((S/'parts.json').read_text())
def string(f):
 b=f.read(1)
 if not b:return None
 n=b[0]&127;shift=7
 while b[0]&128:b=f.read(1);n|=(b[0]&127)<<shift;shift+=7
 return f.read(n).decode()
def poly(v):
 p=vtk.vtkPolyData();pts=vtk.vtkPoints();pts.SetData(numpy_to_vtk(v.reshape(-1,3),deep=True));p.SetPoints(pts)
 c=vtk.vtkCellArray();c.SetData(numpy_to_vtkIdTypeArray(np.arange(0,len(v)*3+1,3,dtype=np.int64),deep=True),numpy_to_vtkIdTypeArray(np.arange(len(v)*3,dtype=np.int64),deep=True));p.SetPolys(c)
 clean=vtk.vtkCleanPolyData();clean.SetInputData(p);clean.Update();norm=vtk.vtkPolyDataNormals();norm.SetInputConnection(clean.GetOutputPort());norm.SetFeatureAngle(35);norm.Update();o=vtk.vtkPolyData();o.DeepCopy(norm.GetOutput());return o
ren=vtk.vtkRenderer();ren.SetBackground(.063,.106,.165)
win=vtk.vtkRenderWindow();win.SetOffScreenRendering(1);win.SetSize(W-PANEL,H);win.SetMultiSamples(4);win.AddRenderer(ren)
cam=ren.GetActiveCamera();cam.ParallelProjectionOn()
def actor(p,col):
 m=vtk.vtkPolyDataMapper();m.SetInputData(p);m.ScalarVisibilityOff();a=vtk.vtkActor();a.SetMapper(m);a.GetProperty().SetColor(*col);a.GetProperty().SetAmbient(.28);a.GetProperty().SetDiffuse(.7);a.GetProperty().SetSpecular(.3);a.GetProperty().SetSpecularPower(30);ren.AddActor(a);return a
records={}
with (S/'meshes.bin').open('rb') as f:
 while ver:=string(f):
  idx=int(string(f));n=struct.unpack('<i',f.read(4))[0];v=np.frombuffer(f.read(n*36),'<f4').reshape(-1,3,3).astype(float);q=meta[ver][idx]
  if ver!='new' or q['role'] not in ['cooler','closure']:continue
  p=poly(v);a=actor(p,(.84,.49,.28));plane=vtk.vtkPlane();plane.SetOrigin(0,0,0);plane.SetNormal(0,0,1);planes=vtk.vtkPlaneCollection();planes.AddItem(plane)
  clip=vtk.vtkClipClosedSurface();clip.SetInputData(p);clip.SetClippingPlanes(planes);clip.GenerateFacesOn();clip.Update();cut=vtk.vtkPolyData();cut.DeepCopy(clip.GetOutput())
  records[q['role']]={'actor':a,'full':p,'cut':cut}
assert set(records)=={'cooler','closure'}
def tube(points,r,col):
 pp=vtk.vtkPoints();[pp.InsertNextPoint(*q) for q in points];line=vtk.vtkPolyLine();line.GetPointIds().SetNumberOfIds(len(points))
 for j in range(len(points)):line.GetPointIds().SetId(j,j)
 cells=vtk.vtkCellArray();cells.InsertNextCell(line);p=vtk.vtkPolyData();p.SetPoints(pp);p.SetLines(cells);t=vtk.vtkTubeFilter();t.SetInputData(p);t.SetRadius(r);t.SetNumberOfSides(12);t.Update();return actor(t.GetOutput(),col)
def circle(r,y,start=0,end=math.tau):
 a=np.linspace(start,end,241);return np.column_stack((r*np.cos(a),np.full(len(a),y),r*np.sin(a)))
gold=(1,.78,.25);blue=(.16,.65,.87)
rings=[tube(circle(r,-8.88),.40,gold) for r in [12.925,22.925]]
half_rings=[tube(circle(r,-8.88,0,math.pi),.4,gold) for r in [12.925,22.925]]
# A thin explanatory water sheet inside the actual annular channel.
water=[]
for j in range(180):
 a,b=j*math.tau/180,(j+1)*math.tau/180
 p=lambda r,t:[r*math.cos(t),-5.0,r*math.sin(t)]
 water.extend([[p(15.55,a),p(20.45,a),p(20.45,b)],[p(15.55,a),p(20.45,b),p(15.55,b)]])
wa=actor(poly(np.array(water)),blue);wa.GetProperty().SetOpacity(.8)
capture=vtk.vtkWindowToImageFilter();capture.SetInput(win);capture.SetInputBufferTypeToRGB();capture.ReadFrontBufferOff()
def font(n,b=False):return ImageFont.truetype('C:/Windows/Fonts/'+('segoeuib.ttf' if b else 'segoeui.ttf'),n)
TITLE,BODY,SMALL=font(35,True),font(24),font(18)
def wrap(d,s,xy,width,ft,col):
 x,y=xy;line=''
 for w in s.split():
  test=(line+' '+w).strip()
  if line and d.textlength(test,font=ft)>width:d.text((x,y),line,font=ft,fill=col);y+=ft.size+9;line=w
  else:line=test
 d.text((x,y),line,font=ft,fill=col);return y+ft.size+9
def sm(u):u=max(0,min(1,u));return u*u*(3-2*u)
def frame(i,u):
 gap=30*sm((u-.1)/.75) if i==0 else 30*(1-sm((u-.1)/.75)) if i==3 else 0
 for k,q in records.items():
  a=q['actor'];a.SetVisibility(not(i==1 and k=='closure') and not(i==2 and k=='cooler'));a.SetPosition(0,-gap if k=='closure' else 0,0);a.GetMapper().SetInputData(q['cut'] if i==4 else q['full']);a.GetProperty().SetOpacity(.3 if i==3 and u>.8 else 1)
 for a in rings:a.SetVisibility(i in [1,2,3])
 for a in half_rings:a.SetVisibility(i==4)
 wa.SetVisibility(i==1)
 focus=np.array([0.,-15-gap/2,0]);scale=59;el=-.38;az=.60+.12*math.sin(u*math.pi)
 if i==1:focus[1]=-5;el=-1.25;scale=52
 if i==2:focus[1]=-14;el=1.28;scale=43
 if i==4:focus[1]=-9;el=.18;az=.1;scale=53
 direction=np.array([math.sin(az)*math.cos(el),math.sin(el),math.cos(az)*math.cos(el)*(-1 if i==4 else 1)])
 cam.SetFocalPoint(*focus);cam.SetPosition(*(focus+direction*400));cam.SetViewUp(0,1,0);cam.SetParallelScale(scale);ren.ResetCameraClippingRange()
 win.Render();capture.Modified();capture.Update();pixels=vtk_to_numpy(capture.GetOutput().GetPointData().GetScalars()).reshape(H,W-PANEL,3)
 im=Image.new('RGB',(W,H),'#101b2a');im.paste(Image.fromarray(np.flipud(pixels)),(PANEL,0));d=ImageDraw.Draw(im);d.rectangle((0,0,PANEL-1,H),fill='#1b2b3f')
 d.text((28,29),'ADVANCED TINKERING / TWELVE STACKS',font=SMALL,fill='#a9c2d7');y=wrap(d,scenes[i]['title'],(28,90),375,TITLE,'#f0f6fc')+30
 for txt in scenes[i]['bullets']:
  d.ellipse((29,y+9,36,y+16),fill='#ffcf5b');y=wrap(d,txt,(52,y),350,BODY,'#d5e5f1')+24
 for yy,col,txt in [(671,'#d58b50','Updated copper parts'),(711,'#ffcf5b','Proposed braze regions'),(751,'#45b5de','Water-channel overlay')]:
  d.rectangle((29,yy+4,43,yy+17),fill=col);d.text((55,yy),txt,font=SMALL,fill='#d7e6ef')
 wrap(d,'Concept only. Existing grooves need redesign; CAD files are unchanged.',(28,804),375,SMALL,'#efcb77')
 def label(txt,p,xy,col='#e5eff8'):
  ren.SetWorldPoint(*p,1);ren.WorldToDisplay();x,y,_=ren.GetDisplayPoint();x+=PANEL;y=H-y
  d.line((x,y,xy[0],xy[1]+11),fill=col,width=2);d.ellipse((x-4,y-4,x+4,y+4),fill=col);box=d.textbbox(xy,txt,font=SMALL);d.rectangle((box[0]-6,box[1]-4,box[2]+6,box[3]+5),fill='#17283a');d.text(xy,txt,font=SMALL,fill=col)
 if i==0:
  label('Cooling body',[32,-4,5],(1190,190));label('Copper backplate',[27,-16-gap,0],(1160,720))
 elif i==1:
  label('Inner continuous bond',[12.925,-9,0],(1160,240),'#ffcf5b');label('Outer continuous bond',[-22.925,-9,0],(490,230),'#ffcf5b');label('One annular water passage',[0,-5,18],(1070,740),'#80dcff')
 elif i==2:
  label('Inner joint region',[12.925,-9,0],(1150,200),'#ffcf5b');label('Outer joint region',[-22.925,-9,0],(490,210),'#ffcf5b');label('Outer magnet bores stay dry',[29,-9,0],(1120,735))
 elif i==3:
  label('Prepared backplate closes onto body',[30,-9-gap,0],(1120,730));d.text((550,105),'GOLD REVEALS THE BURIED JOINT REGIONS',font=SMALL,fill='#ffcf5b')
 else:
  label('Inner bond',[12.925,-9,0],(1080,210),'#ffcf5b');label('Outer bond',[-22.925,-9,0],(520,210),'#ffcf5b');label('Enclosed water channel',[18,-5,0],(1130,690),'#80dcff');d.text((550,105),'SECTION: HALF OF BOTH COPPER PARTS REMOVED',font=SMALL,fill='#c4d6e4')
 d.text((460,28),'23 NOV 2026 TWELVE-STACK CAD / PROPOSED JOINT OVERLAY',font=SMALL,fill='#a9c2d7');d.text((460,849),f'{i+1:02} / 05  TWO COPPER PARTS, TWO CONTINUOUS BONDS',font=SMALL,fill='#b4cadb');d.rectangle((PANEL,892,W,899),fill='#2b4054');d.rectangle((PANEL,892,PANEL+round((W-PANEL)*u),899),fill='#ffcf5b');return np.array(im)
if __name__=='__main__':
 if 'preview' in sys.argv:
  for i in range(5):Image.fromarray(frame(i,.55)).save(P/f'preview-{i}.png')
  win.Finalize();sys.exit()
 chunks=[];durations=[];params=None
 for i in range(5):
  with wave.open(str(P/f'voice-{i}.wav'),'rb') as f:p=f.getparams();raw=f.readframes(p.nframes)
  if params is None:params=p
  dur=math.ceil((p.nframes/p.framerate+1.2)*FPS)/FPS;durations.append(dur);lead=round(.4*p.framerate);tail=round(dur*p.framerate)-lead-p.nframes;chunks.append(bytes(lead*p.sampwidth*p.nchannels)+raw+bytes(tail*p.sampwidth*p.nchannels))
 with wave.open(str(P/'narration.wav'),'wb') as f:
  f.setparams(params)
  for chunk in chunks:f.writeframes(chunk)
 writer=imageio_ffmpeg.write_frames(str(P/'silent.mp4'),(W,H),fps=FPS,codec='libx264',quality=8,macro_block_size=1);writer.send(None)
 for i,dur in enumerate(durations):
  for n in range(round(dur*FPS)):writer.send(frame(i,n/(dur*FPS)))
  print(f'Scene {i+1}/5 complete ({dur:.1f}s)',flush=True)
 writer.close();win.Finalize();final=P/'Updated twelve-stack copper joint - explained.mp4'
 subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-y','-v','error','-i',str(P/'silent.mp4'),'-i',str(P/'narration.wav'),'-c:v','copy','-c:a','aac','-b:a','160k','-movflags','+faststart',str(final)],check=True)
 print(f'COMPLETE {sum(durations):.1f}s: {final}',flush=True)
