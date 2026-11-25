# Part 01 — copper cooling body

**Superseded by [RevB](RevB/README.md).** Revision A below omitted the magnet pack. Do not use its geometry or videos as the current design.

20 November 2026. Revision A CAD built in SolidWorks and exported to STEP. Preliminary engineering model; not released for manufacture.

## Built revision A

Native file: `F01-001 Copper cooling body RevA.SLDPRT`. Exchange file: `F01-001 Copper cooling body RevA.step`. Reproducible geometry generator: `build-part01.ps1`.

The built model supersedes the unresolved dimensions in the initial concept table below:

| Feature | Modeled dimension |
|---|---|
| Body | Diameter 70 mm × 7 mm thick |
| Target seat | Flat continuous front face; nominal 50.8 mm target centered on it |
| Water passage | Radii 11–25 mm, 3 mm deep; 300-degree C passage with radius 7 mm semicircular ends |
| Copper beneath target | 4 mm between channel floor and target seat |
| Inner O-ring groove | Radii 6.7–9.3 mm, depth 1.5 mm; nominal ID14 × 2 mm ring candidate |
| Outer O-ring groove | Radii 26.7–29.3 mm, depth 1.5 mm; nominal ID54 × 2 mm ring candidate |
| Coolant-cover fastening | Six diameter 2.5 mm blind pilot pockets, 4 mm deep, on diameter 64 mm circle, at 0 + 60n degrees |
| Target-clamp fastening | Three diameter 2.5 mm blind pilot pockets from front, 3 mm deep, on diameter 64 mm circle, at 30 + 120n degrees |

Actual CAD coordinates use **X** as the axis: rear cover face X = 0, target seat X = +7 mm. Angles are measured in the Y/Z plane from +Y toward +Z. This supersedes the initial Z-axis convention below. Candidate inlet/return axes in the future cover are radius 18 mm at +30 and -30 degrees, over the channel end centers; those ports are not holes in this part.

The screw pockets represent M3 × 0.5 thread intent, not finished threads. Drill points, full thread length, runout, venting and copper-thread preload require detailing. Groove root/edge radii and finished surface specifications also remain to be detailed. Sketches are coordinate-defined native features, not fully dimension-constrained production sketches.

At nominal geometry, the 2 mm rings have 25% axial squeeze and approximately 80.55% gland volume fill. These are geometry checks, not seal qualification; tolerances, compound, swell, temperature, cover deflection, ring positioning and pressure direction must be checked. The annulus between the seals includes the channel and its bridge: cover contact on the bridge alone is not a qualified divider seal. Specify bypass control when designing the cover.

Geometry verification passed: one solid; bounding dimensions 7 × 70 × 70 mm; volume 21,474.788553 mm³, matching an independent analytic sum of blank minus channel, glands and pockets. Water channel volume is 4.420221 mL. Channel-to-groove radial ligaments are 1.7 mm; outer groove to rear pilot edge is 1.45 mm; pilot edge to outside diameter is 1.75 mm. Front and rear pilot patterns are staggered and do not meet. These checks do not establish pressure strength or magnetic/thermal performance.

Rear isometric and front-face PNGs were visually inspected. The STEP export completed without reported save warnings. No complete coolant enclosure, vacuum seal assembly or gun assembly has yet been built. Next component is the mating coolant cover, after review of this body.

## Design decision

Use a single machined copper body with a flat front target seat and a rear-machined coolant passage. A separate cover will close the passage with O-rings. The target is indirectly cooled and is not part of a water seal. Target replacement must leave the coolant cover and all vacuum-boundary seals assembled.

This is a fresh component. No earlier CAD part or dimensions are inherited. The only inherited interfaces are the nominal 50.8 mm target diameter and the selected Ceramaseal 16959-01-KF feedthrough elsewhere in the assembly.

## Initial geometry

Define the target seating face as Z = 0, with positive Z toward the plasma and negative Z toward the magnets/rear utilities.

| Feature | First-iteration definition | Status |
|---|---|---|
| Material | C110 copper candidate | Engineering selection; confirm stock and machining route |
| Body outside diameter | 70 mm | Provisional packaging envelope, not a calculated minimum |
| Target contact face | Flat, continuous metal beneath the complete 50.8 mm target footprint | Selected architecture |
| Target location | Removable clamp/locator; no close-fitting pocket in the copper face in this iteration | Detail to follow actual target tolerances and thermal expansion |
| Target thickness | Unspecified | Deliberately open |
| Water passage | Rear-machined annular/C-shaped passage with inlet and return separated by an integral divider | Candidate layout; radii and cross-section unresolved |
| Front copper wall | Continuous between the target seat and coolant | Thickness unresolved pending pressure, thermal and magnetic-spacing checks |
| Passage closure | Separate removable rear cover | O-ring boundaries and cover loading to be designed together |
| Dry magnet region | Behind the coolant closure, connected to the rear atmospheric cavity | Envelope reserved; exact position depends on field design |

The 70 mm body gives 9.6 mm radial space beyond a nominal 50.8 mm target. This is a packaging allowance for retention and adjoining interfaces, not proof that fasteners, O-ring glands and insulation fit. Enlarge or reduce it after the section layout.

Revision A assigns provisional thicknesses for an actual geometry iteration. Reconcile the front wall, water depth and seal lands with the magnet-to-target distance before release. No performance rating follows from these provisional dimensions.

## Thermal path

Target → dry target/copper contact → continuous copper front wall → flowing water.

The target clamp must provide distributed contact load. Copper conductivity alone does not establish adequate cooling: contact resistance, target flatness/material, heat-flux distribution and water-side convection all matter.

For first sizing, use coolant heat removal Q = mass flow × specific heat × temperature rise. At approximately 1 litre/minute of water, the bulk heat capacity rate is about 70 W/K. Thus a hypothetical 300 W heat load gives about 4.3 K bulk water rise. This is an illustration only, not a selected gun power, required flow, or predicted target temperature. Assume the full selected electrical power becomes a cooling load for an initial conservative heat balance; add other loads if applicable.

## Interfaces to preserve

- No coolant passage or coolant port opens onto the target seating face.
- Keep clamp fasteners out of the wet cavity. Receiving blind holes need enough backing material and a defined vent path to their own pressure region.
- Cover seals should separate water from the atmospheric interior. A continuous copper wall separates water from vacuum beneath the target. Trace the remaining peripheral water/vacuum boundary in the section before claiming this arrangement everywhere.
- An integral divider needs a defined mating closure feature to prevent inlet-to-return bypass. External O-ring sealing alone does not seal the divider.
- Vacuum-seal lands between this live body and its insulating support must be coordinated with the coolant lands; no gland dimensions are frozen yet.
- The cooling body is live. The electrical contact, structural support and coolant isolation are separate interfaces to be engineered.

## Required before dimensioned CAD release

Set design coolant pressure including pump shutoff/transients, coolant conditions, heat load and target range. Lay out the magnets and evaluate the target-face field through the complete target/wall/channel/cover stack. Check wall and cover deflection, seal compression and fastener loads. Then set wall thickness, channel dimensions, gland geometry, flatness/finish and tolerances.

The first wet-perimeter layout is now modeled in revision A. Complete the mating-cover/divider design before detailing the clamp or housing.

## Basis

[Lesker source technical notes](https://www.lesker.com/newweb/deposition_sources/technotes_sputtering.cfm) describe indirect cooling with a clamped target on a copper cooling well and identify poor target-to-well contact as a thermal limitation. The geometry and 70 mm envelope above are our proposal, not dimensions from that source or the Advanced Tinkering STEP assembly.
