# Magnetic cooling head — revision B

20 November 2026. This is the current concept. It supersedes the two-part revision A layout, which did not reserve space for a magnet pack. Revision A files and videos remain historical references and do not describe this head.

## What changed

The magnets no longer sit behind an uninterrupted water channel and cover. They pass through seven dry holes in the cover and enter seven blind copper wells in the body. Each well is surrounded by solid copper and has its own face O-ring where the cover meets the body. Water flows around the outside of the well islands, never through the dry magnet bores in the intended sealed assembly.

This permits magnet tips at X = 3 mm, only 4 mm behind the target seating face at X = 7 mm. The coolant floor is at X = 4 mm. Blind-well ends are at X = 4.5 mm, leaving a 1.5 mm tip gap and 2.5 mm minimum front copper wall. Those dimensions are a mechanical layout, not a pressure or magnetic rating.

## Selected layout for this iteration

| Component/interface | Provisional design |
|---|---|
| Target | 50.8 mm nominal diameter; thickness/material remain open; target not included |
| Copper body | Diameter 82 × 7 mm; target seat X7; cover mating face X0 |
| Wet pocket | Annulus R10–29, depth4, with six R7.5 dry islands and an integral 6 mm-wide divider at +Y |
| Outer poles | Six axially magnetized diameter8 × 20 mm rods on PCD40 at0,60,…300 degrees |
| Center pole | Two axially aligned diameter12 × 10 mm discs, stacked to20 mm total |
| Magnet positions | All rods span X-17…3; center discs span X-17…-7 and X-7…3 |
| Dry wells | Diameter8.3 outer /12.3 center, blind X0…4.5 |
| Cover | Diameter82 ×3 mm, X-3…0; dry through-holes diameter8.6 /12.6 |
| Inlet and return | R26 at±30 degrees; axes Y22.5166605, Z±13 mm; diameter4 water passages |
| Port bosses | Integral diameter14 ×8 mm, X-11…-3; proposed G1/8 tapping-pilot envelopes |
| Steel return yoke | Diameter82 ×5 mm, X-22…-17, with two diameter16.5 utility clearances |
| Rear magnet locator | Diameter64 ×3 mm PEEK candidate, X-17…-14; seven guide bores; two open utility reliefs |
| Three load spacers | OD6 /ID3.4 ×14 mm, X-17…-3, on R37 at0,120,240 degrees |
| Main fastening | Six cover axes on PCD74; three also support yoke through spacers; nominal M3×25 long screw /M3×6 short screw intent |
| Locator fastening | Three M2×5 screw locations on R28 at60,180,300 degrees, into yoke |

Magnet sizes are new provisional engineering choices using the reference design's available form factors; the six-rod quantity was selected for this layout. They are not an inherited requirement or a validated magnetic prescription. N45 is a reference grade only. Final grade/coating and supplier demagnetization curves remain to be selected against temperature and operating point. Outer poles face N toward the target and the center stack faces S, or reverse all poles together. Both center discs are aligned in the same axial magnetization direction.

The six outer pole areas total about2.67 times the center pole area. This is not proof of a balanced or suitable field. Field strength, racetrack continuity, flux balance, yoke saturation, target material/thickness effects and thermal demagnetization require analysis or mapping before freezing the magnets and water geometry.

## Seals and pressure regions

Eight primary body/cover face O-rings are required:

| Count | Nominal ring | Gland in body | Nominal squeeze |
|---|---|---|---|
| 6 | ID10 ×1.5 mm | Local radii4.75–6.75 around each outer well; depth1.15 |23.33% |
| 1 | ID14 ×1.5 mm | Radii6.75–8.75 about center; depth1.15 |23.33% |
| 1 | ID62 ×2 mm | Radii30.7–33.3 about center; depth1.5 |25% |

The small-ring nominal gland fill is76.83%. These values do not establish seal suitability. Compound, tolerances, pressure direction, gland edge radii, surface finish, cover bending and thermal swelling remain to be designed. The supplied 62 mm ring listing previously pointed to a76 mm item; no supplier part number is approved here.

Body and cover bores are dry. Their clearance around the magnets connects the blind-well tip spaces to the open rear magnet region. Preserve an actual atmospheric vent path through the future housing. The head currently has no complete vacuum housing, insulating vacuum boundary or chamber mount, so it is not a standalone vacuum-ready source.

