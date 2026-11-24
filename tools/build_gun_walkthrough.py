"""Complete R06 gun explanation using all 141 actual CAD component instances.

Creates silent and narrated 1080p versions of identical detailed shots.
Run with --preview for contact sheets, or without arguments for the movies.
"""
from pathlib import Path
import json,math,sys,time,wave,subprocess,hashlib,csv
import numpy as np
import vtk,imageio_ffmpeg
from PIL import Image,ImageDraw,ImageFont
from vtk.util.numpy_support import vtk_to_numpy
from build_assembly_walkthrough import Renderer as Studio, smooth, ramp

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'media/gun-complete-walkthrough';OUT.mkdir(exist_ok=True)
WORK=OUT/'render';WORK.mkdir(exist_ok=True);W,H,FPS=1920,1080,24
META=json.loads((ROOT/'chamber-design/coolant-fitting-r06/R06 component register.json').read_text())
GUN=[i for i,q in enumerate(META) if q['group']=='gun']
def role(*names):return [i for i in GUN if META[i]['role'] in {'gun_'+n for n in names}]
def name(prefix):return next(i for i in GUN if META[i]['name'].startswith(prefix))
def center(i):b=META[i]['bbox_mm'];return (np.array(b[:3])+b[3:])/2
def combine(*groups):return list(dict.fromkeys(i for g in groups for i in g))
def ids(*numbers):return [name('Gun '+str(n)+' ') for n in numbers]
def radvec(i,length):
    p=center(i);v=np.array([p[0],p[1],0.]);return v/max(np.linalg.norm(v),1)*length

SHOTS=[]
def shot(key,label,detail,primary,context=(),mode='lift',moves=None,az=-62,el=24,section=None,fit_primary=False,seconds=12,speech=None):
    SHOTS.append(dict(key=key,label=label,detail=detail,primary=list(primary),context=list(context),mode=mode,moves=moves or {},az=az,el=el,section=section,fit_primary=fit_primary,minimum_seconds=seconds,speech=speech or detail))

def zmove(groups,offsets):
    return {str(i):[0,0,z] for g,z in zip(groups,offsets) for i in g}
def radial(group,length,z=0):return {str(i):(radvec(i,length)+[0,0,z]).tolist() for i in group}
def merge(*maps):return {k:v for d in maps for k,v in d.items()}

C=role('cooler');B=role('closure');Y=role('yoke');SP=role('spacer');BASE=role('base');PT=role('isolator')
TARGET=role('target');CLAMP=role('clamp');SEALS=role('waterseal');HEADSEAL=role('headseal');ISOSEALS=role('upper62','lower62')
CUPS=role('cups');BASEB=role('basebolts');HEADB=role('headbolts');BACKB=role('backbolts');TB=role('targetbolts')
MAG=role('outermag','centermag');HOSE=role('hoses');FITT=role('fittings');STEM=role('kftube');COAX=role('coax')
RFHOT=role('rfhot');RFGND=role('rfground');SHIELD=role('shieldtube');DARK=role('darkcap')
HEAD=combine(C,B,Y,SP,BASE,PT,TARGET,CLAMP,SEALS,HEADSEAL,ISOSEALS,MAG)

shot('complete','R06 sputter gun','141 CAD components • target, cooling, magnets, insulation, services and shields',GUN,mode='orbit',seconds=14,
 speech='This is the complete current R zero six gun, including all one hundred and forty one modeled component instances. We will open it, examine the small parts as well as the main bodies, follow its connections, and assemble it again.')
shot('exploded','Complete exploded assembly','All component instances remain present; offsets reveal the assembly hierarchy',GUN,mode='overall',seconds=18,
 speech='The exploded view separates the actual component solids. The target and clamp sit at the front, followed by the cooling and magnetic head, spacer, insulation and grounded body. The service tube carries the hoses and coax. Fasteners and seals remain individual parts.')
shot('front_guard','Dark-space cap','Grounded front guard surrounds the live target clamp',DARK,combine(SHIELD,CLAMP,TARGET),moves=zmove([DARK],[-30]),el=-18,
 speech='The front dark-space cap belongs to the grounded shield. It surrounds the live target clamp while leaving the target opening exposed. We separate the cap to show its actual seating relationship and the gap to the live assembly.')
shot('cap_screws','Front guard screws ×6','Radial screws attach the dark-space cap to the grounded shield',role('upperbolts'),combine(DARK,SHIELD),moves=radial(role('upperbolts'),22),el=-12,
 speech='Six small radial screws secure the front guard. Each screw follows its own radial receiving axis. All six instances are shown; these are separate from the twelve screws that hold the target clamp.')
shot('shield','Grounded shield tube','Surrounds the head; the inner pressure boundary is formed by the sealed body stack',SHIELD,combine(HEAD,DARK),moves={str(i):[-145,0,0] for i in SHIELD},
 speech='The grounded shield tube surrounds the source head. Moving it aside exposes the internal stack without changing any part geometry. This outer shield is not itself the complete atmosphere-to-vacuum seal; the face seals inside the body provide that boundary.')
shot('shield_screws','Shield-to-body screws ×3','Three radial screws connect the shield tube to the grounded body',role('lowerbolts'),combine(SHIELD,BASE),moves=radial(role('lowerbolts'),22),
 speech='Three further radial screws attach the shield tube to the grounded body. They are a different size and position from the six front-cap screws. Their radial approach is shown with the actual receiving geometry.')
