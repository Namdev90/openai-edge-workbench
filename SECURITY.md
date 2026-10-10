# Security policy

## Report privately

Use [GitHub private vulnerability reporting](https://github.com/Namdev90/openai-edge-workbench/security/advisories/new). It is enabled for this repository. Include the affected commit/version, a minimal reproduction and expected impact. Do not post credentials, local session capabilities, private backups or complete laptop logs in a public issue.

The current preview on `main` is the maintained line. Historical installers in `legacy/` are evidence archives, not supported executables. There is no guaranteed response or remediation deadline.

## Trust boundaries

- The short launch trusts the current GitHub launcher. `SETUP.md` provides an independently pinned and SHA-256-checked first download.
- Setup resolves one immutable source commit, validates the complete embedded payload, and runs offline tests. Hashes establish correspondence; they do not establish an independent build attestation.
- The GUI binds to `127.0.0.1`. APIs require a session capability and exact Host; writes require same-origin JSON. No arbitrary command, path or download URL is accepted.
- Feature checks use registered read-only queries and bounded official catalog requests. Report analyses never execute report content. At most two feature jobs run concurrently.
- Recipes are restricted to a marked Workbench-owned directory and eight validated options. Managed paths reject symlinks/junctions. Cleanup preserves active runtimes and unrelated software.
- Credentials remain in native stores. GitHub CLI handles authentication without placing tokens in raw-host URLs. No report or support bundle is uploaded automatically.
- Optional cloud AI reads only a curated summary after explicit preview consent. Its three endpoints/models are fixed; requests reject redirects, cap time/output and never retry or fall back to paid models. A pasted provider key remains only in session memory. Free-tier account/billing eligibility cannot be inferred from the key and requires user confirmation.

Redaction is defense in depth. Review exported diagnostics yourself. Exports omit private backups and authentication/session files, but unusual secret formats may not be recognized. Installation success does not prove cloud permissions; simulation is never real installation evidence.

## Contributor requirements

Follow [CONTRIBUTING.md](CONTRIBUTING.md). Preserve originals, fail visibly on integrity errors, use official sources, and test unsafe paths, conflicts and command failures. Adapters must declare network, configuration, approval and model-quota effects. Generic CI is not proof of a real Windows install.
