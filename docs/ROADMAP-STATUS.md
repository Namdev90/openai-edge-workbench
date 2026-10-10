# Roadmap and implemented feature status

The [Feature Studio catalog](../source/feature_hub.py) implements 100 registered actions. The [100 capability proposals](../FEATURE-PROPOSALS.md) describe a different roadmap assessed against the earlier v2.0.4 source snapshot, `e24318beb4b2db0cd62fef62e48c1eee96a93593`. They are separate inventories: merging the proposal document adds no executable features and does not establish 200 implemented capabilities.

Use explicit namespaces when referring to an item:

| Inventory | Example | Meaning |
| --- | --- | --- |
| Roadmap | `roadmap:F041` | A proposal and its full acceptance criteria in FEATURE-PROPOSALS.md. |
| Feature Studio | `studio:f061` | A registered action in the implemented application catalog. |

The shared number does not imply a relationship. For example, `roadmap:F041` is a run-history browser, while `studio:f041` is an installation timeline analysis. The mapping below follows behavior and acceptance criteria rather than matching numbers.

## How to read the status

- **Current counterpart:** the implemented application offers the principal proposed user operation. The table identifies its limits and evidence; this label does not certify every acceptance criterion.
- **Partial:** implemented actions support part of the proposal, but the listed remaining operation or acceptance requirement is absent.
- **Planned:** no implemented user operation satisfies the proposal as described. Existing installation/report primitives can still provide useful foundations.
- **Complete:** reserve this label for a proposal whose full acceptance criteria have been met, with implementation, relevant offline tests, and separately identified real Windows acceptance evidence linked. A merged document, a registered button, green generic CI, or a successful installation is insufficient.

This reconciliation identifies 2 current counterparts, 18 partial proposals, and 80 planned proposals. It assigns no blanket **Complete** status. The implemented action count remains 100. These are implementation mappings, not a promise to execute roadmap work automatically.

## Current counterparts

| Roadmap proposal | Implemented counterpart | Current behavior | Acceptance and evidence boundary |
| --- | --- | --- | --- |
| `roadmap:F007` — Cost-free maintenance mode | `studio:f071` — Full workshop without model requests profile | Returns an explicit selection with every optional pack enabled except `live`; applying it updates selections, and installation requires a separate start action. The generated plan excludes the Codex model-request step. | Offline profile tests verify distinct valid selections and that profile generation does not start installation. A controlled real run and request evidence are separate from this offline guarantee. This operation does not remove network downloads or establish a provider's billing policy. Manually selecting the live test later changes the selection. |
| `roadmap:F041` — Local run-history browser | Completed-report picker and history endpoint; `studio:f061` — Run outcome history | Selects a supported completed installation report and shows dated run identifiers and outcome summaries. Report analyses use the selected run; partial or invalid reports are excluded by the history service. | History service and report tests cover supported folder identities, completed reports, exclusions, and simulation labeling. Actual local history and browser behavior require their own Windows/UI observation. Listing a report does not re-run its checks, read private backups, or make its old observations current. |

## Partially covered proposals

