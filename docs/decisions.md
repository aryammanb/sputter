# Design decision register

Dates identify the supplied project snapshot, not a claim that a part was ordered or received. Each selection remains subject to its recorded interface and qualification limits.

| ID | Decision | Reason and consequence | Evidence |
|---|---|---|---|
| D01 | Twelve outer D6×20 stacks and D20×20 centre, N42 | Retain selected magnetic circuit and yoke; assess field numerically. Area ratio alone does not prove balance. | Original magnetic assessment and [current resampling](../simulations/current-target-r06/README.md) |
| D02 | D50.8×3.175 Al target | Fits selected stock target. Requires R05 shoulder/lip and screw changes, plus target-plane reassessment. | [R05 notes](../cad/target-clamp-r05/READ%20FIRST%20-%20Clamp%20R05.txt) |
| D03 | Raise gun 1.175 mm | Preserves target face Z141 and default 100 mm gap after thicker target. | R05 redesign checks |
| D04 | M3×10 target screws | Increases nominal engagement without moving seats; real useful thread depth/preload pending. | R05 checks and dimension schedule |
| D05 | SMC KQG2S04-M5 internal coolant fittings | Compact OD9 envelope fits D14 yoke openings. Revises backplate to M5 ports; seal qualification stays open. | [R06 notes](../cad/coolant-fitting-r06/READ%20FIRST%20-%20Coolant%20fittings%20R06.txt) |
| D06 | One CB01 chamber/door vendor order | Supplier integrates shell, ports, window/seals and chamber hardware; avoids double purchase. | [CB01 scope](../cad/chamber-supplier-package/CB01%20frozen%20layout%20and%20supplier%20scope.txt) |
| D07 | Selected purchased KF25/1-inch gland | Use existing selected eBay source; Lesker is a dimensional reference only. Full 25.4 mm passage must be verified. | Gun mount procurement check and workbook |
| D08 | Direct turbo-to-backing route | Current selected one-pump topology; no separate roughing bypass. | MFC R03 and plumbing reference |
| D09 | EXT70/EXDC80 two-pump lot | One installed, one spare; selected 80 V supply recorded separately. | Procurement tab 05 |
| D10 | INDOVAC HV2-150 backing pump | Local sourcing selection; old RV3 model remains reference only. | Procurement tab 05 |
| D11 | STEC SEC-4400MC-G2, Ar 500 sccm MFC | Owner selection supersedes R01-R03; fittings accepted by owner, PE-D20 retained and perfboard adapter selected; exact wiring, calibration and low-flow checks pending. | MFC R04 |
| D12 | Independent gun/turbo cooling loops | Separate flow/temperature duties and planned isolation checks. | Procurement tabs 08/09 |
| D13 | 200 W RF source + matcher | Current source selection supersedes earlier 300 W operating idea; old cooling basis retained. | Procurement tab 10 |
| D14 | Viewport centre Z105 | Improves sampled sightlines below the target; does not predict glow or all-height visibility. | R04/R05 ray checks |
| D15 | Fixed stage and manually rotated shutter | Local fabrication + existing stock; no motor/actuator purchase selected. | Stage/shutter fabrication record |
| D16 | Existing corrected R06 walkthroughs and essential stills | One combined architecture/CAD guide; eight views, corrected shutter/coax exports and no new videos. | [Current render assets](../design/current-render-assets.json) |
