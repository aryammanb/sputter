$ErrorActionPreference='Stop'
Add-Type -AssemblyName System.Speech
$out=Join-Path $PSScriptRoot 'single-coax-proposal'
New-Item -ItemType Directory -Path $out -Force | Out-Null
$chapters=Get-Content (Join-Path $PSScriptRoot 'coax-video-chapters.json') -Raw | ConvertFrom-Json
$voice=New-Object System.Speech.Synthesis.SpeechSynthesizer
$voice.SelectVoice('Microsoft David Desktop')
$voice.Rate=1
for($i=0;$i -lt $chapters.Count;$i++){
 $voice.SetOutputToWaveFile((Join-Path $out ('voice-{0:00}.wav' -f $i)))
 $voice.Speak($chapters[$i].speech)
 $voice.SetOutputToNull()
}
$voice.Dispose()
Write-Output 'Narration complete'

