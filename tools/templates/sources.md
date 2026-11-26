# Sources, attribution and rights

The project builds on a reconstruction and subsequent changes to an Advanced Tinkering magnetron concept. The original reconstruction workspace is not bundled; the external build references and retained current design records document that lineage. This snapshot does not assert ownership of the original design or assign an open-source license.

Supplier CAD, manuals, catalogs and drawings remain third-party reference materials. Their inclusion in this private engineering record does not grant redistribution rights. Review permissions and replace restricted references with links before making the repository public. The original downloaded source video, browser profiles and cached third-party media are not included.

## Project background and contributions

The [project presentation](../Sputter%20v2.pptx) describes the earlier HackerFab IITB sputter, the v2 objectives, design choices, procurement status and possible future improvements. Our earlier machine is distinct from the v2 CAD documented here. The [README introductions](../README.md#new-to-sputtering-start-here) link that build, Advanced Tinkering, The Thought Emporium, Applied Science and CMU HackerFab.

The presentation also credits images of an AJA system at IITBNF during a target change, supplied by Jai. These are design references rather than measurements of this proposed system.

As recorded in slide 20, ChatGPT assisted with research and ideation, SolidWorks API CAD work, component-list management, CAD animations and simulation/documentation scripts. Aryamman orchestrated and reviewed the work. AI-assisted output still requires the part-by-part engineering review and physical checks documented in [Review before building](verification.md).

## Reference locations

| Topic | Local evidence |
|---|---|
| R06 fitting selection | `system-architecture-and-cad/references/coolant-fitting-selection/` catalog and selection record |
| Current backplate/native CAD | `system-architecture-and-cad/models/` checks and notes |
| Selected target/clamp | `system-architecture-and-cad/sources/target-clamp-r05/` notes and dimensional checks |
| Chamber vendor scope | `system-architecture-and-cad/manufacturing/chamber/` CB01 scope, interface schedule and source references |
| Turbo/controller | Saved manual and procurement records; full-system supplier reference directory |
| MFC dimensional reference | Legacy HORIBA drawing (reference only) and R04 500 sccm selection note |
| Magnetic formulation/materials | Original `Simulation assessment.txt`, solver B-H data and requirements |
| Procurement selections/quotes | Current workbook, readable cell/CSV exports and selected support records |

URLs in the original notes and workbook are recorded sourcing references as of the project work. This repository preparation does not reverify current seller availability, quotations, exchange rates or published specifications. Prices in the documentation are dated planning records.

## CAD explanations and provenance

The combined CAD guide selects existing R06 system renders and the corrected walkthroughs; [current render assets](../design/current-render-assets.json) records their selection and hashes. No new videos were created for the documentation reorganization. Current screenshots are rendered from the R06 system STEP. Field plots are generated from the retained FEM solution at the current target plane. Narration uses Windows Microsoft David Desktop and is synthetic. No generated image is presented as a photograph of physical hardware, and no video is presented as a record of a working machine.
