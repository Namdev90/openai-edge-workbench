## Problem and resulting behavior

Describe the concrete problem, the user action that triggers it, and the behavior after this change.

## Validation

List the checks actually run, their results and any checks that remain unverified. Include a sanitized screenshot for meaningful dashboard changes.

- Application regression tests:
- Deterministic build and payload verification:
- Archived migration verification:
- Windows PowerShell / PowerShell 7 setup checks, when relevant:

## Impact and limitations

Identify installation or configuration changes, compatibility boundaries, required permissions, quota costs and any remaining limitations. Delete this prompt if the change has no such impact.

## Review checklist

- [ ] The description reflects the final implementation.
- [ ] User data, credentials, settings and unrelated installations remain protected.
- [ ] New operations use fixed handlers and preserve dashboard capability/origin checks.
- [ ] Relevant tests pass; simulations and unverified checks are labeled honestly.
- [ ] Generated launchers and `release.json` were rebuilt if embedded source changed.
- [ ] No private logs, authentication files, session capabilities or private backups are included.
- [ ] Historical archive bytes and migration provenance remain intact.
