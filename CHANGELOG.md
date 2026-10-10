# Changelog

Preview releases can encounter publisher/channel changes. Version observations describe the checked run, not permanent pins for future toolkit installs.

## 3.0.0-preview.2 — 10 October 2026

- Completed rejected local HTTP requests without leaving small POST bodies unread, preventing intermittent Windows connection resets during bootstrap self-tests. Authorization remains checked before JSON parsing; discarding bytes has a strict size limit and overall deadline.
- Rejected ambiguous or unsupported request framing and preserved the original capability, Host and same-origin protections. No unauthorized action is retried.
- Made failed NoLaunch verification exit with its diagnostic and failure code without opening a modal error window. Interactive launches retain their visible error message.

The targeted update follows an intermittent failure observed while checking the actual installed launcher cache after preview.1 passed CI. Existing toolkit runtimes and configuration are preserved.

## 3.0.0-preview.1 — 10 October 2026

- Added 100 Feature Studio actions: 30 diagnostics, 35 report analyses, 25 profile/plan/export/recipe actions, and ten dashboard controls.
- Redesigned the local dashboard with searchable cards, favorites, a keyboard palette, display preferences and a responsive layout.
- Added completed-report selection, comparison analyses, safe JSON/Markdown/CSV/HTML/ZIP exports, and one owned validated selection recipe.
- Added optional report assistance: immediate local rule-based guidance and three explicitly selected public AI integrations with free-access options. Cloud requests require preview/consent and a suitable free-tier account/key.
- Protected feature jobs with existing capability/origin checks, bounded concurrency, official catalog limits, simulation guards and sensitive-field redaction. Preserved malformed or externally extended recipe files.
- Merged PR #1's separate proposal roadmap and added status reconciliation; its IDs do not define the implemented action catalog.
- Added repository branding, real simulated screenshots, developer/architecture/security guides, contribution templates and documented-catalog checks. Updated pinned CI actions.
- Corrected plan and recipe requests to use the dashboard's current selections. Hardened recipe writes against planted temporary files and preserved the competing unfinished maintenance draft as an inert reviewed archive.

See [verification](source/VERIFICATION.md) for checks and remaining evidence boundaries.

## 2.0.4-preview.1 — 10 October 2026

Preserved structured Codex doctor warnings, failures, details and remediation even when the command exits successfully. Full selected-tool installation completed without failed steps; remaining catalog and review evidence stayed visible.

## 2.0.3-preview.1 — 10 October 2026

Retained the official Node nightly for tools while running newest npm on its own newest compatible official Node host. Verified actual npm execution without the earlier engine warning. Recognized .NET go-live RC development channels and exercised an installed daily SDK with a compiled console fixture.

## 2.0.2-preview.1 — 10 October 2026

Added complete Python wheel-solution preflight and locks, bounded same-channel timeout retries, native WebView2 verification, checked PowerShell reporting, and candidate/configuration preservation fixes driven by the first laptop diagnostic.

## 2.0.0 / 2.0.1-preview.1 — 10 October 2026

Established the standalone repository, recovered historical project archives, protected local dashboard, verified updater and reproducible distribution. [Migration evidence](MIGRATION.md) records archive integrity and conditional branch cleanup.
