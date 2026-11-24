import math
import struct
from pathlib import Path

import imageio_ffmpeg
import numpy as np
from PIL import Image, ImageDraw, ImageFont

root = Path(__file__).resolve().parent
parts = []
with (root / '.r08-mesh.bin').open('rb') as file:
    while byte := file.read(1):
        length = byte[0] & 127
        if byte[0] & 128:
            length += 128 * file.read(1)[0]
        name = file.read(length).decode().split('/')[-1].split()
        code = name[2] if name[1] == 'R01' else name[1]
        count, = struct.unpack('<i', file.read(4))
        mesh = np.frombuffer(file.read(36 * count), '<f4').reshape(-1, 3, 3)
        parts.append((code, mesh, mesh.mean((0, 1))))
parts.sort(key=lambda item: (item[0], math.atan2(item[2][2], item[2][1])))
assert len(parts) == 76

# Each row names a moving set in order. Positions are exploded-view offsets in mm.
chapters = [
    ('Complete gun', 'The rear guard houses the power terminal. The small end is the shielded 2-inch target. The large flange docks to the chamber.', '', []),
    ('Rear guard', 'Four rear screws release the cover. The copper terminal socket grips the feedthrough conductor. The cable end is a design envelope.', '601 01', [('607','Rear cover screws',-31),('602','Rear cover',-22),('604','Cable insulation',-37),('605','Cable core',-64),('603','Terminal socket',-12)]),
    ('Guard and ground', 'Four screws fasten the guard to the NW100 plate. Their metal flange faces form the bond. The final cable entry and interlock are pending.', '101 01', [('606','Mounting screws',26),('601','Grounded shell',-50)]),
    ('KF25 vacuum joint', 'The clamp draws the beveled rims together. The centering ring locates the O-ring, which seals between the faces. The stub stays welded to the mount.', '101 04', [('05','KF25 clamp',0),('01','Ceramaseal feedthrough',-40),('03','O-ring',-17),('02','Centering ring',-8)]),
    ('Shield removal', 'Remove the three shield screws and slide the shield toward the target face. Its open rear clears the head, exposing the clamp screws.', '502 401 402', [('503','Shield screws',40),('501','Shield slides toward the substrate',74)]),
    ('Target stack', 'With the shield out of the way, remove three clamp screws. Lift the retaining ring and the 2-inch aluminum target off the copper seat.', '308', [('403','Clamp screws',85),('402','Retaining ring',55),('401','Aluminum target',28)]),
    ('Grounded weldment • fabrication view', 'The KF25 stub and stem seat on the NW100 plate. The shield seat attaches at the front of the stem. These are welded joints.', '', [('04','Welded KF25 stub',-28),('101','NW100 mount plate',-14),('102','Grounded stem',11),('502','Shield seat',37)]),
    ('Coolant • grounded side', 'Two welded bulkheads bring coolant through the mount. Angled tubes and reducers spread the lines from 6.2 mm to 20.4 mm apart at the breaks.', '101', [('103','Welded bulkheads',-22),('106','Stainless transitions',6),('109','Copper reducers',24),('107','Grounded sockets',41)]),
    ('Coolant • isolated side', 'The alumina breaks interrupt the metal path. Live sockets and reducers bring the inlet and return back together at the copper jacket. Joined parts shown apart for fabrication.', '107 305', [('105','Alumina breaks',-22),('108','Live sockets',-9),('110','Live reducers',6),('104','Cathode coolant tubes',24)]),
    ('Power rod', 'The copper rod carries DC or RF from the center pin to the yoke. The ceramic guide centers it and leaves passages for both coolant breaks.', '01 304', [('201','Power rod and socket',-18),('202','Ceramic rod guide',22)]),
    ('Ceramic head mounting', 'The grounded keeper captures the outer shoulder. Three separate live screws and washers secure the carrier stack to the yoke.', '304 502', [('207','Ground keeper screws',-31),('204','Grounded keeper',-19),('205','Live retainer screws',-42),('206','Live washers',-25),('203','Stepped alumina carrier',19)]),
    ('Rear magnet pack', 'The locator pockets hold all nine magnets behind the yoke. The annular center and the eight outer magnets have opposite axial polarity.', '305', [('301','Alumina locator',-23),('302','Center magnet',-40),('303','Outer magnets',-51),('304','Steel yoke',-8)]),
    ('Copper jacket • fabrication view', 'The head screws are outside the water path. The brazed backplate, channel core and target-seat cover form one sealed jacket.', '304', [('309','Head screws',-35),('308','Copper target-seat cover',36),('306','C-channel core',16),('305','Copper backplate',-10)]),
    ('Water through the C-channel', 'The two ports open on opposite sides of the divider. Water follows the long arc behind the target. The moving dots show direction.', '104 306', []),
    ('Complete gun', 'The gun is ready for design review. Check shield extraction space in the chamber. The supplier-dependent power and coolant interfaces are still open.', '', []),
]

