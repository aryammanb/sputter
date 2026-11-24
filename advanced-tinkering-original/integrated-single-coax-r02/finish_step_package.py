from pathlib import Path
import json,struct,shutil
import cadquery as cq
P=Path(__file__).resolve().parent;D=P/'STEP delivery'
report=json.loads((P/'geometry-verification.json').read_text())
solids=cq.importers.importStep(str(D/'Integrated single coax magnetron R02.step')).val().Solids()
assert len(solids)==129 and all(s.isValid() for s in solids)
reference=cq.importers.importStep(str(P/'Integrated single coax magnetron R02.step')).val().Solids()
assert len(reference)==129
v0=sum(s.Volume() for s in reference);v1=sum(s.Volume() for s in solids)
assert abs(v0-v1)<v0*1e-7
def string(f):
 b=f.read(1)
 if not b:return None
 n=b[0]&127;shift=7
 while b[0]&128:b=f.read(1);n|=(b[0]&127)<<shift;shift+=7
 return f.read(n).decode()
n=tri=0
with (P/'integrated-mesh.bin').open('rb') as f:
 while string(f):
  string(f);count=struct.unpack('<i',f.read(4))[0];data=f.read(count*36);assert len(data)==count*36;n+=1;tri+=count
assert n==129
for q in report['new_parts']:shutil.copy2(q['step'],D/Path(q['step']).name)
report['status']='Mechanical interference check complete: four intentional nominal-thread, spring and formed-saddle contact representations remain, explained in READ ME. RF and cooling performance unqualified.'
(P/'geometry-verification.json').write_text(json.dumps(report,indent=2))
shutil.copy2(P/'geometry-verification.json',D/'geometry-verification.json')
status={'format':'STEP assembly with named/color-coded component instances','components':129,'valid_solids_on_reimport':129,'triangle_count':tri,'reference_compound_volume_mm3':v0,'named_assembly_reimport_volume_mm3':v1,'volume_relative_difference':abs(v0-v1)/v0,'new_interference_check':'Four intentional contacts; classified in geometry-verification.json and READ ME. No other new volume intersections found.','minimum_electrical_clearance':'Not certified. An additional exhaustive exact-distance pass was stopped because it was excessively slow; no minimum-clearance result is claimed.','solidworks_native_conversion':'Not completed; running SolidWorks instances were unresponsive. STEP assembly and 15 individual new/modified STEP parts supplied.','scope':'Mechanical integration study; reference clamp/lug shapes use catalogue dimensions, not certified vendor CAD.'}
(P/'STEP-verification.json').write_text(json.dumps(status,indent=2));shutil.copy2(P/'STEP-verification.json',D/'STEP-verification.json')
print(json.dumps(status,indent=2),flush=True)
