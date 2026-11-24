from pathlib import Path
import json,subprocess,wave,re,zipfile
import numpy as np
from PIL import Image
import imageio_ffmpeg
P=Path(__file__).resolve().parent;exe=imageio_ffmpeg.get_ffmpeg_exe()
video=P/'Twelve stack magnetron - mechanical comparison.mp4'
report=json.loads((P/'Video verification.json').read_text())
chapters=json.loads((P/'chapters.json').read_text())
# Sentence-level subtitles retain readability when enabled in a video player.
def stamp(t):
 n=round(t*1000);return f'{n//3600000:02}:{n//60000%60:02}:{n//1000%60:02},{n%1000:03}'
subs=[]
for i,(start,title) in enumerate(report['chapters']):
 end=report['chapters'][i+1][0] if i+1<len(chapters) else report['duration_seconds']
 sentences=[s.strip()+'.' for s in chapters[i]['speech'].split('.') if s.strip()]
 total=sum(map(len,sentences));t=start+.35
 for sentence in sentences:
  finish=t+(end-start-1.5)*len(sentence)/total
  subs.append(f'{len(subs)+1}\n{stamp(t)} --> {stamp(finish)}\n{sentence}\n');t=finish
(P/'Captions.srt').write_text('\n'.join(subs),encoding='utf-8')
temp=P/'final-with-captions.mp4'
subprocess.run([exe,'-y','-v','error','-i',str(video),'-i',str(P/'Captions.srt'),'-map','0:v','-map','0:a','-map','1:s','-map_metadata','0','-map_chapters','0','-c:v','copy','-c:a','copy','-c:s','mov_text','-movflags','+faststart',str(temp)],check=True)
temp.replace(video)
subprocess.run([exe,'-v','error','-i',str(video),'-map','0:v','-map','0:a','-f','null','-'],check=True)
info=subprocess.run([exe,'-hide_banner','-i',str(video)],capture_output=True,text=True).stderr
assert 'Video: h264' in info and 'Audio: aac' in info and 'Subtitle: mov_text' in info
assert len(re.findall(r'Chapter #',info))==7
levels=[]
for i in range(7):
 with wave.open(str(P/f'voice-{i:02}.wav'),'rb') as f:
  a=np.frombuffer(f.readframes(f.getnframes()),'<i2').astype(float);rms=float(np.sqrt(np.mean(a*a)));assert rms>100;levels.append(rms)
for i,t in [(2,65),(4,120),(6,185)]:
 subprocess.run([exe,'-y','-v','error','-ss',str(t),'-i',str(video),'-frames:v','1',str(P/f'Encoded video check {i}.png')],check=True)
report.update(full_audio_video_decode_passed=True,video_codec='h264',audio_codec='aac',subtitle_codec='mov_text',embedded_chapters=7,narration_rms=levels)
(P/'Video verification.json').write_text(json.dumps(report,indent=2))
geometry=json.loads((P/'Geometry verification.json').read_text());assert geometry['unexplained_changed_component_interferences']==0
files=['Original R03 comparison.step','Proposed twelve stack mechanical study.step','Proposed cooler.step','Proposed closure.step','Proposed yoke.step','Mechanical changes explained.txt','Part change register.csv','Geometry verification.json','Video transcript.txt']
with zipfile.ZipFile(P/'Twelve stack magnetron - CAD comparison.zip','w',zipfile.ZIP_DEFLATED) as z:
 for name in files:z.write(P/name,arcname=name)
print(json.dumps({'video_seconds':report['duration_seconds'],'video_bytes':video.stat().st_size,'cad_zip_bytes':(P/'Twelve stack magnetron - CAD comparison.zip').stat().st_size,'valid_proposed_solids':geometry['step_reimport_valid_solids']['new'],'unexplained_changed_component_interferences':0},indent=2))