shot('target_stack','Target and floating clamp','Target seats against copper; the pressure lip retains its front edge',combine(TARGET,CLAMP,TB),C,moves=zmove([TARGET,CLAMP,TB],[-22,-45,-62]),el=-25,seconds=16,
 speech='The target sits against the copper cooling body. The revised clamp presses at its outer front edge. The twelve screws retain the floating clamp arrangement. The animation separates the target, clamp and screws so their order and contact faces can be seen.')
shot('target','Aluminium target','Ø50.8 × 3.175 mm • the consumable surface from which material is sputtered',TARGET,combine(C,CLAMP),moves=zmove([TARGET],[-26]),el=-30,
 speech='The current consumable is a fifty point eight millimetre diameter aluminium target, three point one seven five millimetres thick. Its back contacts the copper body. Its exposed front is the surface from which the discharge removes material.')
shot('clamp_lip','R05 target clamp','Pressure lip bears on the target edge; central aperture exposes the target face',CLAMP,TARGET,moves=zmove([CLAMP],[-25]),section={'normal':[0,1,0],'origin':[0,0,0]},el=-8,
 speech='A section through the actual revised clamp reveals its pressure lip and aperture. The lip retains the thicker target at its edge. This is the R zero five clamp retained in R zero six, not the earlier clamp for a two millimetre target.')
shot('target_fasteners','Target clamp screws ×12','M3 ×10 screws enter the copper body through the clamp counterbores',TB,combine(C,CLAMP,TARGET),moves=zmove([TB],[-26]),mode='fasteners',el=-24,
 speech='All twelve target screws are modeled individually. Their heads sit in the clamp counterbores and their shanks enter the copper receiving holes. The current nominal length is M three by ten. Thread envelopes and illustrative turning do not specify an installation torque.')
shot('copper','Copper cooling body','Conducts heat away from the target and contains the coolant passage',C,combine(TARGET,B),moves=zmove([TARGET,B],[-24,28]),el=36,
 speech='The copper cooling body supports the target and transfers heat toward its internal coolant passage. We remove the backplate and target to expose both interfaces. The copper shape is the current CAD solid, including its magnet wells, drilled ports and screw holes.')
shot('water_channel','Coolant passage · section','Water passage stays separate from the magnet wells and surrounding vacuum',C,combine(B,SEALS),moves=zmove([B,SEALS],[25,12]),section={'normal':[0,1,0],'origin':[0,0,0]},el=22,seconds=16,
 speech='This section opens the actual copper passage rather than inventing an internal channel. The coolant space lies between its sealing lands. It is separated from the magnet wells and the chamber vacuum. The routing geometry does not by itself establish flow or thermal performance.')
inner=sorted(SEALS,key=lambda i: META[i]['bbox_mm'][3]-META[i]['bbox_mm'][0])[0];outer=next(i for i in SEALS if i!=inner)
shot('water_rings','Water O-rings ×2','Inner and outer face rings contain the coolant at the backplate interface',SEALS,combine(C,B),moves=zmove([[inner],[outer],B],[10,19,32]),el=45,
 speech='Two individual O rings seal the coolant interface: an inner ring and an outer ring. Each seats on its own land between the copper parts. Both are shown separately. Their installed CAD shapes represent compression; this is not an elastomer deformation simulation.')
shot('backplate','R06 copper backplate','Closes the cooling passage and carries the two revised M5 coolant ports',B,combine(C,SEALS),moves=zmove([B],[32]),el=42,
 speech='The copper backplate closes the cooling body and carries the two revised coolant ports. In R zero six each port has a three millimetre flow passage and a four point two millimetre tap-drill feature. M five threading is specified, but helical teeth are not modeled.')
shot('backplate_screws','Backplate screws ×12','M3 ×16 fasteners close the copper backplate joint',BACKB,combine(C,B,SEALS),moves=zmove([BACKB],[26]),mode='fasteners',el=42,
 speech='Twelve nominal M three by sixteen screws close the backplate joint. Watch the separate fastener pattern move toward the existing copper receiving holes. This set closes the copper assembly and is distinct from the longer spacer attachment screws.')
shot('yoke','Steel magnetic return yoke','Rear magnetic return path; openings clear the coolant fittings and live terminal',Y,combine(MAG,B),moves=zmove([Y],[36]),el=45,
 speech='The steel yoke sits behind the magnets and provides the magnetic return path. Its two larger openings provide clearance around the coolant fittings, while another passage accommodates the live terminal connection. The yoke separates here so those interfaces are visible.')
shot('yoke_screw','Yoke screw','Single M4 ×10 screw at the modeled yoke attachment',role('yokebolt'),combine(Y,B),moves=zmove([role('yokebolt')],[24]),mode='fasteners',el=40,
 speech='This small M four by ten fastener is the modeled yoke attachment. It is easy to miss in a whole-gun view, so it has its own close-up. The source thread-envelope contact is retained; this view does not resolve its manufacturing detail.')
shot('centre_magnets','Centre magnets ×2','Two Ø20 ×10 mm discs form the centre stack; north pole faces the target',role('centermag'),combine(C,Y),moves=zmove([[role('centermag')[0]],[role('centermag')[1]],Y],[28,44,72]),el=40,
 speech='The centre stack contains two twenty by ten millimetre N forty two discs. They occupy the centre well between the copper head and yoke. Their target-facing polarity is north. The two individual discs separate so the stack is visible.')
shot('outer_magnets','Outer magnets · 12 stacks, 24 discs','Two Ø6 ×10 mm discs per position; outer target-facing poles oppose the centre',role('outermag'),combine(C,Y),moves=zmove([Y],[72])|{str(i):[0,0,30+(18 if center(i)[2]>156 else 0)] for i in role('outermag')},el=66,seconds=16,
 speech='The outer ring contains twelve positions, each with two six by ten millimetre N forty two discs: twenty four individual outer magnets. Each stack seats in its own blind well. Their south poles face the target, opposite to the centre stack.')
