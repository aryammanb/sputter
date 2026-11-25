from pathlib import Path
import json,subprocess,re,zipfile,wave
import cadquery as cq
import imageio_ffmpeg,numpy as np
from PIL import Image
P=Path(__file__).resolve().parent
checks={}
for name in ['Refined compression fitting - assembled.step','Refined compression fitting - exploded.step','Chamber R02 - refined fitting door closed.step','Chamber R02 - refined fitting door open.step']:
 s=cq.importers.importStep(str(P/name)).val();solids=s.Solids();assert all(x.isValid() for x in solids)
 checks[name]={'solids':len(solids),'all_valid':True}
 print('Reimported',name,len(solids),'valid solids',flush=True)
body=cq.importers.importStep(str(P/'body.step')).val();cap=cq.importers.importStep(str(P/'cap.step')).val()
engagement=[]
for lift in [0,1.3,2,4]:
 s=cap.rotate((0,0,0),(0,0,1),180*lift).translate((0,0,lift))
 c=body.intersect(s);v=c.Volume() if c.Solids() else 0
 assert v<.001,(lift,v)
 engagement.append({'lift_mm':lift,'rotation_deg':180*lift,'body_cap_overlap_mm3':v})
(P/'CAD verification.json').write_text(json.dumps({'reimport':checks,'thread_motion_samples':engagement},indent=2))
video=P/'Gun compression fitting - assembly and adjustment.mp4'
if not video.exists():print('CAD verified; video still pending');raise SystemExit()
exe=imageio_ffmpeg.get_ffmpeg_exe();vr=json.loads((P/'Video verification.json').read_text())
subprocess.run([exe,'-v','error','-i',str(video),'-map','0:v','-map','0:a','-f','null','-'],check=True)
info=subprocess.run([exe,'-hide_banner','-i',str(video)],capture_output=True,text=True).stderr
assert 'Video: h264' in info and 'Audio: aac' in info and 'Subtitle: mov_text' in info
assert len(re.findall(r'Chapter #',info))==8
levels=[]
sheet=Image.new('RGB',(1600,1800),'#101a29')
for i,(start,title) in enumerate(vr['chapters']):
 with wave.open(str(P/f'voice-{i:02}.wav'),'rb') as f:
  a=np.frombuffer(f.readframes(f.getnframes()),'<i2').astype(float);rms=float(np.sqrt(np.mean(a*a)));assert rms>100;levels.append(rms)
 end=vr['chapters'][i+1][0] if i<7 else vr['duration_seconds']
 frame=P/f'Encoded check {i+1:02}.png'
 subprocess.run([exe,'-y','-v','error','-ss',str(start+.6*(end-start)),'-i',str(video),'-frames:v','1',str(frame)],check=True)
 sheet.paste(Image.open(frame).resize((800,450)),((i%2)*800,(i//2)*450))
sheet.save(P/'Encoded animation contact sheet.jpg')
vr.update(full_audio_video_decode_passed=True,embedded_chapters=8,subtitle_codec='mov_text',narration_rms=levels)
(P/'Video verification.json').write_text(json.dumps(vr,indent=2))
with zipfile.ZipFile(P/'Compression fitting R02 - refined CAD.zip','w',zipfile.ZIP_DEFLATED) as z:
 for p in P.iterdir():
  if p.suffix in ['.step','.txt','.json','.py','.ps1'] or p.name in ['preview-00.png','preview-06.png']:
   z.write(p,p.name)
print(json.dumps({'video_seconds':vr['duration_seconds'],'CAD_zip_bytes':(P/'Compression fitting R02 - refined CAD.zip').stat().st_size,'thread_samples_clear':True}),flush=True)
