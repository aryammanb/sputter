from pathlib import Path
import json,subprocess,wave,math
import cv2,imageio_ffmpeg,numpy as np
from PIL import Image

p=Path(__file__).resolve().parent/'coax-video'
summary=json.loads((p/'Render summary.json').read_text())
v=p/'SMA coax mating and electrical isolation - 3D explanation.mp4'
ff=imageio_ffmpeg.get_ffmpeg_exe()
meta=subprocess.run([ff,'-hide_banner','-i',str(v)],capture_output=True,text=True).stderr
(p/'Encoded metadata.txt').write_text(meta)
assert meta.count('Chapter #')==7
assert all(s in meta for s in ['1920x1080','h264','aac','mov_text'])
test=subprocess.run([ff,'-v','error','-i',str(v),'-map','0:v:0','-map','0:a:0','-f','null','-'],capture_output=True,text=True)
assert test.returncode==0 and not test.stderr.strip(),test.stderr
cap=cv2.VideoCapture(str(v));assert cap.isOpened();fps=cap.get(cv2.CAP_PROP_FPS);count=int(cap.get(cv2.CAP_PROP_FRAME_COUNT));assert fps==15
assert abs(count/fps-summary['runtime_seconds'])<.1
sheet=Image.new('RGB',(1440,810),'#101b2a');start=0
for i in range(7):
 with wave.open(str(p/f'voice-{i:02}.wav')) as f:duration=math.ceil((f.getnframes()/f.getframerate()+1.8)*fps)/fps
 cap.set(cv2.CAP_PROP_POS_MSEC,(start+.65*duration)*1000);ok,frame=cap.read();assert ok
 im=Image.fromarray(cv2.cvtColor(frame,cv2.COLOR_BGR2RGB));im.save(p/f'encoded-check-{i:02}.jpg');im.thumbnail((480,270));sheet.paste(im,((i%3)*480,(i//3)*270));start+=duration
cap.release();sheet.save(p/'Encoded chapter review.jpg')
with wave.open(str(p/'narration.wav')) as f:
 duration=f.getnframes()/f.getframerate();a=np.frombuffer(f.readframes(f.getnframes()),'<i2').astype(float)
assert abs(duration-count/fps)<.01
assert np.sqrt(np.mean(a*a))>500
report={'video':str(v),'runtime_seconds':count/fps,'resolution':[1920,1080],'fps':fps,'frames':count,'chapters':7,'embedded_subtitles':True,'full_audio_video_decode':'passed without errors','audio_rms':float(np.sqrt(np.mean(a*a))),'bytes':v.stat().st_size,'chapter_frames_reviewed':7,'scope':'Native terminal plate and source head bodies; explanatory connector internals and proposed head termination; no electrical rating or field simulation.'}
(p/'Video verification.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
