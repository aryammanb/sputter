"""Render the actual R06 STEP components as a narrated mechanical assembly tour.

python tools/build_assembly_walkthrough.py --preview
python tools/build_assembly_walkthrough.py
All visible solids come from the R06 STEP tessellation. Section planes only
clip the compression fitting, never the gun. No substitute primitive geometry.
"""
from pathlib import Path
import sys, json, math, subprocess, hashlib, wave, time
import numpy as np
import vtk, imageio_ffmpeg
from vtk.util.numpy_support import numpy_to_vtk, numpy_to_vtkIdTypeArray, vtk_to_numpy
from PIL import Image, ImageDraw, ImageFont
from build_current_media import prepare_mesh
from build_silent_walkthrough import CHAMBER, STAGE, BAFFLE, TURBO, ISO, FORE, GAUGE, MFC, VCR, GAS, POWER

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'media/assembly-walkthrough';OUT.mkdir(exist_ok=True)
WORK=OUT/'render';WORK.mkdir(exist_ok=True)
W,H,FPS=1920,1080,24

def shot(key,label,speech,focus,scale,az=-55,el=22,seconds=12):
    return dict(key=key,label=label,speech=speech,focus=focus,scale=scale,az=az,el=el,minimum_seconds=seconds)

SHOTS=[
 shot('whole','Complete assembly','This walkthrough uses the actual current R zero six CAD assembly. We will build up the chamber and follow the mechanical connections, keeping the sputter gun itself assembled.',(140,80,80),700,seconds=12),
 shot('stand','Chamber support frame','The chamber sits on four risers above the system base plate. The lower ties connect the risers. This leaves space for the turbo underneath, while the frame carries the chamber load.',(130,55,-110),470,az=-50,el=20,seconds=12),
 shot('shell','Chamber shell','The floor, three walls, roof and front loading frame form the welded chamber. Watch their mating edges come together. These are welded plates, so there are no invented shell fastening bolts.',(0,0,160),290,seconds=17),
 shot('ports','Chamber weld-on ports','The bottom ISO sixty three neck receives the turbo. The roof K F twenty five neck receives the gun gland. Three rear connections serve gas and gauges; two right-side connections remain spare.',(0,15,150),245,az=40,el=27,seconds=15),
 shot('door','Door, hinges & seal','The door carries its own hinge leaves. They align with the fixed chamber barrels around the two vertical hinge pins. The door swings about that shared axis and closes against the front frame gasket.',(-65,-55,145),270,az=-63,el=15,seconds=16),
 shot('window','Viewport assembly','At the front door, the gasket, glass and retaining bezel stack along the viewing axis. Six retainer screws enter the modeled blind holes in the door. The clear opening remains seventy millimetres.',(0,-130,105),112,az=-73,el=14,seconds=14),
 shot('stage','Baffle & substrate stage','Inside the chamber, the deposition baffle seats over its two spacers and around the four stage posts. The removable stage then rests on those posts, with the substrate on top.',(0,0,48),112,az=-55,el=32,seconds=15),
 shot('shutter_install','Shutter screw & blade','The bent shutter sits inside the chamber. Turning the top screw turns the screw, nuts, washer and blade together as one assembly. Only the O ring stays compressed and stationary against the roof.',(-40,0,165),205,az=-62,el=14,seconds=15),
 shot('gland_parts','Compression fitting','Here is the actual modeled gland assembly, separated into its body, tube seal, follower and threaded cap. The lower K F face seal and clamp form a different joint from the tube compression seal.',(0,0,362),78,az=-60,el=25,seconds=14),
 shot('gland_seat','Seat the fitting body','Place the face seal between the roof flange and the fitting body. The body lowers onto that seal. The compression cap remains loose while the chamber-side joint is assembled.',(0,0,352),76,az=-60,el=23,seconds=12),
 shot('gland_clamp','Secure the KF clamp','The two clamp jaws swing around their modeled hinge and close around the mating flange rims. The wing nut secures the clamp. This fixes the gland body to the chamber roof.',(0,0,338),53,az=-58,el=28,seconds=13),
 shot('gun_insert','Feed the gun tube upward','Feed the gun service tube upward through the loose gland, from the chamber side. The large gun head stays below the roof. This axial close-up shows the tube engagement, rather than claiming a complete handling path through the door.',(0,0,225),270,az=-65,el=9,seconds=15),
 shot('gun_height','Set the gun height','With the cap loose and the gun supported, the entire gun slides axially. The fixed gland body does not move. The modeled target to substrate range is seventy five to one hundred and fifty millimetres; here it returns to one hundred.',(0,0,240),255,az=-65,el=8,seconds=16),
 shot('gland_tighten','Tighten the compression cap','Hold the gun tube still while the cap turns clockwise, viewed from above, and advances down the body thread. The cap grips through the follower and tube seal. The tube does not turn with the cap.',(0,0,367),47,az=-62,el=19,seconds=15),
 shot('gland_section','Compression fitting · section','Only the fitting is sectioned here. The cap shoulder bears on the follower above the tube O ring. The lower K F face seal remains separate and stationary. The threads and seal seats shown are the existing CAD details; their dimensions still require purchased-part verification.',(0,0,365),47,az=-89,el=10,seconds=17),
 shot('gun_reposition','Loosen, slide, retighten','For repositioning, the cap loosens, the supported gun slides, and the cap tightens again. The K F clamp stays closed throughout. The modeled cap travel and number of turns illustrate the mechanism; they are not a specified tightening torque.',(0,0,352),98,az=-64,el=18,seconds=16),
 shot('turbo_seat','Turbo inlet & face seal','At the chamber underside, the ISO sixty three face seal sits between the chamber and turbo inlet flanges. The pump approaches along their common axis. The chamber stand carries the chamber independently.',(0,0,-115),190,az=-52,el=-8,seconds=14),
 shot('turbo_clamp','ISO63 claw clamps','Four double-claw clamps engage the two flange rims. Their screws tighten while the pump and mating flanges stay fixed. These are the actual clamp and screw solids in the assembly.',(0,0,-48),94,az=-48,el=-18,seconds=13),
 shot('foreline','Foreline connections','The turbo outlet is K F sixteen in this reference. An adapter takes it to the K F twenty five hose. Follow the hose to the backing pump inlet, where another face seal and split clamp complete the connection.',(230,180,-140),330,az=-48,el=27,seconds=15),
 shot('gauges','Pirani & Penning connections','The two lower rear ports receive K F elbows, then the gauge stems and bodies. Each flange joint has its own centering seal and split clamp. The elbows turn the gauges down, away from direct target exposure.',(0,175,40),150,az=60,el=16,seconds=15),
 shot('mfc_mount','Mass flow controller support','The mass flow controller has a separate shelf and gussets at the rear. Its two mounting screws locate the flow body on that shelf, so the gas fitting does not have to serve as the controller support.',(0,235,213),122,az=32,el=28,seconds=14),
 shot('mfc_out','MFC outlet to chamber','The chamber-side K F joint carries the outlet adapter. Its female V C R nut meets the controller male outlet, with a metal gasket between the mating faces. Watch the gasket seat before the swivel nut advances.',(0,177,210),60,az=8,el=23,seconds=15),
 shot('mfc_in','MFC inlet fittings','At the inlet, the second V C R metal gasket sits between the controller face and the female adapter. That adapter carries the N P T to six millimetre push fitting. The fitting chain closes from the controller outward.',(0,315,210),77,az=8,el=22,seconds=15),
 shot('tube_insert','Gas tube insertion','The actual six millimetre tube slides into the push fitting collet. The CAD shows sixteen millimetres of engagement as an illustrative value. The purchased fitting determines the required insertion depth.',(0,356,210),38,az=8,el=20,seconds=12),
 shot('gas','Argon supply route','The tube continues back to the regulator and argon cylinder. This is the existing CAD route into the controller inlet; the controller outlet then connects directly to the upper rear chamber port.',(330,280,215),530,az=40,el=22,seconds=12),
 shot('gun_water','Gun cooling connections','The two external cooling lines continue from the existing gun hoses at the top of the stem. Follow the supply and return to the gun cooling unit. The gun stays assembled throughout this connection view.',(-170,0,155),500,az=-70,el=15,seconds=14),
 shot('turbo_water','Turbo cooling connections','The second cooling loop connects to the two cooler stubs on the turbo. The CAD preserves the separate supply and return route to its own cooling cabinet. The cabinet and hose endpoints are existing layout references.',(310,-65,-120),480,az=-65,el=24,seconds=14),
 shot('power','RF supply, matching & earth','The RF cable runs from the source through the matching network, then to the gun coax at the top of the stem. The separate protective earth lead bonds the system structure. Follow the modeled cable endpoints.',(230,-110,100),535,az=-62,el=19,seconds=14),
 shot('whole_end','Complete assembly','The assembly is now shown together: chamber, gun gland, stage, shutter, pumps, gas control, cooling and RF services. The gun remains complete. Purchased-equipment envelopes and unresolved supplier interfaces are retained exactly as they exist in the current CAD.',(140,80,80),700,az=-42,el=25,seconds=14),
]

