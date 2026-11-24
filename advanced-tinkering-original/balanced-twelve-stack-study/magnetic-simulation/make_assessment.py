from pathlib import Path
import json,math,csv,importlib.metadata
import numpy as np
P=Path(__file__).resolve().parent
def read(name):return json.loads((P/name).read_text())
fine=read('fine_nominal_metrics.json');coarse=read('coarse_nominal_metrics.json');wide=read('wide_nominal_metrics.json');hard=read('coarse_steel-hard_metrics.json');soft=read('coarse_steel-soft_metrics.json');analytic=read('fine_analytic_analytic_validation.json');solve=read('fine_nominal_solve.json');mesh=read('fine_mesh.json');thickness=read('target_thickness_sensitivity.json')
track=fine['racetrack_Bz_zero'];mean=track['Bparallel_mean_mT'];cmean=coarse['racetrack_Bz_zero']['Bparallel_mean_mT']
checks={'nonlinear_residual':solve['history'][-1]['nonlinear_residual_after'],'mesh_mean_change_percent':100*abs(mean-cmean)/mean,'mesh_minimum_change_percent':100*abs(track['Bparallel_min_mT']-coarse['racetrack_Bz_zero']['Bparallel_min_mT'])/track['Bparallel_min_mT'],'domain_and_remesh_mean_change_percent':100*abs(wide['racetrack_Bz_zero']['Bparallel_mean_mT']-cmean)/cmean,'analytical_free_space_vector_relative_L2_error_percent':100*analytic['vector_relative_L2_error'],'analytical_free_space_pointwise_p95_error_percent':100*analytic['pointwise_relative_error_p95'],'steel_H_half_mean_change_percent':100*(soft['racetrack_Bz_zero']['Bparallel_mean_mT']/cmean-1),'steel_H_double_mean_change_percent':100*(hard['racetrack_Bz_zero']['Bparallel_mean_mT']/cmean-1),'target_ring_continuity_angles':track['angles_with_crossing'],'weakest_ring_Bparallel_mT':track['Bparallel_min_mT']}
assert checks['nonlinear_residual']<2e-7
assert checks['mesh_mean_change_percent']<2
assert checks['domain_and_remesh_mean_change_percent']<2
assert analytic['vector_relative_L2_error']<.05
assert track['angles_with_crossing']==360
checks['numerical_checks_passed']=True
summary={'assessment':'Positive magnetic-strength screening; not a plasma-operation or balanced-topology certification.','nominal_geometry':'12 outer D6x20 stacks on PCD58; centerD20x20; exact proposed steel yoke; targetD50.8x2; pole tips2.5mm behind seat,4.5mm behind front face.','field_results':fine,'numerical_verification':checks,'mesh':mesh,'target_thickness_sensitivity':thickness,'assumptions':solve['assumptions'],'limitations':['Actual yoke material and N42 magnet curves not supplied.','No plasma sheath, RF voltage waveform, collision kinetics or space-charge solve.','No density, confinement time, ignition pressure, erosion rate or coating-uniformity prediction.','Balanced topology not established by equal magnet areas or by a local closed racetrack.','No experimental Hall-probe validation.']}
(P/'Assessment results.json').write_text(json.dumps(summary,indent=2))
text=f'''MAGNETIC CIRCUIT SIMULATION - CONFINEMENT ASSESSMENT
23 November 2026

RESULT
The proposed twelve-stack circuit has ample predicted field strength to
magnetize electrons near the target. At0.25mm above the assumed2mm target,
the candidate racetrack has a mean parallel field of{mean:.1f}mT and a weakest
point of{track['Bparallel_min_mT']:.1f}mT. This is positive magnetic-strength
screening, not proof that a specified discharge will ignite or operate well.
The copper/target spacing does not appear to make the field too weak.

WHAT WAS ACTUALLY SIMULATED
Three-dimensional nonlinear magnetostatics using tetrahedral finite elements.
The actual proposed yoke STEP, including fitting and screw-clearance holes,
was imported. The26 axially magnetized discs are represented by13 contiguous
cylinders: two touching discs with the same polarity are equivalent here to
one20mm-long cylinder; small coating/interface gaps are neglected.

Outer magnets:12 D6x20 stacks on PCD58, S toward target.
Center: D20x20, N toward target.
Nominal N42 remanence1.30T, recoil relative permeability1.05, temperature20C.
Target:D50.8x2, nonmagnetic. Pole tips are4.5mm behind the front face.
Copper, water, air and insulation are approximated with relative permeability1.
Their static magnetic effect is therefore their spacing, not shielding.
Surrounding ferromagnetic chamber components, if any, are not included.

Yoke: a published reference AISI1010 nonlinear B-H curve, reproduced by
QuickField from CERN DIRAC note2012-02. The actual steel grade/heat treatment
has not been specified. H-values were scaled by0.5 and2 as sensitivity cases.
These are assumptions about steel, not measurements of the proposed part.

MODEL AND SOLVER
Magnetic scalar potential, no free currents:
  B = -mu_r grad(u) + Br, where u = mu0 * magnetic scalar potential.
  Integral(mu_r grad(u).grad(v)) = Integral(Br.grad(v)).
Coordinates use millimetres and u in tesla-millimetres.
Simulation(x,y,z) = CAD(x,-z,y); target front is z=2mm.
Piecewise-linear tetrahedra, Newton iteration with line search and the
differential B-H Jacobian; algebraic-multigrid-preconditioned conjugate gradient.
Scalar potential is zero on the enclosing air-box boundary.
Air-side element fields are volume-projected to nodes for field sampling.
The trajectory lines integrate the resulting static B direction. Animated
markers are direction indicators, not simulated plasma electrons.

NUMERICAL VERIFICATION
Nominal refined mesh:{mesh['vertices']:,} vertices,{mesh['tetrahedra']:,} tetrahedra.
Air box extends +/-80mm in each direction; checked with +/-120mm at coarse size.
Near-circuit nominal mesh size1.2mm; coarse size1.8mm.
Final nonlinear residual:{checks['nonlinear_residual']:.2e} relative to source.
Refining the mesh changed ring mean field by{checks['mesh_mean_change_percent']:.2f}%.
Larger-domain/remeshing check changed coarse ring mean by{checks['domain_and_remesh_mean_change_percent']:.2f}%.
Independent analytical comparison: same magnets in free space, unit
permeability everywhere, compared with Magpylib analytical cylinder fields at
9,600 points. Refined vector L2 error:{checks['analytical_free_space_vector_relative_L2_error_percent']:.2f}%.
Pointwise relative error95th percentile:{checks['analytical_free_space_pointwise_p95_error_percent']:.2f}%.
This is solver verification, not experimental validation of the steel circuit.
These differences are not certified uncertainty bars for the real hardware.

FIELD RESULTS AT0.25mm ABOVE TARGET
Continuous Bnormal=0 contour found at all360 sampled angles.
Mean contour radius:{track['radius_mean_mm']:.2f}mm.
Radius range:{track['radius_min_mm']:.2f}..{track['radius_max_mm']:.2f}mm.
Minimum distance to target edge:{track['target_edge_margin_min_mm']:.2f}mm.
Parallel field along contour:{track['Bparallel_min_mT']:.1f}..{track['Bparallel_max_mT']:.1f}mT.
Peak-to-peak field variation / mean:{track['peak_to_peak_over_mean_percent']:.1f}%.
This is a candidate magnetic racetrack, not a simulated erosion profile.
Field nonuniformity is not equivalent to deposition-thickness nonuniformity.

YOKE
Volume-weighted mean B:{fine['yoke']['B_volume_weighted_mean_T']:.2f}T.
Element B99th percentile:{fine['yoke']['B_p99_T']:.2f}T.
Maximum element B:{fine['yoke']['B_max_T']:.2f}T, sensitive to sharp-edge meshing.
No extensive high-field saturation region was predicted with the assumed curve.
Halving/doubling the reference H values changed the coarse ring mean by
{checks['steel_H_half_mean_change_percent']:.3f}% / {checks['steel_H_double_mean_change_percent']:.3f}%.
This sensitivity does not cover every possible steel, especially nonmagnetic
stainless steel, hysteresis, or a wrong/missing yoke.

ELECTRON MAGNETIZATION
For perpendicular electron energy Eperp:
  electron gyroradius = sqrt(2*me*Eperp)/(e*B).
Using the weakest ring field gives conservative local values:
10eV:{fine['electron_gyroradius_mm_at_weakest_track_field']['10']:.3f}mm.
100eV:{fine['electron_gyroradius_mm_at_weakest_track_field']['100']:.3f}mm.
The local gyro-orbits are small compared with the millimetre-scale field
structure. This supports local magnetization. It does not prevent parallel
losses or establish confinement time. No plasma temperature is inferred from
these illustrative electron energies.

IS THAT GOOD ENOUGH?
For the magnetic-strength question: the model is encouraging. It does not
indicate that the nominal4.5mm spacing leaves inadequate field.
The often cited20-50mT near-target range is context, not a universal cutoff.
This candidate is stronger, which can affect ignition, discharge voltage and
erosion. More magnetic field is not automatically a better sputter source.

For overall gun operation: not established. No operating gas pressure, RF
sheath, electron energy distribution, plasma density or secondary emission
has been solved. Ignition and sustaining conditions cannot be certified from
magnetic strength alone. A full kinetic plasma simulation would require those
inputs and should be checked against an actual discharge.

BALANCE IS A SEPARATE QUESTION
The mechanical proposal was called a balanced candidate because its nominal
outer/center pole-area ratio is1.08. That alone does not establish balance.
This simulation resolves the near-target field and candidate confinement ring.
No axis Bz reversal was found in the sampled nominal region up to68mm above
the target, but that is not proof of exact balance. A local closed racetrack
exists in unbalanced magnetrons too.
Do not treat this work as certification of balanced topology. A reliable
effective pole-flux/leakage assessment needs additional pole-face refinement
and a defined balance measure; this mesh was verified for the target-region
field, not tiny-offset flux integrals over individual6mm pole faces.

SPACING SENSITIVITY (NONMAGNETIC TARGET ONLY)
'''
for d in thickness:text+=f"Target {d['target_thickness_mm']}mm; pole-to-face {d['pole_tip_to_front_face_mm']:.1f}mm: ring mean {d['track_mean_Bparallel_mT']:.1f}mT, minimum {d['track_min_Bparallel_mT']:.1f}mT.\n"
text+='''
RECOMMENDED NEXT CHECK
Map the assembled cold field with a calibrated Hall probe at known heights
above the actual target, for example1,3 and5mm. Compare the measured normal
and parallel components with the model before deciding whether to alter
magnet strength, pole spacing or copper thickness. Then establish ignition,
stability, target erosion and temperatures over the intended operating range.

SOURCES
Magnetostatic scalar-potential formulation for magnetron circuits:
https://simulation.ist.fraunhofer.de/bfield_howto/
Reference AISI1010 B-H table and its CERN source attribution:
https://quickfield.com/glossary/soft_steel.htm
N42 magnetic material reference:
https://www.arnoldmagnetics.com/products/neodymium-iron-boron-magnets/
Typical magnetron magnetic-field context:
https://doi.org/10.1088/1361-6595/AC7F53

FILES
Magnetic circuit simulation - confinement assessment.mp4: narrated results.
Assessment results.json: numerical results and checks.
Target field map.png / Field section.png / Racetrack uniformity.png /
Field versus height.png: standalone scientific figures.
fine_nominal_field.npz: mesh, potential, element B, projected air B and materials.
The code and material assumptions are supplied for reproducibility.
No mechanical CAD has been changed by this simulation task.
'''
(P/'Simulation assessment.txt').write_text(text,encoding='utf-8')
with (P/'Field versus height.csv').open('w',newline='') as f:
 w=csv.writer(f);w.writerow(['Height above target mm','Mean parallel B mT at r20mm','Minimum parallel B mT at r20mm'])
 for row in zip(fine['height_scan']['above_target_mm'],fine['height_scan']['Bparallel_mean_mT'],fine['height_scan']['Bparallel_min_mT']):w.writerow(row)
with (P/'Racetrack field.csv').open('w',newline='') as f:
 s=np.load(P/'fine_nominal_samples.npz');w=csv.writer(f);w.writerow(['Angle degrees','Bnormal-zero radius mm','Parallel B mT'])
 for row in zip(np.rad2deg(s['theta']),s['track_r'],s['track_B']*1000):w.writerow(row)
packages=['numpy','scipy','gmsh','scikit-fem','pyamg','magpylib','vtk','matplotlib','Pillow','imageio-ffmpeg']
(P/'requirements.txt').write_text('\n'.join(n+'=='+importlib.metadata.version(n) for n in packages)+'\n')
print(json.dumps(checks,indent=2))
