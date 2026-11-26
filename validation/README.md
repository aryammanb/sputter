# Snapshot verification

Repository checks verify the package rather than the physical machine.

| Record | Check scope |
|---|---|
| [File manifest](file-manifest.json) | SHA-256 and byte length for every selected payload file; excludes generated reports and itself |
| [Repository check](repository-check.json) | Payload hashes, relative links, current artifact selections, workbook export and media/field source hashes |
| [Media check](media-check.json) | Stream inspection, hashes and complete decode checks for the three selected current silent walkthroughs |
| [CAD check](cad-check.json) | Independent reopening of current STEP, component/solid counts and validity classifications |

The workbook was preserved unchanged; exports inspect saved values/formulas and do not claim recalculation. Current rendered stills were visually reviewed. Field resampling reproduced the original mean before sampling the current plane. Historical FEM solver checks are retained as supplied, not described as newly rerun.

Run `python tools/validate_repository.py` after cloning. CI performs the same standard-library integrity check on pushes and pull requests. For physical fabrication/operation requirements, read [engineering verification gates](../docs/verification.md).
