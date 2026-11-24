$ErrorActionPreference='Stop'
Add-Type -AssemblyName System.Speech
$voice=New-Object System.Speech.Synthesis.SpeechSynthesizer
$voice.SelectVoice('Microsoft David Desktop');$voice.Rate=1
$folder=Join-Path $PSScriptRoot 'assembly-video'
$chapters=Get-Content -LiteralPath (Join-Path $folder 'chapters.json') -Raw | ConvertFrom-Json
for($chapter=0;$chapter -lt $chapters.Count;$chapter++){
 $voice.SetOutputToWaveFile((Join-Path $folder ('voice-{0:D2}.wav' -f $chapter)))
 $voice.Speak($chapters[$chapter].speech);$voice.SetOutputToNull()
 Write-Output ('Narrated {0}: {1}' -f ($chapter+1),$chapters[$chapter].title)
}
$voice.Dispose()
