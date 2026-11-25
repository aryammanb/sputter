from pathlib import Path
import json,math,zipfile,shutil
import cadquery as cq
P=Path(__file__).resolve().parent;ROOT=P.parent.parent;r=json.loads((P/'Clamp redesign and verification.json').read_text());m=json.loads((P/'parts.json').read_text());ns=[q for q in m if q['group']=='gun'];gg=cq.importers.importStep(str(P/'Latest magnetron R05 - aluminium3.175mm.step')).val().Solids();assert len(gg)==len(ns)==141
by=[q|{'shape':s} for q,s in zip(ns,gg)]
def overlap_bbox(a,b):
 A=a.BoundingBox();B=b.BoundingBox();return all(getattr(A,k+'min')<getattr(B,k+'max')-1e-7 and getattr(B,k+'min')<getattr(A,k+'max')-1e-7 for k in ['x','y','z'])
new_bolts=[q for q in by if q['role']=='gun_targetbolts'];interferences=[]
for bolt in new_bolts:
 for q in by:
  if q['role']=='gun_cooler' or q is bolt or not overlap_bbox(bolt['shape'],q['shape']):continue
  v=bolt['shape'].intersect(q['shape']).Volume()
  if v>1e-5:interferences.append({'screw':bolt['name'],'other':q['name'],'volume_mm3':v})
assert not interferences,interferences
ver={'new_screw_interference_outside_intended_copper_threads':interferences,'gun_solids':141,'gun_valid_solids':sum(s.isValid() for s in gg),'assemblies':{}}
assert ver['gun_valid_solids']==141
for name in ['Target clamp R05 - 3.175mm target','Aluminium target D50.8 x3.175','Clamp R05 fit assembly','Complete sputter system R05','Complete sputter system R05 - loading']:
 solids=cq.importers.importStep(str(P/(name+'.step'))).val().Solids();bad=[s for s in solids if not s.isValid()];expect=r['solids'] if name.startswith('Complete') else 3 if name.startswith('Clamp R05 fit') else 1;assert len(solids)==expect
 if name.startswith('Complete'):
  assert len(bad)==1
  b=bad[0].BoundingBox();assert b.xmin>300 and b.ymin>0 and b.zmax<0,'Unexpected invalid geometry'
 else:assert not bad
 ver['assemblies'][name]={'solids':len(solids),'valid':len(solids)-len(bad),'known_invalid_supplier_RV3':len(bad)}
 if name=='Complete sputter system R05':
  k=0
  for q in m:
   ss=solids[k:k+q['solid_count']];k+=q['solid_count']
   if q['role']=='gun_target':b=ss[0].BoundingBox();assert abs(b.zmin-141)<1e-5 and abs(b.zmax-144.175)<1e-5;ver['actual_target_front_z_mm']=b.zmin
   if q['role']=='substrate':ver['actual_substrate_top_z_mm']=ss[0].BoundingBox().zmax
  ver['actual_default_gap_mm']=ver['actual_target_front_z_mm']-ver['actual_substrate_top_z_mm'];assert abs(ver['actual_default_gap_mm']-100)<1e-5
 print('Verified',name,ver['assemblies'][name],flush=True)
