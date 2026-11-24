from pathlib import Path
import json,subprocess,wave,zipfile,shutil
import cv2,numpy as np,imageio_ffmpeg
from PIL import Image
P=Path(__file__).resolve().parent;summary=json.loads((P/'Render summary.json').read_text());video=Path(summary['video']);exe=imageio_ffmpeg.get_ffmpeg_exe()
result=subprocess.run([exe,'-v','error','-i',str(video),'-map','0:v:0','-map','0:a:0','-f','null','-'],capture_output=True,text=True);assert result.returncode==0 and not result.stderr,result.stderr
meta=subprocess.run([exe,'-i',str(video)],capture_output=True,text=True).stderr
assert '1920x1080' in meta and 'h264' in meta and 'aac' in meta and 'mov_text' in meta and meta.count('Chapter #')==11
(P/'Encoded metadata.txt').write_text(meta,encoding='utf-8')
cap=cv2.VideoCapture(str(video));fps=cap.get(cv2.CAP_PROP_FPS);n=cap.get(cv2.CAP_PROP_FRAME_COUNT);assert abs(n/fps-summary['runtime_seconds'])<.2
def get(t):
 cap.set(cv2.CAP_PROP_POS_MSEC,t*1000);ok,a=cap.read();assert ok;return a
images=[]
for i,((t,title),d) in enumerate(zip(summary['timeline'],summary['chapter_durations_seconds'])):
 a=get(t+d*.55);im=Image.fromarray(cv2.cvtColor(a,cv2.COLOR_BGR2RGB));im.save(P/f'encoded-{i:02}.jpg',quality=92);images.append(im.resize((640,360)))
sheet=Image.new('RGB',(1920,1440))
for i,im in enumerate(images):sheet.paste(im,((i%3)*640,(i//3)*360))
sheet.save(P/'Encoded chapter review.jpg')
t=summary['timeline'][1][0];d=summary['chapter_durations_seconds'][1];a=get(t+d*.03);b=get(t+d*.70);motion=float(np.abs(a[:,460:].astype(float)-b[:,460:].astype(float)).mean());assert motion>1
cap.release()
with wave.open(str(P/'narration.wav'),'rb') as f:
 a=np.frombuffer(f.readframes(f.getnframes()),'<i2').astype(float);rms=float(np.sqrt(np.mean(a*a)));assert rms>100
report={'decoded_video_audio':'pass, no decoder errors','resolution':[1920,1080],'fps':fps,'frames':n,'runtime_seconds':n/fps,'chapters':11,'subtitles':'embedded mov_text','narration_rms_pcm16':rms,'exploded_motion_mean_pixel_difference':motion,'sampled_encoded_chapters':11,'bytes':video.stat().st_size}
(P/'Video verification.json').write_text(json.dumps(report,indent=2))
shutil.copy2(P.parent/'single-piece-ptfe-r02'/'Single piece PTFE with outward lip - R02.step',P/'Single piece PTFE with outward lip - R02.step')
shutil.copy2(P.parent/'integrated-single-coax-r02'/'STEP delivery'/'READ ME - integration and limits.txt',P/'Inherited R02 RF integration notes.txt')
files=['Current magnetron R03 - complete study assembly.step','Single piece PTFE with outward lip - R02.step','Current assembly BOM.csv','Assembly verification.json','READ ME - current combined assembly.txt','Inherited R02 RF integration notes.txt','Walkthrough transcript.txt','Video verification.json']
with zipfile.ZipFile(P/'Current magnetron R03 - CAD and walkthrough notes.zip','w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for name in files:z.write(P/name,name)
with zipfile.ZipFile(P/'Current magnetron R03 - CAD and walkthrough notes.zip') as z:assert z.testzip() is None
print(json.dumps(report,indent=2))
