# Coolant closure — proposed joint geometry

## Selected architecture — 15 November 2026

User selected indirect cooling: the replaceable 50.8 mm diameter × 3.175 mm aluminium target clamps onto a separate copper cooling body. Heat crosses the dry target-to-copper contact and the solid copper wall to the enclosed coolant. Target removal must not open the coolant enclosure. Dedicated inlet and outlet tubes serve the enclosure; the magnet/yoke assembly remains outside the coolant circuit.

This selects the cooling architecture, not a qualified joining process. The existing integral body 308 and proposed rear closure 305 implement this concept provisionally. Their braze dimensions, tube connections and manufacturing process remain subject to review and physical qualification below. No CAD geometry was changed by this architecture decision. Next review: the copper body's target contact face and continuous water-separating wall, followed by the channel and closure. The target clamp adaptation remains outstanding.

15 November 2026. User-authorized refinement of the water/vacuum boundary. Native part `R09 305 Brazing-land rear closure.SLDPRT` replaces the former flat 305 plate in the active R09 assembly. Integral body 308 remains one piece. This is a process-development design, not a qualified leak-tight assembly or compliance claim against a named standard.

## What changed in CAD

| Feature | Nominal geometry | Purpose |
|---|---|---|
| Outer dry mounting rim | Radius 27.2–34.4 mm, X=156.7–159.7 mm | Retains the existing mechanical stack and screw-head load path. Not the water seal. |
| Central closure face | X=159.650 mm, inside radius 26.2 mm | Provides a proposed 0.050 mm face-braze allowance to the body's mating lands at X=159.700 mm. Central plate thickness is 2.950 mm. |
| Outer primary braze land | Mating body radius 25.0–26.2 mm, width 1.2 mm | Continuous metal joint separating the water cavity from the dry outer interface. Width and strength require qualification. |
| Inner support/seal land | Body center radius 0–10.4 mm | Bonded to closure face; avoids an unjoined inner interface and supports the cover. |
| Divider joint | Entire existing divider face | Prevents an inlet-to-outlet bypass across the rear of the divider. |
| Dry annular relief | Radius 26.2–27.2 mm; floor X=159.2 mm | Separates the primary joining area from the mounting rim and provides an inspectable dry interface. |
| Dry vent slot | 1.0 mm wide at +Y/Z=0, from radius 26.2 to OD; floor X=159.2 mm | Opens the relief groove to chamber vacuum rather than leaving a closed trapped annulus. Keep clear of filler. |
| Tube receiving bores | Two diameter 4.60 mm through bores at the unchanged radius 13 mm port centers | Around existing diameter 4.50 mm tube envelopes, gives proposed 0.050 mm radial braze allowance and 2.950 mm nominal overlap. |
| Mounting-screw holes | Three diameter 3.30 mm through holes at radius 29.4 mm | Remain outside the primary seal and groove. Nominal clearance from groove outer edge to nearest hole edge is 0.55 mm. |

The nominal jacket ceiling is now 0.050 mm farther from the channel floor before brazing, giving 4.050 mm cavity depth where the channel was 4.000 mm. The target-facing copper wall stays 5.000 mm. No nominal interference was introduced with the existing tube or screw envelopes.

## Required permanent joints

**J1: rear closure to integral body.** Establish a continuous, qualified face-brazed outer seal, and fully bond the central land and divider. Do not braze the dry outer rim or fill the dry groove/vent. The outer rim positions the parts but does not replace fixturing for flatness and gap control. Merely tightening the mounting screws is insufficient.

**J2/J3: the two tube connections.** Each must have its own continuous circumferential, qualified brazed joint over the receiving overlap. The tubes and their internal bores must remain open and supported against service loads. The drawn diameter 4.50 mm tubes are still a design envelope pending final stock/tolerance selection.

There are no filler-metal solids in this pre-braze CAD. The 0.050 mm gaps are deliberately open until the joining process fills them. Do not interpret the unjoined assembly as sealed, and do not use the absence of component interference as a fluid-tightness test.

## What the dry groove does NOT do

It is not an O-ring groove, a second seal, a water drain, a leak-detection chamber, or secondary containment. It vents to chamber vacuum. If J1 leaks, water can reach this groove and then the vacuum. This revision defines where the primary seal must work; it does not make a defective seal harmless.

## Joining process still to establish

- Select compatible copper grade/temper and a vacuum-compatible filler/process with the fabricator. No filler, flux, furnace cycle or alloy certification is selected by this revision.
- The 0.050 mm room-temperature allowances are provisional CAD dimensions, not a universal brazing specification. Recalculate/set clearances at joining temperature for the selected filler and process; specify tolerances and flatness so the gap exists over the full joint.
- Evaluate the 1.2 mm outer land, narrow divider, plate thickness and tube overlap for the actual pressure, temperature, cyclic loading and joint properties before release.
- Define filler placement/quantity, wetting, stop-off compatibility where needed, fixturing, cleaning and inspection. Avoid filler blocking ports or the divider-adjacent passage. Avoid trapping flux or residues in the water/vacuum assembly.
- Join before magnets and ceramics are installed. Recheck target-face flatness and finish after joining; provide machining allowance if post-join finishing is needed.

## Verification and acceptance work

1. Dimensionally inspect bores, tube sizes, land continuity, plate flatness and joining clearances before assembly.
2. Qualify the joining procedure on representative coupons or a prototype, including the narrow divider and outer seal land. No leak-rate or pressure acceptance values are invented here.
3. Use a documented hydraulic proof/leak procedure with pressure limits based on the verified design and weakest component. Inspect for permanent distortion and external leakage.
4. Clean and dry the water circuit; verify helium leakage from the coolant circuit toward the evacuated exterior using a qualified setup and acceptance criterion derived from the vacuum requirement. A successful hydraulic test alone does not establish vacuum leak performance.
5. Check coolant continuity/pressure drop and verify that inlet flow follows the channel rather than bypassing the divider. External helium tightness does not prove the divider is sealed internally.
6. Repeat the relevant acceptance checks after representative thermal/pressure cycling. Final qualification remains physical work.

## CAD checks completed

- New closure is one native solid. Volume: 10,782.569698 mm³, matching independent disk/step/groove/hole/slot geometry calculation.
- Active gun references the new closure, has 75 leaf parts and no missing references.
- SolidWorks reports only the 23 previously expected screw/pilot thread-envelope overlaps, with matching volumes; no other volumetric interference was reported.
- The water-channel body and target seating position were preserved. The target clamp still needs its previously identified adaptation to the 3.175 mm target; this sealing revision does not resolve that separate issue.

## Source basis

[Lucas Milhaupt: Designing braze joints at temperature](https://blog.lucasmilhaupt.com/en-us/about/blog/designing-braze-joints-at-temperature) explains why joining-temperature clearance must be considered. [Lucas Milhaupt: Vacuum brazing](https://blog.lucasmilhaupt.com/en-us/about/blog/vacuum-brazing) discusses atmosphere/process considerations and the benefit of avoiding entrapped flux. These sources guide process development; they do not qualify this custom geometry or prescribe its 0.050 mm allowance.
