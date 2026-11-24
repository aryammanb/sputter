import csv,json,math,struct,sys,time,wave,subprocess
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
import vtk
from vtk.util.numpy_support import numpy_to_vtk,numpy_to_vtkIdTypeArray,vtk_to_numpy
import imageio_ffmpeg

ROOT=Path(__file__).resolve().parent;OUT=ROOT/'assembly-video';W,H,PANEL,FPS=1920,1080,460,15
chapters=json.loads((OUT/'chapters.json').read_text());audit=json.loads((ROOT/'native-assembly-audit.json').read_text(encoding='utf-8-sig'))
poses={c['name']:np.array(c['transform'][9:12])*1000 for c in audit['components']}
def smooth(u):u=max(0,min(1,u));return u*u*(3-2*u)
def part_string(f):
    b=f.read(1)
    if not b:return None
    n=b[0]&127;shift=7
    while b[0]&128:b=f.read(1);n|=(b[0]&127)<<shift;shift+=7
    return f.read(n).decode()
def role(name,file):
    group=int(name[:2])
    exact={'Kuehlkoerper.SLDPRT':'cooler','Backplate.SLDPRT':'closure','Magnet Joke.SLDPRT':'yoke','Abstandshalter.SLDPRT':'spacer','Isolator.SLDPRT':'isolator','Boden.SLDPRT':'base','Target Klemme.SLDPRT':'clamp','Groundshield Rohr.SLDPRT':'shieldtube','Dunkelraumabschirmung.SLDPRT':'darkcap'}
    if file in exact:return exact[file]
    if 'outer magnet' in file:return 'outermag'
    if 'center magnet' in file:return 'centermag'
    if 'O-ring ID14p5' in file or 'O-ring ID35x' in file:return 'waterseal'
    if 'O-ring ID76x' in file:return 'headseal'
    if 'O-ring ID62x' in file:return 'upper62' if poses[name][1]>-43 else 'lower62'
    if 'M3x16' in file:return 'backbolts'
    if 'M4x10' in file:return 'yokebolt'
    if 'M4x8' in file:return 'hvbolt' if group==1 else 'lowerbolts'
    if 'wire hook' in file:return 'hook'
    if 'fitting' in file:return 'fittings'
    if group==7:return 'services'
    if 'M3x35' in file:return 'headbolts' if group==2 else 'basebolts'
    if 'shoulder sleeve' in file:return 'sleeves'
    if 'titanium target' in file:return 'target'
    if 'M3x8' in file:return 'targetbolts'
    if 'M3x6' in file:return 'upperbolts'
    if 'flange clamp half' in file:return 'kfclamps'
    if 'KF16 flanged tube' in file:return 'kftube'
    if 'KF16 centering' in file:return 'kfcenter'
    if 'KF16 O-ring' in file:return 'kfseal'
    if 'M5x20' in file:return 'kfbolts'
    raise ValueError((name,file))
def color(file,tag):
    if tag in ['cooler','closure']:return (.83,.49,.27)
    if tag=='outermag':return (.77,.23,.25)
    if tag=='centermag':return (.20,.39,.79)
    if tag in ['waterseal','headseal','upper62','lower62','kfseal']:return (.09,.12,.105)
    if tag in ['isolator','sleeves']:return (.91,.88,.77)
    if 'blue' in file:return (.10,.32,.68)
    if 'white HV' in file:return (.94,.92,.85)
    if 'copper conductor' in file or tag=='hook':return (.83,.48,.24)
    if tag=='yoke':return (.40,.46,.54)
    if tag=='shieldtube':return (.40,.53,.61)
    if tag=='target':return (.61,.63,.68)
    return (.59,.65,.71)
records=[]
with (ROOT/'actual-assembly-mesh.bin').open('rb') as f:
    while name:=part_string(f):
        file=part_string(f);n=struct.unpack('<i',f.read(4))[0];v=np.frombuffer(f.read(n*36),'<f4').reshape(-1,3,3).astype(np.float64)
        records.append({'name':name,'file':file,'v':v,'role':role(name,file),'anchor':poses[name]})
