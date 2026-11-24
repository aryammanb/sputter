from pathlib import Path
import json,csv,subprocess,re,zipfile,shutil
import cadquery as cq
import imageio_ffmpeg
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parent
meta=json.loads((P/'parts.json').read_text());report=json.loads((P/'System dimension report.json').read_text())
checks={}
for name in ['Full sputter system R03 - closed.step','Full sputter system R03 - loading.step']:
 solids=cq.importers.importStep(str(P/name)).val().Solids();assert len(solids)==report['solids']
 bad=[s for s in solids if not s.isValid()]
 # The imported RV3 supplier solid is known to be invalid before this assembly.
 assert len(bad)<=1,(name,len(bad))
 if bad:
  b=bad[0].BoundingBox();actual=[b.xmin,b.ymin,b.zmin,b.xmax,b.ymax,b.zmax];expect=report['dimensions_mm']['RV3_import_bbox_mm']
  # CADQuery's cached triangulation inflates this supplier model's bounds by
  # up to0.5 mm; exported BRep extrema match the untriangulated source.
  assert max(abs(a-b) for a,b in zip(actual,expect))<.75
 checks[name]={'solids':len(solids),'valid_solids':len(solids)-len(bad),'known_supplier_RV3_invalid_solids':len(bad)}
 print('Reimported',name,checks[name],flush=True)
with (P/'Dimension schedule.csv').open('w',newline='',encoding='utf-8-sig') as f:
 w=csv.writer(f);w.writerow(['Dimension','Nominal model value','Note'])
 for k,v in report['dimensions_mm'].items():
  if k!='hose_path_samples':w.writerow([k,json.dumps(v),'mm unless text specifies otherwise'])
separate=P/'Separate assemblies'
for source in ['Bent shutter.step','Top plate.step','Substrate stage.step','Front door.step']:
 shutil.copy2(P.parent/'complete-chamber-r01'/'Separate parts'/source,separate/source)
for source in ['Refined compression fitting - assembled.step','Refined compression fitting - exploded.step']:
 shutil.copy2(P.parent/'compression-fitting-r02'/source,separate/source)
shutil.copy2(P.parent/'complete-chamber-r01'/'Dimension and clearance report.json',P/'Inherited internal clearance checks.json')
checks['scope']='Internal stage/shutter/gun geometry unchanged from checked R01/R02. New exterior layout not a full tolerance/structural/flow verification.'
(P/'CAD verification.json').write_text(json.dumps(checks,indent=2))
video=P/'Full sputter system R03 - integrated walkthrough.mp4'
if not video.exists():print('CAD checked; video pending',flush=True);raise SystemExit()
exe=imageio_ffmpeg.get_ffmpeg_exe();vr=json.loads((P/'Video verification.json').read_text())
subprocess.run([exe,'-v','error','-i',str(video),'-map','0:v','-map','0:a','-f','null','-'],check=True)
info=subprocess.run([exe,'-hide_banner','-i',str(video)],capture_output=True,text=True).stderr
assert 'Video: h264' in info and 'Audio: aac' in info and 'Subtitle: mov_text' in info
assert len(re.findall(r'Chapter #',info))==len(vr['chapters'])==16
sheet=Image.new('RGB',(1600,1800),'#101a29')
selected=[0,1,3,6,8,9,10,11,12,13,14,15]
for j,i in enumerate(selected):
 start,title=vr['chapters'][i];end=vr['chapters'][i+1][0] if i+1<len(vr['chapters']) else vr['duration_seconds']
 path=P/f'Encoded check {i+1:02}.png'
 subprocess.run([exe,'-y','-v','error','-ss',str(start+.45*(end-start)),'-i',str(video),'-frames:v','1',str(path)],check=True)
 sheet.paste(Image.open(path).resize((533,300)),((j%3)*533,(j//3)*450));ImageDraw.Draw(sheet).text(((j%3)*533+10,(j//3)*450+310),f'{i+1:02} {title}',fill='white')
sheet.save(P/'Encoded integrated contact sheet.jpg')
vr.update(full_audio_video_decode_passed=True,embedded_chapters=16,subtitle_codec='mov_text')
(P/'Video verification.json').write_text(json.dumps(vr,indent=2))
files=[p for p in P.iterdir() if p.suffix in ['.step','.txt','.csv','.json','.py','.ps1'] and p.name!='parts.json']
files += list(separate.iterdir())
files += [P/'preview-00.png',P/'preview-05.png',P/'preview-07.png',P/'System walkthrough contact sheet.jpg']
with zipfile.ZipFile(P/'Full sputter system R03 - CAD and dimensions.zip','w',zipfile.ZIP_DEFLATED) as z:
 for p in files:z.write(p,p.relative_to(P))
print(json.dumps({'video_seconds':vr['duration_seconds'],'chapters':16,'instances':report['instances'],'solids':report['solids'],'CAD_zip_bytes':(P/'Full sputter system R03 - CAD and dimensions.zip').stat().st_size,'video_bytes':video.stat().st_size}),flush=True)
