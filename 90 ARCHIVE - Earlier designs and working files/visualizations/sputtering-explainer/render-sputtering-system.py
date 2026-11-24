import math
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from importlib.util import spec_from_file_location, module_from_spec

spec = spec_from_file_location("magnetron_geometry", Path(__file__).with_name("render-magnetron-extended.py"))
gun = module_from_spec(spec)
spec.loader.exec_module(gun)

folder = Path(__file__).parent
W, H, FPS = 1280, 720, 24
BG = (18, 23, 31)
WHITE = (241, 246, 253)
MUTED = (174, 188, 206)
LINE = (77, 95, 116)
BLUE = (117, 198, 242)
VIOLET = (205, 159, 255)
GOLD = (255, 207, 125)

def font(size, bold=False):
    return ImageFont.truetype("C:/Windows/Fonts/" + ("segoeuib.ttf" if bold else "segoeui.ttf"), size)

small, body, title, giant = font(19), font(26), font(40, True), font(58, True)
scenes = [
    (9, "Load the wafer", "The 2-inch wafer faces the 2-inch aluminum target.\nThe chamber closes with the shutter between them."),
    (19, "Remove most of the air", "The rotary-vane pump draws air out through the roughing line.\nIts sliding vanes trap, compress, and expel the gas."),
    (31, "Reach base pressure", "The turbopump’s fast blades drive gas toward its outlet.\nThe same rotary-vane pump now backs the turbo through the foreline."),
    (44, "Feed argon and set the pressure", "The mass flow controller meters argon in. The throttle valve adjusts\nhow quickly gas is pumped out, and the gauge measures the pressure."),
    (53, "The gun is a cooled electrode", "The clamp holds aluminum against the copper cathode, which carries\nDC power and conducts heat away to circulating coolant."),
    (62, "The magnets shape the discharge", "The center and outer magnets confine electrons near the target face.\nThe steel yoke gives their magnetic flux a return path."),
    (71, "Keep the powered parts isolated", "Ceramic separates the cathode from the grounded flange. The shield\nseats on that flange and its inward lip covers the powered clamp."),
    (83, "Ignite the argon", "The supply biases aluminum negative. Electrons ionize argon near\nthe target, and positive argon ions accelerate toward it."),
    (93, "Clean the target with the shutter closed", "Ion impacts knock atoms off the target, removing its surface layer.\nThe closed shutter intercepts the material that would reach the wafer."),
    (107, "Open the shutter and grow the film", "Argon ions keep striking the target. Some ejected aluminum atoms\nreach the wafer and stick. The film builds up as more atoms arrive."),
    (123, "Check thickness across the wafer", "Measure the center, middle, and edge. Adjust spacing if needed.\nRotation can average angular variation. A radial gradient can remain."),
    (134, "End the run and unload", "Close the shutter, turn off power and argon, and isolate the chamber\nbefore venting. The coated wafer can then be removed."),
]

def smooth(x):
    x = min(1, max(0, x))
    return x*x*(3-2*x)

def dot(p, x, y, r, color):
    p.ellipse((x-r,y-r,x+r,y+r),fill=color)

def text(p, x, y, value, color=WHITE, face=small, anchor="lm"):
    p.text((x,y), value, font=face, fill=color, anchor=anchor)

def box(p, bounds, label, active=False):
    p.rounded_rectangle(bounds, radius=10, fill=(27, 37, 50),
                        outline=BLUE if active else LINE, width=2)
    x,y,x2,y2=bounds
    text(p,(x+x2)/2,(y+y2)/2,label,WHITE if active else MUTED,anchor="mm")

def pipe(p, points, active, t):
    p.line(points, fill=LINE, width=3, joint="curve")
    if not active:
        return
    p.line(points,fill=(51, 114, 148),width=4,joint="curve")
    lengths=[math.dist(a,b) for a,b in zip(points,points[1:])]
    for i in range(4):
        offset=((t*.65 + i/4)%1)*sum(lengths)
        for a,b,length in zip(points,points[1:],lengths):
            if offset<=length:
                f=offset/length
                dot(p,a[0]+(b[0]-a[0])*f,a[1]+(b[1]-a[1])*f,4,BLUE)
                break
            offset-=length

assembled=gun.frame(2).crop((470,120,810,407))
gun_tile=assembled.resize((212,179),Image.Resampling.LANCZOS)

