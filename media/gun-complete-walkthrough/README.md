# Complete R06 sputter-gun CAD walkthrough

[Silent walkthrough](R06%20sputter%20gun%20-%20complete%20silent%20walkthrough.mp4) · [Narrated companion](R06%20sputter%20gun%20-%20complete%20narrated%20walkthrough.mp4)

Both versions contain the same 60 detailed 1080p shots. The main version has no audio; each view uses a short part label and one function/connection line. The companion adds synthetic narration without changing the pictures or omitting shots.

All 141 current R06 component instances are accounted for in [component-coverage.json](component-coverage.json). Each instance has dedicated coverage beyond the general complete/exploded views. Repeated components appear in their full patterns, with close-ups of individual connections where appropriate.

The walkthrough opens the shield and target assembly, explains the copper cooling passage and seals, separates both magnet systems and the yoke, shows spacer and head fasteners, opens the main PTFE/body sealing stack, details an individual screw shoulder sleeve and all twelve installed positions, and follows the full RF centre and shield connections. The five coax parts, small ground carrier, spring clamp, mounting screw, nut, blind anchor screw, live stand-off, terminal screw and ring lug are individually included. The service-tube joint, centering ring, O-ring, two clamp halves, six clamp screws, both coolant fittings, both release rings and both hoses are also included before full reassembly.

Visible geometry comes from the 141 gun components in the actual R06 system STEP, in installed coordinates. That preserves the current gun orientation and target datum used in the system walkthrough. Sections clip these actual component meshes; no replacement cylinders, generic gun internals or imagined supplier internals are introduced. Selected context parts are made translucent to expose otherwise-hidden connections. Coax layers receive distinct material colors for jacket, shield, dielectric and centre conductor.

Exploded offsets and screw turning illustrate mating relationships, not a certified installation sequence, prescribed turn count or torque. Nominal screw shafts, existing fitted seal envelopes and supplier-envelope limitations remain as modeled. RF, thermal, pressure/leak and manufacturing qualification are separate engineering work. Historical source part names can refer to earlier magnet sizes; the current R06 geometry and current engineering dossier take precedence. The PTFE sleeve is the current integrated one-piece sleeve/cup/lip geometry; a separate ceramic proposal is not substituted.

Reproduce with `python tools/build_gun_walkthrough.py`; append `--preview` for the contact sheet without rendering the movies. `provenance.json` records CAD hashes and chapter timings; `Narration.txt` contains the companion text.
