import json, math, struct, subprocess, sys, wave
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg
from numba import njit

@njit(cache=True)
def rasterize(pixels,triangles,colors):
    height,width=pixels.shape[:2];depth=np.full((height,width),-1e20)
    for i in range(len(triangles)):
        a,b,c=triangles[i];den=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
        if abs(den)<1e-8:continue
        xmin=max(437,int(math.floor(min(a[0],b[0],c[0]))));xmax=min(width-1,int(math.ceil(max(a[0],b[0],c[0]))))
        ymin=max(65,int(math.floor(min(a[1],b[1],c[1]))));ymax=min(height-75,int(math.ceil(max(a[1],b[1],c[1]))))
        for y in range(ymin,ymax+1):
            for x in range(xmin,xmax+1):
                u=((b[1]-c[1])*(x+.5-c[0])+(c[0]-b[0])*(y+.5-c[1]))/den
                v=((c[1]-a[1])*(x+.5-c[0])+(a[0]-c[0])*(y+.5-c[1]))/den
                w=1-u-v
                if u>=-1e-6 and v>=-1e-6 and w>=-1e-6:
                    z=u*a[2]+v*b[2]+w*c[2]
                    if z>depth[y,x]:depth[y,x]=z;pixels[y,x]=colors[i]
    return pixels

ROOT=Path(__file__).resolve().parent
chapters=json.loads((ROOT/'video-chapters.json').read_text())
meshes=[];features=[]
with (ROOT/'part01-video-mesh.bin').open('rb') as f:
    while first:=f.read(1):
        length=first[0]&127;shift=7
        while first[0]&128:
            first=f.read(1);length|=(first[0]&127)<<shift;shift+=7
        name=f.read(length).decode();count=struct.unpack('<i',f.read(4))[0]
        meshes.append(np.frombuffer(f.read(count*36),'<f4').reshape(-1,3,3))
        features.extend([name]*count)
mesh=np.concatenate(meshes).astype(float);features=np.array(features)
assert len(mesh)==2106
W,H,FPS=1600,900,15
def font(n,bold=False):return ImageFont.truetype('C:/Windows/Fonts/'+('segoeuib.ttf' if bold else 'segoeui.ttf'),n)
TITLE,BODY,SMALL,TINY=font(37,True),font(26),font(21),font(18)
COPPER=np.array([208,134,86]);BLUE=np.array([77,190,233]);GOLD=np.array([242,198,75])
def smooth(t):t=max(0,min(1,t));return t*t*(3-2*t)
def wrap(draw,text,xy,width,ft,color,spacing=9):
    x,y=xy;line=''
    for word in text.split():
        trial=(line+' '+word).strip()
        if line and draw.textlength(trial,font=ft)>width:
            draw.text((x,y),line,font=ft,fill=color);y+=ft.size+spacing;line=word
        else:line=trial
    draw.text((x,y),line,font=ft,fill=color);return y+ft.size+spacing
def clip_mesh(vertices):
    # Clip actual CAD triangles at Y=0; retain Y<=0. Section edges are drawn explicitly.
    result=[];source=[];edges=[]
    for idx,tri in enumerate(vertices):
        poly=[];crossings=[]
        for a,b in zip(tri,np.roll(tri,-1,axis=0)):
            ina=a[1]<=1e-8;inb=b[1]<=1e-8
            if ina:poly.append(a)
            if ina!=inb:
                p=a+(b-a)*(-a[1])/(b[1]-a[1]);poly.append(p);crossings.append(p)
        if len(crossings)==2:edges.append(crossings)
        for n in range(1,len(poly)-1):result.append([poly[0],poly[n],poly[n+1]]);source.append(idx)
    return np.array(result),np.array(source),np.array(edges)
