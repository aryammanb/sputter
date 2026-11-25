# Magnetron sputter gun — R09 mechanical design review

**Water-boundary refinement, 15 November 2026:** Active rear plate 305 replaced with a native brazing-land closure: proposed 0.050 mm face allowance, defined outer/central/divider bond regions, dry vented relief outside the seal, and two revised tube sockets. This is pre-braze geometry, not demonstrated leak-tightness. See `Coolant joint design revision.md` for scope and qualification requirements. Earlier viewer exports depict the preceding plate.

**Integral cooling-body update, 15 November 2026:** User approved combining 306 and 308. The active assembly now contains one integral copper seat/channel body (item 308), OD 68.8 mm × 9 mm, with 4 mm rear channel and 5 mm front wall. Separate core 306 is removed from the active assembly; leaf count is now 75. Rear plate 305 remains a separate closure. Earlier references below to a three-layer copper jacket are historical. See `308 part review.md` for current details.

**15 November 2026 amendment:** User selected Vritra Technologies' 99.99% Al target, diameter 2 in (50.8 mm), thickness 0.125 in (3.175 mm). Native part 401 now has this thickness with its rear face unchanged. Its front face is X = 171.875 mm, leaving a 2.825 mm gap below the unchanged clamp lip. Clamp adaptation is pending the part-by-part review. The analysis and assembly-verification results below describe the earlier 6 mm target unless explicitly amended; the previous full-assembly viewer also depicts that earlier thickness. See the working BOM at ../BOM.md.

Reviewed 14 November 2026. Scope: manufacturability, retention, assembly, vacuum/coolant joints and service access. Baseline: native R08 SolidWorks files and their construction scripts. R09 is a separate review revision; R08 is preserved.

## Verdict

**Do not send the current assembly to a shop as a complete build-to-print design.** The packaging is coherent, but R08 contained definite fastening/retention defects. R09 corrects several of them. It still contains unengineered electrical contacts, unspecified permanent joints, purchased-part envelopes and screw envelopes. A successful interference check alone does not establish that it can be manufactured, fastened or operated.

The likely path to a workable instrument is to finish these interfaces, not discard the whole arrangement. No claim of demonstrated sputtering performance, structural life, coolant integrity or electrical qualification is made.

## Corrections actually made in native SolidWorks

| Parts | R08 problem | R09 change | Remaining qualification |
|---|---|---|---|
| 501 grounded shield | Ø5.7 holes cut through its 4 mm mounting flange; Ø5.5 screw heads could pass through. There was no bearing shoulder. | Removed the oversized cuts; retained Ø3.3 clearance holes. Screw heads now bear on the front flange face. | Choose actual screw head/drive standard; set hole and flatness tolerances. |
| 502 shield seat | Ø3.3 clearance holes offered no screw retention. | Three Ø2.5 pilot bores with M3×0.5 thread intent. | Specify tapped thread tolerance and full usable thread length. |
| 308 copper target seat | Head screws ended in Ø3.3 clearance holes, and clamp screws also had clearance-sized receiving bores. | Six Ø2.5 through pilot bores: three for head screws and three for clamp screws, on alternating phases of the same bolt circle. | Specify M3×0.5 tapping, verify copper thread strength/preload, protect threads during joining. |
| 204 keeper; 304 yoke | Ground keeper and live retainer screws respectively entered Ø3.3 bores without a defined tapped receiver. | Ø2.5 pilot bores at the corresponding three-hole patterns; original passage holes preserved. | Tapping/drill-point allowance and ceramic preload control remain to be detailed. |
| 101 mount plate; 601 guard shell | Ø3.1 receiving bores were too large to define the intended conventional M3 tapped joints. | Four Ø2.5 blind pilot bores in each receiving part. | Drawing must distinguish full thread depth, drill depth, runout and screw-tip clearance. |
| 203 ceramic carrier | Its Ø19 center opening was larger than the Ø18 center magnet. The Ø18.4 locator bore also did not capture that magnet. Magnetic attraction was the only rear retention. | Reduced carrier center bore to Ø8.4. This creates an annular rear support under the Ø18/Ø9 magnet while clearing the Ø6.4 rod by 1.0 mm radially. | Magnet/cavity thickness tolerances must prevent crushing the brittle magnet; use controlled axial clearance or a qualified compliant restraint. |
| All assemblies | Parts were positioned by transforms without a completed mating scheme. | Fixed the reviewed component positions in the separate R09 assemblies. | Fixed placement is not a mechanical mate or tolerance-stack proof. |

