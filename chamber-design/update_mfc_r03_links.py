from pathlib import Path

base = Path(__file__).resolve().parent.parent
targets = [
    ('00 START HERE - Main design.txt', 'ARGON FLOW CONTROL ENGINEERING', 'MAIN DESIGN:'),
    ('01 MAIN DESIGN - Updated Advanced Tinkering/00 READ FIRST - Current design.txt', 'ARGON MFC SIZING - 24 NOVEMBER 2026', 'PUMPING LAYOUT SELECTED'),
    ('chamber-design/target-clamp-r05/READ FIRST - Clamp R05.txt', 'GAS FLOW ENGINEERING ADDENDUM', 'Target procurement:'),
    ('chamber-design/main-system-r04/README.txt', 'LATER GAS FLOW ENGINEERING ADDENDUM - 24 NOVEMBER 2026', 'Open Complete sputter system'),
]
for rel, start, end in targets:
    path = base / rel
    text = path.read_text(encoding='utf-8')
    a, b = text.index(start), text.index(end, text.index(start))
    link = ('chamber-design/' if not rel.startswith('chamber-design/') and not rel.startswith('01 ') else '../chamber-design/' if rel.startswith('01 ') else '../') + 'Argon MFC selection R03 - 200 sccm.txt'
    replacement = (start + '\nOwner selects200sccm MFC. Exact model/Ar calibration remain to verify.\n'
        'About42mTorr is a plausible ignition trial pressure, not a guaranteed\n'
        'strike threshold or a measured system pressure.50mTorr is not a universal\n'
        'minimum. Check installed pressure, low-flow accuracy and pump gas-load limits.\n'
        'Current selection and engineering assessment: ' + link + '\n'
        'R01/R02 range recommendations are superseded. No CAD/layout change.\n\n')
    path.write_text(text[:a] + replacement + text[b:], encoding='utf-8')
for name in ['Argon MFC sizing and specification R01.txt', 'Argon MFC sizing and specification R02.txt']:
    path = base / 'chamber-design' / name
    text = path.read_text(encoding='utf-8')
    notice = ('CURRENT OWNER SELECTION:200sccm MFC. See Argon MFC selection R03 - 200 sccm.txt.\n'
              'All earlier range recommendations below are superseded by R03.\n\n')
    if notice not in text:
        path.write_text(notice + text, encoding='utf-8')
print('Updated four project guides and marked R01/R02 selections superseded.')
