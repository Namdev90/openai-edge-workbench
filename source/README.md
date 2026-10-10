# OpenAI Edge Workbench 2.0.2-preview.1

Independent, unsigned Windows maintenance utility generated for Namu. It is not an OpenAI product.

## Run

Double-click **OpenAI-Edge-Workbench.cmd**. No original audit script or manual flags are required. A bootstrap window appears first, followed by a local browser dashboard. Setup starts after a visible 12-second countdown. Changing an option pauses the countdown. Use **Start now** to proceed.

Run as your normal Windows user. Individual package installers may ask for UAC permission or Microsoft Store sign-in. Do not turn off Defender, SmartScreen or organization policy to run this utility. Review the source if Windows flags this unsigned download. The source ZIP contains all code; no obfuscated remote installer is fetched and executed.

Requires Windows x64/ARM64, internet, sufficient disk space and WinGet / Microsoft App Installer. If Python 3.11+ already exists, it is reused solely to display the dashboard. Otherwise the bootstrap installs uv and the newest native normal CPython build in uv's catalog. The main run updates uv and separately selects a managed development Python runtime for your tools.

## Release policy

It uses Node's official nightly catalog; the highest supported public semantic versions from the official npm packages, including development prereleases; preview/Insiders/Canary desktop channels; and the newest compatible native normal CPython available to uv, including alphas/betas/RCs. Before installing Python, the complete selected pack set is resolved to binary wheels for the actual Windows architecture. Unsupported interpreter versions and resolver evidence are recorded. Network errors do not justify choosing an older interpreter. Exact resolved packages are SHA-256 locked, installed together, and checked through imports and dependency consistency. Superseded prereleases and platform-specific npm wrapper releases are excluded. A final release is newer than its own already-superseded alpha. Private builds, arbitrary source commits and unsupported experimental Python variants are not selected.

WinGet tools are updated to the version offered by their **specific configured catalog/channel**. That may lag the upstream publisher, and a public preview may not exist for an application. The utility records this distinction instead of claiming every component is on a nightly. A failed experimental install is not silently retried on an older stable runtime. Re-running discovers package releases again; it does **not** rewrite this utility's source or learn arbitrary new product migrations by itself.

Completed installer network timeouts (`0x80072EE2`) receive bounded retries of the same exact package and channel. Killed managers, signature/security failures and other errors are not retried. WebView2 presence is checked through Microsoft's documented Evergreen registry values because WinGet can omit that runtime. A known catalog-versus-installed mismatch stays visible as `VERSION_MISMATCH`. npm's actual version is stored separately from its compatibility warnings; a running nightly does not suppress those warnings.

## Default scope

Always: current ChatGPT desktop Store ID `9PLM9XGG6VKS`, Git, GitHub CLI, uv, PowerShell Preview, VS Code Insiders, Windows Terminal Preview, WebView2, Node nightly, npm bundled with that nightly, official Codex CLI, official OpenAI API CLI when a verifiable Windows release asset exists, isolated Python and JavaScript OpenAI SDKs, OpenAI/Python/Jupyter preview editor extensions.

Enabled but selectable: documents/data/media (7-Zip, Pandoc, FFmpeg, PowerToys, Python document and data libraries), browser automation (Chrome Canary, Playwright, matched Chromium), scientific Python (Biopython, SciPy, SymPy, scikit-learn), supported editor migration, unused **Workbench-owned** runtime cleanup, official read-only OpenAI documentation MCP, and one read-only Codex model request.

Optional, off by default: newest advertised .NET preview channel's daily SDK, with signature checking on its installer.

Individual package lists and sources are visible in `engine.py` and the dashboard. These tools expand what a local coding agent can use; they are **not all required just to chat with ChatGPT**. Installing a tool is not the same as connecting or granting permission to use it.

## Costs, installation impact and permissions

The selected toolkit can consume several GB of network and disk capacity. No paid app is purchased, API key created, subscription changed or cloud plugin authorized. Existing account usage/entitlements apply. The optional live Codex test is ON by default because it was requested: one model round trip may consume plan quota or incur API charges depending on your current authentication. Turn it off before Start to avoid the request.

No Windows Insider enrollment, operating-system upgrade, driver update, WSL/Docker setup, firewall weakening, antivirus changes, forced reboot, unrestricted remote MCP, hidden service or scheduled task is installed. No automatic email/message sending is enabled.

## Migration and cleanup boundaries

