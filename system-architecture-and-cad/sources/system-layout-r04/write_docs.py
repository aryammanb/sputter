from pathlib import Path
import json,shutil,csv
P=Path(__file__).resolve().parent
text='''COMPLETE SPUTTER SYSTEM R04 — MAIN DESIGN WALKTHROUGH
24 November 2026

Open Complete sputter system R04.step for the assembled system, or the loading
STEP for the open door and parked shutter. Units are millimetres. Separate
assemblies include the latest 141-instance gun, compression fitting, revised
front door and utilities. The gun-only file uses its original design coordinate
system; the full assembly places the gun in the chamber.

The main MP4 has narration, chapter markers and switchable English captions.
It incorporates the seven relevant chapters of the earlier compression-fitting
animation. The final standalone-review closing was omitted.

NEW IN R04
- Argon cylinder/regulator envelopes and continuous 6mm OD gas tubing.
- Tube seated in existing push fitting: mouth Y360.196, end Y344.196,
  engagement16. This engagement is provisional, not a manufacturer dimension.
  Tube ID4 is a chosen representative bore. OD6 and nominal socket fit are
  explicitly modeled. Gripper internals and pressure compatibility are not.
- Cooling system1 with OD4/ID2.5 extensions to existing gun hoses.
- Cooling system2 with OD9/ID6 reference hoses to turbo cooler. Edwards manual
  calls for approximately6mm ID reinforced hose/clips or1/8BSP direct fittings.
  Cabinets, hose routes and end fittings are representative; duty/flow pending.
- Representative power supply, RF matching network, cable and earth bond.
  RF configuration is shown. DC configuration bypasses the RF matching network.
- Viewport centre lowered fromZ175 toZ105. Same clear diameter70. Door aperture,
  glass, gasket, bezel and screws move together. Checked at gap100.

VIEWPORT EVIDENCE
Near-face ray check.json samples72 points on a geometric ring R20 atZ136,
5mm below the target faceZ141. Both aperture end planes and all gun triangles
are tested. At eye(0,-400,20),47/72 ring points are unobstructed with the revised
window. The original window passes none from this eye. The original window
also fails at the higher sampled eyes that do pass through its aperture.
At eye(0,-400,-20), the revised aperture gives72/72 clear samples. A separate
ring atZ125 checks the region below the shield. This establishes geometric
access; actual visible glow extent/brightness is not predicted. The illustrated
plasma is intentionally schematic. Visibility across all gun heights or through
a coated window is not certified. See Viewport sightline checked.png.

MAGNETRON
Latest selected candidate: centre2xD20x10N42, outer12 stacks of2xD6x10N42 onPCD58,
centreN and outerS facing target. Area proxy1.08 is not a flux ratio. Mechanical
changes are to the copper body, backplate, yoke, water seals and local routing.
The magnetic study uses assumedN42 properties, a referenceAISI1010 steel curve
and a nonmagneticD50.8x2 target. Near-target calculated parallel field is
approximately89.5..99.5mT, mean95.1mT, racetrackR19.99. This is a magnetostatic
calculation, not a plasma, erosion, deposition or thermal simulation. Balanced
design intent is distinguished from experimentally established topology.

DIMENSIONS
Internal chamber200x200x300 (12litres gross); shell10; door228x316x16.
StageD90x6, topZ40; substrate50x50x1, topZ41.
Target-substrate gap75..150, default100; default target faceZ141.
Shutter sheet1, undersideZ53, substrate clearance12, midplane drop240,
parked rotation80degrees. Inherited internal clearance checks are included.
Full dimension schedule and per-component scope are provided asCSV/JSON.

ENGINEERING STATUS
This is a dimensioned nominal system layout, not a fabrication release.
Purchased interfaces, compression-fitting threads/seal stack, clear bore,
rotary shutter seal, vessel/window strength, materials, tolerance stacks,
thermal loads, coolant flow, gas compatibility, RF/DC insulation and grounding
need qualification. The imported supplierRV3 solid retains its existing
geometry defect; other exported solids are checked. RV3 is a reference, not a
confirmed backing-pump purchase. EXT70 is reconstructed exterior geometry;
the reference nativeKF16 outlet is adapted toKF25, omit adapter if the actual
purchased pump hasKF25. Gauge housings are generic. No blanket exterior
collision or hose-bend certification is claimed.

Still to specify for an operating machine: compatible turbo controller/cable,
gauge electronics and MFC power/control, interlocked cooling/pressure/source
enable, vent procedure and valve hardware, backing-pump exhaust/oil-mist
handling and protective enclosure as applicable. These are stated in the video;
the cabinets shown do not constitute a wired control design.

SOURCE REFERENCES
Edwards manufacturer manual (hosted copy):
https://www.idealvac.com/files/manualsII/Edwards_EXT_70_250_Turbo_Pump_Manual.pdf
EdwardsRV3 supplierCAD:
https://www.idealvac.com/files/cad/P101919.step
HORIBAMFC reference drawing:
https://static.horiba.com/fileadmin/Horiba/Semiconductor/Resources/Manual_Downloads/others/I030106200.pdf
RF matching and target conductivity:
https://angstromengineering.com/tech/magnetron-sputtering/rf-sputtering/
https://www.lesker.com/newweb/process_instruments/processequipment_powersupplies_rf.cfm
Gas adapters/selected push fitting: Purchased component references.csv.
Magnet selection: confirmed recent magnetron chat and local mechanical study.
The older mechanical-study text predates the magnetic study; current magnetic
assessment results are included separately to avoid treating that old status
as the current simulation status.

REPRODUCIBILITY
Authoring scripts remain in the workspace folder. They reuse the preceding
R01/R02/R03 sources and the gun project at their original relative paths.
The delivered STEP assemblies are standalone; scripts require the project tree.
'''
(P/'README.txt').write_text(text,encoding='utf-8')
shutil.copy2(P/'preview-16.png',P/'Viewport sightline checked.png')
S=P/'Magnetic assessment';S.mkdir(exist_ok=True);B=P.parents[2]/'simulations'/'magnetic-model'
for n in ['Simulation assessment.txt','Assessment results.json','fine_nominal_metrics.json','Target field map.png','Field section.png']:shutil.copy2(B/n,S/n)
with (P/'Purchased component references.csv').open('a',newline='',encoding='utf-8-sig') as f:
 w=csv.writer(f);w.writerow(['Turbo cooler hose','Edwards manual: approximately6mm ID reinforced hose','https://www.idealvac.com/files/manualsII/Edwards_EXT_70_250_Turbo_Pump_Manual.pdf','OD9/ID6 is nominal reference; clips/adapters pending'])
print('Main documentation and evidence saved')
