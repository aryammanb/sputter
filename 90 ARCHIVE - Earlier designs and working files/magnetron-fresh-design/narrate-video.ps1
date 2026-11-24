$ErrorActionPreference='Stop'
Add-Type -AssemblyName System.Speech
$narrator=New-Object System.Speech.Synthesis.SpeechSynthesizer
$narrator.SelectVoice('Microsoft David Desktop')
$narrator.Rate=0
$chapters=Get-Content -LiteralPath (Join-Path $PSScriptRoot 'video-chapters.json') -Raw | ConvertFrom-Json
for($chapterIndex=0;$chapterIndex -lt $chapters.Count;$chapterIndex++){
 $narrator.SetOutputToWaveFile((Join-Path $PSScriptRoot ('voice-{0:D2}.wav' -f $chapterIndex)))
 $narrator.Speak($chapters[$chapterIndex].speech)
 $narrator.SetOutputToNull()
 Write-Output ('Narrated chapter {0}: {1}' -f ($chapterIndex+1),$chapters[$chapterIndex].title)
}
$narrator.Dispose()
