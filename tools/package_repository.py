"""Select meaningful engineering records without moving/deleting local sources.

The explicit file manifest is the upload scope. Historical CAD/code is retained;
older movies, app profiles, dependencies and intermediate images/audio are not.
"""
from pathlib import Path
import hashlib, json, shutil

ROOT=Path(__file__).resolve().parents[1]
ROOTS=['chamber-design','advanced-tinkering-original','90 ARCHIVE - Earlier designs and working files','01 MAIN DESIGN - Updated Advanced Tinkering']
EXT={'.py','.ps1','.csv','.json','.txt','.md','.step','.sldprt','.sldasm','.slddrw','.stl','.dxf','.npz','.msh','.log','.pdf','.svg','.html','.srt','.ffmeta','.ffmetadata','.bin'}
SKIP={'node_modules','.git','__pycache__','browser-profile','browser-check','video','tools'}
ZIP_NAMES={'Coolant fittings R06 - SolidWorks CAD package.zip','CB01 supplier handoff.zip','Stage and shutter - local fabrication.zip'}
IMAGE_NAMES={'Target field map.png','Field section.png','Field versus height.png','Racetrack uniformity.png','Viewport sightline checked.png','Clamp R05 design review.png','Vacuum plumbing - flowcharts only.png'}

def selected(path):
    rel=path.relative_to(ROOT)
    if path.name.startswith('~$'):return False
    if any(x.lower() in SKIP or 'browser-profile' in x.lower() for x in rel.parts[1:-1]):return False
    if path.suffix.lower() in {'.bak','.lnk'}:return False
    if path.name in ZIP_NAMES:return True
    if path.name in IMAGE_NAMES:return True
    # Keep the early educational animation linked from the beginner README.
    if rel.as_posix() == '90 ARCHIVE - Earlier designs and working files/visualizations/sputtering-explainer/magnetron-sputtering-explained.mp4':return True
    # Third-party original video/code download tools and repetitive frame renders stay local.
    if path.suffix.lower() not in EXT:return False
    if path.name.startswith('Encoded') or path.name.endswith('.inspect.ndjson'):return False
    if path.suffix=='.bin' and path.name not in {'mesh.bin','actual-assembly-mesh.bin','fitting-mesh.bin'}:return False
    return True

def media_payload(path):
    rel = path.relative_to(ROOT/'media')
    selected_assets = ROOT/'design/current-render-assets.json'
    if selected_assets.exists() and path.relative_to(ROOT).as_posix() in json.loads(selected_assets.read_text())['images']:
        return True
    if 'render' in rel.parts:
        return False
    # Retain finished exports, scripts' metadata and contact sheets, not frame QA.
    if path.suffix.lower() in {'.jpg', '.png'} and len(rel.parts) > 1:
        return 'contact-sheet' in path.name or path.name == '8x-qa.jpg'
    return path.suffix.lower() not in {'.wav', '.tmp'}


def main():
    support=ROOT/'procurement/support';support.mkdir(parents=True,exist_ok=True)
    source=ROOT/'outputs/01a209eb-c119-74d1-bef5-c610f57d428f'
    for name in ['gun_procurement_data.json','Target thickness interface check.json','EXDC80 80V manual.pdf','Mean Well NPP-450 specification.pdf']:
        if (source/name).exists() and not (support/name).exists():shutil.copy2(source/name,support/name)
    files=[]
    for folder in ROOTS:
        files.extend(p for p in (ROOT/folder).rglob('*') if p.is_file() and selected(p))
    for folder in ['docs','design','procurement','media','simulations','tools','.github','validation']:
        if (ROOT/folder).exists():
            files.extend(p for p in (ROOT/folder).rglob('*') if p.is_file() and not any(x in p.relative_to(ROOT).parts for x in ['.work','__pycache__']) and (folder != 'media' or media_payload(p)) and p.name not in ['file-manifest.json','local-stage-paths.txt','repository-check.json','media-check.json','cad-check.json'])
    for name in ['README.md','CHANGELOG.md','.gitignore','.gitattributes','requirements-engineering.txt','Sputter v2.pptx']:
        files.append(ROOT/name)
    files=sorted(set(files),key=lambda p:p.relative_to(ROOT).as_posix())
    for p in files:
        if p.stat().st_size>95_000_000:raise RuntimeError(f'File exceeds package size policy: {p}')
    records=[{'path':p.relative_to(ROOT).as_posix(),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in files]
    out=ROOT/'validation';out.mkdir(exist_ok=True)
    (out/'file-manifest.json').write_text(json.dumps({'snapshot':'2026-11-24','selection':'Current deliverables and meaningful historical engineering files; excludes browser caches, dependencies, third-party source video, older walkthrough movies and intermediate frames/audio. Original relative paths preserved. Manifest excludes itself and generated check reports to avoid circular hashes.','files':records},indent=2),encoding='utf-8')
    paths=[r['path'] for r in records]+['validation/file-manifest.json','validation/repository-check.json','validation/media-check.json','validation/cad-check.json']
    (out/'local-stage-paths.txt').write_text('\n'.join(paths)+'\n',encoding='utf-8')
    print(json.dumps({'files':len(records),'size_MB':round(sum(x['bytes'] for x in records)/1e6,2),'largest_MB':round(max(x['bytes'] for x in records)/1e6,2)},indent=2))

if __name__=='__main__':main()
