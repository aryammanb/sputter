"""Validate package files and authored local links using the standard library.

CI reads the frozen manifest; it does not silently regenerate hashes. Physical
engineering qualification is separate. Optional media/CAD checks are separate.
"""
from pathlib import Path
from urllib.parse import unquote
import hashlib,json,re,sys

ROOT=Path(__file__).resolve().parents[1]

def main():
    errors=[];manifest=json.loads((ROOT/'validation/file-manifest.json').read_text())
    paths={x['path'] for x in manifest['files']}
    for item in manifest['files']:
        p=ROOT/item['path']
        if not p.is_file():errors.append('Missing '+item['path']);continue
        if p.stat().st_size!=item['bytes']:errors.append('Changed length '+item['path'])
        if hashlib.sha256(p.read_bytes()).hexdigest()!=item['sha256']:errors.append('Hash mismatch '+item['path'])
    linked=0
    authored=[ROOT/'README.md',ROOT/'CHANGELOG.md']
    for folder in ['docs','procurement','media','simulations','validation']:
        authored.extend((ROOT/folder).glob('*.md'))
    authored.extend((ROOT/'simulations/current-target-r06').glob('*.md'))
    authored.extend((ROOT/'system-architecture-and-cad').rglob('README.md'))
    authored.append(ROOT/'archive/chamber-design/README.md')
    for p in authored:
        for raw in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)',p.read_text(encoding='utf-8')):
            if raw.startswith(('http:','https:','mailto:','#')):continue
            raw=raw.strip('<>');target=(p.parent/unquote(raw.split('#')[0])).resolve();linked+=1
            if not target.exists():errors.append('Broken link '+str(p.relative_to(ROOT))+' -> '+raw)
            elif target.is_file() and target.relative_to(ROOT).as_posix() not in paths and target.name not in ['file-manifest.json','repository-check.json','media-check.json','cad-check.json']:errors.append('Link target excluded from package '+raw)
    current=json.loads((ROOT/'design/current.json').read_text())
    for value in list(current['current_files'].values())+current['current_media']:
        if not (ROOT/value).is_file():errors.append('Missing current selection '+value)
    report=json.loads((ROOT/'procurement/export-report.json').read_text())
    if hashlib.sha256((ROOT/'procurement/Sputter system procurement.xlsx').read_bytes()).hexdigest()!=report['sha256']:errors.append('Workbook hash mismatch')
    if any(s['cached_errors'] for s in report['sheets']):errors.append('Saved workbook error values')
    if len(report['sheets'])!=13:errors.append('Unexpected workbook tab count')
    for r in manifest['files']:
        if any(x in Path(r['path']).parts for x in ['node_modules','browser-profile','browser-check','.env']):errors.append('Unexpected local/private cache '+r['path'])
    provenance=json.loads((ROOT/'media/provenance.json').read_text())
    if hashlib.sha256((ROOT/provenance['source_step']).read_bytes()).hexdigest()!=provenance['source_sha256']:errors.append('Media source STEP mismatch')
    field=json.loads((ROOT/'simulations/current-target-r06/assessment.json').read_text())
    fieldfile=ROOT/'advanced-tinkering-original/balanced-twelve-stack-study/magnetic-simulation/fine_nominal_field.npz'
    if hashlib.sha256(fieldfile.read_bytes()).hexdigest()!=field['field_sha256']:errors.append('Current field source hash mismatch')
    for reportfile in ['media-check.json','cad-check.json']:
        p=ROOT/'validation'/reportfile
        if not p.exists():errors.append('Missing check report '+reportfile);continue
        check=json.loads(p.read_text())
        if not check['passed']:errors.append('Failed check report '+reportfile)
        for row in check.get('videos',check.get('checks',[])):
            if hashlib.sha256((ROOT/row['file']).read_bytes()).hexdigest()!=row['sha256']:errors.append('Stale verification report for '+row['file'])
    result={'snapshot':'2026-11-24','passed':not errors,'file_count':len(manifest['files']),'local_links_checked':linked,'workbook_tabs':len(report['sheets']),'workbook_cached_error_count':sum(len(x['cached_errors']) for x in report['sheets']),'scope':'Package hashes, selected artifact presence, authored relative links, source geometry/field hashes and saved workbook export. No new physical tests or Excel recalculation.','errors':errors}
    (ROOT/'validation/repository-check.json').write_text(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2));return 0 if not errors else 1

if __name__=='__main__':sys.exit(main())
