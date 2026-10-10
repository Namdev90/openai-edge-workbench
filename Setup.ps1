# OpenAI Edge Workbench: commit-resolved, checksum-verified GitHub updater.
[CmdletBinding()]
param([switch]$Library,[switch]$VerifyOnly,[switch]$NoLaunch,[switch]$NoShortcut,[switch]$Offline,
 [string]$Commit,[string]$Root=([IO.Path]::Combine($env:LOCALAPPDATA,'OpenAI-Edge-Workbench')))
$ErrorActionPreference='Stop';$ProgressPreference='SilentlyContinue'
Import-Module ([IO.Path]::Combine($PSHOME,'Modules/Microsoft.PowerShell.Management/Microsoft.PowerShell.Management.psd1')) -ErrorAction Stop
Import-Module ([IO.Path]::Combine($PSHOME,'Modules/Microsoft.PowerShell.Utility/Microsoft.PowerShell.Utility.psd1')) -ErrorAction Stop
Import-Module ([IO.Path]::Combine($PSHOME,'Modules/Microsoft.PowerShell.Security/Microsoft.PowerShell.Security.psd1')) -ErrorAction Stop
$script:Repository='Namdev90/openai-edge-workbench';$script:UseGh=$false
function Test-GhAuthenticated([string]$Command){
 $prior=$ErrorActionPreference
 try{$ErrorActionPreference='Continue';& $Command auth status --hostname github.com *> $null;return ($LASTEXITCODE -eq 0)}
 finally{$ErrorActionPreference=$prior}
}
function Write-SetupFile([string]$Path,[string]$Text){
 $tmp=$Path+'.'+[guid]::NewGuid().ToString('N')+'.tmp'
 [IO.File]::WriteAllText($tmp,$Text,[Text.UTF8Encoding]::new($false))
 if(Test-Path -LiteralPath $Path){[IO.File]::Replace($tmp,$Path,[NullString]::Value)}else{[IO.File]::Move($tmp,$Path)}
}
function Assert-SetupPath([string]$Path){
 $cursor=[IO.Path]::GetFullPath($Path)
 while($cursor){
  if((Test-Path -LiteralPath $cursor) -and ((Get-Item -LiteralPath $cursor -Force).Attributes -band [IO.FileAttributes]::ReparsePoint)){throw 'Refusing a junction/symlink in the setup path.'}
  $parent=Split-Path $cursor -Parent;if($parent -eq $cursor){break};$cursor=$parent
 }
}
function Get-SetupJson([string]$Endpoint){
 if($Endpoint -notlike "repos/$script:Repository/*"){throw 'Setup request escaped the standalone repository.'}
 if($script:UseGh){
  $result=& $script:Gh api --hostname github.com $Endpoint 2>$null
  if($LASTEXITCODE -ne 0){throw 'Authenticated GitHub read failed. Run gh auth status and check repository read access.'}
  return (($result -join "`n")|ConvertFrom-Json)
 }
 try{return Invoke-RestMethod "https://api.github.com/$Endpoint" -Headers @{'User-Agent'='OpenAI-Edge-Workbench';Accept='application/vnd.github+json'} -TimeoutSec 45}
 catch{throw 'GitHub read failed. For private access install GitHub CLI and run gh auth login --hostname github.com --web with an account allowed to read this repository. Public API/network failures may require a retry.'}
}
function Get-SetupDownload([string]$Name,[string]$Sha,[string]$Destination){
 if($Sha -notmatch '^[a-f0-9]{40}$' -or $Name -notmatch '^[A-Za-z0-9_.-]+$'){throw 'Unsafe download identity.'}
 $meta=Get-SetupJson "repos/$script:Repository/contents/${Name}?ref=$Sha"
 if($meta.type -ne 'file' -or $meta.encoding -ne 'base64' -or $meta.size -gt 1MB){throw 'Unsupported source file.'}
 $bytes=[Convert]::FromBase64String([string]$meta.content)
 if($bytes.Length -ne $meta.size){throw 'Source file size mismatch.'}
 [IO.File]::WriteAllBytes($Destination,$bytes)
}
function Assert-SetupPayload([string]$Launcher,$Manifest){
 if($Manifest.schema -ne 1 -or [string]$Manifest.launcherSha256 -notmatch '^[a-f0-9]{64}$' -or [string]$Manifest.payloadSha256 -notmatch '^[a-f0-9]{64}$' -or !$Manifest.sourceFiles){throw 'Invalid release manifest.'}
 foreach($required in @('bootstrap.ps1','app.py','engine.py','index.html','style.css','app.js','tests/test_migration_security.py')){if(!($Manifest.sourceFiles.PSObject.Properties.Name -ccontains $required)){throw "Missing required source: $required"}}
 if((Get-FileHash -LiteralPath $Launcher -Algorithm SHA256).Hash -ine $Manifest.launcherSha256){throw 'Launcher checksum mismatch.'}
 $text=[IO.File]::ReadAllText($Launcher,[Text.Encoding]::ASCII);$mark="`r`n::EDGE_PAYLOAD`r`n"
 $parts=$text.Split(@($mark),[StringSplitOptions]::None)
 if($parts.Count -ne 2){throw 'Invalid launcher payload marker.'}
 $bytes=[Convert]::FromBase64String($parts[1]);$alg=[Security.Cryptography.SHA256]::Create()
 try{$hash=([BitConverter]::ToString($alg.ComputeHash($bytes))).Replace('-','').ToLowerInvariant()}finally{$alg.Dispose()}
 if($hash -ne $Manifest.payloadSha256){throw 'Embedded payload checksum mismatch.'}
 Add-Type -AssemblyName System.IO.Compression
 $memory=[IO.MemoryStream]::new($bytes);$zip=[IO.Compression.ZipArchive]::new($memory,[IO.Compression.ZipArchiveMode]::Read)
 try{
  if($zip.Entries.Count -ne @($Manifest.sourceFiles.PSObject.Properties).Count -or $zip.Entries.Count -gt 100){throw 'Payload source count mismatch.'}
  $seen=@{};$total=0
  foreach($entry in $zip.Entries){
   $name=$entry.FullName
   if($name -notmatch '^(?:[A-Za-z0-9_-][A-Za-z0-9_.-]*/)*[A-Za-z0-9_-][A-Za-z0-9_.-]*\.(?:ps1|py|js|html|css|md)$' -or $name -match '(^|/)\.\.(/|$)' -or $seen.ContainsKey($name)){throw 'Unsafe or duplicate embedded source path.'}
   $seen[$name]=$true;$total+=$entry.Length
   if($total -gt 20MB){throw 'Payload exceeds size budget.'}
   $stream=$entry.Open();$sha=[Security.Cryptography.SHA256]::Create()
   try{$digest=([BitConverter]::ToString($sha.ComputeHash($stream))).Replace('-','').ToLowerInvariant()}finally{$stream.Dispose();$sha.Dispose()}
   if($digest -ne [string]$Manifest.sourceFiles.$name){throw "Embedded source mismatch: $name"}
  }
 }finally{$zip.Dispose();$memory.Dispose()}
}
function Set-SetupPrivateAccess([string]$Path){
 Assert-SetupPath $Path
 $directory=[IO.DirectoryInfo]::new($Path)
 # Load only the existing DACL, then persist only modified access rules. A new
 # descriptor passed to Set-Acl can try to replace owner/audit sections and
 # require SeSecurityPrivilege on an already-installed directory.
 if($PSVersionTable.PSEdition -eq 'Core'){
  $acl=[IO.FileSystemAclExtensions]::GetAccessControl($directory,[Security.AccessControl.AccessControlSections]::Access)
 }else{$acl=$directory.GetAccessControl([Security.AccessControl.AccessControlSections]::Access)}
 $acl.SetAccessRuleProtection($true,$false)
 foreach($rule in @($acl.GetAccessRules($true,$false,[Security.Principal.SecurityIdentifier]))){$acl.RemoveAccessRuleSpecific($rule)}
 foreach($sid in @([Security.Principal.WindowsIdentity]::GetCurrent().User.Value,'S-1-5-18','S-1-5-32-544')){
  $identity=[Security.Principal.SecurityIdentifier]::new($sid)
  $rule=[Security.AccessControl.FileSystemAccessRule]::new($identity,'FullControl','ContainerInherit, ObjectInherit','None','Allow')
  [void]$acl.AddAccessRule($rule)
 }
 if($PSVersionTable.PSEdition -eq 'Core'){
  [IO.FileSystemAclExtensions]::SetAccessControl($directory,$acl)
 }else{$directory.SetAccessControl($acl)}
}
if($Library){return}
if($env:OS -ne 'Windows_NT'){throw 'Windows 10/11 is required.'}
if($Commit -and $Commit -notmatch '^[a-f0-9]{40}$'){throw 'Invalid requested commit.'}
[Net.ServicePointManager]::SecurityProtocol=[Net.ServicePointManager]::SecurityProtocol -bor [Net.SecurityProtocolType]::Tls12
$lock=$null;$selected='';$stage=''
try{
 Assert-SetupPath $Root;[void](New-Item -ItemType Directory -Path $Root -Force)
 Set-SetupPrivateAccess $Root
 $lock=[IO.File]::Open((Join-Path $Root 'setup.lock'),'OpenOrCreate','ReadWrite','None')
 $ghCommand=Get-Command gh.exe -ErrorAction SilentlyContinue
 if($ghCommand){$script:Gh=$ghCommand.Source;$script:UseGh=Test-GhAuthenticated $script:Gh}
 $pointer=Join-Path $Root 'setup-current.json';Assert-SetupPath $pointer
 $current=$null;if(Test-Path -LiteralPath $pointer){$current=Get-Content $pointer -Raw|ConvertFrom-Json}
 $status=[ordered]@{repository=$script:Repository;utc=[DateTime]::UtcNow.ToString('o');state='NOT_CHECKED';commit='';authentication=$(if($script:UseGh){'GitHub CLI stored authentication'}else{'public API'})}
 try{
  if($Offline){throw 'Offline launch requested.'}
  $sha=$Commit;if(!$sha){$head=Get-SetupJson "repos/$script:Repository/commits/main";$sha=[string]$head.sha}
  if($sha -notmatch '^[a-f0-9]{40}$'){throw 'Invalid GitHub commit.'}
  $stage=Join-Path $Root ('.setup-stage-'+[guid]::NewGuid().ToString('N'));[void](New-Item -ItemType Directory -Path $stage)
  Get-SetupDownload 'release.json' $sha (Join-Path $stage 'release.json')
  Get-SetupDownload 'OpenAI-Edge-Workbench.cmd' $sha (Join-Path $stage 'OpenAI-Edge-Workbench.cmd')
  Get-SetupDownload 'Setup.ps1' $sha (Join-Path $stage 'Setup.ps1')
  $manifest=Get-Content (Join-Path $stage 'release.json') -Raw|ConvertFrom-Json
  Assert-SetupPayload (Join-Path $stage 'OpenAI-Edge-Workbench.cmd') $manifest
  if((Get-FileHash (Join-Path $stage 'Setup.ps1')).Hash -ine $manifest.setupSha256){throw 'Updated setup checksum mismatch.'}
  $destination=Join-Path $Root ('setup/'+$sha+'-'+[guid]::NewGuid().ToString('N'));Assert-SetupPath $destination
  [void](New-Item -ItemType Directory -Path (Split-Path $destination -Parent) -Force);Move-Item -LiteralPath $stage -Destination $destination;$stage=''
  $selected=$destination;$status.state='VERIFIED_GITHUB_COMMIT';$status.commit=$sha
  Write-SetupFile $pointer (@{directory=(Split-Path $destination -Leaf);commit=$sha}|ConvertTo-Json)
 }catch{
  if($Commit -or !$current -or [string]$current.directory -notmatch '^[a-f0-9]{40}-[a-f0-9]{32}$'){throw}
  $selected=Join-Path $Root ('setup/'+$current.directory);Assert-SetupPath $selected
  $manifest=Get-Content (Join-Path $selected 'release.json') -Raw|ConvertFrom-Json
  Assert-SetupPayload (Join-Path $selected 'OpenAI-Edge-Workbench.cmd') $manifest
  $status.state='UPDATE_FAILED_VERIFIED_CACHE';$status.commit=$current.commit;$status.error=$_.Exception.Message
  Write-Warning 'GitHub update unavailable. Verified cached payload remains available; update failure is recorded.'
 }
 Write-SetupFile (Join-Path $Root 'Setup-Status.json') ($status|ConvertTo-Json -Depth 5)
 if(!$VerifyOnly){
  if((Get-FileHash (Join-Path $selected 'Setup.ps1')).Hash -ine $manifest.setupSha256){throw 'Cached setup checksum mismatch.'}
  Write-SetupFile (Join-Path $Root 'Setup.ps1') ([IO.File]::ReadAllText((Join-Path $selected 'Setup.ps1')))
  if(!$NoShortcut){
   $shell=New-Object -ComObject WScript.Shell;$link=$shell.CreateShortcut((Join-Path ([Environment]::GetFolderPath('Desktop')) 'OpenAI Edge Workbench.lnk'))
   $link.TargetPath=Join-Path $env:WINDIR 'System32/WindowsPowerShell/v1.0/powershell.exe';$link.Arguments='-NoProfile -STA -ExecutionPolicy Bypass -File "'+(Join-Path $Root 'Setup.ps1')+'"';$link.WorkingDirectory=$Root;$link.Save()
  }
 }
 Write-Host "Verified GitHub commit $($status.commit) and embedded source hashes."
}finally{
 try{if($stage -and (Test-Path -LiteralPath $stage)){Assert-SetupPath $stage;if((Split-Path $stage -Parent) -ne $Root -or (Split-Path $stage -Leaf) -notmatch '^\.setup-stage-[a-f0-9]{32}$'){throw 'Unsafe setup staging cleanup.'};Remove-Item -LiteralPath $stage -Recurse -Force}}finally{if($lock){$lock.Dispose()}}
}
if(!$VerifyOnly){
 $oldRoot=$env:EDGE_ROOT;$oldNoLaunch=$env:EDGE_NO_LAUNCH
 try{$env:EDGE_ROOT=$Root;$env:EDGE_NO_LAUNCH=$(if($NoLaunch){'1'}else{'0'});& (Join-Path $selected 'OpenAI-Edge-Workbench.cmd');if($LASTEXITCODE -ne 0){throw 'Application bootstrap failed; inspect Bootstrap-Diagnostic.txt in the Workbench folder.'}}
 finally{$env:EDGE_ROOT=$oldRoot;$env:EDGE_NO_LAUNCH=$oldNoLaunch}
}
