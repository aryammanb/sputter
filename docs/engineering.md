# Engineering dossier

This dossier explains the reasoning supported by the supplied records. Detailed dimensions and checks remain linked so a reviewer can inspect the original evidence. The machine remains a prototype engineering study.

## Magnetron and magnetic return circuit

The selected head uses a centre pair of D20×10 N42 discs and twelve outer pairs of D6×10 N42 discs on PCD58. Centre N and outer S face the target. The nominal pole-area ratio 1.08 guided the candidate layout, while the FEM study checks near-target field. It does not establish exact balanced topology.

The model imports the proposed yoke, assumes an AISI1010 reference B-H curve and N42 remanence of 1.30 T at 20 °C. The actual steel grade/heat treatment and magnet properties remain unverified. Copper, target, coolant and insulation use relative permeability 1. Surrounding ferromagnetic equipment is omitted. See [simulation evidence](simulations.md) for numerical checks and the current target plane.

## Target, clamp and fasteners

The selected target is VritraTech Al99.99%, D50.8×3.175. Its back still seats at source Y0. R05 moves the clamp shoulder to Y3.175, retains front Y5 and leaves a 1.825 mm axial lip. The minimum aperture is D47.8, with a 0.25 mm contact-side chamfer and front flare D49.45. The nominal bearing band is 1.25 mm wide before actual target bevels.

Twelve M3×10 socket screws replace M3×8. Nominal straight shaft/tap-drill envelope overlap increases from about 3.55 to 5.55 mm, with 1 mm tip-to-pilot-bottom clearance. This is geometric overlap, not a full-thread or strip-strength rating. Real thread depth, copper strength, target thickness tolerance, preload, bottoming and thermal expansion require drawings and qualification. No tightening torque has been established.

The entire gun is raised 1.175 mm so the target front remains Z141 at the default gap. A nominal 1 mm live-clamp/grounded-shield gap remains. It is not an RF voltage rating. Evidence: [R05 redesign checks](../chamber-design/target-clamp-r05/Clamp%20redesign%20and%20verification.json) and [R05 notes](../chamber-design/target-clamp-r05/READ%20FIRST%20-%20Clamp%20R05.txt).

## Copper cooler, closure and coolant ports

R06 selects 2× SMC KQG2S04-M5, OD4 tubing, M5×0.8 male thread, nominal body OD9 and installed projection 14.1. Two D14 yoke openings leave 2.5 mm radial body clearance, and the collet extends 4.1 mm beyond the 10 mm yoke.

The backplate ports are at native X±18/Z0. Old D7.95 counterbores and D5 passages are removed. Revised D3 passages run through, with D4.2 tap drills 5 mm deep from rear Y−22.5 and a specification of M5×0.8-6H, useful thread ≥4 mm. The retained flat seat uses the manufacturer's specified M5 gasket. Thread tape does not replace that gasket interface.

The SMC vacuum-retention caveat, pressurized-water sealing, gasket seat tolerances, tube bend radius and compatibility remain unresolved. Current checks found no new non-thread geometric overlaps, with threaded engagement overlaps explicitly classified. No zero-leakage assertion follows. Historical copper-bonding explanations are proposals, not a completed joining revision. Evidence: [R06 scope notes](../chamber-design/coolant-fitting-r06/READ%20FIRST%20-%20Coolant%20fittings%20R06.txt) and [Fitting selection](../chamber-design/coolant-fitting-selection/Selection%20and%20required%20CAD%20changes.json).

## Cooling and electrical isolation

Procurement retains separate CW-5000-style gun and turbo loops. The gun budget uses a 300 W heat basis and 0.5 L/min target; the selected RF source is 200 W. That budget is conservative planning, not proof of a 300 W operating rating. The turbo loop targets 15 °C and 0.5 L/min commissioning flow. The recorded manufacturer minimum is 0.25 L/min at 15 °C; verify against the exact purchased unit and manual.

Actual coolant flow at installed head, pressure limits, heat transfer, target contact, magnet temperature, chiller duty, conductivity and live-cathode isolation still need measurements and design qualification. No completed thermal or CFD analysis is present. See procurement cooling tabs and [verification gates](verification.md).

## Vacuum and argon delivery

The selected route is chamber → EXT70 → one rotary vane pump, with no separate roughing bypass. Procurement selects INDOVAC HV2-150. The RV3 solid in context remains a legacy reference and has a known topology defect. The turbo exterior is reconstructed reference geometry; the outlet adapter depends on the actual received port.

The owner-selected MFC range is 200 sccm. Exact model, gas calibration, valve/interface configuration and low-flow accuracy remain to verify. For the recorded 0 °C standard flow reference and 20 °C gas assumption, throughput is `Q = 0.018124 × flow_sccm` mbar·L/s. At 200 sccm, Q≈3.6248 mbar·L/s. With effective speed 65 L/s, p≈41.83 mTorr. The 65 L/s example uses an N2 rating; actual installed Ar pumping speed is unverified. Pressure follows installed speed, conductance and gas load, and must be measured.

About 42 mTorr is an ignition trial idea, not an established threshold or a guaranteed maximum. Turbo gas load, backing pressure and drive power limits must be checked before commanding full flow. Consider low-flow accuracy at intended deposition flows. Evidence: [MFC R03 engineering assessment](../chamber-design/Argon%20MFC%20selection%20R03%20-%20200%20sccm.txt) and procurement tabs 05/07.

## Chamber, window, stage and mounting

The chamber package CB01 freezes nominal interfaces for a single Alfa Technovac order. Its INR100,000 is a planning allowance, not a quotation. Supplier scope includes shell, welded ports, door/window/seals, mating hardware and fixed mounting provisions. Pumps, gauges, the gland, removable stage/shutter and equipment stand remain separate.

The selected eBay compression gland is not confirmed as the Lesker reference model. A 25.4 mm gun tube must pass through the complete KF25 centering/seal/gland stack. Nominal model clearance is not purchased-hardware compatibility. The supplier must qualify bore, seal stack and tolerances.

The D70 viewport centre was lowered to Z105. R05 ray checks give 43/72, 55/72 and 31/72 clear sampled rays at gaps 75/100/150 from the stated eye position. These are partial geometric ring samples, not percentages of visible plasma. Window coating, real eye positions and glow distribution are unmodeled. Blind door retainer pilot holes have retained backing; actual threads/engagement still require release detail.

Nominal shell thickness, seals, welds, window stress and door closure are not supported by a completed structural FEA or released pressure design. The stage/shutter package includes a developed blank with a chosen K-factor; material, bend allowance and fabricated fit must be agreed with the shop.

## RF, controls and integration

Procurement selects a provisional Omicron 200 W RF source and matching network. Earlier 300 W language is superseded as an operating selection. Connector/coax insulation, matched-side voltage/current, cathode isolation, protective earth/RF bonds and water-loop isolation remain engineering checks. A nominal SMA mechanical envelope does not establish suitability for this source.

The controls budget includes emergency stop, door switch, flow/temperature inputs, pressure interface and RF permit logic. A proposed permit requires door closed, suitable measured pressure, healthy gun cooling and reset emergency circuit. Loss of a required condition must remove RF permission; reset must not automatically restart it. Final fault handling and turbo run-down behavior depend on the actual equipment. No completed wiring schematic or assessed safety performance level is claimed.
