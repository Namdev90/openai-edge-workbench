# OpenAI Edge Workbench v2 — 10 October 2026

## Intent
One double-clickable Windows file opens a visible local dashboard, installs/updates a curated OpenAI and general-task toolkit using the newest public development channels where supported, migrates supported settings, and generates evidence for an iterative repair conversation.

## Architecture
A self-extracting CMD invokes a short Windows PowerShell bootstrap. The bootstrap reuses Python >=3.11 or bootstraps uv and selects a Python build from its catalog. A standard-library Python app hosts a token-protected, loopback-only dashboard and a single installation worker. The Python engine owns isolated Node, npm and Python environments and a state manifest. WinGet owns Windows applications. User configuration is inspected or backed up, not rewritten speculatively.

## Requirements and boundaries
- Public previews/alpha/nightly enabled by default, version-first selection, no silent stable retry after a preview fails.
- GUI auto-start countdown, pause countdown, start, stop-after-current-operation, progress, output, package results, report download/copy, local terminal and sign-in guidance.
- Latest catalog is re-fetched on each run; unknown future products are not automatically trusted.
- Current ChatGPT Microsoft Store ID 9PLM9XGG6VKS. Classic ID 9NT1R1C2HH7J is distinct; do not erase Classic data before signed-in migration verification.
- SDK environments are isolated. Existing projects, native Work routing, Headroom/RTK/Caveman, credentials, cookies, global npm/Python packages and OS settings remain intact.
- Automatic migration: same-product upgrades in place, non-conflicting VS Code settings/snippets and extension reinstall into Insiders, shared existing CODEX_HOME, managed version switch, cleanup of only unused Workbench-owned runtime generations while keeping one prior generation.
- No unsolicited accounts, purchases, secrets, remote control servers, third-party OAuth grants, disabled security controls, force-closing applications or automatic reboot.
- File SHA-256 verification for direct executable archives; never claim checksum is a publisher signature.
- Real command/exit-code evidence and local smoke checks; never equate HTTP response or install exit code with working authentication or desktop feature health.
- Windows installation/GUI behavior cannot be executed in the Linux authoring environment. Python policy, protection, workflow failure handling and HTTP GUI contract are testable locally.

## Validation
Unit tests before implementation: semantic versions, Python release parsing, channel selection, redaction, URL trust and archive traversal, merging, command results, progress failures, report coverage, UI authorization. Run Python compile, unit tests, live loopback HTTP tests, and JavaScript syntax check. Document Windows-only checks separately.
