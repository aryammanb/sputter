# R06 system assembly and operation walkthrough

[Silent four-minute version](Sputter%20R06%20-%20silent%204%20minute%20walkthrough%20v2.mp4) — all 37 shots retained in the original order and timing, with all audio removed. 1920 × 1080 at 60 fps; 3:59.6. The complete shutter assembly turns together, with only the compressed O-ring remaining stationary.

[Play the rebuilt walkthrough](Sputter%20R06%20-%20mechanical%20assembly%20walkthrough.mp4)

This rebuild follows the earlier R04 main walkthrough and its integrated compression-fitting demonstration. It uses the actual current R06 STEP component meshes, original component colors, 1080p rendering, and synthetic narration. The screen carries one short assembly/action label at a time.

The construction sequence shows the stand, welded chamber plates and necks, door hinge pins and gasket, viewport stack and retainer screws, baffle and stage, and shutter mounting. The gun sequence distinguishes the roof KF joint from the tube compression joint: body seating, hinged KF clamp closure, upward tube insertion, height adjustment, cap rotation and axial advance, a stationary section, and later repositioning. The gun itself stays assembled and opaque.

The remaining sequences follow the turbo inlet seal, four ISO63 claw clamps and screws, foreline flange joints, rear gauge elbows, MFC support screws, outlet and inlet VCR gaskets/nuts, gas tube insertion, argon route, cooling endpoints, and RF/earth connections.

The operating-cycle section shows substrate loading and door closure, the evacuation route, regulated argon admission, target conditioning with the shutter closed, the actual 80-degree shutter sweep, coating exposure with the shutter parked, shutter closure, and unloading after shutdown and venting. Narration explains the tool's thin-film purpose and the role of the shutter. No plasma, particle, or film-growth geometry is invented. The complete gun is temporarily hidden only in the top-down view of the shutter sweep.

Shutter actuation in the latest silent version: the top screw, nuts, washer and blade rotate together. Only the O-ring remains compressed and stationary. A small gold surface witness mark makes the round screw's rotation visible without changing the CAD geometry. The narrated exports predate this clarification.

All visible component solids come from `system-architecture-and-cad/models/Complete sputter system R06.step`, through its existing tessellation cache. No proxy solids, replacement gun, reconstructed chamber, or colored substitute assemblies are introduced. Fitting section faces are computed by clipping those actual component meshes. No gun internals are exposed. Part placements change only for exploded/assembly illustrations and modeled rigid motions.

The underlying CAD remains a design study. In particular, its fitting threads, seal seats, clamp profiles and some purchased equipment are existing nominal/reference geometry. The section does not simulate seal deformation. Cap turns and travel explain the modeled mechanism, not a purchased-part tightening instruction. Exploded approaches do not certify handling clearances, manufacturing order, weld procedures or installation safety. The historical RV3 reference remains in the source; selected backing-pump procurement is INDOVAC HV2-150. These source limitations are not repaired by rendering.

Reproduce: `python tools/build_assembly_walkthrough.py`. Preview only: append `--preview`. `provenance.json` records the STEP hash and timeline; `Narration.txt` contains the spoken text. The earlier silent tour remains separately available.
