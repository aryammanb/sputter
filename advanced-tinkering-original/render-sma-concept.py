"""Mechanical connection study; original CAD remains unmodified."""
import importlib.util
from pathlib import Path
import numpy as np
import vtk
from PIL import Image,ImageDraw,ImageFont
from vtk.util.numpy_support import numpy_to_vtk,vtk_to_numpy

root=Path(__file__).resolve().parent
out=root/'sma-connection-concept';out.mkdir(exist_ok=True)
spec=importlib.util.spec_from_file_location('assembly',root/'render-full-assembly-video.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
m.window.SetSize(1200,1000)
for a in m.flow_lines+m.flow_dots:a.SetVisibility(False)
new=[]
def ring(ro,ri,y0,y1,color,sides=80):
    vs=[]
    for i in range(sides):
        a=i*2*np.pi/sides;b=(i+1)*2*np.pi/sides
        p=lambda r,y,t:[r*np.cos(t),y,r*np.sin(t)]
        for q in [[p(ro,y0,a),p(ro,y0,b),p(ro,y1,b),p(ro,y1,a)],
                  [p(ri,y0,b),p(ri,y0,a),p(ri,y1,a),p(ri,y1,b)],
                  [p(ri,y0,a),p(ri,y0,b),p(ro,y0,b),p(ro,y0,a)],
                  [p(ro,y1,a),p(ro,y1,b),p(ri,y1,b),p(ri,y1,a)]]:
            vs.extend([[q[0],q[1],q[2]],[q[0],q[2],q[3]]])
    poly=m.polydata(np.array(vs));mapper=vtk.vtkPolyDataMapper();mapper.SetInputData(poly);a=vtk.vtkActor();a.SetMapper(mapper);a.GetProperty().SetColor(*color);a.GetProperty().SetAmbient(.25);a.GetProperty().SetSpecular(.3);m.renderer.AddActor(a);new.append((a,poly));return a
steel=(.56,.64,.70);gold=(.86,.65,.23);black=(.12,.16,.20)
shell=ring(25,23,-282,-320,steel)
top=ring(25,10,-280,-282,steel)
collar=ring(16,10,-268,-280,steel)
plate=ring(25,3.3,-320,-322,steel)
socket=ring(3.5,.9,-315,-328,gold)
washer=ring(5,3.5,-322,-323,gold)
nut=ring(4.8,3.5,-317,-319,gold,6)
plug=ring(4.4,3.6,-328,-337,gold,6)
boot=ring(3,0,-337,-344,black)
external=ring(2.2,0,-344,-380,black)
coax=ring(2.2,0,-315,-220,black)
dielectric=ring(1.5,.4,-315,-220,(.9,.88,.76))
core=ring(.4,0,-315,-220,gold)
font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',27)
small=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',22)
def render(view,cut=False,unplug=False):
    for r in m.records:
        a=r['actor'];a.SetVisibility(view=='overview');a.SetPosition(0,0,0)
        a.GetMapper().SetInputData(r['poly'])
        if r['role']=='services' and 'blue' not in r['file']:a.SetVisibility(False)
    for a,p in new:
        a.SetVisibility(True);a.GetMapper().SetInputData(m.clipped(p,half=True) if cut else p);a.SetPosition(0,0,0)
    if unplug:
        for a in [plug,boot,external]:a.SetPosition(0,-18,0)
    if view=='overview':focus=np.array([0.,-173.,0.]);scale=218
    else:focus=np.array([0.,-319.,0.]);scale=65
    m.camera.SetFocalPoint(*focus);m.camera.SetPosition(*(focus+np.array([800,100,650])));m.camera.SetViewUp(0,1,0);m.camera.SetRoll(0);m.camera.SetParallelScale(scale);m.camera.SetClippingRange(500,1600)
    m.window.Render();m.capture.Modified();m.capture.Update()
    pix=vtk_to_numpy(m.capture.GetOutput().GetPointData().GetScalars()).reshape(1000,1200,3)
    im=Image.fromarray(np.flipud(pix));d=ImageDraw.Draw(im)
    def label(text,pt,xy):
        m.renderer.SetWorldPoint(*pt,1);m.renderer.WorldToDisplay();x,y,_=m.renderer.GetDisplayPoint();y=1000-y
        d.line((x,y,xy[0],xy[1]+15),fill='#dceaf5',width=2);d.ellipse((x-3,y-3,x+3,y+3),fill='#dceaf5')
        box=d.textbbox(xy,text,font=font);d.rectangle((box[0]-5,box[1]-4,box[2]+5,box[3]+4),fill='#101b2a');d.text(xy,text,font=font,fill='#e6eff6')
    if view=='overview':
        label('Existing magnetron head',[0,-20,48],(690,115));label('Atmospheric service tube',[10,-190,0],(690,425));label('New external service housing',[23,-300,0],(680,665));label('SMA cable from matchbox',[0,-370,0],(170,870))
    else:
        label('Removable metal panel',[22,-321,0],(730,540));label('Bulkhead SMA female socket',[3.5,-325,0],(630,710));label('Cable plug screws onto socket',[4.4,-333-(18 if unplug else 0),0],(60,850))
        if cut:
            label('Internal coax to gun',[1,-250,0],(690,140));label('Retaining nut + washer',[4,-318,0],(70,430));label('Metal shell bonded to panel',[4,-322,0],(690,360))
        else:label('Tube attachment / split collar',[22,-283,0],(50,150))
    d.text((25,25),'MECHANICAL CONCEPT / NEW HARDWARE IS ILLUSTRATIVE',font=small,fill='#adc2d4')
    d.text((25,955),'Original CAD tube is 20 mm; chosen 25.4 mm tube adaptation is a separate change.',font=small,fill='#adc2d4')
    im.save(out/f'{view}{"-cut" if cut else ""}.jpg',quality=90)
render('overview');render('connector',False,True);render('connector',True,False)
m.window.Finalize()
print(out)
