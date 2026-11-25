# Reproducing the work

You can read the project without rebuilding anything. Use [System architecture and CAD](../system-architecture-and-cad/README.md) for the selected files and current walkthroughs, [Parts and procurement](../procurement/README.md) for the workbook and exports, and [Engineering and simulations](engineering.md) for the calculations.

## Obtain and check the repository

```sh
git clone https://github.com/aryammanb/sputter.git
cd sputter
python tools/validate_repository.py
```

The repository uses ordinary Git files, without Git LFS pointers or external submodules. A full clone includes current CAD, procurement, new media and retained simulation data. GitHub may require downloading a raw binary or cloning to open it. Read access requires permission while the repository is private.

## Read without a CAD license

Markdown, CSV, JSON and transcripts work directly in GitHub. Use a STEP-capable viewer for neutral CAD. Native SLDASM/SLDPRT editing requires a compatible SolidWorks installation; neutral STEP does not preserve native feature history. The currently selected system and gun walkthroughs are silent H.264 MP4s. Older narrated exports have separate audio/subtitle arrangements; they are retained as historical records.

## Dependencies and generated artifacts

Use Python 3.13 as the original authoring environment. [requirements-engineering.txt](../requirements-engineering.txt) records the versions used in this environment. For the original FEM pipeline, use [its pinned requirements](../advanced-tinkering-original/balanced-twelve-stack-study/magnetic-simulation/requirements.txt). Install into a separate virtual environment rather than modifying a system interpreter. Native SolidWorks regeneration also requires Windows/SolidWorks; its saved deliverables can be read without rerunning native automation.

Commands for the new reproducible layer, from the repository root:

```sh
python tools/export_procurement.py
python tools/reassess_current_field.py
python tools/build_documentation.py
python tools/package_repository.py
python tools/validate_repository.py
```

`export_procurement.py` reads the checked-in XLSX and creates CSV plus cell/formula records without modifying/recalculating the workbook. Formula results are the workbook's saved caches. `reassess_current_field.py` requires the saved fine nominal field and produces the new target-plane assessment and plots. The selected existing walkthroughs and eight essential stills are listed in [current render assets](../design/current-render-assets.json); no video rendering is needed to read or validate them. `build_current_media.py` is the earlier narrated-review renderer and does not reproduce the later corrected system/gun edits. Their historical authoring scripts and correction records remain alongside the assets. The checked-in mesh is a viewing convenience, not authoritative engineering geometry.

The main reader guides are maintained as Markdown templates under `tools/templates/`; `build_documentation.py` copies them to their published paths. Keep the template and published page aligned when editing. For example, the combined design page is sourced from `tools/templates/design.md`.

## Original FEM reruns

The following mirrors the original scripts' interface. It can overwrite original generated evidence; run in a disposable clone and compare results before accepting changes.

```sh
cd advanced-tinkering-original/balanced-twelve-stack-study/magnetic-simulation
python make_mesh.py coarse 1.8 80
python solve_field.py coarse nominal
python analyze_field.py metrics coarse_nominal
```

See the actual solver CLI in `solve_field.py` for supported material variants and analytic mode. The original scripts and full numerical outputs are retained. Exact bitwise FEM reproducibility is not promised across mesh generators, sparse solvers or platforms. Compare metrics and physical assumptions, not only file hashes.

## CAD source and portability limits

Historical CAD/video scripts are included for engineering traceability. Several original scripts contain Windows paths, COM automation, local font/voice choices or links to earlier study files. They have not all been ported or rerun in a clean environment. Their presence does not imply a one-command rebuild of every historical assembly. The current standalone STEP/native package is the practical design handoff.

The current R06 CadQuery preparation source is [prepare_r06.py](../system-architecture-and-cad/references/coolant-fitting-selection/prepare_r06.py); it reuses R05 geometry and metadata from the repository root. That script changes generated CAD files, so run in a disposable clone. Native build plans preserve original path strings as provenance; adapt paths for regeneration. Original reconstruction scripts may need externally sourced reference video; that third-party video/browser cache is deliberately not republished.

## Updating integrity records

`tools/package_repository.py` selects meaningful source files, excludes application profiles/caches, old videos and repetitive intermediate renders, and writes `validation/file-manifest.json`. It does not move or delete local originals. Run it after adding a revision or generated artifact, then run validation. Do not treat a regenerated manifest as proof that changed engineering remains correct.
