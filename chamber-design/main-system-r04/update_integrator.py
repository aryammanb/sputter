from pathlib import Path
P=Path(__file__).resolve().parent;p=P/'integrate_video.py';s=p.read_text();a=s.index("filt=f'");b=s.index('\nsubprocess.run',a)
s=s[:a]+'''detail_start=main['chapters'][19][0];detail_end=main['chapters'][20][0]
filt=(f'[0:v]trim=start=0:end={cut},setpts=PTS-STARTPTS,fps=12[v0];[0:a]atrim=start=0:end={cut},asetpts=PTS-STARTPTS[a0];'
 f'[1:v]trim=start=0:end={fitend},setpts=PTS-STARTPTS,fps=12[v1];[1:a]atrim=start=0:end={fitend},asetpts=PTS-STARTPTS[a1];'
 f'[0:v]trim=start={cut}:end={detail_start},setpts=PTS-STARTPTS,fps=12[v2];[0:a]atrim=start={cut}:end={detail_start},asetpts=PTS-STARTPTS[a2];'
 f'[2:v]setpts=PTS-STARTPTS,fps=12[v3];[0:a]atrim=start={detail_start}:end={detail_end},asetpts=PTS-STARTPTS[a3];'
 f'[0:v]trim=start={detail_end},setpts=PTS-STARTPTS,fps=12[v4];[0:a]atrim=start={detail_end},asetpts=PTS-STARTPTS[a4];'
 '[v0][a0][v1][a1][v2][a2][v3][a3][v4][a4]concat=n=5:v=1:a=1[v][a]')''' +s[b:]
s=s.replace("'-filter_complex',filt", "'-i',str(P/'Deposition detail scene.mp4'),'-filter_complex',filt")
p.write_text(s)
print('Integration includes improved deposition stage view')
