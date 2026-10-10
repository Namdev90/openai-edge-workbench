$ErrorActionPreference='Stop'
$repoRoot=Split-Path $PSScriptRoot -Parent
. (Join-Path $repoRoot 'Setup.ps1') -Library
$script:Count=0
function Assert($Condition,[string]$Message){if(!$Condition){throw "FAIL: $Message"};$script:Count++}
function Throws([scriptblock]$Action,[string]$Message){$failed=$false;try{& $Action}catch{$failed=$true};Assert $failed $Message}
$tmp=Join-Path $env:TEMP ('edge-setup-tests-'+[guid]::NewGuid().ToString('N'));[void](New-Item -ItemType Directory -Path $tmp)
try{
 $manifest=Get-Content (Join-Path $repoRoot 'release.json') -Raw|ConvertFrom-Json
 $launcher=Join-Path $tmp 'launcher.cmd';Copy-Item -LiteralPath (Join-Path $repoRoot 'OpenAI-Edge-Workbench.cmd') -Destination $launcher
 Assert-SetupPayload $launcher $manifest;Assert $true 'published embedded payload accepted'
 [IO.File]::AppendAllText($launcher,'tampered')
 Throws {Assert-SetupPayload $launcher $manifest} 'tampered launcher rejected'
 Throws {Get-SetupJson 'repos/Namdev90/amreye-ai/contents/README.md'} 'setup cannot fetch from another repository'
 Throws {Get-SetupDownload 'file.ps1' 'main' (Join-Path $tmp 'download')} 'mutable source ref rejected'
 Throws {Get-SetupDownload '../file.ps1' ('a'*40) (Join-Path $tmp 'download')} 'unsafe download path rejected'
 Write-SetupFile (Join-Path $tmp 'atomic') 'first';Write-SetupFile (Join-Path $tmp 'atomic') 'second'
 Assert ((Get-Content (Join-Path $tmp 'atomic') -Raw) -eq 'second') 'atomic replacement supported'
 $private=Join-Path $tmp 'existing-private';[void](New-Item -ItemType Directory -Path $private)
 $beforeAcl=Get-Acl -LiteralPath $private
 $ownerBefore=$beforeAcl.GetOwner([Security.Principal.SecurityIdentifier]).Value
 $groupBefore=$beforeAcl.GetGroup([Security.Principal.SecurityIdentifier]).Value
 $content=Join-Path $private 'preserved.txt';[IO.File]::WriteAllText($content,'preserved')
 # Existing explicit access must be removed, not retained alongside the three
 # private principals. This adds access only to a disposable test directory.
 $extra=[Security.AccessControl.FileSystemAccessRule]::new([Security.Principal.SecurityIdentifier]::new('S-1-1-0'),'ReadAndExecute','ContainerInherit, ObjectInherit','None','Allow')
 [void]$beforeAcl.AddAccessRule($extra);Set-Acl -LiteralPath $private -AclObject $beforeAcl
 foreach($pass in 1..2){
  Set-SetupPrivateAccess $private
  $afterAcl=Get-Acl -LiteralPath $private
  $rules=@($afterAcl.GetAccessRules($true,$true,[Security.Principal.SecurityIdentifier]))
  $expected=@([Security.Principal.WindowsIdentity]::GetCurrent().User.Value,'S-1-5-18','S-1-5-32-544') | Sort-Object
  $actual=@($rules | ForEach-Object {$_.IdentityReference.Value}) | Sort-Object
  Assert ($afterAcl.AreAccessRulesProtected) "private DACL is protected on pass $pass"
  Assert ($rules.Count -eq 3 -and ($actual -join ',') -eq ($expected -join ',')) "exact private principals on pass $pass"
  Assert (@($rules | Where-Object {$_.IsInherited -or $_.AccessControlType -ne 'Allow' -or $_.FileSystemRights -ne 'FullControl' -or $_.InheritanceFlags -ne 'ContainerInherit, ObjectInherit' -or $_.PropagationFlags -ne 'None'}).Count -eq 0) "private rules retain full control and child inheritance on pass $pass"
  Assert ($afterAcl.GetOwner([Security.Principal.SecurityIdentifier]).Value -eq $ownerBefore -and $afterAcl.GetGroup([Security.Principal.SecurityIdentifier]).Value -eq $groupBefore) "owner and group preserved on pass $pass"
  Assert (([IO.File]::ReadAllText($content)) -eq 'preserved') "existing contents remain accessible on pass $pass"
 }
 $fake=Join-Path $tmp 'no-auth.cmd';[IO.File]::WriteAllText($fake,"@echo off`r`necho Not signed in 1>&2`r`nexit /b 1`r`n")
 Assert (!(Test-GhAuthenticated $fake)) 'missing GitHub sign-in permits public fallback without terminating Windows PowerShell'
 function Get-SetupJson([string]$Endpoint){return [pscustomobject]@{type='file';encoding='base64';size=3;content='YWJj'}}
 Get-SetupDownload 'file.ps1' ('a'*40) (Join-Path $tmp 'download')
 Assert ((Get-Content (Join-Path $tmp 'download') -Raw) -eq 'abc') 'private GitHub contents decoding preserves bytes'
 function Get-SetupJson([string]$Endpoint){return [pscustomobject]@{type='file';encoding='base64';size=4;content='YWJj'}}
 Throws {Get-SetupDownload 'file.ps1' ('a'*40) (Join-Path $tmp 'download')} 'download size mismatch rejected'
 foreach($path in @('Setup.ps1','source/bootstrap.ps1','tools/launcher-loader.ps1')){
  $tokens=$null;$errors=$null;[void][Management.Automation.Language.Parser]::ParseFile((Join-Path $repoRoot $path),[ref]$tokens,[ref]$errors)
  Assert ($errors.Count -eq 0) "$path parses"
 }
}finally{Assert-SetupPath $tmp;if((Split-Path $tmp -Parent) -eq $env:TEMP -and (Split-Path $tmp -Leaf) -match '^edge-setup-tests-[a-f0-9]{32}$'){Remove-Item -LiteralPath $tmp -Recurse -Force}}
Write-Output "PASS: $script:Count setup tests; no installations, account calls or settings changes."
