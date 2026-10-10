# Development

## Local checks

Use Python 3.11 or newer. The GUI has no third-party Python runtime dependency. From the repository root:

```powershell
Push-Location source
python -m unittest discover -s tests -v
Pop-Location
python tools/build_release.py
python tools/verify_payload.py
python tools/verify_migration.py
node --check source/app.js
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/Test-Setup.ps1
pwsh.exe -NoProfile -File tools/Test-Setup.ps1
```

Check each exit status before proceeding. Rebuild whenever embedded source or tests change. Active text uses LF; executable CMD launchers retain CRLF. Do not normalize historical archives.

## Try without installing

```powershell
python source/app.py --simulate --root "$env:TEMP\Namu-Workbench-Demo"
```

The demo is visibly labeled. Installation steps are simulated; native diagnostics launch no commands or catalog requests. It can still save a recipe under its demo root or download local artifacts. **Quit dashboard** releases the lock. Never use a real laptop report as a public screenshot fixture.

## Add a capability

Declare stable metadata and a specific user operation. The 100-entry catalog is deliberately exact: changing it requires an intentional catalog/schema update and documentation reconciliation. Validate inputs, show effects, and prefer pure analysis. Avoid arbitrary command/URL escape hatches. Test meaningful behavior, failure paths, redaction and preservation.

Recipes never start installation. Keep Apply separate from Start, and pause auto-start when a user reviews a feature. Preserve keyboard focus, denied-storage behavior, responsive layout, reduced motion and CSP compatibility.

## Release checklist

1. Review changes; bump `engine.VERSION`, catalog and verification record.
2. Normalize only active source, rebuild deterministic launchers, and run regression/setup/payload/migration checks.
3. Exercise browser controls and label demo screenshots. Record actual Windows observations separately, with private reports outside Git.
4. Push without rewriting history; verify Windows/Linux CI at the published commit.
5. Publish a prerelease with setup CMD, standalone CMD, source ZIP, `Setup.ps1`, `Run.ps1`, `SETUP.md` and SHA-256 sums. Download again and compare hashes.
6. Test the real GitHub bootstrap with `EDGE_NO_LAUNCH=1` and an isolated `EDGE_ROOT`. Inspect installed source/provenance; this does not run toolkit installers or model requests.

The proposal snapshot uses `roadmap:Fnnn`; the implemented catalog uses `studio:fnnn`. Update [status reconciliation](ROADMAP-STATUS.md) when acceptance criteria are met.
