@echo off
setlocal
powershell.exe -NoProfile -STA -ExecutionPolicy Bypass -Command "$p=Join-Path $env:TEMP ('namu-ai-edge-'+[guid]::NewGuid().ToString('N')+'.ps1'); try {Invoke-WebRequest 'https://raw.githubusercontent.com/Namdev90/amreye-ai/namu-ai-edge/tools/namu-ai-edge/install.ps1' -UseBasicParsing -OutFile $p -ErrorAction Stop; & $p} catch {Write-Host $_ -ForegroundColor Red; exit 1} finally {Remove-Item -LiteralPath $p -ErrorAction SilentlyContinue}"
if errorlevel 1 pause
