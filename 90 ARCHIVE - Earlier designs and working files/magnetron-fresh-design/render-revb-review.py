import math,struct,runpy
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parent
helper=runpy.run_path(str(ROOT/'render-video.py'));rasterize=helper['rasterize'];clip_mesh=helper['clip_mesh'];wrap=helper['wrap']
parts=[]
with (ROOT/'RevB/actual-head-mesh.bin').open('rb') as f:
    while first:=f.read(1):
        n=first[0]&127;shift=7
        while first[0]&128:first=f.read(1);n|=(first[0]&127)<<shift;shift+=7
        name=f.read(n).decode();count=struct.unpack('<i',f.read(4))[0];v=np.frombuffer(f.read(count*36),'<f4').reshape(-1,3,3).astype(float)
        code=name.split()[0];parts.append((code,v))
assert len(parts)==15
def ft(n,b=False):return ImageFont.truetype('C:/Windows/Fonts/'+('segoeuib.ttf' if b else 'segoeui.ttf'),n)
TITLE,BODY,SMALL=ft(36,True),ft(25),ft(18)
palette={'F01-001':(217,143,90),'F01-002':(65,163,159),'F01-003':(218,73,73),'F01-004':(79,128,229),'F01-005':(130,148,169),'F01-006':(219,205,160),'F01-007':(173,186,200)}
for mode in ['exploded','cutaway','assembled']:
    W,H=1600,1000;scene=[];colors=[];cutedges=[]
    shiftmap={'F01-001':80,'F01-002':40,'F01-005':-40,'F01-006':-20} if mode=='exploded' else {}
    for code,v in parts:
        vv=v.copy();vv[:,:,0]+=shiftmap.get(code,0)
        if mode=='cutaway' and code in ['F01-001','F01-002','F01-005','F01-006']:
            vv[:,:,1]=np.where(np.abs(vv[:,:,1])<1e-5,0,vv[:,:,1])
            vv,_,edges=clip_mesh(vv);cutedges.extend(edges)
        scene.append(vv);colors.append(np.tile(palette[code],(len(vv),1)))
    vertices=np.concatenate(scene);rgb=np.concatenate(colors).astype(float)
    yaw,elevation,scale,center,origin=(1.12,.25,5.4,np.array([12.,0,0]),(1010,480)) if mode=='exploded' else (1.05,.20,8.2,np.array([-7.5,0,0]),(1035,480))
    if mode=='assembled':yaw=.75;scale=8.5
    cy,sy=math.cos(yaw),math.sin(yaw);ce,se=math.cos(elevation),math.sin(elevation)
    def proj(points):
        x,y,z=np.moveaxis(np.asarray(points)-center,-1,0);depth=-x*cy+y*sy
        return np.stack((origin[0]+scale*(x*sy+y*cy),origin[1]-scale*(z*ce-depth*se),depth*ce+z*se),axis=-1)
    tri=proj(vertices);normal=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);normal/=np.maximum(np.linalg.norm(normal,axis=1,keepdims=True),1e-8)
    rgb=np.clip(rgb*(.48+.45*np.abs(normal@np.array([-.2,-.4,.89])))[:,None]+7,0,255).astype('uint8')
    im=Image.new('RGB',(W,H),'#101b2a');draw=ImageDraw.Draw(im);draw.rectangle((0,0,436,H),fill='#1b2b3f')
    draw.text((30,30),'F01 / MAGNETIC COOLING HEAD / REV B',font=SMALL,fill='#a9c2d7')
    titles={'exploded':'Magnets now have a defined home','cutaway':'Dry wells bring the poles forward','assembled':'The revised magnetic head'}
    y=wrap(draw,titles[mode],(30,100),370,TITLE,'#f1f7fb')+35
    bullets=['Six outer rods: D8 x 20 mm','Center: two D12 x 10 mm discs','Magnet pack and ports checked together'] if mode=='exploded' else ['Seven dry wells through the coolant region','4 mm from pole tips to target seat','Eight primary O-ring locations'] if mode=='cutaway' else ['82 mm head diameter','15 candidate part instances','Zero nominal solid interferences']
    for text in bullets:y=wrap(draw,text,(30,y),365,BODY,'#d5e5f1')+25
    y=610
    for code,name in [('F01-001','Copper body'),('F01-002','Coolant cover'),('F01-003','Outer magnets: N toward target'),('F01-004','Center stack: S toward target'),('F01-005','Steel return yoke'),('F01-006','Dry magnet locator')]:
        draw.rectangle((30,y+5,43,y+18),fill=palette[code]);draw.text((55,y),name,font=SMALL,fill='#d5e5f1');y+=39
    wrap(draw,'Concept CAD. Magnetic field, cooling and seal performance remain unverified.',(30,890),370,SMALL,'#edc968')
    im=Image.fromarray(rasterize(np.array(im),tri,rgb));draw=ImageDraw.Draw(im)
    def line(points,color,width=2):
        p=proj(np.asarray(points));draw.line([tuple(q[:2]) for q in p],fill=color,width=width)
    def label(text,point,xy,color='#e5eff8'):
        p=proj(np.array(point));draw.line((p[0],p[1],xy[0],xy[1]+12),fill=color,width=2)
        draw.ellipse((p[0]-4,p[1]-4,p[0]+4,p[1]+4),fill=color)
        draw.rounded_rectangle((xy[0]-6,xy[1]-2,xy[0]+draw.textlength(text,font=SMALL)+6,xy[1]+28),radius=4,fill='#17283a');draw.text(xy,text,font=SMALL,fill=color)
    if mode=='exploded':
        label('Body: integral dry wells',[80,-20,0],(1260,135),'#f3b77d')
        label('Cover: magnets pass through',[40,-20,-4],(1130,820),'#84dfd9')
        label('Six outer magnets',[0,20,0],(860,155),'#f18d8d')
        label('Center stack',[0,0,0],(760,780),'#9cbcff')
        label('Steel yoke',[-60,-20,0],(485,150),'#ccd7e7')
        draw.text((480,941),'ACTUAL CAD MESH / DISPLAY OFFSETS ARE ILLUSTRATIVE / O-RINGS AND SCREWS NOT SHOWN',font=SMALL,fill='#a9c2d7')
    if mode=='cutaway':
        label('Outer magnet in its reserved dry well',[1,20,0],(1120,135),'#f18d8d')
        label('Central two-disc stack',[-3,0,0],(560,210),'#9cbcff')
        label('Target seating face',[7,0,-22],(1180,820),'#f3b77d')
        line([[3,0,-5],[7,0,-5]],'#ffffff',4)
        label('4 mm pole-to-seat separation',[5,0,-5],(1000,730))
        label('Load-bearing spacer',[-10,37,0],(580,820))
        draw.text((480,941),'CUTAWAY: HALF OF BODY, COVER, YOKE AND LOCATOR REMOVED / MAGNETS KEPT WHOLE',font=SMALL,fill='#a9c2d7')
    if mode=='assembled':
        label('Port bosses between outer magnet axes',[-11,22.5167,13],(1030,145),'#84dfd9')
        label('Magnet return yoke',[-22,-20,0],(560,790),'#ccd7e7')
        draw.text((480,941),'ACTUAL CAD ASSEMBLY / MAIN VACUUM HOUSING AND RF FEEDTHROUGH CONNECTION STILL TO DESIGN',font=SMALL,fill='#a9c2d7')
    out=ROOT/'RevB'/f'RevB review {mode}.png';im.save(out);print(out)
