from pathlib import Path
import json, math, struct
import numpy as np
from PIL import Image,ImageDraw,ImageFont
import vtk
from vtk.util.numpy_support import numpy_to_vtk,numpy_to_vtkIdTypeArray,vtk_to_numpy

P=Path(__file__).resolve().parent
sma=(0,4.5);hoses=[(-5.4,-3.6),(5.4,-3.6)]
distance=math.dist(sma,hoses[0])
report={
 'tube_OD_mm':25.4,'tube_wall_mm':1.5,'tube_bore_mm':22.4,
 'end_plate_OD_mm':25.2,'end_plate_thickness_mm':2,
 'SMA_center_X_Z_mm':sma,'hose_centers_X_Z_mm':hoses,
 'SMA_pilot_diameter_mm':6.5,'hose_guide_holes_mm':7.2,'vent_diameter_mm':2,
 'SMA_washer_nominal_OD_mm':10.2,'hose_guide_flange_OD_mm':8,
 'maximum_hose_OD_mm':6,'hose_guide_bore_mm':6.3,
 'nominal_SMA_to_guide_gap_mm':distance-5.1-4,
 'nominal_guide_to_bore_gap_mm':11.2-math.hypot(*hoses[0])-4,
 'nominal_plate_web_between_SMA_and_hose_holes_mm':distance-3.25-3.6,
 'worst_case_assumptions':{'minimum_bore_mm':22.2,'maximum_washer_OD_mm':10.6,'maximum_guide_OD_mm':8.1,'center_position_tolerance_each_axis_mm':.05},
 'conservative_worst_case_SMA_to_guide_gap_mm':distance-5.3-4.05-2*math.sqrt(2)*.05,
 'conservative_worst_case_guide_to_bore_gap_mm':11.1-math.hypot(*hoses[0])-4.05-math.sqrt(2)*.05,
 'maximum_fixed_radial_envelope_nominal_mm':12.7,
 'qualification':'Mechanical packaging only. Actual eBay gland bore, weld finish, coax electrical rating, cooling performance and upper tube transition remain unverified.'
}
assert report['conservative_worst_case_SMA_to_guide_gap_mm']>.2
assert report['conservative_worst_case_guide_to_bore_gap_mm']>.4
audit=json.loads((P/'native-verification.json').read_text(encoding='utf-8-sig'))
assert audit['components']==10 and all(q['check']==1 for q in audit['parts'])
assert not audit['interferences'],audit['interferences']
report['native_solid_checks']='8 unique native solids valid; 10 assembly instances'
report['native_interferences']=0
(P/'packaging-verification.json').write_text(json.dumps(report,indent=2))

F=lambda n,b=False:ImageFont.truetype('C:/Windows/Fonts/'+('segoeuib.ttf' if b else 'segoeui.ttf'),n)
im=Image.new('RGB',(1800,1250),'#f5f7fa');d=ImageDraw.Draw(im)
ink='#1b2c3e';muted='#4d6072';blue='#2b6cab';gold='#bf8b30'
d.text((55,35),'ONE-INCH TERMINAL / R01 MECHANICAL FIT',font=F(43,True),fill=ink)
d.text((55,100),'Front view from atmosphere  |  All dimensions in mm  |  Original magnetron head unchanged',font=F(27),fill=muted)
cx,cy,scale=450,540,25
def pt(x,z):return cx+x*scale,cy-z*scale
def circle(x,z,r,fill,outline=ink,width=2):
 X,Y=pt(x,z);d.ellipse((X-r*scale,Y-r*scale,X+r*scale,Y+r*scale),fill=fill,outline=outline,width=width)
circle(0,0,12.7,'#9aa7b2');circle(0,0,12.6,'#d9e0e6')
# Bore reference, dashed to distinguish it from an actual front-face edge.
for a in range(0,360,12):
 r=11.2*scale;d.arc((cx-r,cy-r,cx+r,cy+r),a,a+6,fill=muted,width=2)
circle(*sma,5.1,'#e7cb86',gold);circle(*sma,3.175,'#bd8b3c',gold);circle(*sma,.55,'#324659')
for x,z in hoses:
 circle(x,z,4,'#ede9d9');circle(x,z,3.15,'#aeb7b8');circle(x,z,3,'#4c96ce');circle(x,z,2,'#173d60')
circle(0,-9,1,'#354a5e')
def leader(text,point,xy):
 X,Y=pt(*point);d.line((X,Y,xy[0],xy[1]+17),fill=muted,width=2);d.text(xy,text,font=F(27),fill=ink)
leader('SMA socket + retaining hardware',(0,7.5),(75,165))
leader('Two hose guides',(-8.8,-3.6),(35,900))
leader('Open atmospheric vent',(0,-9),(320,980))
d.line((cx-12.7*scale,cy-12.7*scale-22,cx+12.7*scale,cy-12.7*scale-22),fill=ink,width=2)
d.text((cx+130,cy-12.7*scale-65),'25.4 max envelope',font=F(27),fill=ink)
lines=[('Tube','25.4 OD x 1.5 wall; 22.4 bore'),('End plate','25.2 OD x 2.0 thick; flush attachment'),('SMA center','X = 0; Z = +4.5'),('Hose centers','X = +/-5.4; Z = -3.6'),('SMA hole','6.5 diameter / 6.0 high D-shaped hole'),('Hose-guide holes','2 x 7.2; guides 8.0 OD / 6.3 bore'),('Vent','2.0 diameter at X = 0; Z = -9.0'),('Hose allowance','Up to 6.0 OD each; 4.0 OD also fits'),('Internal coax allowance','5.0 OD; final cable rating pending')]
y=185
for title,value in lines:
 d.text((915,y),title,font=F(27,True),fill=ink);d.text((915,y+38),value,font=F(26),fill=muted);y+=86
