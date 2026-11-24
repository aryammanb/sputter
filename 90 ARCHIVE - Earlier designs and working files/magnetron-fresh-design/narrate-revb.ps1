$ErrorActionPreference='Stop'
Add-Type -AssemblyName System.Speech
$voice=New-Object System.Speech.Synthesis.SpeechSynthesizer
$voice.SelectVoice('Microsoft David Desktop');$voice.Rate=1
$chapters=Get-Content -LiteralPath (Join-Path $PSScriptRoot 'RevB\video-chapters.json') -Raw | ConvertFrom-Json
for($revbChapter=0;$revbChapter -lt $chapters.Count;$revbChapter++){
 $voice.SetOutputToWaveFile((Join-Path $PSScriptRoot ('RevB\voice-{0:D2}.wav' -f $revbChapter)))
 $voice.Speak($chapters[$revbChapter].speech);$voice.SetOutputToNull()
 Write-Output ('Narrated chapter {0}' -f ($revbChapter+1))
}
$voice.Dispose()
