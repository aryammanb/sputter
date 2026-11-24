from pathlib import Path
import json,csv,zipfile
P=Path('chamber-design/main-system-r04');m=json.loads((P/'parts.json').read_text())
with (P/'System parts list.csv').open('w',newline='',encoding='utf-8-sig') as f:
 w=csv.writer(f);w.writerow(['Name','Role','Group','Scope / reference','Valid']);w.writerows([q['name'],q['role'],q['group'],q['note'],q['valid']] for q in m)
with (P/'README.txt').open('a',encoding='utf-8') as f:f.write('\nWINDOW RETAINER DETAIL\nSix nominalM5 retainer pilot bores areD4.2 x10deep from the outer door face,\nleaving6mm solid backing to the vacuum side. All six backing regions were\nchecked solid. Threads and actual screw engagement remain to detail.\n')
with (P/'Dimension schedule.csv').open('a',newline='',encoding='utf-8-sig') as f:csv.writer(f).writerow(['Viewport retainer bores',[4.2,10,6],'diameter, blind depth, remaining solid backing; mm'])
with (P/'Purchased component references.csv').open('a',newline='',encoding='utf-8-sig') as f:csv.writer(f).writerow(['Turbo cooler hose','Approximately6mm ID reinforced hose','https://www.idealvac.com/files/manualsII/Edwards_EXT_70_250_Turbo_Pump_Manual.pdf','Modeled OD9/ID6; selected reinforced hose and clips pending'])
checks=json.loads((P/'CAD verification.json').read_text());checks['door_retainer_bores']=json.loads((P/'Door retainer bore check.json').read_text());checks['viewport_travel_check']='Viewport travel range check.json';(P/'CAD verification.json').write_text(json.dumps(checks,indent=2))
files=[p for p in P.iterdir() if p.suffix in ['.step','.txt','.csv','.json','.srt'] and p.name not in ['parts.json','chapters.json']]
files+=list((P/'Separate assemblies').iterdir())+list((P/'Magnetic assessment').iterdir())
files += [P/'preview-00.png',P/'Viewport sightline checked.png',P/'Deposition stage detail.png',P/'Encoded main video contact sheet.jpg']
pack=P/'Complete sputter system R04 - CAD and design package.zip'
with zipfile.ZipFile(pack,'w',zipfile.ZIP_DEFLATED) as z:
 for p in files:z.write(p,p.relative_to(P))
with zipfile.ZipFile(pack) as z:assert z.testzip() is None;print('Final package:',len(z.namelist()),'files;',pack.stat().st_size,'bytes; CRC check passed')
print('Final video:',(P/'Complete sputter system R04 - main walkthrough.mp4').stat().st_size,'bytes')
