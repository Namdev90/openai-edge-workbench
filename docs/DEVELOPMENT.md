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
python tools/feature_catalog.py --check
python tools/verify_docs.py
python tools/verify_language_lab.py
python -m unittest discover -s tools -p test_language_lab.py -v
python -m unittest discover -s tools -p test_package_release.py -v
python tools/build_language_atlas.py --check
node --check source/app.js
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/Test-Setup.ps1
pwsh.exe -NoProfile -File tools/Test-Setup.ps1
```

Check each exit status before proceeding. Rebuild whenever embedded source or tests change. Active text uses LF; executable CMD launchers retain CRLF. Do not normalize historical archives.

## Documentation-only changes

Use the [documentation guide](README.md) to put information beside the existing source of truth. Check relative links, command spelling, evidence scope and historical references. Run `python tools/verify_docs.py`; if catalog or atlas documentation changes, also run their checks above. An edit limited to the root README or Markdown under `docs/` does not require rebuilding the embedded application, changing its version or publishing a release. Markdown under `source/`, including `source/README.md` and `source/VERIFICATION.md`, is embedded by `tools/build_release.py`: rebuild the launchers/manifest and run payload verification whenever any embedded file changes. Do not rewrite dated verification records as if their checks were repeated.

The [CI workflow](../.github/workflows/verify.yml) is the executable reference for Windows/Linux coverage. Windows PowerShell and launcher smoke checks require Windows; a Linux pass does not replace them.

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

### Stage release files without overwriting local data

After the checks above pass, choose a **new** directory whose parent already exists:

```powershell
python tools/package_release.py --output "$env:TEMP\Namu-Workbench-Release-Candidate"
```

The packager verifies the embedded payload, snapshots the six release assets and writes their checksum file. It refuses an existing output path, including an empty directory, and rejects symlink/junction destinations or parents. A repeated run needs a different output path; no overwrite option is provided. A failed disk write can leave a partial new directory for inspection, which must not be published as a completed release.

Compare the six entries in `SHA256SUMS.txt` with the staged files. Staging is local preparation, not a GitHub release or proof of a real Windows installation. The packaging regression suite verifies deterministic bytes, checksums, failed-verification behavior and preservation of existing/concurrently created destinations on Windows and Linux CI.
