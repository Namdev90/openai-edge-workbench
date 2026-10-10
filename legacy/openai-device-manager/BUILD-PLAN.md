# OpenAI Device Manager implementation plan

Goal: a Windows PowerShell 5.1 GUI manager, experimental-first, reversible managed toolchains, reusable GitHub bootstrap, weekly local maintenance, and private redacted support reports.

1. Write offline core tests: release choice, quoting, redaction, scoped deletion, source integrity.
2. Implement process execution with bounded runtime, immutable updater, catalog, GUI and report.
3. Implement Node nightly, managed Codex/SDK/browser/Python and known migrations.
4. Publish to a dedicated branch without modifying main; run Windows CI for parsing and offline tests.
5. Reconcile every requested capability and disclose untested installation/authentication checks.

Constraints: no credential collection, no auto-send, no arbitrary package discovery/install, no disabling Windows security, no unverified removal of existing software. Public experimental releases only. No promise of arbitrary self-programming or future compatibility.