d.text((55,1060),f'Nominal hardware gap: {report["nominal_SMA_to_guide_gap_mm"]:.2f}  |  Conservative tolerance check: {report["conservative_worst_case_SMA_to_guide_gap_mm"]:.2f}',font=F(29,True),fill=ink)
d.text((55,1115),'SMA packaging reference: Amphenol 132118; rear crimp avoids a loose solder-cup termination.',font=F(27),fill=muted)
d.text((55,1165),'Mechanical fit study, not an RF qualification. Gland passage and finished weld envelope must be checked.',font=F(26),fill=muted)
im.save(P/'One inch terminal - dimensioned layout.png')

def string(f):
 b=f.read(1)
 if not b:return None
 n=b[0]&127;shift=7
 while b[0]&128:b=f.read(1);n|=(b[0]&127)<<shift;shift+=7
 return f.read(n).decode()
ren=vtk.vtkRenderer();ren.SetBackground(.063,.106,.165)
window=vtk.vtkRenderWindow();window.SetOffScreenRendering(1);window.SetSize(1500,1100);window.SetMultiSamples(4);window.AddRenderer(ren)
records=[]
with (P/'terminal-mesh.bin').open('rb') as f:
 while name:=string(f):
  file=string(f);n=struct.unpack('<i',f.read(4))[0];v=np.frombuffer(f.read(n*36),'<f4').reshape(-1,3)
  poly=vtk.vtkPolyData();points=vtk.vtkPoints();points.SetData(numpy_to_vtk(v,deep=True));poly.SetPoints(points);cells=vtk.vtkCellArray();cells.SetData(numpy_to_vtkIdTypeArray(np.arange(0,len(v)+1,3,dtype=np.int64),deep=True),numpy_to_vtkIdTypeArray(np.arange(len(v),dtype=np.int64),deep=True));poly.SetPolys(cells)
  clean=vtk.vtkCleanPolyData();clean.SetInputData(poly);clean.Update();poly=clean.GetOutput()
  if file.startswith('01'):
   planes=vtk.vtkPlaneCollection();p=vtk.vtkPlane();p.SetNormal(-1,0,0);planes.AddItem(p);clip=vtk.vtkClipClosedSurface();clip.SetInputData(poly);clip.SetClippingPlanes(planes);clip.Update();poly=clip.GetOutput()
  normals=vtk.vtkPolyDataNormals();normals.SetInputData(poly);normals.SetFeatureAngle(30);normals.Update();mapper=vtk.vtkPolyDataMapper();mapper.SetInputData(normals.GetOutput());mapper.ScalarVisibilityOff();a=vtk.vtkActor();a.SetMapper(mapper)
  c=(.60,.68,.74)
  if file[:2] in ['03','04','05']:c=(.84,.64,.24)
  if file.startswith('06'):c=(.9,.88,.77)
  if file.startswith('07'):c=(.15,.46,.8)
  if file.startswith('08'):c=(.2,.22,.25)
  a.GetProperty().SetColor(*c);a.GetProperty().SetAmbient(.25);a.GetProperty().SetSpecular(.28);a.GetProperty().SetSpecularPower(30);ren.AddActor(a);records.append(a)
camera=ren.GetActiveCamera();camera.ParallelProjectionOn();camera.SetFocalPoint(0,-20,0);camera.SetPosition(130,150,95);camera.SetViewUp(0,0,1);camera.SetParallelScale(43);ren.ResetCameraClippingRange();window.Render()
capture=vtk.vtkWindowToImageFilter();capture.SetInput(window);capture.ReadFrontBufferOff();capture.SetInputBufferTypeToRGB();capture.Update();v=vtk_to_numpy(capture.GetOutput().GetPointData().GetScalars()).reshape(1100,1500,3);im=Image.fromarray(np.flipud(v));d=ImageDraw.Draw(im)
def label(text,p,xy):
 ren.SetWorldPoint(*p,1);ren.WorldToDisplay();x,y,_=ren.GetDisplayPoint();y=1100-y;d.line((x,y,xy[0],xy[1]+16),fill='#dfeaf5',width=2);d.ellipse((x-4,y-4,x+4,y+4),fill='#dfeaf5');box=d.textbbox(xy,text,font=F(27));d.rectangle((box[0]-4,box[1]-3,box[2]+4,box[3]+3),fill='#101b2a');d.text(xy,text,font=F(27),fill='#e6eef6')
d.text((35,25),'ACTUAL SOLIDWORKS SUBASSEMBLY / TUBE SECTIONED',font=F(31,True),fill='#e6eef6')
label('SMA socket / cable unplugged',(0,10,4.5),(70,180))
label('Flush end plate / 25.2 OD',(10,1,0),(990,160))
label('Two hoses / 6 mm maximum study OD',(5.4,27,-3.6),(850,920))
label('Shielded internal coax',(0,-28,4.5),(70,830))
label('25.4 OD tube / 22.4 bore',(-10,-35,0),(80,480))
d.text((35,1040),'Connector and cables are mechanical envelopes; source head and its water seals are unchanged.',font=F(25),fill='#b9cbdc')
im.save(P/'One inch terminal - native CAD cutaway.png');window.Finalize()
print(json.dumps(report,indent=2))
