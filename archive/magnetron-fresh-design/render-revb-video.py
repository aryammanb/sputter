import json,math,struct,subprocess,sys,wave,runpy
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
import imageio_ffmpeg
ROOT=Path(__file__).resolve().parent;OUT=ROOT/'RevB'
helpers=runpy.run_path(str(ROOT/'render-video.py'))
rasterize,clip_mesh,wrap,smooth=[helpers[n] for n in ['rasterize','clip_mesh','wrap','smooth']]
chapters=json.loads((OUT/'video-chapters.json').read_text())
parts=[]
with (OUT/'actual-head-mesh.bin').open('rb') as f:
    while first:=f.read(1):
        n=first[0]&127;shift=7
        while first[0]&128:first=f.read(1);n|=(first[0]&127)<<shift;shift+=7
        name=f.read(n).decode();count=struct.unpack('<i',f.read(4))[0]
        mesh=np.frombuffer(f.read(count*36),'<f4').reshape(-1,3,3).astype(float)
        parts.append((name.split()[0],mesh))
assert len(parts)==15
PALETTE={'F01-001':(218,143,91),'F01-002':(68,171,164),'F01-003':(224,77,77),'F01-004':(77,128,230),'F01-005':(135,153,177),'F01-006':(222,207,163),'F01-007':(180,192,208)}
W,H,FPS=1600,900,15
def font(n,b=False):return ImageFont.truetype('C:/Windows/Fonts/'+('segoeuib.ttf' if b else 'segoeui.ttf'),n)
TITLE,BODY,SMALL,TINY=font(35,True),font(25),font(20),font(17)
CLIPPED=[]
for code,v in parts:
    if code in ['F01-001','F01-002','F01-005','F01-006']:
        vv=v.copy();vv[:,:,1]=np.where(abs(vv[:,:,1])<1e-5,0,vv[:,:,1]);vv,_,_=clip_mesh(vv);CLIPPED.append((code,vv))
    else:CLIPPED.append((code,v))

