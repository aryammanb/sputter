from pathlib import Path
import json,csv,zipfile
import cadquery as cq
P=Path(__file__).resolve().parent;ROOT=P.parent.parent;B=P.parent/'target-clamp-r05';m=json.loads((B/'parts.json').read_text());solids=cq.importers.importStep(str(B/'Complete sputter system R05.step')).val().Solids();parts=[];k=0
exclude={'stage','substrate','pump_baffle','shutter_seal'}
for q in m:
 ss=solids[k:k+q['solid_count']];k+=q['solid_count']
 take=(q['group']=='chamber' and q['role'] not in exclude) or q['group']=='door' or q['role'] in ['iso_clamp','iso_screw','iso_seal'] or q['role'] in ['fit_kf_seal','fit_clamp_left','fit_clamp_right','fit_clamp_bolt','fit_clamp_wing','fit_clamp_pin'] or q['name'].startswith(('Right spare ','Pirani rear port joint','Penning rear port joint','MFC chamber KF25 joint'))
 if take:parts.append(q|{'shape':ss[0] if len(ss)==1 else cq.Compound.makeCompound(ss)})
assert all(q['shape'].isValid() for q in parts)
for name,angle in [('CB01 chamber and door - frozen layout',0),('CB01 chamber and door - loading',-110)]:
 a=cq.Assembly(name=name)
 for i,q in enumerate(parts):
  s=q['shape']
  if q['group']=='door':s=s.rotate((-118,-116,0),(-118,-116,1),angle)
  a.add(s,name=str(i)+'_'+q['name'].replace('/','_'),color=cq.Color(*q['color']))
 a.save(str(P/(name+'.step')))
 re=cq.importers.importStep(str(P/(name+'.step'))).val();assert re.isValid()
 print('Exported and reopened',name,len(re.Solids()),'valid solids',flush=True)
ports=[['Gun mount','KF25; free passage forOD25.4 gun tube',0,0,330,'+Z','Nominal neck bore27; complete centering hardware must permit tube passage'],['Turbo inlet','ISO63-K',0,0,-45,'-Z','Standard mating seal and4 double-claw clamps included'],['Gas inlet','KF25',0,140.132,210,'+Y','MFC/VCR adapter separately procured'],['Pirani connection','KF25',-50,140.132,90,'+Y','Gauge and elbow separate'],['Penning connection','KF25',50,140.132,90,'+Y','Gauge and elbow separate'],['Right lower spare','KF25',140.132,0,75,'+X','Blank cap/seal/clamp included'],['Right upper spare','KF25',140.132,0,225,'+X','Blank cap/seal/clamp included'],['Viewport axis','Clear openingD70',0,-132,105,'Y axis','Coordinates use outer door plane, not a purchased viewport flange face'],['Shutter shaft axis','Nominal roof clearanceD6.8',-65,0,310,'+Z','Preserve shaft axis and roof sealing land; actuator/seal belongs to subsystem4']]
with (P/'Frozen chamber interfaces.csv').open('w',newline='',encoding='utf-8-sig') as f:
 w=csv.writer(f);w.writerow(['Interface','Connection','X mm','Y mm','Z mm','Outward axis','Scope']);w.writerows(ports)