shot('magnetic_layout','Magnetic circuit','Opposed centre and outer poles shape the field above the target; steel returns the flux',combine(MAG,Y),combine(C,TARGET),mode='magnetic',el=-28,seconds=14,
 speech='Together, the centre and outer poles shape the field near the target. The steel yoke forms the return path. Copper and target context are made translucent in this explanatory view. This shows the magnetic construction, not a simulated plasma or a proof of balanced operation.')
shot('spacer','Live spacer','Connects the copper head to the insulated body stack',SP,combine(C,HEADSEAL,PT),moves=zmove([SP,PT],[32,65]),section={'normal':[0,1,0],'origin':[0,0,0]},el=14,
 speech='The spacer joins the copper head to the insulation and grounded-body stack. Its shoulder, central opening and receiving holes are retained from the source geometry. The spacer belongs to the live side, so the later insulating interfaces are important.')
shot('head_seal','Copper-to-spacer O-ring','Face seal closes the copper / spacer interface',HEADSEAL,combine(C,SP),moves=zmove([HEADSEAL,SP],[18,42]),el=36,
 speech='This separate face O ring lies between the copper head and the spacer. It is not one of the two coolant rings. It seals a different interface in the atmosphere-to-vacuum boundary, and is therefore shown as its own part.')
shot('head_fasteners','Head-to-spacer screws ×12','Long M3 ×35 screws attach the spacer to the copper head',HEADB,combine(SP,C,HEADSEAL),moves=zmove([HEADB],[32]),mode='fasteners',el=40,
 speech='Twelve long M three by thirty five screws connect the spacer and copper head. All twelve are visible as separate instances. This pattern is independent of the backplate screws and the insulated screws that later connect the grounded body.')
shot('ptfe_ring','Main PTFE isolator','Separates live spacer from grounded body while carrying the face-seal stack',PT,combine(SP,BASE,ISOSEALS),moves=zmove([PT,BASE],[28,65]),section={'normal':[0,1,0],'origin':[0,0,0]},el=16,
 speech='The main PTFE isolator sits between the live spacer and grounded body. Its faces participate in the sealing stack while its insulating material separates the two metal bodies. We section the actual part to expose the steps and mating surfaces.')
shot('isolator_rings','Isolator face O-rings ×2','One ring seals to the spacer; the other seals to the grounded body',ISOSEALS,combine(PT,SP,BASE),moves=zmove([role('upper62'),PT,role('lower62'),BASE],[12,26,40,65]),el=30,
 speech='Two further O rings seal the two sides of the main isolator. One belongs to the spacer-side interface; the other belongs to the grounded-body interface. Keeping these separate explains why the large PTFE ring and the elastomer seals have different jobs.')
cup=CUPS[0];bolt=min(BASEB,key=lambda i:np.linalg.norm(center(i)[:2]-center(cup)[:2]));cy=float(center(cup)[1])
shot('ptfe_sleeve','PTFE screw shoulder sleeve','One machined part: shank sleeve, bearing shoulder, recessed-head guard and outward lip',[cup],[bolt],moves=zmove([[cup],[bolt]],[0,30]),el=30,seconds=15,
 speech='This is one of the small PTFE screw insulators. The shank sleeve, bearing shoulder, screw-head guard and outward lip are one continuous part. There is no separate cap or guard fastener. The recessed opening remains accessible to the screw tool.')
shot('sleeve_section','Insulated screw · section','Live metal screw enters the spacer; PTFE separates its shank and head from grounded metal',[cup,bolt],combine(BASE,PT,SP),moves=zmove([[bolt]],[23]),section={'normal':[0,1,0],'origin':[0,cy,0]},fit_primary=True,el=15,az=-85,seconds=16,
 speech='A section through one real fastener position shows the metal screw inside its PTFE sleeve. The screw threads into the live spacer. The sleeve separates its shank and recessed head from the grounded body. The small insulator must be understood together with the main PTFE ring.')
shot('all_sleeves','PTFE screw sleeves ×12','All twelve sleeves fit their corresponding body pockets; lips remain outside the holes',CUPS,BASE,moves=zmove([CUPS],[35]),el=52,
 speech='Now all twelve screw sleeves are shown in their actual positions. Each enters a corresponding body pocket from the head side. The larger lip stays outside the opening. This view includes every sleeve, rather than replacing the repeated pattern with a single example.')
shot('insulated_screws','Insulated body screws ×12','Metal M3 ×35 screws pass through the sleeves and main isolator into the live spacer',BASEB,combine(CUPS,BASE,PT,SP),moves=zmove([BASEB],[35]),mode='fasteners',el=44,
 speech='These twelve metal M three by thirty five screws pass through the insulating sleeves and into the spacer. They are metal load-carrying screws, not PTFE screws. The sleeves stay seated as the screws approach their receiving holes. Actual preload and PTFE creep remain engineering considerations.')
shot('body','Grounded body / Boden','Supports the service-tube joint, shield attachment and internal RF ground carrier',BASE,combine(PT,SP),moves=zmove([BASE],[38]),section={'normal':[0,1,0],'origin':[0,0,0]},el=18,
 speech='The grounded body, also called the Boden in the source files, carries the service-tube joint, shield attachment and internal ground carrier. Its cone, pockets and seal faces are all part of the actual CAD solid. The live spacer is isolated from it by the PTFE stack.')
