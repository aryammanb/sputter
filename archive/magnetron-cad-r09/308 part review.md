# Part 308 — copper target seat / cooling-jacket cover

**Rear closure refinement:** The active assembly now uses `305 Brazing-land rear closure`, with a proposed 0.050 mm face-braze allowance, a dry annular relief/vent outside the primary seal, and revised 4.60 mm tube bores. Body 308 geometry is unchanged. See `Coolant joint design revision.md` for current mating dimensions, joining intent and outstanding physical qualification. The dry groove is not secondary containment.

**Implemented 15 November 2026:** At the user's instruction, separate parts 306 and 308 were combined in native SolidWorks into `R09 308 Integral copper target seat and channel.SLDPRT`, verified as exactly one solid. The active cooling-head assembly now uses that single component, with no separate 306; the complete gun has 75 leaf instances. Body OD is 68.8 mm; thickness is 9 mm; rear channel depth is 4 mm; front copper wall remains 5 mm. The axial envelope is X = 159.7 to 168.7 mm. Rear plate 305 remains separate. The descriptions below of the former 5 mm standalone cover and two-piece proposal are retained as review history and are superseded by this implementation note.

The six original fastener axes are preserved: three rear holes have 3.3 mm clearance over the rear 4 mm followed by the 5 mm M3 pilot zone; three front clamp holes retain a 5 mm-deep 2.5 mm pilot and are now blind within the integral body. Thread cutting, drill-point/runout, dry-side venting and machining corner radii still require manufacturing detail. Source-body features plus a native Combine feature define the solid; manufacturing intent is one copper blank, not joining the source bodies. Existing source part files are retained only as history.

Verified solid volume: 26,796.709167 mm³, equal to the union of the old seat and core without altering the coolant cavity. The target seating plane is unchanged. The 3.175 mm target still requires clamp adaptation; that is not corrected by integrating the cooling body.

Reviewed 15 November 2026 against native SolidWorks R09. Quantity: one. Custom manufactured component. Status: nominal geometry checked; fabrication release pending.

## Native geometry and all defining dimensions

One solid disk, diameter 68.800 mm, thickness 5.000 mm. Rear face X = 163.700 mm; target seating face X = 168.700 mm. Six diameter 2.500 mm through pilot bores on a diameter 58.800 mm pitch circle. Intended finished threads: M3×0.5 through, thread tolerance class not specified. No modeled counterbores, countersinks, target-locating recess, chamfers or fillets. SolidWorks material: Copper, with no procurement grade/temper established.

The six hole centers lie at radius 29.400 mm. Each three-hole family has 120-degree spacing; the two families are offset 60 degrees, producing six holes at 60-degree intervals. Coordinates below are millimetres in the assembly Y-Z plane, viewed from the target side with +Y right and +Z up. Angles are measured from +Y toward +Z.

| Function | Angle | Y | Z |
|---|---:|---:|---:|
| Head attachment, screw 309 | 90° | 0 | 29.400 |
| Head attachment, screw 309 | 210° | -25.461147 | -14.700 |
| Head attachment, screw 309 | 330° | 25.461147 | -14.700 |
| Target clamp, screw 403 | 30° | 25.461147 | 14.700 |
| Target clamp, screw 403 | 150° | -25.461147 | 14.700 |
| Target clamp, screw 403 | 270° | 0 | -29.400 |

These extra coordinate decimals describe nominal geometry; they are not machining tolerances. Define the pattern from its pitch circle, datum orientation and true-position tolerance on the production drawing.

Native SolidWorks check: one solid, two planar faces, outer cylindrical radius 34.400 mm, six cylindrical bore radii 1.250 mm; solid volume 18,440.913257 mm³, matching the disk minus six through bores.

## Interfaces and derived nominal distances

| Interface / feature | Value | Meaning |
|---|---:|---|
| Seat extending beyond Ø50.8 target | 9.000 mm radial | Space around target for clamp/fastener pattern. |
| Target rear to seat front | 0 mm nominal gap | Both faces at X = 168.700 mm; real contact depends on flatness/preload. |
| Hole center to outer edge | 5.000 mm | From radius 29.4 to radius 34.4. |
| Outer edge to nominal M3 major-diameter envelope | 3.500 mm | Uses 1.5 mm thread radius, not the smaller pilot. |
| Nominal M3 envelope to target edge | 2.500 mm radial | 29.4 − 1.5 − 25.4. |
| Nominal M3 envelope to maximum channel radius | 2.900 mm radial | 29.4 − 1.5 − 25.0; excludes joining/tolerance effects. |
| Copper separating target from jacket water | 5.000 mm nominal | Cover thickness above the channel; not a validated pressure/thermal design. |
| Existing head screw 309 overlap in cover | 3.800 mm | Screw end X = 167.5, rear cover face X = 163.7. |
| Existing clamp screw 403 overlap in cover | 3.200 mm | Seat front X = 168.7, screw end X = 165.5. Valid only at current, unadapted clamp position. |