The divider is a contacting copper land, not a qualified internal seal. The old short cord-strip pocket has been removed. Residual flow across the bridge under cover lift/flatness error must be measured or bounded. It is an internal inlet-to-return bypass, distinct from leakage into the dry wells or the chamber.

## Mechanical retention and utility routing

The steel yoke supports the rear pole faces. The locator guides their bases, and the cover and blind wells guide the front ends. Magnets are captured with axial clearance rather than clamped into the structural stack. The three spacers transmit the yoke attachment load directly to the cover and body. Bolts, finished threads, washers, preload and drill/runout geometry remain to be detailed; they are not included as CAD solids.

The relocated port axes lie between the outer pole axes. Both yoke and locator have clearances along those routes. A separate reference assembly reserves two diameter16 ×30 mm fitting/tube cylinders at X-41…-11. These are nonphysical space reservations, not selected fittings or validated wrench/hose-bend envelopes. Replace them with supplier models and actual routing before release. Port pilot bores are not complete standard sealed ports.

All live-side metals and wetted parts require an engineered RF connection and coolant isolation plan. The Ceramaseal16959-01-KF remains the fixed feedthrough requirement but has not yet been connected to this head in CAD. Neither the plastic locator nor the coolant hoses are established main electrical insulators.

## Verification and remaining constraints

- All seven physical part definitions rebuild as one solid each. The assembled model has15 instances: body, cover, yoke, locator, six rods, two discs and three spacers.
- SolidWorks reports zero volumetric interference in the15-instance head, with coincident contact faces ignored. The17-instance utility-reservation assembly also reports zero interference.
- Independent integration of the wet-pocket cross-section and analytic sums reproduce the body and cover native volumes to within0.000001 mm³. Wet-pocket volume is approximately4.9623 mL. This is a geometry check, not a flow result.
- Magnet-to-body well radial clearance is0.15 mm nominal. The cover passage radial clearance is0.30 mm.
- A diameter16 utility reservation clears the nearest magnet by1.241 mm. The locator's relief-to-magnet-hole ligament is only0.841 mm: review robustness, machining and tolerances, and enlarge/reinforce the locator if needed.
- Body bore-to-gland inner ligaments are0.60 mm; cover bore-to-gland inner lands are0.45 mm. These narrow seal-support regions require careful tolerance, finish, extrusion and strength review.
- Water gaps are2.5 mm between central island and an outer island, and1.5 mm outside an outer island. Assess pressure loss, flow distribution, cleaning and achievable machining radii.
- Copper body and cover are C110 candidates; yoke is low-carbon1018 candidate; locator is PEEK candidate; spacers are316L candidates. No grade certificates or manufacturing drawings are released.
- No magnetic FEA/field mapping, thermal or pressure analysis, leak/bypass test, tolerance validation or RF test has been performed. The next engineering gate is evaluating the magnetic field through the actual target and copper/well stack while reviewing the narrow lands and flow passages.

## Main deliverables

- `F01 Magnetic cooling head RevB.SLDASM` — fitted native assembly.
- `F01 Magnetic cooling head RevB.step` — fitted exchange assembly.
- `F01 RevB exploded inspection.SLDASM` — separate exploded inspection model.
- `F01 RevB utility clearance check.SLDASM` — includes reference fitting reservations.
- `RevB review exploded.png`, `RevB review cutaway.png` — rendered from actual native CAD tessellation; inspection offsets/cutaway omissions are explanatory.
- `RevB native geometry checks.txt` and `RevB independent dimension checks.json` — evidence and limits.

## Engineering references

[Arnold NdFeB magnet data](https://www.arnoldmagnetics.com/products/neodymium-iron-boron-magnets/) and its [magnetization-loss discussion](https://www.arnoldmagnetics.com/wp-content/uploads/2022/06/AMT-Whitepaper-Magnetization-Losses-220629.pdf) support evaluating grade, temperature and operating point together. [Lesker process guidance](https://www.lesker.com/newweb/ped/rateuniformity.cfm) discusses target magnetic and thermal behavior. These references do not validate the custom geometry, selected magnet count or its field.