Thread geometry is represented by minor-diameter pilot cylinders and nominal screw cylinders, not helical threads. Custom properties identify this convention. The resulting 23 screw/pilot overlap volumes are intentional thread envelopes; they must not be interpreted as 23 ordinary collisions or as evidence that real threads have been manufactured.

## Fastener audit

Axial dimensions below are measured from the modeled intervals, not certified usable engagement. Chamfers, incomplete threads, drill points and tolerances reduce the available full engagement.

| Fastener | Quantity | Receiving part | Nominal overlap | Modeled under-head length | Assessment |
|---|---:|---|---:|---:|---|
| 205 live ceramic retainer | 3 | 304 steel yoke | 5.0 mm | 19.2 mm | Receiving thread intent corrected; nonstandard screw envelope length, ceramic loading and blind-hole detail remain open. |
| 207 grounded keeper screw | 3 | 204 keeper | 6.0 mm | 10.0 mm | Geometry is consistent with a 10 mm screw; choose actual standard and tolerances. |
| 309 head attachment | 3 | 308 copper seat | 3.8 mm | 18.8 mm | Receiving thread corrected. Short engagement in copper and nonstandard length require a final screw/insert design. |
| 403 target clamp | 3 | 308 copper seat | 3.2 mm | 8.5 mm | Receiving thread corrected. Copper pullout and target clamping load remain unverified. |
| 503 shield screw | 3 | 502 shield seat | 3.7 mm | 7.7 mm | Head now has a bearing face. Choose actual screw length and head dimensions. |
| 606 guard mounting screw | 4 | 101 mount plate | 6.0 mm | 10.0 mm | Receiving pilot corrected; verify blind-hole bottom/runout. |
| 607 guard cover screw | 4 | 601 guard shell | 5.0 mm | 9.0 mm | Receiving pilot corrected; choose actual screw length. |

Do not order the screws by their file labels alone. Several lengths and head heights were drawn as envelopes, not standard hardware. Use a specified standard and part number, then recheck protrusion, bottoming, head clearance and tool access. Do not use a steel-nut tightening torque for a short copper tapped hole or a ceramic-bearing joint. Inserts are an option, but their vacuum compatibility, wall thickness and installation access need design work.

## Remaining defects and design decisions, in priority order

### 1. Electrical sockets do not define an actual connection

The 201 rod socket has a Ø6.5 bore around a nominal Ø6.4 feedthrough pin: 0.05 mm radial clearance. The 603 rear terminal likewise has a Ø6.4 socket around a nominal Ø6.4 pin, without a clamp, setscrew, collet split, spring contact or specified press fit. At the yoke, a Ø6.7 rod feature meets a Ø6.7 hole at nominal size, also without a specified joint. The cable core meets the terminal envelope without a modeled termination.

These interfaces may appear connected in a rendering but do not establish reliable mechanical or electrical contact. Select an engineered clamp/collet or supplier termination, define contact pressure and retention, and keep assembly torque and cable loads off the ceramic feedthrough. This is a build-blocking interface, not a detail to improvise during assembly.

### 2. Coolant route exists, but its joints are not build-to-print

The two coolant ports enter the C-channel on opposite sides of its divider. The jacket has backplate, core and target-seat cover layers, and the fasteners lie outside the nominal water cavity. This arrangement is mechanically plausible.

However, most tube/socket/jacket interfaces are coincident or near-coincident nominal surfaces. They do not specify braze clearance, insertion stops, weld preparations, filler alloy, joining method, cleaning, accessibility or inspection. A geometric butt contact is not a leak-tight joint. The stainless/copper transitions especially need an approved joining process.