assert len(records)==120
N={tag:sum(r['role']==tag for r in records) for tag in set(r['role'] for r in records)}
assert N['outermag']==12 and N['centermag']==2 and N['sleeves']==12 and sum(v for k,v in N.items() if 'bolts' in k or k in ['yokebolt','hvbolt'])==65

def polydata(v):
    poly=vtk.vtkPolyData();points=vtk.vtkPoints();points.SetData(numpy_to_vtk(v.reshape(-1,3),deep=True));poly.SetPoints(points)
    cells=vtk.vtkCellArray();cells.SetData(numpy_to_vtkIdTypeArray(np.arange(0,len(v)*3+1,3,dtype=np.int64),deep=True),numpy_to_vtkIdTypeArray(np.arange(len(v)*3,dtype=np.int64),deep=True));poly.SetPolys(cells)
    clean=vtk.vtkCleanPolyData();clean.SetInputData(poly);clean.SetTolerance(1e-8);clean.Update()
    normals=vtk.vtkPolyDataNormals();normals.SetInputConnection(clean.GetOutputPort());normals.SetFeatureAngle(35);normals.SplittingOn();normals.ConsistencyOn();normals.AutoOrientNormalsOn();normals.Update()
    result=vtk.vtkPolyData();result.ShallowCopy(normals.GetOutput());return result
def clipped(poly,half=False,trim=False):
    planes=vtk.vtkPlaneCollection()
    if half:
        p=vtk.vtkPlane();p.SetOrigin(0,0,0);p.SetNormal(-1,0,0);planes.AddItem(p)
    if trim:
        p=vtk.vtkPlane();p.SetOrigin(0,-110,0);p.SetNormal(0,1,0);planes.AddItem(p)
    if not planes.GetNumberOfItems():return poly
    clip=vtk.vtkClipClosedSurface();clip.SetInputData(poly);clip.SetClippingPlanes(planes);clip.GenerateFacesOn();clip.GenerateOutlineOff();clip.SetTolerance(1e-5);clip.Update()
    result=vtk.vtkPolyData();result.ShallowCopy(clip.GetOutput());return result
renderer=vtk.vtkRenderer();renderer.SetBackground(16/255,27/255,42/255)
window=vtk.vtkRenderWindow();window.SetOffScreenRendering(1);window.SetSize(W-PANEL,H);window.SetMultiSamples(4);window.AddRenderer(renderer)
camera=renderer.GetActiveCamera();camera.ParallelProjectionOn()
for r in records:
    r['poly']=polydata(r['v']);mapper=vtk.vtkPolyDataMapper();mapper.SetInputData(r['poly']);mapper.ScalarVisibilityOff();actor=vtk.vtkActor();actor.SetMapper(mapper)
    actor.GetProperty().SetColor(*color(r['file'],r['role']));actor.GetProperty().SetAmbient(.24);actor.GetProperty().SetDiffuse(.68);actor.GetProperty().SetSpecular(.26);actor.GetProperty().SetSpecularPower(35);actor.GetProperty().SetInterpolationToPhong()
    if r['role'] in ['waterseal','headseal','upper62','lower62','kfseal']:actor.GetProperty().SetSpecular(.05)
    renderer.AddActor(actor);r['actor']=actor;r['mapper']=mapper;r['variants']={'full':r['poly']};r['current']='full'
capture=vtk.vtkWindowToImageFilter();capture.SetInput(window);capture.SetInputBufferTypeToRGB();capture.ReadFrontBufferOff();capture.ShouldRerenderOff()