| Roadmap proposal | Existing Feature Studio actions | Implemented portion | Remaining proposal requirement |
| --- | --- | --- | --- |
| `roadmap:F001` — Read-only change-plan preview | `studio:f076` | Preview the selected options and actual generated step names before starting installation. | Discover and display exact installed/target versions, origins, planned changes, and uncertainty before mutation across adapters. |
| `roadmap:F003` — Named toolkit recipes | `studio:f066`–`studio:f075`, `studio:f087`–`studio:f089` | Built-in profiles and one locally saved selection recipe, loaded for explicit review. | Multiple named user recipes and per-component execution dependency semantics. The current recipe stores the eight supported pack options; core tools remain included. |
| `roadmap:F004` — Preflight readiness gate | `studio:f001`, `studio:f003`, `studio:f021` | Architecture, free-space, and curated package-manager readiness observations. | A unified pre-download gate with declared blocking/advisory reasons, permissions evidence, and supported next actions. Individual diagnostics do not automatically gate installation. |
| `roadmap:F008` — Review queue for unresolved findings | `studio:f033`, `studio:f060` | Read-only review-needed outcomes and recurring unresolved step summaries. | Persistent owner-selected resolve/defer state and evidence-matched recheck closure. |
| `roadmap:F009` — Side-effect permission matrix | `studio:f078` | Lists selected catalog operations, sources, possible Windows approvals, and whether the model request is selected. | Adapter-level UAC, restart, network, and configuration declarations with unknown-impact enforcement before unattended execution. |
| `roadmap:F011` — Publisher-versus-catalog freshness board | `studio:f023`–`studio:f025`, `studio:f064` | Official Node/npm/.NET catalog observations and recorded catalog-versus-installed application versions. | A consolidated publisher-versus-WinGet freshness board across supported tools with timestamped upstream evidence and unavailable states. Catalog currency alone does not prove upstream latestness. |
| `roadmap:F012` — Release eligibility explainer | `studio:f037`, `studio:f038` | Recorded Python resolver decisions and npm host/runtime compatibility explanations. | A complete considered-candidate view across tools, including architecture and channel eligibility with operational errors separated from incompatibility. |
| `roadmap:F017` — Tool compatibility graph | `studio:f077` | A curated description of runtime dependencies and preservation/isolation boundaries. | Checked graph edges, incompatible candidate visualization, evidence timestamps, and explicit unknown constraints. A static dependency description is not a resolver proof. |
| `roadmap:F024` — Network-route diagnostic map | `studio:f027`, `studio:f035` | Bounded official-host TLS checks and recorded HTTP transport/service-access distinctions. | Layered DNS, TLS, proxy, and endpoint diagnosis in one bounded route map. Reachability does not establish authentication or service functionality. |
| `roadmap:F035` — PATH conflict resolution preview | `studio:f008`, `studio:f009` | Inspect current-process CLI collisions and managed command resolution. | Fresh-shell effective resolution plus a backed-up, explicitly approved user PATH change preview. Diagnostics do not rewrite PATH. |
| `roadmap:F042` — Semantic report comparison | `studio:f058`, `studio:f059`, `studio:f086` | Compare recorded step outcomes and managed versions against a predecessor; export a two-run comparison. | Explicit cross-schema reconciliation and check-scope changes, with missing evidence distinguished from regressions. A status or version difference does not prove a new machine failure. |
| `roadmap:F043` — Concise paste-back summary builder | `studio:f032`, `studio:f082` | Failure triage and a downloadable readable report table. | A bounded paste summary combining failures, new changes, next actions, run/source identifiers, and an omitted-detail count. A full Markdown export is not that summary. |
| `roadmap:F045` — Machine-readable repair case export | `studio:f081`, `studio:f085` | Export the selected diagnostic as JSON or a local support bundle. | A separate versioned repair-case schema, structured action/evidence scopes, validated round-trip import, and rejection of executable instructions. Exported diagnostics are not imported repair plans. |
| `roadmap:F046` — Offline remediation decision trees | `studio:f032`, `studio:f045` | Deterministic evidence-text classification with bounded review suggestions and no automatic retries or repairs. | Curated supported failure-code decision trees with documented branches and explicit unknown-code behavior. A category suggestion is not a diagnosed root cause. |
| `roadmap:F047` — Diagnostic provenance timeline | `studio:f041` | Calculate valid installation step durations and retain missing/inconsistent times as unknown. | Correlate transaction journal, checks, activation, and repair events using operation identities and timestamps. A duration timeline does not establish event ordering absent those records. |
| `roadmap:F052` — Managed shell resolution matrix | `studio:f008`, `studio:f009` | Inspect CLI collisions and current-process command routing. | Exercise ordinary and Edge terminals across PowerShell 5.1, PowerShell 7, and CMD; compare observed path/version results without global changes. |
| `roadmap:F091` — Workbench SBOM export | `studio:f047`, `studio:f081` | Recorded managed tool/package manifests and diagnostic JSON export. | Supported SPDX/CycloneDX output with installed metadata, hashes, license records, and source references. A version list is not a standardized SBOM. |
| `roadmap:F095` — Managed installation ownership ledger | `studio:f011`, `studio:f013`, `studio:f053` | Inspect owned generations and ownership markers; summarize recorded managed cleanup. | Source/run/path ownership receipts and an inspectable change ledger that protects externally modified targets. An ownership marker or observed application name does not establish a full receipt. |

