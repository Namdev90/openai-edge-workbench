param([switch]$Gui)
$ErrorActionPreference='Stop'
$projectRoot=Split-Path $PSScriptRoot -Parent
if(!(Test-Path "$projectRoot/Edge.ps1")){throw 'FAIL: Edge.ps1 has not been implemented'}
. "$projectRoot/Edge.ps1" -Library
$script:Count=0
function Assert($Condition,[string]$Message){if(!$Condition){throw "FAIL: $Message"};$script:Count++}
Assert ((Get-EdgeVersion @('1.0.0','2.0.0-beta.4','2.0.0-alpha.10','2.0.0-alpha.2')) -eq '2.0.0-alpha.10') 'earliest maturity, then latest build'
Assert ((Get-EdgeVersion @('3.0.0','2.0.0-alpha.20')) -eq '3.0.0') 'do not choose obsolete lower-base alpha'
Assert ((Get-EdgeVersion @('3.0.0-beta.2','3.0.0-nightly.20261010')) -eq '3.0.0-nightly.20261010') 'nightly outranks beta in same release line'
Assert ((Get-EdgeVersion @('bad','1.0.0-alpha.1-linux-x64','1.0.0')) -eq '1.0.0') 'reject platform-specific npm package variants'
Assert ((Get-EdgeVersion @()) -eq '') 'empty version feed'
Assert ((Get-EdgeVersion @('1.0.0-rc.1','1.0.0-beta.9')) -eq '1.0.0-beta.9') 'beta before release candidate'
Assert ((Get-EdgeVersion @('1.0.0-rc.1','1.0.0')) -eq '1.0.0-rc.1') 'explicit prerelease preference'
Assert ((Get-EdgeVersion @('1.10.0','1.9.99')) -eq '1.10.0') 'numeric base ordering'
Assert ((Protect-Text 'Bearer abcDEF123456 sk-proj-abcdefghijk namu@example.com') -notmatch 'abcDEF123456|abcdefghijk|namu@example.com') 'redact tokens and emails'
Assert ((Protect-Text 'https://test.example/path?token=secretvalue') -notmatch 'secretvalue') 'redact URL query values'
Assert ((Protect-Text 'C:\Users\namde\Desktop\report.txt') -notmatch 'namde') 'redact user path'
Assert ((Protect-Text 'api_key="privatevalue" password=notpublic') -notmatch 'privatevalue|notpublic') 'redact key-value secrets'
Assert ((Get-HttpMeaning 401) -eq 'REACHABLE_AUTH_REQUIRED') 'HTTP 401 is not authenticated success'
Assert ((Get-HttpMeaning 403) -eq 'REACHABLE_BLOCKED') 'HTTP 403 is not functioning service'
Assert ((Get-HttpMeaning 404) -eq 'REACHABLE_HTTP_ERROR') 'missing endpoint is not healthy'
Assert ((Get-HttpMeaning 500) -eq 'SERVICE_ERROR') 'server errors not healthy'
Assert ((Get-HttpMeaning 0) -eq 'NETWORK_FAILED') 'unreachable endpoint'
Assert ((Get-HttpMeaning 200) -eq 'HTTP_OK_AUTH_UNVERIFIED') 'HTTP 200 alone not authorization'
Assert ((Quote-Arg 'a b') -eq '"a b"') 'Windows argument quoting'
Assert ((Quote-Arg '') -eq '""') 'empty argument quoting'
$temp=Join-Path ([IO.Path]::GetTempPath()) ('edge-tests-'+[guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $temp | Out-Null
try {
 $inside=Join-Path $temp 'tools/old'
 New-Item -ItemType Directory -Path $inside -Force | Out-Null
 Assert (Test-OwnedPath $inside $temp) 'owned child allowed'
 Assert (!(Test-OwnedPath $temp $temp)) 'root itself cannot be removed'
 Assert (!(Test-OwnedPath ($temp+'-neighbor') $temp)) 'prefix collision cannot be removed'
 Assert (!(Test-OwnedPath (Join-Path $temp '../outside') $temp)) 'traversal cannot be removed'
 Write-Atomic (Join-Path $temp 'test.txt') 'first'
 Write-Atomic (Join-Path $temp 'test.txt') 'second'
 Assert (([IO.File]::ReadAllText((Join-Path $temp 'test.txt'))) -eq 'second') 'atomic overwrite'
 $script:Root=$temp; $script:RunDir=Join-Path $temp 'run'
 New-Item -ItemType Directory -Path $script:RunDir | Out-Null
 $script:Events=New-Object 'System.Collections.Generic.List[object]'
 Add-Event 'test' 'REVIEW' 'token=privatevalue' 'rerun audit'
 $e=Get-Content (Join-Path $script:RunDir 'events.jsonl') | ConvertFrom-Json
 Assert ($e.state -eq 'REVIEW') 'structured event state'
 Assert ($e.detail -notmatch 'privatevalue') 'events redact before disk'
 Add-Event 'URL' 'REVIEW' 'https://example.test/status?token=privatevalue'
 Save-Report
 $parsed=Get-Content (Join-Path $script:RunDir 'Report.json') -Raw|ConvertFrom-Json
 Assert ($parsed.schema -eq 'namu-ai-edge-report-v2') 'redaction preserves valid structured JSON'
 Write-Atomic (Join-Path $script:RunDir 'stop.flag') 'test'
 $stopped=Invoke-Program 'definitely-not-a-real-edge-test-program.exe' @() 'stop test' 1 -Private
 Assert ($stopped.code -eq -4) 'no additional subprocess after stop or timeout'
} finally {Remove-Item -LiteralPath $temp -Recurse -Force}
$errors=@()
Get-ChildItem $projectRoot -Filter '*.ps1' -Recurse | ForEach-Object {
 $t=$null;$e=$null;[void][Management.Automation.Language.Parser]::ParseFile($_.FullName,[ref]$t,[ref]$e)
 $errors+=@($e)
}
Assert ((Get-Content "$projectRoot/Edge.ps1" -Raw) -notmatch '(?i)\$(?:home|pid|host)\s*=') 'do not assign read-only automatic variables'
Assert ($errors.Count -eq 0) ('all PowerShell files parse: '+($errors|Out-String))
$catalog=Get-Content "$projectRoot/catalog.json" -Raw | ConvertFrom-Json
Assert ($catalog.packages.Count -ge 10) 'curated workstation catalog present'
Assert (@($catalog.packages|Group-Object id|Where-Object Count -gt 1).Count -eq 0) 'unique package IDs'
Assert ($catalog.packages[0].id -eq '9PLM9XGG6VKS') 'official ChatGPT Store identifier'
Assert ($catalog.pythonPackages -contains 'openai') 'OpenAI Python SDK included'
Assert ($catalog.npmPackages -contains '@openai/codex') 'official Codex package included'
if($Gui){$guiOutput=& "$projectRoot/Edge.ps1" -GuiSmoke; Assert ($guiOutput -contains 'GUI_CONSTRUCTION_OK') 'Windows Forms construction'}
Write-Output "PASS: $script:Count tests; no apps installed, no account calls, no scheduler writes."