COPPER={'cooler','closure','waterseal','backbolts'}
MAG=COPPER|{'outermag','centermag','yoke'}
CONNECTED=MAG|{'yokebolt','hvbolt','hook','fittings'}
SPACER=CONNECTED|{'spacer','headseal'}
HEAD=SPACER|{'headbolts'}
ISOLATED=HEAD|{'upper62','isolator'}
BASE=ISOLATED|{'base','lower62','sleeves','basebolts'}
MOUNTED=BASE|{'kftube','kfclamps','kfcenter','kfseal','kfbolts','services'}
TARGETED=MOUNTED|{'target','clamp','targetbolts'}
ALL=set(N)
LAYER={'cooler':70,'closure':40,'yoke':0,'outermag':5,'centermag':5,'spacer':-35,'isolator':-60,'base':-85,'target':90,'clamp':100,'darkcap':120,'headseal':-35,'upper62':-35,'lower62':-85,'waterseal':40}
def scene(index,u,r):
    tag=r['role'];pos=np.zeros(3);orientation=np.zeros(3);origin=np.zeros(3);half=False;trim=index not in [0,1,2,17];highlight=False
    visible=True
    if index==0:pass
    elif index==1:
        visible=tag in LAYER;pos[1]=LAYER.get(tag,0)
    elif index==2:
        visible=tag in ['cooler','closure'];pos[0]=52 if tag=='cooler' else -52
        if tag=='closure':origin=np.array([0,-15.75,0]);orientation[0]=180
    elif index==3:
        visible=tag in ['closure','waterseal'] or (tag=='cooler' and u>.48)
        if tag=='waterseal':pos[1]=18*(1-smooth((u-.08)/.30));highlight=True
        if tag=='cooler':pos[1]=42*(1-smooth((u-.5)/.42))
    elif index==4:
        visible=tag in COPPER
        if tag=='backbolts':pos[1]=-22*(1-smooth((u-.12)/.62));highlight=True
    elif index==5:
        visible=tag in MAG
        if tag in ['yoke','outermag','centermag']:pos[1]=-40*(1-smooth((u-.10)/.78))
        half=tag in ['cooler','closure'];highlight=tag in ['outermag','centermag']
    elif index==6:
        visible=tag in CONNECTED
        if tag=='yokebolt':pos[1]=-18*(1-smooth((u-.08)/.32));highlight=True
        if tag=='fittings':pos[1]=-20*(1-smooth((u-.30)/.35));highlight=True
        if tag in ['hvbolt','hook']:pos[1]=-15*(1-smooth((u-.67)/.28));highlight=True
    elif index==7:
        visible=tag in SPACER
        if tag in ['spacer','headseal']:pos[1]=-42*(1-smooth((u-.34)/.59))
        if tag=='headseal':pos[1]+=17*(1-smooth((u-.05)/.25));highlight=True
    elif index==8:
        visible=tag in HEAD
        if tag=='headbolts':pos[1]=-30*(1-smooth((u-.1)/.7));highlight=True
    elif index==9:
        visible=tag in ISOLATED
        if tag=='upper62':pos[1]=-16*(1-smooth((u-.08)/.31));highlight=True
        if tag=='isolator':pos[1]=-30*(1-smooth((u-.43)/.5));highlight=True
    elif index==10:
        visible=tag in ['base','sleeves','lower62']
        if tag=='sleeves':pos[1]=-22*(1-smooth((u-.05)/.48));highlight=True
        if u>.60:half=tag=='base'
    elif index==11:
        visible=tag in BASE
        if tag in ['base','lower62','sleeves']:pos[1]=-32*(1-smooth((u-.08)/.48))
        if tag=='basebolts':visible=u>.58;pos[1]=-30*(1-smooth((u-.62)/.32));highlight=True
        half=u<.60 and tag in ['base','isolator']
    elif index==12:
        visible=tag in MOUNTED and tag!='services'
        if tag in ['kfcenter','kfseal']:pos[1]=-12*(1-smooth((u-.04)/.18));highlight=True
        if tag=='kftube':pos[1]=-40*(1-smooth((u-.22)/.29))
        if tag=='kfclamps':pos[2]=(-1 if r['v'][:,:,2].mean()<0 else 1)*30*(1-smooth((u-.52)/.24));highlight=True
        if tag=='kfbolts':visible=u>.74;pos[1]=-25*(1-smooth((u-.77)/.20));highlight=True
    elif index==13:visible=tag in ['cooler','waterseal','fittings']
    elif index==14:
        visible=tag in MOUNTED|{'shieldtube'}
        half=tag not in ['outermag','centermag','services','hook','fittings'];trim=True
    elif index==15:
        visible=tag in TARGETED
        if tag=='target':pos[1]=28*(1-smooth((u-.05)/.26));highlight=True
        if tag=='clamp':visible=u>.29;pos[1]=40*(1-smooth((u-.34)/.28))
        if tag=='targetbolts':visible=u>.64;pos[1]=28*(1-smooth((u-.68)/.28));highlight=True
    elif index==16:
        visible=tag in ALL
        if tag=='shieldtube':pos[1]=100*(1-smooth((u-.03)/.27))
        if tag=='lowerbolts':
            visible=u>.29;a=r['anchor'].copy();a[1]=0;a/=np.linalg.norm(a);pos=a*15*(1-smooth((u-.32)/.16));highlight=True
        if tag=='darkcap':visible=u>.46;pos[1]=22*(1-smooth((u-.5)/.22))
        if tag=='upperbolts':
            visible=u>.73;a=r['anchor'].copy();a[1]=0;a/=np.linalg.norm(a);pos=a*12*(1-smooth((u-.77)/.2));highlight=True
    elif index==17:
        if u<.52:half=tag not in ['outermag','centermag','services','hook','fittings'];trim=True
        else:trim=False
    return visible,pos,orientation,origin,half,trim,highlight

