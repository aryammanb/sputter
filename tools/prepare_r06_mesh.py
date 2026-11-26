"""Prepare the exact R06 STEP tessellation used by the retained walkthroughs."""
from pathlib import Path
import json
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'system-architecture-and-cad/models'
OUT=ROOT/'media'
def prepare_mesh():
    cache=OUT/'r06-view-mesh.npz'; meta=json.loads((SRC/'R06 component register.json').read_text())
    if cache.exists(): return meta,np.load(cache)
    import cadquery as cq
    print('Reading exact R06 system STEP',flush=True)
    solids=cq.importers.importStep(str(SRC/'Complete sputter system R06.step')).val().Solids()
    assert sum(q['solid_count'] for q in meta)==len(solids)
    arrays={};k=0;valid=[]
    for i,q in enumerate(meta):
        count=q['solid_count'];group=solids[k:k+count];k+=count
        triangles=[]
        for s in group:
            valid.append(s.isValid());v,f=s.tessellate(.18,.22)
            triangles.append(np.array([x.toTuple() for x in v],dtype=np.float32)[np.array(f)])
        arrays[f'p{i}']=np.concatenate(triangles)
        if i%50==0:print('Meshed',i,'of',len(meta),flush=True)
    np.savez_compressed(cache,**arrays)
    (OUT/'r06-geometry-read.json').write_text(json.dumps({'component_instances':len(meta),'solid_count':len(solids),'invalid_solid_count':valid.count(False),'expected_invalid_reference':'Legacy RV3 supplier reference; see R06 scope notes.'},indent=2))
    return meta,arrays
