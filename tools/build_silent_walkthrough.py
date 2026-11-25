"""Silent, assembly-level R06 CAD tour. Uses the cached exact STEP tessellation.

Reproduce: python tools/build_silent_walkthrough.py
Preview:   python tools/build_silent_walkthrough.py --preview
No gun disassembly, voice, music, subtitles, or explanatory text overlays.
"""
from pathlib import Path
import sys, json, math, subprocess, hashlib, time
import numpy as np
import vtk
from vtk.util.numpy_support import numpy_to_vtk, numpy_to_vtkIdTypeArray, vtk_to_numpy
from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg
from build_current_media import prepare_mesh

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'media/system-walkthrough'
OUT.mkdir(parents=True,exist_ok=True)
W,H,FPS=1440,810,24
BG=(.055,.073,.095)
CHAMBER={'structure','service_port','gun_mount','turbo_flange','door_seal','hinge_fixed','hinge_pin','latch_catch','blank_cap'}
STAGE={'stage','stage_support','substrate'}
BAFFLE={'pump_baffle','baffle_support'}
TURBO={'turbo_body','turbo_core','turbo_fin','turbo_outlet','turbo_vent','turbo_connector','turbo_cooling'}
ISO={'iso_seal','iso_clamp','iso_screw'}
FORE={'backing_pump','hose','hose_ribs','hose_end','foreline_adapter'}
GAUGE={r for r in ['gauge_pirani','gauge_penning','gauge_stem','gauge_connector','gauge_band','gauge_elbow']}
MFC={'mfc_body','mfc_electronics','mfc_male_vcr','mfc_signal','mfc_bracket','mfc_mount_screw'}
VCR={'vcr_gasket','vcr_in_nut','vcr_npt_adapter','vcr_out_nut','mfc_out_adapter','push_body','push_collet','gas_insert'}
GAS={'gas_line','cylinder','regulator','regulator_dial'}
POWER={'power','power_display','matching','power_cable','earth'}

def scene(label,seconds,roles=None,groups=(),highlight=(),focus=None,scale=None,az=-65,el=20,move=None,opened=0,cut=False):
    return dict(label=label,seconds=seconds,roles=roles,groups=set(groups),highlight=set(highlight),focus=focus,scale=scale,az=az,el=el,move=move,opened=opened,cut=cut)

