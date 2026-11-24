$ErrorActionPreference='Stop'
Add-Type -AssemblyName System.Speech
$speaker=New-Object System.Speech.Synthesis.SpeechSynthesizer
$speaker.SelectVoice('Microsoft David Desktop')
$speaker.Rate=1
$chapters=Get-Content -LiteralPath (Join-Path $PSScriptRoot 'chapters.json') -Raw | ConvertFrom-Json
for($i=0;$i -lt $chapters.Count;$i++){
 $speaker.SetOutputToWaveFile((Join-Path $PSScriptRoot ('voice-{0:D2}.wav' -f $i)))
 $speaker.Speak($chapters[$i].speech)
 $speaker.SetOutputToNull()
}
$speaker.Dispose()
Write-Output 'Seven narration tracks created'
