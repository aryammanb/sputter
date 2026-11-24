import math,struct,runpy
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parent
helpers=runpy.run_path(str(ROOT.parent/'magnetron-fresh-design/render-video.py'))
rasterize,wrap,rawclip=helpers['rasterize'],helpers['wrap'],helpers['clip_mesh']
def string(f):
    b=f.read(1)
    if not b:return None
    n=b[0]&127;shift=7
    while b[0]&128:b=f.read(1);n|=(b[0]&127)<<shift;shift+=7
    return f.read(n).decode()
parts=[]
with (ROOT/'actual-assembly-mesh.bin').open('rb') as f:
    while name:=string(f):
        file=string(f);count=struct.unpack('<i',f.read(4))[0];v=np.frombuffer(f.read(count*36),'<f4').reshape(-1,3,3).astype(float);parts.append((name,file,v))
assert len(parts)==120
def clip(v,axis,value=0,less=True):
    order=[0,1,2];order[axis],order[1]=order[1],order[axis];temp=v[:,:,order].copy();sign=1 if less else -1
    temp[:,:,1]=(temp[:,:,1]-value)*sign;temp[:,:,1]=np.where(abs(temp[:,:,1])<1e-5,0,temp[:,:,1]);out,_,_=rawclip(temp)
    if not len(out):return np.empty((0,3,3))
    out[:,:,1]=out[:,:,1]*sign+value;return out[:,:,np.argsort(order)]
def color(file):
    if file in ['Kuehlkoerper.SLDPRT','Backplate.SLDPRT']:return (216,141,89)
    if 'outer magnet' in file:return (208,74,77)
    if 'center magnet' in file:return (79,125,217)
    if 'O-ring' in file:return (53,67,63)
    if 'PTFE' in file or file=='Isolator.SLDPRT':return (232,223,192)
    if 'blue' in file:return (57,117,212)
    if 'white HV' in file:return (235,230,211)
    if 'wire hook' in file or 'copper conductor' in file:return (220,155,87)
    if file=='Magnet Joke.SLDPRT':return (130,145,163)
    if file=='Groundshield Rohr.SLDPRT':return (116,153,169)
    if 'titanium' in file:return (179,180,186)
    return (167,181,193)
def font(n,b=False):return ImageFont.truetype('C:/Windows/Fonts/'+('segoeuib.ttf' if b else 'segoeui.ttf'),n)
TITLE,BODY,SMALL,TINY=font(34,True),font(25),font(20),font(16)
originals={'Dunkelraumabschirmung.SLDPRT','Target Klemme.SLDPRT','Kuehlkoerper.SLDPRT','Backplate.SLDPRT','Magnet Joke.SLDPRT','Abstandshalter.SLDPRT','Isolator.SLDPRT','Boden.SLDPRT'}
def offset(file,v):
    if file=='Dunkelraumabschirmung.SLDPRT':return 120
    if file=='Target Klemme.SLDPRT':return 100
    if 'titanium target' in file:return 90
    if file=='Kuehlkoerper.SLDPRT':return 70
    if file=='Backplate.SLDPRT':return 40
    if 'magnet D' in file:return 5
    if file=='Magnet Joke.SLDPRT':return 0
    if file=='Abstandshalter.SLDPRT':return -35
    if file=='Isolator.SLDPRT':return -60
    if file=='Boden.SLDPRT':return -85
    if 'O-ring' in file:
        y=v[:,:,1].mean()
        return 40 if y>-11 else -35 if y>-43 else -85
    return 0
