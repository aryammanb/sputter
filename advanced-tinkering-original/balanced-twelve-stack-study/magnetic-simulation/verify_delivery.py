from pathlib import Path
import json,subprocess,re,wave,zipfile
import numpy as np
import imageio_ffmpeg
P=Path(__file__).resolve().parent;exe=imageio_ffmpeg.get_ffmpeg_exe();video=P/'Magnetic circuit simulation - confinement assessment.mp4'
r=json.loads((P/'Video verification.json').read_text());assessment=json.loads((P/'Assessment results.json').read_text())
subprocess.run([exe,'-v','error','-i',str(video),'-map','0:v','-map','0:a','-f','null','-'],check=True)
info=subprocess.run([exe,'-hide_banner','-i',str(video)],capture_output=True,text=True).stderr
assert 'Video: h264' in info and 'Audio: aac' in info and 'Subtitle: mov_text' in info
assert len(re.findall(r'Chapter #',info))==7
levels=[]
for i in range(7):
 with wave.open(str(P/f'voice-{i:02}.wav'),'rb') as f:
  a=np.frombuffer(f.readframes(f.getnframes()),'<i2').astype(float);level=float(np.sqrt(np.mean(a*a)));assert level>100;levels.append(level)
for i,(t,title) in enumerate(r['chapters']):
 end=r['chapters'][i+1][0] if i+1<7 else r['duration_seconds'];sample=(t+end)/2
 subprocess.run([exe,'-y','-v','error','-ss',str(sample),'-i',str(video),'-frames:v','1',str(P/f'Encoded chapter {i+1}.png')],check=True)
r.update(full_audio_video_decode_passed=True,embedded_chapters=7,video_codec='h264',audio_codec='aac',captions='mov_text, sentence-level',narration_rms=levels)
(P/'Video verification.json').write_text(json.dumps(r,indent=2))
assert assessment['numerical_verification']['numerical_checks_passed']
include=[]
for pattern in ['*.py','requirements.txt','Simulation assessment.txt','Assessment results.json','*_metrics.json','*_solve.json','*_mesh.json','*_analytic_validation.json','*sensitivity.json','*.csv','Target field map.png','Field section.png','Racetrack uniformity.png','Field versus height.png','Video transcript.txt','Video verification.json','chapters.json','narrate.ps1','fine_mesh.npz','fine_nominal_field.npz','fine_nominal_samples.npz']:
 include.extend(P.glob(pattern))
archive=P/'Magnetic simulation model and results.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
 for path in sorted(set(include)):z.write(path,arcname='magnetic-simulation/'+path.name)
 for name in ['Proposed yoke.step','parts.json','meshes.bin']:z.write(P.parent/name,arcname=name)
print(json.dumps({'video_seconds':r['duration_seconds'],'video_bytes':video.stat().st_size,'archive_bytes':archive.stat().st_size,'chapters':7,'numerical_checks_passed':True,'full_video_decode_passed':True},indent=2))