OPERATION_SHOTS=[
 shot('op_load','Load the substrate','The tool coats a substrate with a thin film of target material. After venting, open the door and place the substrate on the stage. The shutter is parked for access. Close the door before evacuation.',(-60,-45,140),270,az=-63,el=18,seconds=15),
 shot('op_pump','Evacuate the chamber','The closed chamber is evacuated through the bottom connection, turbo and backing pump. This is the actual pumping route in the CAD. Pressure measurement determines when the next process step can begin.',(210,80,65),510,az=-50,el=20,seconds=14),
 shot('op_gas','Admit regulated argon','Regulated argon enters through the mass flow controller and the upper rear chamber port. Gas admission and pumping establish the process conditions. The flow controller meters gas; the gauges measure chamber pressure.',(0,180,165),225,az=55,el=20,seconds=14),
 shot('op_condition','Shutter closed · target conditioning','R F power sustains an argon discharge. Argon ions strike the target and eject target material. With the shutter closed, the blade intercepts that material above the substrate. The target can condition before the sample is exposed.',(-15,0,122),145,az=-64,el=14,seconds=14),
 shot('op_sweep','Shutter screw · opening','This top view temporarily hides the complete gun so the shutter movement is visible. Turn the top screw to rotate the complete shutter assembly away from the substrate. Only the O ring remains compressed and stationary.',(-22,0,47),125,az=-90,el=90,seconds=15),
 shot('op_deposit','Shutter open · substrate coating','With the shutter parked, sputtered target material reaches the substrate and builds a thin film. The source remains above the fixed stage. The shutter controls the coating interval without moving either the substrate or the gun.',(-15,0,115),145,az=-64,el=14,seconds=16),
 shot('op_stop','Shutter screw · closing','Turn the complete screw and shutter assembly back to bring the blade over the substrate. Only the O ring remains compressed and stationary. Closing the shutter ends direct exposure before shutdown and venting.',(-22,0,47),125,az=-90,el=90,seconds=14),
 shot('op_unload','Vent, open & unload','After the source is off and the pumping system has completed its shutdown and vent sequence, open the door and remove the coated substrate. This completes the high-level cycle: load, evacuate, admit gas, condition, coat and unload.',(-60,-45,140),270,az=-63,el=18,seconds=16),
]
SHOTS=SHOTS[:-1]+OPERATION_SHOTS+SHOTS[-1:]

