"""Render the exact R06 STEP with revision-stamped explanatory movies.

Requires CadQuery, VTK, NumPy, Pillow, imageio-ffmpeg. Narration uses Windows
System.Speech (Microsoft David). STEP remains authoritative; mesh is a view.
Run from any directory. No application automation or external media required.
"""
from pathlib import Path
import json, hashlib, subprocess, math, sys, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import vtk, imageio_ffmpeg
from vtk.util.numpy_support import numpy_to_vtk, numpy_to_vtkIdTypeArray, vtk_to_numpy

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'system-architecture-and-cad/models'
OUT=ROOT/'media'; WORK=ROOT/'tools/.work'; OUT.mkdir(exist_ok=True); WORK.mkdir(parents=True,exist_ok=True)
W,H,VW,VH,FPS=1600,900,1050,710,8

CHAPTERS=[
 {'id':'system','title':'Complete system R06','view':'system','bullets':['R06 gun in R04 system layout','200 x 200 x 300 mm interior','339 component instances','Purchased equipment: reference envelopes'], 'speech':'This is the current R zero six sputter system context, prepared on November twenty fourth, twenty twenty six. The latest gun has the three point one seven five millimetre aluminium target, revised clamp, and M five coolant fittings. The chamber and external layout come from R zero four. The assembly contains three hundred and thirty nine component instances. Equipment cabinets and several purchased parts are representative envelopes. The visible R V three backing pump is an old reference, while the selected purchase is the Indovac H V two, one fifty. Vendor replacement geometry remains pending.'},
 {'id':'chamber','title':'Chamber, stage and shutter','view':'chamber','bullets':['12 L gross internal volume','D90 stage; 50 x 50 mm substrate','Target gap: 75-150 mm; default 100','Window centre Z105; clear D70'], 'speech':'The chamber has a two hundred by two hundred by three hundred millimetre clear interior, giving twelve litres gross volume. The current view hides the shell and door to expose the latest gun, ninety millimetre substrate stage, and shutter. The reference substrate is fifty by fifty by one millimetre. Target to substrate adjustment is seventy five to one hundred and fifty millimetres, with one hundred as the default. The shutter underside is twelve millimetres above the reference substrate. The seventy millimetre window centre is at height one hundred and five. Ray checks establish partial geometric access at sampled observer positions; they do not predict visible glow. Chamber and window strength and final supplier sealing details are still to qualify.'},
 {'id':'utilities','title':'Pumping, gas and procurement','view':'system','bullets':['Chamber > EXT70 > HV2-150','One installed turbo; one spare','Owner-selected 200 sccm MFC','RF source selection: 200 W'], 'speech':'The selected pumping route is chamber, Edwards E X T seventy, then one Indovac rotary vane backing pump. No separate roughing bypass is selected. The procurement bundle contains two turbo pumps with E X D C eighty drivers, with one pump installed and one spare. The selected turbo supply is the Owon S P M eighty two zero five; voltage and current limits must follow the actual driver. The owner selected a two hundred S C C M mass flow controller. Exact model and argon calibration need confirmation. The earlier Horiba housing remains a dimensional reference. Approximately forty two millitorr is only an illustrative flow and pumping speed case, not a guaranteed ignition pressure. The selected R F supply is two hundred watts. The three hundred watt cooling calculation is a retained planning basis, not an operating power rating.'},
 {'id':'gun','title':'Latest 141-component gun','view':'gun','bullets':['R06 gun; native SolidWorks + STEP','Al target D50.8 x 3.175 mm','R05 clamp and M3 x 10 screws','Nominal grounded-shield gap: 1 mm'], 'speech':'The gun shown here is the latest R zero six geometry. Its one hundred and forty one component instances are available as a native SolidWorks assembly and as neutral STEP. The target is a two inch diameter aluminium disc, three point one seven five millimetres thick. R zero five revised the clamp contact shoulder and aperture, and changed the twelve clamp screws to M three by ten. The target back remains seated on the same cooler datum. The complete gun was raised one point one seven five millimetres in the chamber so the target front and the default one hundred millimetre substrate gap remain fixed. A nominal one millimetre gap separates the live clamp from the grounded shield. Screw preload, thermal contact, tolerances, and electrical qualification remain engineering work.'},
 {'id':'magnetron','title':'Twelve-stack magnetic head','view':'magnetron','bullets':['Centre: 2 x D20 x 10, N42','Outer: 12 x (2 x D6 x 10), N42','Outer pitch circle: D58 mm','Pole-area proxy 1.08; balance unproved'], 'speech':'This isolated head uses the current R zero six parts, with copper surfaces made translucent to reveal the magnetic circuit. The centre has two twenty by ten millimetre N forty two discs. Twelve outer stacks each have two six by ten millimetre discs on a fifty eight millimetre pitch circle. The centre north pole and outer south poles face the target. The steel return yoke, copper cooling body, and backplate are retained. The area ratio of one point zero eight is only a geometric proxy. It does not certify balanced magnetic topology. Historical component names may mention older magnet sizes, so the geometry, selection notes, and current field assessment take precedence.'},
 {'id':'cooling','title':'R06 coolant fittings and backplate','view':'cooling','bullets':['2 x SMC KQG2S04-M5','D3 passage; D4.2 tap drill x 5','M5 x 0.8; useful thread >= 4 mm','Gasket sealing and water/vacuum test pending'], 'speech':'R zero six selects two S M C K Q G two S zero four, M five fittings for four millimetre outside diameter tubing. The backplate now has three millimetre flow passages and four point two millimetre tap drills, five millimetres deep. The specified M five by zero point eight threads need at least four millimetres of useful thread. The native backplate contains real cut features. Thread callouts represent machining intent; helical teeth are not modeled. Nine millimetre fitting bodies pass through fourteen millimetre yoke holes, giving two point five millimetres nominal radial clearance. Use the specified manufacturer gasket and installation procedure. Nominal interference checks do not establish leak tightness. Coolant in vacuum suitability, pressure testing, hose bend limits, electrical isolation, and thermal performance remain to qualify.'},
 {'id':'field','title':'Current target-plane field assessment','view':'field','bullets':['Current target thickness: 3.175 mm','Mean parallel field: 86.43 mT','Contour radius mean: 20.19 mm','Saved FEM field resampled; no new solve'], 'speech':'The original nonlinear magnetostatic model used a two millimetre nonmagnetic target and gave ninety five point one millitesla mean parallel field near its surface. That is an earlier target revision. This updated assessment samples the saved fine mesh solution a quarter millimetre above the current three point one seven five millimetre target. The calculated mean parallel field is eighty six point four three millitesla. The range is eighty two point nine six to eighty nine point five three, with a mean normal field zero contour radius of twenty point one nine millimetres. The changed target, copper and fittings have unit relative permeability in this model, and the magnets and yoke are unchanged. This supports resampling the existing solution. It is not a new mesh or nonlinear solve, and it does not establish new uncertainty bounds or experimental validation.'},
 {'id':'limits','title':'Evidence and remaining engineering','view':'gun','bullets':['Valid gun geometry and export checks','FEM mesh/domain/analytical checks retained','No thermal, plasma or vessel FEA claimed','Manufacturing + commissioning gates documented'], 'speech':'The repository includes the design decisions, current procurement workbook, individual CAD parts, geometry checks, source scripts, magnetic meshes, field arrays, and numerical verification results. The latest native gun export has one hundred and forty one valid solids. A known invalid legacy R V three supplier solid remains in the complete context and is identified in the documentation. There is no completed thermal, plasma, structural vessel, or deposition simulation in the supplied evidence. Before fabrication and operation, complete the qualified drawings, sealing design, pressure and leak tests, thermal and flow measurements, electrical and R F ratings, interlocks, and controlled commissioning. This repository documents the current engineering study and the evidence still needed to release a machine.'}
]

