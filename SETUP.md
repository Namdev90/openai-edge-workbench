# Verified setup

## Current public repository

Paste this single line into Windows PowerShell as your normal user:

```powershell
& { $ErrorActionPreference='Stop'; $p=Join-Path $env:TEMP ('Edge-'+[guid]::NewGuid().ToString('N')+'.ps1'); Invoke-WebRequest 'https://raw.githubusercontent.com/Namdev90/openai-edge-workbench/6ff4e27597fa88255589528bd5fafbf0ed5a4460/Setup.ps1' -UseBasicParsing -OutFile $p; if ((Get-FileHash $p -Algorithm SHA256).Hash -ine '12c84bba8543a9ee822b9519f4fed2314f5349c954c34b966861c24b10eff7b7') { throw 'Setup checksum mismatch' }; powershell.exe -NoProfile -STA -ExecutionPolicy Bypass -File $p }
```

The initial setup is pinned to reviewed commit `6ff4e27597fa88255589528bd5fafbf0ed5a4460` and independently SHA256-checked. It then downloads the newest published Workbench at one immutable commit, checks the complete embedded source, runs offline application tests, and opens the graphical dashboard. The desktop shortcut repeats this published-code update on later launches.

Alternatively, download **OpenAI-Edge-Workbench-Setup.cmd** from the GitHub release and double-click it. This tiny launcher checks the same pinned setup; if GitHub CLI is already signed in it uses authenticated contents downloads instead of exposing a token in a raw URL.

## Private repository

GitHub CLI must be installed. If it is missing, run `winget install --id GitHub.cli --exact --source winget` and open a new PowerShell window. This is an explicit installation prerequisite for private GitHub authentication. Sign in with an account allowed to read the repository, using the following authenticated one-command bootstrap:

```powershell
& { $ErrorActionPreference='Stop'; gh auth login --hostname github.com --web; if ($LASTEXITCODE -ne 0) { throw 'GitHub sign-in failed' }; $m=gh api --hostname github.com 'repos/Namdev90/openai-edge-workbench/contents/Setup.ps1?ref=6ff4e27597fa88255589528bd5fafbf0ed5a4460' | ConvertFrom-Json; if ($LASTEXITCODE -ne 0) { throw 'Repository access failed' }; $p=Join-Path $env:TEMP ('Edge-'+[guid]::NewGuid().ToString('N')+'.ps1'); [IO.File]::WriteAllBytes($p,[Convert]::FromBase64String($m.content)); if ((Get-FileHash $p).Hash -ine '12c84bba8543a9ee822b9519f4fed2314f5349c954c34b966861c24b10eff7b7') { throw 'Setup checksum mismatch' }; powershell.exe -NoProfile -STA -ExecutionPolicy Bypass -File $p }
```

The browser sign-in requires your participation. No token needs to be pasted into this chat. After sign-in, the setup CMD and installed desktop shortcut reuse that stored authentication. The installer does not change repository visibility.

## Verification and impact

The exact pinned downloader was fetched from GitHub, its hash checked, and its authenticated download/extraction/test path executed on Windows with NoLaunch. Windows/Linux CI and Windows bootstrap smoke tests passed. Full toolkit installation and account connectivity are established only by the actual installation report.

The dashboard starts installation after a visible 12-second countdown; changing selections pauses it. The optional live model test consumes quota. Installation approvals/Store sign-in can require your input. No private beta access is promised.

The standalone CMD in the repository contains the complete release snapshot. The setup CMD and desktop shortcut add published-source self-update. Historical installers under legacy/ are preserved as source references and are not executed.
