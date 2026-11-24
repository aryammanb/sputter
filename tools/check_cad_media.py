"""Read current STEP independently and decode current master movies."""
from pathlib import Path
import json, re, subprocess, hashlib,sys
import cadquery as cq
import imageio_ffmpeg

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'validation';OUT.mkdir(exist_ok=True)

def check_cad():
    records=[]
    for rel in ['chamber-design/coolant-fitting-r06/Magnetron R06.step','chamber-design/coolant-fitting-r06/Complete sputter system R06.step']:
        p=ROOT/rel;print('Reading',rel,flush=True)
        solids=cq.importers.importStep(str(p)).val().Solids();bad=[i for i,s in enumerate(solids) if not s.isValid()]
        records.append({'file':rel,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'solid_count':len(solids),'invalid_indices_zero_based':bad,'invalid_count':len(bad)})
    assert records[0]['solid_count']==141 and records[0]['invalid_count']==0
    assert records[1]['solid_count']==406 and records[1]['invalid_count']==1
    meta=json.loads((ROOT/'chamber-design/coolant-fitting-r06/R06 component register.json').read_text())
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
    for name in ['01-current-system.mp4','02-current-gun.mp4','03-current-field-and-evidence.mp4']:
        p=ROOT/'media'/name;print('Decoding',name,flush=True)
        info=subprocess.run([ff,'-hide_banner','-i',str(p)],capture_output=True,text=True).stderr
        assert 'Video: h264' in info and 'Audio: aac' in info and 'Subtitle: mov_text' in info
        check=subprocess.run([ff,'-hide_banner','-v','warning','-i',str(p),'-map','0:v:0','-map','0:a:0','-f','null','-'],capture_output=True,text=True)
        assert check.returncode==0,check.stderr
        volume=subprocess.run([ff,'-hide_banner','-i',str(p),'-vn','-sn','-af','volumedetect','-f','null','-'],capture_output=True,text=True).stderr
        mean=re.search(r'mean_volume: ([\-\d.]+) dB',volume)
        assert mean and -50<float(mean[1])<0
        reports.append({'file':'media/'+name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'duration':re.search(r'Duration: ([\d:.]+)',info)[1],'video':'H.264','audio':'AAC','subtitles':'mov_text English','full_video_audio_decode_exit_code':check.returncode,'mean_audio_volume_dB':float(mean[1]),'decoder_warnings':check.stderr.strip()})
    (OUT/'media-check.json').write_text(json.dumps({'passed':True,'method':'FFmpeg stream inspection, complete video/audio decode, audio volume check; rendered stills visually reviewed. No physical hardware footage claimed.','videos':reports},indent=2))
    print('CAD and media checks passed',flush=True)

if __name__=='__main__':
    if '--media-only' not in sys.argv:check_cad()
    check_media()
