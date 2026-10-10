# Verification record

Build: OpenAI Edge Workbench 2.0.2-preview.1, 10 October 2026.

## Application checks

81 regression tests pass locally on Windows. Coverage includes interpreter selection with a full selected-pack wheel solution, explicit resolution rejection versus transport errors, hashed package locks, pack imports and version matching, candidate preservation, exact-channel timeout retries, WebView2 registry verification, catalog mismatches, native PowerShell JSON under a foreign module search path, safe original PATH backups, npm version/warning separation, and concurrent HTTP report reads while reports are replaced.

Existing coverage also checks architecture/release selection, secret redaction, archive traversal, Windows junctions, configuration conflict preservation, ownership-limited cleanup, process exit evidence, local capability/origin/Host checks, simulation labeling, and rejection of a second worker. An independent Astra review ran the suite and checked the fixes.

The JavaScript parser check passes. The release build regenerates every embedded source byte and its SHA-256 manifest. CI runs application and payload tests on Windows and Linux; Windows additionally runs the 12 setup/security tests under Windows PowerShell 5.1 and PowerShell 7 plus real CMD extraction and NoLaunch bootstrap.

## Real resolver and installation evidence

The installed uv executable was exercised against the complete selected package set. CPython 3.15.0 was rejected because DuckDB has no matching cp315 wheel. CPython 3.14.8 resolved all 143 dependencies. Core OpenAI SDKs alone resolve on 3.15.0, so disabling optional packs can retain the newer interpreter. A development target was also accepted as a target argument and rejected for a proven wheel incompatibility. These are runtime observations, not permanent version pins.

The supplied initial laptop diagnostic confirmed exact Codex alpha execution, configured ChatGPT login, a real authenticated model round trip, matching Playwright browser launch, and many installed package versions. It also identified two preview network timeouts, hidden WebView2 registration, an incompatible document wheel, and failed PATH/report generation. The targeted repair records actual results separately in the local diagnostic directory; private laptop reports are not committed to this public repository.

Native registry verification confirmed the reported WebView2 version independently of WinGet inventory. Actual npm execution reproduced its nightly engine warning; the version remains clean while the warning is preserved. A passing process startup does not establish npm's declared compatibility.

## Limits

Offline tests and installer registration do not establish every desktop feature, plugin action, OAuth connection, same-account identity across apps, or cloud synchronization. The initial model round trip is evidence only for that CLI/provider configuration. Repair verification does not repeat a quota-consuming model request automatically.

Package catalog availability and network failures remain visible. The utility does not suppress signature checks, reset security or organization policy, remove original applications, overwrite project environments, or export credentials. Existing configuration contents and private backups stay local.

## Earlier builds

The initial 2.0.0 build had 42 offline tests and a simulated browser fixture. The standalone 2.0.1-preview.1 review had 48 application tests and 12 setup/security tests, plus verified download/extraction/NoLaunch paths. Those earlier checks did not by themselves establish a complete laptop installation. This repair was driven by the subsequent real diagnostic.
