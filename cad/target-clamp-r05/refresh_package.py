from pathlib import Path
import zipfile
P=Path('cad/target-clamp-r05');files=[x for x in P.iterdir() if x.suffix.lower() in ['.step','.json','.csv','.txt','.png','.xlsx'] and x.name!='parts.json'];pack=P/'Clamp R05 - revised CAD package.zip'
with zipfile.ZipFile(pack,'w',zipfile.ZIP_DEFLATED) as z:
 for f in files:z.write(f,f.name)
with zipfile.ZipFile(pack) as z:assert z.testzip() is None;print('Final CAD package:',len(z.namelist()),'files,',pack.stat().st_size,'bytes, CRC passed')
