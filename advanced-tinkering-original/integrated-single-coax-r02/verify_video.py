from pathlib import Path
import json,subprocess,wave,math,zipfile
import cv2,numpy as np,imageio_ffmpeg
from PIL import Image
P=Path(__file__).resolve().parent;O=P/'video';summary=json.loads((O/'Render summary.json').read_text());video=Path(summary['video']);exe=imageio_ffmpeg.get_ffmpeg_exe()
decoded=subprocess.run([exe,'-v','error','-i',str(video),'-map','0:v:0','-map','0:a:0','-f','null','-'],capture_output=True,text=True)
assert decoded.returncode==0 and not decoded.stderr,decoded.stderr
meta=subprocess.run([exe,'-i',str(video)],capture_output=True,text=True).stderr
assert '1920x1080' in meta and 'h264' in meta and 'aac' in meta and 'mov_text' in meta
assert meta.count('Chapter #')==6
(O/'Encoded video metadata.txt').write_text(meta)
cap=cv2.VideoCapture(str(video));fps=cap.get(cv2.CAP_PROP_FPS);count=cap.get(cv2.CAP_PROP_FRAME_COUNT);assert abs(count/fps-summary['runtime_seconds'])<.2
durations=[]
for i in range(6):
 with wave.open(str(O/f'voice-{i:02}.wav'),'rb') as f:durations.append(math.ceil((f.getnframes()/f.getframerate()+1.8)*15)/15)
frames=[];t=0
for i,d in enumerate(durations):
 cap.set(cv2.CAP_PROP_POS_MSEC,(t+d*.4)*1000);ok,a=cap.read();assert ok
 im=Image.fromarray(cv2.cvtColor(a,cv2.COLOR_BGR2RGB));im.save(O/f'encoded-{i:02}.jpg',quality=90);frames.append(im.resize((720,405)));t+=d
cap.release();sheet=Image.new('RGB',(1440,1215))
for i,im in enumerate(frames):sheet.paste(im,((i%2)*720,(i//2)*405))
sheet.save(O/'Encoded video contact sheet.jpg')
with wave.open(str(O/'narration.wav'),'rb') as f:
 a=np.frombuffer(f.readframes(f.getnframes()),dtype='<i2').astype(float);rms=float(np.sqrt(np.mean(a*a)));assert rms>100
result={'decoded_video_and_audio':'pass, no decoder errors','codec':'H264 + AAC + embedded text subtitles','resolution':[1920,1080],'fps':fps,'frames':count,'runtime_seconds':count/fps,'embedded_chapters':6,'narration_rms_pcm16':rms,'sampled_encoded_views':6,'bytes':video.stat().st_size}
(O/'Video verification.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))