for mode in ['assembled','cutaway','layers']:
    scene=[];colors=[]
    for name,file,v in parts:
        if mode=='layers' and not(file in originals or 'magnet D' in file or 'titanium target' in file or ('AT O-ring' in file)):continue
        vv=v.copy()
        if mode=='layers':vv[:,:,1]+=offset(file,v)
        if mode=='cutaway':
            vv=clip(vv,1,-99,False)
            if not len(vv):continue
            if not('magnet D' in file or 'blue coolant hose' in file or 'HV' in file or 'release collar' in file):vv=clip(vv,0,0,True)
            if not len(vv):continue
        scene.append(vv);colors.append(np.tile(color(file),(len(vv),1)))
    vertices=np.concatenate(scene);rgb=np.concatenate(colors).astype(float)
    W,H=1600,1000;origin=(1015,485);az=.77;elev=.16;scale=2.35;center=np.array([0,-142,0]);roll=False
    if mode=='cutaway':az=1.13;elev=.12;scale=6.5;center=np.array([0,-40,0])
    if mode=='layers':az=.83;elev=.25;scale=3.1;center=np.array([0,-12,0]);roll=True
    ca,sa=math.cos(az),math.sin(az);ce,se=math.cos(elev),math.sin(elev)
    def project(points):
        x,y,z=np.moveaxis(np.asarray(points)-center,-1,0);depth=x*sa+z*ca;h=x*ca-z*sa;vertical=y*ce-depth*se
        xx,yy=(vertical,-h) if roll else (h,vertical)
        return np.stack((origin[0]+scale*xx,origin[1]-scale*yy,depth*ce+y*se),axis=-1)
    triangles=project(vertices);normal=np.cross(triangles[:,1]-triangles[:,0],triangles[:,2]-triangles[:,0]);normal/=np.maximum(np.linalg.norm(normal,axis=1,keepdims=True),1e-8)
    shaded=np.clip(rgb*(.48+.45*np.abs(normal@np.array([-.2,-.4,.89])))[:,None]+7,0,255).astype('uint8')
    im=Image.new('RGB',(W,H),'#101b2a');draw=ImageDraw.Draw(im);draw.rectangle((0,0,436,H),fill='#1b2b3f')
    draw.text((29,30),'ADVANCED TINKERING / ORIGINAL DESIGN',font=TINY,fill='#a8c1d6')
    titles={'assembled':'Original magnetron, reconstructed','cutaway':'The sealed interior','layers':'How the original layers fit'}
    y=wrap(draw,titles[mode],(29,98),370,TITLE,'#f1f7fb')+35
    bullets={'assembled':['120 solid component instances','Original supplied geometry preserved','Reference tube, fittings and flexible utilities labeled'],
             'cutaway':['12 outer rods + 2 center discs','Continuous annular water channel','5 specified face O-rings + reference KF16 seal'],
             'layers':['Shared source coordinates retained','Layers separated only for inspection','Shield tube, hardware and utilities hidden']}[mode]
    for text in bullets:y=wrap(draw,text,(29,y),365,BODY,'#d6e5f0')+25
    for row,(c,text) in enumerate([((216,141,89),'C110 copper parts'),((130,145,163),'A36 return yoke'),((232,223,192),'PTFE insulation'),((208,74,77),'Outer poles: S toward target'),((79,125,217),'Center stack: N toward target'),((57,117,212),'Reference coolant hoses')]):
        yy=665+row*34;draw.rectangle((29,yy+5,43,yy+19),fill=c);draw.text((55,yy),text,font=TINY,fill='#d6e5f0')
    wrap(draw,'Study reconstruction / inferred service hardware is not an exact author drawing',(29,899),365,TINY,'#e6c66c')
    im=Image.fromarray(rasterize(np.array(im),triangles,shaded));draw=ImageDraw.Draw(im)
    def line(points,c,w=2):
        pp=project(np.asarray(points));draw.line([tuple(q[:2]) for q in pp],fill=c,width=w)
    def label(text,point,xy,c='#e6eff8'):
        p=project(np.array(point));draw.line((p[0],p[1],xy[0],xy[1]+12),fill=c,width=2);draw.ellipse((p[0]-4,p[1]-4,p[0]+4,p[1]+4),fill=c)
        draw.rounded_rectangle((xy[0]-6,xy[1]-2,xy[0]+draw.textlength(text,font=SMALL)+6,xy[1]+29),radius=4,fill='#17283a');draw.text(xy,text,font=SMALL,fill=c)
    if mode=='assembled':
        label('Grounded outer shield',[35,-25,35],(1120,140));label('2-inch target end',[0,15,0],(630,120))
        label('Original two-piece flange clamp',[20,-84,0],(1120,350));label('KF16 tube: 200 mm reference length',[0,-200,10],(1110,670))
        label('Atmospheric hoses and cable',[3,-290,0],(650,850),'#a8cff8')
        draw.text((475,948),'ACTUAL SOLIDWORKS TESSELLATION / COLORS DISTINGUISH MATERIALS AND FUNCTIONS',font=TINY,fill='#a8c1d6')
    if mode=='cutaway':
        label('Copper target seat',[0,0,25],(1170,140),'#f1b67c');label('12 outer rods',[0,-10,25],(1180,295),'#f18d8d')
        label('Two center discs',[0,-12.5,0],(515,150),'#a5bfff')
        label('76 x2 outer head seal',[0,-12.725,39.425],(1160,430),'#a2d3b4')
        label('PTFE ring + two 62 x2 seals',[0,-43.5,32],(1110,630),'#e9deb5')
        label('Separate screw insulation',[0,-69,39.56],(1100,810),'#e9deb5')
        # Wireframe shows the source-defined water cavity on the removed half.
        a=np.linspace(-math.pi/2,math.pi/2,100)
        for r in [11.05,16.05]:
            for yy in [-9,-2]:line(np.column_stack((r*np.cos(a),np.full(len(a),yy),r*np.sin(a))),'#6dd5ef',2)
        label('Annular water space',[13.55,-5,0],(520,355),'#83d9ef')
        label('Water seals: 14.5 x2 and 35 x2',[0,-9.725,18.425],(510,455),'#a2d3b4')
        draw.text((475,948),'HOUSINGS SECTIONED / MAGNETS AND SERVICES KEPT WHOLE / CYAN LINES MARK THE WATER SPACE',font=TINY,fill='#a8c1d6')
    if mode=='layers':
        for text,p,xy,c in [
            ('Bottom body',[0,-145,0],(500,220),'#d6e2ed'),('PTFE ring',[0,-103,0],(650,740),'#e9deb5'),
            ('Spacer',[0,-62,0],(780,205),'#d6e2ed'),('Steel yoke',[0,-27.5,0],(865,745),'#ccd7e8'),
            ('Magnets',[0,-4,25],(920,190),'#f18d8d'),('Copper closure',[0,25,0],(1040,740),'#f1b67c'),
            ('Copper cooler',[0,65,0],(1170,200),'#f1b67c'),('Target + clamp',[0,100,0],(1300,735),'#d6e2ed'),
            ('Dark-space shield',[0,130,0],(1280,150),'#d6e2ed')]:label(text,p,xy,c)
        draw.text((475,948),'ACTUAL SOURCE PARTS / AXIAL DISPLAY OFFSETS ARE ILLUSTRATIVE, NOT ASSEMBLY COORDINATES',font=TINY,fill='#a8c1d6')
    out=ROOT/f'Original magnetron - {mode}.png';im.save(out);print(out,flush=True)
