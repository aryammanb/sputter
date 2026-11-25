import json, math, struct, subprocess, wave
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg

root=Path(__file__).parent
stages=json.loads((root/'.r06-video-stages.json').read_text())
parts=[]
with (root/'.r06-mesh.bin').open('rb') as f:
    while b:=f.read(1):
        n=b[0]&127
        if b[0]&128: n+=f.read(1)[0]*128
        name=f.read(n).decode().split('/')[-1]
        code=name.split()[2 if 'R01' in name else 1]
        count=struct.unpack('<i',f.read(4))[0]
        vertices=np.frombuffer(f.read(count*36),dtype='<f4').reshape(-1,3,3)
        parts.append((code,vertices))
assert len(parts)==45
W,H=1280,720
fps=15
bg=(16,23,34)
def font(size,bold=False):
    return ImageFont.truetype('C:/Windows/Fonts/'+('segoeuib.ttf' if bold else 'segoeui.ttf'),size)
title,body,small=font(36,True),font(21),font(16)
palette={
 '01':(199,144,103),'02':(182,188,199),'03':(82,90,107),'04':(149,172,188),'05':(122,144,162),
 '101':(137,166,185),'102':(117,145,169),'103':(69,156,197),'104':(69,156,197),'105':(128,205,213),'106':(69,156,197),
 '201':(234,159,84),'202':(231,224,189),'203':(231,224,189),'301':(161,127,207),'302':(236,113,112),'303':(90,175,143),'304':(101,120,143),
 '305':(201,123,73),'306':(234,151,84),'308':(224,167,112),'309':(201,214,225),'401':(220,225,233),'402':(124,146,166),
 '403':(206,215,225),'501':(110,165,157),'502':(138,170,183),'503':(206,215,225)}
