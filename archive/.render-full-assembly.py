import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg

W,H=1280,720
BG=(16,24,36)
steel=(150,174,191)
dark=(94,115,137)
copper=(226,144,84)
ceramic=(224,226,213)
green=(104,169,148)
purple=(155,125,211)
blue=(71,171,225)
red=(237,129,101)
gold=(222,184,96)
silver=(208,220,233)
def font(n,b=False):
    return ImageFont.truetype('C:/Windows/Fonts/'+('segoeuib.ttf' if b else 'segoeui.ttf'),n)
big,medium,body,small=font(44,True),font(26,True),font(22),font(17)
stages=[
 ('Feedthrough and mounting plate','Seat the KF25 stub and seal. Close the clamp around both flange rims.'),
 ('Grounded stem','Seat the hollow stem against the NW100 plate. The circumferential weld bonds them.'),
 ('Live conductor and ceramic guide','The rod socket grips the feedthrough tube. The ceramic guide centers the rod.'),
 ('Coolant tubes and head carrier','Two sealed tubes cross the plate. The ceramic carrier isolates the live head.'),
 ('Nine magnets and locator','Seat one center magnet and eight outer magnets in the 5 mm locator against the yoke.'),
 ('Water-cooled cathode','Seat the copper body on the front of the yoke. Seal the channel with the copper cover.'),
 ('Al target and retaining ring','Seat the 2-inch target, lower the retaining ring, then insert its three screws.'),
 ('Grounded shield','Slide the shield over the head onto its grounded seat. The lip covers the clamp.'),
 ('Trace the coolant','Supply → stem → yoke crossings → C-shaped channel → return.'),
 ('Assembled gun','Rear service connections stay outside the chamber. The target head faces the substrate.')
]
D=4.2
def ease(u):
    u=max(0,min(1,u))
    return u*u*(3-2*u)