SCENES=[
 scene('Sputter system',7,az=-60,el=24),
 scene('Support frame',5,CHAMBER|{'frame','base_plate'},highlight={'frame','base_plate'},az=-55,el=15),
 scene('Vacuum chamber',6,CHAMBER,('door',),highlight={'structure'},focus=(0,0,145),scale=205,az=-55,el=22),
 scene('Loading door',8,CHAMBER|STAGE|BAFFLE,('door','gun','fitting','shutter'),highlight={'door_plate','door_handle','hinge_moving'},focus=(-70,-65,155),scale=255,az=-64,el=18,move='door'),
 scene('Viewport',5,CHAMBER,('door',),highlight={'glass','viewport_bezel'},focus=(0,-112,112),scale=105,az=-85,el=8),
 scene('Substrate stage',7,CHAMBER|STAGE|BAFFLE,highlight=STAGE,focus=(0,0,45),scale=115,az=-65,el=30,move='stage',cut=True),
 scene('Pump baffle',5,CHAMBER|BAFFLE,highlight=BAFFLE,focus=(0,0,30),scale=105,az=-65,el=28,move='baffle',cut=True),
 scene('Sputter gun',8,CHAMBER|STAGE,('gun','fitting'),highlight={'@gun','@fitting','gun_mount'},focus=(0,0,310),scale=315,az=-62,el=12,move='gun',cut=True),
 scene('Rotary shutter',7,CHAMBER|STAGE,('gun','fitting','shutter'),highlight={'@shutter','shutter_seal'},focus=(-20,0,165),scale=190,az=-64,el=16,move='shutter',cut=True),
 scene('Turbo pump',8,CHAMBER|TURBO|ISO,highlight=TURBO|ISO,focus=(0,0,-80),scale=185,az=-55,el=-4,move='turbo'),
 scene('Backing pump & foreline',7,TURBO|ISO|FORE|{'turbo_flange','kf_clamp','connection_seal'},highlight=FORE,az=-48,el=22),
 scene('Pressure gauges',7,CHAMBER|GAUGE|{'kf_clamp','connection_seal'},highlight=GAUGE,focus=(0,170,32),scale=140,az=58,el=18,move='gauges'),
 scene('Argon supply',6,CHAMBER|MFC|VCR|GAS,highlight=GAS,az=45,el=20),
 scene('Mass flow controller',8,CHAMBER|MFC|VCR|{'kf_clamp','connection_seal'},highlight=MFC|VCR,focus=(0,235,220),scale=155,az=35,el=28,move='mfc'),
 scene('Spare vacuum ports',5,CHAMBER|{'kf_clamp','connection_seal'},highlight={'blank_cap'},focus=(95,0,155),scale=175,az=-15,el=15),
 scene('Gun cooling loop',7,CHAMBER|{'gun_water','chiller1'},('gun','fitting'),highlight={'gun_water','chiller1'},az=-72,el=18),
 scene('Turbo cooling loop',7,TURBO|{'turbo_water','chiller2','turbo_flange'},highlight={'turbo_water','chiller2','turbo_cooling'},az=-65,el=25),
 scene('RF supply & matching network',7,CHAMBER|POWER,('gun','fitting'),highlight={'power','power_display','matching','power_cable'},az=-60,el=20),
 scene('Protective earth',4,CHAMBER|POWER|{'base_plate','frame'},highlight={'earth'},az=-55,el=20),
 scene('Sputter system',7,az=-57,el=25),
]

def ease(t):
    t=max(0,min(1,t)); return t*t*(3-2*t)

def motion(u):
    return 1-ease((u-.15)/.55)

