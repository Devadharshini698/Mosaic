$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Speech
$demoDirectory = Join-Path $PSScriptRoot '../artifacts/demo'
$demoScenes = Get-Content -LiteralPath (Join-Path $demoDirectory 'scenes.json') -Raw | ConvertFrom-Json
$narrator = New-Object System.Speech.Synthesis.SpeechSynthesizer
$narrator.SelectVoice('Microsoft Zira Desktop')
$narrator.Rate = 3
for ($sceneIndex = 0; $sceneIndex -lt $demoScenes.Count; $sceneIndex++) {
    $narrator.SetOutputToWaveFile((Join-Path $demoDirectory ('scene-{0}.wav' -f $sceneIndex)))
    $narrator.Speak($demoScenes[$sceneIndex].text)
    $narrator.SetOutputToNull()
}
$narrator.Dispose()
Write-Output 'Synthetic narration rendered for 8 scenes.'
