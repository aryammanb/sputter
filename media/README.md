# Current design explanations

## Complete gun walkthrough

[Complete R06 gun — silent](gun-complete-walkthrough/R06%20sputter%20gun%20-%20complete%20silent%20walkthrough.mp4) · [Narrated companion](gun-complete-walkthrough/R06%20sputter%20gun%20-%20complete%20narrated%20walkthrough.mp4). Detailed exploded and sectioned views cover all 141 component instances across 60 shots, including small fasteners, PTFE sleeves, seals and individual electrical connections. [Coverage and reproduction](gun-complete-walkthrough/README.md).

## Mechanical assembly walkthrough

[Silent four-minute walkthrough](assembly-walkthrough/Sputter%20R06%20-%20silent%204%20minute%20walkthrough.mp4) — all 37 shots from the corrected tour at 2.5× speed, with audio removed. 1080p, 60 fps.

[Rebuilt R06 assembly and operation walkthrough](assembly-walkthrough/Sputter%20R06%20-%20mechanical%20assembly%20walkthrough.mp4) — actual R06 CAD component geometry and colors, detailed assembly motions, compression-cap tightening, and a narrated operating cycle with shutter opening/closure in 1080p. The gun stays assembled. [Scope and reproduction](assembly-walkthrough/README.md).

## Silent assembly walkthrough

[Silent system CAD walkthrough](system-walkthrough/Sputter%20system%20-%20silent%20CAD%20walkthrough.mp4) — 2:11, part labels only, no audio. Shows major assemblies, attachment interfaces, and door/shutter motion without disassembling the gun. [Scope and reproduction](system-walkthrough/README.md).

## Narrated design reviews

All videos and CAD stills in this library were generated from the latest R06 system STEP for the 24 November 2026 snapshot. The magnetic plot uses the current 3.175 mm target-plane assessment. Old walkthrough segments are not reused. [provenance.json](provenance.json) records source hashes and synthetic narration details.

| Video | Subjects | Transcript |
|---|---|---|
| [01 Current system](01-current-system.mp4) | Whole system, internal chamber/stage/shutter, pumping and gas selections | [Text](01-current-system-transcript.txt) |
| [02 Current gun](02-current-gun.mp4) | R06 gun, twelve-stack magnets, R05 target/clamp, R06 M5 ports | [Text](02-current-gun-transcript.txt) |
| [03 Current field and evidence](03-current-field-and-evidence.mp4) | Updated field assessment and remaining qualification | [Text](03-current-field-and-evidence-transcript.txt) |

MP4 files have English synthetic narration and switchable English subtitle tracks. Individual chapter MP4/SRT files are also retained. Some GitHub clients require opening/downloading the raw video. These are explanatory CAD animations, not footage of physical hardware or a validated running machine.

## Current stills

![Complete current system](system.png)

![Current internal chamber view](chamber.png)

![Current gun](gun.png)

![Current magnetic head](magnetron.png)

![Current coolant ports](cooling.png)

Copper transparency and hidden chamber context reveal internal parts. Views retain actual R06 part positions. The RV3 reference, MFC housing and cabinet geometry remain subject to the documented selection mismatches. No rendered photo is presented as an as-built record.

To reproduce: `python tools/build_current_media.py`. See [reproduction guide](../docs/reproducibility.md) for dependencies and native narration requirements.