fps = 15
size = (1280, 720)
font_dir = Path('C:/Windows/Fonts')
big = ImageFont.truetype(str(font_dir / 'segoeuib.ttf'), 35)
body = ImageFont.truetype(str(font_dir / 'segoeui.ttf'), 22)
small = ImageFont.truetype(str(font_dir / 'segoeui.ttf'), 17)
colors = {
    **dict.fromkeys('01 107 108 109 110 201 305 306 308 603 605'.split(),(223,148,95)),
    **dict.fromkeys('105 202 203 301 604'.split(),(242,229,193)),
    **dict.fromkeys('103 104 106'.split(),(93,176,219)),
    **dict.fromkeys('101 102 204 501 502 601 602'.split(),(103,161,160)),
    '302':(235,122,118), '303':(138,166,232), '03':(112,124,150),
}

def smooth(value):
    value = min(1, max(0, value))
    return value * value * (3 - 2 * value)

def layout(index):
    _, _, context, moves = chapters[index]
    codes = set(context.split()) | {code for code, _, _ in moves}
    selected = [(c, mesh, pivot) for c, mesh, pivot in parts if not codes or c in codes]
    transforms = {}
    order = []
    for code, label, dx in moves:
        matches = [i for i, item in enumerate(selected) if item[0] == code]
        assert matches, code
        for rank, i in enumerate(matches):
            _, _, center = selected[i]
            yz = center[1:]
            radial = yz / max(1, np.linalg.norm(yz))
            extra = 15 + (rank % 2) * 12 if len(matches) > 1 else 0
            if code == '05':
                radial, extra = (0, 1), 42
            transforms[i] = np.array([dx, *(np.asarray(radial) * extra)])
            order.append((i, label, rank, len(matches)))
    fit = np.concatenate([mesh + transforms.get(i, 0) for i, (_, mesh, _) in enumerate(selected)] +
                         [mesh for _, mesh, _ in selected])
    center = (fit.min((0, 1)) + fit.max((0, 1))) / 2
    max_span = max(np.ptp(fit[:,:,0]), 1.1 * np.ptp(fit[:,:,1]), 1.1 * np.ptp(fit[:,:,2]))
    scale = min(6.2, 720 / max_span)
    return selected, transforms, order, center, scale

