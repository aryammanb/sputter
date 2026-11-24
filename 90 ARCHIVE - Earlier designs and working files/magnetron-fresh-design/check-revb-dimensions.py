"""Independent scalar/area checks for the RevB native geometry (mm)."""
import json, math, re
from pathlib import Path
from scipy.integrate import quad

ROOT=Path(__file__).resolve().parent/'RevB'
poles=[(20*math.cos(i*math.pi/3),20*math.sin(i*math.pi/3)) for i in range(6)]
ports=[(26*math.cos(math.pi/6),13),(26*math.cos(math.pi/6),-13)]
def subtract(intervals,lo,hi):
    result=[]
    for a,b in intervals:
        if lo>a:result.append((a,min(b,lo)))
        if hi<b:result.append((max(a,hi),b))
    return [(a,b) for a,b in result if b>a]
def wet_width(y):
    if abs(y)>=29:return 0.
    z=math.sqrt(29**2-y*y);intervals=[(-z,z)]
    if abs(y)<10:
        z=math.sqrt(100-y*y);intervals=subtract(intervals,-z,z)
    for a,b in poles:
        if abs(y-a)<7.5:
            z=math.sqrt(7.5**2-(y-a)**2);intervals=subtract(intervals,b-z,b+z)
    if y>=9:intervals=subtract(intervals,-3,3)
    return sum(b-a for a,b in intervals)
events=[-29,29,-10,10,9,math.sqrt(100-9),math.sqrt(29**2-9)]
events.extend(max(-29,min(29,y+s*7.5)) for y,z in poles for s in [-1,1])
for y,z in poles:
    for edge in [-3,3]:
        if abs(edge-z)<7.5:
            delta=math.sqrt(7.5**2-(edge-z)**2);events.extend([y-delta,y+delta])
breakpoints=sorted({round(v,10) for v in events})
wet_area=sum(quad(wet_width,a,b,epsabs=1e-8,epsrel=1e-10,limit=250)[0] for a,b in zip(breakpoints,breakpoints[1:]))
body_expected=(math.pi*41**2*7-wet_area*4-math.pi*(6.15**2+6*4.15**2)*4.5
               -math.pi*(8.75**2-6.75**2)*1.15-6*math.pi*(6.75**2-4.75**2)*1.15
               -math.pi*(33.3**2-30.7**2)*1.5-math.pi*1.25**2*(6*4+3*3))
cover_expected=(math.pi*41**2*3+2*math.pi*7**2*8-math.pi*(6.3**2+6*4.3**2)*3
                -6*math.pi*1.7**2*3-2*math.pi*(4.4**2*7+2**2*4))
report={
 'outer_magnets':6,'center_discs':2,'dry_wells':7,'primary_face_o_rings':8,
 'outer_magnet_pcd_mm':40,'head_diameter_mm':82,
 'magnet_tip_to_target_seat_mm':7-3,'blind_well_end_clearance_mm':4.5-3,
 'minimum_front_copper_mm':7-4.5,
 'body_well_radial_fit_mm':(8.3-8)/2,
 'cover_outer_passage_radial_fit_mm':(8.6-8)/2,
 'utility_to_outer_magnet_min_mm':min(math.dist(a,b)-8-4 for a in ports for b in poles),
 'locator_hole_to_utility_relief_ligament_mm':min(math.dist(a,b)-8.25-4.15 for a in ports for b in poles),
 'body_gland_to_blind_bore_inner_ligament_mm':min(4.75-4.15,6.75-6.15),
 'cover_hole_to_gland_inner_ligament_mm':min(4.75-4.3,6.75-6.3),
 'central_to_outer_wet_gap_mm':20-7.5-10,
 'outer_island_to_outer_wet_wall_gap_mm':29-20-7.5,
 'wet_pocket_area_mm2':wet_area,'water_pocket_volume_ml':wet_area*4/1000,
 'body_expected_volume_mm3':body_expected,'cover_expected_volume_mm3':cover_expected,
 'small_ring_nominal_squeeze_percent':(1.5-1.15)/1.5*100,
 'small_ring_nominal_gland_fill_percent':math.pi*.75**2/(2*1.15)*100,
 'perimeter_ring_nominal_squeeze_percent':25,
 'main_long_screw_nominal_engagement_mm':25-5-14-3,
 'magnetic_field_validation':'NOT PERFORMED','pressure_thermal_seal_qualification':'NOT PERFORMED'
}
native=(ROOT/'RevB native geometry checks.txt').read_text()
for key,label,expected in [('body_volume_difference_mm3','F01-001',body_expected),('cover_volume_difference_mm3','F01-002',cover_expected)]:
    row=next(s for s in native.splitlines() if s.startswith(label))
    actual=float(re.search(r'volume_mm3=([0-9.]+)',row).group(1));report[key]=actual-expected
    assert abs(actual-expected)<.02,(label,actual,expected)
assert report['utility_to_outer_magnet_min_mm']>1
assert report['blind_well_end_clearance_mm']>0
(ROOT/'RevB independent dimension checks.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print(json.dumps(report,indent=2))