def frame(t):
    step=min(9,int(t/D))
    local=t-step*D
    close=step in (4,5,6,7)
    cut=step in (2,3,4,5,8)
    spin=.50 if close else .34
    tilt=.21 if close else .13
    scale=3.05 if close else 2.72
    pivot=102 if close else 51
    faces=[]
    def project(p):
        x,y,z=p
        v=z-pivot
        return (640+scale*(math.cos(spin)*v+math.sin(spin)*x),
                365+scale*(tilt*v-.95*y-.13*x),
                math.sin(spin)*v-math.cos(spin)*x-.21*y)
    def face(points,col,light):
        pts=[project(p) for p in points]
        faces.append((sum(p[2] for p in pts)/len(pts),[p[:2] for p in pts],tuple(int(v*light) for v in col)))
    def cyl(r,a,b,col,bore=0,x=0,y=0,section=False):
        n=36
        def p(rad,theta,z):
            return (x+rad*math.cos(theta),y+rad*math.sin(theta),z)
        for i in range(n):
            u,v=i*math.tau/n,(i+1)*math.tau/n
            if section and math.cos((u+v)/2)<.20:
                continue
            light=.66+.31*(.5+.5*math.sin(u+.35))
            face([p(r,u,a),p(r,v,a),p(r,v,b),p(r,u,b)],col,light)
            if bore:
                face([p(bore,u,a),p(bore,v,a),p(bore,v,b),p(bore,u,b)],col,.63)
            for z in [a,b]:
                face([p(bore,u,z),p(r,u,z),p(r,v,z),p(bore,v,z)],col,.94)
    def moved(stage,start=0,span=2.3,dist=31):
        return dist*(1-ease((local-start)/span)) if step==stage else 0
    def polar(r,a):
        return r*math.cos(a),r*math.sin(a)
    ports=[polar(14,3*math.pi/8),polar(14,11*math.pi/8)]
    # z=0 is the atmosphere-side face of the gun plate.
    off=moved(0,.1,2.3,-42)
    cyl(3.2,-111+off,41+off,copper,2.4)
    cyl(6,-66+off,-39+off,ceramic,3.2)
    cyl(6,-17+off,-4+off,ceramic,3.2)
    cyl(20,-22+off,-17+off,steel,6)
    cyl(16,-17+off,-15+off,gold,11)
    cyl(20,-15,0,steel,11)
    if step or local>2.4:
        clamp=moved(0,2.4,1.3,29)
        cyl(25,-24,-10,dark,19.9,y=clamp,section=step==0)
    cyl(65,0,12,steel,11)
    if step>=1:
        stem=moved(1)
        cyl(27,12+stem,121+stem,steel,24,section=cut)
        cyl(28,12+stem,14+stem,dark,27,section=cut)
    if step>=2:
        rod=moved(2,.1,2.4)
        if cut:
            cyl(3.2,41+rod,138+rod,copper)
            cyl(5,34+rod,45+rod,gold,3.22)
            guide=moved(2,1.4,2,25)
            cyl(23.8,69+guide,75+guide,ceramic,20,section=True)
            cyl(7,69+guide,75+guide,ceramic,3.3)
            for x in [-13,13]:
                cyl(6.5,69+guide,75+guide,ceramic,x=x)
    if step>=3:
        off=moved(3,0,2.1,-25)
        for idx,(x,y) in enumerate(ports):
            col=[blue,red][idx]
            cyl(4,-25+off,0+off,col,2,x,y)
            if cut:
                cyl(2.25,12+off,151+off,col,1.65,x,y)
        carrier=moved(3,1.0,2.5,30)
        cyl(26,121+carrier,127+carrier,ceramic,12,section=cut)
    if step>=4:
        yp=moved(4,.2,2.3,39)
        lp=yp+moved(4,.7,2.3,-18)
        mp=lp+moved(4,1.25,2.55,-22)
        cyl(34.4,138+yp,146+yp,dark,4,section=step==8)
        # Expose the magnet faces by cutting away the schematic locator in close-up.
        cyl(30,133+lp,138+lp,purple,0,section=step in (4,5,8))
        for i in range(8):
            x,y=polar(21,i*math.tau/8)
            cyl(5,133+mp,138+mp,green,x=x,y=y)
        cyl(9,133+mp,138+mp,green)
    if step>=5:
        head=moved(5,.1,2.5,43)
        lid=moved(5,1.2,2.5,24)
        cyl(34.4,146+head,152+head,copper,section=step in (5,8))
        cyl(34.4,152+head+lid,158+head+lid,copper,section=step==8)
    if step>=6:
        target=moved(6,0,1.55,38)
        ring=moved(6,.8,1.8,29)
        screws=moved(6,1.7,2.2,33)
        cyl(25.4,158+target,164+target,silver)
        cyl(34.4,159+ring,164+ring,dark,25.6)
        cyl(34.4,164+ring,166+ring,dark,24)
        for i in range(3):
            x,y=polar(29.4,math.pi/2+i*math.tau/3)
            cyl(1.5,151+screws,164+screws,silver,x=x,y=y)
            cyl(2.8,164+screws,166+screws,silver,x=x,y=y)
    if step>=7:
        shield=moved(7,.2,2.8,54)
        cyl(39,121+shield,171+shield,steel,36.4,section=step in (7,8))
        cyl(39,169+shield,171+shield,steel,23.4,section=step in (7,8))
    im=Image.new('RGB',(W,H),BG)
    d=ImageDraw.Draw(im)
    d.line((55,366,1225,366),fill=(42,59,77),width=1)
    for _,pts,col in sorted(faces,key=lambda f:f[0]):
        d.polygon(pts,fill=col)

    def trace(points,col,width=5):
        d.line([project(p)[:2] for p in points],fill=col,width=width,joint='curve')
    if step in (5,8):
        channel=[(*polar(21,.63+i*5.75/80),151) for i in range(81)]
        p0,p1=ports
        if step==5:
            trace([(x,y,z+head) for x,y,z in channel],blue,5)
        else:
            supply=[(*p0,-25),(*p0,146),channel[0]]
            returns=[channel[-1],(*p1,146),(*p1,-25)]
            for path,col in [(supply,blue),(channel,blue),(returns,red)]:
                trace(path,col,6)
            route=supply+channel[1:]+returns[1:]
            lengths=[0]
            for a,b in zip(route,route[1:]):
                lengths.append(lengths[-1]+math.dist(a,b))
            for i in range(13):
                s=(local*85+i*lengths[-1]/13)%lengths[-1]
                j=next(j for j in range(1,len(lengths)) if lengths[j]>s)
                f=(s-lengths[j-1])/(lengths[j]-lengths[j-1])
                x,y,_=project(tuple(a+(b-a)*f for a,b in zip(route[j-1],route[j])))
                d.ellipse((x-4,y-4,x+4,y+4),fill=(244,250,255))
    d.text((55,42),'2-inch magnetron assembly',font=big,fill='#f1f6fb')
    name,caption=stages[step]
    d.text((58,105),f'{step+1:02d} / 10    {name}',font=medium,fill='#aac8e2')
    def tag(text,xy,anchor):
        x,y=xy
        px,py,_=project(anchor)
        d.line((x,y+8,px,py),fill='#b7cadd',width=2)
        d.ellipse((px-3,py-3,px+3,py+3),fill='#e8f2fc')
        b=d.textbbox(xy,text,font=small)
        d.rectangle((b[0]-5,b[1]-3,b[2]+5,b[3]+3),fill=BG)
        d.text(xy,text,font=small,fill='#e7f0f7')
    if step==4:
        tag('5 mm magnet locator',(480,214),(0,24,135+lp))
        tag('Steel yoke',(850,236),(0,30,142+yp))
        tag('Center + 8 outer magnets',(390,524),(0,-17,135+mp))
    if step==5:
        tag('Copper channel body',(490,224),(0,29,149+head))
        tag('Copper cover / target seat',(800,215),(0,29,155+head+lid))
    if step==8:
        tag('Supply fitting',(430,240),(*ports[0],-24))
        tag('C-shaped channel',(896,219),channel[36])
        tag('Return fitting',(464,520),(*ports[1],-24))
    d.rectangle((0,621,W,H),fill='#1c2a3c')
    d.text((55,638),caption,font=body,fill='#eaf3f9')
    note={3:'Proposed carrier attachment and tube penetrations',4:'5 mm is illustrative. Locator retention and cathode fastening are open.',5:'Proposed channel closure and tube joints',7:'Proposed shield attachment to grounded stem',8:'Flow animation shows routing, with speed illustrative',9:'Chamber mounts at NW100 flange. Rear terminal cover is schematic.'}.get(step,'Concept assembly geometry')
    d.text((56,680),note,font=small,fill='#a7bdd1')
    if step==9:
        d.rounded_rectangle((90,193,518,226),5,outline='#617f97')
        d.text((102,198),'Grounded terminal enclosure envelope',font=small,fill='#b0c7dd')
    return np.asarray(im)

out='C:/Users/Aryamman/Documents/ChatGPT/sputter/magnetron-full-assembly.mp4'
fps=18
writer=imageio_ffmpeg.write_frames(out,(W,H),fps=fps,codec='libx264',quality=8,output_params=['-movflags','+faststart'])
writer.send(None)
for i in range(round(fps*D*len(stages))):
    writer.send(frame(i/fps))
writer.close()

