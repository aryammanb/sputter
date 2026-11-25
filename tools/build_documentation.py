"""Build the repository reading paths and procurement views from frozen sources."""
from pathlib import Path
from urllib.parse import quote
import csv, json

ROOT=Path(__file__).resolve().parents[1]
DOC=ROOT/'docs';DOC.mkdir(exist_ok=True)

def write(path,text):
    p=ROOT/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text.strip()+'\n',encoding='utf-8')

def link(label,path,depth=1):return f'[{label}]('+('../'*depth)+quote(path,safe='/')+')'
R06='chamber-design/coolant-fitting-r06/'
R05='chamber-design/target-clamp-r05/'
R04='chamber-design/main-system-r04/'
SIM='advanced-tinkering-original/balanced-twelve-stack-study/magnetic-simulation/'

def main():
    # Export exact instance metadata; legacy source names are retained as provenance.
    register=json.loads((ROOT/'chamber-design/coolant-fitting-r06/R06 component register.json').read_text())
    (ROOT/'design').mkdir(exist_ok=True)
    with (ROOT/'design/current-component-register.csv').open('w',newline='',encoding='utf-8') as f:
        writer=csv.writer(f);writer.writerow(['instance','group','role','source_name','solid_count','valid','volume_mm3','note'])
        for i,q in enumerate(register,1):writer.writerow([i,q['group'],q['role'],q['name'],q['solid_count'],q['valid'],q['volume_mm3'],q['note']])
    assessment=json.loads((ROOT/'simulations/current-target-r06/assessment.json').read_text())['current']
    manifest = json.loads((ROOT/'design/current.json').read_text(encoding='utf-8'))
    write('design/current.json',json.dumps(manifest,indent=2))
    write('README.md', (ROOT/'tools/templates/README.md').read_text(encoding='utf-8'))
    write('docs/current-design.md',f'''
# Current design and revision control

The authority for this snapshot is [design/current.json](../design/current.json), dated 24 November 2026. “Latest” is determined by engineering revisions and recorded selections, not by a filename or filesystem timestamp.

| Layer | Current artifact | What it establishes |
|---|---|---|
| Gun | {link('R06 STEP',R06+'Magnetron R06.step')} | 141-component gun with revised M5 fittings/backplate |
| Native gun | {link('R06 SolidWorks assembly',R06+'SolidWorks R06/Magnetron R06 - M5 coolant fittings.SLDASM')} | Fixed components at checked positions; native passage and tap-drill cuts in backplate |
| Complete context | {link('R06 system STEP',R06+'Complete sputter system R06.step')} | R06 gun in the retained R04 chamber/utilities layout, with R05 target position correction |
| Target/clamp | {link('R05 notes',R05+'READ FIRST - Clamp R05.txt')} | D50.8 × 3.175 target, revised shoulder/lip, M3×10 screws |
| Chamber supplier handoff | {link('CB01 scope','chamber-design/chamber-supplier-package/CB01 frozen layout and supplier scope.txt')} | Frozen interfaces and single vendor package; quote/manufacturing release pending |
| Procurement | [Workbook](../procurement/Sputter%20system%20procurement.xlsx) | Latest saved selections and planning allowances |
| Gas selection | {link('MFC R04','chamber-design/Argon MFC selection R04 - 500 sccm.txt')} | Owner-selected STEC SEC-4400MC-G2 Ar 500 sccm; calibration/interfaces pending |
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
''')
    write('docs/design.md', (ROOT/'tools/templates/design.md').read_text(encoding='utf-8'))
    write('docs/system.md', '# System architecture\n\nContinue to [System architecture and CAD](design.md), including CAD downloads, current walkthroughs and essential rendered views.\n')
    write('docs/cad.md', '# CAD\n\nContinue to [System architecture and CAD](design.md#cad-downloads) for downloads, current walkthroughs, rendered views and editing notes.\n')
    write('docs/engineering.md',f'''
# Engineering dossier

This dossier explains the reasoning supported by the supplied records. Detailed dimensions and checks remain linked so a reviewer can inspect the original evidence. The machine remains a prototype engineering study.

## Magnetron and magnetic return circuit

The selected head uses a centre pair of D20×10 N42 discs and twelve outer pairs of D6×10 N42 discs on PCD58. Centre N and outer S face the target. The nominal pole-area ratio 1.08 guided the candidate layout, while the FEM study checks near-target field. It does not establish exact balanced topology.

The model imports the proposed yoke, assumes an AISI1010 reference B-H curve and N42 remanence of 1.30 T at 20 °C. The actual steel grade/heat treatment and magnet properties remain unverified. Copper, target, coolant and insulation use relative permeability 1. Surrounding ferromagnetic equipment is omitted. See [simulation evidence](simulations.md) for numerical checks and the current target plane.

## Target, clamp and fasteners

The selected target is VritraTech Al99.99%, D50.8×3.175. Its back still seats at source Y0. R05 moves the clamp shoulder to Y3.175, retains front Y5 and leaves a 1.825 mm axial lip. The minimum aperture is D47.8, with a 0.25 mm contact-side chamfer and front flare D49.45. The nominal bearing band is 1.25 mm wide before actual target bevels.

Twelve M3×10 socket screws replace M3×8. Nominal straight shaft/tap-drill envelope overlap increases from about 3.55 to 5.55 mm, with 1 mm tip-to-pilot-bottom clearance. This is geometric overlap, not a full-thread or strip-strength rating. Real thread depth, copper strength, target thickness tolerance, preload, bottoming and thermal expansion require drawings and qualification. No tightening torque has been established.

The entire gun is raised 1.175 mm so the target front remains Z141 at the default gap. A nominal 1 mm live-clamp/grounded-shield gap remains. It is not an RF voltage rating. Evidence: {link('R05 redesign checks',R05+'Clamp redesign and verification.json')} and {link('R05 notes',R05+'READ FIRST - Clamp R05.txt')}.

## Copper cooler, closure and coolant ports

R06 selects 2× SMC KQG2S04-M5, OD4 tubing, M5×0.8 male thread, nominal body OD9 and installed projection 14.1. Two D14 yoke openings leave 2.5 mm radial body clearance, and the collet extends 4.1 mm beyond the 10 mm yoke.

The backplate ports are at native X±18/Z0. Old D7.95 counterbores and D5 passages are removed. Revised D3 passages run through, with D4.2 tap drills 5 mm deep from rear Y−22.5 and a specification of M5×0.8-6H, useful thread ≥4 mm. The retained flat seat uses the manufacturer's specified M5 gasket. Thread tape does not replace that gasket interface.

The SMC vacuum-retention caveat, pressurized-water sealing, gasket seat tolerances, tube bend radius and compatibility remain unresolved. Current checks found no new non-thread geometric overlaps, with threaded engagement overlaps explicitly classified. No zero-leakage assertion follows. Historical copper-bonding explanations are proposals, not a completed joining revision. Evidence: {link('R06 scope notes',R06+'READ FIRST - Coolant fittings R06.txt')} and {link('Fitting selection','chamber-design/coolant-fitting-selection/Selection and required CAD changes.json')}.

## Cooling and electrical isolation

Procurement retains separate CW-5000-style gun and turbo loops. The gun budget uses a 300 W heat basis and 0.5 L/min target; the selected RF source is 200 W. That budget is conservative planning, not proof of a 300 W operating rating. The turbo loop targets 15 °C and 0.5 L/min commissioning flow. The recorded manufacturer minimum is 0.25 L/min at 15 °C; verify against the exact purchased unit and manual.

Actual coolant flow at installed head, pressure limits, heat transfer, target contact, magnet temperature, chiller duty, conductivity and live-cathode isolation still need measurements and design qualification. No completed thermal or CFD analysis is present. See procurement cooling tabs and [verification gates](verification.md).

## Vacuum and argon delivery

The selected route is chamber → EXT70 → one rotary vane pump, with no separate roughing bypass. Procurement selects INDOVAC HV2-150. The RV3 solid in context remains a legacy reference and has a known topology defect. The turbo exterior is reconstructed reference geometry; the outlet adapter depends on the actual received port.

The owner-selected MFC is STEC SEC-4400MC-G2, listed for Ar 500 sccm. Gas calibration, valve/interface configuration and low-flow accuracy remain to verify. For the recorded 0 °C standard flow reference and 20 °C gas assumption, throughput is `Q = 0.018124 × flow_sccm` mbar·L/s. At 500 sccm, Q≈9.062 mbar·L/s. With effective speed 65 L/s, p≈104.6 mTorr. The 65 L/s example uses an N2 rating; actual installed Ar pumping speed is unverified. Pressure follows installed speed, conductance and gas load, and must be measured.

The earlier 42 mTorr ignition trial idea remains unqualified. The new 500 sccm range adds flow headroom; it does not establish an ignition threshold or an allowable full-flow operating point. Turbo gas load, backing pressure and drive power limits must be checked before commanding full flow. Consider low-flow accuracy at intended deposition flows. Evidence: {link('MFC R04 engineering assessment','chamber-design/Argon MFC selection R04 - 500 sccm.txt')} and procurement tabs 05/07.

## Chamber, window, stage and mounting

The chamber package CB01 freezes nominal interfaces for a single Alfa Technovac order. Its INR100,000 is a planning allowance, not a quotation. Supplier scope includes shell, welded ports, door/window/seals, mating hardware and fixed mounting provisions. Pumps, gauges, the gland, removable stage/shutter and equipment stand remain separate.

The selected eBay compression gland is not confirmed as the Lesker reference model. A 25.4 mm gun tube must pass through the complete KF25 centering/seal/gland stack. Nominal model clearance is not purchased-hardware compatibility. The supplier must qualify bore, seal stack and tolerances.

The D70 viewport centre was lowered to Z105. R05 ray checks give 43/72, 55/72 and 31/72 clear sampled rays at gaps 75/100/150 from the stated eye position. These are partial geometric ring samples, not percentages of visible plasma. Window coating, real eye positions and glow distribution are unmodeled. Blind door retainer pilot holes have retained backing; actual threads/engagement still require release detail.

Nominal shell thickness, seals, welds, window stress and door closure are not supported by a completed structural FEA or released pressure design. The stage/shutter package includes a developed blank with a chosen K-factor; material, bend allowance and fabricated fit must be agreed with the shop.

## RF, controls and integration

Procurement selects a provisional Omicron 200 W RF source and matching network. Earlier 300 W language is superseded as an operating selection. Connector/coax insulation, matched-side voltage/current, cathode isolation, protective earth/RF bonds and water-loop isolation remain engineering checks. A nominal SMA mechanical envelope does not establish suitability for this source.

The controls budget includes emergency stop, door switch, flow/temperature inputs, pressure interface and RF permit logic. A proposed permit requires door closed, suitable measured pressure, healthy gun cooling and reset emergency circuit. Loss of a required condition must remove RF permission; reset must not automatically restart it. Final fault handling and turbo run-down behavior depend on the actual equipment. No completed wiring schematic or assessed safety performance level is claimed.
''')
    write('docs/decisions.md',f'''
# Design decision register

Dates identify the supplied project snapshot, not a claim that a part was ordered or received. Each selection remains subject to its recorded interface and qualification limits.

| ID | Decision | Reason and consequence | Evidence |
|---|---|---|---|
| D01 | Twelve outer D6×20 stacks and D20×20 centre, N42 | Retain selected magnetic circuit and yoke; assess field numerically. Area ratio alone does not prove balance. | Original magnetic assessment and [current resampling](../simulations/current-target-r06/README.md) |
| D02 | D50.8×3.175 Al target | Fits selected stock target. Requires R05 shoulder/lip and screw changes, plus target-plane reassessment. | {link('R05 notes',R05+'READ FIRST - Clamp R05.txt')} |
| D03 | Raise gun 1.175 mm | Preserves target face Z141 and default 100 mm gap after thicker target. | R05 redesign checks |
| D04 | M3×10 target screws | Increases nominal engagement without moving seats; real useful thread depth/preload pending. | R05 checks and dimension schedule |
| D05 | SMC KQG2S04-M5 internal coolant fittings | Compact OD9 envelope fits D14 yoke openings. Revises backplate to M5 ports; seal qualification stays open. | {link('R06 notes',R06+'READ FIRST - Coolant fittings R06.txt')} |
| D06 | One CB01 chamber/door vendor order | Supplier integrates shell, ports, window/seals and chamber hardware; avoids double purchase. | {link('CB01 scope','chamber-design/chamber-supplier-package/CB01 frozen layout and supplier scope.txt')} |
| D07 | Selected purchased KF25/1-inch gland | Use existing selected eBay source; Lesker is a dimensional reference only. Full 25.4 mm passage must be verified. | Gun mount procurement check and workbook |
| D08 | Direct turbo-to-backing route | Current selected one-pump topology; no separate roughing bypass. | MFC R03 and plumbing reference |
| D09 | EXT70/EXDC80 two-pump lot | One installed, one spare; selected 80 V supply recorded separately. | Procurement tab 05 |
| D10 | INDOVAC HV2-150 backing pump | Local sourcing selection; old RV3 model remains reference only. | Procurement tab 05 |
| D11 | STEC SEC-4400MC-G2, Ar 500 sccm MFC | Owner selection supersedes R01-R03; fittings accepted by owner, PE-D20 retained and perfboard adapter selected; exact wiring, calibration and low-flow checks pending. | MFC R04 |
| D12 | Independent gun/turbo cooling loops | Separate flow/temperature duties and planned isolation checks. | Procurement tabs 08/09 |
| D13 | 200 W RF source + matcher | Current source selection supersedes earlier 300 W operating idea; old cooling basis retained. | Procurement tab 10 |
| D14 | Viewport centre Z105 | Improves sampled sightlines below the target; does not predict glow or all-height visibility. | R04/R05 ray checks |
| D15 | Fixed stage and manually rotated shutter | Local fabrication + existing stock; no motor/actuator purchase selected. | Stage/shutter fabrication record |
| D16 | R06 media derived from exact latest STEP | Avoids presenting R04 or older magnetron media as current. | [Media provenance](../media/provenance.json) |
''')
    write('docs/simulations.md',f'''
# Simulation and calculation evidence

## What exists

| Work | Evidence and scope | Current applicability |
|---|---|---|
| 3D nonlinear magnetostatic FEM | Meshes, code, B-H data, solved fields, metrics, analytical comparison | Original target 2 mm; current plane assessed separately |
| Mesh refinement | Ring mean change about 0.44% | Numerical verification for original sampling region |
| Air-domain/remesh check | Coarse ring mean change about 0.11% | Numerical check, not full hardware uncertainty |
| Independent analytical comparison | Unit-permeability magnets vs Magpylib, 9,600 sample points; refined vector L2 error 2.33% | Solver verification without steel |
| Steel curve sensitivity | Reference H values scaled 0.5× / 2× | Narrow assumed-material sensitivity, not a bound for arbitrary steel |
| Target spacing sensitivity | Nonmagnetic target plane variants in saved results | Historical discrete samples; new 3.175 mm plane below |
| Current target resampling | [Current results](../simulations/current-target-r06/README.md) | 3.175 mm target, 0.25 mm above face |
| Geometry/interference | R05/R06 Boolean checks and native export/reference checks | Nominal CAD, classified thread overlaps |
| Viewport ray tracing | R04/R05 sampled observation rings | Geometric sightlines at defined eyes/gaps |
| Gas throughput / pressure | MFC R01–R04 calculations | R04 500 sccm selection is current; actual effective Ar speed unknown |

## Original magnetic model

The scalar-potential FEM assumes 13 contiguous magnet cylinders representing 26 touching discs, nonlinear reference AISI1010 yoke, N42 remanence 1.30 T, recoil μr 1.05 and 20 °C. Nonmagnetic materials use μr=1. The refined mesh contains 114,336 vertices and 708,128 tetrahedra. Zero scalar potential is imposed on an enclosing ±80 mm box; a larger ±120 mm coarse-domain check is retained.

The original 2 mm target assessment calculated about 95.1 mT mean parallel field at 0.25 mm above its face, with about 19.99 mm mean normal-field zero-contour radius. This result belongs to that target plane. The reported final residual and mesh checks measure numerical solution behavior, not agreement with the physical assembly.

Read {link('full original assessment',SIM+'Simulation assessment.txt')}, {link('numerical results',SIM+'Assessment results.json')}, {link('mesh script',SIM+'make_mesh.py')}, {link('solver',SIM+'solve_field.py')} and {link('analysis',SIM+'analyze_field.py')}. The repository retains native `.msh`, compressed mesh arrays, solved `.npz` fields, coarse/wide/steel cases and logs for inspection and rerun.

## Current target plane

Current R05/R06 target thickness is 3.175 mm, and pole-to-face spacing is 5.675 mm. The new [assessment](../simulations/current-target-r06/assessment.json) uses the saved refined solution at simulation Z3.425, 0.25 mm above the new face. Original magnets and yoke remain unchanged, and changed target/copper/fittings are all μr=1 in this model. Resampling therefore preserves the same magnetic material problem under these assumptions. No new mesh or nonlinear solve is claimed.

| Metric | Current calculated result |
|---|---|
| Mean parallel field on B-normal zero contour | {assessment['Bparallel_mean_mT']:.3f} mT |
| Minimum / maximum | {assessment['Bparallel_min_mT']:.3f} / {assessment['Bparallel_max_mT']:.3f} mT |
| Mean contour radius | {assessment['radius_mean_mm']:.3f} mm |
| Minimum target-edge margin | {assessment['target_edge_margin_min_mm']:.3f} mm |
| Sampled angles with crossing | 360 / 360 |

![Current field assessment](../simulations/current-target-r06/current-racetrack.png)

The script first reproduces the original mean to within 0.05 mT (actual difference is recorded), then samples the new plane using linear crossing interpolation. It does not rerun original mesh convergence at the new plane. The old error metrics are not an uncertainty certificate for this result.

## Analyses not supplied

No completed plasma/kinetic, RF sheath, ignition, deposition-thickness/erosion, thermal/CFD, coolant pressure-drop, vessel/window structural FEA, fatigue or RF breakdown simulation is present. A rendered plasma or material stream in older media is illustrative. No such visualization is evidence of a solved physical model. Balanced topology and a specified operating power remain unproven.

Proposed next evidence is a calibrated Hall-probe map at known heights above the actual target, followed by instrumented cooling and discharge commissioning. Requirements are listed in [verification](verification.md).
''')
    write('docs/verification.md','''
# Verification, qualification and release gates

Completed checks are evidence of their stated scope. They do not release the machine for fabrication or operation.

| Area | Supplied evidence | Required next evidence |
|---|---|---|
| Gun geometry | R05 interference checks; R06 changed-part checks; native gun 141 valid solids | Released drawings, datums, materials/finishes and tolerances |
| Coolant joints | Nominal M5 ports/gasket seats and fitting clearance | Vendor suitability, specified gasket compression, thread depth, leak/pressure tests with acceptance criteria |
| Target clamp | Revised lip/shoulder and screw engagement envelopes | Target tolerance, preload/strip strength, stiffness and thermal contact qualification |
| Magnet circuit | Nonlinear FEM and numerical checks; current-plane sampling | Actual magnet/yoke material data and calibrated Hall-probe comparison |
| Thermal | Cooling selections and planning heat basis | Measured installed flow/head, pressure drop, chiller capacity and temperatures under staged load |
| Chamber/window | Frozen nominal interfaces and supplier scope | Supplier structural basis, rated window/closure, weld/material documents and measured leak acceptance |
| Compression gland | Model clearance and reference fitting | Identify actual hardware; verify full 25.4 mm tube passage, sealing, retained support and travel |
| Vacuum | Selected pump topology and equipment budget | Received-model manuals, controller/cable compatibility, gas-load/backing-pressure limits and pumping tests |
| MFC/gas | Owner range selection; throughput calculation | Exact Ar calibration, low-flow accuracy, regulator/valve compatibility, measured pressure response |
| RF/electrical | Provisional source/matcher and controls budget | Source interfaces, cable/connector ratings, electrical design, grounding/isolation tests and qualified fault logic |
| Stage/shutter | Separate CAD/developed blank and stock items | Bend tolerances, installed clearance/travel and shaft seal qualification |
| Procurement | Workbook selections and allowances | Actual quotes/receipts, tax/freight, received condition, serials and acceptance records |

## Proposed commissioning sequence

These are planning gates, not an operating procedure for energized equipment. Establish final procedures using actual equipment manuals and qualified design review.

1. Freeze and inspect received hardware against the interface register. Resolve RV3/HV2-150, MFC, turbo outlet and cabinet mismatches.
2. Complete manufacturing drawings and supplier acceptance requirements. Confirm vessel/window suitability, materials, seals, threads and welding/cleaning.
3. Qualify each pressurized coolant joint before installation. Establish leak-test method and acceptance threshold, then test installed cooling paths and electrical isolation.
4. Verify protective earth, RF bonds, insulation, emergency/reset behavior, door/pressure/flow/temperature interlocks and actual fault handling without enabling the discharge.
5. Verify pump/controller/cable/supply compatibility. Establish backing, vent, exhaust/oil-mist and turbo run-down procedures from actual manuals.
6. Establish vacuum integrity, base pressure and argon flow/pressure response within pump load limits. Document calibrated gauges and MFC basis.
7. Map the cold magnetic field above the actual target and compare with the model, keeping probe position and orientation records.
8. Commission at staged source conditions with measured coolant flow, temperatures and pressures. Record ignition/stability, faults, deposition and erosion before assigning an operating envelope.

## Current repository checks

The [validation directory](../validation/README.md) records file hashes, local-link checks, media stream/decode checks, workbook export status and CAD read results. These repository checks establish package integrity and readability. They are distinct from the physical engineering gates above.
''')
    write('docs/reproducibility.md',f'''
# Reproduction and package checks

## Obtain the complete snapshot

```sh
git clone https://github.com/aryammanb/sputter.git
cd sputter
python tools/validate_repository.py
```

The repository uses ordinary Git files, without Git LFS pointers or external submodules. A full clone includes current CAD, procurement, new media and retained simulation data. GitHub may require downloading a raw binary or cloning to open it. Read access requires permission while the repository is private.

## Read without a CAD license

Markdown, CSV, JSON and transcripts work directly in GitHub. Use a STEP-capable viewer for neutral CAD. Native SLDASM/SLDPRT editing requires a compatible SolidWorks installation; neutral STEP does not preserve native feature history. MP4 files use H.264 video/AAC audio and English subtitle tracks.

## Dependencies and generated artifacts

Use Python 3.13 as the original authoring environment. [requirements-engineering.txt](../requirements-engineering.txt) records the versions used in this environment. For the original FEM pipeline, use {link('its pinned requirements',SIM+'requirements.txt')}. Install into a separate virtual environment rather than modifying a system interpreter. Native SolidWorks regeneration also requires Windows/SolidWorks; its saved deliverables can be read without rerunning native automation.

Commands for the new reproducible layer, from the repository root:

```sh
python tools/export_procurement.py
python tools/reassess_current_field.py
python tools/build_current_media.py
python tools/build_documentation.py
python tools/validate_repository.py
```

`export_procurement.py` reads the checked-in XLSX and creates CSV plus cell/formula records without modifying/recalculating the workbook. Formula results are the workbook's saved caches. `reassess_current_field.py` requires the saved fine nominal field and produces the new target-plane assessment and plots. `build_current_media.py` imports the exact R06 system STEP, creates a view mesh, and renders the current media. It uses Windows System.Speech/Microsoft David for synthetic narration; its transient WAVs/encoder files stay under ignored `tools/.work`. The checked-in mesh is an export convenience, not authoritative engineering geometry.

## Original FEM reruns

The following mirrors the original scripts' interface. It can overwrite original generated evidence; run in a disposable clone and compare results before accepting changes.

```sh
cd advanced-tinkering-original/balanced-twelve-stack-study/magnetic-simulation
python make_mesh.py coarse 1.8 80
python solve_field.py coarse nominal
python analyze_field.py metrics coarse_nominal
```

See the actual solver CLI in `solve_field.py` for supported material variants and analytic mode. The original scripts and full numerical outputs are retained. Exact bitwise FEM reproducibility is not promised across mesh generators, sparse solvers or platforms. Compare metrics and physical assumptions, not only file hashes.

## CAD source and portability limits

Historical CAD/video scripts are included for engineering traceability. Several original scripts contain Windows paths, COM automation, local font/voice choices or links to earlier study files. They have not all been ported or rerun in a clean environment. Their presence does not imply a one-command rebuild of every historical assembly. The current standalone STEP/native package is the practical design handoff.

The current R06 CadQuery preparation source is {link('prepare_r06.py','chamber-design/coolant-fitting-selection/prepare_r06.py')}; it reuses R05 geometry and metadata from the repository root. That script changes generated CAD files, so run in a disposable clone. Native build plans preserve original path strings as provenance; adapt paths for regeneration. Original reconstruction scripts may need externally sourced reference video; that third-party video/browser cache is deliberately not republished.

## Updating integrity records

`tools/package_repository.py` selects meaningful source files, excludes application profiles/caches, old videos and repetitive intermediate renders, and writes `validation/file-manifest.json`. It does not move or delete local originals. Run it after adding a revision or generated artifact, then run validation. Do not treat a regenerated manifest as proof that changed engineering remains correct.
''')
    write('docs/sources.md','''
# Sources, attribution and rights

The project builds on a reconstruction and subsequent changes to an Advanced Tinkering magnetron concept. The historical source workspace, design notes, change registers and authoring scripts preserve that lineage. This snapshot does not assert ownership of the original design or assign an open-source license.

Supplier CAD, manuals, catalogs and drawings remain third-party reference materials. Their inclusion in this private engineering record does not grant redistribution rights. Review permissions and replace restricted references with links before making the repository public. The original downloaded source video, browser profiles and cached third-party media are not included.

## Reference locations

| Topic | Local evidence |
|---|---|
| R06 fitting selection | `chamber-design/coolant-fitting-selection/` catalog and selection record |
| Current backplate/native CAD | `chamber-design/coolant-fitting-r06/` checks and notes |
| Selected target/clamp | `chamber-design/target-clamp-r05/` notes and dimensional checks |
| Chamber vendor scope | `chamber-design/chamber-supplier-package/` CB01 scope, interface schedule and source references |
| Turbo/controller | Saved manual and procurement records; full-system supplier reference directory |
| MFC dimensional reference | Legacy HORIBA drawing (reference only) and R04 500 sccm selection note |
| Magnetic formulation/materials | Original `Simulation assessment.txt`, solver B-H data and requirements |
| Procurement selections/quotes | Current workbook, readable cell/CSV exports and selected support records |

URLs in the original notes and workbook are recorded sourcing references as of the project work. This repository preparation does not reverify current seller availability, quotations, exchange rates or published specifications. Prices in the documentation are dated planning records.

## Newly generated explanations

Current screenshots are rendered from the R06 system STEP. Field plots are generated from the retained FEM solution at the current target plane. Narration uses Windows Microsoft David Desktop and is synthetic. No generated image is presented as a photograph of physical hardware, and no video is presented as a record of a working machine.
''')
    write('CHANGELOG.md','''
# Change log

## 2026-11-24 — Repository engineering snapshot

- Select R06 native gun and system context as the current CAD, retaining R05 target/clamp and R04 system layout.
- Preserve the latest procurement workbook unchanged; add 13 CSV tabs plus exact cell/formula-cache exports.
- Add a navigation README, engineering dossier, revision/decision registers, CAD guide, simulation evidence and verification/reproduction guides.
- Resample the saved refined magnetostatic field at the current 3.175 mm target plane. Keep original 2 mm results as historical numerical evidence.
- Add fresh R06-derived narrated videos, captions, transcripts, stills and source hashes. Exclude prior-revision videos from the current library.
- Preserve engineering CAD/scripts/checks and numerical data at original relative paths. Exclude browser caches, dependency folders, downloaded reference video and redundant render intermediates.
- Record known context mismatches and open physical qualification work without treating them as completed analyses.

## Preceding engineering revisions

R06 updates coolant fittings/backplate to SMC M5 hardware. R05 fits the 3.175 mm aluminium target with revised clamp and M3×10 screws. R04 integrates utilities and lowers the viewport. Earlier system R03, chamber R01, compression R02 and magnetron studies remain under their dated/revision source directories. Refer to their original notes for detailed histories.
''')
    # Extract the exact saved planning amounts rather than recalculating the workbook.
    with (ROOT/'procurement/subsystems.csv').open(encoding='utf-8') as f:rows=list(csv.reader(f))
    budget=[]
    for row in rows:
        if row[0].isdigit() and len(row)>3:
            budget.append(f'| {row[0]} | {row[1]} | {float(row[3]):,.2f} | {row[2]} |')
    report=json.loads((ROOT/'procurement/export-report.json').read_text())
    tabs='\n'.join(f"| {s['sheet']} | [{s['csv']}]({s['csv']}) | [{s['cells']}]({s['cells']}) |" for s in report['sheets'])
    write('procurement/README.md',f'''
# Procurement and cost plan

**Updated: 25 November 2026 (MFC selection).** [Current workbook](Sputter%20system%20procurement.xlsx) includes the owner-selected 500 sccm MFC and recalculated totals. Its SHA-256 and export checks are in [export-report.json](export-report.json). The workbook is the source of procurement selections and saved planning values. These are not purchase orders, proof of receipt, or newly verified quotes.

## Saved planning budget (INR)

| No. | Subsystem | Saved estimate | Recorded status |
|---|---|---:|---|
{chr(10).join(budget)}

| Budget layer | Saved amount (INR) |
|---|---:|
| Equipment and installation | 948,482.00 |
| Freight, tax and clearance reserve | 70,000.00 |
| Contingency, 10% of equipment/installation | 94,848.20 |
| Total planning budget | **1,113,330.20** |

The budget includes provisional allowances. Do not add reserve twice to prices already including tax. Replace allowances with actual scope-matched quotes and freight/tax records when available. Supplier/contact information and sourcing links remain in the workbook and exports. No messages or orders were sent as part of this repository work.

## Selections that override older descriptions

- Chamber and loading door: one Alfa Technovac CB01 custom package. Its INR100,000 is a planning allowance, with GST/delivery and final quote pending. Included chamber hardware must not be bought again separately.
- Target: VritraTech Al99.99%, D50.8×3.175. R05 clamp and M3×10 screws retained.
- Internal gun fittings: 2× SMC KQG2S04-M5, reflected in R06. Catalog-envelope geometry does not establish pressurized coolant-in-vacuum suitability.
- Pumping: EXT70/EXDC80 lot, one installed and one spare; INDOVAC HV2-150 backing pump. RV3 remains an old CAD reference only. Selected driver supply is OWON SPM8205; exact driver compatibility and settings need verification.
- MFC: owner-selected STEC SEC-4400MC-G2, Ar 500 sccm, USD329.00. Fittings accepted as compatible by owner. Retain PE-D20 at checked USD230.01; owner-built perfboard adapter and 2 m shielded cable replace branded SC-EDH purchase within the existing INR2,500 allowance. Verify exact G2 pin mapping, continuity and supply voltage/polarity before connecting; calibration and low-flow performance remain to qualify.
- RF: provisional Omicron 200 W source plus matching network. The cooling plan's retained 300 W basis is not an operating power selection.
- Gun/turbo cooling: separate loops with installed duty/flow/isolation qualification still pending.

## Readable exports

| Workbook tab | Saved values (CSV) | Cell references + formulas (JSON) |
|---|---|---|
{tabs}

CSV values are the saved OOXML caches. A missing cache stays blank, not zero. Cell JSON preserves formula text and cached values separately. Exporting does not recalculate Excel, change formulas or verify native Excel behavior. Existing workbook layout and styles are retained; CSVs are data views.

## CAD and supplier records

Use [current CAD selection](../design/current.json), [System architecture and CAD](../docs/design.md#cad-downloads), the CB01 chamber scope and stage/shutter package. Original local Windows path strings remain in the workbook for provenance; the repository guides provide portable links. Procurement support records copied under `support/` retain their source names and dates.
''')
    write('simulations/current-target-r06/README.md',f'''
# Current target-plane magnetic assessment

Current gun R06 retains the magnetic circuit and uses the R05 D50.8×3.175 nonmagnetic target. The pole-to-front spacing is 5.675 mm. [assessment.json](assessment.json) records a sample at 0.25 mm above that face, simulation Z3.425, using the retained refined nonlinear FEM solution.

**Calculated mean parallel field: {assessment['Bparallel_mean_mT']:.3f} mT**, range {assessment['Bparallel_min_mT']:.3f}–{assessment['Bparallel_max_mT']:.3f} mT. The B-normal zero contour crosses all 360 sampled angles, with mean radius {assessment['radius_mean_mm']:.3f} mm. [racetrack.csv](racetrack.csv) contains the samples.

![Current target plane](current-target-map.png)

![Comparison with original target plane](current-racetrack.png)

## Method and applicability

The [resampling script](../../tools/reassess_current_field.py) loads the original `fine_nominal_field.npz` using the original VTK field-probing method. It samples 469 radii per angle, locates the first sign-changing B-normal crossing and linearly interpolates the radius and parallel vector. It first reproduces the original 2 mm-target mean within 0.05 mT, then samples the current plane.

No new mesh or nonlinear solve is performed. This is appropriate within the saved model because the retained magnets/yoke are unchanged and target/copper/fittings are μr=1. Real ferromagnetic fittings or different material properties would require a revised magnetic problem. The field file SHA-256 is recorded in the report. Original mesh/analytical checks are retained but not newly established uncertainty bounds at this plane.

This is magnetic-strength screening. It does not certify ignition, balanced topology, plasma confinement time, deposition, erosion, temperature or a power rating. Compare with a calibrated field map above the actual target before relying on the prediction. See [full simulation evidence](../../docs/simulations.md).
''')
    write('media/README.md', '# Render assets\n\nThe reader guide is now [System architecture and CAD](../docs/design.md). This directory stores the linked images, videos and provenance records.\n')
    print('Documentation built')

if __name__=='__main__':main()
