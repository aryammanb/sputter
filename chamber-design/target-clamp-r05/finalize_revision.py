from pathlib import Path
import json,csv,zipfile,shutil
P=Path('chamber-design/target-clamp-r05');m=json.loads((P/'parts.json').read_text());
with (P/'R05 component change register.csv').open('w',newline='',encoding='utf-8-sig') as f:
 w=csv.writer(f);w.writerow(['Component','Role','R05 change'])
 for q in m:
  change='Unchanged'
  if q['role']=='gun_clamp':change='Central pressure lip redesigned for3.175mm target; outer/screw interface retained.'
  elif q['role']=='gun_target':change='Al99.99% D50.8x3.175, VritraTech source.'
  elif q['role']=='gun_targetbolts':change='M3x10 replaces M3x8, same head seat.'
  elif q['group']=='gun':change='Shape unchanged; assembly pose raised1.175mm to retain100mm target gap.'
  elif q['role']=='gun_water' or q['name']=='Power cable to gun coax':change='External flexible extension follows raised gun endpoint.'
  w.writerow([q['name'],q['role'],change])
# Add the viewport evidence to the review notes.
p=P/'READ FIRST - Clamp R05.txt';s=p.read_text(encoding='utf-8');s+='\nVIEWPORT RECHECK\nAt observer(0,-400,20), with the existingD70 window centredZ105, the\nR20 observation ring5mm below target has43/72 clear rays at gap75,55/72\nat gap100 and31/72 at gap150. Geometric access only, no brightness prediction.\n';p.write_text(s,encoding='utf-8')
