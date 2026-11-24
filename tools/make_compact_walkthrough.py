"""Keep every frame of the corrected tour, remove audio, play 2.5x faster."""
from pathlib import Path
import json,subprocess,hashlib
import imageio_ffmpeg

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'media/assembly-walkthrough'
source=OUT/'Sputter R06 - corrected shutter.mp4'
dest=OUT/'Sputter R06 - silent 4 minute walkthrough.mp4'
original=json.loads((OUT/'provenance.json').read_text())
if original.get('complete_shutter_rotation'):
    source=OUT/'Sputter R06 - mechanical assembly walkthrough.mp4'
elif (OUT/'compact-provenance.json').exists() and json.loads((OUT/'compact-provenance.json').read_text()).get('complete_shutter_rotation'):
    raise SystemExit('The compact movie has the complete shutter rotation fix. Rebuild the full tour with build_assembly_walkthrough.py before retiming; do not use the superseded narrated source.')
assert original.get('shutter_correction'),'Use the corrected screw-driven version.'
speed=2.5
source_frames=round(original['duration_seconds']*original['fps'])
chapters=[s|{'start_seconds':s['start_seconds']/speed,'duration_seconds':s['duration_seconds']/speed} for s in original['chapters']]
metadata=';FFMETADATA1\ntitle=Sputter R06 - silent system walkthrough\n'
for s in chapters:
    metadata+=f'[CHAPTER]\nTIMEBASE=1/1000\nSTART={round(s["start_seconds"]*1000)}\nEND={round((s["start_seconds"]+s["duration_seconds"])*1000)}\ntitle={s["label"]}\n'
meta=OUT/'render/compact-chapters.ffmeta';meta.write_text(metadata,encoding='utf-8')
# The source has 24 frames per second. Re-timestamping every input frame at
# 60 fps gives exactly 2.5x playback without discarding any source frames.
subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-y','-loglevel','error','-i',str(source),'-i',str(meta),'-map','0:v:0','-map_metadata','1','-map_chapters','1','-vf','settb=1/60,setpts=N','-an','-sn','-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-r','60','-fps_mode','cfr','-frames:v',str(source_frames),'-movflags','+faststart',str(dest)],check=True)
report=original|{'source_video':source.name,'source_video_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'duration_seconds':original['duration_seconds']/speed,'fps':60,'speed_multiplier':speed,'audio':False,'narration':None,'chapters':chapters,'editing':'All source frames and all 37 shots retained in their original order; retimed from 24 to 60 fps; audio removed.'}
(OUT/'compact-provenance.json').write_text(json.dumps(report,indent=2))
print(json.dumps({'video':str(dest),'duration_seconds':report['duration_seconds'],'shots':len(chapters),'fps':60,'audio':False}),flush=True)
