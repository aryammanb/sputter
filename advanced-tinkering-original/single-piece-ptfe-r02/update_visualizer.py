from pathlib import Path
import re
P=Path(__file__).resolve().parent
V=Path('C:/Users/Aryamman/.codex/visualizations/2026/11/19/01a1f594-d837-7b70-8c70-7c7ffe09a027')
s=(V/'single-piece-ptfe-cup.html').read_text(encoding='utf-8')
s=s.replace('ptfe-cup-view','ptfe-lip-view')
s=re.sub(r'(<script type="application/json" id="ptfe-mesh-data">).*?(</script>)',lambda m:m[1]+(V/'single-ptfe-outward-lip-geometry.json').read_text(encoding='utf-8')+m[2],s,flags=re.S)
s=s.replace('id="ptfe-context">','id="ptfe-context" checked>')
s=s.replace('section=true,showContext=false','section=true,showContext=true')
s=s.replace('and screw-head guard wall.','screw-head guard wall, and integral outward lip over the surrounding grounded face.')
s=s.replace('<span>3 · Guard wall</span>','<span>3 · Guard wall</span><span>4 · Outward lip</span>')
s=s.replace('One solid · retained by the metal screw · open tool-access end','One solid · integral outward lip · retained by the metal screw')
s=s.replace('Concept dimensions: Ø11.6 mm cup · Ø3.3 mm screw bore · 32 mm overall. Preload and RF clearances unverified.','Concept: Ø17.6 mm lip · 3 mm outward projection · 2 mm gap above ground face. Preload and RF clearances unverified.')
s=s.replace("part:'One-piece screw-captured PTFE sleeve, shoulder and guard cup',section,showContext","part:'One-piece PTFE with integral outward lip',revision:'outward-lip-r02',section,showContext")
s=s.replace("function load(s){if(!s)return;const a=s.modelContent||{},b=s.privateContent||{};","function load(s){if(!s||s.modelContent?.revision!=='outward-lip-r02')return;const a=s.modelContent||{},b=s.privateContent||{};")
s=s.replace('The metal head clamps the integral shoulder against Boden; the whole PTFE part is captured.','The screw captures the shoulder; the outer lip emerges past the hole and overlaps the grounded face.')
s=s.replace("[[0,-12,5.2],'3']]","[[0,-12,5.2],'3'],[[0,-15,8.2],'4']]")
assert "'4']" in s and 'outward-lip-r02' in s
(V/'single-piece-ptfe-outward-lip.html').write_text(s,encoding='utf-8')
test=(P/'check_visualizer.mjs').read_text(encoding='utf-8').replace('/single-piece-ptfe/','/single-piece-ptfe-r02/').replace('ptfe-cup-view','ptfe-lip-view')
(P/'check_visualizer.mjs').write_text(test,encoding='utf-8')
print('Updated visualizer',len(s.encode('utf-8')),'bytes')