labels=[
 [('KF25 feedthrough','01'),('NW100 mounting plate','101'),('Shield and target end','501')],
 [('Clamp','05'),('Centering ring','02'),('O-ring','03'),('Mating stub','04'),('Grounded stem','102')],
 [('Feedthrough','01'),('Copper rod and socket','201'),('Ceramic guide','202'),('Ceramic carrier','203'),('Live steel yoke','304')],
 [('External bulkheads','103'),('Angled transitions','106'),('Dielectric sections','105'),('Head tubes','104')],
 [('Ceramic carrier','203'),('5 mm locator','301'),('Center magnet','302'),('Eight outer magnets','303'),('Steel yoke','304'),('Copper backplate','305')],
 [('Steel yoke','304'),('Copper backplate','305'),('C-channel core','306'),('Target-seat cover','308'),('Three head screws','309')],
 [('Supply and return tubes','104'),('C-channel core','306')],
 [('Copper target seat','308'),('2-inch Al target','401'),('Retaining ring','402'),('Three clamp screws','403')],
 [('Grounded stem','102'),('Shield seat','502'),('Grounded shield','501'),('Shield screws','503'),('Target clamp','402')],
 [('External connections','01'),('Grounded mount','101'),('Removable shield','501')]
]
cards=[
 'The shielded target sits inside the chamber. Power and water connect outside.',
 'The clamp pulls the two beveled rims together and compresses the O-ring.',
 'The copper rod carries power. The ceramic guide and carrier provide isolation.',
 'The two lines pass through the stem and feed the copper head.',
 'The locator positions nine magnets on the rear of the yoke. The copper head seats on its front.',
 'Three copper pieces enclose the channel. The screws pass through solid copper outside it.',
 'Water sweeps around the channel behind the target. Marker speed is illustrative.',
 'The ring lip overlaps the target by 1.4 mm per side.',
 'The shield comes off first during a target swap. The mounting flange is Ø92 mm.',
 'R06 resolves all references. Four coolant transition overlaps remain.'
]
shifts=[
 {},{'05':(0,0,33),'01':(-29,0,0),'02':(-10,0,0),'03':(0,0,16),'04':(11,0,0),'102':(24,0,0)},
 {},{}, {'203':(-25,0,0),'301':(-11,0,0),'302':(-18,0,15),'303':(-17,0,0),'304':(12,0,0),'305':(37,0,0)},
 {'304':(-25,0,0),'305':(-12,0,0),'306':(12,0,0),'308':(35,0,0),'309':(-17,0,20)},
 {},{'308':(-12,0,0),'401':(14,0,0),'402':(35,0,0),'403':(50,0,0)},
 {'501':(67,0,0),'503':(21,0,0)},{}
]
def scene(index, fraction):
    _,_,only,_=stages[index]
    codes=set(only.split())
    whole=index in (0,9)
    selected=[(c,a) for c,a in parts if whole or c in codes]
    if index==6: selected=[(c,a) for c,a in selected if c in {'104','305','306'}]
    poses=shifts[index]
    # The middle of each chapter holds the exploded pose long enough to inspect it.
    amt=min(1,fraction*5,(1-fraction)*5) if poses else 0
    verts=np.concatenate([a+amt*np.array(poses.get(c,(0,0,0))) for c,a in selected])
    color=np.concatenate([np.tile(palette[c],(len(a),1)) for c,a in selected])
    fit=np.concatenate([a for c,a in selected]+[a+np.array(poses.get(c,(0,0,0))) for c,a in selected])
    center=(fit.min((0,1))+fit.max((0,1)))/2
    span=max(np.ptp(fit[:,:,0]),np.ptp(fit[:,:,1])*1.25,np.ptp(fit[:,:,2])*1.25)
    scale=min(5.4,720/span,355/max(np.ptp(fit[:,:,1]),np.ptp(fit[:,:,2])))
    yaw=(.69+.62*fraction if index in (4,5,6) else -.42+.82*fraction) if not whole else ((-.65 if index==0 else .72)+(1.25 if index==0 else -1.42)*fraction)
    roll=(fraction-.5)*1.5 if whole else (fraction-.5)*.52
    cx,sx=math.cos(yaw),math.sin(yaw)
    cr,sr=math.cos(roll),math.sin(roll)
    def proj(points):
        x,y,z=np.moveaxis(np.asarray(points)-center,-1,0)
        a=y*cr+z*sr; b=z*cr-y*sr
        xx=x*cx-a*sx; depth=x*sx+a*cx
        return np.stack((790+scale*xx,332-scale*(b*.97+.24*depth),depth),axis=-1)
    pp=proj(verts)
    normal=np.cross(pp[:,1]-pp[:,0],pp[:,2]-pp[:,0])
    normal/=np.maximum(np.linalg.norm(normal,axis=1,keepdims=True),.001)
    light=.54+.40*np.abs(normal@np.array([-.23,.39,.89]))
    shaded=np.clip(color*light[:,None]+9,0,255).astype('uint8')
    im=Image.new('RGB',(W,H),bg); d=ImageDraw.Draw(im)
    d.rectangle((0,0,331,H),fill=(23,33,48))
    d.text((40,47),'MAGNETRON / R06',font=small,fill='#9bbbd4')
    def wrap(text,xy,width,f,fill,line):
        x,y=xy; s=''
        for word in text.split():
            trial=(s+' '+word).strip()
            if s and d.textlength(trial,font=f)>width:
                d.text((x,y),s,font=f,fill=fill);y+=line;s=word
            else:s=trial
        if s:d.text((x,y),s,font=f,fill=fill)
        return y+line
    y=wrap(stages[index][0],(40,94),250,title,'#f1f5fb',43)+22
    for name,c in labels[index]:
        d.ellipse((42,y+6,52,y+16),fill=palette[c])
        y=wrap(name,(65,y),225,small,'#e0e9f3',22)+9
    for j in np.argsort(pp[:,:,2].mean(1)):
        d.polygon([tuple(pt) for pt in pp[j,:,:2]],fill=tuple(shaded[j]))
    if index==6:
        # Flow is an explanatory overlay. All opaque surfaces are SolidWorks meshes.
        radius=18
        theta=np.linspace(math.pi/8+.23,math.pi/8+math.tau-.23,115)
        arc=np.column_stack((np.full(len(theta),161.7),radius*np.cos(theta),radius*np.sin(theta)))
        ports=[(13*math.cos(math.pi/8+q),13*math.sin(math.pi/8+q)) for q in (.24,-.24)]
        arc=np.vstack(([118.7,*ports[0]],[159.7,*ports[0]],arc,[159.7,*ports[1]],[118.7,*ports[1]]))
        ap=proj(arc)
        for n in range(len(ap)-1):
            u=n/(len(ap)-1)
            c=tuple(round(a+(b-a)*u) for a,b in zip((76,183,254),(255,139,95)))
            d.line([tuple(ap[n,:2]),tuple(ap[n+1,:2])],fill=c,width=5)
        for i in range(11):
            n=int((fraction*340+i*len(ap)/11)%len(ap))
            x,y=ap[n,:2]; d.ellipse((x-4,y-4,x+4,y+4),fill='white')
    d.rectangle((332,589,W,H),fill=(23,33,48))
    wrap(cards[index],(363,610),874,body,'#e7f0f7',28)
    d.text((40,655),f'{index+1:02d} / {len(stages):02d}',font=body,fill='#a4c0d7')
    d.text((363,680),'SolidWorks geometry  /  Design review',font=small,fill='#a4c0d7')
    return np.asarray(im)

