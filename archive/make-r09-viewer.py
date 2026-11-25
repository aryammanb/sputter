from pathlib import Path
import struct, json, base64, collections
import numpy as np

root=Path(__file__).resolve().parent
target=Path(r'C:\Users\Aryamman\.codex\visualizations\2026\11\14\01a1d8c2-add9-7730-a89b-f446da43fbe6\magnetron-r09-parts.html')
notes={
'01':'Purchased feedthrough envelope; replace with supplier CAD',
'02':'Purchased centering-ring envelope', '03':'O-ring envelope; real seal compression not modeled',
'04':'Permanent vacuum-weld interface requires a drawing', '05':'Unsplit clamp envelope; actual clamp access unverified',
'101':'Revised M3 receiving pilots; chamber flange interface still incomplete',
'102':'Grounded stem; define weld preparation and inspection',
'103':'Bulkhead joint and external fittings still need definition',
'104':'Permanent jacket connection; whole-head service needs a plan',
'105':'Purchased ceramic-break envelope, not a validated hermetic part',
'106':'Stainless transition; mixed-metal joining process unspecified',
'107':'Socket envelope; supplier joining procedure required',
'108':'Live socket envelope; supplier joining procedure required',
'109':'Copper reducer; joining clearance and process unspecified',
'110':'Copper reducer; joining clearance and process unspecified',
'201':'Power socket has clearance but no engineered clamp/contact',
'202':'Ceramic guide axial retention needs definition',
'203':'Revised Ø8.4 bore supports center magnet; preload/tolerances pending',
'204':'Revised M3 receiving pilots; ceramic capture clearance pending',
'205':'Nominal 5 mm engagement; screw envelope is not procurement hardware',
'206':'Load-spreading washer; control ceramic preload',
'207':'Nominal 6 mm engagement into keeper',
'301':'Locator must not crush magnets in the axial tolerance stack',
'302':'Center magnet now has rear ceramic support; field unverified',
'303':'Outer magnet; field and axial capture tolerances unverified',
'304':'Revised M3 pilots; yoke in front of magnets is a field concern',
'305':'Revised brazing-land closure; J1 outer seal and J2/J3 tube joints remain provisional',
'306':'C-channel core; joining and leak inspection remain to be specified',
'308':'One-piece copper seat and C-channel; 5 mm front wall; rear closure separately joined',
'309':'Nominal 3.8 mm engagement in copper; nonstandard screw envelope',
'401':'Ø50.8 × 3.175 mm aluminium target; dry contact to cooled seat',
'402':'Clamp adaptation pending: current lip leaves a 2.825 mm gap above the thinner target',
'403':'Nominal 3.2 mm engagement in copper; nonstandard screw envelope',
'501':'Corrected clearance holes now provide screw-head bearing',
'502':'Revised M3 shield-screw pilots; permanent stem attachment',
'503':'Head now bears on shield; choose actual screw standard',
'601':'Revised cover-screw pilots; hose exits and hardware still missing',
'602':'Rear cover; cable gland and interlock still undefined',
'603':'Terminal envelope has no defined clamp or cable termination',
'604':'Cable insulation envelope; actual cable/strain relief unspecified',
'605':'Cable conductor envelope; termination unspecified',
'606':'Nominal 6 mm engagement into mount plate',
'607':'Nominal 5 mm engagement; finalize actual screw length',
}
offsets={'01':-40,'02':-8,'03':-17,'04':-28,'05':0,'101':-14,'102':11,'103':-45,'104':60,'105':0,'106':-25,'107':-15,'108':15,'109':-30,'110':35,'201':-45,'202':-10,'203':30,'204':65,'205':-75,'206':-50,'207':95,'301':-23,'302':-40,'303':-51,'304':-8,'305':-10,'306':16,'308':36,'309':-35,'401':28,'402':55,'403':85,'501':74,'502':37,'503':40,'601':0,'602':-35,'603':-15,'604':-60,'605':-90,'606':30,'607':-55}
groupdx={'10':0,'11':-100,'20':80,'21':160,'30':240,'31':320,'40':400,'50':480,'60':-240}
parts=[]
with (root/'.r09-mesh.bin').open('rb') as f:
 while first:=f.read(1):
  length=first[0]&127;shift=7
  while first[0]&128:
   first=f.read(1);length|=(first[0]&127)<<shift;shift+=7
  name=f.read(length).decode()
  count=struct.unpack('<i',f.read(4))[0]
  coords=np.frombuffer(f.read(36*count),'<f4').reshape(-1,3)
  q=np.rint(coords*100).astype('<i2')
  assert np.max(np.abs(coords*100))<32767
  vertices,indices=np.unique(q,axis=0,return_inverse=True)
  assert len(vertices)<65536
  group=name.split('/')[0].split()[1]
  leaf=name.split('/')[-1]
  words=leaf.split();code=words[2] if words[1]=='R01' else words[1]
  c=(coords.max(0)+coords.min(0))/2
  radial=c[1:]/max(1,np.linalg.norm(c[1:]))
  repeated=code in {'103','104','105','107','108','109','110','205','206','207','303','309','403','503','606','607'}
  extra=24 if repeated else (42 if code=='05' else 0)
  s=[offsets[code],float(radial[0]*extra),float(radial[1]*extra)]
  if code=='05':s=[0,0,42]
  parts.append(dict(id=str(len(parts)),g=group,code=code,label=leaf.replace('R09 ','',1),note=notes[code],e=[groupdx[group],0,0],s=s,v=base64.b64encode(vertices.astype('<i2').tobytes()).decode(),f=base64.b64encode(indices.astype('<u2').tobytes()).decode()))
assert len(parts)==75
html=(root/'visualizations/r09-parts-template.html').read_text(encoding='utf-8').replace('__MESH_DATA__',json.dumps(parts,separators=(',',':')))
assert len(html.encode())<1_000_000
target.parent.mkdir(parents=True,exist_ok=True)
target.write_text(html,encoding='utf-8')
print(f'Viewer: {target}\nBytes: {len(html.encode())}; instances: {len(parts)}; groups: {collections.Counter(p["g"] for p in parts)}')
