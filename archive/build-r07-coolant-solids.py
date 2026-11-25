"""Generate and check the three replacement coolant solids in millimetres."""
import math
from pathlib import Path

import cadquery as cq


def cylinder(radius, length, base, direction=(1, 0, 0)):
    return cq.Solid.makeCylinder(radius, length, cq.Vector(*base), cq.Vector(*direction))


folder = Path(__file__).resolve().parent / "magnetron-cad-r07"
folder.mkdir(exist_ok=True)
divider = math.pi / 8
outer_radius, inner_radius = 25, 10.4
width = 4
channel_plane = cq.Plane(origin=(159.7, 0, 0), xDir=(0, 1, 0), normal=(1, 0, 0))
start, end = divider + .04, divider + math.tau - .04


def polar(radius, angle):
    return radius * math.cos(angle), radius * math.sin(angle)


void = (
    cq.Workplane(channel_plane)
    .moveTo(*polar(outer_radius, start))
    .threePointArc(polar(outer_radius, divider + math.pi), polar(outer_radius, end))
    .lineTo(*polar(inner_radius, end))
    .threePointArc(polar(inner_radius, divider + math.pi), polar(inner_radius, start))
    .close()
    .extrude(width)
    .val()
)
assert len(void.Solids()) == 1 and void.isValid()
core = cylinder(34.4, width, (159.7, 0, 0)).cut(void)
for index in range(3):
    y, z = polar(29.4, math.pi / 2 + index * math.tau / 3)
    core = core.cut(cylinder(1.65, width, (159.7, y, z)))
assert core.isValid() and len(core.Solids()) == 1
cq.exporters.export(core, str(folder / "306-channel.step"))

for index, angle in enumerate((divider - .24, divider + .24), 1):
    y0, z0 = polar(20.8, angle)
    y1, z1 = polar(13, angle)
    dy, dz = y1 - y0, z1 - z0
    length = math.sqrt(24**2 + dy**2 + dz**2)
    direction = (24 / length, dy / length, dz / length)
    base = (20.7, y0 - 5 * dy / 24, z0 - 5 * dz / 24)
    trim = cq.Solid.makeBox(24, 100, 100, cq.Vector(25.7, -50, -50))
    transition = cylinder(2.25, length * 34 / 24, base, direction).cut(
        cylinder(1.65, length * 34 / 24, base, direction)
    ).intersect(trim)
    bounds = transition.BoundingBox()
    assert transition.isValid() and len(transition.Solids()) == 1
    assert abs(bounds.xmin - 25.7) < 1e-5 and abs(bounds.xmax - 49.7) < 1e-5
    cq.exporters.export(transition, str(folder / f"106-transition-{index}.step"))
    # Check the entire backplate opening against the channel, not just its center.
    port = cylinder(2.4, width, (159.7, y1, z1))
    intersection = port.intersect(void).Volume()
    assert abs(intersection - port.Volume()) < 1e-5, (index, intersection, port.Volume())
    print(f"Port {index}: entire Ø4.8 mm opening within the single C-channel void")
print(f"Expected SolidWorks channel core volume: {core.Volume():.6f} mm³")