shot('ground_carrier','RF ground carrier and saddle','Conductive carrier seats on the grounded body and supports the shield clamp',ids(130),combine(ids(129,131,132,133),BASE),moves={str(name('Gun 130 ')):[0,25,-15]},fit_primary=True,el=22,
 speech='The small conductive carrier supports the cable shield clamp. Its shaped saddle seats against the grounded body, and its mounting tab has a dedicated anchor. This close-up retains the actual formed geometry and attachment holes.')
shot('ground_anchor','Blind ground-anchor screw','M3 ×6 screw secures the carrier to the grounded body',ids(133),combine(ids(130),BASE),moves={str(name('Gun 133 ')):[0,13,-13]},fit_primary=True,mode='lift',el=20,
 speech='The M three by six ground-anchor screw enters a blind receiving pilot in the grounded body. It holds the carrier saddle at its contact seat. The animation follows the inclined attachment direction instead of treating this screw as an axial head-stack fastener.')
shot('shield_clamp','Coax shield spring clamp','Spring contact grips the exposed braid; jacket ends before the contact band',ids(129),combine(ids(130),ids(138)),moves={str(name('Gun 129 ')):[18,0,0]},section={'window':[184,208]},fit_primary=True,el=25,
 speech='The spring clamp contacts the exposed coax shield, where the outer jacket has ended. Its contact transfers the braid to the grounded carrier. The modeled spring shape and overlap are an installed envelope, not a spring-contact simulation.')
shot('clamp_hardware','Shield-clamp screw and nut','Small M3 ×4 screw and separate nut retain the clamp on its carrier',ids(131,132),ids(129,130),moves={str(name('Gun 131 ')):[0,-16,0],str(name('Gun 132 ')):[0,12,0]},el=30,
 speech='The shield clamp has its own small M three by four mounting screw and a separate nut. Both are shown here with the carrier and clamp. These are distinct from the larger blind screw that anchors the carrier to the body.')
shot('ground_path','RF shield / grounded return path','Coax shield → spring clamp → carrier → grounded body',combine(RFGND,ids(138)),BASE,mode='static',section={'window':[184,210]},fit_primary=True,el=26,seconds=14,
 speech='This is the modeled shield connection path: exposed braid to spring clamp, carrier and grounded body. The body still needs its external verified ground bond. The compression O ring around the service tube is not assumed to be the electrical bond.')
shot('live_standoff','Copper terminal stand-off','Passes through the yoke opening and contacts the copper backplate',ids(134),combine(B,Y),moves=zmove([ids(134)],[24]),fit_primary=True,el=25,
 speech='On the live side, a copper stand-off passes through the existing yoke opening and contacts the copper backplate. It brings the terminal connection to the rear of the yoke without inventing a slot through the magnetic return plate.')
shot('live_lug','M4 ring terminal','Centre conductor terminates in the lug; the eye seats on the live stand-off',ids(136),ids(134,135,140,141),moves=zmove([ids(136)],[16]),section={'window':[159,193]},fit_primary=True,el=28,
 speech='The centre conductor terminates at a ring lug. Its eye seats over the live stand-off and is retained by the terminal screw. The lug in the CAD is a catalogue-dimension study envelope; actual crimp deformation is not modeled.')
shot('live_screw','Live terminal screw','M4 ×20 screw clamps the lug and stand-off to the copper backplate',ids(135),combine(ids(134,136),B),moves=zmove([ids(135)],[26]),fit_primary=True,mode='fasteners',el=22,
 speech='The M four by twenty terminal screw clamps the ring lug and stand-off onto the copper backplate. This is the separate live attachment. Its nominal screw shaft and receiving bore do not provide a validated thread-strength or torque rating.')
shot('live_path','RF centre / live path','Centre conductor → lug → stand-off → backplate → target',combine(RFHOT,ids(140),B,C,TARGET),ids(141),mode='static',section={'window':[130,190]},el=-12,seconds=14,
 speech='Follow the live path from the coax centre to the ring lug, stand-off and copper backplate, then through the copper head to the target. This view isolates the actual conducting parts. The shield connection belongs to the other path.')
coaxlayers=ids(137,138,139,140)
shot('coax_layers','Coaxial cable · actual CAD section','Outer jacket / shield / dielectric / centre conductor',coaxlayers,mode='layers',section={'window':[438,442]},el=45,seconds=14,
 speech='The cable has four separately modeled layers. This short section is cut from the actual routed cable: outer jacket, shield, centre dielectric and centre conductor. They separate radially here and return to their concentric arrangement.')
for n,key,label,detail in [
 (137,'jacket','Coax outer jacket','Outer protection ends before the exposed shield contact band'),
 (138,'braid','Coax shield','Outer conductor contacts the grounded spring clamp'),
 (139,'dielectric','Coax centre dielectric','Separates the live centre conductor from the grounded shield'),
 (140,'conductor','Coax centre conductor','Carries the live RF connection to the ring terminal')]:
    shot(key,label,detail,ids(n),[i for i in coaxlayers if i!=name('Gun '+str(n)+' ')],mode='layers',moves={str(name('Gun '+str(n)+' ')):[7,0,0]},section={'window':[438,442]},el=42,speech=detail+'. The actual layer is shown on its own and then returned to the cable section; its geometry is not replaced by a generic diagram.')
shot('guard','Extra dielectric guard sleeve','Protects the centre tail beyond the shield termination',ids(141),ids(139,140,136),moves={str(name('Gun 141 ')):[-9,0,0]},section={'window':[174,191]},el=30,
 speech='The added dielectric guard sleeve covers the protected centre tail beyond the braid termination. It is a separate modeled part, distinct from the coax original centre dielectric. Its material and electrical rating remain to be selected and verified.')