def smooth(x):
    x=max(0,min(1,x));return x*x*(3-2*x)
def ramp(u,a=.15,b=.75):return smooth((u-a)/(b-a))
def interp(u,pts):
    for (a,v),(b,w) in zip(pts,pts[1:]):
        if u<=b:return v+(w-v)*smooth((u-a)/(b-a))
    return pts[-1][1]

def narration():
    (OUT/'shots.json').write_text(json.dumps(SHOTS,indent=2))
    ps=WORK/'narrate.ps1'
    ps.write_text("param([string]$Json,[string]$Output)\nAdd-Type -AssemblyName System.Speech\n$s=New-Object System.Speech.Synthesis.SpeechSynthesizer\n$s.SelectVoice('Microsoft David Desktop')\n$s.Rate=0\nforeach($c in (Get-Content -LiteralPath $Json -Raw | ConvertFrom-Json)) { $s.SetOutputToWaveFile((Join-Path $Output ($c.key+'.wav'))); $s.Speak($c.speech); $s.SetOutputToNull() }\n$s.Dispose()\n")
    if '--preview' not in sys.argv:
        subprocess.run(['powershell','-NoProfile','-ExecutionPolicy','Bypass','-File',str(ps),str(OUT/'shots.json'),str(WORK)],check=True)
    duration=[]
    for s in SHOTS:
        if '--preview' in sys.argv:duration.append(s['minimum_seconds']);continue
        with wave.open(str(WORK/(s['key']+'.wav')),'rb') as f:secs=f.getnframes()/f.getframerate()
        duration.append(math.ceil(max(s['minimum_seconds'],secs+2)*FPS)/FPS)
    return duration