def camera_pose(index,u):
    focus=np.array([0.,-23.,0]);scale=81;az=.8+.12*math.sin(u*math.pi*2);elev=.18;roll=0
    if index==0:focus[1]=-141;scale=185;az=.65+.7*u
    if index==1:focus[1]=-12;scale=120;az=.83;elev=.25;roll=90
    if index==2:focus[1]=-13;scale=85;az=.18;elev=-1.12
    if index==3:focus[1]=-10;scale=70;elev=1.0-.65*smooth((u-.45)/.4)
    if index==4:focus[1]=-15;scale=67;az=.6;elev=-.92
    if index==5:focus[1]=-23;scale=78;az=1.12;elev=.18
    if index==6:focus[1]=-27;scale=62;az=.70;elev=-.72
    if index==7:focus[1]=-30;scale=93;elev=.18
    if index==8:focus[1]=-29;scale=74;elev=-.82
    if index==9:focus[1]=-34;scale=84;elev=-.35
    if index==10:focus[1]=-61;scale=65;az=.5+(1.1-.5)*smooth((u-.55)/.2);elev=-.9+.70*smooth((u-.55)/.2)
    if index==11:focus[1]=-42;scale=99;az=.95;elev=-.38
    if index==12:focus[1]=-70;scale=92;az=.72;elev=-.3
    if index==13:focus[1]=-13;scale=58;az=.45;elev=-1.12
    if index==14:focus[1]=-42;scale=80;az=1.11;elev=.15
    if index==15:focus[1]=-10;scale=88;az=.65;elev=.72
    if index==16:focus[1]=-12;scale=138-37*smooth((u-.3)/.4);az=.5+.5*u;elev=.18
    if index==17:
        q=smooth((u-.56)/.32);focus[1]=-40-101*q;scale=80+105*q;az=1.1+.6*q;elev=.16
    direction=np.array([math.sin(az)*math.cos(elev),math.sin(elev),math.cos(az)*math.cos(elev)])
    camera.SetFocalPoint(*focus);camera.SetPosition(*(focus+1000*direction));camera.SetViewUp(0,1,0);camera.SetParallelScale(scale);camera.SetRoll(roll);camera.SetClippingRange(500,1600)

def flow_actor(points,color,radius=.30):
    p=vtk.vtkPoints();p.SetData(numpy_to_vtk(np.asarray(points,dtype=float),deep=True));lines=vtk.vtkCellArray();lines.InsertNextCell(len(points))
    for i in range(len(points)):lines.InsertCellPoint(i)
    poly=vtk.vtkPolyData();poly.SetPoints(p);poly.SetLines(lines);tube=vtk.vtkTubeFilter();tube.SetInputData(poly);tube.SetRadius(radius);tube.SetNumberOfSides(9);tube.CappingOn();tube.Update();m=vtk.vtkPolyDataMapper();m.SetInputConnection(tube.GetOutputPort());a=vtk.vtkActor();a.SetMapper(m);a.GetProperty().SetColor(*color);a.GetProperty().SetAmbient(.8);renderer.AddActor(a);return a
