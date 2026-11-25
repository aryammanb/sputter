"""Build the repository reading paths and procurement views from frozen sources."""
from pathlib import Path
from urllib.parse import quote
import csv, json

ROOT=Path(__file__).resolve().parents[1]
DOC=ROOT/'docs';DOC.mkdir(exist_ok=True)

def write(path,text):
    p=ROOT/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text.strip()+'\n',encoding='utf-8')

def link(label,path,depth=1):return f'[{label}]('+('../'*depth)+quote(path,safe='/')+')'
R06='cad/coolant-fitting-r06/'
R05='cad/target-clamp-r05/'
R04='cad/main-system-r04/'
SIM='advanced-tinkering-original/balanced-twelve-stack-study/magnetic-simulation/'

def main():
    # Export exact instance metadata; legacy source names are retained as provenance.
    register=json.loads((ROOT/'cad/coolant-fitting-r06/R06 component register.json').read_text())
    (ROOT/'design').mkdir(exist_ok=True)
    with (ROOT/'design/current-component-register.csv').open('w',newline='',encoding='utf-8') as f:
        writer=csv.writer(f);writer.writerow(['instance','group','role','source_name','solid_count','valid','volume_mm3','note'])
        for i,q in enumerate(register,1):writer.writerow([i,q['group'],q['role'],q['name'],q['solid_count'],q['valid'],q['volume_mm3'],q['note']])
    assessment=json.loads((ROOT/'simulations/current-target-r06/assessment.json').read_text())['current']
    manifest = json.loads((ROOT/'design/current.json').read_text(encoding='utf-8'))
    write('design/current.json',json.dumps(manifest,indent=2))
    write('README.md', (ROOT/'tools/templates/README.md').read_text(encoding='utf-8'))
    write('docs/current-design.md', (ROOT/'tools/templates/current-design.md').read_text(encoding='utf-8'))
    write('docs/design.md', (ROOT/'tools/templates/design.md').read_text(encoding='utf-8'))
    write('docs/system.md', '# System architecture\n\nContinue to [System architecture and CAD](design.md), including CAD downloads, current walkthroughs and essential rendered views.\n')
    write('docs/cad.md', '# CAD\n\nContinue to [System architecture and CAD](design.md#cad-downloads) for downloads, current walkthroughs, rendered views and editing notes.\n')
    write('docs/engineering.md', (ROOT/'tools/templates/engineering.md').read_text(encoding='utf-8'))
    write('docs/decisions.md', (ROOT/'tools/templates/decisions.md').read_text(encoding='utf-8'))
    write('docs/simulations.md', (ROOT/'tools/templates/simulations.md').read_text(encoding='utf-8'))
    write('docs/verification.md', (ROOT/'tools/templates/verification.md').read_text(encoding='utf-8'))
    write('docs/reproducibility.md', (ROOT/'tools/templates/reproducibility.md').read_text(encoding='utf-8'))
    write('docs/sources.md', (ROOT/'tools/templates/sources.md').read_text(encoding='utf-8'))
    write('CHANGELOG.md','''
# Change log

## 2026-11-24 — Repository engineering snapshot

- Select R06 native gun and system context as the current CAD, retaining R05 target/clamp and R04 system layout.
- Preserve the latest procurement workbook unchanged; add 13 CSV tabs plus exact cell/formula-cache exports.
- Add a navigation README, engineering dossier, revision/decision registers, CAD guide, simulation evidence and verification/reproduction guides.
- Resample the saved refined magnetostatic field at the current 3.175 mm target plane. Keep original 2 mm results as historical numerical evidence.
- Add fresh R06-derived narrated videos, captions, transcripts, stills and source hashes. Exclude prior-revision videos from the current library.
- Preserve engineering CAD/scripts/checks and numerical data at original relative paths. Exclude browser caches, dependency folders, downloaded reference video and redundant render intermediates.
- Record known context mismatches and open physical qualification work without treating them as completed analyses.

## Preceding engineering revisions

R06 updates coolant fittings/backplate to SMC M5 hardware. R05 fits the 3.175 mm aluminium target with revised clamp and M3×10 screws. R04 integrates utilities and lowers the viewport. Earlier system R03, chamber R01, compression R02 and magnetron studies remain under their dated/revision source directories. Refer to their original notes for detailed histories.
''')
    # Extract the exact saved planning amounts rather than recalculating the workbook.
    with (ROOT/'procurement/subsystems.csv').open(encoding='utf-8') as f:rows=list(csv.reader(f))
    budget=[]
    for row in rows:
        if row[0].isdigit() and len(row)>3:
            budget.append(f'| {row[0]} | {row[1]} | {float(row[3]):,.2f} | {row[2]} |')
    report=json.loads((ROOT/'procurement/export-report.json').read_text())
    tabs='\n'.join(f"| {s['sheet']} | [{s['csv']}]({s['csv']}) | [{s['cells']}]({s['cells']}) |" for s in report['sheets'])
    write('procurement/README.md', (ROOT/'tools/templates/procurement.md').read_text(encoding='utf-8'))
    write('simulations/current-target-r06/README.md',f'''
# Current target-plane magnetic assessment

Current gun R06 retains the magnetic circuit and uses the R05 D50.8×3.175 nonmagnetic target. The pole-to-front spacing is 5.675 mm. [assessment.json](assessment.json) records a sample at 0.25 mm above that face, simulation Z3.425, using the retained refined nonlinear FEM solution.

**Calculated mean parallel field: {assessment['Bparallel_mean_mT']:.3f} mT**, range {assessment['Bparallel_min_mT']:.3f}–{assessment['Bparallel_max_mT']:.3f} mT. The B-normal zero contour crosses all 360 sampled angles, with mean radius {assessment['radius_mean_mm']:.3f} mm. [racetrack.csv](racetrack.csv) contains the samples.

![Current target plane](current-target-map.png)

![Comparison with original target plane](current-racetrack.png)

## Method and applicability

The [resampling script](../../tools/reassess_current_field.py) loads the original `fine_nominal_field.npz` using the original VTK field-probing method. It samples 469 radii per angle, locates the first sign-changing B-normal crossing and linearly interpolates the radius and parallel vector. It first reproduces the original 2 mm-target mean within 0.05 mT, then samples the current plane.

No new mesh or nonlinear solve is performed. This is appropriate within the saved model because the retained magnets/yoke are unchanged and target/copper/fittings are μr=1. Real ferromagnetic fittings or different material properties would require a revised magnetic problem. The field file SHA-256 is recorded in the report. Original mesh/analytical checks are retained but not newly established uncertainty bounds at this plane.

This is magnetic-strength screening. It does not certify ignition, balanced topology, plasma confinement time, deposition, erosion, temperature or a power rating. Compare with a calibrated field map above the actual target before relying on the prediction. See [full simulation evidence](../../docs/simulations.md).
''')
    write('media/README.md', '# Render assets\n\nThe reader guide is now [System architecture and CAD](../docs/design.md). This directory stores the linked images, videos and provenance records.\n')
    print('Documentation built')

if __name__=='__main__':main()
