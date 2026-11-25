from pathlib import Path

base = Path(__file__).resolve().parents[2]
targets = [
    ('system-architecture-and-cad/sources/target-clamp-r05/READ FIRST - Clamp R05.txt', 'GAS FLOW ENGINEERING ADDENDUM', 'Target procurement:'),
    ('system-architecture-and-cad/sources/system-layout-r04/README.txt', 'LATER GAS FLOW ENGINEERING ADDENDUM - 24 NOVEMBER 2026', 'Open Complete sputter system'),
]
for rel, start, end in targets:
    path = base / rel
    text = path.read_text(encoding='utf-8')
    a, b = text.index(start), text.index(end, text.index(start))
    replacement = (start + '\nOwner selects200sccm MFC. Exact model/Ar calibration remain to verify.\n'
        'About42mTorr is a plausible ignition trial pressure, not a guaranteed\n'
        'strike threshold or a measured system pressure.50mTorr is not a universal\n'
        'minimum. Check installed pressure, low-flow accuracy and pump gas-load limits.\n'
        'Current selection and engineering assessment: ' + link + '\n'
        'R01/R02 range recommendations are superseded. No CAD/layout change.\n\n')
    path.write_text(text[:a] + replacement + text[b:], encoding='utf-8')
for name in ['Argon MFC sizing and specification R01.txt', 'Argon MFC sizing and specification R02.txt']:
    path = base / 'system-architecture-and-cad' / name
    text = path.read_text(encoding='utf-8')
    notice = ('CURRENT OWNER SELECTION:200sccm MFC. See Argon MFC selection R03 - 200 sccm.txt.\n'
              'All earlier range recommendations below are superseded by R03.\n\n')
    if notice not in text:
        path.write_text(notice + text, encoding='utf-8')
print('Updated two project guides and marked R01/R02 selections superseded.')