## Planned proposals

The following proposals retain **Planned** status. Their detailed user operation, dependencies, and acceptance criteria remain in [FEATURE-PROPOSALS.md](../FEATURE-PROPOSALS.md). Listing a related installed tool or a report field does not complete the proposed workflow.

| Roadmap area | Planned proposal IDs |
| --- | --- |
| Planning and maintenance | `roadmap:F002`, `roadmap:F005`, `roadmap:F006`, `roadmap:F010` |
| Release intelligence | `roadmap:F013`, `roadmap:F014`, `roadmap:F015`, `roadmap:F016`, `roadmap:F018`, `roadmap:F019`, `roadmap:F020` |
| Download and cache operations | `roadmap:F021`, `roadmap:F022`, `roadmap:F023`, `roadmap:F025`, `roadmap:F026`, `roadmap:F027`, `roadmap:F028`, `roadmap:F029`, `roadmap:F030` |
| Recoverable transactions | `roadmap:F031`, `roadmap:F032`, `roadmap:F033`, `roadmap:F034`, `roadmap:F036`, `roadmap:F037`, `roadmap:F038`, `roadmap:F039`, `roadmap:F040` |
| Diagnostic handoff | `roadmap:F044`, `roadmap:F048`, `roadmap:F049`, `roadmap:F050` |
| Verification workspaces | `roadmap:F051`, `roadmap:F053`, `roadmap:F054`, `roadmap:F055`, `roadmap:F056`, `roadmap:F057`, `roadmap:F058`, `roadmap:F059`, `roadmap:F060` |
| Supported migration operations | `roadmap:F061`, `roadmap:F062`, `roadmap:F063`, `roadmap:F064`, `roadmap:F065`, `roadmap:F066`, `roadmap:F067`, `roadmap:F068`, `roadmap:F069`, `roadmap:F070` |
| Local task and project utilities | `roadmap:F071`, `roadmap:F072`, `roadmap:F073`, `roadmap:F074`, `roadmap:F075`, `roadmap:F076`, `roadmap:F077`, `roadmap:F078`, `roadmap:F079`, `roadmap:F080` |
| Platform and curated toolchains | `roadmap:F081`, `roadmap:F082`, `roadmap:F083`, `roadmap:F084`, `roadmap:F085`, `roadmap:F086`, `roadmap:F087`, `roadmap:F088`, `roadmap:F089`, `roadmap:F090` |
| Trust and maintainer operations | `roadmap:F092`, `roadmap:F093`, `roadmap:F094`, `roadmap:F096`, `roadmap:F097`, `roadmap:F098`, `roadmap:F099`, `roadmap:F100` |

## Evidence used for this reconciliation

Implementation references:

- [Feature registry and completed-report context](../source/feature_hub.py).
- [Live read-only diagnostics](../source/feature_diagnostics.py).
- [Evidence-only report analyses](../source/feature_reports.py).
- [Profiles, previews, local exports, and selection recipe](../source/feature_plans.py).
- [Dashboard controls](../source/app.js) and [interface](../source/index.html).

Relevant offline evidence:

- [Feature service tests](../source/tests/test_feature_hub.py) cover catalog identities, supported inputs, report-history exclusions, simulation, and job admission.
- [Report analysis tests](../source/tests/test_feature_reports.py) cover incomplete/simulated evidence, selected-run comparisons, boundaries, and read-only behavior.
- [Plan and export tests](../source/tests/test_feature_plans.py) cover explicit previews, recipe behavior, HTML escaping, CSV handling, and local bundles.
- [Dashboard feature tests](../source/tests/test_dashboard_features.py) cover browser controls and explicit profile application.

Offline fixtures prove the assertions under test. Real Windows observations, installer results, browser checks, sign-in evidence, and quota-consuming model tests must be linked separately in the [verification record](../source/VERIFICATION.md). None of these evidence classes substitutes for another. A historical report is an observation from its recorded run, not a present health check.

Update this page when behavior changes. For any transition to **Complete**, identify the implementation commit or PR, the exact acceptance criteria met, the relevant offline checks, any required real Windows evidence, and unresolved limitations. Preserve the original roadmap identifiers and keep Feature Studio identifiers separate.
