# Namu AI Edge 2.0.0

A Windows GUI maintenance tool for a defined ChatGPT/Codex development workstation. Full readable PowerShell source, package catalog and tests are in this folder. It is not an official OpenAI product and is not a universal repair guarantee.

## Run

Download `Start-Namu-AI-Edge.cmd` and double-click it, or paste this single line into **Windows PowerShell**:

```powershell
& { $ErrorActionPreference='Stop'; $p=Join-Path $env:TEMP ('Namu-AI-Edge-'+[guid]::NewGuid().ToString('N')+'.ps1'); Invoke-WebRequest 'https://raw.githubusercontent.com/Namdev90/amreye-ai/namu-ai-edge/tools/namu-ai-edge/install.ps1' -UseBasicParsing -OutFile $p; powershell.exe -NoProfile -STA -ExecutionPolicy Bypass -File $p }
```

The bootstrap checks its GitHub code, verifies each source file against its SHA256 manifest, runs its PowerShell regression tests, and opens a Windows Forms dashboard. The dashboard starts maintenance automatically after five seconds. Click **Audit only** during that period for inventory without package installation. Windows may request installation approval. A desktop shortcut is created for subsequent runs. This is a process-local execution-policy setting; Defender, SmartScreen, signature/hash checks and system-wide execution policy are not disabled.

**First use requires Windows 10/11, Internet access and working Microsoft Store/WinGet.** Missing WinGet is reported with the App Installer recovery action, not silently worked around with untrusted installers. Non-Windows execution is unsupported. Run as your normal Windows user, not a different administrator account.

## Default behavior

- Installs/updates the current ChatGPT/Codex desktop app from Microsoft Store ID `9PLM9XGG6VKS`, VS Code Insiders, PowerShell Preview, Terminal Preview, Git, GitHub CLI, uv, 7-Zip, LibreOffice, Pandoc, FFmpeg, ImageMagick and Zotero. Their license/source agreements are accepted when package commands run. Preview IDs are explicit; other native apps follow the latest version in their selected WinGet channel. The tool does **not** claim every native app is on its most experimental upstream build.
- Downloads the highest compatible advertised Node nightly from nodejs.org, verifies its published SHA256 and tests the binary. Existing system Node installations remain untouched.
- Selects official npm package versions by highest numeric release line, then earliest public maturity (nightly > canary/snapshot > dev > alpha > beta/preview > RC > stable), then newest build identifier in that maturity. An obsolete lower-base alpha does not beat a newer release line. Package deprecations/platform-specific variants are excluded. Stable is used only when no qualifying prerelease wins for that package. Private or unreleased channels cannot be unlocked.
- Manages Codex CLI, OpenAI JavaScript/Agents/Codex SDKs, MCP SDK and Playwright in a dedicated package prefix. It tests the Codex executable and installs/tests a Playwright Chromium browser. These are local tool capabilities; they do not silently grant ChatGPT control over other applications.
- Installs the highest CPython download exposed by the current uv catalog, including alpha/beta/RC when available. Uses an isolated Python environment, and permits prereleases for OpenAI/Agents/MCP SDKs plus scientific, document and PDF libraries. Imports and dependency checks are recorded. The newest interpreter can lack compatible wheels; failures are reported, not disguised by stable fallback.
- Copies missing stable VS Code settings/keybindings/snippets to Insiders and reinstalls its listed extensions requesting prereleases. Conflicting existing profiles are not overwritten. Stable VS Code is retained because copying settings does not prove every profile/account/workspace is redundant.
- Preserves CODEX_HOME, credentials, conversation/session history, existing system runtimes, project dependencies and Headroom routing. Detects command paths, relevant local helpers/proxy listeners, MCP registration and Codex login. Local port/HTTP/MCP listing results are **not** authentication or end-to-end success.
- Runs one isolated authenticated Codex model round trip when logged in and the required isolation flags are available. **This uses subscription quota or billable API tokens.** It tests the baseline connection with user configuration ignored, not every configured proxy/MCP server.
- Removes only old validated Node/Python versions created by this tool, retaining the current and one previous version. Unknown old applications are flagged rather than blindly deleted. Installer caches, chats, cloud data and arbitrary project folders are never bulk-deleted.

