from pathlib import Path
import shutil,json,zipfile
ROOT=Path.cwd();P=ROOT/'cad/stage-shutter-procurement';S=ROOT/'archive/chamber-design/complete-chamber-r01/Separate parts'
for n in ['Bent shutter.step','Substrate stage.step','Shutter blank reference.dxf','Shutter developed blank - K0.42.step']:shutil.copy2(S/n,P/n)
rows=[
 {'id':'SS01','component':'Substrate stage plate','spec':'SS304 disc, D90 x6mm; simple passive removable stage as current CAD','required':1,'stock':0,'new':1,'method':'Custom vendor order','status':'Local fabrication','unit_price':1500,'supplier':'Mumbai precision turning/machining shop; vendor quote pending','note':'Keep existing stage geometry. Stage supports are included inCB01. Stage topZ40; reference1mm specimen topZ41.','file':str(P/'Substrate stage.step')},
 {'id':'SS02','component':'One-piece bent sheet-metal shutter','spec':'SS304 sheet1mm; two90deg bends, innerR2;56x56 blade; existing folded CAD controls','required':1,'stock':0,'new':1,'method':'Custom vendor order','status':'Local fabrication','unit_price':1000,'supplier':'Mumbai laser-cutting and press-brake vendor; quote pending','note':'Finished geometry controls. K0.42 DXF is a reference; fabricator adjusts blank/bend allowance to actual tooling. Include small thrust-washer detail in same job.','file':str(P/'Bent shutter.step')},
 {'id':'SS03','component':'Shutter hand screw','spec':'1/4-28 x1.25in flared-collar thumb screw; previous reference99607A246','required':1,'stock':1,'new':0,'method':'No purchase','status':'Already in stock','unit_price':0,'supplier':'Existing stock; reference only:https://www.mcmaster.com/99607A246/','note':'User confirmed stock. Manual operation; no separate actuator.','file':''},
 {'id':'SS04','component':'Shutter FKM O-ring','spec':'Previous reference6540K248;1/4in ID x1/2in OD x1/8in cross-section','required':1,'stock':1,'new':0,'method':'No purchase','status':'Already in stock','unit_price':0,'supplier':'Existing stock; reference only:https://www.mcmaster.com/6540K248/','note':'One seal allocated from user stock; do not buy another pack. Actual rotary seal stack still needs installed leak/wear checking.','file':''},
 {'id':'SS05','component':'Shutter nuts','spec':'1/4-28 aluminium nuts; previous reference90670A155','required':2,'stock':2,'new':0,'method':'No purchase','status':'Already in stock','unit_price':0,'supplier':'Existing stock; reference only:https://www.mcmaster.com/90670A155/','note':'Two installed nuts allocated; no new pack to procure.','file':''},
 {'id':'SS06','component':'Small shutter thrust washer','spec':'Existing CAD reference: ID6.6 OD16 x0.5mm','required':1,'stock':0,'new':0,'method':'Included in SS02','status':'Included in fabrication','unit_price':0,'supplier':'Supplied/finished with the sheet-metal job','note':'Retain as part of existing assembly detail if required; included inSS02 allowance, not a separate shopping item or an assumed stock holding.','file':''},
 {'id':'SS07','component':'Fixed stage supports','spec':'4 posts D6 x34 atX/Y +/-29mm','required':4,'stock':0,'new':0,'method':'Included in CB01','status':'Included in chamber package','unit_price':0,'supplier':'Alfa Technovac chamber package','note':'Already inCB01 supplier scope and allowance; do not buy or charge twice.','file':''},
 {'id':'SS08','component':'Reference specimen','spec':'50x50x1mm reference only','required':1,'stock':0,'new':0,'method':'Reference only','status':'Not a hardware purchase','unit_price':0,'supplier':'Process specimen, not a stage fabrication item','note':'Shown only to define stage/shutter/target distances; actual process substrates are outside this hardware purchase list.','file':''}
]
record={'subsystem':4,'rows':rows,'new_spend_estimate_INR':2500,'basis':'Assistant planning allowances only: stage1500, folded shutter job1000; GST/delivery as quoted. Stock hardware haszero new-purchase cost.','user_decisions':['No separate actuator','Screw, O-ring and nuts already in stock','Shutter sheet-metal part goes to local fabrication'],'stage_selection':'SS304 plainD90x6 disc, current CAD geometry retained','personal_input_required':False}
(P/'Stage and shutter procurement record.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
notes='''SUBSTRATE STAGE AND MANUAL SHUTTER - LOCAL FABRICATION SCOPE
24 November2026

NEW WORK TO QUOTE
1. Stage: one SS304 disc, diameter90mm, thickness6mm, per Substrate stage.step.
   Keep the current simple passive/removable geometry. Break sharp edges and
   provide a clean, flat, deburred vacuum-facing finish. The four fixed supports
   are already part of Alfa Technovac's chamber package; do not quote them again.
   Existing installed stage undersideZ34, topZ40. With the reference1mm specimen,
   specimen topZ41 is the deposition-distance datum.
2. Shutter: one SS304 sheet-metal part,1mm thick, two90degree bends, innerR2,
   per Bent shutter.step. Blade56x56mm, upper strip16mm wide, mounting holeD6.6.
   Folded CAD is the dimensional master. DXF/flat STEP use provisionalK0.42;
   the fabricator must adjust developed allowances to their material/tooling
   to obtain the specified finished geometry. Deburr, clean, leave unpainted.
   Retain the small existing washer detail (ID6.6 OD16 t0.5) within this job
   where required; no separate procurement line or separate charge is planned.

STOCK COMPONENTS - NO NEW PURCHASE
One1/4-28 x1.25in flared-collar hand screw (reference99607A246).
One FKM O-ring (previous reference6540K248).
Two1/4-28 aluminium nuts (previous reference90670A155).
The owner confirmed these are already in stock. References identify the parts;
they are not purchasing instructions. There is no separate actuator to procure.

RETAINED GEOMETRY
Shutter axisX-65,Y0. Blade undersideZ53, topZ54,12mm above reference specimen.
Upper flatZ293..294. Flat midplane drop240mm; straight vertical length235mm.
Closed blade centred on the specimen; parking rotation80degrees.
Inherited nominal sweep wall clearance is approximately2.877mm at its minimum.
The chamber roof hole/sealing land is included inCB01. The stocked hand screw,
seal and nuts remain the manual mechanism. Confirm fit and installed leak/wear
performance of the existing seal stack; it has not been qualified as a rotary
vacuum feedthrough by the illustrative CAD. No new actuator is being designed.

BUDGET RECORD
Stage planning allowance INR1500; shutter fabrication job INR1000.
Combined new work INR2500, pending local quotations and applicable tax/delivery.
Stock screw, O-ring and nuts havezero new-purchase cost. Washer work is included
in the shutter job; stage supports are included inCB01. These are not supplier
quotations and no orders or messages have been sent.
'''
(P/'Local fabrication scope.txt').write_text(notes,encoding='utf-8')
with zipfile.ZipFile(P/'Stage and shutter - local fabrication.zip','w',zipfile.ZIP_DEFLATED) as z:
 for f in P.iterdir():
  if f.suffix in ['.step','.dxf','.txt']:z.write(f,f.name)
print('Stage/shutter fabrication packet saved; only2 new fabrication jobs; stock hardware cost0')
