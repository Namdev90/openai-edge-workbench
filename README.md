# OpenAI Edge Workbench

Unofficial one-click Windows installer/updater with a browser dashboard, selectable tool packs, live progress and an auditable repair report. This standalone repository is separate from AMReye.AI.

## Install

Download the setup launcher from Releases and double-click it, or use the exact PowerShell command in [SETUP.md](SETUP.md). Setup pins the initial downloader to a reviewed commit and verifies SHA256 before execution. The updater resolves one current main commit, validates the complete launcher and embedded source, runs offline tests, and opens the dashboard.

The dashboard starts after a visible 12-second countdown. Changing selections pauses that countdown. Public nightly/alpha/beta/Insiders/Canary channels are selected where supported. The optional live Codex request uses model quota or API billing; disable it in the dashboard if desired. Windows package installation approvals and account sign-in may require your input.

If the repository is private, use the authenticated command in SETUP.md. The updater uses GitHub CLI's existing stored sign-in and never exports its token to raw download hosts or diagnostics. The repository's current visibility is preserved.

## Updates, migration and reports

The **OpenAI Edge Workbench** desktop shortcut refreshes published source before each launch. Offline fallback rechecks cached launcher and embedded source hashes and records the failed update. Fresh Python/JavaScript SDK candidates are selected only after checks; failed packs retain the previous managed SDK selection. Existing projects, credentials, Codex history/configuration, provider routes, original applications and browser profiles are preserved.

The setup launcher updates published code. The self-contained OpenAI-Edge-Workbench.cmd in the repository is also available as a snapshot for that release. Neither invents repair code or enables private publisher betas.

Use **Copy report**, or open:

```text
%LOCALAPPDATA%\OpenAI-Edge-Workbench\reports\<run-id>\Paste-Into-ChatGPT.txt
```

The report records selected/observed versions, exits, failures, model checks and the source commit. Review redacted text before sharing. No logs or messages are automatically sent. Local package installation and HTTP reachability do not establish cloud authorization or cross-device synchronization.

## Source and verification

[source/](source/) contains every embedded application file. [release.json](release.json) and [tools/verify_payload.py](tools/verify_payload.py) verify exact byte correspondence, including tests. No source-byte exception is used. [tools/build_release.py](tools/build_release.py) rebuilds the deterministic launcher after edits.

The reviewed build passes 48 application tests and 11 setup/security tests in Windows PowerShell 5.1 and PowerShell 7. The actual CMD extraction and bootstrap were exercised in NoLaunch mode on Windows, with an existing Python, without installing toolkit apps or making model requests. CI repeats application/distribution checks on Windows and Linux, plus the Windows bootstrap smoke test. This does not certify a complete laptop installation; the installation report is still required.

[MIGRATION.md](MIGRATION.md) and [migration-audit.json](migration-audit.json) document exact historical archives, branch cleanup conditions and verification. Historical files in legacy/ are inert references and are not executed by the active setup.

[Detailed scope](source/README.md) · [Verification record](source/VERIFICATION.md) · [Official publisher references](source/SOURCES.md).