def main():
    meta,arrays=prepare_mesh()
    window=vtk.vtkRenderWindow();window.SetOffScreenRendering(1);window.SetSize(W,H);window.SetMultiSamples(0)
    ren=vtk.vtkRenderer();ren.SetBackground(*BG);window.AddRenderer(ren)
    camera=ren.GetActiveCamera();camera.ParallelProjectionOn();camera.SetViewUp(0,0,1)
    actors=[]
    for i,q in enumerate(meta):
        triangles=arrays[f'p{i}'];pd=vtk.vtkPolyData();points=vtk.vtkPoints();points.SetData(numpy_to_vtk(triangles.reshape(-1,3),deep=True));pd.SetPoints(points)
        cells=vtk.vtkCellArray();cells.SetData(numpy_to_vtkIdTypeArray(np.arange(0,len(triangles)*3+1,3,dtype=np.int64),deep=True),numpy_to_vtkIdTypeArray(np.arange(len(triangles)*3,dtype=np.int64),deep=True));pd.SetPolys(cells)
        clean=vtk.vtkCleanPolyData();clean.SetInputData(pd)
        norm=vtk.vtkPolyDataNormals();norm.SetInputConnection(clean.GetOutputPort());norm.SetFeatureAngle(45);norm.Update()
        mapper=vtk.vtkPolyDataMapper();mapper.SetInputData(norm.GetOutput())
        actor=vtk.vtkActor();actor.SetMapper(mapper)
        prop=actor.GetProperty();prop.SetAmbient(.32);prop.SetDiffuse(.68);prop.SetSpecular(.3);prop.SetSpecularPower(36)
        ren.AddActor(actor);actors.append(actor)
    capture=vtk.vtkWindowToImageFilter();capture.SetInput(window);capture.SetInputBufferTypeToRGB();capture.ReadFrontBufferOff()
    font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',34)
    previews=[]

    def configure(s):
        visible=[]
        for q,a in zip(meta,actors):
            role,group=q['role'],q['group']
            show=s['roles'] is None or role in s['roles'] or group in s['groups']
            if role in {'kf_clamp','connection_seal'} and s['roles'] is not None:
                prefixes={'Backing pump & foreline':('Turbo KF16','KF25 turbo hose','RV3 inlet'),
                          'Pressure gauges':('Pirani','Penning'),
                          'Mass flow controller':('MFC chamber',),
                          'Spare vacuum ports':('Right spare',)}
                show=show and q['name'].startswith(prefixes.get(s['label'],()))
            # An open-front CAD view gives assembly access without exposing the gun internals.
            if s['cut'] and (q['name'] in ['Roof plate','Front welded door frame','Left wall - reserved blank'] or role in ['door_seal','hinge_fixed','hinge_pin','latch_catch']):show=False
            a.SetVisibility(show);a.SetUserTransform(None)
            selected=role in s['highlight'] or '@'+group in s['highlight']
            color=tuple(q['color'])
            if s['highlight']:
                color=(.20,.78,.87) if selected else (.38,.44,.50)
            else:
                # Keep neutral metal and original utility colours.
                color=tuple(.18+.75*c for c in color)
            a.GetProperty().SetColor(*color)
            a.GetProperty().SetOpacity(.32 if role=='glass' else 1)
            if show:visible.append(q['bbox_mm'])
        bounds=np.array(visible);lo=bounds[:,:3].min(axis=0);hi=bounds[:,3:].max(axis=0)
        focus=np.array(s['focus'] if s['focus'] else (lo+hi)/2,dtype=float)
        az=math.radians(s['az']);el=math.radians(s['el'])
        direction=np.array([math.cos(az)*math.cos(el),math.sin(az)*math.cos(el),math.sin(el)])
        right=np.cross(direction,[0,0,1]);right/=np.linalg.norm(right);up=np.cross(right,direction)
        corners=np.array([[x,y,z] for x in [lo[0],hi[0]] for y in [lo[1],hi[1]] for z in [lo[2],hi[2]]])-focus
        scale=s['scale'] or max(np.abs(corners@up).max(),np.abs(corners@right).max()/(W/H))*1.18
        return focus,scale

    def frame(s,u,focus,scale):
        m=motion(u)
        for q,a in zip(meta,actors):
            if not a.GetVisibility():continue
            role,group=q['role'],q['group'];tr=vtk.vtkTransform();kind=s['move']
            if group=='door' and kind=='door':
                # Open, hold, then close; no latch detail is invented.
                angle=-105*(ease((u-.12)/.25)-ease((u-.73)/.22))
                tr.Translate(-118,-116,0);tr.RotateZ(angle);tr.Translate(118,116,0)
            elif kind=='stage' and role in {'stage','substrate'}:tr.Translate(0,0,60*m)
            elif kind=='baffle' and role=='pump_baffle':tr.Translate(0,0,55*m)
            elif kind=='gun' and group in {'gun','fitting'}:tr.Translate(0,0,190*m)
            elif kind=='shutter' and group=='shutter':
                angle=95*(ease((u-.13)/.3)-ease((u-.73)/.24))
                tr.Translate(-65,0,0);tr.RotateZ(angle);tr.Translate(65,0,0)
            elif kind=='turbo':
                if role in TURBO:tr.Translate(0,0,-95*m)
                elif role=='iso_seal':tr.Translate(0,0,-30*m)
                elif role in {'iso_clamp','iso_screw'}:
                    b=q['bbox_mm'];x=(b[0]+b[3])/2;y=(b[1]+b[4])/2;tr.Translate(x*.7*m,y*.7*m,0)
            elif kind=='gauges' and (role in GAUGE or (role in {'kf_clamp','connection_seal'} and 'gauge joint' in q['name'])):tr.Translate(0,65*m,0)
            elif kind=='mfc' and role in MFC|VCR:
                # Mounted controller approaches its chamber-side KF/VCR connection.
                tr.Translate(0,(35 if role in {'mfc_out_adapter','vcr_out_nut','vcr_gasket'} else 70)*m,0)
            a.SetUserTransform(tr)
        az=math.radians(s['az']+5*(u-.5));el=math.radians(s['el'])
        camera.SetFocalPoint(*focus);camera.SetPosition(*(focus+2000*np.array([math.cos(az)*math.cos(el),math.sin(az)*math.cos(el),math.sin(el)])))
        camera.SetParallelScale(scale);ren.ResetCameraClippingRange()
        window.Render();capture.Modified();capture.Update()
        rgb=vtk_to_numpy(capture.GetOutput().GetPointData().GetScalars()).reshape(H,W,3)
        im=Image.fromarray(np.flipud(rgb));draw=ImageDraw.Draw(im)
        # One part label only; the CAD occupies the complete frame.
        draw.rectangle((0,H-88,W,H),fill=tuple(round(c*255) for c in BG))
        draw.text((48,H-67),s['label'],font=font,fill=(235,242,246))
        # Brief dip at cuts gives each assembly a clean start/end.
        fade=min(1,u*14,(1-u)*14)
        if fade<1:im=Image.blend(Image.new('RGB',(W,H),tuple(round(c*255) for c in BG)),im,max(0,fade))
        return im

    for j,s in enumerate(SCENES):
        focus,scale=configure(s);im=frame(s,.42,focus,scale);im.save(OUT/f'preview-{j+1:02}.jpg',quality=90);previews.append(im)
    sheet=Image.new('RGB',(1440,math.ceil(len(previews)/4)*203),(14,19,24))
    for j,im in enumerate(previews):sheet.paste(im.resize((360,203)),((j%4)*360,(j//4)*203))
    sheet.save(OUT/'contact-sheet.jpg',quality=93)
    if '--preview' in sys.argv:
        window.Finalize();print('Previews ready',flush=True);return
    ffmpeg=imageio_ffmpeg.get_ffmpeg_exe();video=OUT/'Sputter system - silent CAD walkthrough.mp4'
    proc=subprocess.Popen([ffmpeg,'-y','-loglevel','error','-f','rawvideo','-vcodec','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-an','-c:v','libx264','-preset','fast','-crf','19','-pix_fmt','yuv420p','-movflags','+faststart',str(video)],stdin=subprocess.PIPE)
    chapters=[];start=0;clock=time.time()
    try:
        for j,s in enumerate(SCENES):
            print(f'{j+1}/{len(SCENES)} {s["label"]} ({time.time()-clock:.0f}s elapsed)',flush=True)
            focus,scale=configure(s);n=round(s['seconds']*FPS)
            for k in range(n):proc.stdin.write(np.asarray(frame(s,k/(n-1),focus,scale)).tobytes())
            chapters.append({'label':s['label'],'start_seconds':start,'duration_seconds':s['seconds']});start+=s['seconds']
    finally:proc.stdin.close()
    if proc.wait()!=0:raise RuntimeError('Video encoding failed')
    source=ROOT/'system-architecture-and-cad/models/Complete sputter system R06.step'
    report={'source':str(source.relative_to(ROOT)),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'resolution':[W,H],'fps':FPS,'duration_seconds':start,'audio':False,'subtitles':False,'gun_internal_disassembly':False,'chapters':chapters,'notes':['Assembly-level CAD illustration; docking offsets are illustrative, not a service procedure.','RV3 backing pump is historical reference geometry; selected pump is INDOVAC HV2-150.','MFC and utility cabinets are reference envelopes; exact vendor geometry is pending.','Door rotates about modeled hinge axis; shutter rotates about modeled shaft.']}
    (OUT/'provenance.json').write_text(json.dumps(report,indent=2))
    window.Finalize();print(str(video),flush=True)

if __name__=='__main__':main()
