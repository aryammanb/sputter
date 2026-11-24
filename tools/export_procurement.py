"""Losslessly preserve the workbook; export OOXML cells for GitHub reading.

Uses Python's standard library. Cached formula values are explicitly distinguished
from formula text. This program does not recalculate or edit the workbook.
"""
from pathlib import Path
import csv, hashlib, json, re, shutil, zipfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'procurement'
NS = {'m': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
RID = '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id'

def export(source):
    source = source.resolve()
    OUT.mkdir(exist_ok=True)
    dest = OUT / 'Sputter system procurement.xlsx'
    if source.resolve() != dest.resolve():
        shutil.copy2(source, dest)
    records = []
    with zipfile.ZipFile(dest) as z:
        strings = []
        if 'xl/sharedStrings.xml' in z.namelist():
            strings = [''.join(x.itertext()) for x in ET.fromstring(z.read('xl/sharedStrings.xml'))]
        rels = {x.attrib['Id']: x.attrib['Target'] for x in ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))}
        for sheet in ET.fromstring(z.read('xl/workbook.xml')).find('m:sheets', NS):
            name = sheet.attrib['name']
            target = rels[sheet.attrib[RID]]
            target = target.lstrip('/') if target.startswith('/') else 'xl/' + target
            xml = ET.fromstring(z.read(target))
            cells, formulas, errors = {}, {}, []
            for cell in xml.findall('.//m:sheetData/m:row/m:c', NS):
                ref = cell.attrib['r']; typ = cell.attrib.get('t', '')
                val = cell.find('m:v', NS); raw = val.text if val is not None else ''
                if typ == 's': raw = strings[int(raw)]
                elif typ == 'inlineStr': raw = ''.join(cell.find('m:is', NS).itertext())
                formula = cell.find('m:f', NS)
                if formula is not None: formulas[ref] = {'formula': formula.text, 'cached_value': raw}
                if typ == 'e': errors.append({'cell': ref, 'error': raw})
                if raw: cells[ref] = raw
            maxrow = max([int(re.search(r'\d+', x)[0]) for x in cells] or [0])
            def colno(ref):
                n = 0
                for c in re.match('[A-Z]+', ref)[0]: n = n * 26 + ord(c) - 64
                return n
            maxcol = max([colno(x) for x in cells] or [0])
            rows = [[''] * maxcol for _ in range(maxrow)]
            for ref, value in cells.items(): rows[int(re.search(r'\d+', ref)[0]) - 1][colno(ref) - 1] = value
            slug = re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')
            with (OUT / f'{slug}.csv').open('w', newline='', encoding='utf-8') as f: csv.writer(f).writerows(rows)
            (OUT / f'{slug}.cells.json').write_text(json.dumps({'sheet': name, 'values': cells, 'formulas': formulas, 'cached_errors': errors}, indent=2, ensure_ascii=False), encoding='utf-8')
            records.append({'sheet': name, 'rows': maxrow, 'columns': maxcol, 'formula_count': len(formulas), 'cached_errors': errors, 'csv': f'{slug}.csv', 'cells': f'{slug}.cells.json'})
    result = {'source': source.relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(dest.read_bytes()).hexdigest(), 'method': 'Original workbook copied unchanged; CSVs use saved values. Formula text and cached values exported separately. No new recalculation claimed.', 'sheets': records}
    (OUT / 'export-report.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser(); p.add_argument('--source', type=Path, default=OUT / 'Sputter system procurement.xlsx')
    export(p.parse_args().source)