The coolant channel lies behind this cover and extends nominally between radii 10.4 and 25.0 mm apart from its divider. Hole positions are outside that fluid cavity. The cover still requires a continuous qualified seal to the channel core. The target is not a water seal.

## What is sound and what remains open

- A flat disk with six axial holes is a straightforward machining geometry. There is no inaccessible undercut or cross-drilled internal passage in this part.
- The target is fully backed by the front face. There is no locating pocket: lateral target location depends on the clamp-ring bore and the assembly's centering/clearance scheme.
- Target thickness reduction from 6.000 to 3.175 mm does not require moving this seating plane. Keeping it fixed preserves the coolant jacket. The clamp must be adapted; there is currently a 2.825 mm gap beneath its lip.
- The part is both a structural threaded receiver and a coolant boundary. A nominally collision-free model does not establish thread pullout capacity, cover bending, seam integrity or thermal contact.
- Specify copper grade/temper and a joining process for 305/306/308 with the fabricator. Do not assume coincident CAD surfaces are a manufacturable leak-tight braze joint. Braze clearances, filler, joint lands, fixturing and inspection are not defined.
- Define mating-face flatness, front/rear parallelism, target-contact surface finish, thickness/diameter tolerances, hole position/thread class and edge breaks. Set the final finishing sequence to account for joining distortion.
- The pilot bores are not actual finished threaded geometry. A production drawing must call out M3×0.5 through and the usable full thread length; complete tapping and keep joining material out of the threads.
- The existing short engagements in copper need a preload/pullout assessment. The 403 engagement will change with the thinner target's clamp redesign. Do not freeze a torque or screw length now.
- Manufacture and join/test the jacket before installing magnets, ceramics or target. Routine target changes should not separate this permanently joined cover.

## Review disposition

Retain the current nominal disk diameter, thickness, seating plane and bolt-circle geometry as the review baseline. No geometry change made during this review. Add to BOM as make item 308, quantity one. Joining details, tolerances, copper selection and clamp/fastener decisions remain open; not released for manufacture.

## Follow-up: threads, screw functions and cooling architecture

The six M3 holes are on the dry outer rim, not intentionally connected to the water channel or atmosphere. Their nominal major-diameter envelopes stop at radius 27.9 mm; the channel ends at radius 25.0 mm. The 2.9 mm radial separation does not itself seal the interfaces between the three copper layers. A defective joint can let water migrate along a mating face to a screw passage or the vacuum-exposed perimeter. Threads must not be used as the coolant seal.

Screws 309 (three, installed from rear) pass through the yoke/backplate/core and engage the seat to retain the cooling-head stack on the yoke. Screws 403 (three, installed from target side) engage the alternating seat holes and load the target clamp ring. Neither set replaces the permanent coolant-jacket seal. Only the target-clamp set is normally removed for a target change, after removing the separate shield fasteners.

Virtual leaks remain possible from trapped gas, even without a coolant leak. In particular, the three clamp holes are through part 308 but backed by solid part 306, making them effectively blind in the joined stack. Specify vented hardware or a deliberate vent to vacuum on the dry side; never vent into the coolant channel. Check the entire installed screw pocket, not just the isolated plate.

Current cooling cavity: C-shaped annulus, inner radius 10.4 mm, outer radius 25.0 mm, axial depth 4.0 mm, radial width 14.6 mm. The two backplate ports are on opposite sides of the divider. A sealed divider forces water around the long arc; leakage above or below it would allow bypass. The current three-layer build needs continuous qualified joints at its fluid boundary and a sealed divider at both mating faces.

The target is cooled indirectly: target rear contact -> 5 mm copper cover -> coolant. Its center lies above the solid inner land; heat there spreads laterally to the annular water passage. The 3.3 mm nominal tube bore is smaller in area than the channel (about 8.55 mm² versus 58.4 mm²), so channel width alone cannot establish circulation or pressure drop. Target contact and cover flatness are material design issues; no allowable operating power has been established.

Preferred architecture for further refinement (proposal, NOT yet modeled): machine the C-channel into the rear of an integral seat/channel body occupying the existing combined 9 mm axial envelope, retaining a 5 mm target-side wall and 4 mm channel depth. Close it with the existing 3 mm backplate using a specified leak-tight joining process. This removes one whole copper interface and one possible divider bypass plane. The screw-hole/vent details would be adapted with the integral body; it is not yet an approved part substitution.

References: [Lesker gas loads and virtual leaks](https://www.lesker.com/newweb/technical_info/vacuumtech/outgas_03_gasload.cfm?section=outgassing), [UC Components vented screw guidance](https://uccomponents.com/faqs/), and [Lesker direct versus indirect target cooling](https://www.lesker.com/newweb/deposition_sources/technotes_sputtering.cfm?init=skip&section=tech). Geometry statements are from the native CAD and its construction profiles, not from those supplier references.
