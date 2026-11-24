from pathlib import Path
import json,subprocess,wave
import cv2,numpy as np,imageio_ffmpeg
from PIL import Image
P=Path(__file__).resolve().parent;s=json.loads((P/'Video summary.json').read_text());v=Path(s['video']);exe=imageio_ffmpeg.get_ffmpeg_exe()
r=subprocess.run([exe,'-v','error','-i',str(v),'-map','0:v:0','-map','0:a:0','-f','null','-'],capture_output=True,text=True)
assert r.returncode==0 and not r.stderr,r.stderr
c=cv2.VideoCapture(str(v));n=c.get(cv2.CAP_PROP_FRAME_COUNT);fps=c.get(cv2.CAP_PROP_FPS);assert abs(n/fps-s['duration_seconds'])<.15
t=0;images=[]
for i,d in enumerate(s['chapter_durations_seconds']):
 c.set(cv2.CAP_PROP_POS_MSEC,(t+d*.5)*1000);ok,a=c.read();assert ok
 im=Image.fromarray(cv2.cvtColor(a,cv2.COLOR_BGR2RGB));im.save(P/f'Encoded view {i+1}.jpg',quality=92);images.append(im.resize((960,540)));t+=d
c.release();sheet=Image.new('RGB',(960,1620))
for i,im in enumerate(images):sheet.paste(im,(0,i*540))
sheet.save(P/'Encoded video review.jpg')
with wave.open(str(P/'Narration.wav'),'rb') as f:
 a=np.frombuffer(f.readframes(f.getnframes()),'<i2').astype(float);rms=float(np.sqrt(np.mean(a*a)));assert rms>100
result={'decode':'pass, no audio/video decoder errors','fps':fps,'frames':n,'runtime_seconds':n/fps,'narration_rms':rms,'sampled_encoded_views':3,'bytes':v.stat().st_size}
(P/'Video verification.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
