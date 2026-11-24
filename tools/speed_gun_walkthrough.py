from pathlib import Path
import json,subprocess,math,time
import imageio_ffmpeg
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'media/gun-complete-walkthrough'
WORK=OUT/'render/8x';WORK.mkdir(parents=True,exist_ok=True)
source=OUT/'R06 sputter gun - complete silent walkthrough.mp4'
dest=OUT/'R06 sputter gun - 8x faster silent walkthrough.mp4'
meta=json.loads((OUT/'provenance.json').read_text())
shots={s['key']:s for s in json.loads((OUT/'shots.json').read_text())}
segments=[];chapters=[];base=0;outbase=0
for ch in meta['chapters']:
 n=round(ch['duration_seconds']*24);mode=shots[ch['key']]['mode']
 if mode=='overall':ranges=[(0,9),(round(.1*(n-1)),round(.8*(n-1))),(n-12,n-1)]
 elif mode=='reassemble':ranges=[(0,9),(round(.1*(n-1)),round(.9*(n-1))),(n-12,n-1)]
 elif mode in {'orbit','static'}:ranges=[(0,n-1)]
 else:ranges=[(0,math.floor(.38*(n-1))+6),(math.ceil(.55*(n-1)),math.floor(.88*(n-1))+12)]
 ranges=[(max(0,a),min(n-1,b)) for a,b in ranges]
 retained=sum(b-a+1 for a,b in ranges);duration=n/24/8;speed=retained/24/duration
 chapters.append({'key':ch['key'],'label':ch['label'],'start_seconds':outbase,'duration_seconds':duration,'source_frames':n,'retained_source_frames':retained,'motion_speed':speed})
 for a,b in ranges:
  segments.append((base+a,base+b,outbase,speed));outbase+=(b-a+1)/24/speed
 base+=n
def balanced(terms):
 if len(terms)==1:return terms[0]
 h=len(terms)//2;return '('+balanced(terms[:h])+'+'+balanced(terms[h:])+')'
select=balanced(list(f'between(n,{a},{b})' for a,b,_,_ in segments))
timing=balanced(list(f'between(PTS*TB,{(a-.25)/24:.9f},{(b+.25)/24:.9f})*({t:.12f}+(PTS*TB-{a/24:.12f})/{s:.12f})' for a,b,t,s in segments))
filterfile=WORK/'speed.filter'
filterfile.write_text(f"[0:v]select='{select}',setpts='({timing})/TB',fps=30,tpad=stop_mode=clone:stop_duration=0.1[v]")
chapterfile=WORK/'chapters.ffmeta'
text=';FFMETADATA1\ntitle=R06 sputter gun - 8x faster full walkthrough\n'
for c in chapters:
 text+=f"[CHAPTER]\nTIMEBASE=1/1000\nSTART={round(c['start_seconds']*1000)}\nEND={round((c['start_seconds']+c['duration_seconds'])*1000)}\ntitle={c['label']}\n"
chapterfile.write_text(text,encoding='utf-8')
ff=imageio_ffmpeg.get_ffmpeg_exe();frames=round(outbase*30)
print(json.dumps({'source_seconds':base/24,'output_seconds':frames/30,'shots':len(chapters),'retained_seconds':sum(b-a+1 for a,b,_,_ in segments)/24}),flush=True)
subprocess.run([ff,'-y','-loglevel','error','-i',str(source),'-i',str(chapterfile),'-/filter_complex',str(filterfile),'-map','[v]','-map_metadata','1','-map_chapters','1','-an','-sn','-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-frames:v',str(frames),'-movflags','+faststart',str(dest)],check=True)
report={'source':str(source),'video':str(dest),'source_seconds':base/24,'duration_seconds':frames/30,'resolution':[1920,1080],'fps':30,'audio':False,'shots_retained':len(chapters),'chapters':chapters,'edit':'Trimmed stationary holds and accelerated retained ranges to eight times shorter overall; every original shot retained.'}
(OUT/'8x-edit.json').write_text(json.dumps(report,indent=2));print(str(dest),flush=True)

