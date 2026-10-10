# OpenAI Edge Workbench

Unofficial one-click Windows installer/updater with a browser dashboard, selectable tool packs, live progress and an auditable repair report. This standalone repository is separate from AMReye.AI.

## Install

Short graphical launch in ordinary Windows PowerShell:

```powershell
irm https://raw.githubusercontent.com/Namdev90/openai-edge-workbench/main/Run.ps1 | iex
```

Every tool pack is selected initially; edit choices during the dashboard countdown. The short launcher trusts current GitHub code; SETUP.md also provides the pinned, independently checksum-verified first-download command.


Download the setup launcher from Releases and double-click it, or use the exact PowerShell command in [SETUP.md](SETUP.md). Setup pins the initial downloader to a reviewed commit and verifies SHA256 before execution. The updater resolves one current main commit, validates the complete launcher and embedded source, runs offline tests, and opens the dashboard.

The dashboard starts after a visible 12-second countdown. Changing selections pauses that countdown. Public nightly/alpha/beta/Insiders/Canary channels are selected where supported. The optional live Codex request uses model quota or API billing; disable it in the dashboard if desired. Windows package installation approvals and account sign-in may require your input.

If the repository is private, use the authenticated command in SETUP.md. The updater uses GitHub CLI's existing stored sign-in and never exports its token to raw download hosts or diagnostics. The repository's current visibility is preserved.

## Updates, migration and reports

The **OpenAI Edge Workbench** desktop shortcut refreshes published source before each launch. Offline fallback rechecks cached launcher and embedded source hashes and records the failed update. Fresh Python/JavaScript SDK candidates are selected only after checks; failed packs retain the previous managed SDK selection. Existing projects, credentials, Codex history/configuration, provider routes, original applications and browser profiles are preserved.

Version 2.0.2 repairs the first laptop diagnostic: Python is selected only after a full compatible wheel preflight, WebView2 is checked through Microsoft's registry values, preview network timeouts receive bounded same-channel retries, and native Windows PowerShell produces checked JSON for the original user PATH backup. Report reads and writes are synchronized, and remaining version or npm compatibility warnings stay visible.

Version 2.0.3 retains the newest official Node nightly for tool execution and selects the newest npm separately. Official npm semver checks choose its newest compatible private Node host; no npm warning is suppressed and no engine metadata is patched. npm/npx launchers use that explicit host, while Codex and SDK execution keep the nightly runtime. .NET daily discovery also recognizes release-candidate channels marked go-live.

The setup launcher updates published code. The self-contained OpenAI-Edge-Workbench.cmd in the repository is also available as a snapshot for that release. Neither invents repair code or enables private publisher betas.

Use **Copy report**, or open:

```text
%LOCALAPPDATA%\OpenAI-Edge-Workbench\reports\<run-id>\Paste-Into-ChatGPT.txt
```

The report records selected/observed versions, exits, failures, model checks and the source commit. Review redacted text before sharing. No logs or messages are automatically sent. Local package installation and HTTP reachability do not establish cloud authorization or cross-device synchronization.

## Source and verification

[source/](source/) contains every embedded application file. [release.json](release.json) and [tools/verify_payload.py](tools/verify_payload.py) verify exact byte correspondence, including tests. No source-byte exception is used. [tools/build_release.py](tools/build_release.py) rebuilds the deterministic launcher after edits.

Application regression tests and 22 setup/security tests cover Windows PowerShell 5.1 and PowerShell 7. The actual CMD extraction and bootstrap are exercised in NoLaunch mode, and CI repeats application/distribution checks on Windows and Linux. [The verification record](source/VERIFICATION.md) separates offline checks, the supplied installation report, and targeted laptop repair results. It does not certify every desktop feature or cloud plugin.

[MIGRATION.md](MIGRATION.md) and [migration-audit.json](migration-audit.json) document exact historical archives, branch cleanup conditions and verification. Historical files in legacy/ are inert references and are not executed by the active setup.

[Detailed scope](source/README.md) Â· [Verification record](source/VERIFICATION.md) Â· [Official publisher references](source/SOURCES.md).

See [FEATURES.md](FEATURES.md) for the exact legacy feature reconciliation and [ALTERNATIVES.md](ALTERNATIVES.md) for researched alternatives.

[100 new capability proposals](FEATURE-PROPOSALS.md) provides a prioritized roadmap with current gaps, acceptance criteria and dependencies. It is a documentation proposal, not an implemented feature list or an automatic implementation trigger.

Version 2.0.4 keeps structured Codex doctor warnings/failures visible, including their individual details and remediation. Successful installation or doctor process exit does not hide degraded optional MCP configuration, security observations or history-index warnings. Security exclusions and history databases are not modified automatically.