clipped,clip_source,section_edges=clip_mesh(mesh)
def frame(index,t,duration):
    ch=chapters[index];fraction=t/duration;kind=ch['view']
    yaw=.28+.12*math.sin(fraction*math.pi*2);elevation=.25;scale=9.1;center=np.array([3.5,0,0]);origin=(1035,440)
    if kind=='front':yaw=math.pi-.25+.09*math.sin(fraction*math.pi*2)
    if kind=='bridge':yaw=.10+.12*math.sin(fraction*math.pi);scale=12.8;center=np.array([1,7,12]);origin=(1000,475)
    if kind=='section':yaw=-.97;elevation=.12;scale=10;origin=(1010,440)
    cy,sy=math.cos(yaw),math.sin(yaw);ce,se=math.cos(elevation),math.sin(elevation)
    def project(points):
        x,y,z=np.moveaxis(np.asarray(points)-center,-1,0);depth=-x*cy+y*sy
        return np.stack((origin[0]+scale*(x*sy+y*cy),origin[1]-scale*(z*ce-depth*se),depth*ce+z*se),axis=-1)
    source=clip_source if kind=='section' else np.arange(len(mesh));verts=clipped if kind=='section' else mesh
    names=features[source];colors=np.tile(COPPER,(len(verts),1)).astype(float)
    colors[np.array(['Water passage' in n for n in names])]*=.78
    colors[np.array(['gland' in n for n in names])]*=.68
    colors[np.array(['pilot' in n for n in names])]*=.45
    highlight=ch['highlight']
    if highlight and highlight!='front':
        match=np.array([highlight in n for n in names]);colors[match]=BLUE if highlight=='Water passage' else GOLD
    if highlight=='front':
        match=np.all(abs(verts[:,:,0]-7)<.001,axis=1);colors[match]=[232,170,115]
    tri=project(verts)
    normal=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);normal/=np.maximum(np.linalg.norm(normal,axis=1,keepdims=True),1e-8)
    lighting=.45+.48*np.abs(normal@np.array([-.25,-.45,.86]));colors=np.clip(colors*lighting[:,None]+8,0,255).astype('uint8')
    im=Image.new('RGB',(W,H),'#101b2a');draw=ImageDraw.Draw(im)
    draw.rectangle((0,0,436,H),fill='#1b2b3f');draw.line((436,0,436,H),fill='#34485d',width=2)
    draw.text((34,30),'F01-001  /  COPPER COOLING BODY',font=TINY,fill='#9db6ce')
    y=wrap(draw,ch['title'],(34,91),365,TITLE,'#f4f6f8')+34
    for bullet in ch['bullets']:
        draw.ellipse((36,y+10,43,y+17),fill=tuple(BLUE.astype(int)))
        y=wrap(draw,bullet,(57,y),340,BODY,'#d3e2ee')+26
    draw.text((34,678),'REV A  /  CONCEPT CAD',font=SMALL,fill='#f2c64b')
    wrap(draw,'Dimensions are preliminary. No operating rating assigned.',(34,719),365,SMALL,'#a6bbce')
    im=Image.fromarray(rasterize(np.array(im),tri,colors));draw=ImageDraw.Draw(im)
    def line3(points,color,width=3):
        pp=project(np.array(points));draw.line([tuple(p[:2]) for p in pp],fill=color,width=width);return pp
    def point3(point,color='#ffffff',radius=5):
        x,y,_=project(np.array(point));draw.ellipse((x-radius,y-radius,x+radius,y+radius),fill=color)
    def label(text,point,xy,color='#eaf5ff'):
        p=project(np.array(point));draw.line((p[0],p[1],xy[0],xy[1]+14),fill=color,width=2);point3(point,color,4)
        draw.rounded_rectangle((xy[0]-8,xy[1]-4,xy[0]+draw.textlength(text,font=SMALL)+8,xy[1]+31),radius=5,fill='#132134')
        draw.text(xy,text,font=SMALL,fill=color)
    if kind=='front':
        angles=np.linspace(0,math.tau,181);points=np.column_stack((np.full(len(angles),7.08),25.4*np.cos(angles),25.4*np.sin(angles)))
        line3(points,'#a4e7ff',3);label('2-inch target footprint',[7.1,-16,19],(1120,125),'#a4e7ff')
        if index==8:
            for a in [30,150,270]:
                r=math.radians(a);point3([7.2,32*math.cos(r),32*math.sin(r)],'#f2c64b',6)
            label('Clamp pilot: 1 of 3',[7.2,0,-32],(1130,750),'#f2c64b')
    if index in [3,4]:
        angles=np.linspace(math.pi/6,11*math.pi/6,170)
        path=np.column_stack((np.full(len(angles),1.2),18*np.cos(angles),18*np.sin(angles)))
        line3(path,'#b9edff',3)
        for n in range(6):point3(path[(int(t*20)+n*28)%len(path)],'#ffffff',4)
        label('Future inlet',[0,18*math.cos(math.pi/6),9],(1150,90),'#9fe7ff')
        label('Future outlet',[0,18*math.cos(math.pi/6),-9],(1160,730),'#9fe7ff')
        if index==4:label('Solid bridge / bypass control',[0,18,0],(1160,470),'#f2c64b')
    if index==5:
        for edge in section_edges:line3(edge,'#f6cb71',2)
        label('Target seating face',[7,0,20],(1150,140))
        label('Water-channel floor',[3,0,-18],(620,715),'#9fe7ff')
        line3([[3,0,-18],[7,0,-18]],'#ffffff',5)
        label('4 mm copper wall',[5,0,-18],(1130,700),'#ffffff')
        draw.text((550,110),'SECTION AT Y = 0  /  OPEN CUT EDGES',font=TINY,fill='#f6cb71')
    if index==6:
        label('Inner gland',[.3,-8,0],(560,235),'#f2c64b')
        label('Outer gland',[.3,0,-28],(1160,735),'#f2c64b')
    if index==7:
        for a in range(0,360,60):point3([-.1,32*math.cos(math.radians(a)),32*math.sin(math.radians(a))],'#f2c64b',6)
        label('Cover pilot: 1 of 6',[0,-32,0],(550,170),'#f2c64b')
    if index in [0,9]:
        label('70 mm outside diameter',[0,-35,0],(560,145))
        label('Rear channel and seal face',[0,18,-18],(1130,740))
    draw.text((472,30),'ACTUAL SOLIDWORKS MESH  |  EXPLANATORY OVERLAYS',font=TINY,fill='#9db6ce')
    draw.text((475,849),f'{index+1:02} / {len(chapters):02}    '+('TARGET SIDE' if kind=='front' else 'CUTAWAY' if kind=='section' else 'COOLANT-COVER SIDE'),font=TINY,fill='#a9bfd2')
    draw.rectangle((436,890,1599,899),fill='#273b50');draw.rectangle((436,890,436+int(1164*fraction),899),fill='#51bde9')
    return np.asarray(im)

