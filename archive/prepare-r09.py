from pathlib import Path
import shutil

root=Path(__file__).resolve().parent
out=root/'magnetron-cad-r09'
if (out/'R09 308 Integral copper target seat and channel.SLDPRT').exists():
    raise SystemExit('R09 now uses the integral 308 seat/channel. This legacy R08-to-R09 preparation must not overwrite the reviewed revision.')
out.mkdir(exist_ok=True)
changed={'101','203','204','304','308','401','501','502','601'}
for p in (root/'magnetron-cad-r08').glob('R08 *.SLDPRT'):
    if p.name.split()[1] not in changed:
        shutil.copy2(p,out/p.name.replace('R08 ','R09 ',1))
s=(root/'build-magnetron-r08.ps1').read_text().replace('r08','r09').replace('R08','R09')
s=s.replace('Pattern(4,45,1.55,Math.PI/4)','Pattern(4,45,1.25,Math.PI/4)')
s=s.replace('Tube(168.7,174.7,25.4,0)', 'Tube(168.7,171.875,25.4,0)')
s=s.replace('{135.7,9.5},{143.7,9.5}', '{135.7,4.2},{143.7,4.2}')
s=s.replace('}},keeperBolts);','}},Pattern(3,32.5,1.25,Math.PI/3));')
s=s.replace('doc=>Holes(doc,ceramicBolts,148.7,154.7)','doc=>Holes(doc,Pattern(3,12,1.25,Math.PI/2),148.7,154.7)')
s=s.replace('Tube(163.7,168.7,34.4,0),headBolts, doc=>Holes(doc,clampBolts,165.2,168.7)', 'Tube(163.7,168.7,34.4,0),Combine(Pattern(3,29.4,1.25,Math.PI/2),Pattern(3,29.4,1.25,-Math.PI/2))')
s=s.replace('shieldBolts,doc=>Holes(doc,Pattern(3,42.2,2.85),135.7,139.7)', 'shieldBolts')
s=s.replace('Combine(shieldBolts,keeperBolts)', 'Combine(Pattern(3,42.2,1.25),keeperBolts)')
s=s.replace('Pattern(4,52,1.55)', 'Pattern(4,52,1.25)')
s=s.replace('doc.ViewZoomtofit2();\n   Save(doc,path);', '''var props=doc.Extension.CustomPropertyManager[""];
   props.Add3("Release status",30,"DESIGN REVIEW ONLY - not released for manufacture",2);
   if(name.StartsWith("101")||name.StartsWith("204")||name.StartsWith("304")||name.StartsWith("308")||name.StartsWith("502")||name.StartsWith("601"))
    props.Add3("Thread intent",30,"M3 x 0.5 tapped holes represented by 2.5 mm pilot bores; screw overlaps are thread envelopes. See R09 review for locations and engagement. No modeled helical thread.",2);
   doc.ViewZoomtofit2();
   Save(doc,path);''')
(root/'build-magnetron-r09.ps1').write_text(s)