def frame(index,t,duration):
    u=t/duration;ch=chapters[index];scene=[];colors=[]
    exploded=index==0;cutaway=index==5;source=CLIPPED if cutaway else parts
    shifts={'F01-001':80,'F01-002':40,'F01-005':-40,'F01-006':-20} if exploded else {}
    yaw=1.12+.07*math.sin(u*math.pi*2);scale=5.2;center=np.array([12.,0,0]);origin=(1010,445);elevation=.20
    if index in [1,3,6]:yaw=.28+.12*math.sin(u*math.pi);scale=8.2;center=np.array([3.5,0,0])
    if index==2:yaw=.75+.35*u;scale=8.2;center=np.array([-9.,0,0])
    if index==4:yaw=1.08;scale=6.2;center=np.array([-15.,0,0])
    if index==5:yaw=1.02+.08*math.sin(u*math.pi);scale=7.8;center=np.array([-7.5,0,0])
    if index==7:yaw=.3+(math.pi-.7)*smooth(u);scale=8.;center=np.array([-7.5,0,0])
    for code,v in source:
        if index in [1,3,6] and code!='F01-001':continue
        if index==2 and code in ['F01-001','F01-002','F01-007']:continue
        vv=v.copy();offset=shifts.get(code,0)
        if index==4:
            if code=='F01-001':offset=0
            elif code=='F01-002':offset=-45*(1-smooth((u-.05)/.32))
            elif code=='F01-007':
                if u<.36:continue
            else:offset=-43*(1-smooth((u-.44)/.48))
        vv[:,:,0]+=offset;scene.append(vv)
        rgb=np.tile(PALETTE[code],(len(vv),1)).astype(float)
        if code=='F01-001':
            rear=np.all(abs(v[:,:,0])<1e-5,axis=1);rgb[rear]*=.90
            floor=np.all(abs(v[:,:,0]-4)<1e-5,axis=1)&(np.linalg.norm(v.mean(1)[:,1:],axis=1)<29.1)
            rgb[floor]=[59,163,204] if index in [1,3,6] else np.array(PALETTE[code])*.73
        colors.append(rgb)
    vertices=np.concatenate(scene);rgb=np.concatenate(colors)
    cy,sy=math.cos(yaw),math.sin(yaw);ce,se=math.cos(elevation),math.sin(elevation)
    def project(points):
        x,y,z=np.moveaxis(np.asarray(points)-center,-1,0);d=-x*cy+y*sy
        return np.stack((origin[0]+scale*(x*sy+y*cy),origin[1]-scale*(z*ce-d*se),d*ce+z*se),axis=-1)
    tri=project(vertices);normal=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);normal/=np.maximum(np.linalg.norm(normal,axis=1,keepdims=True),1e-8)
    rgb=np.clip(rgb*(.46+.47*np.abs(normal@np.array([-.2,-.4,.89])))[:,None]+7,0,255).astype('uint8')
    im=Image.new('RGB',(W,H),'#101b2a');draw=ImageDraw.Draw(im);draw.rectangle((0,0,436,H),fill='#1b2b3f')
    draw.text((30,30),'F01 / REV B / MAGNETIC COOLING HEAD',font=TINY,fill='#a9c2d7')
    y=wrap(draw,ch['title'],(30,90),370,TITLE,'#f2f7fb')+30
    for text in ch['bullets']:
        draw.ellipse((32,y+10,39,y+17),fill='#6ac6ed');y=wrap(draw,text,(54,y),345,BODY,'#d5e5f1')+25
    y=617
    for code,name in [('F01-001','Copper body'),('F01-002','Coolant cover'),('F01-003','Outer poles: N toward target'),('F01-004','Center stack: S toward target'),('F01-005','Steel yoke / magnetic return')]:
        draw.rectangle((30,y+5,43,y+17),fill=PALETTE[code]);draw.text((55,y),name,font=TINY,fill='#d4e4f0');y+=33
    wrap(draw,'Concept CAD / operating performance unverified',(30,806),370,TINY,'#edc968')
    im=Image.fromarray(rasterize(np.array(im),tri,rgb));draw=ImageDraw.Draw(im)
    def line3(points,color,width=3):
        pp=project(np.array(points));draw.line([tuple(p[:2]) for p in pp],fill=color,width=width);return pp
    def dot(point,color,r=4):
        x,y,_=project(np.array(point));draw.ellipse((x-r,y-r,x+r,y+r),fill=color)
    def label(text,point,xy,color='#e5eff8'):
        p=project(np.array(point));draw.line((p[0],p[1],xy[0],xy[1]+12),fill=color,width=2);dot(point,color)
        draw.rounded_rectangle((xy[0]-6,xy[1]-2,xy[0]+draw.textlength(text,font=SMALL)+6,xy[1]+29),radius=4,fill='#17283a');draw.text(xy,text,font=SMALL,fill=color)
    def ring(center,radius,color):
        a=np.linspace(0,math.tau,130);line3(np.column_stack((np.full(len(a),center[0]),center[1]+radius*np.cos(a),center[2]+radius*np.sin(a))),color,3)
    if index==0:
        label('Revised cooling body',[80,-20,0],(1240,115),'#f1b67d');label('Magnet pack',[0,20,0],(850,120),'#f18d8d')
        label('Cover dry passages',[40,-20,-5],(1120,750),'#87e0d9');label('Steel yoke',[-60,-20,0],(495,135),'#cbd6e4')
    if index==1:
        label('Dry outer well',[0,20,0],(1180,150),'#f18d8d');label('Dry central well',[0,0,0],(555,220),'#a1bfff')
        label('Water outside the copper islands',[4,-16,12],(1100,735),'#9ce5ff')
    if index==2:
        label('Center stack: two discs',[-5,0,0],(1120,130),'#a1bfff');label('Outer rod: 1 of 6',[-5,20,0],(1130,735),'#f18d8d')
        label('Yoke + rear locator',[-17,-25,0],(520,200),'#d7dce6')
    if index==3:
        green='#a4e8a6';ring([-.12,0,0],32,green);ring([-.12,0,0],7.75,green)
        for a in np.arange(6)*math.pi/3:ring([-.12,20*math.cos(a),20*math.sin(a)],5.75,green)
        label('Six outer-well seals',[0,20,0],(1150,140),green);label('Central well seal',[0,-7.75,0],(540,230),green)
        label('Perimeter seal',[0,0,-32],(1130,750),green)
    if index==4:
        bodygap=45*(1-smooth((u-.05)/.32));packgap=43*(1-smooth((u-.44)/.48))
        text='COVER APPROACH' if u<.4 else 'MAGNET PACK APPROACH' if u<.95 else 'FITTED POSITIONS'
        draw.text((700,110),text,font=BODY,fill='#e4f0fa')
        label('Cover closes against body',[-bodygap,0,-33],(1150,742),'#87e0d9')
        if u>.42:label('Magnets enter the dry wells',[3-packgap,20,0],(570,180),'#f18d8d')
    if index==5:
        label('Target seating face',[7,0,-22],(1140,735),'#f1b67d');label('Dry magnet tip',[3,0,0],(1120,130),'#a1bfff')
        line3([[3,0,-6],[7,0,-6]],'#ffffff',4);label('4 mm to target seat',[5,0,-6],(1040,650))
        label('Load-bearing spacer',[-10,37,0],(520,735))
        draw.text((480,78),'CUTAWAY: HALF OF SUPPORT PARTS REMOVED / MAGNETS KEPT WHOLE',font=TINY,fill='#b8c9db')
    if index==6:
        for radius in [11.2,28.3]:
            a=np.linspace(math.pi/6,11*math.pi/6,160);arc=np.column_stack((np.full(len(a),2.),radius*np.cos(a),radius*np.sin(a)))
            p=np.array([[-11,22.51666,13],[2,22.51666,13]]);q=np.array([[2,22.51666,-13],[-11,22.51666,-13]])
            path=np.concatenate((p,arc,q));line3(path,'#b5ebff',2)
            for n in range(6):dot(path[(int(t*18)+n*28)%len(path)],'#ffffff',3)
        label('Inlet through cover',[-11,22.51666,13],(1130,125),'#9ce5ff');label('Return through cover',[-11,22.51666,-13],(1130,742),'#9ce5ff')
        draw.text((480,78),'COVER AND MAGNETS HIDDEN / ILLUSTRATIVE FLOW ROUTES, NOT CFD',font=TINY,fill='#9ce5ff')
    if index==7:
        label('15-instance fitted head',[0,-40,0],(820,750))
        if yaw>2.2:
            a=np.linspace(0,math.tau,150);line3(np.column_stack((np.full(len(a),7.08),25.4*np.cos(a),25.4*np.sin(a))),'#a4e7ff',3)
            draw.text((750,110),'FUTURE 2-INCH TARGET FOOTPRINT',font=TINY,fill='#a4e7ff')
    draw.text((472,30),'ACTUAL NATIVE CAD MESH / HIGHLIGHTS AND SEAL-FLOW GRAPHICS ARE EXPLANATORY',font=TINY,fill='#a8bfd3')
    draw.text((475,850),f'{index+1:02} / 08     REV B WALKTHROUGH',font=TINY,fill='#b1c5d6')
    draw.rectangle((436,890,1599,899),fill='#273b50');draw.rectangle((436,890,436+int(1164*u),899),fill='#51bde9')
    return np.asarray(im)

