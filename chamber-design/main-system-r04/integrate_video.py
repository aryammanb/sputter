from pathlib import Path
import json,re,subprocess
import imageio_ffmpeg
P=Path(__file__).resolve().parent;F=P.parent/'compression-fitting-r02';exe=imageio_ffmpeg.get_ffmpeg_exe()
main=json.loads((P/'Scene timing.json').read_text());fit=json.loads((F/'Video verification.json').read_text())
cut=main['chapters'][2][0];fitend=fit['chapters'][7][0]
total=main['duration_seconds']+fitend
timeline=main['chapters'][:2]+[[cut+t,title] for t,title in fit['chapters'][:7]]+[[t+fitend,title] for t,title in main['chapters'][2:]]
def stamp(t):
 n=round(t*1000);return f'{n//3600000:02}:{n//60000%60:02}:{n//1000%60:02},{n%1000:03}'
def seconds(s):
 h,m,x=s.replace(',','.').split(':');return int(h)*3600+int(m)*60+float(x)
def captions(path):
 out=[]
 for b in re.split(r'\n\s*\n',path.read_text(encoding='utf-8').strip()):
  a=b.splitlines()
  if len(a)>=3 and '-->' in a[1]:
   start,end=a[1].split(' --> ');out.append((seconds(start),seconds(end),'\n'.join(a[2:])))
 return out
subs=[]
for a,b,s in captions(P/'System captions.srt'):
 shift=0 if a<cut else fitend;subs.append((a+shift,b+shift,s))
for a,b,s in captions(F/'Captions.srt'):
 if a<fitend:subs.append((a+cut,min(b,fitend)+cut,s))
subs.sort();(P/'Captions.srt').write_text('\n\n'.join(f'{i+1}\n{stamp(a)} --> {stamp(b)}\n{s}' for i,(a,b,s) in enumerate(subs))+'\n',encoding='utf-8')
fm=';FFMETADATA1\ntitle=Complete sputter system R04 - main walkthrough\n'
for i,(t,title) in enumerate(timeline):
 end=timeline[i+1][0] if i+1<len(timeline) else total
 fm+=f'[CHAPTER]\nTIMEBASE=1/1000\nSTART={round(t*1000)}\nEND={round(end*1000)}\ntitle={title}\n'
(P/'chapters.ffmeta').write_text(fm)
detail_start=main['chapters'][19][0];detail_end=main['chapters'][20][0]
filt=(f'[0:v]trim=start=0:end={cut},setpts=PTS-STARTPTS,fps=12[v0];[0:a]atrim=start=0:end={cut},asetpts=PTS-STARTPTS[a0];'
 f'[1:v]trim=start=0:end={fitend},setpts=PTS-STARTPTS,fps=12[v1];[1:a]atrim=start=0:end={fitend},asetpts=PTS-STARTPTS[a1];'
 f'[0:v]trim=start={cut}:end={detail_start},setpts=PTS-STARTPTS,fps=12[v2];[0:a]atrim=start={cut}:end={detail_start},asetpts=PTS-STARTPTS[a2];'
 f'[2:v]setpts=PTS-STARTPTS,fps=12[v3];[0:a]atrim=start={detail_start}:end={detail_end},asetpts=PTS-STARTPTS[a3];'
 f'[0:v]trim=start={detail_end},setpts=PTS-STARTPTS,fps=12[v4];[0:a]atrim=start={detail_end},asetpts=PTS-STARTPTS[a4];'
 '[v0][a0][v1][a1][v2][a2][v3][a3][v4][a4]concat=n=5:v=1:a=1[v][a]')
subprocess.run([exe,'-y','-v','error','-i',str(P/'System scenes.mp4'),'-i',str(F/'Gun compression fitting - assembly and adjustment.mp4'),'-i',str(P/'Deposition detail scene.mp4'),'-filter_complex',filt,'-map','[v]','-map','[a]','-c:v','libx264','-preset','fast','-crf','20','-pix_fmt','yuv420p','-c:a','aac','-movflags','+faststart',str(P/'Integrated picture and audio.mp4')],check=True)
final=P/'Complete sputter system R04 - main walkthrough.mp4'
subprocess.run([exe,'-y','-v','error','-i',str(P/'Integrated picture and audio.mp4'),'-i',str(P/'Captions.srt'),'-i',str(P/'chapters.ffmeta'),'-map','0:v','-map','0:a','-map','1:s','-map_metadata','2','-map_chapters','2','-c:v','copy','-c:a','copy','-c:s','mov_text','-movflags','+faststart',str(final)],check=True)
mainchs=json.loads((P/'chapters.json').read_text());fitchs=json.loads((F/'chapters.json').read_text());speeches=mainchs[:2]+fitchs[:7]+mainchs[2:]
trans=[]
for (t,title),ch in zip(timeline,speeches):trans += [f'{int(t)//60}:{int(t)%60:02} {title}',ch['speech'],'']
(P/'Video transcript.txt').write_text('\n'.join(trans),encoding='utf-8')
(P/'Video verification.json').write_text(json.dumps({'duration_seconds':total,'chapters':timeline,'fps':12,'resolution':[1600,900],'integrated_fitting_seconds':fitend,'video':str(final)},indent=2))
print(json.dumps({'video_seconds':total,'chapters':len(timeline),'fitting_segment_seconds':fitend}),flush=True)
