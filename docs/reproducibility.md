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

Markdown, CSV, JSON and transcripts work directly in GitHub. Use a STEP-capable viewer for neutral CAD. Native SLDASM/SLDPRT editing requires a compatible SolidWorks installation; neutral STEP does not preserve native feature history. The currently selected system and gun walkthroughs are silent H.264 MP4s. Superseded design videos and redundant images have been removed.

## Dependencies and generated artifacts

Use Python 3.13 as the original authoring environment. [requirements-engineering.txt](../requirements-engineering.txt) records the versions used in this environment. For the original FEM pipeline, use [its pinned requirements](../simulations/magnetic-model/requirements.txt). Install into a separate virtual environment rather than modifying a system interpreter. Native SolidWorks regeneration also requires Windows/SolidWorks; its saved deliverables can be read without rerunning native automation.

Commands for the new reproducible layer, from the repository root:

```sh
python tools/export_procurement.py
python tools/reassess_current_field.py
python tools/build_documentation.py
python tools/package_repository.py
python tools/validate_repository.py
```

`export_procurement.py` reads the checked-in XLSX and creates CSV plus cell/formula records without modifying/recalculating the workbook. Formula results are the workbook's saved caches. `reassess_current_field.py` requires the saved fine nominal field and produces the new target-plane assessment and plots. The selected existing walkthroughs and eight essential stills are listed in [current render assets](../design/current-render-assets.json); no video rendering is needed to read or validate them. The original narrated-review renderer has been removed; `prepare_r06_mesh.py` retains the exact-STEP tessellation helper used by current authoring scripts. Only selected current media and their correction records are packaged. The checked-in mesh is a viewing convenience, not authoritative engineering geometry.

The main reader guides are maintained as Markdown templates under `tools/templates/`; `build_documentation.py` copies them to their published paths. Keep the template and published page aligned when editing. For example, the combined design page is sourced from `tools/templates/design.md`.

## Original FEM reruns

The following mirrors the original scripts' interface. It can overwrite original generated evidence; run in a disposable clone and compare results before accepting changes.

```sh
cd simulations/magnetic-model
python make_mesh.py coarse 1.8 80
python solve_field.py coarse nominal
python analyze_field.py metrics coarse_nominal
```

See the actual solver CLI in `solve_field.py` for supported material variants and analytic mode. The original scripts and full numerical outputs are retained. Exact bitwise FEM reproducibility is not promised across mesh generators, sparse solvers or platforms. Compare metrics and physical assumptions, not only file hashes.

## CAD source and portability limits

The original Advanced Tinkering reconstruction and its workspace are no longer bundled. The current R06 neutral/native models and the supporting R04/R05 snapshots remain. Saved CAD build-plan paths and workbook sourcing cells are historical records, rather than portable links.

The R06 preparation source is [prepare_r06.py](../system-architecture-and-cad/references/coolant-fitting-selection/prepare_r06.py); it starts from the retained R05 snapshot. Older R04/archive authoring scripts may refer to removed reconstruction inputs and are not supported full rebuild entrypoints. No clean rebuild of the entire historical design sequence is claimed.

Use a disposable clone for regeneration. Current model files and retained media are the practical handoff; [Review before building](verification.md) covers the outstanding physical checks.

## Updating integrity records

`tools/package_repository.py` selects meaningful source files, excludes application profiles/caches, old videos and repetitive intermediate renders, and writes `validation/file-manifest.json`. It does not move or delete local originals. Run it after adding a revision or generated artifact, then run validation. Do not treat a regenerated manifest as proof that changed engineering remains correct.
