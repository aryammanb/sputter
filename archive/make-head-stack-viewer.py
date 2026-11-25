from pathlib import Path
import struct,base64,json
import numpy as np

root=Path(__file__).resolve().parent
groups={'301':1,'302':1,'303':1,'304':2,'305':3,'308':4,'401':5,'309':6}
dx={1:-60,2:-30,3:0,4:30,5:60,6:-90}
parts=[]
with (root/'.r09-mesh.bin').open('rb') as f:
    while first:=f.read(1):
        length=first[0]&127;shift=7
        while first[0]&128:
            first=f.read(1);length|=(first[0]&127)<<shift;shift+=7
        name=f.read(length).decode();n=struct.unpack('<i',f.read(4))[0]
        coords=np.frombuffer(f.read(36*n),'<f4').reshape(-1,3)
        words=name.split('/')[-1].split();code=words[2] if words[1]=='R01' else words[1]
        if code not in groups:continue
        if code=='308':assert 'Integral' in name
        if code=='401':assert abs(float(coords[:,0].max()-coords[:,0].min())-3.175)<.001
        vertices,indices=np.unique(np.rint(coords*100).astype('<i2'),axis=0,return_inverse=True)
        assert len(vertices)<65536
        parts.append({'g':groups[code],'code':code,'dx':dx[groups[code]],'v':base64.b64encode(vertices.tobytes()).decode(),'f':base64.b64encode(indices.astype('<u2').tobytes()).decode()})
assert len(parts)==17,len(parts)
html=(root/'visualizations/head-stack-template.html').read_text(encoding='utf8').replace('__DATA__',json.dumps(parts,separators=(',',':')))
output=Path(r'C:\Users\Aryamman\.codex\visualizations\2026\11\14\01a1d8c2-add9-7730-a89b-f446da43fbe6\head-stack-fit.html')
output.write_text(html,encoding='utf8')
assert output.stat().st_size<1_000_000
print(f'{len(parts)} native instances, {output.stat().st_size} bytes, {output}')
