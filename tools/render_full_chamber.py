"""Render full-chamber stills from the current STEP-derived component mesh."""
from pathlib import Path
import hashlib
import json
import math
import numpy as np
import vtk
from vtk.util.numpy_support import numpy_to_vtk, numpy_to_vtkIdTypeArray, vtk_to_numpy
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'outputs/full-chamber-r06'
OUT.mkdir(parents=True, exist_ok=True)
source = ROOT / 'system-architecture-and-cad/models/Complete sputter system R06.step'
provenance = json.loads((ROOT / 'media/provenance.json').read_text())
digest = hashlib.sha256(source.read_bytes()).hexdigest()
assert digest == provenance['source_sha256'], 'STEP changed: regenerate the view mesh first'
meta = json.loads((source.parent / 'R06 component register.json').read_text())
mesh = np.load(ROOT / 'media/r06-view-mesh.npz')

W, H = 2000, 2000
window = vtk.vtkRenderWindow()
window.SetOffScreenRendering(1)
window.SetSize(W, H)
window.SetMultiSamples(8)
renderer = vtk.vtkRenderer()
renderer.SetBackground(.91, .935, .96)
renderer.SetBackground2(.99, .995, 1)
renderer.GradientBackgroundOn()
window.AddRenderer(renderer)
renderer.SetUseDepthPeeling(1)
renderer.SetMaximumNumberOfPeels(100)
window.SetAlphaBitPlanes(1)
actors = []
groups = {'chamber', 'door', 'gun', 'fitting', 'shutter'}
for i, q in enumerate(meta):
    if q['group'] not in groups:
        continue
    triangles = mesh[f'p{i}']
    poly = vtk.vtkPolyData()
    points = vtk.vtkPoints()
    points.SetData(numpy_to_vtk(triangles.reshape(-1, 3), deep=True))
    poly.SetPoints(points)
    cells = vtk.vtkCellArray()
    cells.SetData(numpy_to_vtkIdTypeArray(np.arange(0, len(triangles)*3+1, 3, dtype=np.int64), deep=True),
                  numpy_to_vtkIdTypeArray(np.arange(len(triangles)*3, dtype=np.int64), deep=True))
    poly.SetPolys(cells)
    clean = vtk.vtkCleanPolyData()
    clean.SetInputData(poly)
    normals = vtk.vtkPolyDataNormals()
    normals.SetInputConnection(clean.GetOutputPort())
    normals.SetFeatureAngle(45)
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(normals.GetOutputPort())
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    prop = actor.GetProperty()
    prop.SetColor(*q['color'])
    prop.SetAmbient(.23)
    prop.SetDiffuse(.7)
    prop.SetSpecular(.45)
    prop.SetSpecularPower(45)
    if q['role'] == 'glass':
        prop.SetColor(.36, .67, .79)
        prop.SetOpacity(.25)
    renderer.AddActor(actor)
    actors.append((q, actor))

camera = renderer.GetActiveCamera()
camera.ParallelProjectionOn()
camera.SetViewUp(0, 0, 1)
capture = vtk.vtkWindowToImageFilter()
capture.SetInput(window)
capture.SetInputBufferTypeToRGB()
capture.ReadFrontBufferOff()
font_path = 'C:/Windows/Fonts/segoeui.ttf'
bold_path = 'C:/Windows/Fonts/segoeuib.ttf'
views = [
    ('01-front', 'Full chamber / front', -55, 18, False),
    ('02-rear', 'Full chamber / rear', 125, 22, False),
    ('03-cutaway', 'Full chamber / interior cutaway', -68, 13, True),
]
for filename, title, azimuth, elevation, cutaway in views:
    for q, actor in actors:
        hidden = cutaway and (q['group'] == 'door' or q['name'] in [
            'Right wall', 'Left wall - reserved blank', 'Front welded door frame',
            'Front door compressed gasket envelope'])
        actor.SetVisibility(not hidden)
    az, el = map(math.radians, (azimuth, elevation))
    focus = (0, 0, 205)
    camera.SetFocalPoint(*focus)
    camera.SetPosition(1200*math.cos(az)*math.cos(el),
                       1200*math.sin(az)*math.cos(el), 205+1200*math.sin(el))
    renderer.ResetCamera()
    camera.SetParallelScale(camera.GetParallelScale()*1.10)
    renderer.ResetCameraClippingRange()
    window.Render()
    capture.Modified()
    capture.Update()
    rgb = vtk_to_numpy(capture.GetOutput().GetPointData().GetScalars()).reshape(H, W, 3)
    image = Image.fromarray(np.flipud(rgb)).copy()
    draw = ImageDraw.Draw(image)
    draw.text((70, 48), title, font=ImageFont.truetype(bold_path, 48), fill='#22354b')
    draw.text((72, 113), 'R06 assembly | actual CAD geometry',
              font=ImageFont.truetype(font_path, 28), fill='#52677a')
    note = 'Door and side walls hidden to expose internals' if cutaway else 'Complete chamber, gun mount and chamber ports'
    draw.text((72, H-105), note, font=ImageFont.truetype(font_path, 28), fill='#52677a')
    image.save(OUT / f'{filename}.png')
    print(OUT / f'{filename}.png', flush=True)

(OUT / 'provenance.json').write_text(json.dumps({
    'source_step': str(source.relative_to(ROOT)), 'source_sha256': digest,
    'mesh': 'media/r06-view-mesh.npz', 'geometry_modified': False,
    'scope': 'Chamber, door, R06 gun, compression fitting and shutter; external utility equipment omitted.',
    'cutaway': 'Door and both side walls hidden. Component positions unchanged.',
    'images': [v[0] + '.png' for v in views],
}, indent=2))
window.Finalize()