flow_paths=[];flow_lines=[];flow_dots=[]
for sign in [1,-1]:
    ang=np.linspace(0,sign*math.pi,130);arc=np.column_stack((13.55*np.cos(ang),np.full(len(ang),-5),13.55*np.sin(ang)))
    path=np.concatenate((np.array([[13.55,-35.5,0],[13.55,-22.5,0],[13.55,-9,0]]),arc,np.array([[-13.55,-9,0],[-13.55,-22.5,0],[-13.55,-35.5,0]])))
    flow_paths.append(path);flow_lines.append(flow_actor(path,(.3,.83,.98)))
    for n in range(7):
        s=vtk.vtkSphereSource();s.SetRadius(.55);s.SetThetaResolution(10);s.SetPhiResolution(8);m=vtk.vtkPolyDataMapper();m.SetInputConnection(s.GetOutputPort());a=vtk.vtkActor();a.SetMapper(m);a.GetProperty().SetColor(.95,1,1);a.GetProperty().SetAmbient(.9);renderer.AddActor(a);flow_dots.append(a)

def font(n,b=False):return ImageFont.truetype('C:/Windows/Fonts/'+('segoeuib.ttf' if b else 'segoeui.ttf'),n)
TITLE,BODY,SMALL,TINY=font(40,True),font(28),font(23),font(18)
def wrap(draw,text,xy,width,ft,fill):
    x,y=xy;line=''
    for word in text.split():
        trial=(line+' '+word).strip()
        if line and draw.textlength(trial,font=ft)>width:draw.text((x,y),line,font=ft,fill=fill);y+=ft.size+10;line=word
        else:line=trial
    draw.text((x,y),line,font=ft,fill=fill);return y+ft.size+10
