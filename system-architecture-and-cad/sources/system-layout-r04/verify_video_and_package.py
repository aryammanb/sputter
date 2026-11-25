from pathlib import Path
import json,re,subprocess,zipfile
import imageio_ffmpeg
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parent;exe=imageio_ffmpeg.get_ffmpeg_exe();vr=json.loads((P/'Video verification.json').read_text());video=P/'Complete sputter system R04 - main walkthrough.mp4'
subprocess.run([exe,'-v','error','-i',str(video),'-map','0:v','-map','0:a','-f','null','-'],check=True)
info=subprocess.run([exe,'-hide_banner','-i',str(video)],capture_output=True,text=True).stderr
assert 'Video: h264' in info and 'Audio: aac' in info and 'Subtitle: mov_text' in info
assert len(re.findall(r'Chapter #',info))==len(vr['chapters'])==28
sheet=Image.new('RGB',(1920,7*300),'#101a29');d=ImageDraw.Draw(sheet)
for j,(start,title) in enumerate(vr['chapters']):
 end=vr['chapters'][j+1][0] if j+1<len(vr['chapters']) else vr['duration_seconds'];t=start+(.68 if 'open: deposition' in title else .42)*(end-start)
 path=P/f'Encoded chapter {j+1:02}.png';subprocess.run([exe,'-y','-v','error','-ss',str(t),'-i',str(video),'-frames:v','1',str(path)],check=True)
 x=(j%4)*480;y=(j//4)*300;sheet.paste(Image.open(path).resize((480,270)),(x,y));d.text((x+6,y+275),f'{j+1:02} {title}',fill='white')
sheet.save(P/'Encoded main video contact sheet.jpg')
vr.update(full_audio_video_decode_passed=True,embedded_chapters=28,subtitle_codec='mov_text');(P/'Video verification.json').write_text(json.dumps(vr,indent=2))
files=[p for p in P.iterdir() if p.suffix in ['.step','.txt','.csv','.json','.srt'] and p.name not in ['parts.json','chapters.json']]
files += list((P/'Separate assemblies').iterdir())+list((P/'Magnetic assessment').iterdir())
files += [P/'preview-00.png',P/'Viewport sightline checked.png',P/'Encoded main video contact sheet.jpg']
with zipfile.ZipFile(P/'Complete sputter system R04 - CAD and design package.zip','w',zipfile.ZIP_DEFLATED) as z:
 for p in files:z.write(p,p.relative_to(P))
print(json.dumps({'video_duration_seconds':vr['duration_seconds'],'chapters':len(vr['chapters']),'video_bytes':video.stat().st_size,'CAD_package_bytes':(P/'Complete sputter system R04 - CAD and design package.zip').stat().st_size,'full_decode':'passed'}),flush=True)
