# Namu AI Edge bootstrap. Downloads one pinned GitHub commit; verifies every source file SHA256,
# runs included tests, atomically switches versions, then launches the Windows GUI.
[CmdletBinding()]
param([switch]$Scheduled,[switch]$AuditOnly,[switch]$NoLaunch)
$ErrorActionPreference='Stop';$ProgressPreference='SilentlyContinue'
if($env:OS -ne 'Windows_NT'){throw 'Windows 10/11 is required.'}
$root=Join-Path $env:LOCALAPPDATA 'Namu-AI-Edge'
$repo='Namdev90/amreye-ai';$branch='namu-ai-edge';$prefix='tools/namu-ai-edge'
[Net.ServicePointManager]::SecurityProtocol=[Net.ServicePointManager]::SecurityProtocol -bor [Net.SecurityProtocolType]::Tls12
Add-Type -AssemblyName System.Windows.Forms
[Windows.Forms.Application]::EnableVisualStyles()
$form=New-Object Windows.Forms.Form;$form.Text='Namu AI Edge - code update';$form.Width=570;$form.Height=175;$form.StartPosition='CenterScreen'
$label=New-Object Windows.Forms.Label;$label.Dock='Fill';$label.Padding=New-Object Windows.Forms.Padding(18);$label.Text='Checking the tool code on GitHub...';$form.Controls.Add($label)
$form.Show();[Windows.Forms.Application]::DoEvents()
function Status([string]$Text){$label.Text=$Text;[Windows.Forms.Application]::DoEvents();Write-Host $Text}
function Atomic([string]$Path,[string]$Text){$t=$Path+'.tmp';[IO.File]::WriteAllText($t,$Text,[Text.UTF8Encoding]::new($false));if(Test-Path $Path){[IO.File]::Replace($t,$Path,[NullString]::Value)}else{[IO.File]::Move($t,$Path)}}
function Test-Build([string]$Directory){
 $ps=Join-Path $env:WINDIR 'System32/WindowsPowerShell/v1.0/powershell.exe'
 $output=& $ps -NoProfile -ExecutionPolicy Bypass -File (Join-Path $Directory 'tests/Test-Edge.ps1') 2>&1 | Out-String
 if($LASTEXITCODE -ne 0){throw ('Downloaded code failed its self-tests: '+$output)}
 return $output.Trim()
}
$lock=$null;$selected='';$status=[ordered]@{repository=$repo;branch=$branch;utc=[DateTime]::UtcNow.ToString('o');state='NOT_CHECKED';commit='';tests=''}
try{
 [void](New-Item -ItemType Directory -Path $root -Force)
 if((Get-Item $root -Force).Attributes -band [IO.FileAttributes]::ReparsePoint){throw 'Installation root is a junction/symlink; choose a regular local directory.'}
 # Backups and diagnostic files remain local and accessible only to this user, SYSTEM and Administrators.
 $acl=New-Object Security.AccessControl.DirectorySecurity
 $acl.SetAccessRuleProtection($true,$false)
 foreach($sid in @([Security.Principal.WindowsIdentity]::GetCurrent().User.Value,'S-1-5-18','S-1-5-32-544')){
  $identity=New-Object Security.Principal.SecurityIdentifier($sid)
  $rule=New-Object Security.AccessControl.FileSystemAccessRule($identity,'FullControl','ContainerInherit, ObjectInherit','None','Allow')
  $acl.AddAccessRule($rule)
 }
 Set-Acl -LiteralPath $root -AclObject $acl
 $lock=[IO.File]::Open((Join-Path $root 'update.lock'),[IO.FileMode]::OpenOrCreate,[IO.FileAccess]::ReadWrite,[IO.FileShare]::None)
 $pointer=Join-Path $root 'current-build.txt'
 if(Test-Path $pointer){$old=(Get-Content $pointer -Raw).Trim();if($old -match '^[a-f0-9]{40}$'){$selected=Join-Path $root "versions/$old"}}
 try{
  $commit=Invoke-RestMethod "https://api.github.com/repos/$repo/commits/$branch" -Headers @{'User-Agent'='Namu-AI-Edge'} -TimeoutSec 45
  $sha=[string]$commit.sha;if($sha -notmatch '^[a-f0-9]{40}$'){throw 'Invalid GitHub commit response.'}
  $base="https://raw.githubusercontent.com/$repo/$sha/$prefix"
  $manifest=Invoke-RestMethod "$base/release.json" -TimeoutSec 45
  if($manifest.schema -ne 2 -or !$manifest.files){throw 'Unsupported release manifest.'}
  $required=@('Edge.ps1','install.ps1','catalog.json','tests/Test-Edge.ps1')
  foreach($name in $required){if(!($manifest.files.PSObject.Properties.Name -contains $name)){throw "Missing required manifest entry: $name"}}
  $destination=Join-Path $root "versions/$sha"
  if(!(Test-Path (Join-Path $destination '.validated'))){
   Status "New code: $($manifest.version). Downloading and checking source files..."
   $stage=Join-Path $root ('.stage-'+[guid]::NewGuid().ToString('N'));[void](New-Item -ItemType Directory -Path $stage)
   $size=0
   foreach($entry in $manifest.files.PSObject.Properties){
    $name=$entry.Name;$hash=[string]$entry.Value
    if($name -notmatch '^(?:[A-Za-z0-9_.-]+/)*[A-Za-z0-9_.-]+\.(?:ps1|json|md|py)$' -or $name -match '(^|/)\.\.(/|$)' -or $hash -notmatch '^[A-Fa-f0-9]{64}$'){throw 'Unsafe manifest entry.'}
    $target=Join-Path $stage $name
    [void](New-Item -ItemType Directory -Path (Split-Path $target -Parent) -Force)
    Invoke-WebRequest "$base/$name" -UseBasicParsing -OutFile $target -TimeoutSec 90
    $size+=(Get-Item $target).Length
    if($size -gt 20MB -or (Get-FileHash $target -Algorithm SHA256).Hash -ine $hash){throw "Source checksum or size check failed: $name"}
   }
   Status 'Checking PowerShell syntax and regression tests before activating this build...'
   $test=Test-Build $stage
   [void](New-Item -ItemType Directory -Path (Split-Path $destination -Parent) -Force)
   if(Test-Path $destination){throw 'Incomplete version directory exists. Remove only that failed tool-owned directory before retrying.'}
   Move-Item -LiteralPath $stage -Destination $destination
   Atomic (Join-Path $destination '.validated') $test
  }else{$test=Test-Build $destination}
  Atomic $pointer $sha
  $selected=$destination
  $status.state='VERIFIED_CURRENT_COMMIT';$status.commit=$sha;$status.tests=$test
  # The loader itself is updated too; the running invocation finishes with its already-parsed code.
  $newLoader=[IO.File]::ReadAllText((Join-Path $selected 'install.ps1'))
  Atomic (Join-Path $root 'install.ps1') $newLoader
 }catch{
  $status.state='UPDATE_FAILED_USING_PREVIOUS_IF_VALID';$status.error=($_.Exception.Message -replace [regex]::Escape($env:USERPROFILE),'%USERPROFILE%')
  if(!$selected -or !(Test-Path (Join-Path $selected 'Edge.ps1'))){throw}
  $status.tests=Test-Build $selected;$status.commit=Split-Path $selected -Leaf
  Status 'GitHub update failed. The previously installed, tested tool remains selected. The report records this failure.'
 }
 Atomic (Join-Path $root 'update-status.json') ($status|ConvertTo-Json -Depth 5)
 $launcher=Join-Path $root 'Start-Namu-AI-Edge.cmd'
 $text="@echo off`r`npowershell.exe -NoProfile -STA -ExecutionPolicy Bypass -File `"%LOCALAPPDATA%\Namu-AI-Edge\install.ps1`"`r`n"
 Atomic $launcher $text
 $desktop=[Environment]::GetFolderPath('Desktop')
 if($desktop -and (Test-Path $desktop)){
  $shell=New-Object -ComObject WScript.Shell;$shortcut=$shell.CreateShortcut((Join-Path $desktop 'Namu AI Edge.lnk'));$shortcut.TargetPath=$launcher;$shortcut.WorkingDirectory=$root;$shortcut.Description='Update Namu AI Edge, then open the graphical maintenance tool';$shortcut.Save()
 }
 Status 'Code checks complete. Opening the live maintenance dashboard...'
}catch{
 $message=$_.Exception.Message -replace [regex]::Escape($env:USERPROFILE),'%USERPROFILE%'
 if(Test-Path $root){[IO.File]::WriteAllText((Join-Path $root 'Bootstrap-Error.txt'),$message)}
 [void][Windows.Forms.MessageBox]::Show("Startup failed. No success is claimed.`r`n$message`r`nLog: %LOCALAPPDATA%\Namu-AI-Edge\Bootstrap-Error.txt",'Namu AI Edge')
 throw
}finally{if($lock){$lock.Dispose()};$form.Close();$form.Dispose()}
if(!$NoLaunch){
 $engine=Join-Path $selected 'Edge.ps1'
 $params=@{Root=$root};if($Scheduled){$params.Scheduled=$true};if($AuditOnly){$params.AuditOnly=$true}
 & $engine @params
}
