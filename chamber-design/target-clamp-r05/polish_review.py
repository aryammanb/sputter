from pathlib import Path
p=Path('chamber-design/target-clamp-r05/render_clamp_review.py');s=p.read_text()
for a,b in [('OD93.6','OD 93.6'),('PCD80','PCD 80'),('aperture47.8','aperture 47.8'),('band1.25','band 1.25'),('opening49.45','opening 49.45'),('clearance1.0','clearance 1.0'),('at100 mm','at 100 mm'),('gun1.175','gun 1.175'),('a2 mm','a 2 mm'),('is5.675','is 5.675')]:s=s.replace(a,b)
p.write_text(s)
