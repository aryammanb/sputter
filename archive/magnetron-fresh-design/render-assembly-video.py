import json,math,struct,subprocess,sys,wave,runpy
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
import imageio_ffmpeg

ROOT=Path(__file__).resolve().parent
helper=runpy.run_path(str(ROOT/'render-video.py'))
rasterize,wrap,smooth=helper['rasterize'],helper['wrap'],helper['smooth']
chapters=json.loads((ROOT/'assembly-video-chapters.json').read_text())
def load_mesh(name):
    vertices=[];features=[]
    with (ROOT/name).open('rb') as f:
        while first:=f.read(1):
            length=first[0]&127;shift=7
            while first[0]&128:
                first=f.read(1);length|=(first[0]&127)<<shift;shift+=7
            feature=f.read(length).decode();n=struct.unpack('<i',f.read(4))[0]
            vertices.append(np.frombuffer(f.read(n*36),'<f4').reshape(-1,3,3));features.extend([feature]*n)
    return np.concatenate(vertices).astype(float),np.array(features)
body,bnames=load_mesh('part01-video-mesh.bin');cover,cnames=load_mesh('part02-video-mesh.bin')
assert len(body)==2106 and len(cover)==1732
W,H,FPS=1600,900,15
def font(n,bold=False):return ImageFont.truetype('C:/Windows/Fonts/'+('segoeuib.ttf' if bold else 'segoeui.ttf'),n)
TITLE,BODY,SMALL,TINY=font(36,True),font(25),font(21),font(17)
COPPER=np.array([218,143,91]);TEAL=np.array([86,181,176]);BLUE=np.array([76,190,234]);GOLD=np.array([247,200,76]);GREEN='#9be29f'
PORTS=np.array([[0,18*math.cos(math.pi/6),9],[0,18*math.cos(math.pi/6),-9]])
SCREWS=np.array([[0,32*math.cos(i*math.pi/3),32*math.sin(i*math.pi/3)] for i in range(6)])
def pose(index,u):
    shift=-55.;angle=0.
    if index==1:angle=math.pi*smooth(u*3)
    elif index==2:angle=math.pi
    elif index==3:angle=math.pi*(1-smooth((u-.12)/.68))
    elif index==4:shift=-55*(1-smooth((u-.12)/.74))
    elif index>=5:shift=0.
    return shift,angle
