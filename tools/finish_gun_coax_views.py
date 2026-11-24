"""Repair the five contiguous cable-section shots without retiming the film."""
from pathlib import Path
import json,subprocess,shutil,time
import numpy as np
import imageio_ffmpeg
from build_gun_walkthrough import GunRenderer,SHOTS,OUT,W,H,FPS
WORK=OUT/'render';ff=imageio_ffmpeg.get_ffmpeg_exe();meta=json.loads((OUT/'provenance.json').read_text())
keys={'coax_layers','jacket','braid','dielectric','conductor'};chapters=[c for c in meta['chapters'] if c['key'] in keys];shots={s['key']:s for s in SHOTS}
movie=WORK/'clean-coax.mp4';proc=subprocess.Popen([ff,'-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-an','-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p',str(movie)],stdin=subprocess.PIPE)
r=GunRenderer();clock=time.time()
try:
 for j,ch in enumerate(chapters):
  s=shots[ch['key']];n=round(ch['duration_seconds']*FPS);held=None;print(f'Clean coax {j+1}/5: {s["label"]}',flush=True)
  for k in range(n):
   u=k/(n-1);static=.38<=u<=.55 or u>=.88
   if static and held is not None:im=held
   else:im=r.frame(s,u);held=im if static else None
   proc.stdin.write(np.asarray(im).tobytes())
  for u in [.05,.46,.95]:r.frame(s,u).save(OUT/f'clean-{s["key"]}-{u}.jpg',quality=95)
finally:proc.stdin.close()
assert proc.wait()==0;r.win.Finalize()
silent=OUT/'R06 sputter gun - complete silent walkthrough.mp4';narrated=OUT/'R06 sputter gun - complete narrated walkthrough.mp4'
base=WORK/'before-coax-silent.mp4';voice=WORK/'before-coax-narrated.mp4'
if not base.exists():shutil.copy2(silent,base);shutil.copy2(narrated,voice)
first=round(chapters[0]['start_seconds']*FPS);count=sum(round(c['duration_seconds']*FPS) for c in chapters);last=first+count;total=round(meta['duration_seconds']*FPS)
filters=f'[0:v]trim=end_frame={first},setpts=PTS-STARTPTS[a];[1:v]setpts=PTS-STARTPTS[b];[0:v]trim=start_frame={last},setpts=PTS-STARTPTS[c];[a][b][c]concat=n=3:v=1:a=0[v]'
output=WORK/'finished-picture.mp4'
print('Integrating clean cable views',flush=True)
subprocess.run([ff,'-y','-loglevel','error','-i',str(base),'-i',str(movie),'-i',str(WORK/'chapters.ffmeta'),'-filter_complex',filters,'-map','[v]','-map_metadata','2','-map_chapters','2','-an','-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-r',str(FPS),'-frames:v',str(total),'-movflags','+faststart',str(output)],check=True)
shutil.copy2(output,silent)
subprocess.run([ff,'-y','-loglevel','error','-i',str(output),'-i',str(voice),'-map','0:v','-map','1:a','-map_metadata','0','-map_chapters','0','-c','copy','-t',str(meta['duration_seconds']),'-movflags','+faststart',str(narrated)],check=True)
meta['coax_explosion']='Cable sections separate axially before spreading sideways, preventing coincident section-face flicker.'
(OUT/'provenance.json').write_text(json.dumps(meta,indent=2));print('Finished both gun walkthroughs',flush=True)