shot('coax_termination','Complete coax termination','Shield terminates on ground; protected centre continues to the live copper terminal',combine(COAX,RFGND,RFHOT),combine(BASE,Y,B),mode='termination',section={'window':[157,222]},el=22,seconds=16,
 speech='The complete termination brings the two paths together without shorting them. The jacket stops before the braid clamp. The protected centre continues through its guard to the live lug. The grounded carrier and live terminal stay physically separate in the actual model.')
shot('service_tube','One-inch service tube and neck','Ø25.4 mm service tube carries two hoses and the coax through the head joint',STEM,combine(HOSE,COAX,BASE),moves={str(i):[75,0,0] for i in STEM},el=12,
 speech='The one-inch service tube carries the two coolant hoses and coax through the head joint. Its flange neck retains the source capture geometry and transitions to the twenty five point four millimetre outer tube. Moving it aside reveals the actual routed services.')
shot('head_joint','Head / service-tube joint','Separate flange capture, centering ring, O-ring and clamp halves',combine(STEM,role('kfcenter','kfseal','kfclamps','kfbolts')),BASE,moves=zmove([STEM,role('kfcenter'),role('kfseal')],[45,15,25]),section={'window':[202,275]},el=32,
 speech='The tube joins the head through a separate flange capture. The centering ring, O ring, clamp halves and six screws are individual modeled parts. This is the head joint, distinct from the chamber roof compression gland shown in the system video.')
shot('centering','Head-joint centering ring','Locates the mating joint and supports the O-ring',role('kfcenter'),combine(role('kfseal'),STEM,BASE),moves=zmove([role('kfcenter')],[16]),section={'window':[202,245]},el=35,
 speech='The centering ring locates the mating head joint and supports its seal. It is a separate part, not a feature merged into the service tube. The source uses a reference standard-form joint rather than an approved purchased assembly.')
shot('joint_seal','Head-joint O-ring','Seals the tube / body joint around the centering ring',role('kfseal'),combine(role('kfcenter'),STEM,BASE),moves=zmove([role('kfseal')],[20]),section={'window':[202,250]},el=36,
 speech='This O ring seals the service-tube joint around the centering ring. It is separate from the body face rings and the coolant seals previously shown. The actual installed CAD seal envelope is retained.')
shot('clamp_halves','Head clamp halves ×2','Two source clamp halves capture the mating flange geometry',role('kfclamps'),combine(STEM,BASE,role('kfcenter','kfseal')),moves={str(i):[0,30 if center(i)[1]>0 else -30,0] for i in role('kfclamps')},section={'window':[200,250]},el=28,
 speech='Two clamp halves capture the mating flange geometry. They approach from opposite sides of the joint, preserving their actual source profiles. The centering ring and O ring remain inside the captured stack.')
shot('clamp_bolts','Head clamp screws ×6','M5 ×20 screws close the clamp arrangement around the head joint',role('kfbolts'),combine(STEM,BASE,role('kfcenter','kfseal','kfclamps')),moves=zmove([role('kfbolts')],[26]),section={'window':[200,270]},mode='fasteners',el=36,
 speech='Six nominal M five by twenty screws close the clamp arrangement. All six are shown separately. Their heads and shafts follow the modeled holes, with thread helices intentionally absent from these nominal fastener solids.')
fitbody=[i for i in FITT if 'body' in META[i]['name']];collets=[i for i in FITT if 'release ring' in META[i]['name']]
shot('fitting_bodies','R06 coolant fitting bodies ×2','SMC KQG2S04-M5 bodies seat in the two backplate ports',fitbody,combine(B,Y),moves=zmove([fitbody],[26]),el=42,
 speech='Two S M C K Q G two S zero four M five fitting bodies seat in the revised backplate ports and pass through the yoke openings. They use their specified gasket seating interface. The visible envelopes do not expose invented internal valve details.')
shot('release_rings','Coolant release rings ×2','Separate collets provide the push-in tube interface',collets,fitbody,moves=zmove([collets],[15]),el=38,
 speech='Each coolant fitting has its own separately modeled release ring. These are not screw nuts or additional threaded adapters. They belong to the push-in tube interface; actual internal retention details follow the purchased fitting.')
shot('hoses','Coolant hoses ×2','Two routed 4 mm OD hoses carry supply and return through the service tube',HOSE,combine(FITT,STEM),moves={str(i):[45 if center(i)[0]>0 else -45,0,0] for i in HOSE},el=12,
 speech='The two four millimetre outside-diameter hoses are independent routed solids. They pass through the service tube to the two head fittings. Their existing bends and insertion segments are retained; the final tube material and allowable bend radius still need supplier confirmation.')
shot('hose_insert','Hose-to-fitting engagement','Tube ends slide axially into their fitting collets',combine(HOSE,FITT),combine(B,Y),moves=zmove([HOSE],[24]),section={'window':[153,205]},el=28,
 speech='This close-up follows the tube ends as they enter the fitting collets. The existing CAD includes an extended insertion segment for the R zero six fitting. The modeled engagement demonstrates the connection; it does not simulate hidden gripping teeth or establish a leak-tight joint.')
shot('water_path','Complete cooling connection','Supply hose → backplate port → copper passage → return port and hose',combine(HOSE,FITT,B,C,SEALS),Y,mode='water_path',section={'normal':[0,1,0],'origin':[0,0,0],'window':[136,205]},el=22,seconds=14,
 speech='The cooling connection now reads as one path: supply hose and fitting, backplate port, copper water passage, then the other port, fitting and return hose. The two water O rings contain that interface. The gun thermal and leak performance still require qualification.')
