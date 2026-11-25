from pathlib import Path
P=Path('cad/main-system-r04')
p=P/'build_system.py';s=p.read_text().replace('seg,4,2.5,\'turbo_water\'','seg,4.5,3,\'turbo_water\'').replace('Representative OD8/ID5 loop','Nominal OD9/ID6 reinforced-hose reference loop').replace('cyl(2.25,20,(52*','cyl(2.1,20,(52*');p.write_text(s)
p=P/'make_renderer.py';s=p.read_text().replace("direction=np.array([1.,-.6,-.5])","direction=np.array([-1.,-.6,.45])")
s=s.replace("(P/'render_main.py').write_text(s)",'''s=s.replace("win.Render();capture.Modified()", "if view=='viewport':cam.ParallelProjectionOff();cam.SetPosition(0,-400,20);cam.SetFocalPoint(0,0,136);cam.SetViewAngle(35);r.ResetCameraClippingRange()\\n win.Render();capture.Modified()")
s=s.replace("im=Image.new('RGB',(W,H)","if ch['title']=='Magnetic circuit and calculated field' and u>.35:\\n  field=Image.open(P.parent.parent/'advanced-tinkering-original'/'balanced-twelve-stack-study'/'magnetic-simulation'/'Target field map.png').convert('RGB');field.thumbnail((VW,VH));bg=Image.new('RGB',(VW,VH),'#101a29');bg.paste(field,((VW-field.width)//2,(VH-field.height)//2));arr=np.flipud(np.array(bg))\\n im=Image.new('RGB',(W,H)")
(P/'render_main.py').write_text(s)''')
p.write_text(s)
