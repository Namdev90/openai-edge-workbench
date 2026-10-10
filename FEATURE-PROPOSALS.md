# 100 new capability proposals

Documentation proposal only; none of these capabilities is implemented by this PR.
This community utility is independent of OpenAI. Priorities are recommendations,
not promises or an instruction to start 100 implementation jobs.

## Evidence and novelty boundary

Reviewed main at [`e24318b`](https://github.com/Namdev90/openai-edge-workbench/tree/e24318beb4b2db0cd62fef62e48c1eee96a93593)
on 10 October 2026. Repository-wide file inventory found no AGENTS.md,
CONTRIBUTING file or .agents/skills directory. The open-PR query returned zero
open PRs at review time; this is a snapshot, not a lock on concurrent work.

Evidence keys below refer to that immutable snapshot:

- **E1**: [engine](https://github.com/Namdev90/openai-edge-workbench/blob/e24318beb4b2db0cd62fef62e48c1eee96a93593/source/engine.py), especially `build_plan`, `execute`, package adapters and candidate activation.
- **E2**: [dashboard](https://github.com/Namdev90/openai-edge-workbench/blob/e24318beb4b2db0cd62fef62e48c1eee96a93593/source/index.html), [client](https://github.com/Namdev90/openai-edge-workbench/blob/e24318beb4b2db0cd62fef62e48c1eee96a93593/source/app.js) and [bounded API](https://github.com/Namdev90/openai-edge-workbench/blob/e24318beb4b2db0cd62fef62e48c1eee96a93593/source/app.py).
- **E3**: [current scope](https://github.com/Namdev90/openai-edge-workbench/blob/e24318beb4b2db0cd62fef62e48c1eee96a93593/source/README.md) and [feature reconciliation](https://github.com/Namdev90/openai-edge-workbench/blob/e24318beb4b2db0cd62fef62e48c1eee96a93593/FEATURES.md).
- **E4**: [setup](https://github.com/Namdev90/openai-edge-workbench/blob/e24318beb4b2db0cd62fef62e48c1eee96a93593/SETUP.md), [updater](https://github.com/Namdev90/openai-edge-workbench/blob/e24318beb4b2db0cd62fef62e48c1eee96a93593/Setup.ps1) and [release manifest](https://github.com/Namdev90/openai-edge-workbench/blob/e24318beb4b2db0cd62fef62e48c1eee96a93593/release.json).
- **E5**: [verification record](https://github.com/Namdev90/openai-edge-workbench/blob/e24318beb4b2db0cd62fef62e48c1eee96a93593/source/VERIFICATION.md), [tests](https://github.com/Namdev90/openai-edge-workbench/tree/e24318beb4b2db0cd62fef62e48c1eee96a93593/source/tests) and [design/plan](https://github.com/Namdev90/openai-edge-workbench/tree/e24318beb4b2db0cd62fef62e48c1eee96a93593/source/docs).
- **E6**: [migration boundaries](https://github.com/Namdev90/openai-edge-workbench/blob/e24318beb4b2db0cd62fef62e48c1eee96a93593/MIGRATION.md) and [alternatives](https://github.com/Namdev90/openai-edge-workbench/blob/e24318beb4b2db0cd62fef62e48c1eee96a93593/ALTERNATIVES.md).

Already present and **not counted**: one-command launch/update, pack selection,
countdown, live logs, stop-after-command, cached verified source, Node nightly,
compatible npm host, full Python wheel preflight, hashed Python locks, preview
desktop channels, .NET daily, SDK staging, default-profile settings/extension
migration, PATH backup, managed cleanup, sign-in/provider/MCP inventory,
documentation MCP, optional live Codex request, structured doctor warnings,
redaction, report copying, simulation and payload tests.

Also **not counted**: resurrecting archived Go/ripgrep/LibreOffice/ImageMagick/Zotero
packs, legacy audit-only/rollback/sign-in buttons or weekly maintenance tasks.
Those are recovered capabilities, not new ideas. Generic performance, styling,
redaction and test-coverage improvements are excluded as standalone features.

Each row introduces a distinct user operation or subsystem absent from the
reviewed active design. Some use existing primitives; the gap column names the
additional operation rather than relabeling the primitive as new. Absence is an
inference from reviewed source/docs, not proof about unpublished work or every
historical conversation. Recheck main and other PRs before implementing any row.

## Delivery rules and sequence

- **P1**: first roadmap tranche, directly supports reliable Windows maintenance.
- **P2**: next tranche, useful workflow expansion after prerequisites land.
- **P3**: optional specialized capability; validate demand before committing effort.
- Dependencies use `Fnnn` IDs; `base` means existing application primitives plus
  capability-specific design/tests. Each section identifies its evidence basis.
- Prefer the latest official publicly available prerelease for newly supported
  tools. Show catalog lag and compatibility exclusions. Do not silently downgrade.
- A plan is not permission to run it. No arbitrary shell/download API, credential
  extraction, security-policy bypass, automatic purchases, forced removals, machine
  PATH changes or hidden background maintenance. Any external model use requires
  an explicit cost warning and an intentional user action in the relevant flow.
- Scope restore/migration to supported formats and Workbench-owned data. Preserve
  settings, original programs and project environments; preview conflicts first.
- Every implementation needs offline fixtures plus the relevant real Windows
  acceptance evidence. CI cannot certify laptop installs, account access, desktop
  UI or OAuth. Keep those evidence classes separate.

Recommended start: F001, F002, F004, F007, F011, F021, F042 and F052.
Then F005/F006, transaction recovery, diagnostic comparisons and migration
workflows. Specialized packs and project helpers follow demonstrated demand.
Dependencies establish ordering, not mandatory bundling into a single large PR.

## A. Planning and user-controlled maintenance

Basis: E1/E2/E3. Today there is one full-run start action with broad pack choices;
there is no persisted, inspectable approval plan or selective operation queue.

| ID | New capability | Priority | User value and current gap | Acceptance criteria | Dependencies |
| --- | --- | --- | --- | --- | --- |
| F001 | Read-only change-plan preview | P1 | Know exactly what will change; current plan names steps but discovers targets during execution. | Show installed/target versions, origin, actions and uncertainty before mutation; preview performs no installs. | base |
| F002 | Per-component opt-in execution | P1 | Repair one component without re-running core installs; current core is always included. | Select individual plan items; required dependencies appear explicitly; unselected tools receive no mutation. | F001 |
| F003 | Named toolkit recipes | P2 | Reuse a personal minimal/document/science selection; choices currently belong to a run. | Save/load named selections locally; schema validation rejects unknown actions; current all-tools shortcut remains available. | F002 |
| F004 | Preflight readiness gate | P1 | Discover missing App Installer, unsupported architecture and permissions before downloads. | Read-only checks produce blocking/advisory reasons and supported next actions; no UAC or installation in preflight. | F001 |
| F005 | Disk allocation planner | P1 | Avoid filling the laptop; only general GB warnings exist. | Estimate download, staging and retained generations per volume; block proven insufficient space; mark unknown sizes. | F001 |
| F006 | Metered-network budget | P2 | Control bandwidth without abandoning latest previews; no download budget exists. | User sets run byte ceiling; known downloads are checked against it; unknown sizes require review; report actual managed bytes. | F001 |
| F007 | Cost-free maintenance mode | P1 | One intentional mode guarantees no model request; currently a live checkbox defaults on. | Mode excludes all quota/API calls from the generated plan; sign-in/transport checks remain labeled separately. | F001 |
| F008 | Review queue for unresolved findings | P2 | Track items requiring a decision instead of losing them in reports. | Persist redacted findings with owner-selected resolve/defer status; recheck can close only matching evidence. | F042 |
| F009 | Side-effect permission matrix | P2 | Understand each planned operation's UAC, restart, network and configuration impact. | Show declared impacts per adapter; unknown impact prevents unattended execution of that item. | F001 |
| F010 | Installer decision checkpoint | P2 | Avoid an unexpected interactive installer in a long run; current worker executes sequentially. | Pause before adapters declared interactive; display expected Windows prompt; continue only on user action. | F009 |

## B. Release intelligence

Basis: E1/E3/E4. Current selection policies resolve live catalogs and record selected
versions; they do not offer comparative release intelligence or eligibility views.

| ID | New capability | Priority | User value and current gap | Acceptance criteria | Dependencies |
| --- | --- | --- | --- | --- | --- |
| F011 | Publisher-versus-catalog freshness board | P1 | Distinguish latest official build from WinGet lag across tools. | Compare official advertised version/channel with configured catalog and local version; show timestamp and unavailable evidence. | base |
| F012 | Release eligibility explainer | P1 | Understand why a newer release cannot be selected; rejection evidence is currently report-oriented. | Present all considered candidates with architecture, engine/wheel and channel rejection reasons; never label network errors incompatible. | F011 |
| F013 | Official release-note inbox | P2 | Read what changed before an experimental upgrade; no consolidated release-note flow exists. | Link publisher notes for installed-to-target releases; never infer missing notes; no fetched HTML/script execution. | F011 |
| F014 | Time-limited version hold | P2 | Keep a known working managed tool during a deadline without changing default preview policy. | Explicit per-tool hold with expiry/reason; discoveries still show latest; report held updates; no automatic downgrade. | F002, F011 |
| F015 | Opt-in known-bad release quarantine | P2 | Avoid a documented broken preview until a newer official release appears. | Local exclusions require evidence and expiry; list excluded exact versions; no silent stable fallback. | F012 |
| F016 | Withdrawal and revocation monitor on launch | P2 | Detect a removed official release already installed; current updater only seeks newer candidates. | Recheck publisher withdrawal/revocation evidence on user launch; flag affected generations; never uninstall automatically. | F011 |
| F017 | Tool compatibility graph | P2 | See Node/npm, Python/wheels and browser/Playwright constraints together. | Render checked dependency edges and incompatible candidates with evidence timestamps; unknown constraints remain unknown. | F012 |
| F018 | Immutable resolution-plan export | P1 | Review or reproduce an entire selected run; current locks cover Python rather than all adapters. | Export exact sources, versions, hashes and platform per item without secrets; import refuses stale/unsupported plans unless re-resolved. | F001, F012 |
| F019 | Public channel availability matrix | P2 | Avoid assuming every desktop tool has a nightly or private beta. | For each supported architecture show official public channels and unavailable channels with publisher references. | F011 |
| F020 | Signature identity change review | P2 | Catch an unexpected publisher change between versions; current signatures are checked per selected installer. | Compare expected signer identities across releases; changed/unrecognized identity blocks that adapter pending explicit review. | F011 |

## C. Download and cache operations

Basis: E1/E4. There are trusted downloads, hashes and cached application fallback,
but no user-managed package cache, transport planner or offline kit workflow.

| ID | New capability | Priority | User value and current gap | Acceptance criteria | Dependencies |
| --- | --- | --- | --- | --- | --- |
| F021 | Resumable verified downloads | P1 | Recover interrupted large downloads; current retries restart work. | Resume only with matching immutable identity/ETag; verify complete hash/signature; changed identity restarts cleanly. | base |
| F022 | Content-addressed artifact cache | P1 | Reuse identical verified installers across runs; cached source fallback is not a package cache. | Key artifacts by digest, retain provenance, reverify before reuse; no auth/config content is cached. | F018 |
| F023 | User-selected offline preparation kit | P2 | Prepare a supported setup on another connected Windows machine. | Export allowed redistributable artifacts plus manifest; exclude Store/OAuth-only items and secrets; import verifies every artifact. | F018, F022 |
| F024 | Network-route diagnostic map | P1 | Explain DNS, TLS, proxy and endpoint failures; current HEAD checks only summarize transport. | Bounded read-only probes separate failure layers; redact addresses; never disable TLS or alter proxy policy. | base |
| F025 | Authenticated enterprise proxy support | P2 | Download behind a managed proxy without leaking credentials. | Use supported OS credential handling; honor user policy; no passwords/tokens in URLs, logs, reports or exported plans. | F024 |
| F026 | Download rate limiter | P2 | Keep video calls usable during setup; no managed rate control exists. | Apply user byte-per-second cap to Workbench transfers; identify external installer transfers that cannot be controlled. | F006 |
| F027 | Cache inspection and eviction preview | P2 | Reclaim cached downloads intentionally; existing cleanup targets runtime generations. | Show artifact size, last use and pinned-kit references; confirm exact eviction set; protect active downloads and kits. | F022 |
| F028 | Read-only download rehearsal | P1 | Check access to selected official assets before installation. | Validate metadata, redirects and availability without invoking executables; distinguish restricted assets and failed transport. | F018, F024 |
| F029 | Integrity failure evidence bundle | P1 | Give maintainers usable checksum/signature failure evidence without executing a suspect file. | Export expected/observed digest, sanitized origin and signer result; quarantine locally; no executable in default share bundle. | F020, F022 |
| F030 | Multi-volume staging chooser | P2 | Use another drive for temporary downloads on a small system SSD. | Validate chosen staging volume, permissions and free space; preserve final managed locations; reject reparse-path escapes. | F005, F022 |

## D. Recoverable transactions

Basis: E1/E3/E4. Candidate preservation and owned-generation cleanup exist. The
new operations below add transaction recovery rather than a generic legacy rollback button.

| ID | New capability | Priority | User value and current gap | Acceptance criteria | Dependencies |
| --- | --- | --- | --- | --- | --- |
| F031 | Crash-recovery operation journal | P1 | Understand where a killed run stopped; incremental reports do not provide a replay contract. | Atomically journal started/committed steps; restart detects incomplete operations; replay never blindly repeats a non-idempotent installer. | F018 |
| F032 | Interrupted-run reconciliation | P1 | Resume safely after checking what actually installed. | Compare journal with observed binaries/registrations; propose remaining actions; require review for ambiguous or still-running operations. | F031 |
| F033 | Selective failed-step retry planner | P1 | Retry the failure without redoing unrelated successful changes. | Build fresh exact-channel plan for selected failures and prerequisites; preserve earlier evidence; no hidden stable fallback. | F002, F032 |
| F034 | Managed-generation switchboard | P2 | Select a retained compatible runtime for a specific task; automatic candidate activation has no selection UI. | List owned generations and validated commands; user selects a generation; explain stale/security risk; never remove system tools. | F017, F031 |
| F035 | PATH conflict resolution preview | P1 | Resolve shadowed shims with evidence; current report warns machine commands can win. | Show effective resolution in a fresh shell and proposed user PATH change; backup and consent before editing; machine PATH untouched. | F004 |
| F036 | Scoped change receipt and undo plan | P2 | Reverse a specific Workbench-owned change, beyond a blanket rollback button. | Receipt records pre/post state; undo preview rejects externally modified targets; third-party uninstall is only documented guidance. | F031 |
| F037 | Reboot continuation handoff | P2 | Continue after a requested Windows reboot without hidden tasks. | Export a resumable run shortcut/checkpoint; user reopens after reboot; validate targets before continuing; never initiate reboot. | F032 |
| F038 | Locked-file owner inspector | P1 | Know why a managed generation cannot be changed; current cleanup only retains busy folders. | Identify owning process names via supported Windows APIs; show graceful-close guidance; never kill processes automatically. | F004 |
| F039 | Orphan staging recovery center | P2 | Inspect and reclaim failed candidates absent from active-generation cleanup. | Match staging ownership and journal; display recover/delete choices; reject active, foreign and reparse targets. | F031, F038 |
| F040 | Workbench retirement wizard | P2 | Retire this utility while preserving tools/settings; no supported retirement flow exists. | Preview owned shortcuts/shims and user PATH removal; preserve private backups/reports by default; do not remove third-party apps. | F036 |

## E. Actionable diagnostics and handoff

Basis: E1/E2/E5. Per-run redacted text/JSON and doctor details exist; there is no
cross-run comparison, interactive privacy selection or structured case workflow.

| ID | New capability | Priority | User value and current gap | Acceptance criteria | Dependencies |
| --- | --- | --- | --- | --- | --- |
| F041 | Local run-history browser | P1 | Find earlier diagnostics without opening folders manually. | Enumerate supported report folders, dates and outcome summaries; load read-only; private backups/session files excluded. | base |
| F042 | Semantic report comparison | P1 | See what changed after repair; current reports are isolated snapshots. | Compare versions, statuses and check scopes across two schemas; distinguish missing evidence from regressions. | F041 |
| F043 | Concise paste-back summary builder | P1 | Paste only failures, new changes and next actions; current full report is the single copy target. | Generate bounded summary with run/source IDs and omitted-detail count; full report stays local and available. | F042 |
| F044 | Interactive share-scope selector | P1 | Remove optional personal details before copying rather than relying only on automatic redaction. | Preview exact outgoing text; include/exclude categories; no automatic upload; capability/auth/private backup fields are never selectable. | F043 |
| F045 | Machine-readable repair case export | P2 | Exchange a structured diagnostic case without ambiguous free text. | Export versioned redacted schema with evidence scopes, failures and actions; validate round-trip import; no executable instructions. | F044 |
| F046 | Offline remediation decision trees | P1 | Get bounded next steps from known failure codes; warnings currently carry individual details. | Curated rule chooses supported steps from observed evidence; unknown codes remain unknown; no downloaded repair code executes. | F043 |
| F047 | Diagnostic provenance timeline | P2 | See which checks preceded or followed activation and repairs. | Correlate journal, checks and versions by timestamps/operation IDs; label simulated versus real evidence. | F031, F041 |
| F048 | Evidence freshness meter | P2 | Avoid treating last month's successful login as current health. | Show age and applicable tool/config identity per check; stale observations never become a present VERIFIED status. | F041 |
| F049 | Consent-reviewed bug report draft | P2 | Create a useful repository issue draft from diagnostics without sending it. | Produce editable Markdown with reproduction/evidence/limits; user copies or explicitly submits separately; no private logs attached. | F044, F046 |
| F050 | Privacy-preserving multi-machine comparison | P3 | Compare two user-exported cases for architecture-specific failures. | Local import uses user-chosen pseudonyms and validated schemas; compare tool/platform facts only; no cloud sync or account identities. | F045 |

## F. Verification workspaces

Basis: E1/E5. Imports, versions, browser checks and one Codex round trip exist.
New checks below prove additional specific operations in disposable owned fixtures.

| ID | New capability | Priority | User value and current gap | Acceptance criteria | Dependencies |
| --- | --- | --- | --- | --- | --- |
| F051 | Local document round-trip lab | P1 | Prove DOCX/XLSX/PDF/PPTX operations rather than imports alone. | Generate and reopen known tiny fixtures, assert content, record per-format result; no user documents opened. | base |
| F052 | Managed shell resolution matrix | P1 | Know which command each supported shell will run. | Check ordinary and Edge terminals across PowerShell 5.1/7 and CMD; report path/version differences without altering global configuration. | F035 |
| F053 | Public SDK request-shape lab | P2 | Catch installed SDK API drift without a paid request. | Exercise request serialization against a local mock for installed Python/JS SDKs; distinguish mock results from live authorization. | base |
| F054 | User-launched desktop smoke checklist | P2 | Record actual desktop launch/sign-in observations instead of inferring them from registration. | Guide user through named app checks; attach manual evidence label/time; unconfirmed steps stay unverified. | F045 |
| F055 | Documentation MCP protocol test | P1 | Prove supported initialize/list/read behavior; current configuration inventory/HEAD is insufficient. | Opt-in bounded read-only protocol test against the curated official server; do not connect arbitrary configured MCPs. | base |
| F056 | Loopback provider health adapters | P2 | Identify a configured local router without overriding routing; current check proves only a listener. | Allowlisted documented health/version probes identify service or remain unknown; no secret reads or auto-start. | F024 |
| F057 | Offline model-routing configuration lint | P1 | Catch malformed routing references before an intentional live request. | Validate supported config references/capabilities using local metadata; preserve file bytes; unknown future fields are advisory. | base |
| F058 | Explicitly selected live SDK probe | P3 | Verify API SDK connectivity separately from Codex authentication. | User initiates one bounded request with visible cost warning and existing supported credential flow; no key extraction/creation or repeated billing. | F053, F007 |
| F059 | Experimental-runtime benchmark fixtures | P3 | Decide whether a nightly materially slows the laptop. | Run bounded synthetic fixtures only on user request; compare hardware-tagged results; no model calls or background runs. | F034 |
| F060 | Signed-in integration evidence notebook | P2 | Track connector permissions without asserting installation connected an account. | Manual per-service permitted-action checklist stores redacted outcome/time/scope; no OAuth granting or connector calls without explicit authorization. | F045, F054 |

## G. Supported migration operations

Basis: E1/E3/E6. Current migration copies missing editor settings/snippets and
default-profile extension IDs; it preserves other profiles, projects and credentials.

| ID | New capability | Priority | User value and current gap | Acceptance criteria | Dependencies |
| --- | --- | --- | --- | --- | --- |
| F061 | Multi-profile editor migration map | P1 | Preserve separate editor roles; only the default profile is currently migrated. | Inventory supported profile formats; preview profile-to-profile mappings; no sign-in/secret copying; fixture and real-profile evidence. | F001 |
| F062 | Three-way settings conflict resolver | P1 | Resolve preserved conflicts through a user decision, not silent overwrite. | Show old source, current target and chosen result per supported key; backup; recheck target hash before applying. | F061, F036 |
| F063 | Extension capability compatibility advisor | P2 | Identify unsupported extensions before migration, beyond copying IDs. | Compare declared editor/API/platform requirements with target; report unknown metadata; no uninstall or account transfer. | F061, F019 |
| F064 | Terminal profile migration preview | P2 | Bring selected supported Terminal profiles into Preview; no terminal settings migration exists. | Map documented settings schema; retain target conflicts and sensitive command fields; user approves selected keys. | F036, F062 |
| F065 | Classic data migration readiness guide | P2 | Know what remains before retiring Classic without extracting its private data. | Track official supported export/import steps and user-confirmed validation; no cookie/database scraping or automatic Classic deletion. | F054 |
| F066 | Existing project environment portability audit | P2 | Know which projects rely on old runtimes without mutating them. | User selects directories; read declared manifests only; report interpreter/engine constraints; exclude .env, auth and dependency trees. | F017 |
| F067 | Settings backup restore rehearsal | P1 | Test a backup before applying it; current backups have no rehearsal flow. | Restore supported non-secret settings into a disposable fixture and compare parsed values; never load credentials into a test app. | F036 |
| F068 | User-approved local settings transfer bundle | P2 | Move Workbench preferences and selected non-secret settings to a second laptop. | Exact-file preview and secret exclusions; validated versioned import; no browser profiles, account material or unattended sync. | F003, F061, F067 |
| F069 | Codex config migration impact preview | P2 | Review upstream supported schema changes while preserving routes. | Use versioned documented rules; show proposed diff offline; refuse unsupported transformations; backup and explicit apply. | F057, F036 |
| F070 | Project-specific tool bindings | P2 | Use a managed generation for one project without changing its environment globally. | Generate user-approved local launcher referring to validated generations; preserve manifests and system PATH; warn on missing generation. | F034, F066 |

## H. Local task and project utilities

Basis: E1/E2/E3. Current adapters install tools and run smoke checks; there are no
user task workspaces, project setup flows or sandboxed file-processing operations.

| ID | New capability | Priority | User value and current gap | Acceptance criteria | Dependencies |
| --- | --- | --- | --- | --- | --- |
| F071 | Disposable task workspace launcher | P2 | Start a contained local task with managed tools quickly. | Create user-selected owned scratch directory and Edge terminal; record ownership; no agent/model execution automatically. | F070 |
| F072 | Minimal SDK starter project generator | P2 | Start with examples matching installed SDK versions; installing libraries provides no project. | Generate Python/JS sample plus exact dependency manifest without keys; local mock smoke test; explain live costs before use. | F053, F071 |
| F073 | Notebook kernel registration wizard | P2 | Make the managed Python environment available in a chosen Jupyter/editor context. | Preview scoped kernel registration; verify interpreter; remove only owned registration; no overwrite of existing kernels. | F036, F052 |
| F074 | Dependency manifest drift inspector | P2 | Discover a project's declared versus resolved dependency drift read-only. | Parse supported lock/manifest pairs in selected folder; report discrepancies; never run package lifecycle scripts. | F066 |
| F075 | Local document conversion queue | P3 | Use installed Pandoc/FFmpeg deliberately without an unrestricted command API. | Curated conversion recipes, user-selected inputs and new output folder; no overwrite or macros; bounded process/resource limits. | F051, F071 |
| F076 | Offline dataset profiling workspace | P3 | Inspect a CSV/Parquet safely using installed data libraries. | User selects file; bounded rows/size; produce local schema/null summary; no network uploads or automatic code from data. | F071 |
| F077 | User-selected browser test recorder | P3 | Capture a reproducible local Playwright test rather than only smoke-launching a browser. | New isolated profile and explicit recording start; review generated script; exclude credentials; no personal-profile import. | F071, F044 |
| F078 | Media format compatibility inspector | P3 | Know whether installed FFmpeg can process a file before conversion. | Read metadata with time/size bounds; show codec support; no file modification or external transfer. | F075 |
| F079 | Scientific environment reproducibility capsule | P3 | Reproduce a user-selected scratch experiment beyond global science-pack install. | Export scripts chosen by user, exact dependency metadata and platform facts; exclude datasets/secrets by default; validate offline import. | F018, F071 |
| F080 | Local capability task finder | P2 | Find which installed tools can satisfy a document/data/browser task. | Curated task-to-tool mappings reflect observed availability and verification; never auto-install or execute a selected task. | F011, F051 |

## I. Platform and additional curated toolchains

Basis: E1/E3/E6. These are new scoped integrations, not repackaged archived tool
names. Each requires official source/architecture/compatibility validation first.

| ID | New capability | Priority | User value and current gap | Acceptance criteria | Dependencies |
| --- | --- | --- | --- | --- | --- |
| F081 | Curated Rust development pack | P2 | Support Rust agent tasks; no Rust toolchain is active or in the reconciled archive catalog. | Optional official rustup-managed toolchain in a scoped location; advertised public preview policy; compile tiny fixture; preserve existing Rust. | F002, F019 |
| F082 | Curated Java development pack | P3 | Support JVM tasks with a documented official OpenJDK distribution. | Explicit curated publisher and public early-access channel if available; scoped environment; compile fixture; no license acceptance by stealth. | F002, F019 |
| F083 | C/C++ build prerequisite advisor | P2 | Explain missing Windows build prerequisites without enrolling the laptop in a large install. | Detect documented compiler/SDK requirements and installed versions; user chooses any later installer; no automatic Visual Studio workload changes. | F004, F066 |
| F084 | Native ARM64 versus emulation advisor | P1 | Explain architecture mismatches instead of merely selecting an archive. | Compare actual executable architecture, shell and selected artifacts; identify emulation/unsupported combinations with evidence. | F004, F012 |
| F085 | GPU compute readiness report | P3 | Determine whether a chosen scientific workload can use existing hardware. | Read supported hardware/driver facts, match curated requirements; no driver update, CUDA install or unsupported bypass. | F004 |
| F086 | WSL interoperability readiness report | P3 | Help an existing WSL user understand Windows/Linux tool boundaries. | User-requested read-only existing-distro inventory; explain path/runtime separation; do not enable WSL or run distro setup scripts. | F052 |
| F087 | Existing container engine readiness report | P3 | Clarify whether a project can use an already installed Docker/Podman engine. | Query documented status only on request; no engine install/start, image pull, privilege escalation or socket exposure. | F066 |
| F088 | Screen-reader operation mode | P2 | Make the graphical maintenance workflow usable without visual table/log scanning. | Keyboard task flow and concise live announcements for operation transitions; verify with a real Windows screen reader; no log flooding. | F001 |
| F089 | Guided offline-language packs | P3 | Offer supported translated operation explanations without a translation service. | Versioned local translations for plan/status/remediation; exact technical IDs remain stable; missing strings fall back visibly. | F046 |
| F090 | Organization policy compatibility report | P2 | Explain blocked installers without weakening managed Windows security. | Read supported AppLocker/WDAC/package policy evidence where permitted; report unavailable access; offer policy-owner guidance only. | F004, F024 |

## J. Trust, ownership and maintainer operations

Basis: E1/E4/E5. Byte-corresponding payloads, local authorization, signatures and
owned cleanup exist. These proposals add inspectable trust/ownership workflows.

| ID | New capability | Priority | User value and current gap | Acceptance criteria | Dependencies |
| --- | --- | --- | --- | --- | --- |
| F091 | Workbench SBOM export | P2 | Know the exact managed inventory and licenses; current reports are not a standardized SBOM. | Export supported SPDX/CycloneDX records from installed metadata with hashes and source refs; unknown license/provenance stays explicit. | F018 |
| F092 | Opt-in public advisory assessment | P2 | Know whether a managed dependency has a published vulnerability. | Query a documented advisory source after user action; match exact versions and timestamp; advise without blanket updates or removals. | F091 |
| F093 | Independent build provenance verifier | P2 | Check whether a downloaded Workbench release corresponds to a published build attestation, beyond embedded hashes. | Verify supported published attestation identity and commit when available; absent attestation is not fabricated; fail closed on mismatch. | F020 |
| F094 | Dependency license review sheet | P3 | Review obligations before distributing an offline kit. | Derive license metadata and publisher links for selected artifacts; flag unknown redistribution rights; no legal assurance implied. | F091, F023 |
| F095 | Managed installation ownership ledger | P1 | Explain exactly what this utility owns versus observed third-party software. | Record ownership receipts with source/run/paths; inventory never claims ownership from name alone; protect externally modified items. | F031 |
| F096 | Private-backup access review | P1 | Detect overbroad permissions without sharing backup content. | Inspect ACL metadata only for owned private directories; report scope; supported correction requires preview and intentional user action. | F095 |
| F097 | Local report retention planner | P2 | Keep useful evidence while limiting disk/privacy accumulation; runtime cleanup does not manage reports. | Show dated report sizes and user retention choices; preserve active/pinned cases; exact deletion preview; private backups excluded. | F041, F095 |
| F098 | Maintainer adapter fixture replay | P2 | Reproduce a redacted failure without installing tools on a contributor laptop. | Validated case maps to curated fixtures/mocks; replay cannot execute commands embedded in imported data; label all simulated output. | F045 |
| F099 | Curated adapter certification checklist | P2 | Decide whether a new tool integration is ready rather than trusting green generic CI. | Require official source, architecture, preview policy, impact, preservation, failure and real Windows evidence per adapter; publish unmet criteria. | F009, F019, F098 |
| F100 | Roadmap-to-evidence completion board | P2 | Track which proposed user operations actually shipped and were verified. | Map stable feature IDs to implementation PRs, offline tests and separately labeled real-machine observations; never infer completion from merge alone. | F099 |

## Review and validation contract

Exactly 100 proposal rows (F001-F100), unique titles and IDs. Group headings and
existing-capability exclusions are not additional features. Dependencies form a
directed acyclic graph; all referenced IDs must exist. Cross-section overlaps
are intentional prerequisites, not duplicate outcomes: planning decides scope,
release intelligence selects targets, transport retrieves them, transactions
recover changes, diagnostics communicates evidence, and verification proves
specific operations.

Novelty review compared every row with E1-E6 and the active API/plan. Recovered
legacy tools and generic improvements were removed from the count. Future
unpublished work could still overlap; implementation owners must revalidate.

For this documentation PR: validate count/uniqueness, complete row fields,
dependency references/cycles, local and immutable source links, Markdown table
shape and `git diff --check`; run application, payload and migration checks.
Do not run an installer, bootstrap launcher, sign-in, live model request or
package update just to validate this proposal.

Only `.github/workflows/verify.yml` is active at the reviewed snapshot. It runs
read-only-repository validation on push/PR, including Windows/Linux tests and
CI-only NoLaunch bootstrap smoke. Archived workflow YAML is inert. No inspected
workflow implements proposed features, deploys them, merges this PR or enables
auto-merge. Repository files cannot establish whether independently configured
GitHub Apps/webhooks exist; check separately before adding automation triggers.
Opening this draft is a proposal for review, not proof that implementation will
start automatically.

Validation performed for this proposal: 100 sequential unique IDs/titles, complete
six-field rows, 33 P1 / 53 P2 / 14 P3 priorities, valid acyclic dependencies and
15 immutable source links with existing checkout targets. `git diff --check`
passed. All 116 application regression tests passed; 23 embedded source files,
the setup CMD correspondence and 20 historical archive hashes verified.
No installer, live model request or account sign-in was invoked. Remote link
targets are grounded in the cloned immutable Git tree; no claim of testing every
external publisher website is made. A fresh main/open-PR check remained unchanged
before publication. The repository hooks query returned no hooks; a separate
installation-metadata query was unavailable, so independent GitHub App behavior
is not established by this review.
