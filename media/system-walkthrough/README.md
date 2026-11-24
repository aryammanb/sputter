# Silent system CAD walkthrough

[Play the walkthrough](Sputter%20system%20-%20silent%20CAD%20walkthrough.mp4)

131 seconds, 1440 × 810, 24 fps. No audio or subtitles. Each shot carries only its assembly label. The current R06 STEP supplies all geometry; the gun stays assembled throughout.

The sequence covers the whole system, support frame, chamber, hinged loading door, viewport, stage, pump baffle, gun and top mount, rotary shutter, turbo and ISO63 connection, backing pump and foreline, gauges, argon supply, MFC and chamber fittings, spare ports, both cooling loops, RF supply and matching network, and protective earth.

Docking offsets illustrate attachment relationships, not an installation or service procedure. The door and shutter use their modeled rotation axes. Some chamber walls are hidden for access views. Highlighted assemblies use cyan; surrounding parts remain gray.

Purchased equipment retains the existing CAD reference envelopes. In particular, the visible RV3 is historical geometry; the selected backing pump is INDOVAC HV2-150. The MFC envelope does not establish the exact selected 200 sccm model or argon calibration. Utility cabinet dimensions remain representative.

Reproduce with `python tools/build_silent_walkthrough.py` from the repository root. `provenance.json` records the source hash and shot timings. `contact-sheet.jpg` shows the rendered shot previews.
