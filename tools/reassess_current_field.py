"""Sample the verified saved magnetostatic field at the R05/R06 target plane.

The target and changed copper/fittings are modeled as mu_r=1. Changing their
boundary has no material effect in this model; magnet/yoke geometry is retained.
This is a resampling assessment, not a newly solved or remeshed FEM model.
"""
from pathlib import Path
import importlib.util, json, hashlib, csv
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'simulations/magnetic-model'
OUT = ROOT / 'simulations/current-target-r06'

def ring(field, z):
    theta = np.linspace(0, 2*np.pi, 360, endpoint=False)
    radii = np.linspace(2, 25.4, 469)
    pts = np.stack(np.broadcast_arrays(radii[None,:]*np.cos(theta[:,None]), radii[None,:]*np.sin(theta[:,None]), z), axis=-1)
    b = field(pts.reshape(-1,3)).reshape(360,469,3)
    roots, fields = [], []
    for i in range(360):
        crossings = np.flatnonzero(b[i,:-1,2]*b[i,1:,2] < 0)
        if not len(crossings): raise RuntimeError(f'No Bz crossing at angle {i}')
        j = crossings[0]
        t = -b[i,j,2] / (b[i,j+1,2]-b[i,j,2])
        roots.append(radii[j]+t*(radii[j+1]-radii[j]))
        fields.append(np.linalg.norm((1-t)*b[i,j,:2]+t*b[i,j+1,:2]))
    roots, fields = np.asarray(roots), np.asarray(fields)*1000
    return roots, fields

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    spec = importlib.util.spec_from_file_location('original_field', SRC / 'analyze_field.py')
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    field = mod.Field('fine_nominal')
    oldr, oldb = ring(field, 2.25)
    roots, b = ring(field, 3.425)
    original = json.loads((SRC / 'fine_nominal_metrics.json').read_text())['racetrack_Bz_zero']
    assert abs(oldb.mean() - original['Bparallel_mean_mT']) < .05
    current = {'target_thickness_mm': 3.175, 'pole_to_front_mm': 5.675, 'sampling_height_above_target_mm': .25, 'simulation_z_mm': 3.425, 'angles_with_crossing': len(roots), 'radius_mean_mm': float(roots.mean()), 'radius_min_mm': float(roots.min()), 'radius_max_mm': float(roots.max()), 'Bparallel_mean_mT': float(b.mean()), 'Bparallel_min_mT': float(b.min()), 'Bparallel_max_mT': float(b.max()), 'target_edge_margin_min_mm': float(25.4-roots.max()), 'peak_to_peak_over_mean_percent': float(np.ptp(b)/b.mean()*100)}
    report = {'date': '2026-11-24', 'method': 'Resample saved fine_nominal FEM field at new nonmagnetic target plane. No new solve/remesh.', 'field_sha256': hashlib.sha256((SRC / 'fine_nominal_field.npz').read_bytes()).hexdigest(), 'applicability': 'R05/R06 retains magnets and yoke; target/copper/fittings treated as mu_r=1. Ferromagnetic purchased parts, actual material properties, plasma and thermal effects omitted.', 'baseline_reproduction': {'resampled_mean_mT': float(oldb.mean()), 'saved_mean_mT': original['Bparallel_mean_mT'], 'absolute_difference_mT': float(abs(oldb.mean()-original['Bparallel_mean_mT']))}, 'current': current, 'limits': 'Prior mesh/domain/analytical checks were for the baseline sampling region. They do not establish a new uncertainty bound at this plane or validate real hardware. No discharge, deposition, balance, thermal, seal or power rating is certified.'}
    (OUT / 'assessment.json').write_text(json.dumps(report, indent=2))
    with (OUT / 'racetrack.csv').open('w', newline='') as f:
        w=csv.writer(f);w.writerow(['angle_deg','radius_mm','parallel_field_mT']);w.writerows(zip(range(360), roots, b))
    plt.style.use('seaborn-v0_8-whitegrid')
    fig, ax = plt.subplots(figsize=(10,4.8), layout='constrained')
    ax.plot(range(360), oldb, color='#8896a5', label='Historical 2 mm target, +0.25 mm')
    ax.plot(range(360), b, color='#007f86', label='Current 3.175 mm target, +0.25 mm')
    ax.set(xlabel='Angle around B-normal zero contour (degrees)',ylabel='Parallel magnetic field (mT)', title='R06 target-plane assessment from saved FEM solution')
    ax.legend();fig.savefig(OUT / 'current-racetrack.png', dpi=180);plt.close(fig)
    xy=np.linspace(-27,27,181);x,y=np.meshgrid(xy,xy);p=np.c_[x.ravel(),y.ravel(),np.full(x.size,3.425)]
    values=field(p).reshape(181,181,3)
    fig,ax=plt.subplots(figsize=(6.8,6.2),layout='constrained')
    m=ax.pcolormesh(x,y,np.linalg.norm(values[:,:,:2],axis=2)*1000,cmap='viridis',shading='auto')
    ax.contour(x,y,values[:,:,2],levels=[0],colors='white',linewidths=1)
    ax.add_patch(plt.Circle((0,0),25.4,fill=False,color='red',linestyle='--',label='Target edge'))
    fig.colorbar(m,ax=ax,label='Parallel field (mT)');ax.set(aspect='equal',xlabel='x (mm)',ylabel='y (mm)',title='Current target +0.25 mm | saved FEM field')
    ax.legend(loc='lower left');fig.savefig(OUT/'current-target-map.png',dpi=180);plt.close(fig)
    print(json.dumps(report,indent=2))

if __name__ == '__main__': main()
