# R07 coolant circuit

The two angled transition solids terminate at the same axial planes as the adjoining components, X = 25.7 and 49.7 mm. Their centerlines remain aligned with the bulkhead and dielectric line bores at each interface. The planar cuts produce elliptical tube ends. The native SolidWorks assembly reports zero solid interferences and zero missing references. These results describe nominal CAD geometry.

## Joining and sealing

- **Bulkhead and transition.** Use a stainless transition and a continuous vacuum-qualified weld at the stainless bulkhead. Form or machine the ends to match the bore and joint faces before welding. Seal the bulkhead shank to the mounting plate with a separate circumferential weld. Inspect the wetted bore for weld intrusion.
- **Dielectric line.** Use a vacuum-compatible liquid electrical break with independent metal end stubs. Join the transition to one stub and the cathode tube to the other using compatible qualified weld or braze joints. Specify a matching metal end adapter to take up the elliptical-to-round section. The physical electrical break, adapter and its retention hardware must be selected and modeled before fabrication. Keep the fittings on either end electrically separated. Qualify leakage current through the coolant in DC and RF.
- **Copper jacket.** Use oxygen-free copper for the backplate, C-channel core and target-seat cover. Specify continuous vacuum-braze seams on the channel perimeter, inner land and divider on both faces of the core. Braze the two cathode-side tube ends into the backplate using a qualified socket joint. Keep filler out of the bores and channel. The head screws attach the bonded jacket to the yoke and sit outside the fluid boundary. Confirm braze gap, filler, sequence and pressure capability with the fabricator.

## Verification

The channel was modeled as one connected void. Boolean checks confirmed that the full area of both Ø4.8 mm backplate openings lies inside that void, on opposite sides of the divider. The imported SolidWorks channel core volume matched the source solid at 8,355.796 mm³. The metal tubes have a Ø3.3 mm nominal internal bore.

Before attaching the jacket to the gun, confirm flow through both ports, pressure-test the circuit to a basis set by the selected coolant hardware, and helium leak-test the coolant-to-vacuum boundary. The CAD check establishes geometric connectivity at the jacket ports. Joining details and leak performance require qualification on the hardware.

Reference for vacuum-brazed copper assemblies and leak testing [CERN Accelerator School on Vacuum for Particle Accelerators](https://cds.cern.ch/record/2942302/files/2006.12072.pdf).
