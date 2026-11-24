# Fresh magnetron — concept 01

20 November 2026. Preliminary architecture, not fabrication geometry.

**Current revision: [RevB magnetic cooling head](RevB/README.md).** The earlier two-part RevA CAD and videos are superseded: they did not reserve magnet space. RevB coordinates the cooling body/cover with seven dry magnet wells, the magnet pack, locator, yoke and utility routes. Magnet and seal performance remain unverified.

## Confirmed requirements

- 2-inch (50.8 mm nominal diameter) target. Thickness, material and retention method are open design choices.
- Retain the previously selected Ceramaseal 16959-01-KF RF feedthrough and its KF25 mounting interface. User confirmed reuse on 20 November 2026. Identification comes from the R09 part inventory; the existing CAD is an envelope, not a controlled supplier model. Design the new gun around this component rather than substituting another feedthrough.
- Take inspiration from Advanced Tinkering's O-ring sealing and integrated water cooling. The supplied STEP parts are reference geometry, not requirements or verified assembly evidence.
- Keep the magnet compartment dry and connected to atmosphere through the rear of the gun.

## Scope reset — 20 November 2026

The user clarified that only the selected feedthrough and 2-inch target diameter carry forward from the previous gun. This supersedes the earlier carry-forward of NW100 mounting, 3.175 mm target thickness and DC + RF operation. Chamber interface, target thickness, operating modes, power/voltage envelope, dimensions, materials, magnet arrangement, insulation and construction methods are open. Retaining an RF feedthrough does not by itself establish a complete operating specification.

The O-ring sealing, water cooling and atmospheric magnet cavity remain the inspiration for this new concept. All architecture below is a proposal for development, not an inherited or approved detailed design.

## Proposed architecture

From the process side toward the rear: removable grounded shield; target retaining ring and target; continuous copper target seat; enclosed water passage behind that seat; dry magnet pack and steel return yoke; rear atmospheric service cavity through an electrically insulating vacuum-boundary assembly; grounded chamber mount and rear enclosure.

Use an indirectly cooled target: its back contacts the copper seat, and water remains inside the cooling body when the target is changed. A bolted rear coolant cover uses static face O-rings. Arrange the coolant-cover seals to separate water from the dry atmospheric interior where geometry permits. The continuous copper front wall remains the water-to-vacuum boundary beneath the target. Route inlet and return from the rear atmospheric side.

The dry magnet cavity needs an actual passage to room atmosphere. O-rings alone cannot establish its pressure. A rear protective enclosure must preserve that pressure connection while protecting live parts. This does not mean exposing live components through an accessible opening.

Channel geometry and magnet positions are coupled: locate coolant beneath the heated target region while minimizing the target-to-magnet distance. Do not choose channel depth, front-wall thickness or magnet dimensions independently. An annular passage with a divider is a candidate; a sealing strategy for the divider must prevent an inlet-to-return shortcut.

## Boundary and seal plan

| ID | Boundary | Proposed treatment |
|---|---|---|
| B1 | Water / chamber vacuum | Continuous copper target-seat wall; size for pressure, temperature, erosion protection and flatness |
| S1 | Water / atmospheric magnet cavity | Static face seal(s) between copper body and removable coolant cover; number and diameters follow the actual wet perimeter |
| S2 | Live copper body / insulating vacuum-boundary member | Vacuum O-ring seal with controlled compression and a defined retaining load path |
| S3 | Insulating member / grounded housing | Separate vacuum O-ring seal; retain electrical separation between housing and cathode |
| S4 | Gun mount / chamber flange | Select chamber interface afresh, then specify its mating seal |
| S5 | Coolant inlet and outlet / surroundings | Rated fittings on the atmospheric side with supported hoses |

S2 and S3 are functional interfaces, not finalized groove locations. Neither an O-ring nor a coolant hose is an electrical-isolation rating. The coolant-wetted cathode is live; both coolant legs require an engineered isolation arrangement. Establish DC leakage and RF return-current behavior with the actual coolant circuit.

The retained Ceramaseal feedthrough supplies the cathode electrical connection. Its placement relative to the atmospheric magnet cavity is still to be designed: an atmospheric cavity does not by itself require the electrical conductor to cross the chamber vacuum boundary. Show the pressure region on each side of the retained feedthrough explicitly in the axial section. Keep its KF25 sealing interface, conductor termination, mechanical support and RF return path explicit; do not use its ceramic as structural support for the gun. Obtain the controlled supplier drawing and confirm operating ratings before dimensioning its final mounting and connections.

Retain seals mechanically with hard stops or controlled gland geometry; do not use O-ring compression as the target-clamp adjustment. Select insulating material after evaluating creep, thermal expansion, sealing loads and electrical conditions. PTFE from the reference design is a candidate, not a fixed requirement.

## Service concept

Removing the shield and target clamp should leave the water enclosure and atmospheric-cavity vacuum seals assembled. Opening the coolant cover is a separate drained service operation. Keep fastening holes outside wet passages and avoid unvented trapped volumes on the vacuum side. Shield the vacuum-exposed insulation and seals from direct plasma and deposited films.

## Next design work

1. Inspect and reconstruct the reference assembly sufficiently to trace its wet, dry and vacuum regions; do not infer mating relationships from filenames alone.
2. Draw our own axial section showing every boundary, seal, vent passage, fastener load path and electrical potential.
3. Establish the power/voltage envelope, coolant inlet temperature, available flow/pressure, operating orientation, chamber geometry and required vacuum performance.
4. Budget the target-to-magnet distance and cooling area; choose magnet layout, channel dimensions, copper wall thickness and housing diameter together.
5. Size glands from the selected seal manufacturer's static liquid/vacuum guidance. The supplied O-ring dimensions are reference values only; the 62 mm entry has an inconsistent 76 mm supplier link.

No thermal, magnetic, structural, RF or leak performance has been established for this concept.

## Engineering references

- [Lesker sputtering-source technical notes](https://www.lesker.com/newweb/deposition_sources/technotes_sputtering.cfm): direct and indirect cooling, including clamped targets on a cooling well.
- [Parker O-Ring Handbook](https://www.parker.com/content/dam/Parker-com/Literature/O-Ring-Division-Literature/ORD-5700.pdf): static liquid and vacuum face-seal gland design.
