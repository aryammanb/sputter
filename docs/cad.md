# CAD access and editing

## Current deliverables

| Deliverable | Scope |
|---|---|
| [Magnetron R06 STEP](../chamber-design/coolant-fitting-r06/Magnetron%20R06.step) | Standalone neutral gun geometry |
| [Complete R06 system STEP](../chamber-design/coolant-fitting-r06/Complete%20sputter%20system%20R06.step) | Standalone system context with latest gun |
| [SolidWorks R06 package ZIP](../chamber-design/coolant-fitting-r06/Coolant%20fittings%20R06%20-%20SolidWorks%20CAD%20package.zip) | Native gun assembly and dependent parts |
| [Unpacked native assembly](../chamber-design/coolant-fitting-r06/SolidWorks%20R06/Magnetron%20R06%20-%20M5%20coolant%20fittings.SLDASM) | Open with adjacent SLDPRT files present |
| [R06 individual STEP parts](../chamber-design/coolant-fitting-r06/STEP%20parts) | Neutral component exports |
| [CB01 supplier handoff](../chamber-design/chamber-supplier-package/CB01%20supplier%20handoff.zip) | Frozen chamber scope and CAD reference, not approved manufacturing drawings |
| [Stage/shutter fabrication package](../chamber-design/stage-shutter-procurement/Stage%20and%20shutter%20-%20local%20fabrication.zip) | Separate fabricated stage and bent shutter references |

Dimensions are millimetres. Download the native ZIP or clone the entire repository before opening SolidWorks. Opening an isolated SLDASM from the GitHub web interface will omit its dependencies. Keep all native part files beside the assembly. The saved reopen/reference checks establish the original package state; after relocating, allow SolidWorks to resolve same-folder components if the original absolute search paths appear.

The native gun assembly contains fixed components. It does not provide editable assembly mates or a motion mechanism. Many components are imported solids. The R06 backplate has native cut-extrudes for the revised passages/tap drills; thread callouts/custom properties carry the M5 specification. Threads are nominal envelopes, not helical teeth.

## Checks supplied with R06

- [Geometry checks](../chamber-design/coolant-fitting-r06/Geometry%20checks.json): no new non-thread overlaps among the changed parts; intentional thread-envelope intersections are classified.
- [Native backplate independent check](../chamber-design/coolant-fitting-r06/Native%20backplate%20independent%20check.json): revised bore geometry matches expected geometry.
- [Native export check](../chamber-design/coolant-fitting-r06/Native%20assembly%20export%20check.json): 141 valid gun solids and small volume difference from reference.
- [Native reopen and reference check](../chamber-design/coolant-fitting-r06/Native%20assembly%20reopen%20and%20reference%20check.json): original saved package component references.
- [SolidWorks verification](../chamber-design/coolant-fitting-r06/SolidWorks%20verification.json): native import validity and per-part volume comparisons.

Read these as nominal geometry checks. They do not certify manufacturing tolerances, useful thread engagement, gasket compression, fatigue, leak integrity or thermal performance.

## Historical CAD and provenance

Source directories retain their original names and relative structure so the engineering scripts and their references remain inspectable. The `advanced-tinkering-original` directory includes subsequent updates as well as the reconstruction. “Original” in its name does not mean all its contents are superseded. The R06 gun and selected current files are the entry point.

Earlier loading/open-door STEP states remain under their revisions. No updated R06 loading state is claimed. Use the R06 assembled system for the current gun and use earlier loading states only to understand historical door/shutter motion.
