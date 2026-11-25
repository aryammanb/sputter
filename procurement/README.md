# Parts and procurement

**Updated: 25 November 2026 (MFC selection).** [Current workbook](Sputter%20system%20procurement.xlsx) includes the owner-selected 500 sccm MFC and recalculated totals. Its SHA-256 and export checks are in [export-report.json](export-report.json). The workbook is the source of procurement selections and saved planning values. These are not purchase orders, proof of receipt, or newly verified quotes.

## How procurement is organized

The component list is prepared and grouped into three routes, matching the project-status slide in the presentation:

| Route | What is ready | What follows the review |
|---|---|---|
| **Custom order** | Specialized vendors identified; CAD and specifications prepared | Confirm the drawing, material, tolerances, included hardware and acceptance requirements, then request the final manufacturing quote |
| **Procure online** | Links identified for Indian and US sources | Confirm the exact variant, condition, included accessories and landed cost before ordering |
| **Procure locally** | Parts and local sourcing routes identified | Confirm specifications, quantities, availability and price with the supplier |

**Next steps:** review the entire design and component selection part by part, then start the procurement and manufacturing process. Follow [Review before building](../docs/verification.md) while checking the workbook against the [CAD and interfaces](../docs/design.md).

## Using the workbook

Start with **Subsystems** for the system totals, then open the relevant numbered tab for individual parts and sources. **Settled sourcing** records the selected routes; **Needs your input** preserves unresolved questions. Review the actual rows rather than treating a tab name as purchasing approval. Check package inclusions before placing separate orders for fittings, seals or mounting hardware.

The workbook is the editable procurement record. The CSV and cell/formula exports below let readers inspect it in GitHub without Excel. Recorded prices and allowances remain planning values until replaced by scope-matched quotes and actual costs.

## Saved planning budget (INR)

| No. | Subsystem | Saved estimate | Recorded status |
|---|---|---:|---|
| 1 | Sputter gun | 50,650.00 | Answers recorded |
| 2 | Chamber and loading door - complete package | 100,000.00 | Layout frozen |
| 3 | Gun mounting and height adjustment | 18,000.00 | Source chosen; fit pending |
| 4 | Substrate stage and shutter | 2,500.00 | Local fabrication + stock |
| 5 | Vacuum pumping | 167,208.00 | 80V bundle and supply selected |
| 6 | Pressure measurement | 60,000.00 | Local supplier selected |
| 7 | Argon supply and flow control | 86,024.00 | Sources selected; qualification pending |
| 8 | Gun water cooling | 45,600.00 | Local sourcing; checks pending |
| 9 | Turbo water cooling | 41,500.00 | Local sourcing; checks pending |
| 10 | Electrical power and controls | 301,500.00 | Supply, controls and wiring budgeted |
| 11 | Frame and equipment supports | 45,000.00 | Local fabrication budgeted |
| 12 | Installation, commissioning and spares | 30,500.00 | Allowances with sourcing routes |

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
| 01 Sputter gun | [01-sputter-gun.csv](01-sputter-gun.csv) | [01-sputter-gun.cells.json](01-sputter-gun.cells.json) |
| Subsystems | [subsystems.csv](subsystems.csv) | [subsystems.cells.json](subsystems.cells.json) |
| Settled sourcing | [settled-sourcing.csv](settled-sourcing.csv) | [settled-sourcing.cells.json](settled-sourcing.cells.json) |
| Needs your input | [needs-your-input.csv](needs-your-input.csv) | [needs-your-input.cells.json](needs-your-input.cells.json) |
| 04 Stage and shutter | [04-stage-and-shutter.csv](04-stage-and-shutter.csv) | [04-stage-and-shutter.cells.json](04-stage-and-shutter.cells.json) |
| 05 Vacuum pumping | [05-vacuum-pumping.csv](05-vacuum-pumping.csv) | [05-vacuum-pumping.cells.json](05-vacuum-pumping.cells.json) |
| 06 Pressure measurement | [06-pressure-measurement.csv](06-pressure-measurement.csv) | [06-pressure-measurement.cells.json](06-pressure-measurement.cells.json) |
| 07 Argon and flow control | [07-argon-and-flow-control.csv](07-argon-and-flow-control.csv) | [07-argon-and-flow-control.cells.json](07-argon-and-flow-control.cells.json) |
| 08 Gun water cooling | [08-gun-water-cooling.csv](08-gun-water-cooling.csv) | [08-gun-water-cooling.cells.json](08-gun-water-cooling.cells.json) |
| 09 Turbo water cooling | [09-turbo-water-cooling.csv](09-turbo-water-cooling.csv) | [09-turbo-water-cooling.cells.json](09-turbo-water-cooling.cells.json) |
| 10 Electrical and RF | [10-electrical-and-rf.csv](10-electrical-and-rf.csv) | [10-electrical-and-rf.cells.json](10-electrical-and-rf.cells.json) |
| 11 Frame and supports | [11-frame-and-supports.csv](11-frame-and-supports.csv) | [11-frame-and-supports.cells.json](11-frame-and-supports.cells.json) |
| 12 Installation and reserves | [12-installation-and-reserves.csv](12-installation-and-reserves.csv) | [12-installation-and-reserves.cells.json](12-installation-and-reserves.cells.json) |

CSV values are the saved OOXML caches. A missing cache stays blank, not zero. Cell JSON preserves formula text and cached values separately. Exporting does not recalculate Excel, change formulas or verify native Excel behavior. Existing workbook layout and styles are retained; CSVs are data views.

## CAD and supplier records

Use [current CAD selection](../design/current.json), [System architecture and CAD](../docs/design.md#cad-downloads), the CB01 chamber scope and stage/shutter package. Original local Windows path strings remain in the workbook for provenance; the repository guides provide portable links. Procurement support records copied under `support/` retain their source names and dates.
