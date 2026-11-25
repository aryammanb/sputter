# Chamber and system design files

Start with [System architecture and CAD](../docs/design.md) for the system explanation, selected videos, essential renders and downloads. [Current selections](../design/current.json) identifies the governing artifacts.

## Current deliverables

| Folder | What to use it for |
|---|---|
| [coolant-fitting-r06](coolant-fitting-r06/) | Current R06 gun and complete-system STEP, native SolidWorks gun package, component exports and checks |
| [chamber-supplier-package](chamber-supplier-package/) | CB01 chamber manufacturing scope, frozen interfaces and supplier handoff |
| [stage-shutter-procurement](stage-shutter-procurement/) | Stage, bent shutter and local fabrication package |

## Supporting geometry and selections

| Folder | Why it remains here |
|---|---|
| [target-clamp-r05](target-clamp-r05/) | Current target/clamp dimensions and the source geometry used to prepare R06 |
| [main-system-r04](main-system-r04/) | Retained chamber/utilities layout, dimensions and source history for R05/R06 |
| [references](references/) | Coolant fitting selection/build scripts, gun-mount check, plumbing reference, RF selection and the current 500 sccm MFC note |

R04/R05 are supporting sources, not alternative current system downloads. Use the R06 assembly for the current geometry. Earlier videos inside source folders predate later changes; the combined guide selects the corrected exports.

## Earlier iterations

The [chamber-design archive](../archive/chamber-design/README.md) contains the earlier top-plate, chamber, compression-fitting and full-system iterations, plus superseded MFC notes. They remain available because later authoring scripts reuse some of their geometry and reference parts.

CAD assemblies, dependent part files and packaged deliverables keep their internal layout. No geometry or video has been regenerated. Saved historical records can contain their original absolute paths; [folder relocations](layout.json) maps the reorganized directories.
