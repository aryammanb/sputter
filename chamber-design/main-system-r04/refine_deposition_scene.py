from pathlib import Path
import math,wave,json,subprocess
P=Path(__file__).resolve().parent;p=P/'render_main.py';src=p.read_text()
needle=" cam.SetViewUp(0,1,0) if view=='internals' and u>.65 else cam.SetViewUp(0,0,1)"
extra="""
 if view=='demo_open' and u>.4:
  v=smooth((u-.4)/.3);focus=np.array([0.,0.,105.-55*v]);scale=125-45*v;direction=np.array([.7-.2*v,-1.,-.05+1.05*v])
"""
if extra not in src:src=src.replace(needle,extra+needle);p.write_text(src)
env={'__file__':str(p),'__name__':'deposition_detail'};exec(compile(src.split("if 'preview' in sys.argv:")[0],str(p),'exec'),env)
from PIL import Image
Image.fromarray(env['frame'](19,.72)).save(P/'Deposition stage detail.png')
if 'preview' in __import__('sys').argv:raise SystemExit()
with wave.open(str(P/'voice-19.wav'),'rb') as f:duration=math.ceil((f.getnframes()/f.getframerate()+1.4)*8)/8
writer=env['imageio_ffmpeg'].write_frames(str(P/'Deposition detail scene.mp4'),(1600,900),fps=8,codec='libx264',quality=8,macro_block_size=1,output_params=['-preset','fast']);writer.send(None)
for n in range(round(duration*8)):writer.send(env['frame'](19,n/(duration*8-1)))
writer.close();env['win'].Finalize();print('Deposition detail replacement rendered',duration,flush=True)