def frame(index,t,duration):
    ch=chapters[index];u=t/duration;shift,angle=pose(index,u)
    def transform(points):
        q=np.asarray(points)-np.array([-1.5,0,0]);x,y,z=np.moveaxis(q,-1,0);ca,sa=math.cos(angle),math.sin(angle)
        return np.stack((x*ca+z*sa-1.5+shift,y,-x*sa+z*ca),axis=-1)
    yaw=.98+.04*math.sin(u*math.pi*2);elevation=.20;scale=6.8;center=np.array([-25,0,0]);origin=(1030,450)
    if index==4:
        s=smooth((u-.12)/.74);center=np.array([-25*(1-s)-2*s,0,0]);scale=6.8+1.9*s;yaw=1.04
    if index==5:scale=8.8;center=np.array([-2,0,0]);yaw=.26+.06*math.sin(u*math.pi)
    if index==6:scale=8.8;center=np.array([3.5,0,0]);yaw=.25+.08*math.sin(u*math.pi)
    if index==7:scale=8.8;center=np.array([-2,0,0]);yaw=.3+(math.pi-.65)*smooth(u)
    cy,sy=math.cos(yaw),math.sin(yaw);ce,se=math.cos(elevation),math.sin(elevation)
    def project(points):
        x,y,z=np.moveaxis(np.asarray(points)-center,-1,0);d=-x*cy+y*sy
        return np.stack((origin[0]+scale*(x*sy+y*cy),origin[1]-scale*(z*ce-d*se),d*ce+z*se),axis=-1)
    meshes=[body];colors=[np.tile(COPPER,(len(body),1)).astype(float)]
    colors[0][np.array(['Water passage' in n for n in bnames])]*=.63
    colors[0][np.array(['gland' in n for n in bnames])]*=.50
    colors[0][np.array(['pilot' in n for n in bnames])]*=.40
    if index==6:colors[0][np.array(['Water passage' in n for n in bnames])]=BLUE
    if index!=6:
        meshes.append(transform(cover));col=np.tile(TEAL,(len(cover),1)).astype(float)
        col[np.array(['clearance' in n or 'water passages' in n or 'pilot' in n for n in cnames])]*=.48
        col[np.array(['bypass' in n for n in cnames])]=GOLD if index in [1,2,3] else TEAL*.6
        colors.append(col)
    vertices=np.concatenate(meshes);rgb=np.concatenate(colors);tri=project(vertices)
    normals=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);normals/=np.maximum(np.linalg.norm(normals,axis=1,keepdims=True),1e-8)
    shade=.43+.5*np.abs(normals@np.array([-.28,-.43,.86]));rgb=np.clip(rgb*shade[:,None]+7,0,255).astype('uint8')
    im=Image.new('RGB',(W,H),'#101b2a');draw=ImageDraw.Draw(im)
    draw.rectangle((0,0,436,H),fill='#1b2b3f');draw.line((436,0,436,H),fill='#34485d',width=2)
    draw.text((33,30),'F01  /  COOLING BODY + COVER',font=TINY,fill='#a9c2d7')
    y=wrap(draw,ch['title'],(33,94),365,TITLE,'#f2f6fa')+36
    for text in ch['bullets']:
        draw.ellipse((35,y+10,42,y+17),fill='#52c0e9');y=wrap(draw,text,(57,y),340,BODY,'#d6e6f2')+24
    draw.rectangle((33,680,48,695),fill=tuple(COPPER));draw.text((59,676),'Cooling body',font=SMALL,fill='#e9eef6')
    draw.rectangle((33,721,48,736),fill=tuple(TEAL));draw.text((59,717),'Coolant cover',font=SMALL,fill='#e9eef6')
    wrap(draw,'Rev A concept / operating performance unverified',(33,776),365,TINY,'#f2c64b')
    im=Image.fromarray(rasterize(np.array(im),tri,rgb));draw=ImageDraw.Draw(im)
    def line3(points,color,width=3,dashed=False):
        projected=project(np.array(points));pp=[tuple(p[:2]) for p in projected]
        if dashed:
            for p,q in zip(projected,np.roll(projected,-1,axis=0)):
                if np.array_equal(q,projected[0]):continue
                count=max(1,int(np.linalg.norm(q[:2]-p[:2])/13))
                for n in range(0,count,2):
                    a=p+(q-p)*n/count;b=p+(q-p)*min(n+1,count)/count;draw.line((a[0],a[1],b[0],b[1]),fill=color,width=width)
        else:draw.line(pp,fill=color,width=width)
        return projected
    def dot(point,color,radius=5):
        x,y,_=project(point);draw.ellipse((x-radius,y-radius,x+radius,y+radius),fill=color)
    def label(text,point,xy,color='#e7f0f8'):
        p=project(np.array(point));draw.line((p[0],p[1],xy[0],xy[1]+13),fill=color,width=2);dot(point,color,4)
        draw.rounded_rectangle((xy[0]-7,xy[1]-3,xy[0]+draw.textlength(text,font=SMALL)+7,xy[1]+30),radius=4,fill='#142236');draw.text(xy,text,font=SMALL,fill=color)
    def ring(radius,x,color):
        a=np.linspace(0,math.tau,181);line3(np.column_stack((np.full(len(a),x),radius*np.cos(a),radius*np.sin(a))),color,4)
    if index==0:
        label('Cooling body',[0,-21,-17],(1160,750),'#f2b783')
        label('Rear fitting bosses',transform([-11,15.588,9]),(540,120),'#8ce1dc')
    if index==1:
        label('Channel + O-ring grooves',[0,-17,-17],(1150,750),'#f2b783')
        label('Cover mating face',transform([0,-15,17]),(520,120),'#8ce1dc')
        draw.text((475,73),'INSPECTION FLIP  /  NOT THE INSTALLATION ORIENTATION',font=TINY,fill='#e7ce8d')
    if index in [2,4] and abs(shift)>.7:
        seal_x=-14*(1-smooth(u*3)) if index==2 else -.1
        ring(8,seal_x,GREEN);ring(28,seal_x,GREEN)
        if index==2:
            line3(transform([[0,10,0],[0,26,0]]),'#f5c74c',6)
            label('O-ring locations',[seal_x,-25,13],(1130,120),GREEN)
            label('Proposed divider strip',transform([0,18,0]),(510,748),'#f5c74c')
    if index==3:
        if angle<.25:
            for p in PORTS:line3([transform(p),p],'#8ae2ff',3,True)
            for p in SCREWS[[1,3,5]]:line3([transform(p),p],'#71879a',2,True)
        label('Match ports to channel ends',PORTS[0],(1110,120),'#8ae2ff')
        label('Bosses face rearward',transform([-11,15.588,-9]),(520,748),'#8ce1dc')
    if index==4:
        label('Mating plane on body',[0,-35,0],(1150,740),'#f2b783')
        draw.rounded_rectangle((805,95,1170,144),radius=9,fill='#20344c');draw.text((823,102),f'FACE GAP  {abs(shift):05.1f} mm',font=BODY,fill='#edf7fc')
        line3([[shift,-37,-15],[0,-37,-15]],'#dbeefc',3)
    if index==5:
        active=min(5,int(u*6))
        for i,p in enumerate(SCREWS):
            q=p.copy();q[0]=-3.15
            dot(q,'#ffe19a' if i==active else '#b5aaa0',9 if i==active else 5)
        p=SCREWS[active].copy();p[0]=-3.15
        label('Screw positions / hardware not modeled',p,(735,760),'#ffe19a')
        draw.text((520,100),'SIX COVER HOLES  /  SIX RECEIVING BODY THREADS',font=TINY,fill='#d6e6f2')
    if index==6:
        a=np.linspace(math.pi/6,11*math.pi/6,180)
        arc=np.column_stack((np.full(len(a),1.4),18*np.cos(a),18*np.sin(a)))
        path=np.concatenate((np.array([[-11,15.588,9],[1.4,15.588,9]]),arc,np.array([[1.4,15.588,-9],[-11,15.588,-9]])))
        line3(path,'#b6ecff',3)
        for n in range(8):dot(path[(int(t*23)+n*25)%len(path)],'#ffffff',4)
        label('Inlet through cover',[ -11,15.588,9],(1150,120),'#9ce3ff')
        label('Return through cover',[-11,15.588,-9],(1150,740),'#9ce3ff')
        draw.text((520,82),'COVER HIDDEN  /  INTENDED FLOW, NOT CFD',font=TINY,fill='#9ce3ff')
    if index==7:
        label('Body + cover at their fitted positions',[0,-35,0],(780,750),'#eaf2fa')
        if yaw>2.3:
            a=np.linspace(0,math.tau,181);line3(np.column_stack((np.full(len(a),7.1),25.4*np.cos(a),25.4*np.sin(a))),'#a4e7ff',3)
            draw.text((720,100),'FRONT: FUTURE 2-INCH TARGET SEAT',font=TINY,fill='#a4e7ff')
    draw.text((472,30),'ACTUAL CAD PARTS  |  SEAL / ALIGNMENT / FLOW GRAPHICS ARE OVERLAYS',font=TINY,fill='#9cb8cc')
    draw.text((475,850),f'{index+1:02} / {len(chapters):02}    ASSEMBLY WALKTHROUGH',font=TINY,fill='#b1c5d6')
    draw.rectangle((436,890,1599,899),fill='#273b50');draw.rectangle((436,890,436+int(1164*u),899),fill='#51bde9')
    return np.asarray(im)