class Renderer:
    def __init__(self):
        self.meta,arrays=prepare_mesh();self.win=vtk.vtkRenderWindow();self.win.SetOffScreenRendering(1);self.win.SetSize(W,H);self.win.SetMultiSamples(4)
        self.ren=vtk.vtkRenderer();self.ren.SetBackground(.19,.225,.265);self.ren.SetBackground2(.37,.405,.445);self.ren.GradientBackgroundOn();self.ren.SetUseFXAA(True);self.ren.AutomaticLightCreationOff();self.win.AddRenderer(self.ren)
        self.cam=self.ren.GetActiveCamera();self.cam.ParallelProjectionOn();self.cam.SetViewUp(0,0,1)
        # A broad studio rig retains the actual component colours and metal finish.
        for position,intensity,color in [((-.8,-1,1.6),.85,(1,.96,.90)),((1,.3,.8),.65,(.84,.91,1)),((0,1,-.2),.35,(1,1,1))]:
            light=vtk.vtkLight();light.SetLightTypeToCameraLight();light.SetPosition(*position);light.SetFocalPoint(0,0,0);light.SetIntensity(intensity);light.SetColor(*color);self.ren.AddLight(light)
        self.actors=[];self.fullmaps=[];self.sectionmaps={};self.planes=[]
        for i,q in enumerate(self.meta):
            a=arrays[f'p{i}'];pd=vtk.vtkPolyData();v=vtk.vtkPoints();v.SetData(numpy_to_vtk(a.reshape(-1,3),deep=True));pd.SetPoints(v)
            cells=vtk.vtkCellArray();cells.SetData(numpy_to_vtkIdTypeArray(np.arange(0,len(a)*3+1,3,dtype=np.int64),deep=True),numpy_to_vtkIdTypeArray(np.arange(len(a)*3,dtype=np.int64),deep=True));pd.SetPolys(cells)
            clean=vtk.vtkCleanPolyData();clean.SetInputData(pd);norm=vtk.vtkPolyDataNormals();norm.SetInputConnection(clean.GetOutputPort());norm.SetFeatureAngle(38);norm.Update()
            mapper=vtk.vtkPolyDataMapper();mapper.SetInputData(norm.GetOutput());mapper.ScalarVisibilityOff()
            if q['role']=='shutter_screw':
                # A surface colour witness mark makes this axisymmetric screw's
                # rotation visible. The CAD mesh and dimensions are unchanged.
                screw_poly=norm.GetOutput();centres=vtk.vtkCellCenters();centres.SetInputData(screw_poly);centres.Update()
                xyz=vtk_to_numpy(centres.GetOutput().GetPoints().GetData())
                angle=np.arctan2(xyz[:,1],xyz[:,0]+65)
                delta=np.arctan2(np.sin(angle+math.radians(62)),np.cos(angle+math.radians(62)))
                mark=(xyz[:,2]>315.5)&(np.abs(delta)<math.radians(16))
                colours=np.tile(np.array(q['color'])*255,(len(xyz),1));colours[mark]=[246,180,44]
                scalars=numpy_to_vtk(colours.astype(np.uint8),deep=True,array_type=vtk.VTK_UNSIGNED_CHAR);scalars.SetName('Screw surface witness mark')
                screw_poly.GetCellData().SetScalars(scalars);mapper.SetScalarModeToUseCellData();mapper.SetColorModeToDirectScalars();mapper.ScalarVisibilityOn()
            actor=vtk.vtkActor();actor.SetMapper(mapper);prop=actor.GetProperty();prop.SetColor(*q['color']);prop.SetAmbient(.24);prop.SetDiffuse(.65);prop.SetSpecular(.38);prop.SetSpecularPower(50)
            if q['role'] in {'glass','door_seal','viewport_seal','fit_tube_seal','fit_kf_seal'}:prop.SetSpecular(.1)
            self.ren.AddActor(actor);self.actors.append(actor)
            self.fullmaps.append(mapper)
            if q['group']=='fitting' and q['role'] in {'fit_body','fit_cap','fit_follower','fit_tube_seal','fit_kf_seal'}:
                plane=vtk.vtkPlane();plane.SetOrigin(0,0,0);plane.SetNormal(0,1,0)
                planes=vtk.vtkPlaneCollection();planes.AddItem(plane)
                clipped=vtk.vtkClipClosedSurface();clipped.SetInputData(norm.GetOutput());clipped.SetClippingPlanes(planes);clipped.GenerateFacesOn();clipped.Update()
                cm=vtk.vtkPolyDataMapper();cm.SetInputData(clipped.GetOutput());cm.ScalarVisibilityOff();self.sectionmaps[i]=cm
        self.cap=vtk.vtkWindowToImageFilter();self.cap.SetInput(self.win);self.cap.SetInputBufferTypeToRGB();self.cap.ReadFrontBufferOff()
        self.font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',36)

    def frame(self,s,u):
        key=s['key'];t=ramp(u);opening=0
        for i,(q,a) in enumerate(zip(self.meta,self.actors)):
            role,name,group=q['role'],q['name'],q['group'];tr=vtk.vtkTransform();show=False
            is_chamber=group=='chamber';is_door=group=='door';is_fit=group=='fitting';is_gun=group=='gun'
            a.SetMapper(self.sectionmaps[i] if key=='gland_section' and i in self.sectionmaps else self.fullmaps[i])
            a.GetMapper().RemoveAllClippingPlanes();a.GetProperty().SetOpacity(.38 if role=='glass' else 1)
            if key in {'whole','whole_end'}:show=True
            elif key in {'op_load','op_unload'}:
                show=is_chamber or is_door or is_fit or is_gun or group=='shutter'
                if is_door:
                    if key=='op_load':angle=-105*(1-ramp(u,.62,.93))
                    else:angle=-105*ramp(u,.08,.4)
                    tr.Translate(-118,-116,0);tr.RotateZ(angle);tr.Translate(118,116,0)
                if group=='shutter':tr.Translate(-65,0,0);tr.RotateZ(80);tr.Translate(65,0,0)
                if role=='substrate':
                    offset=1-ramp(u,.15,.5) if key=='op_load' else ramp(u,.5,.9)
                    tr.Translate(0,-160*offset,18*math.sin(math.pi*offset))
            elif key=='op_pump':
                show=True
            elif key=='op_gas':
                show=True
            elif key in {'op_condition','op_sweep','op_deposit','op_stop'}:
                show=is_gun or group=='shutter' or role in STAGE|BAFFLE|{'shutter_seal'} or name=='Floor plate'
                if key in {'op_sweep','op_stop'}:
                    if is_gun:show=False
                    angle=80*ramp(u,.12,.82) if key=='op_sweep' else 80*(1-ramp(u,.12,.82))
                else:angle=80 if key=='op_deposit' else 0
                if group=='shutter':tr.Translate(-65,0,0);tr.RotateZ(angle);tr.Translate(65,0,0)
            elif key=='stand':
                show=role in {'frame','base_plate'} or name=='Floor plate'
            elif key=='shell':
                names=['Floor plate','Rear wall','Left wall - reserved blank','Right wall','Roof plate','Front welded door frame']
                if name in names:
                    j=names.index(name);p=ramp(u,max(0,(j-1)*.13),max(.12,j*.13+.08)) if j else 1
                    show=u>=max(0,(j-1)*.13-.01) or j==0
                    directions=[(0,0,0),(0,80,0),(-80,0,0),(80,0,0),(0,0,90),(0,-80,0)]
                    tr.Translate(*(np.array(directions[j])*(1-p)))
            elif key=='ports':
                show=role in {'structure','service_port','gun_mount','turbo_flange'}
                if role in {'service_port','gun_mount','turbo_flange'}:
                    direction=(0,50,0) if role=='service_port' and 'Rear' in name else (50,0,0) if role=='service_port' else (0,0,55) if role=='gun_mount' else (0,0,-55)
                    tr.Translate(*(np.array(direction)*(1-t)))
            elif key=='door':
                show=is_chamber or is_door
                if role in STAGE|BAFFLE|{'shutter_seal'}:show=False
                opening=-105*interp(u,[(0,1),(.35,1),(.7,0),(1,1)])
                if is_door:
                    tr.Translate(-118,-116,0);tr.RotateZ(opening);tr.Translate(118,116,0)
                if role=='hinge_pin':tr.Translate(0,0,55*(1-ramp(u,.05,.3)))
            elif key=='window':
                show=is_door
                offset={'viewport_seal':14,'glass':35,'viewport_bezel':58,'door_screw':80}.get(role,0)*(1-ramp(u,.12,.7))
                tr.Translate(0,-offset,0)
                if role=='door_screw':
                    b=q['bbox_mm'];x=(b[0]+b[3])/2;z=(b[2]+b[5])/2
                    tr.Translate(x,-142,z);tr.RotateY(540*ramp(u,.7,.95));tr.Translate(-x,142,-z)
            elif key=='stage':
                show=name=='Floor plate' or role in STAGE|BAFFLE
                if role=='pump_baffle':tr.Translate(0,0,55*(1-ramp(u,.08,.4)))
                if role=='stage':tr.Translate(0,0,90*(1-ramp(u,.42,.7)))
                if role=='substrate':tr.Translate(0,0,115*(1-ramp(u,.72,.92)))
            elif key=='shutter_install':
                show=name in {'Roof plate','Floor plate'} or group=='shutter' or role in STAGE|{'shutter_seal'}
                if name=='Roof plate':a.GetProperty().SetOpacity(.18)
                if role=='shutter':tr.Translate(0,0,-35*(1-ramp(u,.05,.35)))
                if role in {'shutter_screw','shutter_seal'}:tr.Translate(0,0,38*(1-ramp(u,.35,.6)))
                if role in {'shutter_nut','shutter_washer'}:tr.Translate(0,0,-25*(1-ramp(u,.3,.6)))
                if u>.65 and group=='shutter':
                    tr.Translate(-65,0,0);tr.RotateZ(80*math.sin(math.pi*ramp(u,.65,1))**2);tr.Translate(65,0,0)
            elif key.startswith('gland') or key in {'gun_insert','gun_height','gun_reposition'}:
                show=is_fit or is_gun or name=='Roof plate' or role=='gun_mount'
                if key in {'gland_parts','gland_seat','gland_clamp'} and is_gun:show=False
                if key=='gun_height':show=show or name=='Floor plate' or role in STAGE
                caplift=4.;spin=0.;bodylift=0.;jaw=0.;gunshift=0.
                if key=='gland_parts':
                    caplift=35; jaw=35
                    if role=='fit_follower':tr.Translate(0,0,20)
                    if role=='fit_tube_seal':tr.Translate(0,0,10)
                elif key=='gland_seat':bodylift=38*(1-t);jaw=35
                elif key=='gland_clamp':jaw=35*(1-ramp(u,.08,.6))
                elif key=='gun_insert':gunshift=-112*(1-t)
                elif key=='gun_height':gunshift=interp(u,[(0,0),(.3,-25),(.65,50),(1,0)])
                elif key in {'gland_tighten','gland_section'}:caplift=4*(1-t);spin=-720*t
                elif key=='gun_reposition':
                    caplift=interp(u,[(0,0),(.28,4),(.65,4),(1,0)]);spin=180*caplift;gunshift=interp(u,[(0,0),(.3,0),(.65,25),(1,25)])
                if is_gun:tr.Translate(0,0,gunshift)
                if is_fit:
                    if role in {'fit_body','fit_cap','fit_cap_mark','fit_follower','fit_tube_seal'}:tr.Translate(0,0,bodylift)
                    if role in {'fit_cap','fit_cap_mark'}:
                        tr.Translate(0,0,caplift)
                        # A stationary CAD section shows axial movement without
                        # sweeping the cutaway around with the threaded cap.
                        if key!='gland_section':tr.RotateZ(spin)
                    if role=='fit_cap_mark' and key=='gland_section':show=False
                    if role=='fit_follower' and key!='gland_parts':tr.Translate(0,0,.52*min(1,caplift/.52))
                    if role=='fit_clamp_left':tr.Translate(0,25,0);tr.RotateZ(-jaw);tr.Translate(0,-25,0)
                    if role=='fit_clamp_right':tr.Translate(0,25,0);tr.RotateZ(jaw);tr.Translate(0,-25,0)
                    if role in {'fit_clamp_bolt','fit_clamp_wing'} and jaw>2:show=False
                    if role=='fit_clamp_wing' and key=='gland_clamp':tr.Translate(14,-29,332);tr.RotateX(720*ramp(u,.6,.95));tr.Translate(-14,29,-332)
                if key=='gland_section' and name=='Roof plate':show=False
            elif key in {'turbo_seat','turbo_clamp'}:
                show=role in TURBO|ISO or name=='Floor plate' or role=='turbo_flange'
                if key=='turbo_seat':
                    if role in TURBO:tr.Translate(0,0,-95*(1-t))
                    if role=='iso_seal':tr.Translate(0,0,-28*(1-ramp(u,.05,.35)))
                    if role in {'iso_clamp','iso_screw'}:show=False
                else:
                    b=q['bbox_mm'];x=(b[0]+b[3])/2;y=(b[1]+b[4])/2
                    if role in {'iso_clamp','iso_screw'}:tr.Translate(x*.7*(1-ramp(u,.08,.6)),y*.7*(1-ramp(u,.08,.6)),0)
                    if role=='iso_screw':
                        tr.Translate(x,y,-48);tr.RotateZ(720*ramp(u,.6,.95));tr.Translate(-x,-y,48)
            elif key=='foreline':
                show=role in TURBO|FORE|{'connection_seal','kf_clamp'}
                if role in {'connection_seal','kf_clamp'}:show=name.startswith(('Turbo KF16','KF25 turbo hose','RV3 inlet'))
                if role=='foreline_adapter':tr.Translate(30*(1-ramp(u,.1,.4)),0,0)
                if role in {'hose','hose_ribs','hose_end'}:tr.Translate(45*(1-ramp(u,.3,.75)),0,0)
                if role=='kf_clamp':
                    b=q['bbox_mm'];z=(b[2]+b[5])/2
                    tr.Translate(0,0,(18 if 'left' in name else -18)*(1-ramp(u,.7,.95)))
            elif key=='gauges':
                show=role in GAUGE or name=='Rear wall' or (role=='service_port' and ('Pirani' in name or 'Penning' in name))
                if role in {'connection_seal','kf_clamp'}:show=name.startswith(('Pirani','Penning'))
                if role in GAUGE:tr.Translate(0,65*(1-ramp(u,.15,.7)),0)
                if role=='connection_seal' and 'rear port' in name:tr.Translate(0,15*(1-ramp(u,.05,.3)),0)
                if role=='kf_clamp':tr.Translate((-15 if 'left' in name else 15)*(1-ramp(u,.7,.95)),0,0)
            elif key.startswith('mfc') or key=='tube_insert':
                show=role in MFC|VCR or name=='Rear wall' or (role=='service_port' and 'gas' in name)
                if role in {'connection_seal','kf_clamp'}:show=name.startswith('MFC chamber')
                if key=='mfc_mount':
                    if role in MFC-{'mfc_bracket'}:tr.Translate(0,0,35*(1-ramp(u,.2,.65)))
                    if role=='mfc_mount_screw':
                        b=q['bbox_mm'];y=(b[1]+b[4])/2;tr.Translate(0,y,0);tr.RotateZ(540*ramp(u,.65,.95));tr.Translate(0,-y,0)
                elif key=='mfc_out':
                    shift={'mfc_out_adapter':28,'vcr_out_nut':45}.get(role,0)
                    if role=='vcr_gasket' and 'outlet' in name:shift=20
                    if role in MFC-{'mfc_bracket','mfc_mount_screw'}:shift=65
                    tr.Translate(0,shift*(1-t),0)
                    if role=='vcr_out_nut':tr.Translate(0,0,210);tr.RotateY(360*ramp(u,.65,.95));tr.Translate(0,0,-210)
                elif key=='mfc_in':
                    shift=0
                    if role=='vcr_gasket' and 'inlet' in name:shift=18
                    if role in {'vcr_in_nut','vcr_npt_adapter'}:shift=45
                    if role in {'push_body','push_collet'}:shift=75
                    if role=='gas_insert':shift=95
                    tr.Translate(0,shift*(1-t),0)
                    if role in {'vcr_in_nut','vcr_npt_adapter','push_body','push_collet'}:
                        tr.Translate(0,0,210);tr.RotateY(360*ramp(u,.65,.95));tr.Translate(0,0,-210)
                else:
                    if role=='gas_insert':tr.Translate(0,26*(1-t),0)
            elif key=='gas':show=role in MFC|VCR|GAS or (role=='service_port' and 'gas' in name)
            elif key=='gun_water':show=is_gun or is_fit or name=='Roof plate' or role in {'gun_water','chiller1','gun_mount'}
            elif key=='turbo_water':show=role in TURBO|{'turbo_water','chiller2','turbo_flange'}
            elif key=='power':show=is_gun or is_fit or is_chamber or role in POWER
            a.SetVisibility(show);a.SetUserTransform(tr)
        focus=np.array(s['focus'],float);scale=s['scale'];az=s['az'];el=s['el']
        # Slow, small camera changes only where they help follow a physical route.
        if key in {'whole','whole_end','gas','power','gun_water','turbo_water'}:az+=8*(u-.5)
        if key=='ports':az=interp(u,[(0,35),(.4,45),(.8,75),(1,75)])
        if key=='foreline':
            v=ramp(u,.55,.9);focus=focus*(1-v)+np.array([393,325,-115])*v;scale=330*(1-v)+140*v
        if key=='gun_water':
            v=ramp(u,.08,.4)*(1-ramp(u,.65,.95));focus=focus*(1-v)+np.array([0,0,442])*v;scale=scale*(1-v)+85*v
        if key=='turbo_water':
            v=ramp(u,.1,.45)*(1-ramp(u,.7,.95));focus=focus*(1-v)+np.array([0,-30,-180])*v;scale=scale*(1-v)+100*v
        if key=='op_pump':
            v=ramp(u,.35,.85);focus=focus*(1-v)+np.array([270,200,-160])*v;scale=510*(1-v)+300*v
        az=math.radians(az);el=math.radians(el)
        self.cam.SetViewUp(0,1,0) if key in {'op_sweep','op_stop'} else self.cam.SetViewUp(0,0,1)
        self.cam.SetFocalPoint(*focus);self.cam.SetPosition(*(focus+2400*np.array([math.cos(az)*math.cos(el),math.sin(az)*math.cos(el),math.sin(el)])));self.cam.SetParallelScale(scale)
        self.ren.ResetCameraClippingRange();self.win.Render();self.cap.Modified();self.cap.Update()
        rgb=vtk_to_numpy(self.cap.GetOutput().GetPointData().GetScalars()).reshape(H,W,3)
        im=Image.fromarray(np.flipud(rgb));draw=ImageDraw.Draw(im)
        # A single short label, with no explanatory sidebar or blanket recolouring.
        draw.rounded_rectangle((36,H-87,72+draw.textlength(s['label'],font=self.font),H-22),radius=7,fill=(29,38,49))
        draw.text((54,H-78),s['label'],font=self.font,fill=(241,245,248))
        return im