def process(image,p,t):
    rough=9<=t<19
    turbo=19<=t<128
    gas=31<=t<127
    plasma=74<=t<126
    deposit=95<=t<125
    shutter_move=smooth((t-93)/2)*(1-smooth((t-124)/2))
    # Schematic chamber and plumbing, with the exact assembled gun rendering.
    p.rounded_rectangle((355,96,878,508),radius=29,outline=LINE,width=3)
    text(p,379,120,"VACUUM CHAMBER",MUTED)
    pipe(p,[(260,178),(355,178)],gas,t)
    pipe(p,[(878,170),(1081,170),(1081,229)],rough,t)
    pipe(p,[(878,385),(925,385),(925,396),(980,396)],turbo,t)
    pipe(p,[(1081,361),(1081,287)],turbo,t)
    box(p,(60,149,260,207),"Argon flow controller",gas)
    text(p,60,131,"From argon supply",MUTED)
    box(p,(980,229,1182,287),"Rotary-vane pump",rough or turbo)
    box(p,(980,361,1182,431),"Turbomolecular pump",turbo)
    text(p,1015,149,"Roughing line",MUTED)
    text(p,1095,325,"Foreline",MUTED)
    p.line((918,372,933,398),fill=WHITE if turbo else LINE,width=3)
    text(p,894,449,"Throttle valve",MUTED)
    if t<19:
        status="Air in chamber" if t<9 else "Pressure falling"
    elif t<31:
        status="Pumping toward base pressure"
    elif t<74:
        status="Argon process pressure"
    elif t<83:
        status="Strike, then reduce pressure"
    elif t<127:
        status="Deposition pressure"
    else:
        status="Isolate, then vent"
    text(p,379,480,"Pressure gauge  ·  "+status,MUTED)

    image.paste(gun_tile,(510,281))
    film=smooth((t-95)/11)
    p.ellipse((563,161,674,190),fill=(132,155,185),outline=(197,214,234),width=2)
    if film:
        p.arc((563,167,674,195),0,180,fill=GOLD,width=max(1,round(5*film)))
    text(p,697,178,"Wafer",WHITE)
    text(p,727,407,"Magnetron",WHITE)
    if plasma:
        p.ellipse((578,330,657,352),outline=VIOLET,width=4)
        for i in range(9):
            phase=(t*.67+i*.31)%1
            x=617+36*math.cos(i*2.4)
            dot(p,x,309+34*phase,3,VIOLET)
        for i in range(8):
            phase=(t*.59+i*.37)%1
            x=617+(18+32*phase)*math.cos(i*2.4)
            endpoint=193 if deposit else 255
            dot(p,x,333+(endpoint-333)*phase,3,GOLD)
    elif t<74:
        amount=18 if t<9 else max(0,int(18*(1-(t-9)/18))) if t<31 else 10
        for i in range(amount):
            x=389+(i*137)%436+7*math.sin(t+i)
            y=204+(i*67)%101
            dot(p,x,y,2,BLUE if gas else MUTED)
    shift=shutter_move*169
    p.ellipse((550+shift,244,688+shift,271),fill=(64,77,93),outline=(158,176,196),width=2)
    text(p,417 if shift<84 else 788,230,"Shutter closed" if shift<84 else "Shutter open",MUTED,
         anchor="lm" if shift<84 else "mm")
    if 83<=t<107:
        dot(p,77,310,4,VIOLET)
        text(p,91,310,"Argon ions to target")
        dot(p,77,345,4,GOLD)
        text(p,91,345,"Aluminum from target")

def uniformity(p,t):
    cx,cy=377,282
    for radius,color in [(154,(54,68,86)),(112,(61,82,103)),(63,(73,104,129))]:
        p.ellipse((cx-radius,cy-radius,cx+radius,cy+radius),fill=color,outline=LINE,width=2)
    for radius in (0,81,133):
        for sign in (-1,1) if radius else (1,):
            dot(p,cx+sign*radius,cy,6,GOLD)
    text(p,cx,464,"Example measurement points",MUTED,anchor="mm")
    text(p,672,184,"Target-to-wafer spacing",WHITE,body)
    text(p,672,224,"Changes how the flux spreads before it lands.",MUTED)
    text(p,672,301,"Wafer rotation",WHITE,body)
    text(p,672,341,"Averages variation around the rotation axis.",MUTED)
    text(p,672,418,"Thickness map",WHITE,body)
    text(p,672,458,"Shows whether the change improved the film.",MUTED)

def frame(t):
    index=next(i for i,s in enumerate(scenes) if t<s[0])
    _, heading, caption=scenes[index]
    image=Image.new("RGB",(W,H),BG)
    p=ImageDraw.Draw(image)
    if 44<=t<71:
        if t<53:
            original=9+min(8,(t-44)*1.5)
        elif t<62:
            original=26 if t<57.5 else 32
        else:
            original=37 if t<66 else 49-smooth((71-t)/5)*3
        source=gun.frame(original)
        image.paste(source.crop((0,68,W,548)),(0,68))
    elif 107<=t<123:
        uniformity(p,t)
    else:
        process(image,p,t)
    chapter="CHAMBER & GAS" if t<44 else "INSIDE THE MAGNETRON" if t<71 else "PLASMA & FILM" if t<107 else "MEASURE & UNLOAD"
    text(p,60,41,"MAGNETRON SPUTTERING  /  "+chapter,MUTED)
    p.line((60,545,1220,545),fill=LINE,width=2)
    p.line((60,545,60+1160*t/134,545),fill=BLUE,width=3)
    text(p,60,583,heading,WHITE,title)
    p.multiline_text((60,626),caption,font=body,fill=MUTED,spacing=5)
    return image

if __name__=="__main__":
    out=folder/"magnetron-sputtering-explained.mp4"
    cmd=[gun.imageio_ffmpeg.get_ffmpeg_exe(),"-y","-hide_banner","-loglevel","error",
         "-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-",
         "-an","-c:v","libx264","-preset","fast","-crf","17","-pix_fmt","yuv420p",
         "-movflags","+faststart",str(out)]
    with subprocess.Popen(cmd,stdin=subprocess.PIPE) as encoder:
        for i in range(134*FPS):
            encoder.stdin.write(frame(i/FPS).tobytes())
        encoder.stdin.close()
        if encoder.wait():
            raise SystemExit("Encoding failed")

