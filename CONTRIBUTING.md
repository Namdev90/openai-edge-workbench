# Contributing to Namu AI Workbench

Help make Windows tooling easier to install, inspect and maintain. Contributions should preserve existing configurations, show the actual result of each operation, and use verifiable official package sources.

The application uses Python 3.11+ and the standard library. Its dashboard uses plain HTML, CSS and JavaScript; no Node build or npm install is required to develop the dashboard. Full installations require Windows. The regression suite also runs on Linux, where installation behavior is tested through isolated fixtures and simulation.

## Start with a focused change

For a bug, include the affected component, expected behavior, observed behavior and a short reproduction. For a feature, describe the user problem, its effect on the computer, its official source where relevant, and how its result can be verified. An issue is useful for substantial changes, but it is not required for a small correction.

Keep unrelated changes separate. Add regression coverage when a change affects installation, compatibility, migration, security boundaries or reporting. A documentation correction usually needs a careful link and content review instead of a new test.

## Local development

Clone the repository and work on a branch. Use Python 3.11 or newer. To preview the dashboard with a separate development directory:

```powershell
python .\source\app.py --simulate --root "$env:TEMP\Namu-Workbench-Dev"
```

Simulation is clearly labeled and does not establish that software is installed or services work. Pause the visible countdown if you want to inspect the interface before its simulated run starts. Use **Quit dashboard** to stop the local server; closing the browser tab alone leaves it running.

The readable application lives in `source/`. Release construction and verification live in `tools/`. The CMD launchers and `release.json` are generated artifacts. Historical source under `legacy/` is an audited archive; preserve its bytes and provenance.

## Validate your change

Run the application tests from the source directory:

```powershell
Push-Location source
python -m unittest discover -s tests -v
Pop-Location
```

From the repository root, rebuild the deterministic release payload and verify it against the readable source and migration archive:

```powershell
python tools/build_release.py
python tools/verify_payload.py
python tools/verify_migration.py
```

For setup or PowerShell changes, run the setup and parser checks in both Windows PowerShell 5.1 and PowerShell 7:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/Test-Setup.ps1
pwsh.exe -NoProfile -File tools/Test-Setup.ps1
```

Check each command's exit code. Do not treat a later successful command as evidence that an earlier check passed. If you modify source included in the payload, commit the regenerated launchers and manifest with that change. JavaScript edits should also pass `node --check source/app.js` when Node is available. Review dashboard changes at desktop and narrow mobile widths, including keyboard navigation and reduced motion.

The GitHub workflow performs application, payload and archive checks on Windows and Linux, with additional Windows setup and launcher smoke checks. Describe what you actually ran in your pull request and identify checks that remain unverified.

## Keep the boundaries intact

- Prefer official distribution channels. Record exact versions, integrity checks and compatibility evidence; do not suppress a warning to manufacture success.
- Preserve user projects, credentials, settings, profiles and unrelated installations. Cleanup must remain limited to verified Workbench-owned files and retention rules.
- Keep dashboard operations protected by the session capability and same-origin checks. New features must use fixed, reviewable handlers; do not introduce an arbitrary command, path or URL execution interface.
- Keep modifying actions explicit and visible. Do not add silent scheduled jobs, model requests, third-party connections or report uploads.
- Preserve the distinction between installation, execution, authentication and end-to-end verification. Label simulations and incomplete checks.

## Share useful evidence safely

Never commit or attach `local-session.json`, authentication files, credentials, cookies, private backups, complete personal logs or unreviewed diagnostic reports. Remove usernames, private paths, account details, project names and tokens from the smallest excerpt needed to explain a problem. A screenshot must also be reviewed for private information.

Do not publish an exploit or credential in a public issue. Use [private vulnerability reporting](https://github.com/Namdev90/openai-edge-workbench/security/advisories/new), enabled for this repository. See [SECURITY.md](SECURITY.md) for the reporting scope and trust boundaries.

## Pull requests and licensing

Explain the problem, the resulting behavior, the meaningful validation and any remaining limitation. Use the pull request template and keep its evidence current after revisions.

This repository currently has no license file. This guide does not grant a license or choose one for the project. Any licensing decision belongs to the repository owner.
