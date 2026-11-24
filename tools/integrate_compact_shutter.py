"""Replace shutter shots in the silent four-minute film without retiming it."""
from pathlib import Path
import json,subprocess,shutil
import imageio_ffmpeg
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'media/assembly-walkthrough';WORK=OUT/'complete-shutter-repair'
current=OUT/'Sputter R06 - silent 4 minute walkthrough.mp4';before=WORK/'Before complete shutter rotation.mp4';record=WORK/'before-compact-provenance.json'
if not record.exists():shutil.copy2(current,before);shutil.copy2(OUT/'compact-provenance.json',record)
base=json.loads(record.read_text());repair=json.loads((WORK/'timing.json').read_text());fix={s['key']:s for s in repair['chapters']}
blocks=[]
for ch in base['chapters']:
    stream=1 if ch['key'] in fix else 0;s=fix.get(ch['key'],ch)
    assert abs(s['duration_seconds']-ch['duration_seconds'])<1e-5
    if blocks and blocks[-1]['stream']==stream and abs(blocks[-1]['start']+blocks[-1]['duration']-s['start_seconds'])<1e-5:blocks[-1]['duration']+=s['duration_seconds']
    else:blocks.append({'stream':stream,'start':s['start_seconds'],'duration':s['duration_seconds']})
filters=[];order=''
for j,b in enumerate(blocks):
    first=round(b['start']*60);end=round((b['start']+b['duration'])*60)
    filters.append(f'[{b["stream"]}:v]trim=start_frame={first}:end_frame={end},setpts=PTS-STARTPTS[v{j}]');order+=f'[v{j}]'
filters.append(order+f'concat=n={len(blocks)}:v=1:a=0[v]')
metadata=';FFMETADATA1\ntitle=Sputter R06 - silent system walkthrough\n'
for s in base['chapters']:metadata+=f'[CHAPTER]\nTIMEBASE=1/1000\nSTART={round(s["start_seconds"]*1000)}\nEND={round((s["start_seconds"]+s["duration_seconds"])*1000)}\ntitle={s["label"]}\n'
meta=WORK/'chapters.ffmeta';meta.write_text(metadata,encoding='utf-8');dest=OUT/'Sputter R06 - silent 4 minute walkthrough v2.mp4'
subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-y','-loglevel','error','-i',str(before),'-i',str(WORK/'Complete shutter rotation - silent.mp4'),'-i',str(meta),'-filter_complex',';'.join(filters),'-map','[v]','-map_metadata','2','-map_chapters','2','-an','-sn','-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-r','60','-fps_mode','cfr','-frames:v',str(round(base['duration_seconds']*60)),'-movflags','+faststart',str(dest)],check=True)
shutil.copy2(dest,current)
base['shutter_correction']='The screw, nuts, washer and shutter blade rotate together about (-65,0); only the compressed O-ring remains stationary.'
base['complete_shutter_rotation']=True
base['operation_geometry']='Complete shutter assembly rotates 0 to 80 degrees, then returns. O-ring remains compressed and stationary. No gun disassembly or simulated plasma/film geometry.'
base['visual_rotation_cue']='Small gold surface colour witness mark on existing screw mesh; no additional CAD geometry.'
base['editing']='All 37 shots, order, duration and timing retained from the 3:59.6 silent film. Only six shutter views re-rendered for coupled rotation and screw witness mark.'
(OUT/'compact-provenance.json').write_text(json.dumps(base,indent=2));print(str(dest),flush=True)