shot('seal_stack','All gun seals','Two coolant rings, copper/spacer ring, two isolator rings, and head-joint ring',combine(SEALS,HEADSEAL,ISOSEALS,role('kfseal')),combine(C,B,SP,PT,BASE,role('kfcenter')),mode='seal_stack',el=22,seconds=15,
 speech='This final seal review includes every gun O ring: two coolant rings, the copper-to-spacer ring, two isolator face rings and the head-joint ring. Each closes a different interface. Keeping the parts separate is essential to understanding the pressure and coolant boundaries.')
shot('reassembly','Gun reassembly','All 141 component instances return to their checked R06 assembly positions',GUN,mode='reassemble',seconds=20,
 speech='The complete exploded gun returns to its checked assembly positions. Every repeated screw, magnet disc, sleeve and separate small connector part is included. The motion explains mating relationships rather than certifying a collision-free workshop procedure.')
shot('complete_end','Complete R06 gun','Target / cooling / magnetic circuit / electrical isolation / RF connections / grounded shielding',GUN,mode='orbit',seconds=16,
 speech='The assembled gun combines the consumable target, copper cooling head, magnetic circuit, PTFE isolation, separate RF centre and shield paths, routed services and grounded guards. This walkthrough explains the full current CAD design. Electrical, thermal, pressure and manufacturing qualification remain separate engineering work.')

# Expose the internal attachment points rather than filming an opaque wall.
for s in SHOTS:
    if s['key'] in {'ground_carrier','ground_anchor','ground_path','live_standoff'}:
        section=dict(s['section'] or {});section.update(normal=[1,0,0],origin=[0,0,0]);s['section']=section;s['az']=-145
    if s['key'] in {'water_rings','isolator_rings','centering','joint_seal','ground_carrier','ground_anchor','ground_path','live_standoff'} or s['mode']=='fasteners':s['ghost_context']=True

def pulse(u):
    if u<.38:return smooth(u/.38)
    if u<.55:return 1.
    if u<.88:return 1-smooth((u-.55)/.33)
    return 0.

def overall_offset(i):
    r=META[i]['role'][4:]
    z={'darkcap':-72,'upperbolts':-72,'targetbolts':-56,'clamp':-40,'target':-21,'waterseal':12,'closure':30,'backbolts':48,'outermag':54,'centermag':54,'yoke':82,'yokebolt':100,'headseal':110,'spacer':125,'headbolts':145,'upper62':160,'isolator':178,'lower62':195,'base':220,'cups':248,'basebolts':275,'kfcenter':265,'kfseal':280,'kfbolts':300,'kftube':300}.get(r,0)
    p=np.array([0.,0.,float(z)])
    if r=='shieldtube':p+=(-170,0,0)
    if r in {'upperbolts','lowerbolts'}:p+=radvec(i,22)
    if r=='kfclamps':p+=(0,40 if center(i)[1]>0 else -40,265)
    if r in {'hoses','fittings'}:p+=(140,25,90)
    if r in {'coax','rfhot','rfground'}:p+=(180,-30,90)
    return p