def frame(index, time, duration, scene, reverse=False):
    title, description, _, _ = chapters[index]
    selected, transforms, order, center, scale = scene
    count = len(order)
    fraction = time / duration
    progress = min(1, max(0, (time - .45) / max(1, duration - 2.4)))
    positions = {i: smooth(progress * count - step) for step, (i, _, _, _) in enumerate(order)}
    active = order[min(count - 1, int(progress * count))] if count else None
    coords = np.concatenate([mesh + transforms.get(i, 0) * positions.get(i, 0)
                             for i, (_, mesh, _) in enumerate(selected)])
    rgb = np.concatenate([np.tile(colors.get(c, (177, 193, 215)), (len(mesh),1))
                          for c, mesh, _ in selected])
    yaw = (.30 + .52 * fraction) if index not in (0, 13, 14) else (-.57 + 1.47 * fraction)
    if index in (4, 5):
        yaw = -.51 - .19 * fraction
    if index == 13:
        yaw = .98
    cy, sy = math.cos(yaw), math.sin(yaw)
    def project(points):
        x,y,z = np.moveaxis(points-center,-1,0)
        depth = -x*sy + y*cy
        return np.stack((786+scale*(x*cy+y*sy), 342-scale*(.96*z+.28*depth), depth),axis=-1)
    mesh = project(coords)
    normal = np.cross(mesh[:,1]-mesh[:,0],mesh[:,2]-mesh[:,0])
    normal /= np.maximum(1e-6,np.linalg.norm(normal,axis=1,keepdims=True))
    lighting = .55 + .42*np.abs(normal @ np.array([-.23,.39,.89]))
    shaded = np.uint8(np.clip(rgb*lighting[:,None]+6,0,255))
    im = Image.new('RGB',size,'#121c2b')
    draw = ImageDraw.Draw(im)
    draw.rectangle((0,0,320,720),fill='#1d2c40')
    draw.text((32,34),'MAGNETRON  /  R08',font=small,fill='#a8c9e1')
    def wrap(text, x, y, width, font, fill):
        line = ''
        for word in text.split():
            candidate = (line + ' ' + word).strip()
            if line and draw.textlength(candidate,font=font)>width:
                draw.text((x,y),line,font=font,fill=fill)
                y += font.size + 8
                line = word
            else:
                line = candidate
        draw.text((x,y),line,font=font,fill=fill)
    wrap(title,32,85,255,big,'#f2f6fa')
    wrap(description,32,235,248,body,'#d9e8f4')
    for i in np.argsort(mesh[:,:,2].mean(1)):
        draw.polygon(mesh[i,:,:2].reshape(-1).tolist(),fill=tuple(shaded[i]))
    if active and .45 < time < duration-1:
        i, label, rank, total = active
        code, _, point = selected[i]
        x, y, _ = project(point + transforms[i] * positions[i])
        caption = label + (f'  {rank+1}/{total}' if total>1 else '')
        draw.ellipse((x-6,y-6,x+6,y+6), fill='#fff3cd', outline='#121c2b', width=2)
        draw.text((343,648),caption,font=body,fill='#fff3cd')
    if index == 13:
        angles = math.pi/8 + np.linspace(.24,math.tau-.24,170)
        points = np.column_stack((np.full(len(angles),161.7),18*np.cos(angles),18*np.sin(angles)))
        a,b = [(13*math.cos(theta),13*math.sin(theta)) for theta in angles[[0,-1]]]
        points = np.vstack(([118.7,*a],[159.7,*a],[161.7,*a],points,[161.7,*b],[159.7,*b],[118.7,*b]))
        path = project(points)[:,:2]
        draw.line([tuple(point) for point in path],fill='#6ddaf4',width=4)
        for n in range(7):
            x,y=path[(int(time*39)+n*24)%len(path)]
            draw.ellipse((x-4,y-4,x+4,y+4),fill='white')
    draw.text((32,668),f'{index+1:02}  /  {len(chapters):02}',font=small,fill='#a8c9e1')
    if reverse:
        draw.text((1060,34),'ASSEMBLY REPLAY',font=small,fill='#a8c9e1')
    return np.asarray(im)

if __name__ == '__main__':
    import sys
    scenes = [layout(i) for i in range(len(chapters))]
    assert {part[0] for part in parts} == {code for _, _, _, moves in chapters for code, _, _ in moves}
    if 'preview' in sys.argv:
        for i in (0,4,5,8,10,11,13):
            Image.fromarray(frame(i,4,7,scenes[i])).save(root/f'.r08-preview-{i}.png')
        sys.exit()
    filename = root/'magnetron-r08-teardown-final.mp4'
    writer = imageio_ffmpeg.write_frames(str(filename),size,fps=fps,quality=8,
                                        output_params=['-movflags','+faststart'])
    writer.send(None)
    timeline = []
    elapsed = 0
    for i in range(len(chapters)):
        count = len(scenes[i][2])
        duration = 5.0 if not count else max(6.0, 2.4 + count*.85)
        frames = math.ceil(duration*fps)
        timeline.append((elapsed/fps,chapters[i][0]))
        for step in range(frames):
            writer.send(frame(i,step/fps,duration,scenes[i]))
        elapsed += frames
        print(f'{i+1}/{len(chapters)}: {chapters[i][0]}',flush=True)
    timeline.append((elapsed/fps,'Assembly replay'))
    for i in reversed(range(1,13)):
        duration = 6
        for step in range(24):
            writer.send(frame(i,duration*(1-step/23),duration,scenes[i],True))
    for step in range(45):
        writer.send(frame(14,step/fps,3,scenes[14],True))
    writer.close()
    (root/'magnetron-r08-teardown-chapters.md').write_text(
        '# Magnetron R08 teardown\n\n'+'\n'.join(
            f'- {int(s)//60}:{int(s)%60:02} {title}' for s,title in timeline)+'\n',encoding='utf-8')