- Installs selected new versions and reuses your existing native `CODEX_HOME` / `.codex` configuration. Does not replace current providers, Headroom/RTK/Caveman routing, credentials, cookies or native Work configuration.
- Backs up `config.toml` and `AGENTS.md` locally. These backups can contain private information and are **not** part of the report.
- Copies missing VS Code settings/snippets into Insiders and migrates existing default-profile extension IDs. Conflicting target settings remain unchanged and are listed for review. Other profile memberships, sign-ins and workspace dependencies are not guaranteed migrated.
- Adds an official read-only documentation MCP only when not already present. A conflicting name or unparseable existing config is reported rather than overwritten.
- Creates managed `codex` / `codex-edge`, `openai-api`, `python-edge`, `node-edge` and `npm-edge` launchers. Only the Workbench bin folder is prepended to **User PATH**; the machine PATH is not changed. Another machine-wide executable can still take precedence. Use **Open Edge Terminal** for the managed tools.
- Original system runtimes, global packages, ChatGPT Classic, old editors and project environments are not uninstalled merely because newer copies exist. Automatic deletion is restricted to unused runtime generations created by this Workbench; active versions and two recent generations are retained. That is deliberately narrower than universal migration/uninstall.
- Restart ChatGPT/editor/terminal applications to inherit changed environment variables. Their own bundled runtimes are independently managed.

There is no universal rollback button. A pre-Workbench User PATH backup is saved under `private-backups`; installed third-party software can be removed through Windows Apps. The command directories are owned by this utility, but original programs are not purged. Do not delete the Workbench folder while its managed commands or terminal are in use.

## GUI and diagnostics

The dashboard listens **only on 127.0.0.1**, on a random local port. API operations require a per-run capability, an exact Host header, and a same-origin write request. It has no API for arbitrary shell commands or user-supplied download URLs. No report is uploaded automatically. The capability is kept locally in `local-session.json`; do not share that file.

**Stop after current command** allows the current package operation to finish. It is not an instant kill switch. On a command timeout, further steps stop; an installer child process may still be running, which the report flags. **Quit dashboard** closes the local server after any current operation finishes. Closing only the browser tab does not stop the engine; reopening the launcher returns to the same run.

A separate report folder is created for every invocation:

`%LOCALAPPDATA%\OpenAI-Edge-Workbench\reports\<run-id>\`

It contains `Paste-Into-ChatGPT.txt`, `Diagnostic.json`, and `Activity-redacted.jsonl`. An incremental report is saved after each operation. **Copy report** is the intended handoff for iterative fixes. Automated redaction removes common token/key patterns, emails and user-home paths, but it cannot recognize every possible secret: review before sharing. Never share auth files, private backups or the local session file.

Statuses distinguish VERIFIED, CATALOG_CURRENT, INSTALLED_CHECK_NEEDED, REVIEW_NEEDED, NOT_AVAILABLE, FAILED, STOPPED and NOT_RUN. VERIFIED means the **specific recorded check** passed, not that all features and services work. A simulated/demo run is always marked SIMULATED.

## What must still be checked in signed-in apps

Same account in desktop/CLI/editor; account/workspace entitlement; desktop app behavior; feature rollout; private beta access; each plugin's OAuth authorization and a real permitted action; browser extension installation approval; migration of Classic-specific local data. Use the official app's import/sign-in UI where applicable. This utility does not bypass permissions or claim HTTP reachability proves authentication.

## Verification performed during creation

See `VERIFICATION.md` for actual commands and results. Python logic, local HTTP authorization and simulation flows are testable here. Windows PowerShell bootstrap, WinGet/MSIX installers, UAC interactions and the complete live laptop run have **not** been executed in the build environment. Your first report is required to verify the actual Windows result.

## Source entry points

`bootstrap.ps1` bootstraps the Python GUI; `app.py` serves the bounded loopback interface; `engine.py` manages explicit software adapters; `index.html`, `style.css`, `app.js` render the dashboard; `tests` contains automated tests. `SOURCES.md` lists official documentation. Source dependencies: Python standard library only. No separate web framework or GUI library is installed for the dashboard.

## Reviewed standalone updater

Use the repository Setup.ps1 command or the setup release asset for self-update. Setup resolves one immutable main commit, verifies the launcher and every embedded source file, and uses GitHub CLI stored authentication when available. The desktop Workbench shortcut repeats that update check. The direct embedded CMD remains a complete snapshot of its release.

Every launch extracts fresh verified source and runs offline application tests before opening the dashboard. Python and JavaScript SDKs are installed into per-run candidates; failed packs or failed SDK imports preserve the previous selected SDK environment. Cached source is not trusted solely because a marker exists. Junctions in managed paths and nested cleanup candidates are rejected. Update provenance appears in the diagnostic report.