class GunRenderer(Studio):
    def __init__(self):
        super().__init__();self.gun=GUN;self.clipped={};self.configured=None
        for i in range(len(self.actors)):
            if i not in GUN:self.ren.RemoveActor(self.actors[i])
        # Material identity makes the separately modeled coax layers readable.
        colours={137:(.10,.13,.16),138:(.58,.64,.68),139:(.90,.86,.70),140:(.83,.43,.19),141:(.90,.86,.70)}
        for n,c in colours.items():self.actors[name('Gun '+str(n)+' ')].GetProperty().SetColor(*c)
        self.small=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',24)

    def section_mapper(self,i,section):
        key=(i,json.dumps(section,sort_keys=True))
        if key in self.clipped:return self.clipped[key]
        planes=vtk.vtkPlaneCollection()
        spec=[]
        if 'normal' in section:spec.append((section['normal'],section['origin']))
        if 'window' in section:
            lo,hi=section['window'];spec.extend([([0,0,1],[0,0,lo]),([0,0,-1],[0,0,hi])])
        for normal,origin in spec:
            p=vtk.vtkPlane();p.SetNormal(*normal);p.SetOrigin(*origin);planes.AddItem(p)
        clip=vtk.vtkClipClosedSurface();clip.SetInputData(self.fullmaps[i].GetInput());clip.SetClippingPlanes(planes);clip.GenerateFacesOn();clip.Update()
        m=vtk.vtkPolyDataMapper();m.SetInputData(clip.GetOutput());m.ScalarVisibilityOff();self.clipped[key]=m;return m

    def set_parts(self,s,u):
        e=pulse(u);mode=s['mode'];visible=set(s['primary']+s['context'])
        for i in self.gun:
            a=self.actors[i];q=META[i];a.SetVisibility(i in visible)
            if i not in visible:continue
            a.SetMapper(self.section_mapper(i,s['section']) if s['section'] else self.fullmaps[i]);a.GetProperty().SetOpacity(1)
            if s.get('ghost_context') and i in s['context'] and i not in s['primary']:a.GetProperty().SetOpacity(.20)
            shift=np.array(s['moves'].get(str(i),[0,0,0]),float)*e
            if mode in {'overall','reassemble'}:shift=overall_offset(i)*(ramp(u,.1,.8) if mode=='overall' else 1-ramp(u,.1,.9))
            if mode=='layers':
                lift=min(1,2*e);spread=max(0,2*e-1)
                if not s['moves']:
                    j=s['primary'].index(i);shift=np.array([(j-1.5)*8*spread,0,j*6*lift])
                elif i in s['primary']:
                    shift=np.array(s['moves'][str(i)])*spread+np.array([0,0,8*lift])
            if mode=='seal_stack':
                if i in s['primary']:shift=np.array([0,0,(s['primary'].index(i)+1)*15*e])
                else:a.GetProperty().SetOpacity(.18)
            if mode=='magnetic' and i in C+TARGET:a.GetProperty().SetOpacity(.2)
            if mode=='termination' and i in BASE+Y+B:a.GetProperty().SetOpacity(.16)
            if mode=='water_path' and i in Y:a.GetProperty().SetOpacity(.15)
            tr=vtk.vtkTransform();tr.Translate(*shift)
            if mode=='fasteners' and i in s['primary']:
                p=center(i);axis=radvec(i,1) if q['role'] in {'gun_upperbolts','gun_lowerbolts'} else np.array([0,0,1])
                tr.Translate(*p);tr.RotateWXYZ(720*ramp(u,.55,.88),*axis);tr.Translate(*(-p))
            a.SetUserTransform(tr)

    def configure(self,s):
        # Union of actual transformed bounds fixes framing throughout the motion.
        use=s['primary'] if s['fit_primary'] else s['primary']+s['context'];bounds=[]
        for u in [0,.4,.55,1]:
            self.set_parts(s,u)
            for i in use:
                a=self.actors[i];b=a.GetBounds()
                if b and all(math.isfinite(v) for v in b) and b[0]<=b[1]:bounds.append(b)
        assert bounds,s['key'];b=np.array(bounds);lo=b[:,[0,2,4]].min(axis=0);hi=b[:,[1,3,5]].max(axis=0);focus=(lo+hi)/2
        az=math.radians(s['az']);el=math.radians(s['el']);direction=np.array([math.cos(az)*math.cos(el),math.sin(az)*math.cos(el),math.sin(el)])
        right=np.cross(direction,[0,0,1]);right/=np.linalg.norm(right);up=np.cross(right,direction)
        corners=np.array([[x,y,z] for x in [lo[0],hi[0]] for y in [lo[1],hi[1]] for z in [lo[2],hi[2]]])-focus
        scale=max(np.abs(corners@up).max(),np.abs(corners@right).max()/(W/H))*1.23
        # Reserve the bottom two text lines without covering the primary parts.
        focus=focus-up*scale*.10
        self.focus=focus;self.scale=max(scale,3.5);self.configured=s['key']

    def frame(self,s,u):
        if self.configured!=s['key']:self.configure(s)
        self.set_parts(s,u);az=math.radians(s['az']+(10*(u-.5) if s['mode']=='orbit' else 0));el=math.radians(s['el'])
        self.cam.SetViewUp(0,0,1);self.cam.SetFocalPoint(*self.focus);self.cam.SetPosition(*(self.focus+2500*np.array([math.cos(az)*math.cos(el),math.sin(az)*math.cos(el),math.sin(el)])));self.cam.SetParallelScale(self.scale)
        self.ren.ResetCameraClippingRange();self.win.Render();self.cap.Modified();self.cap.Update()
        rgb=vtk_to_numpy(self.cap.GetOutput().GetPointData().GetScalars()).reshape(H,W,3);im=Image.fromarray(np.flipud(rgb));d=ImageDraw.Draw(im)
        width=max(d.textlength(s['label'],font=self.font),d.textlength(s['detail'],font=self.small))+44
        d.rounded_rectangle((30,H-124,min(W-30,30+width),H-18),radius=7,fill=(29,38,49));d.text((48,H-118),s['label'],font=self.font,fill=(241,245,248));d.text((48,H-64),s['detail'],font=self.small,fill=(218,229,237))
        return im

def make_voices():
    (OUT/'shots.json').write_text(json.dumps(SHOTS,indent=2))
    ps=WORK/'narrate.ps1';ps.write_text("param([string]$Json,[string]$Output)\nAdd-Type -AssemblyName System.Speech\n$s=New-Object System.Speech.Synthesis.SpeechSynthesizer\n$s.SelectVoice('Microsoft David Desktop');$s.Rate=0\nforeach($c in (Get-Content -LiteralPath $Json -Raw | ConvertFrom-Json)) {$s.SetOutputToWaveFile((Join-Path $Output ($c.key+'.wav')));$s.Speak($c.speech);$s.SetOutputToNull()}\n$s.Dispose()")
    subprocess.run(['powershell','-NoProfile','-ExecutionPolicy','Bypass','-File',str(ps),str(OUT/'shots.json'),str(WORK)],check=True)
    durations=[];chunks=[];params=None
    for s in SHOTS:
        with wave.open(str(WORK/(s['key']+'.wav')),'rb') as f:p=f.getparams();raw=f.readframes(p.nframes)
        if params is None:params=p
        duration=math.ceil(max(s['minimum_seconds'],p.nframes/p.framerate+1.6)*FPS)/FPS;durations.append(duration)
        lead=round(.4*p.framerate);tail=round(duration*p.framerate)-lead-p.nframes;chunks.append(bytes(lead*p.sampwidth*p.nchannels)+raw+bytes(tail*p.sampwidth*p.nchannels))
    with wave.open(str(WORK/'Narration.wav'),'wb') as f:
        f.setparams(params)
        for c in chunks:f.writeframes(c)
    return durations