def frame(index,t,duration):
    u=t/duration
    for r in records:
        visible,pos,ori,org,half,trim,highlight=scene(index,u,r);a=r['actor'];a.SetVisibility(visible)
        if not visible:continue
        variant=('half' if half else '')+('trim' if trim else '') or 'full'
        if variant not in r['variants']:r['variants'][variant]=clipped(r['poly'],half,trim)
        if r['current']!=variant:r['mapper'].SetInputData(r['variants'][variant]);r['current']=variant
        a.SetOrigin(*org);a.SetOrientation(*ori);a.SetPosition(*pos)
        c=np.array(color(r['file'],r['role']))
        if highlight and 'bolt' in r['role']:c=c*.6+np.array([1,.82,.3])*.4
        a.GetProperty().SetColor(*c)
    for a in flow_lines:a.SetVisibility(index==13)
    for j,a in enumerate(flow_dots):
        a.SetVisibility(index==13)
        if index==13:
            path=flow_paths[j//7];a.SetPosition(*path[(int(t*18)+(j%7)*19)%len(path)])
    camera_pose(index,u);window.Render();capture.Modified();capture.Update();pixels=vtk_to_numpy(capture.GetOutput().GetPointData().GetScalars()).reshape(H,W-PANEL,3);scene_image=Image.fromarray(np.flipud(pixels))
    im=Image.new('RGB',(W,H),'#101b2a');im.paste(scene_image,(PANEL,0));draw=ImageDraw.Draw(im);draw.rectangle((0,0,PANEL-1,H),fill='#1b2b3f')
    draw.text((30,30),'ADVANCED TINKERING / ORIGINAL',font=TINY,fill='#a9c2d7')
    y=wrap(draw,chapters[index]['title'],(30,100),395,TITLE,'#f2f7fb')+38
    for text in chapters[index]['bullets']:
        draw.ellipse((32,y+10,39,y+17),fill='#66c9ec');y=wrap(draw,text,(55,y),370,BODY,'#d8e8f3')+28
    for n,(c,txt) in enumerate([('#d78c50','Copper cooling parts'),('#cd4c50','Outer magnets: S forward'),('#4c7bd1','Center stack: N forward'),('#e6ddbf','PTFE insulation'),('#3e78c9','Reference coolant hoses')]):
        yy=782+n*35;draw.rectangle((30,yy+5,43,yy+19),fill=c);draw.text((56,yy),txt,font=TINY,fill='#d5e5f1')
    wrap(draw,'Study reconstruction. Missing hardware and utility dimensions are labeled in the CAD report.',(30,979),395,TINY,'#e8cc7a')
    def project(point):renderer.SetWorldPoint(*np.asarray(point,dtype=float),1);renderer.WorldToDisplay();x,y,z=renderer.GetDisplayPoint();return x+PANEL,H-y,z
    def label(text,point,xy,c='#e5f0fa'):
        x,y,z=project(point);draw.line((x,y,xy[0],xy[1]+15),fill=c,width=2);draw.ellipse((x-4,y-4,x+4,y+4),fill=c)
        draw.rounded_rectangle((xy[0]-7,xy[1]-3,xy[0]+draw.textlength(text,font=SMALL)+7,xy[1]+34),radius=5,fill='#17283b');draw.text(xy,text,font=SMALL,fill=c)
    def note(text):draw.text((PANEL+28,78),text,font=TINY,fill='#c9d7e4')
    # Labels use exact fitted coordinates, with the same display translations as the actors.
    if index==0:
        label('Target end',[0,15,0],(1040,110));label('Reference KF16 tube',[0,-200,10],(1300,720));label('Atmospheric service tails',[3,-295,0],(760,925),'#b5d8ff')
    elif index==1:
        note('DISPLAY EXPLOSION ONLY / SHIELD TUBE, FASTENERS AND UTILITIES HIDDEN')
        for txt,p,xy in [('Bottom body',[0,-145,0],(500,180)),('PTFE ring',[0,-103,0],(710,850)),('Spacer',[0,-62,0],(870,190)),('Yoke',[0,-27.5,0],(1000,850)),('Magnet pack',[0,0,25],(1080,170)),('Copper closure',[0,25,0],(1210,850)),('Copper cooler',[0,65,0],(1370,190)),('Target clamp',[0,100,0],(1510,850)),('Dark-space shield',[0,130,0],(1580,140))]:label(txt,p,xy)
    elif index==2:
        note('COPPER CLOSURE FLIPPED FOR INSPECTION / NOT AN INSTALLATION ORIENTATION')
        label('Cooling-body rear face',[52,-9,12],(1320,170),'#f2b881');label('Closure mating face',[-52,-22.5,-20],(570,820),'#f2b881')
    elif index==3:
        note('INSTALLED SEAL ENVELOPES / NO ELASTOMER DEFORMATION SIMULATION')
        shift=18*(1-smooth((u-.08)/.30));label('Inner water seal',[8.675,-9.725+shift,0],(570,190),'#b3e3bd');label('Outer water seal',[18.425,-9.725+shift,0],(1330,850),'#b3e3bd')
    elif index==4:
        p=next(r for r in records if r['role']=='backbolts')['anchor'].copy();p[1]+=-22*(1-smooth((u-.12)/.62));label('One of twelve rear screws',p,(1160,865),'#f4d48a')
    elif index==5:
        note('COPPER PARTS SECTIONED / MAGNETS RETAINED WHOLE')
        shift=-40*(1-smooth((u-.10)/.78));label('Twelve outer rods',[25,-8+shift,0],(1340,185),'#f18f91');label('Stack of two center discs',[0,-12.5+shift,0],(570,820),'#a7c6ff')
    elif index==6:
        label('Yoke retaining screw',[0,-28,-13.55],(580,185),'#f1d58a');label('Coolant fitting clearances',[13.55,-32,0],(1330,840),'#b4d8ff');label('Separate electrical contact',[0,-24,13.55],(1300,180),'#f2b881')
    elif index==7:
        shift=-42*(1-smooth((u-.34)/.59));label('76 x2 outer face seal',[39.425,-12.725+shift,0],(580,185),'#b3e3bd');label('Spacer moves around the yoke',[36,-24+shift,0],(1300,850))
    elif index==8:
        p=next(r for r in records if r['role']=='headbolts')['anchor'].copy();p[1]+=-30*(1-smooth((u-.1)/.7));label('Head-attachment screw pattern',p,(1050,870),'#f4d48a')
    elif index==9:
        shift=-30*(1-smooth((u-.43)/.5));label('Main PTFE ring',[38,-43.5+shift,0],(1320,850),'#eee1b9');label('62 x2 spacer-face seal',[32.425,-40.275,0],(570,185),'#b3e3bd')
    elif index==10:
        if u>.60:note('BOTTOM BODY SECTIONED TO EXPOSE THE SLEEVE SHANKS')
        p=next(r for r in records if r['role']=='sleeves')['anchor'].copy();p[1]-=22*(1-smooth((u-.05)/.48));label('One shoulder sleeve / twelve total',p,(1070,875),'#eee1b9')
    elif index==11:
        label('Second 62 x2 face seal',[32.425,-46.725,0],(570,185),'#b3e3bd');label('Independent insulated base screws',[38,-69.5,10],(1240,865),'#f4d48a')
    elif index==12:
        note('LONG TUBE CROPPED FOR JOINT INSPECTION / PURCHASED PARTS ARE REFERENCES')
        label('Two original clamp halves',[22,-82,0],(1290,850));label('KF16 centering and seal',[10,-76,0],(580,190),'#b3e3bd')
    elif index==13:
        note('CLOSURE AND MAGNET PACK HIDDEN / MOVING DOTS ARE NOT CFD RESULTS')
        label('Supply port',[13.55,-15,0],(1320,185),'#a6e5fb');label('Opposite return port',[-13.55,-15,0],(580,850),'#a6e5fb');label('Continuous annulus',[0,-5,13.55],(1330,850),'#a6e5fb')
    elif index==14:
        note('SECTIONED PRESSURE-REGION EXPLANATION / NO CHAMBER OR FLOW SIMULATION')
        label('Water channel',[13.55,-5,0],(1300,160),'#a6e5fb');label('Dry atmospheric interior',[0,-38,8],(570,425),'#b3e3bd');label('Vacuum outside sealed stack',[47.5,-25,0],(1320,640),'#e6d5a3');label('Air connection down the tube',[0,-96,-4],(880,920),'#b3e3bd')
    elif index==15:
        label('Target seats on copper',[0,0,22],(1280,170));label('Separate front clamp screws',[38.637,1,10.353],(1230,870),'#f4d48a')
    elif index==16:
        label('Grounded outer tube',[38,-20,32],(1310,170));label('Three lower radial screws',[0,-60.262,50.8],(570,870),'#f4d48a')
        if u>.48:label('Top dark-space shield',[0,15,30],(1260,850))
    elif index==17:
        note('COMPLETE ORIGINAL-DESIGN RECONSTRUCTION / SOURCE AND REFERENCE DETAILS DISTINGUISHED')
        if u<.52:label('Actual CAD cutaway',[0,-20,20],(1270,850))
        else:label('120 resolved solid instances',[0,-25,35],(1260,190))
    draw.text((PANEL+28,30),'ACTUAL SOLIDWORKS GEOMETRY / EDUCATIONAL ASSEMBLY ANIMATION',font=TINY,fill='#a8c0d3')
    draw.text((PANEL+28,H-53),f'{index+1:02} / {len(chapters):02}    '+chapters[index]['title'],font=TINY,fill='#b2c8d9')
    draw.rectangle((PANEL,H-10,W-1,H-1),fill='#273b50');draw.rectangle((PANEL,H-10,PANEL+int((W-PANEL)*u),H-1),fill='#58c5e9')
    return np.asarray(im)

def stamp(t):
    n=round(t*1000);return f'{n//3600000:02}:{n//60000%60:02}:{n//1000%60:02},{n%1000:03}'
def coverage():
    detail={'cooler':2,'closure':2,'waterseal':3,'backbolts':4,'outermag':5,'centermag':5,'yoke':5,'yokebolt':6,'hvbolt':6,'hook':6,'fittings':6,'spacer':7,'headseal':7,'headbolts':8,'isolator':9,'upper62':9,'sleeves':10,'base':11,'lower62':11,'basebolts':11,'kfclamps':12,'kftube':12,'kfcenter':12,'kfseal':12,'kfbolts':12,'services':14,'target':15,'clamp':15,'targetbolts':15,'shieldtube':16,'darkcap':16,'upperbolts':16,'lowerbolts':16}
    assert set(detail)==set(N)
    with (OUT/'Component video coverage.csv').open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.writer(f);w.writerow(['Component instance','Part file','Functional role','Detailed chapter','Chapter title'])
        for r in records:
            i=detail[r['role']];w.writerow([r['name'],r['file'],r['role'],i+1,chapters[i]['title']])
if __name__=='__main__':
    coverage();print('Loaded actual assembly:120 instances;153824 triangles;coverage assigned.',flush=True)
    if 'preview' in sys.argv:
        for i in range(len(chapters)):
            Image.fromarray(frame(i,13,20)).save(OUT/f'preview-{i:02}.jpg')
        for t in [2,9,19]:Image.fromarray(frame(5,t,20)).save(OUT/f'magnet-motion-{t:02}.jpg')
        for t in [2,10,19]:Image.fromarray(frame(16,t,20)).save(OUT/f'shield-motion-{t:02}.jpg')
        print('Chapter and motion previews saved.',flush=True);window.Finalize();sys.exit()
    durations=[];chunks=[];params=None
    for i in range(len(chapters)):
        with wave.open(str(OUT/f'voice-{i:02}.wav'),'rb') as f:p=f.getparams();raw=f.readframes(p.nframes)
        if params is None:params=p
        assert params[:3]==p[:3]
        duration=math.ceil((p.nframes/p.framerate+1.8)*FPS)/FPS;durations.append(duration);lead=int(.5*p.framerate);tail=round(duration*p.framerate)-lead-p.nframes;chunks.append(bytes(lead*p.sampwidth*p.nchannels)+raw+bytes(tail*p.sampwidth*p.nchannels))
    with wave.open(str(OUT/'narration.wav'),'wb') as f:
        f.setparams(params)
        for chunk in chunks:f.writeframes(chunk)
    writer=imageio_ffmpeg.write_frames(str(OUT/'silent.mp4'),(W,H),fps=FPS,codec='libx264',quality=8,macro_block_size=1,output_params=['-preset','fast']);writer.send(None)
    elapsed=0;timeline=[];subtitles=[];render_start=time.perf_counter()
    for i,(ch,duration) in enumerate(zip(chapters,durations)):
        timeline.append((elapsed,ch['title']));sentences=[s.strip()+'.' for s in ch['speech'].split('.') if s.strip()];length=sum(map(len,sentences));start=elapsed+.5
        for s in sentences:
            end=start+(duration-1.8)*len(s)/length;subtitles.append(f'{len(subtitles)+1}\n{stamp(start)} --> {stamp(end)}\n{s}\n');start=end
        for n in range(round(duration*FPS)):writer.send(frame(i,n/FPS,duration))
        elapsed+=duration;print(f'{i+1:02}/{len(chapters)} rendered: {ch["title"]} ({duration:.1f}s)',flush=True)
    writer.close();window.Finalize();(OUT/'subtitles.srt').write_text('\n'.join(subtitles),encoding='utf8')
    metadata=';FFMETADATA1\ntitle=Advanced Tinkering original magnetron - detailed full assembly\n';transcript=[]
    for i,(start,title) in enumerate(timeline):
        end=timeline[i+1][0] if i+1<len(timeline) else elapsed;metadata+=f'[CHAPTER]\nTIMEBASE=1/1000\nSTART={round(start*1000)}\nEND={round(end*1000)}\ntitle={title}\n';transcript.extend([f'{int(start)//60}:{int(start)%60:02} {title}',chapters[i]['speech'],''])
    (OUT/'chapters.ffmeta').write_text(metadata,encoding='utf8');(OUT/'Detailed assembly video transcript.txt').write_text('\n'.join(transcript),encoding='utf8')
    subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-y','-v','error','-i',str(OUT/'silent.mp4'),'-i',str(OUT/'narration.wav'),'-i',str(OUT/'subtitles.srt'),'-i',str(OUT/'chapters.ffmeta'),'-map','0:v','-map','1:a','-map','2:s','-map_metadata','3','-map_chapters','3','-c:v','copy','-c:a','aac','-b:a','160k','-c:s','mov_text','-movflags','+faststart',str(OUT/'Advanced Tinkering original magnetron - detailed full assembly.mp4')],check=True)
    (OUT/'Render summary.json').write_text(json.dumps({'runtime_seconds':elapsed,'chapters':len(chapters),'components':len(records),'roles':N,'resolution':[W,H],'fps':FPS,'render_seconds':time.perf_counter()-render_start},indent=2))
    print(f'COMPLETE: {elapsed:.1f}s video, render {time.perf_counter()-render_start:.1f}s',flush=True)