## Weekly maintenance and self-update

A Windows scheduled task named **Namu AI Edge - Weekly** is registered and read back during an apply run: **Sunday at 15:00 in the laptop's local timezone**, as the signed-in user with limited privileges. It requires network access and requests missed-run catch-up. It cannot run while the laptop is powered off or guarantee execution while signed out. It opens the GUI in the user session and closes it after completion; logs remain available. An update needing UAC/account interaction can remain blocked until attended. The log distinguishes successful registration from an actual scheduled run.

Every launch, including weekly maintenance, resolves one GitHub commit and obtains its source files. New code is checksum-verified and self-tested before atomic activation. The installed bootstrap updates too. If fetching/testing new code fails, a previously validated build may be used, with the failure recorded. Hashes protect transfer integrity; they are **not an independent signature or protection against a compromised GitHub account/branch**.

Self-update means consuming published code and catalog updates. It does not mean an unsupervised agent can correctly invent arbitrary replacement code or discover and configure every future product. Known retries handle package-source/cache failures. New providers and deeper code bugs require a tested repository patch. No logs are automatically uploaded and no GitHub issue, email or message is posted on your behalf.

To remove only the weekly task:

```powershell
Unregister-ScheduledTask -TaskName 'Namu AI Edge - Weekly' -Confirm:$false
```

## Report and repair loop

Use **Copy report** after completion, or read:

```text
%LOCALAPPDATA%\Namu-AI-Edge\Latest-Report.txt
%LOCALAPPDATA%\Namu-AI-Edge\logs\<run>\Paste-Into-ChatGPT.txt
```

The report includes code commit/build, before/target/after observations, exit codes, bounded redacted error tails, retry records, verification results and manual/blocked items. It embeds a repair handoff telling ChatGPT how to retrieve the current source, classify the failure, add tests, patch, regenerate the release manifest, and publish corrected source. Review redacted output before sharing; regex redaction cannot guarantee removal of every unusual secret. Auth files and full MCP configuration are not copied into reports.

## Repository layout and verification

Published in `Namdev90/amreye-ai`, isolated branch `namu-ai-edge`, folder `tools/namu-ai-edge`. AMReye.AI's `main` branch is not changed. All source is directly readable. Use `Build-Release.py` after editing to regenerate the SHA256 manifest.

Tests: `tests/Test-Edge.ps1` exercises edge-channel ordering, credential redaction, HTTP status interpretation, Windows argument quoting, cleanup path boundaries, atomic writing, event serialization, parser validation and package-catalog invariants. Add `-Gui` to construct the Windows Forms GUI without starting maintenance. CI performs these tests on Windows PowerShell 5.1 and PowerShell 7 without installing apps, authenticating, spending model quota or registering tasks. Passing these tests is not equivalent to a real laptop installation or complete UI usability testing.

```powershell
powershell.exe -NoProfile -STA -ExecutionPolicy Bypass -File .\tests\Test-Edge.ps1 -Gui
```

## Sources used for the adapters

- OpenAI Windows distribution: https://help.openai.com/en/articles/9982051-using-the-chatgpt-windows-app
- Codex CLI and flags: https://developers.openai.com/codex/cli/reference
- VS Code extension CLI: https://code.visualstudio.com/docs/configure/command-line
- WinGet exact IDs, sources and package agreements: https://learn.microsoft.com/en-us/windows/package-manager/winget/install
- Node nightly builds/checksums: https://nodejs.org/download/nightly/
- uv Python and prerelease package options: https://docs.astral.sh/uv/reference/cli/

Native package identities are rechecked against the selected source on every run. Source availability and permissions can change.

## Desktop package provenance

The current Windows guide at https://learn.chatgpt.com/docs/windows/windows-app identifies Store package `9PLM9XGG6VKS` for the ChatGPT/Codex desktop app. The older help article still identifies `9NT1R1C2HH7J`; this catalog targets the newer guide and does not freshly install the older package. Existing older app data is not erased without a verified migration path. Verified 10 October 2026.
