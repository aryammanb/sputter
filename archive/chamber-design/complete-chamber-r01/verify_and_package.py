from pathlib import Path
import json,csv,math,zipfile,subprocess,re,wave
import cadquery as cq
import numpy as np
import imageio_ffmpeg
import ezdxf
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parent
report=json.loads((P/'Dimension and clearance report.json').read_text())
d=report['dimensions_mm']
assert report['checks']['all_shapes_valid']
assert not report['checks']['shutter_sweep_interferences']
assert not report['checks']['gun_at_75_100_150_gap_interferences']
assert d['shutter_blade_bottom_z']-d['substrate_top_z']==12
assert d['stage_top_z']-34==d['stage_thickness']==6
reimport={}
for name in ['Complete chamber - door closed shutter closed.step','Complete chamber - door open shutter parked.step']:
 s=cq.importers.importStep(str(P/name)).val();solids=s.Solids()
 assert len(solids)==report['valid_solids']
 assert all(q.isValid() for q in solids)
 reimport[name]={'valid_solids':len(solids),'all_valid':True}
print('Both STEP assembly states reimported and all solids valid',flush=True)

# Verify source target plane and stage support contact from actual exported solids.
target=cq.importers.importStep(str(P.parents[2]/'advanced-tinkering-original'/'balanced-twelve-stack-study'/'Proposed twelve stack mechanical study.step')).val()
candidates=[]
for s in target.Solids():
 b=s.BoundingBox()
 if abs(s.Volume()-math.pi*25.4**2*2)<.1:
  faces=[f for f in s.Faces() if f.geomType()=='PLANE']
  candidates.append(max(f.Center().y for f in faces))
assert any(abs(y-2)<1e-6 for y in candidates),candidates
sh=cq.importers.importStep(str(P/'Separate parts'/'Bent shutter.step')).val()
assert sh.isValid() and len(sh.Solids())==1

# Regenerate flat DXF from actual upper planar face, then add bend-tangent marks.
flat=cq.importers.importStep(str(P/'Separate parts'/'Shutter developed blank - K0.42.step')).val()
top=max(flat.Faces(),key=lambda f:f.Center().z)
cq.exporters.export(cq.Workplane('XY').add(top).wires(),str(P/'Separate parts'/'Shutter blank reference.dxf'))
doc=ezdxf.readfile(str(P/'Separate parts'/'Shutter blank reference.dxf'))
doc.layers.new('BEND_TANGENTS',dxfattribs={'color':3})
for x in d['shutter_bend_tangent_stations']:doc.modelspace().add_line((x,-8),(x,8),dxfattribs={'layer':'BEND_TANGENTS'})
doc.saveas(P/'Separate parts'/'Shutter blank reference.dxf')
with (P/'Dimension schedule.csv').open('w',newline='',encoding='utf-8-sig') as f:
 w=csv.writer(f);w.writerow(['Dimension','Nominal value','Units / note'])
 for k,v in d.items():w.writerow([k,json.dumps(v),'mm unless name specifies litres/degrees'])

video=P/'Sputter chamber R01 - dimensioned walkthrough.mp4'
if not video.exists():
 (P/'CAD verification.json').write_text(json.dumps({'step_reimport':reimport,'source_target_face_y':candidates,'bent_shutter_single_valid_solid':True},indent=2))
 print('CAD verified; run again after video finishes to verify/package',flush=True)
 raise SystemExit()
exe=imageio_ffmpeg.get_ffmpeg_exe();vr=json.loads((P/'Video verification.json').read_text())
subprocess.run([exe,'-v','error','-i',str(video),'-map','0:v','-map','0:a','-f','null','-'],check=True)
info=subprocess.run([exe,'-hide_banner','-i',str(video)],capture_output=True,text=True).stderr
assert 'Video: h264' in info and 'Audio: aac' in info and 'Subtitle: mov_text' in info
assert len(re.findall(r'Chapter #',info))==9
levels=[]
for i in range(9):
 with wave.open(str(P/f'voice-{i:02}.wav'),'rb') as f:
  a=np.frombuffer(f.readframes(f.getnframes()),'<i2').astype(float)
  rms=float(np.sqrt(np.mean(a*a)));assert rms>100;levels.append(rms)
sheet=Image.new('RGB',(1600,1350),'#101a29')
for i,(start,title) in enumerate(vr['chapters']):
 end=vr['chapters'][i+1][0] if i<8 else vr['duration_seconds']
 t=start+(end-start)*(.85 if i==2 else .45)
 frame=P/f'Encoded check {i+1:02}.png'
 subprocess.run([exe,'-y','-v','error','-ss',str(t),'-i',str(video),'-frames:v','1',str(frame)],check=True)
 im=Image.open(frame).resize((533,300));sheet.paste(im,((i%3)*533,(i//3)*450))
 ImageDraw.Draw(sheet).text(((i%3)*533+10,(i//3)*450+308),f'{i+1:02}: {title}',fill='white')
sheet.save(P/'Encoded video contact sheet.jpg')
vr.update(full_audio_video_decode_passed=True,embedded_chapters=9,subtitle_codec='mov_text',narration_rms=levels)
(P/'Video verification.json').write_text(json.dumps(vr,indent=2))
(P/'CAD verification.json').write_text(json.dumps({'step_reimport':reimport,'source_target_face_y':candidates,'bent_shutter_single_valid_solid':True},indent=2))
files=[p for p in P.iterdir() if p.suffix.lower() in ['.step','.txt','.json','.csv','.py','.ps1'] and p.name not in ['parts.json','chapters.json']]
files+=list((P/'Separate parts').iterdir())
files += [P/'preview-01.png',P/'preview-06.png',P/'Walkthrough contact sheet.jpg']
with zipfile.ZipFile(P/'Sputter chamber R01 - CAD and dimensions.zip','w',zipfile.ZIP_DEFLATED) as z:
 for p in files:z.write(p,p.relative_to(P))
print(json.dumps({'video_seconds':vr['duration_seconds'],'video_bytes':video.stat().st_size,'cad_zip_bytes':(P/'Sputter chamber R01 - CAD and dimensions.zip').stat().st_size,'valid_solids_per_state':report['valid_solids'],'zero_shutter_and_gun_interferences':True}),flush=True)
