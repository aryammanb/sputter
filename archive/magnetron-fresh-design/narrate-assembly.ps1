$ErrorActionPreference='Stop'
Add-Type -AssemblyName System.Speech
$narrator=New-Object System.Speech.Synthesis.SpeechSynthesizer
$narrator.SelectVoice('Microsoft David Desktop')
$narrator.Rate=1
$chapters=Get-Content -LiteralPath (Join-Path $PSScriptRoot 'assembly-video-chapters.json') -Raw | ConvertFrom-Json
for($assemblyChapter=0;$assemblyChapter -lt $chapters.Count;$assemblyChapter++){
 $narrator.SetOutputToWaveFile((Join-Path $PSScriptRoot ('assembly-voice-{0:D2}.wav' -f $assemblyChapter)))
 $narrator.Speak($chapters[$assemblyChapter].speech)
 $narrator.SetOutputToNull()
 Write-Output ('Narrated {0}: {1}' -f ($assemblyChapter+1),$chapters[$assemblyChapter].title)
}
$narrator.Dispose()