def font(n,bold=False):
    p=Path('C:/Windows/Fonts')/('segoeuib.ttf' if bold else 'segoeui.ttf')
    if not p.exists(): p=Path('/usr/share/fonts/truetype/dejavu')/('DejaVuSans-Bold.ttf' if bold else 'DejaVuSans.ttf')
    return ImageFont.truetype(str(p),n)

def prepare_mesh():
    cache=OUT/'r06-view-mesh.npz'; meta=json.loads((SRC/'R06 component register.json').read_text())
    if cache.exists(): return meta,np.load(cache)
    import cadquery as cq
    print('Reading exact R06 system STEP',flush=True)
    solids=cq.importers.importStep(str(SRC/'Complete sputter system R06.step')).val().Solids()
    assert sum(q['solid_count'] for q in meta)==len(solids)
    arrays={};k=0;valid=[]
    for i,q in enumerate(meta):
        count=q['solid_count'];group=solids[k:k+count];k+=count
        triangles=[]
        for s in group:
            valid.append(s.isValid());v,f=s.tessellate(.18,.22)
            triangles.append(np.array([x.toTuple() for x in v],dtype=np.float32)[np.array(f)])
        arrays[f'p{i}']=np.concatenate(triangles)
        if i%50==0:print('Meshed',i,'of',len(meta),flush=True)
    np.savez_compressed(cache,**arrays)
    (OUT/'r06-geometry-read.json').write_text(json.dumps({'component_instances':len(meta),'solid_count':len(solids),'invalid_solid_count':valid.count(False),'expected_invalid_reference':'Legacy RV3 supplier reference; see R06 scope notes.'},indent=2))
    return meta,arrays