def coverage():
    covered={i:[s['key'] for s in SHOTS if i in s['primary'] and s['key'] not in {'complete','exploded','reassembly','complete_end'}] for i in GUN}
    missing=[META[i]['name'] for i,chapters in covered.items() if not chapters]
    assert not missing,missing
    report={'source_component_instances':len(GUN),'shots':len(SHOTS),'all_components_explicitly_covered':not missing,'components':[{'index':i,'name':META[i]['name'],'role':META[i]['role'],'source_note':META[i]['note'],'dedicated_shots':chapters} for i,chapters in covered.items()]}
    (OUT/'component-coverage.json').write_text(json.dumps(report,indent=2));return report

def main():
    report=coverage();r=GunRenderer();preview='--preview' in sys.argv
    images=[]
    for j,s in enumerate(SHOTS):
        im=r.frame(s,.46);im.save(OUT/f'preview-{j+1:02}.jpg',quality=93);images.append(im)
    sheet=Image.new('RGB',(1920,math.ceil(len(images)/4)*270))
    for j,im in enumerate(images):sheet.paste(im.resize((480,270)),(j%4*480,j//4*270))
    sheet.save(OUT/'contact-sheet.jpg',quality=94)
    for key in ['ptfe_sleeve','sleeve_section','water_channel','coax_layers','coax_termination','target_stack']:
        s=next(s for s in SHOTS if s['key']==key)
        for u in [.05,.46,.95]:r.frame(s,u).save(OUT/f'check-{key}-{u}.jpg',quality=95)
    if preview:r.win.Finalize();print(json.dumps({'previews':len(SHOTS),'covered_parts':len(GUN)}));return
    durations=make_voices();ff=imageio_ffmpeg.get_ffmpeg_exe();picture=WORK/'picture.mp4'
    proc=subprocess.Popen([ff,'-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-an','-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p',str(picture)],stdin=subprocess.PIPE)
    timeline=[];elapsed=0;clock=time.time()
    try:
        for j,(s,duration) in enumerate(zip(SHOTS,durations)):
            print(f'{j+1}/{len(SHOTS)} {s["label"]} | {duration:.1f}s | render {time.time()-clock:.0f}s',flush=True);n=round(duration*FPS)
            # Static explanatory holds reuse a rendered frame; moving parts stay at full 24 fps.
            held=None
            for k in range(n):
                u=k/(n-1);static=(s['mode']=='static' or (s['mode'] not in {'orbit','overall','reassemble','fasteners'} and (.38<=u<=.55 or u>=.88)))
                if static and held is not None:im=held
                else:im=r.frame(s,u);held=im if static else None
                proc.stdin.write(np.asarray(im).tobytes())
            timeline.append({'key':s['key'],'label':s['label'],'start_seconds':elapsed,'duration_seconds':duration});elapsed+=duration
    finally:proc.stdin.close()
    if proc.wait()!=0:raise RuntimeError('Encoding failed')
    meta=';FFMETADATA1\ntitle=R06 sputter gun - complete CAD walkthrough\n'
    for ch in timeline:meta+=f'[CHAPTER]\nTIMEBASE=1/1000\nSTART={round(ch["start_seconds"]*1000)}\nEND={round((ch["start_seconds"]+ch["duration_seconds"])*1000)}\ntitle={ch["label"]}\n'
    (WORK/'chapters.ffmeta').write_text(meta,encoding='utf-8')
    silent=OUT/'R06 sputter gun - complete silent walkthrough.mp4';narrated=OUT/'R06 sputter gun - complete narrated walkthrough.mp4'
    subprocess.run([ff,'-y','-loglevel','error','-i',str(picture),'-i',str(WORK/'chapters.ffmeta'),'-map','0:v','-map_metadata','1','-map_chapters','1','-an','-c:v','copy','-movflags','+faststart',str(silent)],check=True)
    subprocess.run([ff,'-y','-loglevel','error','-i',str(picture),'-i',str(WORK/'Narration.wav'),'-i',str(WORK/'chapters.ffmeta'),'-map','0:v','-map','1:a','-map_metadata','2','-map_chapters','2','-c:v','copy','-c:a','aac','-b:a','160k','-t',str(elapsed),'-movflags','+faststart',str(narrated)],check=True)
    source=ROOT/'chamber-design/coolant-fitting-r06/Complete sputter system R06.step';gun=ROOT/'chamber-design/coolant-fitting-r06/Magnetron R06.step'
    provenance={'source_system_step':str(source.relative_to(ROOT)),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'gun_step':str(gun.relative_to(ROOT)),'gun_sha256':hashlib.sha256(gun.read_bytes()).hexdigest(),'geometry':'All 141 R06 gun instances extracted from the exact system STEP tessellation; no substitute part geometry. Sections clip the actual meshes.','resolution':[W,H],'fps':FPS,'duration_seconds':elapsed,'chapters':timeline,'coverage':'component-coverage.json','narration':'Microsoft David Desktop synthetic voice in companion version only','notes':['Repeated hardware shown in full patterns, with separate local close-ups.','Exploded offsets illustrate mating relationships, not collision-free installation paths or tightening instructions.','Source nominal thread envelopes, fitted seal shapes and supplier-envelope limitations are preserved.','Coax layers use material colours to distinguish jacket, shield, dielectric and conductor.','Thermal, RF, leak and manufacturing qualification are not certified by the animation.']}
    (OUT/'provenance.json').write_text(json.dumps(provenance,indent=2));(OUT/'Narration.txt').write_text('\n\n'.join(s['label']+'\n'+s['speech'] for s in SHOTS),encoding='utf-8');r.win.Finalize();print(json.dumps({'seconds':elapsed,'shots':len(SHOTS),'parts':len(GUN),'silent':str(silent),'narrated':str(narrated)}),flush=True)

if __name__=='__main__':main()
