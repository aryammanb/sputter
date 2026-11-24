# Sputter deposition system

A compact, adjustable magnetron sputtering system: a 12 L chamber, a 2-inch aluminium target, a twelve-stack magnetic head, turbomolecular pumping, argon flow control, and independent gun/turbo cooling loops.

**Current snapshot: 24 November 2026.** Gun **R06**, target/clamp **R05**, integrated into the **R04** system layout. The design is a nominal engineering study. Fabrication release, sealing qualification and machine commissioning remain open.

![Current R06 system](media/system.png)

## Start here

| What you need | Open |
|---|---|
| Understand the whole project | [System architecture](docs/system.md) |
| Identify the latest files and revision boundaries | [Current design](docs/current-design.md) · [machine-readable selection](design/current.json) |
| Download the current CAD | [Complete system STEP](chamber-design/coolant-fitting-r06/Complete%20sputter%20system%20R06.step) · [Gun STEP](chamber-design/coolant-fitting-r06/Magnetron%20R06.step) |
| Edit the current gun in SolidWorks | [Native CAD package](chamber-design/coolant-fitting-r06/Coolant%20fittings%20R06%20-%20SolidWorks%20CAD%20package.zip) · [CAD guide](docs/cad.md) |
| Buy and fabricate parts | [Procurement guide and budget](procurement/README.md) · [workbook](procurement/Sputter%20system%20procurement.xlsx) |
| Understand the engineering decisions | [Decision register](docs/decisions.md) · [Engineering dossier](docs/engineering.md) |
| Review calculations and simulations | [Simulation evidence](docs/simulations.md) · [Current target-plane assessment](simulations/current-target-r06/README.md) |
| Inspect current component instances | [R06 component register](design/current-component-register.csv) |
| Watch the latest explanations | [Current video library](media/README.md) |
| Plan the remaining work | [Verification and release gates](docs/verification.md) |
| Reproduce or check this snapshot | [Reproduction guide](docs/reproducibility.md) · [Validation report](validation/README.md) |

## Watch the current design

| Video | Content |
|---|---|
| [01 · Complete system](media/01-current-system.mp4) | Latest geometry, chamber, stage/shutter, pumping, gas and procurement context |
| [02 · Gun and magnetron](media/02-current-gun.mp4) | Current gun, twelve-stack circuit, R05 target/clamp and R06 coolant ports |
| [03 · Field and engineering evidence](media/03-current-field-and-evidence.mp4) | Current target-plane field result, evidence scope and outstanding qualification |

All three are freshly rendered explanations of the current snapshot, with synthetic English narration, captions and transcripts. These are CAD visualizations; there are no photographs or measurements of built hardware in this snapshot. Older video segments are not reused.

## Key dimensions and selections

| Item | Current basis |
|---|---|
| Chamber interior | 200 × 200 × 300 mm; 12 L gross |
| Target | Al 99.99%, D50.8 × 3.175 mm; VritraTech selection |
| Target/substrate gap | 75–150 mm adjustment; 100 mm default |
| Stage / substrate | D90 × 6 mm / 50 × 50 × 1 mm |
| Magnetic circuit | 2 × D20 × 10 N42 centre; 12 outer stacks of 2 × D6 × 10 N42 on PCD58 |
| Gun coolant fitting | 2 × SMC KQG2S04-M5; gasket sealing remains to qualify |
| Pumping selection | Chamber → EXT70 / EXDC80 → INDOVAC HV2-150; direct foreline |
| MFC selection | 200 sccm full scale; exact model/Ar calibration unconfirmed |
| RF source selection | Omicron 200 W supply + matching network; provisional procurement basis |
| Planning budget | INR 1,108,831.64, including allowances, reserve and contingency; not a supplier quotation |

## Evidence boundaries

The current gun has 141 component instances. The context model has 339 instances, represented by 406 solids. The complete context retains a known defective legacy RV3 supplier solid, and several purchased components are illustrative envelopes. The selected backing pump is HV2-150, not RV3.

The original nonlinear FEM study assumed a 2 mm nonmagnetic target. The new assessment resamples its saved field at the current 3.175 mm target plane: mean parallel field **86.43 mT**, 82.96–89.53 mT on the sampled B-normal zero contour at 0.25 mm above the target. This is a calculated magnetic result with stated material assumptions. It does not establish discharge performance, balanced topology, deposition uniformity, coolant integrity or a thermal/power rating.

## Repository contents

`design/` selects the current artifacts. `docs/` explains design and evidence. `procurement/` contains the unchanged workbook and readable exports. `media/` contains current rendered explanations. `simulations/` contains the current-plane assessment. `chamber-design/` and `advanced-tinkering-original/` preserve the engineering sources at their original relative paths. `90 ARCHIVE - Earlier designs and working files/` preserves earlier studies for traceability.

Historical directory names and filenames containing “Current” do not override [design/current.json](design/current.json). Start with that selection and this README. Original notes are retained as dated evidence and can contain superseded selections.

No open-source license has been assigned. Third-party supplier CAD, drawings, manuals and the original reconstruction references retain their respective rights. See [attribution and source handling](docs/sources.md).