def wrap(draw,text,x,y,width,ft,color):
    line=''
    for word in text.split():
        candidate=(line+' '+word).strip()
        if draw.textlength(candidate,font=ft)>width and line:
            draw.text((x,y),line,font=ft,fill=color);y+=ft.size+9;line=word
        else:line=candidate
    if line:draw.text((x,y),line,font=ft,fill=color);y+=ft.size+9
    return y

def main():
    (OUT/'chapters.json').write_text(json.dumps(CHAPTERS,indent=2))
    # Narrate all chapters in one native process. These intermediate WAVs stay local.
    ps=WORK/'narrate.ps1'
    ps.write_text("param([string]$ChapterFile,[string]$WorkDir)\nAdd-Type -AssemblyName System.Speech\n$s=New-Object System.Speech.Synthesis.SpeechSynthesizer\n$s.SelectVoice('Microsoft David Desktop');$s.Rate=0\n$chs=Get-Content -LiteralPath $ChapterFile -Raw | ConvertFrom-Json\nforeach($c in $chs){$s.SetOutputToWaveFile((Join-Path $WorkDir ($c.id+'.wav')));$s.Speak($c.speech);$s.SetOutputToNull()}\n$s.Dispose()",encoding='utf-8')
    if not all((WORK/(c['id']+'.wav')).exists() for c in CHAPTERS):
        subprocess.run(['powershell','-NoProfile','-ExecutionPolicy','Bypass','-File',str(ps),str(OUT/'chapters.json'),str(WORK)],check=True)
    meta,arrays=prepare_mesh()
    window=vtk.vtkRenderWindow();window.SetOffScreenRendering(1);window.SetSize(VW,VH);window.SetMultiSamples(0)
    ren=vtk.vtkRenderer();ren.SetBackground(.04,.07,.11);ren.SetBackground2(.13,.19,.24);ren.GradientBackgroundOn();window.AddRenderer(ren)
    actors=[]
    for i,q in enumerate(meta):
        a=arrays[f'p{i}'];pd=vtk.vtkPolyData();points=vtk.vtkPoints();points.SetData(numpy_to_vtk(a.reshape(-1,3),deep=True));pd.SetPoints(points)
        cells=vtk.vtkCellArray();cells.SetData(numpy_to_vtkIdTypeArray(np.arange(0,len(a)*3+1,3,dtype=np.int64),deep=True),numpy_to_vtkIdTypeArray(np.arange(len(a)*3,dtype=np.int64),deep=True));pd.SetPolys(cells)
        clean=vtk.vtkCleanPolyData();clean.SetInputData(pd);norm=vtk.vtkPolyDataNormals();norm.SetInputConnection(clean.GetOutputPort());norm.SetFeatureAngle(40);norm.Update()
        mapper=vtk.vtkPolyDataMapper();mapper.SetInputConnection(norm.GetOutputPort());ac=vtk.vtkActor();ac.SetMapper(mapper);ac.GetProperty().SetColor(*q['color']);ac.GetProperty().SetAmbient(.3);ac.GetProperty().SetDiffuse(.7);ac.GetProperty().SetSpecular(.25);ren.AddActor(ac);actors.append(ac)
    cap=vtk.vtkWindowToImageFilter();cap.SetInput(window);cap.SetInputBufferTypeToRGB();cap.ReadFrontBufferOff()
    camera=ren.GetActiveCamera();camera.ParallelProjectionOn();camera.SetViewUp(0,0,1)
    ffmpeg=imageio_ffmpeg.get_ffmpeg_exe();durations={}
    for ch in CHAPTERS:
        view=ch['view'];print('Rendering',ch['id'],flush=True)
        for q,a in zip(meta,actors):
            role=q['role'];show=True;opacity=1
            if view=='chamber':show=q['group'] in ['gun','fitting','shutter'] or role in ['stage','substrate','stage_support','pump_baffle','baffle_support'] or q['name']=='Floor plate'
            if view in ['gun','magnetron','cooling','field']:show=q['group']=='gun'
            if view=='magnetron':
                show=role in ['gun_outermag','gun_centermag','gun_cooler','gun_closure','gun_yoke','gun_target','gun_clamp','gun_fittings']
                if role in ['gun_cooler','gun_closure','gun_target','gun_clamp']:opacity=.13
            if view=='cooling':show=role in ['gun_closure','gun_yoke','gun_fittings','gun_hoses','gun_waterseal','gun_yokebolt','gun_cooler'];opacity=.22 if role=='gun_yoke' else 1
            if role=='glass':opacity=.35
            a.SetVisibility(show);a.GetProperty().SetOpacity(opacity)
        if view=='system':focus=(80,50,40);distance=1500;scale=690;elev=34
        elif view=='chamber':focus=(0,0,145);distance=500;scale=200;elev=8
        elif view=='cooling':focus=(0,0,164);distance=250;scale=65;elev=60
        elif view=='magnetron':focus=(0,0,155);distance=250;scale=64;elev=35
        else:focus=(0,0,291);distance=500;scale=190;elev=-12
        camera.SetFocalPoint(*focus);camera.SetParallelScale(scale)
        with wave.open(str(WORK/(ch['id']+'.wav')),'rb') as wav:duration=wav.getnframes()/wav.getframerate()+1.2
        durations[ch['id']]=duration
        if view=='field':
            # Scientific plots are derived from current plane, not old geometry screenshots.
            plot=Image.open(ROOT/'simulations/current-target-r06/current-target-map.png').convert('RGB');plot.thumbnail((VW,VH))
        def frame(u):
            im=Image.new('RGB',(W,H),'#0c1521');d=ImageDraw.Draw(im)
            d.text((35,22),'SPUTTER / CURRENT DESIGN REVIEW',font=font(19,True),fill='#6bd6c7')
            d.text((35,55),ch['title'],font=font(33,True),fill='#edf3f7')
            if view=='field':im.paste(plot,((VW-plot.width)//2+20,140))
            else:
                az=math.radians(-65+32*u);el=math.radians(elev)
                camera.SetPosition(focus[0]+distance*math.cos(az)*math.cos(el),focus[1]+distance*math.sin(az)*math.cos(el),focus[2]+distance*math.sin(el))
                ren.ResetCameraClippingRange();window.Render();cap.Modified();cap.Update()
                a=vtk_to_numpy(cap.GetOutput().GetPointData().GetScalars()).reshape(VH,VW,3)
                im.paste(Image.fromarray(np.flipud(a)),(20,130))
            d=ImageDraw.Draw(im);y=150
            d.text((1100,y),'REVISION BASIS',font=font(20,True),fill='#6bd6c7');y+=45
            for bullet in ch['bullets']:
                y=wrap(d,bullet,1100,y,455,font(25), '#edf3f7')+24
            y=max(y,590)
            y=wrap(d,'Nominal engineering study. Qualification and manufacturing release remain open.',1100,y,450,font(21),'#edbf83')
            if view=='system':wrap(d,'RV3 / MFC / cabinets: reference geometry. Selected backing pump and exact MFC are not modeled.',1100,y+20,450,font(18),'#afbdca')
            d.text((35,858),'R06 gun + R05 target/clamp | 24 November 2026 | CAD-derived views',font=font(20),fill='#a7b9ca')
            return np.asarray(im)
        frame(.5);Image.fromarray(frame(.5)).save(OUT/(ch['id']+'.png'))
        silent=WORK/(ch['id']+'-silent.mp4')
        proc=subprocess.Popen([ffmpeg,'-y','-loglevel','error','-f','rawvideo','-vcodec','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-c:v','libx264','-preset','fast','-crf','22','-pix_fmt','yuv420p',str(silent)],stdin=subprocess.PIPE)
        for i in range(math.ceil(duration*FPS)):proc.stdin.write(frame(i/(duration*FPS)).tobytes())
        proc.stdin.close()
        if proc.wait()!=0:raise RuntimeError('Video encode failed')
        sub=OUT/(ch['id']+'.srt');text=ch['speech'].split('. ');t=0;lines=[]
        def stamp(s):
            ms=int(s*1000);return f'{ms//3600000:02d}:{ms//60000%60:02d}:{ms//1000%60:02d},{ms%1000:03d}'
        for j,s in enumerate(text):
            end=t+(duration-1.2)*len(s)/sum(map(len,text));lines.extend([str(j+1),stamp(t)+' --> '+stamp(end),s,'']);t=end
        sub.write_text('\n'.join(lines),encoding='utf-8')
        subprocess.run([ffmpeg,'-y','-loglevel','error','-i',str(silent),'-i',str(WORK/(ch['id']+'.wav')),'-i',str(sub),'-map','0:v','-map','1:a','-map','2:s','-c:v','copy','-c:a','aac','-b:a','128k','-c:s','mov_text','-metadata:s:s:0','language=eng','-t',str(duration),'-movflags','+faststart',str(OUT/(ch['id']+'.mp4'))],check=True)
    for name,ids in {'01-current-system':['system','chamber','utilities'],'02-current-gun':['gun','magnetron','cooling'],'03-current-field-and-evidence':['field','limits']}.items():
        listing=WORK/(name+'.txt');listing.write_text('\n'.join("file '"+(OUT/(x+'.mp4')).as_posix()+"'" for x in ids))
        subprocess.run([ffmpeg,'-y','-loglevel','error','-f','concat','-safe','0','-i',str(listing),'-map','0','-c','copy','-movflags','+faststart',str(OUT/(name+'.mp4'))],check=True)
        (OUT/(name+'-transcript.txt')).write_text('\n\n'.join(CHAPTERS[[c['id'] for c in CHAPTERS].index(x)]['title']+'\n'+CHAPTERS[[c['id'] for c in CHAPTERS].index(x)]['speech'] for x in ids),encoding='utf-8')
    manifest={'date':'2026-11-24','source_step':'system-architecture-and-cad/models/Complete sputter system R06.step','source_sha256':hashlib.sha256((SRC/'Complete sputter system R06.step').read_bytes()).hexdigest(),'field_report':'simulations/current-target-r06/assessment.json','narration':'Windows Microsoft David Desktop, synthetic narration','chapter_durations_seconds':durations,'notes':'All geometry views generated from latest R06 system STEP. Transparency / hidden context are explanatory. No old MP4 segments reused.'}
    (OUT/'provenance.json').write_text(json.dumps(manifest,indent=2));window.Finalize();print('Current media complete',flush=True)

if __name__=='__main__':main()
