from pathlib import Path
import json
import cadquery as cq
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle

P=Path(__file__).resolve().parent
# Preliminary layout only: roof sizing and weld/seal details are not released.
plate=cq.Workplane('XY').box(220,220,10,centered=(True,True,False)).faces('>Z').workplane().hole(27)
neck=cq.Workplane('XY',origin=(0,0,10)).circle(16.5).circle(13.5).extrude(20)
cq.exporters.export(plate,str(P/'Top plate R01 - preliminary.step'))
cq.exporters.export(neck,str(P/'Weld neck allowance - preliminary.step'))
assembly=cq.Assembly(name='Preliminary roof and neck - KF interface unresolved')
assembly.add(plate,name='Roof_220x220x10_bore27',color=cq.Color(.65,.7,.75))
assembly.add(neck,name='Neck_OD33_ID27_L20_allowance',color=cq.Color(.5,.6,.65))
assembly.save(str(P/'Roof and neck layout - preliminary.step'))
report={
 'status':'PRELIMINARY; NOT A VERIFIED COMPATIBLE ASSEMBLY OR FABRICATION RELEASE',
 'units':'mm', 'plate':{'width':220,'depth':220,'thickness_assumed':10,'central_bore':27},
 'chamber_internal_footprint':[200,200],
 'neck_allowance':{'OD':33,'ID':27,'height_above_plate':20},
 'gun_tube_OD':25.4,'nominal_diametral_clearance_in_roof_and_neck':1.6,
 'checks':{'plate_valid':plate.val().isValid(),'neck_valid':neck.val().isValid(),
 'plate_neck_interference_mm3':plate.val().intersect(neck.val()).Volume(),
 'plate_reimport_valid':cq.importers.importStep(str(P/'Top plate R01 - preliminary.step')).val().isValid()},
 'unresolved':['Standard QF25-100-SRV ring dimensions A23.6/B26 require drawing review; 25.4 tube passage is not established.',
 'KF25 mating flange and seal stack deliberately not modeled. Standard weld stubs can restrict passage below 25.4.',
 'Selected adapter and mating seal must pass tube end and full adjustment travel.',
 'Roof pressure deflection, wall attachment, weld distortion and seal/retention design require verification.',
 'Neck allowance is not a selected purchased KF25 weld flange.',
 'Door assembly access and gun collision checks not yet performed.']}
(P/'Geometry checks.json').write_text(json.dumps(report,indent=2))

fig,(ax,bx)=plt.subplots(1,2,figsize=(13,7),gridspec_kw={'width_ratios':[1,1.15]})
fig.suptitle('Top-mounted gun: preliminary roof layout',fontsize=19,weight='bold')
ax.add_patch(Rectangle((-110,-110),220,220,fc='#edf1f3',ec='#263746',lw=2))
ax.add_patch(Rectangle((-100,-100),200,200,fill=False,ec='#8b959d',ls='--'))
ax.add_patch(Circle((0,0),16.5,fc='#b6c6cf',ec='#263746'))
ax.add_patch(Circle((0,0),13.5,fc='white',ec='#263746'))
ax.plot([-110,110],[0,0],color='#aaa',lw=.6,ls='-.')
ax.plot([0,0],[-110,110],color='#aaa',lw=.6,ls='-.')
ax.annotate('220 mm blank',xy=(-110,-125),xytext=(110,-125),ha='right',arrowprops={'arrowstyle':'<->'})
ax.annotate('Central bore: 27 mm',xy=(13.5,0),xytext=(20,58),arrowprops={'arrowstyle':'->'},fontsize=10)
ax.text(0,120,'TOP VIEW',ha='center',weight='bold')
ax.text(0,-150,'Dashed line: 200 x 200 mm internal chamber\n10 mm roof thickness is provisional',ha='center',fontsize=10)
ax.set(xlim=(-135,135),ylim=(-170,145),aspect='equal');ax.axis('off')
# Section shows only verified roof/neck bore and a deliberately schematic purchased stack.
bx.add_patch(Rectangle((-85,0),71.5,10,fc='#b6c6cf',ec='#263746'))
bx.add_patch(Rectangle((13.5,0),71.5,10,fc='#b6c6cf',ec='#263746'))
for x in [-16.5,13.5]: bx.add_patch(Rectangle((x,10),3,20,fc='#b6c6cf',ec='#263746'))
bx.add_patch(Rectangle((-12.7,-50),25.4,170,fc='#d6e7f0',ec='#247598',lw=1.5))
bx.add_patch(Rectangle((-25,35),50,55,fill=False,ec='#b06b25',lw=1.5,ls='--'))
bx.plot([-25,25],[32,32],color='#b06b25',ls='--',lw=2)
bx.annotate('QF25XVC100 reference\nadapter position\n(schematic envelope)',xy=(25,75),xytext=(43,100),fontsize=10,arrowprops={'arrowstyle':'->'})
bx.annotate('KF25 joint: resolve\nfull tube passage\nand centering seal',xy=(22,32),xytext=(43,47),fontsize=10,color='#96541d',arrowprops={'arrowstyle':'->','color':'#96541d'})
bx.annotate('Weld neck allowance\n27 bore / 33 OD / 20 high',xy=(16.5,17),xytext=(43,-28),fontsize=10,arrowprops={'arrowstyle':'->'})
bx.annotate('25.4 mm gun tube\ninsert from inside chamber',xy=(0,-35),xytext=(-105,-77),fontsize=10,arrowprops={'arrowstyle':'->'})
bx.text(-82,-19,'VACUUM',fontsize=9,color='#555')
bx.text(-82,110,'ATMOSPHERE',fontsize=9,color='#555')
bx.text(0,137,'CENTRAL SECTION - SCHEMATIC',ha='center',weight='bold')
bx.set(xlim=(-110,150),ylim=(-90,150),aspect='equal');bx.axis('off')
fig.text(.5,.045,'Interface concept only. KF mating flange/seal not modeled. Dimensions in mm. Not for fabrication.',ha='center',fontsize=11,color='#96541d')
fig.tight_layout(rect=(0,.08,1,.93));fig.savefig(P/'Top plate R01 - concept.png',dpi=170)
print(json.dumps(report['checks'],indent=2))
