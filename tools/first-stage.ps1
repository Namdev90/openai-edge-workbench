$ErrorActionPreference='Stop';$ProgressPreference='SilentlyContinue'
Import-Module ([IO.Path]::Combine($PSHOME,'Modules/Microsoft.PowerShell.Management/Microsoft.PowerShell.Management.psd1')) -ErrorAction Stop
Import-Module ([IO.Path]::Combine($PSHOME,'Modules/Microsoft.PowerShell.Utility/Microsoft.PowerShell.Utility.psd1')) -ErrorAction Stop
Import-Module ([IO.Path]::Combine($PSHOME,'Modules/Microsoft.PowerShell.Security/Microsoft.PowerShell.Security.psd1')) -ErrorAction Stop
$p=Join-Path $env:TEMP ('Edge-'+[guid]::NewGuid().ToString('N')+'.ps1')
try {
 [Net.ServicePointManager]::SecurityProtocol=[Net.ServicePointManager]::SecurityProtocol -bor [Net.SecurityProtocolType]::Tls12
 $gh=Get-Command gh.exe -ErrorAction SilentlyContinue;$authenticated=$false
 if($gh){$prior=$ErrorActionPreference;try{$ErrorActionPreference='Continue';& $gh.Source auth status --hostname github.com *> $null;$authenticated=($LASTEXITCODE -eq 0)}finally{$ErrorActionPreference=$prior}}
 if($authenticated){
  $json=& $gh.Source api --hostname github.com 'repos/Namdev90/openai-edge-workbench/contents/Setup.ps1?ref=20c323f68c15be6e91ebc4e31f173f581c940c0a' 2>$null
  if($LASTEXITCODE -ne 0){throw 'GitHub repository access failed. Check gh auth status and repository permissions.'}
  $meta=($json -join "`n")|ConvertFrom-Json
  if($meta.encoding -ne 'base64' -or $meta.size -gt 1MB){throw 'Invalid GitHub setup response.'}
  [IO.File]::WriteAllBytes($p,[Convert]::FromBase64String([string]$meta.content))
 }else{Invoke-WebRequest 'https://raw.githubusercontent.com/Namdev90/openai-edge-workbench/20c323f68c15be6e91ebc4e31f173f581c940c0a/Setup.ps1' -UseBasicParsing -OutFile $p -TimeoutSec 90}
 $alg=[Security.Cryptography.SHA256]::Create();try{$hash=([BitConverter]::ToString($alg.ComputeHash([IO.File]::ReadAllBytes($p)))).Replace('-','').ToLowerInvariant()}finally{$alg.Dispose()};if($hash -ne '2360295d3d44f19d5e39ea2f48a774833720ca4d26f9b1ccb1a86c25540cdd04'){throw 'Setup checksum mismatch.'}
 $a=@{}
 if($env:EDGE_NO_LAUNCH -eq '1'){$a.NoLaunch=$true;$a.NoShortcut=$true}
 if($env:EDGE_ROOT){$a.Root=$env:EDGE_ROOT}
 & $p @a
 exit 0
}catch{Write-Host ('Setup failed: '+$_.Exception.Message+' For private access install GitHub CLI and run gh auth login --hostname github.com --web.') -ForegroundColor Red;exit 1}
finally{if(Test-Path -LiteralPath $p){Remove-Item -LiteralPath $p -Force}}
