# Verification, qualification and release gates

Completed checks are evidence of their stated scope. They do not release the machine for fabrication or operation.

| Area | Supplied evidence | Required next evidence |
|---|---|---|
| Gun geometry | R05 interference checks; R06 changed-part checks; native gun 141 valid solids | Released drawings, datums, materials/finishes and tolerances |
| Coolant joints | Nominal M5 ports/gasket seats and fitting clearance | Vendor suitability, specified gasket compression, thread depth, leak/pressure tests with acceptance criteria |
| Target clamp | Revised lip/shoulder and screw engagement envelopes | Target tolerance, preload/strip strength, stiffness and thermal contact qualification |
| Magnet circuit | Nonlinear FEM and numerical checks; current-plane sampling | Actual magnet/yoke material data and calibrated Hall-probe comparison |
| Thermal | Cooling selections and planning heat basis | Measured installed flow/head, pressure drop, chiller capacity and temperatures under staged load |
| Chamber/window | Frozen nominal interfaces and supplier scope | Supplier structural basis, rated window/closure, weld/material documents and measured leak acceptance |
| Compression gland | Model clearance and reference fitting | Identify actual hardware; verify full 25.4 mm tube passage, sealing, retained support and travel |
| Vacuum | Selected pump topology and equipment budget | Received-model manuals, controller/cable compatibility, gas-load/backing-pressure limits and pumping tests |
| MFC/gas | Owner range selection; throughput calculation | Exact Ar calibration, low-flow accuracy, regulator/valve compatibility, measured pressure response |
| RF/electrical | Provisional source/matcher and controls budget | Source interfaces, cable/connector ratings, electrical design, grounding/isolation tests and qualified fault logic |
| Stage/shutter | Separate CAD/developed blank and stock items | Bend tolerances, installed clearance/travel and shaft seal qualification |
| Procurement | Workbook selections and allowances | Actual quotes/receipts, tax/freight, received condition, serials and acceptance records |

## Proposed commissioning sequence

These are planning gates, not an operating procedure for energized equipment. Establish final procedures using actual equipment manuals and qualified design review.

1. Freeze and inspect received hardware against the interface register. Resolve RV3/HV2-150, MFC, turbo outlet and cabinet mismatches.
2. Complete manufacturing drawings and supplier acceptance requirements. Confirm vessel/window suitability, materials, seals, threads and welding/cleaning.
3. Qualify each pressurized coolant joint before installation. Establish leak-test method and acceptance threshold, then test installed cooling paths and electrical isolation.
4. Verify protective earth, RF bonds, insulation, emergency/reset behavior, door/pressure/flow/temperature interlocks and actual fault handling without enabling the discharge.
5. Verify pump/controller/cable/supply compatibility. Establish backing, vent, exhaust/oil-mist and turbo run-down procedures from actual manuals.
6. Establish vacuum integrity, base pressure and argon flow/pressure response within pump load limits. Document calibrated gauges and MFC basis.
7. Map the cold magnetic field above the actual target and compare with the model, keeping probe position and orientation records.
8. Commission at staged source conditions with measured coolant flow, temperatures and pressures. Record ignition/stability, faults, deposition and erosion before assigning an operating envelope.

## Current repository checks

The [validation directory](../validation/README.md) records file hashes, local-link checks, media stream/decode checks, workbook export status and CAD read results. These repository checks establish package integrity and readability. They are distinct from the physical engineering gates above.
