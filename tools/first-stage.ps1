$ErrorActionPreference='Stop';$ProgressPreference='SilentlyContinue'
Import-Module (Join-Path $PSHOME 'Modules/Microsoft.PowerShell.Utility/Microsoft.PowerShell.Utility.psd1') -ErrorAction Stop
Import-Module (Join-Path $PSHOME 'Modules/Microsoft.PowerShell.Security/Microsoft.PowerShell.Security.psd1') -ErrorAction Stop
$p=Join-Path $env:TEMP ('Edge-'+[guid]::NewGuid().ToString('N')+'.ps1')
try {
 [Net.ServicePointManager]::SecurityProtocol=[Net.ServicePointManager]::SecurityProtocol -bor [Net.SecurityProtocolType]::Tls12
 $gh=Get-Command gh.exe -ErrorAction SilentlyContinue;$authenticated=$false
 if($gh){$prior=$ErrorActionPreference;try{$ErrorActionPreference='Continue';& $gh.Source auth status --hostname github.com *> $null;$authenticated=($LASTEXITCODE -eq 0)}finally{$ErrorActionPreference=$prior}}
 if($authenticated){
  $json=& $gh.Source api --hostname github.com 'repos/Namdev90/openai-edge-workbench/contents/Setup.ps1?ref=ee8ce41e532e8dc3d5fc5005c01aeaadc89e8018' 2>$null
  if($LASTEXITCODE -ne 0){throw 'GitHub repository access failed. Check gh auth status and repository permissions.'}
  $meta=($json -join "`n")|ConvertFrom-Json
  if($meta.encoding -ne 'base64' -or $meta.size -gt 1MB){throw 'Invalid GitHub setup response.'}
  [IO.File]::WriteAllBytes($p,[Convert]::FromBase64String([string]$meta.content))
 }else{Invoke-WebRequest 'https://raw.githubusercontent.com/Namdev90/openai-edge-workbench/ee8ce41e532e8dc3d5fc5005c01aeaadc89e8018/Setup.ps1' -UseBasicParsing -OutFile $p -TimeoutSec 90}
 $alg=[Security.Cryptography.SHA256]::Create();try{$hash=([BitConverter]::ToString($alg.ComputeHash([IO.File]::ReadAllBytes($p)))).Replace('-','').ToLowerInvariant()}finally{$alg.Dispose()};if($hash -ne '791ddd5f0a16a2f577b211b1b9449ff66ab87d4728767496ba79b751d9efc9aa'){throw 'Setup checksum mismatch.'}
 $a=@{}
 if($env:EDGE_NO_LAUNCH -eq '1'){$a.NoLaunch=$true;$a.NoShortcut=$true}
 if($env:EDGE_ROOT){$a.Root=$env:EDGE_ROOT}
 & $p @a
 exit 0
}catch{Write-Host ('Setup failed: '+$_.Exception.Message+' For private access install GitHub CLI and run gh auth login --hostname github.com --web.') -ForegroundColor Red;exit 1}
finally{if(Test-Path -LiteralPath $p){Remove-Item -LiteralPath $p -Force}}
