param([string]$Target = (Join-Path $PSScriptRoot 'Manager.ps1'))
$ErrorActionPreference = 'Stop'
if (-not (Test-Path -LiteralPath $Target)) { throw 'Manager implementation missing' }
. $Target -LibraryOnly
$n = 0
function Assert($Condition, [string]$Message) { if (-not $Condition) { throw $Message }; $script:n++ }
Assert ((Compare-Release '1.2.0-alpha.12' '1.2.0-alpha.2') -gt 0) 'Numeric prerelease ordering'
Assert ((Compare-Release '1.2.0' '1.2.0-rc.9') -gt 0) 'Final beats same-core prerelease'
Assert ((Compare-Release '1.3.0-alpha.1' '1.2.9') -gt 0) 'New alpha beats older stable'
Assert ((Compare-Release '3.16.0a2' '3.15.0') -gt 0) 'Python alpha ordering'
Assert ((Compare-Release '3.16.0a12' '3.16.0a2') -gt 0) 'Python numeric alpha ordering'
$t = [pscustomobject]@{latest='1.3.0'; alpha='1.4.0-alpha.2'; beta='1.2.0-beta.9'; 'alpha-win32'='99.0.0'}
Assert ((Select-NpmRelease $t) -eq '1.4.0-alpha.2') 'Newest generic prerelease selected, platform tags excluded'
Assert ((Select-NpmRelease ([pscustomobject]@{latest='2.0.0'; alpha='1.0.0-alpha.1'})) -eq '2.0.0') 'Stale experimental build not selected'
Assert ((Select-NpmRelease ([pscustomobject]@{latest='1.0.0'})) -eq '1.0.0') 'Publisher with no preview'
Assert ((Quote-Literal "a'b") -eq "'a''b'") 'PowerShell literal escaping'
$secret='sk-proj-'+('A'*40)
$text = Protect-Text ('Bearer abcdefghijklmnop '+$secret+' test@example.com https://a.test/?token=PRIVATE')
Assert (-not $text.Contains($secret)) 'OpenAI key redacted'
Assert (-not $text.Contains('abcdefghijklmnop')) 'Bearer token redacted'
Assert (-not $text.Contains('test@example.com')) 'Email redacted'
Assert (-not $text.Contains('PRIVATE')) 'URL query redacted'
Assert (-not (Test-SafeLeaf '../secret')) 'Traversal rejected'
Assert (-not (Test-SafeLeaf 'C:\secret')) 'Absolute path rejected'
Assert (Test-SafeLeaf 'v27.0.0-nightly20261010') 'Version leaf allowed'
Assert (-not (Test-SafeLeaf '.')) 'Dot rejected'
Assert ((Get-ExitClass 0) -eq 'OK') 'Zero exit'
Assert ((Get-ExitClass 3010) -eq 'REBOOT') 'Reboot classified'
Assert ((Get-ExitClass 42) -eq 'FAILED') 'Unknown errors never pass'
Assert ((Get-GitBlobHash ([byte[]]@())) -eq 'e69de29bb2d1d6434b8b29ae775ad8c2e48c5391') 'Git object digest'
$all = [IO.File]::ReadAllText($Target)
$tokens=$null; $errors=$null
[void][Management.Automation.Language.Parser]::ParseInput($all,[ref]$tokens,[ref]$errors)
Assert ($errors.Count -eq 0) ('PowerShell parse: '+($errors | Out-String))
Assert ($all -notmatch '(?i)Set-MpPreference|DisableRealtimeMonitoring|dangerously-bypass-approvals|Remove-AppxPackage') 'No security bypass or automatic app-data removal'
Assert ($all.Contains('Interactive')) 'Scheduled task stays in user session'
Assert ($all.Contains('StartWhenAvailable')) 'Missed scheduled runs supported'
$install=Join-Path (Split-Path $Target -Parent) 'Install.ps1'
if (Test-Path $install) {
    $tokens=$null; $errors=$null
    [void][Management.Automation.Language.Parser]::ParseFile($install,[ref]$tokens,[ref]$errors)
    Assert ($errors.Count -eq 0) ('Bootstrap parse: '+($errors | Out-String))
}
Assert ((Get-ExitClass -1978335189) -eq 'NO_UPDATE') 'WinGet no-update HRESULT'
Assert ((Select-NpmRelease ([pscustomobject]@{latest='1.2.0';canary='1.3.0-canary.8';nightly='1.4.0-nightly.2'})) -eq '1.4.0-nightly.2') 'Nightly/canary are eligible'
if ($env:OS -eq 'Windows_NT') {
    $tmp=Join-Path $env:TEMP ('odm-test-'+[guid]::NewGuid().ToString('N'))
    New-Item -ItemType Directory $tmp | Out-Null
    $script:RunDir=$tmp; $script:Commands=New-Object Collections.ArrayList; $script:StepName='Process regression'
    try {
        $engine=Join-Path $env:SystemRoot 'System32\WindowsPowerShell\v1.0\powershell.exe'
        $r=Invoke-ManagedProcess $engine @('-NoProfile','-Command','Write-Output "quote and spaces OK"; exit 7') 30
        Assert ($r.Code -eq 7) 'Child exit code preserved'
        Assert ($r.Output.Contains('quote and spaces OK')) 'Command arguments preserved'
    } finally { Remove-Item -LiteralPath $tmp -Recurse -Force }
}
$fixture=[ordered]@{url='https://example.test/?token=PRIVATE';next='preserved';nested=@('test@example.com','plain')}
$clean=Protect-Object $fixture
$roundtrip=($clean | ConvertTo-Json -Depth 8) | ConvertFrom-Json
Assert ($roundtrip.next -eq 'preserved') 'Redaction preserves adjacent JSON fields'
Assert ($roundtrip.url -notmatch 'PRIVATE') 'Nested URL secret removed before serialization'
Assert ($roundtrip.nested.Count -eq 2) 'Redaction preserves array structure'
if ($env:OS -eq 'Windows_NT') {
    $tmp=Join-Path $env:TEMP ('odm-inventory-'+[guid]::NewGuid().ToString('N'))
    New-Item -ItemType Directory $tmp | Out-Null
    $script:RunDir=$tmp; $script:Inventory=[ordered]@{}; $script:Commands=New-Object Collections.ArrayList
    try {
        Get-Inventory | Out-Null
        Assert ($script:Inventory.Contains('codexConfigExists')) 'Inventory does not overwrite the read-only HOME variable'
        $DataRoot=$tmp; $RunId='test'; $script:IsAudit=$true
        $script:Inventory=$fixture; $script:Results=@(); $script:Endpoints=@(); $script:Selected=@()
        Save-Report 'TEST'
        $report=Get-Content (Join-Path $tmp 'Report.json') -Raw | ConvertFrom-Json
        Assert ($report.inventory.next -eq 'preserved') 'Complete report JSON round trip'
        Assert ($report.inventory.url -notmatch 'PRIVATE') 'Complete report token redaction'
    } finally { Remove-Item -LiteralPath $tmp -Recurse -Force }
}
Write-Output "PASS: $n offline tests; no installers, credentials, model calls or Windows settings touched."
