# Verification record

Build: Namu AI Workbench 3.0.0-preview.2, 10 October 2026.

## Version 3.0 acceptance record

282 application tests ran locally on Windows: 279 passed, no failures, and three symlink tests skipped because Windows requires additional symlink privilege. The 23 setup/security checks passed separately under Windows PowerShell 5.1 and PowerShell 7. JavaScript syntax, the exact 100-entry documented/executable catalog, active documentation links, SVG/PNG assets and proposal-ID separation were checked.

Preview.2 addresses an intermittent Windows connection reset observed during a later check of the actual installed launcher cache, after preview.1 passed local and CI checks. Rejected requests discard only unambiguously framed raw bytes within 8 KiB and a 250 ms overall deadline, then flush and close the error response. Authorization still precedes JSON parsing. Regression coverage includes 150 real denied POST requests, stalled bodies, ambiguous framing and slow-drip deadlines. Unsafe oversized or ambiguous framing is refused without unbounded draining; complete response delivery to such malformed senders is not guaranteed. Astra independently reviewed this fix without finding a release blocker.

A real Windows PowerShell subprocess also verifies that a failed NoLaunch bootstrap exits with a nonzero status and its diagnostic, without installing anything or opening a modal error dialog. Interactive failures retain their visible error message. These seven added tests do not install toolkits or call an AI provider.

New coverage includes all 30 diagnostic handlers, all 35 report analyses, all 25 profile/plan/export handlers, the ten client controls, actual protected HTTP feature jobs, admission limits, simulation guards, malformed history, secret-field redaction, JSON export round trips, HTML/CSV safety, support ZIP checksums, recipe preservation, and the all-tools launch excluding automatic model requests.

Astra's final review identified dashboard selections missing from plan/requirements/recipe requests. The corrected client is exercised as JavaScript with explicit checkbox fixtures, and the actual HTTP API verifies the matching plan and saved selection without starting installation. Recipe writes use exclusive descriptor-backed temporary files, ownership/target rechecks and atomic publication; real NTFS tests preserve planted fixed temporary paths, late foreign markers/recipes and hard-linked copies, with cleanup after failed replacement. The broader pre-existing engine writers were not changed by this scoped repair.

The separately forwarded maintenance draft was independently reviewed and preserved byte-for-byte outside executable source. Its checkpoint, dependency and shared-environment issues are documented in [handoff reconciliation](../docs/HANDOFF-RECONCILIATION.md); none of its executable changes was applied.

23 offline AI protocol/privacy tests cover three fixed provider adapters, local keyless guidance, session-only key connection, exact-preview approval, free-account acknowledgement, simulation rejection, redirect refusal, response/deadline bounds, key echoes, unsupported/truncated responses, quota errors and no retries/fallback. Separate HTTP/UI checks verify authorization, conflict responses and local simulated guidance. No new-provider inference call was made: account eligibility, keys, quotas and actual generated answers remain unverified.

Actual Chromium interactions exercised the 100-action catalog, all ten browser controls, saved favorites, explicit profile Apply, JSON/ZIP downloads, keyboard focus, denied storage, CSP and the unchanged countdown/pause flow. The final AI UI was exercised with completed synthetic reports and local fixtures: built-in guidance works without keys, cloud approval resets on selection changes, two acknowledgements are required, key fields clear, and results render as text. No external AI service was contacted. At 400 pixels and 125% text size the page had no horizontal overflow. Public screenshots are visibly labeled simulations.

All 30 native read-only diagnostics were also exercised against the existing selected tools on the owner's Windows laptop. The local audit recorded 19 observed results, 10 review findings, and one independently unavailable dashboard-lifecycle observation without reading its private capability. Review findings included memory/restart readiness, PATH routing, preserved junction aliases, partial storage totals, ownership-marker gaps and unsigned executables. Official Node/npm catalogs, Python dependency consistency, editor extensions, matched Playwright cache and certificate-verified TLS probes succeeded. The bounded storage scan reports partial totals rather than pretending it scanned everything. Private audit details remain outside Git.

PR #1's exact documentation head was independently reviewed: 100 unique roadmap rows, valid dependency DAG, complete fields, immutable source targets and green Windows/Linux checks. It merged at `87c21ddd8ed176d7924140a0b1c33ac9ce641b7f`. Its proposal inventory is separate from the implemented Feature Studio catalog; [status reconciliation](../docs/ROADMAP-STATUS.md) records counterparts, partial coverage and planned work.

The release build and payload/migration checks establish source-byte correspondence. GitHub CI repeats checks at published commits, and release assets are verified by downloading them again. No version 3.0 full-tool reinstall or extra paid model round trip was needed for this dashboard/report expansion. The actual full-install observations below belong to earlier builds and are retained as historical evidence.

## Application checks

The earlier 2.0.4 line had 116 passing regression tests. Coverage includes interpreter selection with a full selected-pack wheel solution, explicit resolution rejection versus transport errors, hashed package locks, pack imports and version matching, candidate preservation, exact-channel timeout retries, WebView2 registry verification, catalog mismatches, native PowerShell JSON under a foreign module search path, safe original PATH backups, npm version/warning separation, and concurrent HTTP report reads while reports are replaced. Signed local Terminal recovery and exact per-user Canary side-by-side installation have dedicated failure and cancellation checks.

Existing coverage also checks architecture/release selection, secret redaction, archive traversal, Windows junctions, configuration conflict preservation, ownership-limited cleanup, process exit evidence, local capability/origin/Host checks, simulation labeling, and rejection of a second worker. Astra independently reviewed the earlier 2.0.2 repair. The 2.0.3 npm and .NET changes were additionally checked through regression tests and actual isolated runtime/package operations.

The JavaScript parser check passes. The release build regenerates every embedded source byte and its SHA-256 manifest. CI runs application and payload tests on Windows and Linux; Windows additionally runs the 23 setup/security tests under Windows PowerShell 5.1 and PowerShell 7 plus real CMD extraction and NoLaunch bootstrap.

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

Version 2.0.4 discovers doctor --json support and preserves each non-ok check, warning/failure counts, details and remediation in the report rather than a truncated text tail. Regression checks cover warning retention, failure classification, malformed output and secret redaction.
