$ErrorActionPreference='Stop'
Add-Type -AssemblyName System.Speech
$jointVoice=New-Object System.Speech.Synthesis.SpeechSynthesizer
$jointVoice.SelectVoice('Microsoft David Desktop')
$jointVoice.Rate=1
$jointScenes=Get-Content -LiteralPath (Join-Path $PSScriptRoot 'scenes.json') -Raw | ConvertFrom-Json
for($jointIndex=0;$jointIndex -lt $jointScenes.Count;$jointIndex++) {
 $jointVoice.SetOutputToWaveFile((Join-Path $PSScriptRoot ('voice-{0}.wav' -f $jointIndex)))
 $jointVoice.Speak($jointScenes[$jointIndex].speech)
 $jointVoice.SetOutputToNull()
}
$jointVoice.Dispose()
