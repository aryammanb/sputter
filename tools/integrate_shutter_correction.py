"""Replace only affected shots with the corrected screw-driven shutter views."""
from pathlib import Path
import json,shutil,subprocess
import imageio_ffmpeg
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'media/assembly-walkthrough';REPAIR=OUT/'shutter-repair'
final=OUT/'Sputter R06 - mechanical assembly walkthrough.mp4'
original=OUT/'Before shutter correction.mp4';record=OUT/'before-shutter-correction.json'
if not record.exists():
    shutil.copy2(final,original);shutil.copy2(OUT/'provenance.json',record)
base=json.loads(record.read_text());repair=json.loads((REPAIR/'provenance.json').read_text())
assert base['source_sha256']==repair['source_sha256'],'Correction must use the same CAD revision.'
fix={s['key']:s for s in repair['chapters']};blocks=[];timeline=[];elapsed=0
for ch in base['chapters']:
    patched=ch['key'] in fix;src=fix[ch['key']] if patched else ch;stream=1 if patched else 0
    start=src['start_seconds'];duration=src['duration_seconds']
    if blocks and blocks[-1]['stream']==stream and abs(blocks[-1]['start']+blocks[-1]['duration']-start)<1e-5:blocks[-1]['duration']+=duration
    else:blocks.append(dict(stream=stream,start=start,duration=duration))
    timeline.append(src|{'start_seconds':elapsed});elapsed+=duration
filters=[];order=''
for j,b in enumerate(blocks):
    i=b['stream'];a=b['start'];z=a+b['duration']
    filters.extend([f'[{i}:v]trim=start={a}:end={z},setpts=PTS-STARTPTS[v{j}]',f'[{i}:a]atrim=start={a}:end={z},asetpts=PTS-STARTPTS[a{j}]'])
    order+=f'[v{j}][a{j}]'
filters.append(order+f'concat=n={len(blocks)}:v=1:a=1[v][a]')
metadata=';FFMETADATA1\ntitle=Sputter R06 - assembly and operation walkthrough\n'
for ch in timeline:metadata+=f'[CHAPTER]\nTIMEBASE=1/1000\nSTART={round(ch["start_seconds"]*1000)}\nEND={round((ch["start_seconds"]+ch["duration_seconds"])*1000)}\ntitle={ch["label"]}\n'
meta=OUT/'render/corrected-shutter.ffmeta';meta.write_text(metadata,encoding='utf-8');output=OUT/'render/corrected-shutter.mp4'
subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-y','-loglevel','error','-i',str(original),'-i',str(REPAIR/final.name),'-i',str(meta),'-filter_complex',';'.join(filters),'-map','[v]','-map','[a]','-map_metadata','2','-map_chapters','2','-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-r','24','-c:a','aac','-b:a','160k','-t',str(elapsed),'-movflags','+faststart',str(output)],check=True)
shutil.copy2(output,final)
shutil.copy2(output,OUT/'Sputter R06 - corrected shutter.mp4')
base['chapters']=timeline;base['duration_seconds']=elapsed
base['shutter_correction']='Screw and shutter blade rotate together about (-65,0). Nuts, washer and seal remain stationary during actuation.'
base['operation_geometry']='Actual CAD screw and shutter blade rotate 0 to 80 degrees about (-65,0), then return. No invented plasma/particles/film solids. Complete gun hidden only for top-down shutter sweep.'
(OUT/'provenance.json').write_text(json.dumps(base,indent=2))
# Assemble the transcript from the render's current shot definitions.
from build_assembly_walkthrough import SHOTS
texts={s['key']:s for s in SHOTS}
(OUT/'Narration.txt').write_text('\n\n'.join(texts[s['key']]['label']+'\n'+texts[s['key']]['speech'] for s in timeline),encoding='utf-8')
print(json.dumps({'duration_seconds':elapsed,'corrected_shots':list(fix),'blocks':len(blocks)}),flush=True)
