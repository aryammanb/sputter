# Part 02 — coolant cover, F01-002 revision A

**Superseded by [RevB](RevB/README.md).** Revision A below omitted the magnet pack. Its two-ring cover and port locations are historical, not the current design.

20 November 2026. Native SolidWorks part and STEP export built. First engineering iteration, not released for manufacture.

## What is modeled

One copper component closes the rear of F01-001. Its flat mating lands retain the existing two circular face-seal interfaces. Two integral raised port bosses allow threaded, face-sealed water fittings without a brazed tube joint. The cover also has a pocket for a separate internal bypass-reducing seal strip over the channel bridge.

| Feature | Nominal geometry | Purpose |
|---|---|---|
| Main cover disk | Diameter 70 × 3 mm, X = -3 to 0 | Close the channel while limiting added magnet spacing |
| Material | C110 copper candidate | Compatible material/thermal expansion with Part 01; not a dissimilar-metal joint |
| Two integral bosses | Diameter 14 × 8 mm, X = -11 to -3 | Provide local fitting thread engagement without thickening the whole cover |
| Port axes | Y = 15.5884573; Z = +9 and -9 mm; along X | Match the centers of the existing C-channel end caps |
| Water bores | Diameter 4 mm | Communicate from each fitting pocket to its channel end |
| Fitting pockets | Diameter 8.8 × 7 mm tapping-pilot envelopes | Proposed G1/8-28 parallel female thread interface; finished threads not modeled |
| Cover mounting | Six diameter 3.4 mm clearance holes, PCD64, 0 + 60n degrees | Match Part 01's six rear M3 thread locations |
| Divider-strip pocket | Capsule length 16 × width 2.6 × depth 1.5 mm; Y10–26, Z ±1.3 | Locate a candidate 2 mm elastomer cord strip above the bridge |

The two inlet/outlet connections are interchangeable in this geometry. Bosses are machined from the same blank as the cover. Their end faces at X = -11 are flat sealing lands for the selected fitting's elastomer seal. A G thread alone does not define a complete sealed port; specify the final fitting, seal footprint, lead-in, gauge requirements, thread/runout depth and permitted installation torque together. Current CAD has plain bores, not a released ISO port detail. No tapered fitting is selected.

## Seal and flow behavior

The existing ID14 × 2 and ID54 × 2 ring candidates stay in Part 01. Cover lands at X0 leave their nominal gland depth unchanged at 1.5 mm. The strip pocket lies between those circular gland footprints and does not cross either one. Maintain the full circular sealing lands and finish them for the chosen seals.

The strip is an **internal bypass reducer**, not a primary pressure seal. A candidate FKM 2 mm cord segment would project above the 1.5 mm pocket before cover installation and compress when the metal lands meet. Its cut length, end shape, retention, compound and actual fill must be developed; no strip solid is included. The nominal 0.7 mm end lands between pocket and circular glands remain metal-contact paths and cannot be treated as hermetic. The pocket therefore does not establish zero inlet/outlet shortcut leakage. Test channel flow distribution and bypass, then revise if needed. Primary containment relies on the circular seals, continuous copper and fitting seals.

## Design considerations

- The 3 mm disk is a starting thickness, not a demonstrated pressure rating. Check pressure including shutoff/transients, cover bending, local boss torque and O-ring compression loads with six peripheral screws and the actual supporting lands.
- With this cover, the nominal axial distance from target seat to rear cover plane is 10 mm: 4 mm front copper + 3 mm water channel + 3 mm cover. Add target thickness and any mounting clearance to estimate the magnet-to-target-face distance. The bosses occupy an additional 8 mm behind the cover near the two channel ends. Reserve these volumes in the magnet layout; no magnet placement or field has been verified.
- Copper-to-copper contact is the compression stop. The strip and two O-rings must not hold the entire cover off its lands. Select screw preload against all elastomer forces, pressure separation and the receiving copper thread strength.
- Rear screw heads remain proud. Screw length, usable thread engagement, head bearing, venting and tool access remain to be detailed. Front target-clamp screws remain independent.
- Both bosses and fittings are at cathode potential. An atmospheric cavity does not establish electrical isolation; the later utility routing and insulation design must address both coolant legs and RF currents.
- Edge breaks, gland root radii, boss-root fillets, finished surface flatness/roughness, tap runout and drill points are not modeled. Detail them before production.

## Geometry evidence

The cover is one solid. Native CAD volume is 12,832.683817 mm³ and matches an independent calculation of the blank, bosses and removed pockets. Bounding dimensions are 11 × 70 × 70 mm. The boss outside surfaces have 4 mm nominal separation. The divider pocket is nominally at least 0.7 mm from the channel edges on the body bridge and 0.7 mm from either circular gland boundary. Cover clearance-hole edges are 1 mm radially beyond the outer gland boundary. These narrow lands require tolerance and manufacturing review.

The two-part cooling subassembly places both part origins at zero, with the body at X0…7 and cover at X-11…0. A separate exploded inspection assembly shifts the cover rearward by 16 mm; this is an illustrative inspection position, not an assembly mate or service travel specification. The original Part 01 file is unchanged.

The saved native assembly was reopened and checked: two resolved referenced parts, both with zero origin translation, one solid per part, and zero reported volumetric interferences with coincident mating faces ignored.

O-rings, divider strip, fittings and fasteners are not included. This subassembly alone does not define the complete atmosphere/vacuum boundary. Geometric fit does not establish leak tightness or operating performance.

## Files

- `F01-002 Coolant cover RevA.SLDPRT` and `.step`
- `F01 Cooling body and cover RevA.SLDASM` and `.step`
- `F01 Cooling pair exploded inspection.SLDASM`
- `build-part02.ps1`, `check-cooling-pair.ps1` and geometry/fit check reports

## Fitting research

[Festo QS manufacturer catalogue](https://ftp.festo.com/Public/PNEUMATIC/SOFTWARE_SERVICE/Documentation/2025/EN/QS_EN.PDF) documents G-thread push-in fittings with sealing rings, including G1/8 to 6 mm tube configurations. This supports investigating that connection family; **no Festo fitting has been selected or qualified** for this coolant, temperature, electrical environment or port. Obtain the actual fitting drawing and water-service declaration before finalizing the port geometry.
