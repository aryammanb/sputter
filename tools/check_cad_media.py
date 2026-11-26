"""Read current STEP independently and decode current master movies."""
from pathlib import Path
import json, re, subprocess, hashlib,sys
import cadquery as cq
import imageio_ffmpeg

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'validation';OUT.mkdir(exist_ok=True)

def check_cad():
    records=[]
    for rel in ['system-architecture-and-cad/models/Magnetron R06.step','system-architecture-and-cad/models/Complete sputter system R06.step']:
        p=ROOT/rel;print('Reading',rel,flush=True)
        solids=cq.importers.importStep(str(p)).val().Solids();bad=[i for i,s in enumerate(solids) if not s.isValid()]
        records.append({'file':rel,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'solid_count':len(solids),'invalid_indices_zero_based':bad,'invalid_count':len(bad)})
    assert records[0]['solid_count']==141 and records[0]['invalid_count']==0
    assert records[1]['solid_count']==406 and records[1]['invalid_count']==1
    meta=json.loads((ROOT/'system-architecture-and-cad/models/R06 component register.json').read_text())
    k=0;classified=[]
    for q in meta:
        for i in records[1]['invalid_indices_zero_based']:
            if k<=i<k+q['solid_count']:classified.append({'name':q['name'],'role':q['role'],'note':q['note']})
        k+=q['solid_count']
    assert all(x['role']=='backing_pump' for x in classified)
    cad={'passed':True,'checks':records,'known_invalid_reference':classified,'scope':'Independent current STEP reopen, solid counts and validity. Native SolidWorks original checks are preserved separately; native application was not rerun in this packaging task.'}
    (OUT/'cad-check.json').write_text(json.dumps(cad,indent=2))

def check_media():
    ff=imageio_ffmpeg.get_ffmpeg_exe();reports=[]
    selected=json.loads((ROOT/'design/current.json').read_text())['current_media']
    for rel in selected:
        p=ROOT/rel;print('Decoding',rel,flush=True)
        info=subprocess.run([ff,'-hide_banner','-i',str(p)],capture_output=True,text=True).stderr
        assert 'Video: h264' in info and 'Audio:' not in info
        check=subprocess.run([ff,'-hide_banner','-v','warning','-i',str(p),'-map','0:v:0','-f','null','-'],capture_output=True,text=True)
        assert check.returncode==0,check.stderr
        reports.append({'file':rel,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'duration':re.search(r'Duration: ([\d:.]+)',info)[1],'video':'H.264','audio':False,'full_video_decode_exit_code':check.returncode,'decoder_warnings':check.stderr.strip()})
    (OUT/'media-check.json').write_text(json.dumps({'passed':True,'method':'FFmpeg stream inspection and complete decode of the three selected corrected silent walkthroughs. No new videos rendered.','videos':reports},indent=2))
    print('Current media checks passed',flush=True)

if __name__=='__main__':
    if '--media-only' not in sys.argv:check_cad()
    check_media()