def stamp(t):
    n=round(t*1000);return f'{n//3600000:02}:{n//60000%60:02}:{n//1000%60:02},{n%1000:03}'
if __name__=='__main__':
    if 'preview' in sys.argv:
        for i in range(8):Image.fromarray(frame(i,12,20)).save(ROOT/f'assembly-preview-{i:02}.jpg')
        for t in [2,7,17]:Image.fromarray(frame(4,t,20)).save(ROOT/f'assembly-closure-{t:02}.jpg')
        print('Saved assembly and motion previews');sys.exit()
    durations=[];chunks=[];params=None
    for i in range(8):
        with wave.open(str(ROOT/f'assembly-voice-{i:02}.wav'),'rb') as f:
            p=f.getparams();raw=f.readframes(p.nframes)
        if params is None:params=p
        assert params[:3]==p[:3]
        duration=math.ceil((p.nframes/p.framerate+1.6)*FPS)/FPS;durations.append(duration);lead=int(.5*p.framerate);tail=round(duration*p.framerate)-lead-p.nframes
        chunks.append(bytes(lead*p.sampwidth*p.nchannels)+raw+bytes(tail*p.sampwidth*p.nchannels))
    with wave.open(str(ROOT/'assembly-narration.wav'),'wb') as out:
        out.setparams(params)
        for chunk in chunks:out.writeframes(chunk)
    writer=imageio_ffmpeg.write_frames(str(ROOT/'assembly-silent.mp4'),(W,H),fps=FPS,codec='libx264',quality=8,macro_block_size=1);writer.send(None)
    timeline=[];subs=[];elapsed=0
    for i,(ch,duration) in enumerate(zip(chapters,durations)):
        timeline.append((elapsed,ch['title']))
        sentences=[s.strip()+'.' for s in ch['speech'].split('.') if s.strip()];length=sum(map(len,sentences));start=elapsed+.5
        for s in sentences:
            end=start+(duration-1.6)*len(s)/length;subs.append(f'{len(subs)+1}\n{stamp(start)} --> {stamp(end)}\n{s}\n');start=end
        for n in range(round(duration*FPS)):writer.send(frame(i,n/FPS,duration))
        elapsed+=duration;print(f'{i+1}/8: {ch["title"]} ({duration:.1f}s)',flush=True)
    writer.close();(ROOT/'assembly-subtitles.srt').write_text('\n'.join(subs),encoding='utf8')
    metadata=';FFMETADATA1\ntitle=Cooling body and cover - assembly walkthrough\n'
    transcript=['# Cooling body and cover — assembly walkthrough','', 'Actual F01-001 and F01-002 Rev A CAD meshes. Colors distinguish the two copper parts. Seal traces, screw markers, alignment guides and flow markers are explanatory overlays. No seal deformation or fluid simulation is claimed.','']
    for i,(start,title) in enumerate(timeline):
        end=timeline[i+1][0] if i+1<8 else elapsed
        metadata+=f'[CHAPTER]\nTIMEBASE=1/1000\nSTART={round(start*1000)}\nEND={round(end*1000)}\ntitle={title}\n'
        transcript.extend([f'## {int(start)//60}:{int(start)%60:02} — {title}','',chapters[i]['speech'],''])
    (ROOT/'assembly-chapters.ffmeta').write_text(metadata,encoding='utf8');(ROOT/'Assembly video transcript.md').write_text('\n'.join(transcript),encoding='utf8')
    subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-y','-v','error','-i',str(ROOT/'assembly-silent.mp4'),'-i',str(ROOT/'assembly-narration.wav'),'-i',str(ROOT/'assembly-subtitles.srt'),'-i',str(ROOT/'assembly-chapters.ffmeta'),'-map','0:v','-map','1:a','-map','2:s','-map_metadata','3','-map_chapters','3','-c:v','copy','-c:a','aac','-b:a','160k','-c:s','mov_text','-movflags','+faststart',str(ROOT/'Cooling body and cover - narrated assembly.mp4')],check=True)
    print(f'COMPLETE {elapsed:.1f} seconds',flush=True)
