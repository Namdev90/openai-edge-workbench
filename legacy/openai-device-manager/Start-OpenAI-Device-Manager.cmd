@echo off
setlocal
title OpenAI Device Manager - Preview
echo Opening preview-first OpenAI Device Manager...
powershell.exe -NoProfile -ExecutionPolicy Bypass -STA -Command "$ErrorActionPreference='Stop'; try { $f=Join-Path $env:LOCALAPPDATA 'Namu\OpenAI-Device-Manager\Bootstrap.ps1'; if (!(Test-Path -LiteralPath $f)) { $f=Join-Path $env:TEMP ('OpenAI-Device-Manager-'+[guid]::NewGuid().ToString('N')+'.ps1'); [Net.ServicePointManager]::SecurityProtocol=[Net.SecurityProtocolType]::Tls12; Invoke-WebRequest 'https://raw.githubusercontent.com/Namdev90/amreye-ai/d09e36188b97e876abdda0857ca41f1cede93962/Install.ps1' -UseBasicParsing -TimeoutSec 90 -OutFile $f; if ((Get-FileHash -LiteralPath $f -Algorithm SHA256).Hash -ne '1f76d4bb65a995408cb9ec3cee1bbd5d6ad90a0ff1c89091a577c00834ba8f46') { Remove-Item -LiteralPath $f -Force; throw 'Bootstrap integrity check failed.' } }; & powershell.exe -NoProfile -ExecutionPolicy Bypass -STA -File $f; exit $LASTEXITCODE } catch { Write-Host ('LAUNCH FAILED: '+$_.Exception.Message) -ForegroundColor Red; exit 1 }"
if errorlevel 1 (
  echo.
  echo Startup failed. Copy the error above, or check Bootstrap-Failure.txt in the manager folder.
  pause
  exit /b 1
)
endlocal