def stamp(t):
    n=round(t*1000);return f'{n//3600000:02}:{n//60000%60:02}:{n//1000%60:02},{n%1000:03}'
if __name__=='__main__':
    if 'preview' in sys.argv:
        for i in range(8):Image.fromarray(frame(i,12,20)).save(OUT/f'video-preview-{i:02}.jpg')
        for n in [2,7,18]:Image.fromarray(frame(4,n,20)).save(OUT/f'video-insertion-{n:02}.jpg')
        print('Saved chapter and insertion previews');sys.exit()
    durations=[];chunks=[];params=None
    for i in range(8):
        with wave.open(str(OUT/f'voice-{i:02}.wav'),'rb') as f:p=f.getparams();raw=f.readframes(p.nframes)
        if params is None:params=p
        assert params[:3]==p[:3]
        duration=math.ceil((p.nframes/p.framerate+1.6)*FPS)/FPS;durations.append(duration);lead=int(.5*p.framerate);tail=round(duration*p.framerate)-lead-p.nframes
        chunks.append(bytes(lead*p.sampwidth*p.nchannels)+raw+bytes(tail*p.sampwidth*p.nchannels))
    with wave.open(str(OUT/'narration.wav'),'wb') as f:
        f.setparams(params)
        for chunk in chunks:f.writeframes(chunk)
    writer=imageio_ffmpeg.write_frames(str(OUT/'silent-video.mp4'),(W,H),fps=FPS,codec='libx264',quality=8,macro_block_size=1);writer.send(None)
    elapsed=0;timeline=[];subs=[]
    for i,(ch,duration) in enumerate(zip(chapters,durations)):
        timeline.append((elapsed,ch['title']));sentences=[s.strip()+'.' for s in ch['speech'].split('.') if s.strip()];total=sum(map(len,sentences));start=elapsed+.5
        for s in sentences:
            end=start+(duration-1.6)*len(s)/total;subs.append(f'{len(subs)+1}\n{stamp(start)} --> {stamp(end)}\n{s}\n');start=end
        for n in range(round(duration*FPS)):writer.send(frame(i,n/FPS,duration))
        elapsed+=duration;print(f'{i+1}/8 {ch["title"]} ({duration:.1f}s)',flush=True)
    writer.close();(OUT/'subtitles.srt').write_text('\n'.join(subs),encoding='utf8')
    metadata=';FFMETADATA1\ntitle=Rev B magnetic cooling head - design and assembly\n';transcript=[]
    for i,(start,title) in enumerate(timeline):
        end=timeline[i+1][0] if i<7 else elapsed;metadata+=f'[CHAPTER]\nTIMEBASE=1/1000\nSTART={round(start*1000)}\nEND={round(end*1000)}\ntitle={title}\n'
        transcript.extend([f'{int(start)//60}:{int(start)%60:02} {title}',chapters[i]['speech'],''])
    (OUT/'video-chapters.ffmeta').write_text(metadata,encoding='utf8');(OUT/'Video transcript.txt').write_text('\n'.join(transcript),encoding='utf8')
    subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-y','-v','error','-i',str(OUT/'silent-video.mp4'),'-i',str(OUT/'narration.wav'),'-i',str(OUT/'subtitles.srt'),'-i',str(OUT/'video-chapters.ffmeta'),'-map','0:v','-map','1:a','-map','2:s','-map_metadata','3','-map_chapters','3','-c:v','copy','-c:a','aac','-b:a','160k','-c:s','mov_text','-movflags','+faststart',str(OUT/'RevB magnetic cooling head - narrated walkthrough.mp4')],check=True)
    print(f'COMPLETE {elapsed:.1f} seconds',flush=True)
