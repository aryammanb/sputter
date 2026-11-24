import json,math
from pathlib import Path
ROOT=Path(__file__).resolve().parent
parts=json.loads((ROOT/'original-geometry.json').read_text(encoding='utf-8-sig'))
def cylinders(name,radius,pcd=None):
    result=[]
    for f in next(p for p in parts if p['name']==name)['bodies'][0]['faces']:
        v=f['params']
        if f['kind']=='cylinder' and abs(v[4])>.99 and abs(v[6]*1000-radius)<.001:
            x,z=v[0]*1000,v[2]*1000
            if pcd is None or abs(math.hypot(x,z)*2-pcd)<.01:
                if not any(math.hypot(x-a['X'],z-a['Z'])<.001 for a in result):result.append({'X':x,'Z':z})
    return sorted(result,key=lambda p:math.atan2(p['Z'],p['X']))
def same(a,b):
    assert len(a)==len(b)
    assert all(min(math.hypot(p['X']-q['X'],p['Z']-q['Z']) for q in b)<.001 for p in a)
plan={
 'Magnets':cylinders('Backplate',4.5,50),
 'TargetScrews':cylinders('Target Klemme',1.65,80),
 'BackplateScrews':cylinders('Backplate',1.65,63),
 'SpacerScrews':cylinders('Abstandshalter',1.65,88.55),
 'BaseScrews':cylinders('Boden',2.9,79.1255),
 'ClampHalfScrews':cylinders('Flanschklemme',2.7,40),
 'TubeDisplayLength':200.0,
 'KnownUncertainties':['Purchased KF16 tube length is not specified; 200mm visual length used.','Fitting identity/thread and sleeve profile are inferred, not author drawings.','Screw sizes follow source bore geometry; lengths are fitted reconstructions.','Flexible utilities show a compatible illustrative route, not measured hose lengths.']
}
same(plan['Magnets'],cylinders('Kuehlkoerper',4.5,50))
same(plan['TargetScrews'],cylinders('Kuehlkoerper',1.2645,80))
same(plan['BackplateScrews'],cylinders('Kuehlkoerper',1.2645,63))
same(plan['SpacerScrews'],cylinders('Kuehlkoerper',1.2645,88.55))
same(plan['BaseScrews'],cylinders('Isolator',1.65,79.1255))
same(plan['BaseScrews'],cylinders('Abstandshalter',1.2645,79.1255))
both=plan['ClampHalfScrews']+[{'X':-p['X'],'Z':-p['Z']} for p in plan['ClampHalfScrews']]
same(both,cylinders('Boden',2.117,40))
assert len(plan['Magnets'])==12 and all(len(plan[k])==12 for k in ['TargetScrews','BackplateScrews','SpacerScrews','BaseScrews'])
(ROOT/'construction-plan.json').write_text(json.dumps(plan,indent=2),encoding='utf8')
print('PASS: source-defined 12-magnet pattern and five paired screw-pattern interfaces match within1 micron.')
