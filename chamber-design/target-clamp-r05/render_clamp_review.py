from pathlib import Path
import cadquery as cq,numpy as np,vtk,json,math
from vtk.util.numpy_support import numpy_to_vtk,numpy_to_vtkIdTypeArray,vtk_to_numpy
from PIL import Image,ImageDraw,ImageFont
P=Path(__file__).resolve().parent;ROOT=P.parent.parent
s=cq.importers.importStep(str(P/'Target clamp R05 - 3.175mm target.step')).val();t=cq.importers.importStep(str(P/'Aluminium target D50.8 x3.175.step')).val();c=cq.importers.importStep(str(ROOT/'advanced-tinkering-original/balanced-twelve-stack-study/Proposed cooler.step')).val()
W,H=1600,1000;im=Image.new('RGB',(W,H),'#101c2b');d=ImageDraw.Draw(im);ft=lambda n,b=False:ImageFont.truetype('C:/Windows/Fonts/'+('segoeuib.ttf' if b else 'segoeui.ttf'),n)
d.text((36,20),'Target clamp R05 - 3.175 mm aluminium target',font=ft(31,True),fill='#edf4fa')
win=vtk.vtkRenderWindow();win.SetOffScreenRendering(1);win.SetSize(760,650);win.SetMultiSamples(0);r=vtk.vtkRenderer();r.SetBackground(.055,.09,.14);win.AddRenderer(r)
def actor(shape,col):
 v,f=shape.tessellate(.09,.18);a=np.array([x.toTuple() for x in v],np.float32)[np.array(f)];pd=vtk.vtkPolyData();pt=vtk.vtkPoints();pt.SetData(numpy_to_vtk(a.reshape(-1,3),deep=True));pd.SetPoints(pt);cells=vtk.vtkCellArray();cells.SetData(numpy_to_vtkIdTypeArray(np.arange(0,len(a)*3+1,3,dtype=np.int64)),numpy_to_vtkIdTypeArray(np.arange(len(a)*3,dtype=np.int64)));pd.SetPolys(cells);norm=vtk.vtkPolyDataNormals();norm.SetInputData(pd);norm.Update();mp=vtk.vtkPolyDataMapper();mp.SetInputConnection(norm.GetOutputPort());ac=vtk.vtkActor();ac.SetMapper(mp);ac.GetProperty().SetColor(*col);ac.GetProperty().SetAmbient(.35);ac.GetProperty().SetDiffuse(.65);ac.GetProperty().SetSpecular(.25);r.AddActor(ac);return ac
half=cq.Solid.makeBox(120,30,60,cq.Vector(-60,-15,0));actor(s.intersect(half),(.64,.71,.76));actor(t.intersect(half),(.82,.85,.89));actor(c.intersect(half),(.81,.36,.14))
cam=r.GetActiveCamera();cam.SetPosition(85,110,-75);cam.SetFocalPoint(0,-1,0);cam.SetViewUp(0,1,0);cam.ParallelProjectionOn();cam.SetParallelScale(57);r.ResetCameraClippingRange();win.Render();cap=vtk.vtkWindowToImageFilter();cap.SetInput(win);cap.ReadFrontBufferOff();cap.Update();arr=vtk_to_numpy(cap.GetOutput().GetPointData().GetScalars()).reshape(650,760,3);im.paste(Image.fromarray(np.flipud(arr)),(20,90));win.Finalize()
d.text((55,760),'Sectioned CAD: copper head, aluminium target, revised clamp',font=ft(20),fill='#cad9e6')
# Dimensioned local axial section: true profile coordinates, magnified equally in both axes.
x0,y0,scale=1160,470,33
xy=lambda rad,y:(x0+(rad-25)*scale,y0-y*scale)
old=[(23.9,2.25),(23.9,3),(25.9,5)];profile=[(35.25,3.175),(24.15,3.175),(23.9,3.425),(23.9,4.175),(24.725,5),(35.25,5)]
d.polygon([xy(*p) for p in profile],fill='#9aaab8',outline='#dae5ed',width=2)
d.polygon([xy(21.5,0),xy(25.4,0),xy(25.4,3.175),xy(21.5,3.175)],fill='#d5dce4',outline='#f2f6fa',width=2)
for a,b in zip(old,old[1:]):d.line([xy(*a),xy(*b)],fill='#ffb867',width=3)
d.text((835,98),'Clamping lip - enlarged axial section',font=ft(23,True),fill='#edf4fa')
d.text((835,140),'Grey: R05   Orange: previous aperture profile',font=ft(19),fill='#ffcc8b')
def dim(a,b,label,offset=(0,0)):
 A=xy(*a);B=xy(*b);d.line([A,B],fill='#7ce0ce',width=2)
 for X,Y in [A,B]:d.line([(X-5,Y),(X+5,Y)],fill='#7ce0ce',width=2)
 d.text(((A[0]+B[0])/2+offset[0],(A[1]+B[1])/2+offset[1]),label,font=ft(19,True),fill='#7ce0ce')
dim((20.8,0),(20.8,3.175),'3.175 mm',(-112,-12));dim((32.5,3.175),(32.5,5),'1.825 mm',(-112,-12));d.text((980,490),'Target back remains at Y = 0',font=ft(18),fill='#d9e6f0')
facts=['Clamp OD 93.6 mm; 12 holes on PCD 80 mm','Contact shoulder: Y3.175 mm; front face: Y5.000 mm','Minimum aperture 47.8 mm; contact band 1.25 mm','0.25 mm contact-edge chamfer; front opening 49.45 mm','Counterbores unchanged: D5.7; seat at Y1.0 mm','12 x M3x10 screws; nominal shield clearance 1.0 mm']
y=570
for text in facts:d.text((825,y),text,font=ft(20),fill='#edf4fa');y+=38
d.text((36,845),'Default target-to-substrate gap retained at 100 mm by raising the complete gun 1.175 mm.',font=ft(22,True),fill='#7ce0ce')
d.text((36,892),'Nominal interference checks passed. Lip stiffness, clamping preload, tolerances and thermal performance remain to qualify.',font=ft(20),fill='#d9c6a5')
d.text((36,930),'Earlier magnetic results used a 2 mm target; the revised magnet-to-target-face spacing is 5.675 mm.',font=ft(20),fill='#d9c6a5')
im.save(P/'Clamp R05 design review.png');print('Dimensioned clamp review rendered')
