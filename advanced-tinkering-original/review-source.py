import json,math,hashlib,cv2
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parent
geometry=json.loads((ROOT/'original-geometry.json').read_text(encoding='utf-8-sig'))
for part in geometry:
    print('\n'+part['name'])
    for b in part['bodies']:
        box=[round(x*1000,4) for x in b['box_m']];print(' box mm',box,'size',[round(box[i+3]-box[i],4) for i in range(3)])
        cylinders={}
        for f in b['faces']:
            if f['kind']=='cylinder':
                p=f['params'];key=tuple(round(x,5) for x in p[3:6]);cylinders.setdefault(key,set()).add(round(p[6]*1000,4))
        print(' cylindrical axes/radii mm',[(k,sorted(v)) for k,v in cylinders.items()])
manifest={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'source').glob('*.step')}
(ROOT/'source-sha256.json').write_text(json.dumps(manifest,indent=2))
frames=ROOT/'video/frames';frames.mkdir(exist_ok=True)
capture=cv2.VideoCapture(str(ROOT/'video/reference-indexed.mp4'))
print('video',capture.get(cv2.CAP_PROP_FRAME_COUNT),capture.get(cv2.CAP_PROP_FPS))
times=[44,64,100,149,169,185,205,219,243,257,335,374,400,434,488,514,532,542,560,585,612,625,637,659,670,685,704,730,743,751,765,789,813,838,857,880,905,1080]
font=ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf',19)
for page,start in enumerate(range(0,len(times),20)):
    sheet=Image.new('RGB',(1920,5*294),'#15202c');draw=ImageDraw.Draw(sheet)
    for j,t in enumerate(times[start:start+20]):
        capture.set(cv2.CAP_PROP_POS_MSEC,t*1000);ok,frame=capture.read()
        if not ok:raise RuntimeError(t)
        im=Image.fromarray(cv2.cvtColor(frame,cv2.COLOR_BGR2RGB));im.save(frames/f'{t:04d}.jpg',quality=94)
        im.thumbnail((480,270));x=(j%4)*480;y=(j//4)*294;sheet.paste(im,(x,y));draw.text((x+8,y+271),f'{t//60:02}:{t%60:02}',font=font,fill='white')
    sheet.save(frames/f'contact-{page+1}.jpg',quality=94)
capture.release()
print('Source frames extracted')
