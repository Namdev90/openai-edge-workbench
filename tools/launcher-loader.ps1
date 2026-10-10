# Readable source of the CMD extraction loader. Packaged by build_release.py.
$ErrorActionPreference='Stop';$ProgressPreference='SilentlyContinue'
Import-Module ([IO.Path]::Combine($PSHOME,'Modules/Microsoft.PowerShell.Management/Microsoft.PowerShell.Management.psd1')) -ErrorAction Stop
Import-Module ([IO.Path]::Combine($PSHOME,'Modules/Microsoft.PowerShell.Utility/Microsoft.PowerShell.Utility.psd1')) -ErrorAction Stop
Import-Module ([IO.Path]::Combine($PSHOME,'Modules/Microsoft.PowerShell.Security/Microsoft.PowerShell.Security.psd1')) -ErrorAction Stop
$root=if($env:EDGE_ROOT){$env:EDGE_ROOT}else{Join-Path $env:LOCALAPPDATA 'OpenAI-Edge-Workbench'}
function Regular([string]$p){
 $p=[IO.Path]::GetFullPath($p)
 while($p){if((Test-Path -LiteralPath $p) -and ((Get-Item -LiteralPath $p -Force).Attributes -band [IO.FileAttributes]::ReparsePoint)){throw 'Refusing a junction/symlink in the application path.'};$parent=Split-Path $p -Parent;if($parent -eq $p){break};$p=$parent}
}
try{
 Regular $root
 $text=[IO.File]::ReadAllText($env:EDGE_SELF,[Text.Encoding]::ASCII);$mark="`r`n::EDGE_PAYLOAD`r`n"
 $parts=$text.Split(@($mark),[StringSplitOptions]::None);if($parts.Count -ne 2){throw 'Payload marker mismatch.'}
 $bytes=[Convert]::FromBase64String($parts[1]);$alg=[Security.Cryptography.SHA256]::Create()
 try{$hash=([BitConverter]::ToString($alg.ComputeHash($bytes))).Replace('-','').ToLowerInvariant()}finally{$alg.Dispose()}
 if($hash -ne '__PAYLOAD_SHA256__'){throw 'Payload checksum mismatch.'}
 $parent=Join-Path $root 'app';Regular $parent;[void](New-Item -ItemType Directory -Path $parent -Force)
 $app=Join-Path $parent ('__RELEASE_VERSION__-'+$hash.Substring(0,12)+'-'+[guid]::NewGuid().ToString('N'))
 $zip=$app+'.zip';[IO.File]::WriteAllBytes($zip,$bytes)
 # Every launch extracts fresh verified bytes; no trust in a cached marker file.
 Add-Type -AssemblyName System.IO.Compression.FileSystem
 $archive=[IO.Compression.ZipFile]::OpenRead($zip)
 try{foreach($entry in $archive.Entries){if($entry.FullName -match '(^|/)\.\.(/|$)|[:\\]' -or $entry.FullName.StartsWith('/')){throw 'Unsafe embedded path.'}}}finally{$archive.Dispose()}
 Expand-Archive -LiteralPath $zip -DestinationPath $app;Remove-Item -LiteralPath $zip -Force
 & (Join-Path $app 'bootstrap.ps1') -Root $root -NoLaunch:($env:EDGE_NO_LAUNCH -eq '1')
 exit $LASTEXITCODE
}catch{
 Write-Host ('Launcher failed: '+$_.Exception.Message) -ForegroundColor Red
 exit 1
}
