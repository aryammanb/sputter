"""Tightly framed, text-free 4K assembled-to-exploded R06 gun video."""
from pathlib import Path
import json,math,subprocess,time,sys,hashlib
import numpy as np
import vtk,imageio_ffmpeg
from PIL import Image
from vtk.util.numpy_support import vtk_to_numpy
from build_gun_walkthrough import GunRenderer,GUN,META,smooth

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'media/gun-ordered-explosion';OUT.mkdir(exist_ok=True)
W,H,FPS,SECONDS=3840,2160,24,26
az=math.radians(-62);el=math.radians(30)
D=np.array([math.cos(az)*math.cos(el),math.sin(az)*math.cos(el),math.sin(el)])
R=np.array([0.,0.,1.])-D*D[2];R/=np.linalg.norm(R);U=np.cross(D,R)
angle=math.radians(18);R,U=R*math.cos(angle)-U*math.sin(angle),R*math.sin(angle)+U*math.cos(angle)

def shelf_pack(rects,width):
    places={};x=0.;y=0.;row=0.;used=0.
    for i,w,h in rects:
        if x+w>width and x>0:y+=row;x=0.;row=0.
        places[i]=(x,y);x+=w;used=max(used,x);row=max(row,h)
    return places,used,y+row

def main():
    r=GunRenderer();r.win.SetSize(W,H)
    extents={};rects=[];padding=6.
    for i in GUN:
        a=r.actors[i];a.SetVisibility(True);a.SetMapper(r.fullmaps[i]);a.SetUserTransform(None);a.GetProperty().SetOpacity(1)
        pts=vtk_to_numpy(r.fullmaps[i].GetInput().GetPoints().GetData())
        xy=pts@np.stack([R,U,D],axis=1);lo=xy.min(axis=0);hi=xy.max(axis=0);extents[i]=(lo,hi)
        rects.append((i,hi[0]-lo[0]+padding,hi[1]-lo[1]+padding))
    # Axial separation only: retain every component's original X/Y alignment.
    offsets={'shieldtube':-150,'darkcap':-100,'upperbolts':-100,'lowerbolts':-150,
      'clamp':-60,'targetbolts':-60,'target':-30,'cooler':0,'waterseal':12,
      'closure':35,'backbolts':35,'outermag':65,'centermag':65,'yoke':100,'yokebolt':100,
      'headseal':120,'spacer':150,'headbolts':150,'upper62':175,'isolator':200,
      'lower62':225,'base':255,'cups':255,'basebolts':255,'kfcenter':285,'kfseal':300,
      'kfclamps':325,'kfbolts':325,'kftube':325,'hoses':325,'coax':325,
      'fittings':35,'rfhot':35,'rfground':255}
    shifts={i:np.array([0.,0.,offsets[META[i]['role'][4:]]]) for i in GUN}
    assert all(s[0]==0 and s[1]==0 for s in shifts.values())

    measurements=[]
    def frame(t):
        e=smooth((t-3)/13);bounds=[]
        for i in GUN:
            shift=shifts[i]*e;tr=vtk.vtkTransform();tr.Translate(*shift);r.actors[i].SetUserTransform(tr)
            lo,hi=extents[i];offset=shift@np.stack([R,U,D],axis=1);bounds.append((lo+offset,hi+offset))
        lo=np.min([q[0] for q in bounds],axis=0);hi=np.max([q[1] for q in bounds],axis=0);c=(lo+hi)/2
        focus=R*c[0]+U*c[1]+D*c[2];scale=max((hi[1]-lo[1])/2,(hi[0]-lo[0])/(2*W/H))*1.055
        r.cam.SetViewUp(*U);r.cam.SetFocalPoint(*focus);r.cam.SetPosition(*(focus+D*3000));r.cam.SetParallelScale(scale)
        r.ren.ResetCameraClippingRange();r.win.Render();r.cap.Modified();r.cap.Update()
        rgb=vtk_to_numpy(r.cap.GetOutput().GetPointData().GetScalars()).reshape(H,W,3)
        return np.flipud(rgb).copy(),{'time':t,'explosion_fraction':e,'width_fraction':(hi[0]-lo[0])/(2*scale*W/H),'height_fraction':(hi[1]-lo[1])/(2*scale)}

    for t,label in [(0,'assembled'),(9.5,'opening'),(21,'exploded')]:
        im,m=frame(t);Image.fromarray(im).save(OUT/(label+'.jpg'),quality=96);measurements.append(m)
    if '--preview' in sys.argv:r.win.Finalize();print(json.dumps(measurements));return
    ff=imageio_ffmpeg.get_ffmpeg_exe();dest=OUT/'R06 gun - ordered axial explosion 4K.mp4'
    proc=subprocess.Popen([ff,'-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-an','-sn','-c:v','libx264','-preset','fast','-crf','17','-pix_fmt','yuv420p','-movflags','+faststart',str(dest)],stdin=subprocess.PIPE)
    held_first=None;held_last=None;clock=time.time()
    try:
        for k in range(SECONDS*FPS):
            t=k/FPS
            if t<=3 and held_first is not None:im=held_first
            elif t>=16 and held_last is not None:im=held_last
            else:
                im,_=frame(t)
                if t<=3:held_first=im
                if t>=16:held_last=im
            proc.stdin.write(im.tobytes())
            if k%(FPS*4)==0:print(f'{t:.0f}/{SECONDS}s encoded; {time.time()-clock:.0f}s elapsed',flush=True)
    finally:proc.stdin.close()
    assert proc.wait()==0;r.win.Finalize()
    src=ROOT/'system-architecture-and-cad/models/Complete sputter system R06.step'
    report={'video':str(dest),'source':str(src.relative_to(ROOT)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'resolution':[W,H],'fps':FPS,'duration_seconds':SECONDS,'component_instances':len(GUN),'audio':False,'visible_text':False,'camera':'Landscape orientation, dynamically fitted to actual projected part bounds; 5.5% framing margin.','layout':'Axial assembly-order separation only. Original X/Y coordinates retained. Screws and PTFE sleeves stay with their parent components rather than flying out separately. Actual 141 CAD solids, no scaling or substitute geometry.','framing_samples':measurements,'components':[{'name':META[i]['name'],'exploded_translation_mm':shifts[i].tolist()} for i in GUN]}
    (OUT/'provenance.json').write_text(json.dumps(report,indent=2));print(str(dest),flush=True)

if __name__=='__main__':main()
