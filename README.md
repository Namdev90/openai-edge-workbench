# OpenAI Edge Workbench

Unofficial Windows GUI for auditing and updating locally installed ChatGPT/Codex development tools, supported prerelease runtimes, SDKs and related utilities. This project is **completely separate from AMReye.AI** and is not an OpenAI product.

## One-command install (Windows PowerShell)

Paste this entire line into normal Windows PowerShell:

```powershell
& { $ErrorActionPreference='Stop'; $p=Join-Path $env:TEMP 'OpenAI-Edge-Workbench.cmd'; Invoke-WebRequest 'https://raw.githubusercontent.com/Namdev90/openai-edge-workbench/44c3c10b7332341d1a57d486be80bfce9acd47ea/OpenAI-Edge-Workbench.cmd' -UseBasicParsing -OutFile $p; if ((Get-FileHash $p -Algorithm SHA256).Hash.ToLowerInvariant() -ne '6a42578d7330e8baf82ea93c5cb23120cb7c76210ed43947e0fe2f0e092db014') { throw 'Downloaded file failed integrity verification' }; & $p }
```

The downloader uses a specific reviewed GitHub commit, verifies the exact launcher SHA-256, and runs it. The installer then opens a local graphical dashboard showing installation progress and logs. Because this is an unsigned third-party script, inspect its source before accepting Windows download warnings; never disable Defender/SmartScreen to run it. Windows Store sign-in and administrator approval may still be required by some selected software.

**Direct download:** [OpenAI-Edge-Workbench.cmd](OpenAI-Edge-Workbench.cmd) · [Setup.ps1](Setup.ps1).

The dashboard automatically starts after a visible 12-second countdown unless you pause/change selections. The optional authenticated Codex test is enabled by default and can consume model quota or incur charges; turn it off in the dashboard if desired. Package downloads can be several GB.

## What it does

- Detects Windows app, CLI, SDK, runtime, extension, dependency and supported MCP integration state.
- Prefers compatible, publicly released experimental channels, including nightly, alpha, beta, preview, Insiders and Canary, when the selected package actually provides them.
- Installs/updates supported tools using WinGet, official package registries or verified release manifests, and offers selectable optional packs.
- Preserves unrelated apps, profiles, project runtimes, chats, credentials and provider routing; migrates only supported settings and cleans **utility-owned** unused runtimes.
- Produces a redacted `Paste-Into-ChatGPT.txt` report to diagnose failed or incomplete steps.
- Does **not** grant ChatGPT authorization to external cloud services or guarantee successful migration of every app.

The source code is in [`source/`](source/). Test with `cd source && python -m unittest discover -s tests -v`; the CI pipeline runs on Ubuntu and Windows. All application code is identical to the embedded payload in the launcher; one regression test in the repository has been made Windows path-separator portable, documented in `tools/verify_payload.py`.

## Legacy snapshots

Prior installations are archived under `legacy/` for reference only: the standalone audit script, Namu AI Edge and OpenAI Device Manager. Do not run those old scripts; their hardcoded download paths refer to older AMReye.AI branches.

[Migration record](MIGRATION.md) · [Source detail](source/README.md) · [Verification limits](source/VERIFICATION.md).

The historical files were copied byte-for-byte from their old GitHub branches and individually checked by Git blob SHA. The old branch tips were then reset to unchanged `amreye-ai/main` with an exact-SHA lease; their names and historical Git objects remain. AMReye.AI's main branch was not edited.

## Logs, support and important limits

On Windows, copy the diagnostic text from the GUI or find it at:
`%LOCALAPPDATA%\OpenAI-Edge-Workbench\reports\<run-id>\Paste-Into-ChatGPT.txt`.

Review the report for private information before sharing. This repository and its test suite cannot prove the completed installation or connected app sign-ins until the utility actually runs on the laptop. No credentials, installed applications or messages are uploaded by this repository.
