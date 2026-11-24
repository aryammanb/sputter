"""Insert the added operating cycle before the assembly tour's closing view."""
from pathlib import Path
import json, subprocess, shutil
import imageio_ffmpeg

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'media/assembly-walkthrough'
OP=OUT/'operation'
final=OUT/'Sputter R06 - mechanical assembly walkthrough.mp4'
if (OUT/'provenance.json').exists() and json.loads((OUT/'provenance.json').read_text()).get('shutter_correction'):
    raise SystemExit('The current movie has the screw-driven shutter correction. Rebuild with build_assembly_walkthrough.py to preserve it; do not reinsert superseded clips.')
combined=OUT/'render/assembly-and-operation.mp4'
assembly=OUT/'Sputter R06 - assembly details.mp4'
record=OUT/'assembly-only-provenance.json'
if not record.exists():
    shutil.copy2(OUT/'provenance.json',record)
    shutil.copy2(final,assembly)
    shutil.copy2(OUT/'Narration.txt',OUT/'Assembly narration.txt')
base=json.loads(record.read_text());operation=json.loads((OP/'provenance.json').read_text())
cut=base['chapters'][-1]['start_seconds']
added=operation['duration_seconds']
chapters=base['chapters'][:-1]
for s in operation['chapters']:chapters.append(s|{'start_seconds':s['start_seconds']+cut})
chapters.append(base['chapters'][-1]|{'start_seconds':cut+added})
metadata=';FFMETADATA1\ntitle=Sputter R06 - assembly and operation walkthrough\n'
for s in chapters:
    metadata+=f'[CHAPTER]\nTIMEBASE=1/1000\nSTART={round(s["start_seconds"]*1000)}\nEND={round((s["start_seconds"]+s["duration_seconds"])*1000)}\ntitle={s["label"]}\n'
meta=OUT/'render/combined-chapters.ffmeta';meta.write_text(metadata,encoding='utf-8')
filt=(f'[0:v]trim=end={cut},setpts=PTS-STARTPTS[v0];[0:a]atrim=end={cut},asetpts=PTS-STARTPTS[a0];'
      f'[1:v]trim=end={added},setpts=PTS-STARTPTS[v1];[1:a]atrim=end={added},asetpts=PTS-STARTPTS[a1];'
      f'[0:v]trim=start={cut}:end={base["duration_seconds"]},setpts=PTS-STARTPTS[v2];[0:a]atrim=start={cut}:end={base["duration_seconds"]},asetpts=PTS-STARTPTS[a2];'
      '[v0][a0][v1][a1][v2][a2]concat=n=3:v=1:a=1[v][a]')
subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-y','-loglevel','error','-i',str(assembly),'-i',str(OP/final.name),'-i',str(meta),'-filter_complex',filt,'-map','[v]','-map','[a]','-map_metadata','2','-map_chapters','2','-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-r','24','-c:a','aac','-b:a','160k','-t',str(base['duration_seconds']+added),'-movflags','+faststart',str(combined)],check=True)
shutil.copy2(combined,final)
base['chapters']=chapters;base['duration_seconds']+=added
base['operation_scope']='Load, close door, evacuate, admit argon, condition target behind closed shutter, open shutter, coat substrate, close shutter, shutdown/vent, unload.'
base['operation_geometry']='Actual CAD shutter rotates 0 to 80 degrees about (-65,0), then returns. No invented plasma/particles/film solids. Complete gun hidden only for top-down shutter sweep.'
(OUT/'provenance.json').write_text(json.dumps(base,indent=2))
text=(OUT/'Assembly narration.txt').read_text(encoding='utf-8');ending=text.rfind('\n\nComplete assembly\n')
assert ending>=0
(OUT/'Narration.txt').write_text(text[:ending]+'\n\n'+(OP/'Narration.txt').read_text(encoding='utf-8')+text[ending:],encoding='utf-8')
print(json.dumps({'duration_seconds':base['duration_seconds'],'chapters':len(chapters),'operation_seconds':added}),flush=True)
