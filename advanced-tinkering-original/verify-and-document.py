import json,csv,math,hashlib,collections,re
from pathlib import Path
ROOT=Path(__file__).resolve().parent
def read(name):return json.loads((ROOT/name).read_text(encoding='utf-8-sig'))
audit=read('native-assembly-audit.json');source=read('original-geometry.json');created=read('generated-parts.json');manifest=read('assembly-manifest.json')
repairs=read('hv-repaired-parts.json') if (ROOT/'hv-repaired-parts.json').exists() else []
created_by_name={p['name']:p for p in created};created_by_name.update({p['name']:p for p in repairs})
replacement={'AT bare HV wire hook representative.SLDPRT':'AT bare HV wire hook fitted.SLDPRT','REF HV copper conductor route.SLDPRT':'REF HV copper conductor fitted route.SLDPRT','REF white HV cable insulation.SLDPRT':'REF white HV cable fitted insulation.SLDPRT'}
for item in manifest:
    basename=Path(item['path']).name
    if basename in replacement:item['path']=str(Path(item['path']).with_name(replacement[basename]))
    basename=Path(item['path']).name
    if item['assembly'].startswith('01') and basename=='AT M4x8 socket-head study.SLDPRT':item['transform'][10]=-.02286
    if basename in ['AT bare HV wire hook fitted.SLDPRT','REF HV copper conductor fitted route.SLDPRT']:item['transform'][10]=-.02268
    matching=[c for c in audit['components'] if c['path']==item['path'] and max(abs(a-b) for a,b in zip(c['transform'],item['transform']))<1e-8]
    if matching:item['as_built_instance_name']=matching[0]['name']
