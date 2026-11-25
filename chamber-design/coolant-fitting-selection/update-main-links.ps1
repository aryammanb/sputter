$base=(Resolve-Path 'chamber-design/coolant-fitting-r06').Path
$shell=New-Object -ComObject WScript.Shell
$folder=(Resolve-Path '01 MAIN DESIGN - Updated Advanced Tinkering/01 Latest updated design - twelve-stack').Path
$link=$shell.CreateShortcut((Join-Path $folder '01 MAIN ASSEMBLY - Latest twelve-stack STEP.lnk'));$link.TargetPath=Join-Path $base 'SolidWorks R06/Magnetron R06 - M5 coolant fittings.step';$link.Save()
$link=$shell.CreateShortcut((Join-Path $folder '08 Native SolidWorks assembly - coolant fittings R06.lnk'));$link.TargetPath=Join-Path $base 'SolidWorks R06/Magnetron R06 - M5 coolant fittings.SLDASM';$link.Save()
$link=$shell.CreateShortcut((Join-Path $folder '09 Complete system STEP - coolant fittings R06.lnk'));$link.TargetPath=Join-Path $base 'Complete sputter system R06.step';$link.Save()
@"
LATEST COOLANT FITTING REVISION: R06

Native gun assembly:
$base\SolidWorks R06\Magnetron R06 - M5 coolant fittings.SLDASM

Complete system STEP context:
$base\Complete sputter system R06.step

SolidWorks CAD package:
$base\Coolant fittings R06 - SolidWorks CAD package.zip

SMC KQG2S04-M5 selected; backplate now has native passage/tap-drill cut features
and M5x0.8 thread callouts. R05 target/clamp retained. Seal qualification pending.
"@ | Set-Content '01 MAIN DESIGN - Updated Advanced Tinkering/06 Latest coolant fittings R06.txt' -Encoding utf8