def timestamp(t):
    ms=round(t*1000);return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02},{ms%1000:03}'
if __name__=='__main__':
    if 'preview' in sys.argv:
        for i in range(len(chapters)):Image.fromarray(frame(i,5,20)).save(ROOT/f'video-preview-{i:02}.jpg')
        print('Saved ten chapter previews');sys.exit()
    audio_params=None;durations=[];samples=[];narration_cues=[]
    for i,ch in enumerate(chapters):
        with wave.open(str(ROOT/f'voice-{i:02}.wav'),'rb') as f:
            params=f.getparams();raw=f.readframes(f.getnframes());seconds=f.getnframes()/f.getframerate()
        if audio_params is None:audio_params=params
        assert params[:3]==audio_params[:3]
        duration=math.ceil((seconds+1.6)*FPS)/FPS;durations.append(duration)
        lead=int(.5*params.framerate);tail=round(duration*params.framerate)-lead-params.nframes
        samples.append(bytes(lead*params.sampwidth*params.nchannels)+raw+bytes(tail*params.sampwidth*params.nchannels))
    with wave.open(str(ROOT/'narration.wav'),'wb') as f:
        f.setparams(audio_params)
        for s in samples:f.writeframes(s)
    silent=ROOT/'part01-design-silent.mp4'
    writer=imageio_ffmpeg.write_frames(str(silent),(W,H),fps=FPS,codec='libx264',quality=8,output_params=['-pix_fmt','yuv420p'])
    writer.send(None);elapsed=0;subs=[];timeline=[]
    for i,(ch,duration) in enumerate(zip(chapters,durations)):
        timeline.append((elapsed,ch['title']))
        # Phrase-sized optional subtitle cues; speech remains in the audio track.
        sentences=[s.strip()+'.' for s in ch['speech'].split('.') if s.strip()]
        total=sum(len(s) for s in sentences);start=elapsed+.5;available=duration-1.6
        for sentence in sentences:
            stop=start+available*len(sentence)/total;subs.append(f'{len(subs)+1}\n{timestamp(start)} --> {timestamp(stop)}\n{sentence}\n');start=stop
        for n in range(round(duration*FPS)):writer.send(frame(i,n/FPS,duration))
        elapsed+=duration;print(f'{i+1}/{len(chapters)} rendered: {ch["title"]} ({duration:.1f}s)',flush=True)
    writer.close();(ROOT/'part01-design.srt').write_text('\n'.join(subs),encoding='utf8')
    meta=';FFMETADATA1\ntitle=Copper cooling body Rev A - design walkthrough\n'
    for i,(start,title) in enumerate(timeline):
        stop=timeline[i+1][0] if i+1<len(timeline) else elapsed
        meta+=f'[CHAPTER]\nTIMEBASE=1/1000\nSTART={round(start*1000)}\nEND={round(stop*1000)}\ntitle={title}\n'
    (ROOT/'chapters.ffmeta').write_text(meta,encoding='utf8')
    subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-y','-v','error','-i',str(silent),'-i',str(ROOT/'narration.wav'),'-i',str(ROOT/'part01-design.srt'),'-i',str(ROOT/'chapters.ffmeta'),'-map','0:v','-map','1:a','-map','2:s','-map_metadata','3','-map_chapters','3','-c:v','copy','-c:a','aac','-b:a','160k','-c:s','mov_text','-movflags','+faststart',str(ROOT/'Copper cooling body - narrated design walkthrough.mp4')],check=True)
    (ROOT/'Video chapters.md').write_text('# Copper cooling body video\n\n'+ '\n'.join(f'- {int(t)//60}:{int(t)%60:02} {title}' for t,title in timeline)+f'\n\nRuntime: {elapsed:.1f} seconds. Actual native CAD tessellation; flow markers and target outline are explanatory overlays. English synthetic narration, optional subtitle track, and embedded chapters.\n',encoding='utf8')
    print(f'COMPLETE: {elapsed:.1f} seconds',flush=True)