(ROOT/'assembly-manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
assert audit['leaves']==audit['solids']==120
assert all(c['solids']==1 and c['body_check_return_codes']==[1] for c in audit['components'])
preserved=[]
for p in source:
    if p['name']=='Flanschklemme':
        components=[c for c in audit['components'] if Path(c['path']).name=='AT original flange clamp half.SLDPRT'];assert len(components)==2
        expected=max(b['volume_m3'] for b in p['bodies'])*1e9
    else:
        components=[c for c in audit['components'] if Path(c['path']).name==p['name']+'.SLDPRT'];assert len(components)==1
        expected=sum(b['volume_m3'] for b in p['bodies'])*1e9
        identity=[1,0,0,0,1,0,0,0,1,0,0,0,1,0,0,0]
        assert max(abs(a-b) for a,b in zip(components[0]['transform'],identity))<1e-10
    assert all(abs(c['volume_mm3']-expected)<1e-5 for c in components)
    raw=ROOT/'source'/(p['name']+'.step');download=Path('C:/Users/Aryamman/Downloads')/raw.name
    assert hashlib.sha256(raw.read_bytes()).digest()==hashlib.sha256(download.read_bytes()).digest()
    preserved.append({'source':p['name'],'instances':len(components),'source_volume_mm3':expected,'maximum_native_volume_difference_mm3':max(abs(c['volume_mm3']-expected) for c in components)})
counts=collections.Counter(Path(c['path']).name for c in audit['components'])
assert counts['AT outer magnet D8x20 N45.SLDPRT']==12 and counts['AT center magnet D12x10 N45.SLDPRT']==2
seal_volume_comparisons=[]
for size in ['14p5','35','76','62']:
    free=created_by_name[f'AT O-ring ID{size}x2 free']['volume_mm3'];installed=created_by_name[f'AT O-ring ID{size}x2 installed']['volume_mm3']
    relative=abs(free-installed)/free
    assert relative<.001  #0.1% occupied-volume tolerance, not a deformation prediction.
    seal_volume_comparisons.append({'nominal_id':size,'free_volume_mm3':free,'installed_envelope_volume_mm3':installed,'native_volume_difference_percent':relative*100})
expected={
 ('AT M5x20 socket-head study.SLDPRT','Boden.SLDPRT'):6,
 ('AT M4x8 socket-head study.SLDPRT','Backplate.SLDPRT'):1,
 ('AT M4x10 socket-head study.SLDPRT','Backplate.SLDPRT'):1,
 ('AT M4x8 socket-head study.SLDPRT','Boden.SLDPRT'):3,
 ('AT M4x10 socket-head study.SLDPRT','Magnet Joke.SLDPRT'):1,
 ('AT M3x16 socket-head study.SLDPRT','Kuehlkoerper.SLDPRT'):12,
 ('AT M3x35 socket-head study.SLDPRT','Abstandshalter.SLDPRT'):12,
 ('AT M3x35 socket-head study.SLDPRT','Kuehlkoerper.SLDPRT'):12,
 ('AT M3x8 socket-head study.SLDPRT','Kuehlkoerper.SLDPRT'):12,
 ('AT M3x6 socket-head study.SLDPRT','Dunkelraumabschirmung.SLDPRT'):6,
}
actual=collections.Counter(tuple(sorted(Path(p).name for p in h['paths'])) for h in audit['interferences'])
assert actual==collections.Counter({tuple(sorted(k)):v for k,v in expected.items()}),(actual,expected)
materials={'Kuehlkoerper':'C110 copper','Backplate':'C110 copper','Magnet Joke':'A36 mild steel','Isolator':'PTFE'}
descriptions={'Dunkelraumabschirmung':'Upper dark-space/ground shield','Groundshield Rohr':'Outer ground-shield tube','Magnet Joke':'Magnetic return yoke','Target Klemme':'Target retaining clamp','Abstandshalter':'Intermediate spacer/housing','Boden':'Grounded bottom body','Isolator':'Main PTFE insulating ring','Kuehlkoerper':'Copper target-seat cooling body','Backplate':'Copper cooling-channel closure and magnet guide'}
by_file={p['name']+'.SLDPRT':p for p in created_by_name.values()}
with (ROOT/'Assembly BOM.csv').open('w',newline='',encoding='utf-8-sig') as f:
    writer=csv.writer(f);writer.writerow(['Part file','Description','Quantity','Material','Evidence','Notes'])
    for filename,qty in sorted(counts.items()):
        stem=Path(filename).stem
        if stem in descriptions:
            row=[filename,descriptions[stem],qty,materials.get(stem,'316L stainless steel'),'Exact supplied STEP geometry; original coordinates preserved','']
        else:
            p=by_file[filename];row=[filename,stem,qty,p['material'],p['evidence'],p['detail']]
        writer.writerow(row)
with (ROOT/'Evidence and interface map.csv').open('w',newline='',encoding='utf-8-sig') as f:
    w=csv.writer(f);w.writerow(['Feature','Geometry evidence','Video time','Interpretation or limit'])
    for row in [
      ['Layered face-seal assembly','All source parts share global Y-axis coordinates','02:45–03:08','No source part geometry moved or redesigned'],
      ['Target interface','SeatY0; clamp lipY2; recessD51.8','03:08–04:08','D50.8x2 Ti study target; exact target thickness not supplied'],
      ['Atmospheric service region','Main rings atY-12,-41,-46; centralKF16 receiverD17.2','04:15–05:28','Tube length/fitting models not specified'],
      ['PTFE screw sleeves','BaseD5.8 bores/D8 counterbores;12 copies','05:33–06:20;18:34','Compatible sleeve shape inferred; not an author drawing'],
      ['KF16 clamp','One source half; second by180deg aboutY; sixD5.4 holes matchM5-sized pilot locations','06:22–06:49','Captions misread screw size; geometry supportsM5; tube/centering components representative'],
      ['Main isolator face seals','R31…33.85 glands,depth1.45; ID62x2 rings','08:34–09:18','Two ring locations; supplied link incorrectly describes76mm'],
      ['Spacer/copper outer seal','R38…40.85 gland,depth1.45;ID76x2','10:24–10:32','Separates dry interior from vacuum-facing periphery'],
      ['Magnet positions/polarity','12D9 outer bores onPCD50;D13 center; tipsY-2.5','11:00–11:57','OuterD8x20 S towardtarget; center2D12x10 N towardtarget'],
      ['Annular water channel','R11.05…16.05;floorY-2; closureY-9; opposite portsX±13.55','12:09–13:10','Continuous annulus; no C-channel divider modeled or inferred'],
      ['Two water O-rings','ID14.5x2 and35x2;source gland floorsY-10.45','12:40–13:10','Installedellipses illustrate occupied volume; free-state rings also supplied'],
      ['Yoke-retaining screw','Minor-sizedD3.332 bore in yoke and backplate atZ-13.55','10:35–10:57','Source models thread-sized holes in both members; preserve and flag fastening ambiguity'],
      ['Materials','User-supplied C110,316L,A36,PTFE,N45 specifications','17:50–18:48','Materialspecifications recorded; simulation material data not certified'],
    ]:w.writerow(row)
summary={'source_geometry_preserved':preserved,'source_step_hashes_match_downloads':True,'solid_instances':120,'valid_body_check_count':120,'original_part_instances':11,'outer_magnets':12,'center_discs':2,'author_specified_face_seals':5,'unexplained_interference_regions':0,'intentional_thread_envelope_regions':len(audit['interferences']),'water_channel_volume_ml':math.pi*(16.05**2-11.05**2)*7/1000,'notes':['Screw threads are not helically modeled.','Both the yoke and copper plate contain a minor-sized bore at the retaining screw.','Reference fittings, sleeves, target thickness and flexible routing are not exact purchased-component models.']}
summary['seal_envelope_volume_comparisons']=seal_volume_comparisons
(ROOT/'verification-summary.json').write_text(json.dumps(summary,indent=2),encoding='utf8')
report='''ADVANCED TINKERING ORIGINAL MAGNETRON — STUDY RECONSTRUCTION
21 November2026

OPENING THE ASSEMBLY
Open “Advanced Tinkering magnetron - full reconstruction.SLDASM”. The delivery
folder was created with SolidWorks Pack and Go so native references travel
together. The STEP assembly is an exchange copy; use the SLDASM for the tree.
The seven subassemblies separate cooling/magnets, spacer, base/insulation,
target, ground shield, KF16 mounting, and reference utility routing.

SCOPE
This reconstructs the supplied original design and the bench unit in:
https://www.youtube.com/watch?v=MslftqA7LYw
It does not include the separate custom RevA/RevB gun designed in this chat,
and does not substitute our previously selected RF feedthrough into his gun.

WHAT IS SOURCE-BACKED
The nine single-part STEP files retain their exact imported solid geometry
and original global coordinates. Flanschklemme.step supplies one complete
clamp half plus a1.45e-9 mm3 fragment. The complete half is copied unchanged
and used twice, with the second rotated180degrees about the shared Y axis.
The original ten STEP files and their SHA256 hashes are preserved separately.

There are12 outer D8x20 N45 rods on a50mm pitch circle and two stacked
D12x10 N45 center discs. The yoke rear support plane isY-22.5; magnet tips
areY-2.5, with0.5mm to their blind-well ends. Center target-facing pole isN;
outer poles areS as stated/shown around11:05 in the source video.

THE ACTUAL WATER AND VACUUM SEALS
The source water passage is a full annulus R11.05…16.05, Y-9…-2, about2.98mL
before including port passages. Ports enter atX±13.55. Flow can take both
semicircular paths. There is no C-channel divider in the original geometry.
ID14.5x2 and35x2 FKM rings isolate water from the central and outer magnet
regions. A76x2 ring seals the spacer/copper interface. Two62x2 rings seal the
PTFE ring to the spacer and bottom body. These are five author-specified
face seals. The62mm supplier link repeats the76mm item and remains unresolved.

The face glands are1.45mm deep, giving27.5% nominal axial squeeze on2mm
cross-section rings. Installed models use volume-preserving elliptical
envelopes that fit the measured glands. They do not predict real elastomer
deformation or validate seal performance. The nominal circular free-state
ring parts are included separately for dimension reference.

The main seals close the atmospheric interior against chamber vacuum. The
ground-shield tube itself is not that pressure boundary. Hoses and the wire
pass down the central flanged tube on the atmospheric side. The separate
chamber-side adjustable/compression feedthrough mentioned in the video is
not supplied as STEP or identified by a part number and is not invented here.

WHAT IS RECONSTRUCTED OR REPRESENTATIVE
* Screw nominal diameters follow source receiving/clearance holes. Their
  standard lengths are chosen to fit the measured stack, not claimed as an
  original author BOM.65 screws are modeled with simplified heads/sockets
  and nominal major-diameter shafts; thread helices are not modeled.
*12 PTFE shoulder sleeves fit the measured base bores and counterbores.
  OD5.6/ID3.3 shank22mm, OD7.8 flange1.5mm is a compatible inferred shape.
  Exact author sleeve drawings were not supplied.
* The titanium study target isD50.8x2. The2mm thickness follows the clamp
  contact plane; it is not a supplied target measurement.
* KF16 tube length is200mm for display. Flange/centering/seal geometry follows
  a compatible standard-form reference with a4mm mating gap, not the exact
  purchased manufacturer's model. The source clamp and base are unchanged.
* The black/blue coolant fittings have no confirmed model number or thread.
  They are clearance-fitted reference bodies. Do not order or machine from
  those interface envelopes.
* Blue hoses and white cable show a compatible illustrative route through
  the central tube. Their lengths, cross sections and the thin bare-wire
  hook/lead are visual representations, not electrical/hydraulic selections.
The user confirmed no extra tube/fitting identification was available.

ASSEMBLY METHOD
The originals are already exported in shared assembly coordinates. Fixed
rigid placements preserve these coordinates; this is not a motion model
with editable mechanical mates. Added hardware follows measured bore axes.
Native generated sketches/sweeps represent missing components. Imported
source geometry remains an imported solid rather than rebuilt machining
features. Source cosmetic threads and actual elastomer deformation are not
reverse-engineered.

VERIFICATION
All120 component solid instances return1 (valid) from IBody2.Check. Each
component resolves to one solid. All original-part volumes are preserved;
source file hashes match the user-supplied files. Five paired hole patterns
were checked independently within0.001mm. Free and installed face-ring
envelopes match nominal free torus volumes within0.06% in native CAD (0.1%
acceptance tolerance for this illustration).

The full interference test reports66 regions, all between nominal screw
shafts and source thread-minor-sized bores. No unexplained solid collision
remains. One M4 screw enters a minor-sized yoke bore as well as its copper
receiving hole. This is a source fastening ambiguity, preserved and flagged,
not evidence that the real yoke should be tapped or that the thread phases
would clamp correctly. A raw zero-interference claim would be misleading.

This verifies a geometric study reconstruction. It does not establish
pressure rating, vacuum leak performance, insulation adequacy, magnetic
field strength, coolant suitability or build readiness. The video describes
arcing/corrosion concerns; faithfully reproducing its geometry does not
resolve those source-design issues.

REFERENCES
Source video and time-indexed evidence: “Evidence and interface map.csv”.
SolidWorks body-check convention:
https://help.solidworks.com/2023/english/api/sldworksapi/Check_Bodies_for_Faults_Example_VB.htm
Pfeiffer ISO-KF dimensional reference, source manufacturer catalogue:
https://www.idealvac.com/files/manuals/Pfeiffer_Vacuum_Technology_Chambers_and_Components.pdf
KF16 metric O-ring variant reference:
https://de.lesker.com/newweb/flanges/hardware_kf_centeringrings.cfm?pgid=outerring-oring

FILES
Assembly BOM.csv — quantities, material/evidence classifications, limitations.
verification-summary.json — independent source-preservation and fit checks.
native-assembly-audit.json — per-component body checks and raw interference data.
assembly-manifest.json — construction placements and evidence classifications.
The downloaded video is retained only in the local analysis workspace and
is not redistributed in the CAD delivery archive.
'''
(ROOT/'READ ME - reconstruction and limits.txt').write_text(report,encoding='utf8')
print('PASS:120 valid instances; source geometry/hash checks passed;66 intentional thread regions;0 unexplained regions. BOM and evidence report written.')