(P/'Export verification.json').write_text(json.dumps(ver,indent=2),encoding='utf-8')
notes='''TARGET CLAMP R05 / SELECTED VTRITRATECH ALUMINIUM TARGET
24 November 2026. Nominal prototype design revision.

Target procurement: https://www.vritratech.com/store/product/aluminium-al-sputtering-target/
Al99.99%, diameter2in=50.8mm, thickness0.125in=3.175mm.
Listed price: INR8300 +18%GST1494 = INR9794, delivery extra.

CAD TO USE
Target clamp R05 - 3.175mm target.step: individual revised clamp.
Clamp R05 fit assembly.step: clamp, target and existing copper cooling body.
Latest magnetron R05 - aluminium3.175mm.step: complete141-instance gun,
using the original source gun coordinates (target points +Y).
Complete sputter system R05.step: current full chamber/system assembly.
Complete sputter system R05 - loading.step: door open, shutter parked.

CLAMP GEOMETRY / MACHINING DESCRIPTION
Source coordinates: target backY0; target frontY3.175.
Clamp front planeY5 retained. Rear outer plane is nominalY-2.5
(source STEP retains its original0.00023mm deviation). Overall nominal7.5.
Outer diameter93.6; original outer and rear geometry retained.
Central rear cavity/register diameter70.5 extends to contact shoulderY3.175.
Nominal cavity depth from rear datum is5.675.
New central pressure lip occupiesY3.175..5: axial depth1.825, previously3.
Contact-side edge:0.25mm x45degree chamfer, D48.3 atY3.175 toD47.8 atY3.425.
Straight minimum apertureD47.8 extendsY3.425..4.175.
Front45degree flare ends atD49.45 onY5.
Nominal flat bearing band against the target: radius24.15..25.4,
width1.25, theoretical contact area194.582mm2 before any target bevel.
The smaller front flare preserves a cylindrical lip land while accommodating
the thicker target. Simply cutting the old interference volume away would
leave an undesirable tapered knife edge at the new contact shoulder.
12 clearance holesD3.3 onPCD80, spaced30degrees, first at15degrees from+X
in theX/Z plane. CounterboresD5.7 have seatY1, depth4 from frontY5.
Outer mounting region, hole positions, rear register and screw head seats
are identical to the original part by exact Boolean comparison.

FASTENERS
Use12 nominalM3x10 socket-head screws instead ofM3x8. Head seats stayY1;
new physical tipsY-9, with1mm to the modeled pilot bottomY-10.
Straight shaft/full tap-drill envelope overlap is approximately5.55mm,
versus3.55mm with the previous screws. The modeled0.2mm screw-tip chamfer
and0.25mm pilot entry chamfer are excluded from that straight engagement.
Ensure actualM3x0.5 useful threads, screw tolerances and pilot depth support
this engagement without bottoming. Holes are thread envelopes, not helices.
Screw strip strength, torque and clamping preload have not been rated.
Copper body geometry is retained; specify its useful thread depth in the
released manufacturing drawing rather than inferring it from a drilled hole.

ASSEMBLY INTEGRATION
Target back still seats atY0: no copper roof/channel material was removed.
Nominal target/clamp, cooler/clamp and grounded-shield/clamp overlaps arezero.
The live clamp/grounded dark-cap minimum distance remains1.0mm.
The entire gun is raised1.175mm in the chamber so target front staysZ141
above substrate topZ41: default gap100mm, selected travel75..150mm retained.
External gun coolant and coax extensions meet the raised endpoints.
No other chamber geometry, substrate stage, shutter or vacuum ports changed.
The lower wall of the shutter blade remains12mm above the reference substrate.

ENGINEERING STATUS
This is a completed nominal geometric redesign, not a validated load or300W
operating rating. The lip is thinner axially:1.825mm versus3mm. Check stiffness,
preload, target tolerance/edge bevel/flatness, thermal expansion and target
thermal contact before fabrication/operation. Materials/finishes and final
manufacturing tolerances remain to specify; no tightening torque is given.
Supplier target dimensional tolerances are not published on the product page.
The existing gun architecture retains a floating clamp arrangement; do not
bottom the screws or eliminate its intended compliant travel.

The pole-tip to target-front spacing is now5.675mm, previously4.5mm.
Earlier magnetic-field results assumed a2mm target and must be reassessed
at the new target plane. Do not reuse the earlier95mT value for this target.
The R04 main video predates this target/clamp revision and was not rerendered.
Full system STEP retains the known invalid supplierRV3 reference solid;
all141 gun solids and all other full-system solids reopen valid.
'''
(P/'READ FIRST - Clamp R05.txt').write_text(notes,encoding='utf-8')
latest=Path((ROOT/'outputs/01a209eb-c119-74d1-bef5-c610f57d428f/latest_procurement_workbook.txt').read_text().strip());shutil.copy2(latest,P/'Updated procurement.xlsx')
files=[x for x in P.iterdir() if x.suffix.lower() in ['.step','.json','.csv','.txt','.png','.xlsx'] and x.name not in ['parts.json']]
with zipfile.ZipFile(P/'Clamp R05 - revised CAD package.zip','w',zipfile.ZIP_DEFLATED) as z:
 for f in files:z.write(f,f.name)
with zipfile.ZipFile(P/'Clamp R05 - revised CAD package.zip') as z:assert z.testzip() is None
print('R05 package verified',len(files),'files',flush=True)
