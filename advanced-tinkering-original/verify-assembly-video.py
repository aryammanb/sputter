"""Validate the completed narrated video and extract encoded-frame review images."""
from pathlib import Path
import csv
import json
import math
import subprocess
import wave
import cv2
import imageio_ffmpeg
import numpy as np
from PIL import Image, ImageDraw

root = Path(__file__).resolve().parent
out = root / 'assembly-video'
video = out / 'Advanced Tinkering original magnetron - detailed full assembly.mp4'
ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
summary = json.loads((out / 'Render summary.json').read_text())
metadata = subprocess.run([ffmpeg, '-hide_banner', '-i', str(video)], capture_output=True, text=True)
(out / 'Encoded video metadata.txt').write_text(metadata.stderr, encoding='utf8')
decode = subprocess.run([ffmpeg, '-v', 'error', '-i', str(video), '-map', '0:v:0', '-map', '0:a:0', '-f', 'null', '-'], capture_output=True, text=True)
assert decode.returncode == 0, decode.stderr
assert not decode.stderr.strip(), decode.stderr
assert metadata.stderr.count('Chapter #') == 18
assert '1920x1080' in metadata.stderr and 'h264' in metadata.stderr
assert 'aac' in metadata.stderr and 'mov_text' in metadata.stderr

cap = cv2.VideoCapture(str(video))
assert cap.isOpened()
fps = cap.get(cv2.CAP_PROP_FPS)
count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
assert abs(count / fps - summary['runtime_seconds']) < .1
assert fps == 15
sheet = Image.new('RGB', (1440, 1620), '#101b2a')
start = 0
for i in range(18):
    with wave.open(str(out / f'voice-{i:02}.wav')) as f:
        duration = math.ceil((f.getnframes() / f.getframerate() + 1.8) * fps) / fps
    when = start + duration * .65
    cap.set(cv2.CAP_PROP_POS_MSEC, when * 1000)
    ok, bgr = cap.read()
    assert ok, (i, when)
    img = Image.fromarray(cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB))
    img.save(out / f'encoded-check-{i:02}.jpg')
    img.thumbnail((480, 270))
    sheet.paste(img, ((i % 3) * 480, (i // 3) * 270))
    start += duration
cap.release()
sheet.save(out / 'Encoded chapter review.jpg')
with (out / 'Component video coverage.csv').open(encoding='utf-8-sig', newline='') as f:
    coverage = list(csv.DictReader(f))
assert len(coverage) == 120
with wave.open(str(out / 'narration.wav')) as f:
    audio = np.frombuffer(f.readframes(f.getnframes()), '<i2').astype(np.float64)
    audio_duration = len(audio) / f.getframerate()
assert abs(audio_duration - start) < .01
report = {
    'video': str(video),
    'bytes': video.stat().st_size,
    'runtime_seconds': count / fps,
    'frames': count,
    'fps': fps,
    'resolution': [1920, 1080],
    'chapters': 18,
    'component_coverage': len(coverage),
    'audio_rms': float(np.sqrt(np.mean(audio ** 2))),
    'full_video_audio_decode': 'passed without errors',
    'embedded_subtitles': True,
    'encoded_chapter_frames_extracted': 18,
}
(out / 'Video verification.json').write_text(json.dumps(report, indent=2), encoding='utf8')
print(json.dumps(report, indent=2))