Treat 305/306/308 as one permanently joined jacket. Join and test it before installing magnets or ceramic parts. Locate/hold the layers during brazing, control distortion, finish the target face as required, and verify the two ports and divider stay open. Specify a test method and acceptance criteria with the fabricator.

### 3. Whole-head removal is not the same as target replacement

Removing the shield and clamp makes the target accessible without opening the water jacket. That is a useful feature. Removing the whole cathode head is different: the two permanent coolant legs cross that interface. The current design does not provide a disconnect or a documented way to withdraw the head and plumbing together.

Choose explicitly between a permanently plumbed gun with target-only routine service and a removable cartridge with engineered vacuum-compatible coolant disconnects. Do not label the existing whole head as quickly replaceable. An exploded inspection view of joined parts is not an assembly/disassembly procedure.

### 4. Ceramic mounting needs controlled clearances and preload

The stepped carrier seats on the stem and is captured by the keeper. This is a plausible load path, and live screws are distinct from ground-side keeper screws. But the nominal axial stack is face-to-face with no finished tolerance scheme, shim selection, preload limiter or compliance definition. Tightening the keeper or retainer bolts can impose uneven loads on ceramic or magnets.

Specify datum faces, flatness, edge breaks, axial capture clearance, a shim/compliant-washer strategy and a repeatable assembly procedure. Account for metal/ceramic thermal expansion. The internal 202 ceramic guide also lacks a clearly defined axial retention feature; explain what prevents migration and whether it is intended to float. The reduced center bore is a retention correction, not proof of electrical clearance or ceramic stress.

### 5. Magnet circuit has a fundamental unresolved topology question

In R09, as in R08, the 5 mm magnets are behind an 8 mm continuous steel yoke, followed by the copper jacket and 6 mm target. The magnet front plane is at x=148.7 mm; the target front is x=174.7 mm, a 26 mm separation with steel in between. Opposite magnet poles face that same steel plate.

Engineering inference: that plate can provide a short magnetic return path behind the target and reduce useful field over the target. This is not a simulated result, and the design has not been proven to fail. A candidate redesign would place the return yoke behind the magnets, with the pole faces toward the target and a nonmagnetic structure between poles and target. That would require reworking support, screws and plumbing, so it has not been silently imposed on this mechanical revision. Verify a closed racetrack field with a magnetic model or a real magnet-pack field map before accepting the gun topology.

### 6. Purchased envelopes must be replaced by actual supplied parts

The Ceramaseal feedthrough, KF clamp/O-ring/centering ring, ceramic breaks and cable/terminal are envelopes. In particular, the feedthrough is simplified as one body rather than a complete ceramic/metal assembly, and the clamp is an unsplit ring envelope. Their CAD shape cannot establish the real sealing geometry, installation access or component rating.

The Lesker CFT05W0321 page identifies a 1/4-inch OFHC-copper socket/alumina break. Obtain its controlled dimensional drawing/STEP, pressure rating and permitted joining procedure before freezing the transitions. Do not fabricate the current ceramic-break envelope as if it were a validated hermetic component.

### 7. Chamber mount and rear utility exits are incomplete

The part named NW100 plate is essentially a Ø130 disk with a central opening and utility holes. A diameter/name alone does not define the actual chamber flange standard, seal seat, clamp/bolt interface, surface finish or matching adapter. Supply the mating chamber flange drawing and finish that interface.

The rear guard encloses the atmospheric coolant stubs, but has no finalized hose exits, external elbows, cable gland/strain relief, grounding lug or cover-interlock mounting. The current central rear opening only reserves space for cable insulation. Route all utilities with real fittings before releasing the shell. These are physical packaging and assembly omissions.

### 8. Nominal gaps and service access still need tolerance checks

The shield ID is Ø72.8 around the Ø68.8 live head, giving 2.0 mm radial nominal clearance. Its front lip begins 5.0 mm ahead of the target face and 3.0 mm ahead of the ring front. These are geometry values, not electrical ratings. Include concentricity, thermal movement and deposited film thickness in the clearance budget.

