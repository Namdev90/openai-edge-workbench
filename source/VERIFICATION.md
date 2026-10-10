# Verification record

Build: OpenAI Edge Workbench 2.0.0, 10 October 2026.

## Executed

- `python -m py_compile app.py engine.py`: passed in Python 3.13.
- `python -m unittest discover -s tests -v`: **42 tests passed**. Covers release selection, superseded previews, architecture filtering, redaction, ZIP traversal, migration conflict preservation, unowned cleanup retention, process-exit evidence, installer-result/registered-version mismatches, report serialization, explicit simulation labeling, local HTTP authentication, origin and Host checks, unknown actions, and second-worker rejection.
- `node --check app.js`: passed.
- Chromium offline UI fixture connected through a test bridge to the actual loopback HTTP API: setup/start, 30 simulated result rows, copy-report flow, desktop rendering and 390-pixel mobile layout checked. No JavaScript errors or mobile horizontal overflow observed.
- Direct Chromium navigation to loopback was blocked by the build environment's administrator policy. That policy was **not changed**. The offline UI fixture and separate real loopback HTTP tests are not a claim of a full Windows browser launch.
- Real installed uv CLI exercised for `python list --all-versions --all-platforms --output-format json`; confirms the catalog schema consumed by the selector. This is a schema check, not a current Windows version result.
- Packager verifies the embedded payload SHA-256, safe archive paths, source byte-for-byte matches, CMD payload reconstruction, source ZIP integrity and command-line length constraints. See `SHA256SUMS.txt` beside the release artifacts.

## Not executed or established

- Windows PowerShell parsing/execution of the bootstrap and self-extraction loader.
- Actual Windows Store/WinGet installation, UAC interaction, user PATH changes, desktop shortcuts, app migration or browser launching on the user's laptop.
- Real downloads of all target prerelease binaries or complete Windows package compatibility.
- A real authenticated Codex request, third-party OAuth, all plugin operations, account synchronization, desktop feature availability or private-beta entitlement.

The generated utility includes bounded runtime checks and partial reports for these cases. A successful build/test record is not a certificate that the user's laptop has been repaired. Review the first laptop diagnostic before considering removals or broader migrations.
