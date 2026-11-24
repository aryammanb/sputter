"""Generate R08 from the checked R07 revision, preserving the native parts."""
from pathlib import Path
import shutil

root = Path(__file__).resolve().parent
previous = root / "magnetron-cad-r07"
output = root / "magnetron-cad-r08"
output.mkdir(exist_ok=True)

changed = {"101", "105", "202", "203", "301", "304", "502"}
for part in previous.glob("R07 *.SLDPRT"):
    if part.name.split()[1] in changed or part.name.endswith("C-channel core.SLDPRT"):
        continue
    destination = output / part.name.replace("R07 ", "R08 ", 1)
    if not destination.exists():
        shutil.copy2(part, destination)


