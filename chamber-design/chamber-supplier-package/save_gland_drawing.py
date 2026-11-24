from pathlib import Path
import urllib.request,xml.etree.ElementTree as E
P=Path('chamber-design/gun-mount-procurement-check');P.mkdir(exist_ok=True)
u='https://www.lesker.com/newweb/images/product_drawings/Dwg-HD-QF-COUPLING-ADAPTER.svg'
try:
 data=urllib.request.urlopen(u,timeout=15).read();(P/'Lesker coupling dimensional reference.svg').write_bytes(data);s=E.fromstring(data);print('SVG labels:',[(x.tag,''.join(x.itertext()).strip()) for x in s.iter() if x.tag.endswith('text')])
except Exception as e:print('drawing',type(e).__name__,str(e))
