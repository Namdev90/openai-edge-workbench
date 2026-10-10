# Verification record

Build: OpenAI Edge Workbench 2.0.3-preview.1, 10 October 2026.

## Application checks

112 regression tests pass locally on Windows. Coverage includes interpreter selection with a full selected-pack wheel solution, explicit resolution rejection versus transport errors, hashed package locks, pack imports and version matching, candidate preservation, exact-channel timeout retries, WebView2 registry verification, catalog mismatches, native PowerShell JSON under a foreign module search path, safe original PATH backups, npm version/warning separation, and concurrent HTTP report reads while reports are replaced. Signed local Terminal recovery and exact per-user Canary side-by-side installation have dedicated failure and cancellation checks.

Existing coverage also checks architecture/release selection, secret redaction, archive traversal, Windows junctions, configuration conflict preservation, ownership-limited cleanup, process exit evidence, local capability/origin/Host checks, simulation labeling, and rejection of a second worker. Astra independently reviewed the earlier 2.0.2 repair. The 2.0.3 npm and .NET changes were additionally checked through regression tests and actual isolated runtime/package operations.

The JavaScript parser check passes. The release build regenerates every embedded source byte and its SHA-256 manifest. CI runs application and payload tests on Windows and Linux; Windows additionally runs the 22 setup/security tests under Windows PowerShell 5.1 and PowerShell 7 plus real CMD extraction and NoLaunch bootstrap.

## Real resolver and installation evidence

The installed uv executable was exercised against the complete selected package set. CPython 3.15.0 was rejected because DuckDB has no matching cp315 wheel. CPython 3.14.8 resolved all 143 dependencies. Core OpenAI SDKs alone resolve on 3.15.0, so disabling optional packs can retain the newer interpreter. A development target was also accepted as a target argument and rejected for a proven wheel incompatibility. These are runtime observations, not permanent version pins.

The supplied initial laptop diagnostic confirmed exact Codex alpha execution, configured ChatGPT login, a real authenticated model round trip, matching Playwright browser launch, and many installed package versions. It also identified two preview network timeouts, hidden WebView2 registration, an incompatible document wheel, and failed PATH/report generation. The targeted repair records actual results separately in the local diagnostic directory; private laptop reports are not committed to this public repository.

Native registry verification confirmed the reported WebView2 version independently of WinGet inventory. The earlier npm nightly engine warning was reproduced and preserved in the original repair report. Version 2.0.3 fixes the mismatch by retaining Node v27.0.0-nightly202610086d5e309871 for tool execution while npm 12.2.0 uses the newest official host accepted by its unchanged semver engine range, Node v26.11.1. Isolated real npm version execution and package installation returned without the compatibility warning. The installed package and existing Codex alpha also executed under the nightly runtime. No version checks, engine metadata, or warning levels were altered. These versions are observations; future runs resolve current catalogs again.

.NET discovery recognizes a prerelease SDK in a go-live channel as a development release. Regression checks reject stable or malformed channel substitutions. The signed official installer installed daily SDK 11.0.100-rc.2.26508.107 in the private managed runtime. Its actual version was checked, and a fresh console project compiled and ran Hello, World! successfully. The all-tools launcher is also tested through the actual application process and dashboard response.

The targeted laptop repair verified PowerShell Preview 7.7.5.0 and Terminal Preview 1.26.2734.0. Terminal's repeated streaming URI timeouts were recovered with the exact official bundle after SHA256 and valid Microsoft signature checks; Windows registered the exact healthy Preview AppX. The signed official Canary 157.0.8095.0 installer created the per-user Chrome SxS binary with the documented side-by-side switches. Regular Chrome remained 154.0.8037.98. WebView2 155.0.4283.45 was independently registered. These are point-in-time observations rather than fixed future versions.

The repaired private Python 3.14.8 environment passed real DuckDB, NumPy, Biopython, DOCX, XLSX, and PDF operation checks. Codex configuration and instructions were byte-identical before and after repair. Original user PATH was backed up before adding the managed shims, and the diagnostic/report steps completed without their previous JSON errors.

## Limits

Offline tests and installer registration do not establish every desktop feature, plugin action, OAuth connection, same-account identity across apps, or cloud synchronization. The initial model round trip is evidence only for that CLI/provider configuration. Repair verification does not repeat a quota-consuming model request automatically.

Package catalog availability and network failures remain visible. The utility does not suppress signature checks, reset security or organization policy, remove original applications, overwrite project environments, or export credentials. Existing configuration contents and private backups stay local.

## Earlier builds

The initial 2.0.0 build had 42 offline tests and a simulated browser fixture. The standalone 2.0.1-preview.1 review had 48 application tests and 12 setup/security tests, plus verified download/extraction/NoLaunch paths. Those earlier checks did not by themselves establish a complete laptop installation. This repair was driven by the subsequent real diagnostic.
