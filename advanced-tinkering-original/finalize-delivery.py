import json,hashlib,shutil,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent;OUT=ROOT/'SolidWorks delivery'
status=json.loads((ROOT/'package-verification.json').read_text(encoding='utf-8-sig'))
assert status['leaf_instances']==120 and status['missing_or_external_native_references']==0
hashes=json.loads((ROOT/'source-sha256.json').read_text())
for name,digest in hashes.items():
    dest=OUT/name
    if not dest.exists():shutil.copy2(ROOT/'source'/name,dest)
    assert hashlib.sha256(dest.read_bytes()).hexdigest()==digest,name
files=['Assembly BOM.csv','Evidence and interface map.csv','READ ME - reconstruction and limits.txt','source-sha256.json','verification-summary.json','package-verification.json','pack-and-go-status.json','native-assembly-audit.json','assembly-manifest.json','generated-parts.json','hv-repaired-parts.json','Original magnetron - assembled.png','Original magnetron - cutaway.png','Original magnetron - layers.png']
for name in files:shutil.copy2(ROOT/name,OUT/name)
free=OUT/'Free-state O-rings';free.mkdir(exist_ok=True)
for p in (ROOT/'reconstructed parts').glob('* O-ring * free.SLDPRT'):shutil.copy2(p,free/p.name)
(OUT/'START HERE.txt').write_text('ADVANCED TINKERING ORIGINAL MAGNETRON\n\nOpen: Advanced Tinkering magnetron - full reconstruction.SLDASM\nKeep this entire folder together. It was packaged with SolidWorks Pack and Go.\n\nRead: READ ME - reconstruction and limits.txt\nSee: Original magnetron - cutaway.png and Original magnetron - layers.png\n\n120 solid component instances;120 valid-body checks; no missing native references.\nOriginal supplied geometry preserved. Missing hardware is reconstructed or marked REF.\nTube length, exact fittings, sleeve profile and flexible utility dimensions remain inferred.\nThe66 raw interference regions are intentional nominal screw/thread-bore overlaps;\nsee the report for the source yoke fastening ambiguity.\n\nThis is a study reconstruction of the original design, not our separate RevB gun.\n',encoding='utf8')
archive=ROOT/'Advanced Tinkering original magnetron - SolidWorks package.zip'
with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for path in sorted(OUT.rglob('*')):
        if path.is_file():z.write(path,Path('Advanced Tinkering original magnetron')/path.relative_to(OUT))
with zipfile.ZipFile(archive) as z:assert z.testzip() is None;entries=len(z.infolist())
proof={'archive':str(archive),'bytes':archive.stat().st_size,'files':entries,'sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'original_step_hashes_in_package_match':True,'native_part_definitions':len(list(OUT.glob('*.SLDPRT'))),'native_assembly_documents':len(list(OUT.glob('*.SLDASM'))),'free_state_ring_definitions':len(list(free.glob('*.SLDPRT')))}
(ROOT/'delivery-verification.json').write_text(json.dumps(proof,indent=2),encoding='utf8')
print(json.dumps(proof,indent=2))
