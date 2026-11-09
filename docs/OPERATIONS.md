# Operate and troubleshoot Workbench

This guide covers the current local dashboard and launcher. Start with [setup](../SETUP.md) for installation; use [development](DEVELOPMENT.md) for an isolated simulation.

## Before starting

1. Launch from the supported setup CMD, desktop shortcut or documented PowerShell command as your normal Windows user.
2. Read the update and integrity result. Setup checks one immutable source commit and the embedded payload before opening the dashboard.
3. Review tool selections before the visible 12-second countdown completes. **Pause auto-start**, a changed selection or reviewing a feature pauses the automatic start.
4. Leave optional model testing disabled unless you intend to use its quota or billing. Software installation, account sign-in and cloud authorization are separate steps.
5. Keep existing projects, private reports and credentials outside public screenshots or issue attachments.

The short PowerShell launcher trusts the current GitHub script. The independently checksum-pinned alternative is in [SETUP.md](../SETUP.md); copying a hash from an untrusted source does not independently establish trust.

## During a run

- Follow the visible step statuses and warnings. A command returning successfully does not erase structured warnings.
- A stop request allows the current command to finish. Wait for the recorded result before starting another run.
- Use **Quit dashboard** when finished. Closing the browser tab alone does not stop the server.
- Do not reuse a bookmarked loopback URL after restarting. Each launch creates a fresh local port and session capability.
- Feature Studio actions have their own prerequisites. Completed-report analyses need a completed run; simulation is labeled and skips real diagnostic commands and catalog probes.

The dashboard is local, not a remotely hosted service. Do not expose it through port forwarding or remove capability, Host or same-origin checks to make a request work.

## Find and interpret evidence

Reports are stored beneath:

```text
%LOCALAPPDATA%\OpenAI-Edge-Workbench\reports\<run-id>\
```

Use the dashboard's report controls rather than editing a report in place. The copyable text report is `Paste-Into-ChatGPT.txt` within that run directory. Feature Studio provides completed-history selection and local JSON, Markdown, CSV, HTML and ZIP exports.

Keep these distinctions when reporting a result:

| Evidence | What it establishes |
| --- | --- |
| Simulation | The simulated flow and fixtures ran; no actual installation is established. |
| `VERIFIED` | The specific recorded check passed. Read the associated details and limits. |
| `CATALOG_CURRENT` | The report's catalog comparison, not perpetual freshness or account access. |
| `REVIEW_NEEDED` or a warning | Further review is still needed, even when a process exit code is zero. |
| Model response | Only the explicitly requested round trip; software installation alone is not cloud verification. |

History intentionally excludes partial, malformed or unsafe reports. It is bounded to recognized directories and completed reports, as described in [architecture](ARCHITECTURE.md).

## Troubleshooting

| Symptom | Safe next step |
| --- | --- |
| Checksum or embedded-payload mismatch | Stop. Obtain a fresh copy through the documented source and compare the exact version/commit. Do not bypass the check or execute a legacy installer. |
| Update cannot be reached | Read the launcher diagnostic. An available cached application must still pass its integrity checks; an offline launch does not prove you have the newest release. |
| Dashboard says another run owns the lock | Find the existing dashboard and finish or quit it normally. The OS releases the lock when its process exits; deleting the lock file is not the normal recovery path. |
| Dashboard/API says to open from its launcher | Reopen through the launcher so the port and session capability match. Never paste `local-session.json` into an issue. |
| A required dashboard asset is missing | Extract a fresh complete launcher copy rather than combining files from different releases. |
| A feature result expired | Session results are bounded. Run that specific action again only when needed; select a valid completed report first for report analyses. |
| A selected preview channel or compatible package set is unavailable | Read the official-source/compatibility failure and preserve the existing working environment. Do not reinterpret it as success or silently substitute a stable version. |
| Install succeeded but an account/tool still cannot be used | Check the recorded executable result and the separate account entitlement/sign-in requirement. Never share tokens to demonstrate access. |
| Optional cloud explanation fails or hits quota | Use built-in guidance. Check the selected provider's current terms and account eligibility; the application does not automatically retry or switch to a paid model. |
| A report is not in history | Confirm the run finished. Partial, malformed or unsafe entries are excluded deliberately; do not change their structure to force acceptance. |

## Guidance and sharing

**Built-in guidance** analyzes recorded outcomes locally without a key, model download or network call. Optional cloud assistance requires choosing a provider, previewing the curated summary and explicitly approving that request. See [AI assistance](AI-ASSIST.md) for exactly what may leave the computer and its dated provider information.

For a public bug report, include:

- Application version/commit, Windows version and architecture.
- Whether the run was real or simulated.
- The selected operation and smallest reproduction.
- Expected behavior and a short, manually reviewed diagnostic excerpt.
- Which checks were actually performed and which remain unverified.

Do not attach authentication files, capabilities, private backups, full personal logs or unreviewed support bundles. Redaction cannot recognize every secret format. Use the [issue templates](https://github.com/Namdev90/openai-edge-workbench/issues/new/choose) for ordinary problems and the [security policy](../SECURITY.md) for vulnerabilities.

## Maintenance limits

Managed cleanup is limited to eligible Workbench-owned generations; it is not a general Windows uninstaller. This guide does not prescribe deleting the application root, user environments or old reports. Preserve material you still need and investigate a specific cleanup problem before removing anything.
