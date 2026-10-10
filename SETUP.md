# Verified setup

## Short graphical launch

For the Chris Titus-style launch, paste this into ordinary Windows PowerShell:

```powershell
irm https://raw.githubusercontent.com/Namdev90/openai-edge-workbench/main/Run.ps1 | iex
```

Run.ps1 displays setup progress, selects every tool pack, verifies the commit-pinned downstream downloader, and opens the graphical dashboard. It does not exit your parent shell. This short form trusts the current GitHub launcher before execution. The longer command below also independently pins and verifies the initial script. Both use the same application updater and retain GitHub CLI authentication for private downstream reads. A private repository still requires the authenticated command below to retrieve the first script.

## Current public repository

Paste this single line into Windows PowerShell as your normal user:

```powershell
& { $ErrorActionPreference='Stop'; $p=Join-Path $env:TEMP ('Edge-'+[guid]::NewGuid().ToString('N')+'.ps1'); Invoke-WebRequest 'https://raw.githubusercontent.com/Namdev90/openai-edge-workbench/20c323f68c15be6e91ebc4e31f173f581c940c0a/Setup.ps1' -UseBasicParsing -OutFile $p; if ((Get-FileHash $p -Algorithm SHA256).Hash -ine '2360295d3d44f19d5e39ea2f48a774833720ca4d26f9b1ccb1a86c25540cdd04') { throw 'Setup checksum mismatch' }; $old=$env:EDGE_ALL_TOOLS; try { $env:EDGE_ALL_TOOLS='1'; & "$env:SystemRoot\System32\WindowsPowerShell\v1.0\powershell.exe" -NoProfile -STA -ExecutionPolicy Bypass -File $p; if ($LASTEXITCODE -ne 0) { throw 'Setup failed' } } finally { $env:EDGE_ALL_TOOLS=$old } }
```

The initial setup is pinned to reviewed commit `20c323f68c15be6e91ebc4e31f173f581c940c0a` and independently SHA256-checked. It then downloads the newest published Workbench at one immutable commit, checks the complete embedded source, runs offline application tests, and opens the graphical dashboard. The desktop shortcut repeats this published-code update on later launches.

Alternatively, download **OpenAI-Edge-Workbench-Setup.cmd** from the GitHub release and double-click it. This tiny launcher checks the same pinned setup; if GitHub CLI is already signed in it uses authenticated contents downloads instead of exposing a token in a raw URL.

## Private repository

GitHub CLI must be installed. If it is missing, run `winget install --id GitHub.cli --exact --source winget` and open a new PowerShell window. This is an explicit installation prerequisite for private GitHub authentication. Sign in with an account allowed to read the repository, using the following authenticated one-command bootstrap:

```powershell
& { $ErrorActionPreference='Stop'; gh auth login --hostname github.com --web; if ($LASTEXITCODE -ne 0) { throw 'GitHub sign-in failed' }; $m=gh api --hostname github.com 'repos/Namdev90/openai-edge-workbench/contents/Setup.ps1?ref=20c323f68c15be6e91ebc4e31f173f581c940c0a' | ConvertFrom-Json; if ($LASTEXITCODE -ne 0) { throw 'Repository access failed' }; $p=Join-Path $env:TEMP ('Edge-'+[guid]::NewGuid().ToString('N')+'.ps1'); [IO.File]::WriteAllBytes($p,[Convert]::FromBase64String($m.content)); if ((Get-FileHash $p).Hash -ine '2360295d3d44f19d5e39ea2f48a774833720ca4d26f9b1ccb1a86c25540cdd04') { throw 'Setup checksum mismatch' }; $old=$env:EDGE_ALL_TOOLS; try { $env:EDGE_ALL_TOOLS='1'; & "$env:SystemRoot\System32\WindowsPowerShell\v1.0\powershell.exe" -NoProfile -STA -ExecutionPolicy Bypass -File $p; if ($LASTEXITCODE -ne 0) { throw 'Setup failed' } } finally { $env:EDGE_ALL_TOOLS=$old } }
```

The browser sign-in requires your participation. No token needs to be pasted into this chat. After sign-in, the setup CMD and installed desktop shortcut reuse that stored authentication. The installer does not change repository visibility.

## Verification and impact

The exact pinned downloader was fetched from GitHub, its hash checked, and its authenticated download/extraction/test path executed on Windows with NoLaunch. Windows/Linux CI and Windows bootstrap smoke tests passed. Full toolkit installation and account connectivity are established only by the actual installation report.

This command preselects every tool pack, including the .NET daily SDK. Model requests are off by default. Selections remain editable. The dashboard starts installation after a visible 12-second countdown; changing selections or reviewing a feature pauses it. The optional live model test consumes quota only if intentionally selected. Installation approvals/Store sign-in can require your input. No private beta access is promised.

No Git, Python, web framework or coding knowledge is needed beforehand for public setup: the bootstrap handles its dependencies. Private GitHub access requires the account sign-in prerequisite above. Built-in report guidance works without API setup. Optional cloud AI accounts/keys and third-party sign-in remain separate from software installation.

The standalone CMD in the repository contains the complete release snapshot. The setup CMD and desktop shortcut add published-source self-update. Historical installers under legacy/ are preserved as source references and are not executed.
