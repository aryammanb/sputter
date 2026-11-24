from pathlib import Path
import json,csv
P=Path('chamber-design/main-system-r04');r=json.loads((P/'Viewport travel range check.json').read_text())
with (P/'Viewport sampled visibility.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(r['results'][0]));w.writeheader();w.writerows(r['results'])
with (P/'README.txt').open('a',encoding='utf-8') as f:f.write('\nADDITIONAL VIEWPORT TRAVEL CHECK\nAt the same eye(0,-400,20), the revised aperture admits unobstructed rays to\n37/72 samples at gap75,47/72 at gap100 and31/72 at gap150. These are partial\nring views, not percentages of plasma visibility. Lower viewing angles can\nexpose more of the ring at larger gaps. See Viewport travel range check.json\nand Viewport sampled visibility.csv. No equal-view guarantee is inferred.\n')
print('Travel-range viewport evidence saved')