scope='''CB01 - CHAMBER AND LOADING DOOR: SINGLE SUPPLIER PACKAGE
24 November2026
Supplier selected by owner: Alpha Technovac, Mumbai.
Official supplier name found: Alfa Technovac LLP, Mira Road, Maharashtra.
Supplier reference: https://www.alfavacuum.com/

ORDER STRUCTURE
One complete custom vendor order. The supplier procures and integrates the
chamber/door components. No separate purchaser orders for its plates, flanges,
viewport, gaskets, hinges, handle, latches or associated chamber joint hardware.
The procurement workbook contains one package allowance; this scope does not
constitute a supplier quotation, an order or permission to contact the supplier.

FROZEN LAYOUT AND INTERFACES
This package extracts the currentR05 chamber layout without modifying geometry.
Datum: origin at internal floor centre. X right, Y rear, Z up.
Internal clear envelope200x200x300mm, gross12litres.
Nominal shell/roof/floor10mm. Front frame16mm. Door228x316x16mm.
Clear loading opening180x270mm. Left hinge axisX-118,Y-116, parallelZ.
Left wall remains blank. Door closes toward the front (negativeY).
Clear viewport diameter70mm, centreX0,Z105; outward reference door planeY-132.
Bottom centredISO63-K connection, chamber mating faceZ-45.
Top centredKF25 gun connection, chamber mating faceZ330.
RearKF25 centres: gasX0,Z210; PiraniX-50,Z90; PenningX+50,Z90.
RightKF25 spare centresY0,Z75 and225, both supplied blanked.
See Frozen chamber interfaces.csv for exact nominal external face coordinates.
Roof shutter shaft axisX-65,Y0; nominal holeD6.8 and existing top sealing land.
Fixed stage posts atX/Y+/-29, nominalD6x34, and baffle supports atX+/-44,Y0,
nominalD5x18, are included as mounting provisions. Removable stage, baffle and
shutter mechanism are separate subsystem items.

SUPPLIER PACKAGE INCLUDES
Stainless chamber shell, top/bottom plates, welded front frame and door;
all chamber weld-on connections; rated viewport assembly, seals and retainers;
door seal, hinges, handle and closure hardware; two right-port blank caps;
chamber-side mating clamps/centering seals, including topKF25 and bottomISO63
mating hardware; fixed internal mounting provisions; machining, welding,
cleaning, assembly and vacuum/helium-leak acceptance evidence.
Procurement drawings and tolerances, material grade/finish, weld/seal details
and window/pressure-load qualification are the supplier's responsibility.
Provide the measured leak-test result and method, not only an unqualified
statement of leak-tightness. State the supplied material and acceptance basis.

MATCHING REQUIREMENT AT THE GUN PORT
A25.4mm OD gun tube must pass freely through the full top joint while the
compression cap is loose. The model shows a27mm chamber-neck bore. A standard
KF25 centering ring may obstruct this tube; the supplier must provide compatible
clear-through mating hardware and verify the actual gland interface before
fabrication release. The functional tube/port axes and chamber layout are fixed.
The selected compression gland is separately procured by the owner from
https://www.ebay.com/itm/198508082866 , with LeskerQF25XVC100 as reference.
No assumption is made that the eBay fitting exactly matches Lesker internals.

SUPPLIER DETAILING WITHIN THE FROZEN LAYOUT
The STEP records packaging/nominal dimensions; its simplified flange profiles,
seal envelopes, glass thickness and hinge/latch outlines are not purchased
component or structural certifications. Use appropriate standard/rated hardware
and detail the fabrication within the stated layout, clear aperture and mating
interfaces. In particular, preserve the clear viewport and centre; the modeled
D94x6 glass is a reference envelope, not an independently qualified window.
Retainer holes are blind, nominalD4.2 x10deep in the16mm door, leaving6mm metal.
Preserve the chamber envelope and port positions. If the supplier identifies an
unavoidable functional-interface conflict, resolve it before manufacture rather
than silently altering the gun, pump or door interfaces.

SEPARATE FROM CB01
Gun, compression-gland body/cap/tube seal, turbo and backing pumps/controllers,
gauge bodies/elbows/electronics, MFC/VCR/adapters, removable stage and shutter,
water/power equipment, main stand, process tubing and external wiring.
Chamber-side flange clamps/seals and blank caps included here must not be
costed a second time under those downstream subsystems. Gland internal seal
parts remain with the purchased gland. Final installed vacuum tests must include
the separately installed feedthroughs; temporary test closures are to be provided
where needed for supplier chamber acceptance.

HANDOFF STATUS
Layout and functional interfaces frozen for supplier handoff. No CAD layout
change was made in preparing this package. Supplier detailing/manufacturing
release and the supplier quotation are pending. This does not certify a
fabrication release of the current generic seal/window representations.
'''
(P/'CB01 frozen layout and supplier scope.txt').write_text(scope,encoding='utf-8')
report={'package_id':'CB01','quantity':1,'procurement_method':'Custom vendor order','supplier_user_name':'Alpha Technovac, Mumbai','supplier_record':'Alfa Technovac LLP','supplier_url':'https://www.alfavacuum.com/','budget_allowance_INR':100000,'budget_basis':'Planning allowance set by assistant, not a supplier quote. GST/delivery and final scope price to confirm in quotation.','source_geometry':str(B/'Complete sputter system R05.step'),'layout_changes':0,'scope':'Complete chamber/door and chamber-side mating hardware; fixed mounting provisions included. Removable stage/shutter and external equipment excluded.','supplier_layout_solids':sum(len(q['shape'].Solids()) for q in parts),'supplier_layout_all_valid':True,'status':'Layout/interfaces frozen; supplier detailing and quotation pending','downstream_no_duplicate_items':['Chamber weld-on flanges','Door/window hardware and seals','Chamber-side KF clamps/centering seals','ISO63 inlet clamp/centering set','Right spare blank caps','Fixed stage/baffle supports']}
(P/'CB01 package record.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
with zipfile.ZipFile(P/'CB01 supplier handoff.zip','w',zipfile.ZIP_DEFLATED) as z:
 for file in P.iterdir():
  if file.suffix in ['.step','.csv','.txt']:z.write(file,file.name)
print('Supplier layout frozen and packaged; no individual procurement lines',flush=True)