def main():
    global OUT,WORK,SHOTS
    if '--repair-shutter' in sys.argv:
        keys={'shutter_install','op_load','op_sweep','op_deposit','op_stop','op_unload'}
        SHOTS=[s for s in SHOTS if s['key'] in keys]
        OUT=OUT/'shutter-repair';OUT.mkdir(exist_ok=True);WORK=OUT/'render';WORK.mkdir(exist_ok=True)
    elif '--operation' in sys.argv:
        SHOTS=OPERATION_SHOTS
        OUT=OUT/'operation';OUT.mkdir(exist_ok=True);WORK=OUT/'render';WORK.mkdir(exist_ok=True)
    durations=narration();r=Renderer();previews=[]
    for j,s in enumerate(SHOTS):
        im=r.frame(s,.48);im.save(OUT/f'preview-{j+1:02}.jpg',quality=94);previews.append(im)
    sheet=Image.new('RGB',(1920,math.ceil(len(previews)/4)*270))
    for j,im in enumerate(previews):sheet.paste(im.resize((480,270)),(j%4*480,j//4*270))
    sheet.save(OUT/'assembly-contact-sheet.jpg',quality=94)
    for key in ['shell','gland_clamp','gun_insert','gland_tighten','gland_section','mfc_out']:
        s=next((x for x in SHOTS if x['key']==key),None)
        if s is None:continue
        for u in [.12,.85]:r.frame(s,u).save(OUT/f'check-{key}-{u}.jpg',quality=94)
    if '--preview' in sys.argv:r.win.Finalize();print('Assembly previews ready',flush=True);return
    # Pad each narration to its shot; retain concise speech and a visual hold.
    audio=WORK/'Narration.wav';params=None;chunks=[]
    for s,duration in zip(SHOTS,durations):
        with wave.open(str(WORK/(s['key']+'.wav')),'rb') as f:
            p=f.getparams();raw=f.readframes(p.nframes)
        if params is None:params=p
        assert p.framerate==params.framerate and p.sampwidth==params.sampwidth
        lead=round(.5*p.framerate);tail=round(duration*p.framerate)-lead-p.nframes
        chunks.append(bytes(lead*p.sampwidth*p.nchannels)+raw+bytes(tail*p.sampwidth*p.nchannels))
    with wave.open(str(audio),'wb') as f:
        f.setparams(params)
        for chunk in chunks:f.writeframes(chunk)
    ff=imageio_ffmpeg.get_ffmpeg_exe();silent=WORK/'picture.mp4'
    proc=subprocess.Popen([ff,'-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-an','-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p',str(silent)],stdin=subprocess.PIPE)
    timeline=[];elapsed=0;clock=time.time()
    try:
        for j,(s,seconds) in enumerate(zip(SHOTS,durations)):
            print(f'{j+1}/{len(SHOTS)} {s["label"]}: {seconds:.1f}s, render elapsed {time.time()-clock:.0f}s',flush=True)
            n=round(seconds*FPS)
            for k in range(n):proc.stdin.write(np.asarray(r.frame(s,k/(n-1))).tobytes())
            timeline.append(dict(key=s['key'],label=s['label'],start_seconds=elapsed,duration_seconds=seconds));elapsed+=seconds
    finally:proc.stdin.close()
    if proc.wait()!=0:raise RuntimeError('Video encode failed')
    metadata=';FFMETADATA1\ntitle=Sputter R06 - mechanical assembly walkthrough\n'
    for s in timeline:metadata+=f'[CHAPTER]\nTIMEBASE=1/1000\nSTART={round(s["start_seconds"]*1000)}\nEND={round((s["start_seconds"]+s["duration_seconds"])*1000)}\ntitle={s["label"]}\n'
    (WORK/'chapters.ffmeta').write_text(metadata,encoding='utf-8')
    final=OUT/'Sputter R06 - mechanical assembly walkthrough.mp4'
    subprocess.run([ff,'-y','-loglevel','error','-i',str(silent),'-i',str(audio),'-i',str(WORK/'chapters.ffmeta'),'-map','0:v','-map','1:a','-map_metadata','2','-map_chapters','2','-c:v','copy','-c:a','aac','-b:a','160k','-movflags','+faststart',str(final)],check=True)
    source=ROOT/'cad/coolant-fitting-r06/Complete sputter system R06.step'
    provenance=dict(source=str(source.relative_to(ROOT)),source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),geometry='Exact tessellated R06 component solids; no substituted geometry',resolution=[W,H],fps=FPS,duration_seconds=elapsed,component_instances=len(r.meta),chapters=timeline,narration='Windows Microsoft David Desktop, synthetic',reference_walkthrough='cad/main-system-r04/Complete sputter system R04 - main walkthrough.mp4',notes=['Exploded construction views illustrate mating relationships; no collision-free handling path or weld procedure is certified.','Only the compression fitting is sectioned. Gun internals are never exposed or disassembled.','Fitting thread pitch/turn count and seal details are the pre-existing illustrative CAD, not purchased-part specifications.','RV3, MFC, cabinets and other purchased reference envelopes are unchanged from the source CAD.'])
    provenance['complete_shutter_rotation']=True
    provenance['shutter_correction']='Screw, nuts, washer and blade rotate together; only the compressed O-ring remains stationary.'
    provenance['visual_rotation_cue']='Gold surface witness mark on the unchanged screw mesh.'
    (OUT/'provenance.json').write_text(json.dumps(provenance,indent=2))
    (OUT/'Narration.txt').write_text('\n\n'.join(s['label']+'\n'+s['speech'] for s in SHOTS),encoding='utf-8')
    r.win.Finalize();print(f'Complete: {elapsed:.1f}s / {final}',flush=True)

if __name__=='__main__':main()