if __name__=='__main__':
    lengths=[]
    for i in range(len(stages)):
        with wave.open(str(root/f'.r06-voice-{i}.wav')) as audio:
            lengths.append(math.ceil((audio.getnframes()/audio.getframerate()+.8)*fps))
    if __import__('sys').argv[-1]=='preview':
        for i in (0,4,5,6,8):
            Image.fromarray(scene(i,.47)).save(root/f'.r06-frame-{i}.png')
        raise SystemExit
    out=root/'.r06-silent.mp4'
    writer=imageio_ffmpeg.write_frames(str(out),(W,H),fps=fps,codec='libx264',quality=8)
    writer.send(None)
    for i,frames in enumerate(lengths):
        for j in range(frames):
            writer.send(scene(i,j/(frames-1)))
        print(i+1,flush=True)
    writer.close()
    subs=[]
    def stamp(seconds):
        ms=round(seconds*1000)
        return f'{ms//3600000:02d}:{ms//60000%60:02d}:{ms//1000%60:02d},{ms%1000:03d}'
    import re
    elapsed=0
    voice=root/'.r06-voice-all.wav'
    with wave.open(str(voice),'wb') as dst:
        for i,frames in enumerate(lengths):
            with wave.open(str(root/f'.r06-voice-{i}.wav')) as src:
                if not i: dst.setparams(src.getparams())
                samples=src.getnframes()
                rate=src.getframerate()
                dst.writeframes(src.readframes(samples))
                dst.writeframes(bytes((round(frames/fps*rate)-samples)*src.getsampwidth()*src.getnchannels()))
            sentences=re.split(r'(?<=[.!?]) +',stages[i][1])
            cursor=elapsed
            for sentence in sentences:
                duration=(frames/fps-.25)*len(sentence)/sum(map(len,sentences))
                subs.append(f'{len(subs)+1}\n{stamp(cursor)} --> {stamp(cursor+duration)}\n{sentence}\n')
                cursor+=duration
            elapsed+=frames/fps
    subtitle=root/'magnetron-r06-captions.srt'
    subtitle.write_text('\n'.join(subs),encoding='utf-8')
    subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-y','-loglevel','error','-i',str(out),'-i',str(voice),'-i',str(subtitle),'-c:v','copy','-c:a','aac','-c:s','mov_text','-movflags','+faststart',str(root/'magnetron-r06-assembly-tour.mp4')],check=True)