Shield extraction needs approximately 41 mm axial travel to clear the retaining ring, plus handling/tool allowance. Its screws are accessible axially outside the shield body. Verify that the actual chamber has this space. Clamp screws become accessible after the shield is removed. Ground-keeper screw access is from the stem side; assemble the live head/ceramic stack on the bench and pre-position the keeper before permanent plumbing prevents access.

### 9. Manufacturing documentation is still required

The native revolved profiles were generated from coordinate-defined sketch segments, not a fully dimensioned and constrained production feature scheme. Hole features are plain cuts, with thread intent stored in properties; they are not production Hole Wizard callouts. No released drawings, complete GD&T, weld symbols, braze notes, ceramic tolerances, seal-finish requirements or procurement BOM existed in the baseline.

The CSV supplied here is an instance inventory, not a purchasing BOM. Finish drawings and process specifications after the interface decisions above. Small copper bores/slots and ceramic holes need fabricator review; use achievable stock/forms and radii rather than assume every sharp CAD corner can be produced literally.

## Suggested build sequence after the open interfaces are resolved

1. Finalize real chamber flange, feedthrough, coolant breaks, screw standards and power termination; update their native models.
2. Fabricate the mount/stem/seat weldment; complete and inspect all vacuum-boundary welds.
3. Machine and permanently join the copper jacket and its tubes; inspect flow continuity, leakage and target-face flatness before adding heat-sensitive components.
4. Install the keeper in the required order; assemble the carrier, locator, magnet pack and head using controlled clearances and specified preload. Verify that no ceramic or magnet is trapped in an unintended compression stack.
5. Complete the defined plumbing architecture with supported joints; install/retain the rod guide and engineered power contacts.
6. Fit target and clamp, then the grounded shield. Confirm target-only servicing without disturbing the jacket.
7. Install rear hoses, cable termination, strain relief, protective bond and interlock hardware, then close the guard.
8. Inspect the completed assembly against drawings and perform leak, coolant, retention and electrical checks before any plasma trial. Verify magnetic field independently.

## Verification evidence

- R08 opened in SolidWorks with nine top-level groups, 85 total component entries and 76 leaf part instances; no missing referenced files. Its rebuilt nominal model reported zero volumetric interferences. That did not detect the fastening defects above.
- R09 changes were generated through the installed SolidWorks API as native feature-based parts. The existing imported channel/transition bodies and unchanged parts were retained.
- R09 nominal interference check returned 23 overlaps, all between the seven screw families and their newly defined receiving pilot bores. The values match π(1.5²−1.25²) times the respective nominal engagement lengths. No other volumetric collision was returned in that check. This excludes coincident faces and is not a clearance/tolerance or tool-sweep proof.
- The C-channel solid volume remains 8,355.796 mm³. That is a regression check on the model, not a fluid-flow or leak test.
- The interactive viewer uses tessellated native SolidWorks part geometry, with coordinate quantization for display. Measurements and manufacture must use the native CAD, not the display mesh. Exploded offsets are illustrative.
- No FEA, magnetic FEA, thermal simulation, tolerance Monte Carlo, actual fabrication or physical test was completed. Performance cannot be certified from this review.

## Sources and distinction from model evidence

The geometric findings above come from the local CAD/scripts and SolidWorks checks. These external sources provide context, not validation of this custom gun:

- [Lesker CFT05W0321 ceramic break](https://www.lesker.com/feedthroughs/ceramicbreaks-liquid/part/cft05w0321): purchased-part identity and interface information.
- [Lesker sputtering source technical notes](https://www.lesker.com/newweb/deposition_sources/technotes_sputtering.cfm?section=tech): target cooling concepts; a clamped target interface still needs thermal-contact design.
- [Lesker magnetic-target guidance](https://www.lesker.com/newweb/faqs/question.cfm?id=475): target material/thickness affects magnetic field transmission. The current aluminum target does not establish compatibility with every other material.
- [SolidWorks interference detection](https://help.solidworks.com/2025/English/SolidWorks/sldworks/HIDD_DVE_INTERFERENCE.htm): geometric interference tools do not replace joint engineering.
