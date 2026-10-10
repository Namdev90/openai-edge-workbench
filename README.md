# OpenAI Edge Workbench

Independent, **unofficial** Windows GUI for auditing and updating locally installed ChatGPT/Codex development tools, supported prerelease runtimes, SDKs, and related utilities.

The main executable is `OpenAI-Edge-Workbench.cmd`, accompanied by its complete readable source in `source/`.

**Windows:** download the launcher, then double-click it as your normal user. For a single verified PowerShell setup command, see the installation instructions below after publication.

The local browser-based GUI shows live progress and produces `Paste-Into-ChatGPT.txt`. The utility preferentially selects supported public early-release channels (nightly, alpha, beta, Insiders, Canary) but does not promise every upstream application exposes a preview release.

**Migrations:** Existing personal profiles, Codex authentication, provider routes, and project environments remain protected. Only runtime generations explicitly owned by this utility are eligible for automated cleanup. The live authenticated Codex check can consume quota or incur charges.

This repository is independent of AMReye.AI. Earlier experiments are preserved as read-only historical snapshots under `legacy/`; those installers are **not** used by the current launcher.

Review [source/README.md](source/README.md) and [source/VERIFICATION.md](source/VERIFICATION.md) before running. Source tests: `cd source; python -m unittest discover -s tests -v`.

## Status

Code publishing and file integrity can be verified remotely; a complete Windows installation and signed-in connectivity audit still require running the GUI on the actual laptop. Report failures via the GUI's redacted diagnostic text. No credentials are collected by this repository.
