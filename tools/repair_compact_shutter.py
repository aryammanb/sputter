"""Re-render only the six shutter shots, retaining the compact movie timing."""
from pathlib import Path
import json,subprocess,time
import numpy as np
import imageio_ffmpeg
from build_assembly_walkthrough import Renderer,SHOTS,W,H
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'media/assembly-walkthrough';WORK=OUT/'complete-shutter-repair';WORK.mkdir(exist_ok=True)
base=json.loads((OUT/'compact-provenance.json').read_text())
keys={'shutter_install','op_load','op_sweep','op_deposit','op_stop','op_unload'}
shots={s['key']:s for s in SHOTS};selected=[s for s in base['chapters'] if s['key'] in keys]
movie=WORK/'Complete shutter rotation - silent.mp4';ff=imageio_ffmpeg.get_ffmpeg_exe();fps=60
r=Renderer();proc=subprocess.Popen([ff,'-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(fps),'-i','-','-an','-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p',str(movie)],stdin=subprocess.PIPE)
timeline=[];elapsed=0;clock=time.time()
try:
    for j,ch in enumerate(selected):
        n=round(ch['duration_seconds']*fps);s=shots[ch['key']]
        print(f'{j+1}/{len(selected)} {ch["label"]}; {time.time()-clock:.0f}s elapsed',flush=True)
        for k in range(n):proc.stdin.write(np.asarray(r.frame(s,k/(n-1))).tobytes())
        timeline.append(ch|{'start_seconds':elapsed,'duration_seconds':n/fps});elapsed+=n/fps
finally:proc.stdin.close()
if proc.wait()!=0:raise RuntimeError('Repair encoding failed')
r.win.Finalize();(WORK/'timing.json').write_text(json.dumps({'chapters':timeline,'fps':fps,'duration_seconds':elapsed},indent=2));print('Shutter shot rendering complete',flush=True)
