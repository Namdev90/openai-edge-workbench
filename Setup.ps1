# Unofficial Windows installer for OpenAI Edge Workbench.
# Resolves a GitHub commit, verifies the reviewed launcher SHA256 and executes it.
[CmdletBinding()]
param()
$ErrorActionPreference='Stop'
$ProgressPreference='SilentlyContinue'
if ($env:OS -ne 'Windows_NT') { throw 'Windows 10 or 11 required.' }
[Net.ServicePointManager]::SecurityProtocol = [Net.ServicePointManager]::SecurityProtocol -bor [Net.SecurityProtocolType]::Tls12
$repo='Namdev90/openai-edge-workbench'
$expected='6a42578d7330e8baf82ea93c5cb23120cb7c76210ed43947e0fe2f0e092db014'
$commit=(Invoke-RestMethod "https://api.github.com/repos/$repo/commits/main" -Headers @{'User-Agent'='OpenAI-Edge-Workbench'} -TimeoutSec 30).sha
if ($commit -notmatch '^[a-f0-9]{40}$') { throw 'Unexpected GitHub commit identifier.' }
$dest=Join-Path $env:TEMP ('OpenAI-Edge-Workbench-'+$commit.Substring(0,12)+'.cmd')
Invoke-WebRequest "https://raw.githubusercontent.com/$repo/$commit/OpenAI-Edge-Workbench.cmd" -UseBasicParsing -OutFile $dest -TimeoutSec 90
$actual=(Get-FileHash -LiteralPath $dest -Algorithm SHA256).Hash.ToLowerInvariant()
if ($actual -ne $expected) { Remove-Item -LiteralPath $dest -Force -ErrorAction SilentlyContinue; throw 'Launcher checksum mismatch. New release requires review before execution.' }
Write-Host "Downloaded and verified launcher from GitHub commit $commit"
& $dest
exit $LASTEXITCODE
