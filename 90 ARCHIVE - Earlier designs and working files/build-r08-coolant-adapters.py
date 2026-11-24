"""Model the two socketed coolant paths as solid-wall, open-bore transitions."""
from math import cos, pi, sin
from pathlib import Path

import cadquery as cq

folder = Path(__file__).resolve().parent / "magnetron-cad-r08"


def polar(radius, angle):
    return radius * cos(angle), radius * sin(angle)


def loft(stations, radius_index):
    wires = [
        cq.Wire.makeCircle(row[radius_index], cq.Vector(*row[:3]), cq.Vector(1, 0, 0))
        for row in stations
    ]
    return cq.Solid.makeLoft(wires, ruled=True)


def export(name, stations):
    solid = loft(stations, 3).cut(loft(stations, 4))
    assert solid.isValid() and len(solid.Solids()) == 1
    cq.exporters.export(solid, str(folder / (name + ".step")))
    return solid


results = []
for index, side in enumerate((-1, 1), 1):
    narrow = polar(13, pi / 8 + side * .24)
    wide = polar(15.5, pi / 8 + side * .72)
    results.extend([
        export(f"109-ground-{index}", [
            (49.7, *narrow, 2.25, 1.65),
            (66, *wide, 3.175, 2.4),
            (71, *wide, 3.175, 2.4),
        ]),
        export(f"110-live-{index}", [
            (99, *wide, 3.175, 2.4),
            (104, *wide, 3.175, 2.4),
            (118.7, *narrow, 2.25, 1.65),
        ]),
    ])

for index, solid in enumerate(results):
    for other in results[:index]:
        assert solid.intersect(other).Volume() < 1e-6
print("Four open-bore transitions generated and checked")
