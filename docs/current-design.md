# Current design and revision control

The authority for this snapshot is [design/current.json](../design/current.json), dated 24 November 2026. “Latest” is determined by engineering revisions and recorded selections, not by a filename or filesystem timestamp.

| Layer | Current artifact | What it establishes |
|---|---|---|
| Gun | [R06 STEP](../chamber-design/coolant-fitting-r06/Magnetron%20R06.step) | 141-component gun with revised M5 fittings/backplate |
| Native gun | [R06 SolidWorks assembly](../chamber-design/coolant-fitting-r06/SolidWorks%20R06/Magnetron%20R06%20-%20M5%20coolant%20fittings.SLDASM) | Fixed components at checked positions; native passage and tap-drill cuts in backplate |
| Complete context | [R06 system STEP](../chamber-design/coolant-fitting-r06/Complete%20sputter%20system%20R06.step) | R06 gun in the retained R04 chamber/utilities layout, with R05 target position correction |
| Target/clamp | [R05 notes](../chamber-design/target-clamp-r05/READ%20FIRST%20-%20Clamp%20R05.txt) | D50.8 × 3.175 target, revised shoulder/lip, M3×10 screws |
| Chamber supplier handoff | [CB01 scope](../chamber-design/chamber-supplier-package/CB01%20frozen%20layout%20and%20supplier%20scope.txt) | Frozen interfaces and single vendor package; quote/manufacturing release pending |
| Procurement | [Workbook](../procurement/Sputter%20system%20procurement.xlsx) | Latest saved selections and planning allowances |
| Gas selection | [MFC R04](../chamber-design/Argon%20MFC%20selection%20R04%20-%20500%20sccm.txt) | Owner-selected STEC SEC-4400MC-G2 Ar 500 sccm; calibration/interfaces pending |
| Field | [Current assessment](../simulations/current-target-r06/README.md) | Saved FEM field sampled at the current target plane |
| Explanations | [Current design walkthroughs](design.md#current-walkthroughs) | R06 STEP-derived views with current selections called out |

## Revision sequence

1. Original reconstruction and exploratory variants establish the source architecture.
2. Combined gun R03 and twelve-stack study establish the revised magnetic/cooling head.
3. Chamber R01 and compression fitting R02 develop chamber and mounting concepts.
4. Full-system R03 integrates pumping and gas equipment. System R04 adds utilities, revised viewport and current dimensional layout.
5. R05 fits the 3.175 mm aluminium target, revises clamp/screws and raises the gun 1.175 mm to preserve the target plane.
6. R06 replaces the internal coolant fitting geometry and native backplate ports. Target, clamp and chamber arrangement are retained.
7. This repository snapshot adds current media and a target-plane field resampling assessment. It does not introduce another CAD revision.

## Known representation mismatches

- The context RV3 shape is a legacy reference with an invalid solid. Procurement selects INDOVAC HV2-150. Its replacement geometry remains pending.
- The legacy MFC housing is a dimensional reference. Current selection is STEC SEC-4400MC-G2 Ar 500 sccm. Fittings are accepted as compatible by the owner; PE-D20 with an owner-built perfboard adapter and shielded cable is selected. Exact G2 pin mapping, electrical checks, envelope and calibration remain to verify.
- Chillers, power equipment, gauge housings and some fittings are representative. Final supplier dimensions, connectors and ratings need checking.
- R06 native SolidWorks deliverable is the gun only. The full system is STEP context, not a native mated system assembly.
- The combined design guide selects the corrected R06 system and gun walkthroughs. Earlier system reviews, screw-only shutter illustrations and prior target/fitting videos remain historical artifacts.
- Copper joining proposals predate the current backplate. Proposed bonding lands are not completed qualified joining details. Use R06 geometry and the engineering status in its notes.

## Updating this repository

For a new revision, update CAD and its geometry evidence first, update procurement interfaces, then regenerate media and applicable calculations. Change `design/current.json`, document the change in `CHANGELOG.md`, rebuild file hashes and run repository validation. A new export or new screenshot alone does not establish a new engineered revision.
