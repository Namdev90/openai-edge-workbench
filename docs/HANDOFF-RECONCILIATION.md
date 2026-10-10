# Maintenance-planning handoff reconciliation

Reviewed 10 October 2026. The forwarded maintenance-planning draft was compared in full with the current application source. Its executable changes were **not applied**. The original diff is preserved as an [inert archive](../legacy/maintenance-planning/README.md), not as an installer or supported upgrade path.

The draft was based on commit `87c21ddd8ed176d7924140a0b1c33ac9ce641b7f` and proposed changes to `source/app.py`, `source/engine.py`, and a new `source/maintenance.py`. Its proposed version was `2.1.0-preview.1`. It supplied no corresponding dashboard controls, implementation tests, rebuilt launcher payload, or fresh Windows installation evidence. The active release follows the current source and its own verification record.

## Ideas already represented in the application

The draft overlaps these implemented operations. Matching an idea does not establish every acceptance criterion of its roadmap proposal.

| Draft idea | Current behavior | Remaining boundary |
| --- | --- | --- |
| Toolkit selections | Ten built-in profiles in [Feature Studio](../source/feature_plans.py), including AI essentials, browser, document, science, and .NET selections. | Profiles select the eight supported pack options; core installation steps remain included. They do not provide per-component repair execution. |
| Read-only plan preview | `studio:f076` shows the actual generated steps for selected options; `studio:f077` describes curated runtime dependencies. | This is not an immutable plan with exact versions and hashes for every adapter. |
| Requirements and impact review | `studio:f078` lists selected catalog sources, channels, possible Windows approvals, and whether a model request is selected; `studio:f079` inspects managed runtime isolation. | A complete enforced adapter impact matrix remains separate roadmap work. |
| Saved selections | `studio:f087`–`studio:f089` save, review, and remove one validated selection recipe in the owned Feature Studio workspace. | Multiple named user recipes and individual component execution are not implemented. Loading a recipe requires an explicit dashboard apply action. |
| No model request by default | The all-tools setup path selects the supported packs with the live Codex model check off; `studio:f071` provides the full workshop without model requests profile. Built-in report guidance runs locally without a key or network request. | Downloads and transport checks still use the network. Optional cloud advice requires a separate sanitized preview, consent, and a provider account; the live Codex test can be selected explicitly. |

See [the roadmap status mapping](ROADMAP-STATUS.md) for the distinction between `roadmap:Fnnn` proposals and `studio:fnnn` implemented actions. Their identical numbers do not imply identical functionality.

## Reasons the draft was not applied

The review used the complete diff, the current engine, and pure in-memory calls to the draft's selection planner. No installer, package update, model request, or user configuration change was used to review it.

| Finding | Concrete evidence | Consequence |
| --- | --- | --- |
| Checkpoints lack a usable dashboard continuation flow | The draft worker waits on `checkpoint_event` before each selected WinGet operation when `review_installers` is enabled. This wait occurs before the simulation branch, and the patch adds an API route without dashboard controls. | A real or simulated run can wait indefinitely for an acknowledgement the supplied interface cannot send. Stop or Quit is the available escape; this does not satisfy an installer decision checkpoint workflow. |
| Selecting only Python omits required SDK installation | The draft planner produces `inventory → uv → python → verify → report` for `components=['python']`, with no `python-packages` step. The existing activation code requires `import openai,agents` to succeed in the candidate environment. | The selected candidate is not activated when those imports are absent. A component-level installer needs dependencies that match the activation contract. |
| Selective execution can narrow a shared environment | JavaScript and Playwright operations create a new run environment. Its recorded package set starts from the current candidate, and activation replaces the shared managed JavaScript environment. A selective JavaScript-only or Playwright-only plan does not preserve the other package set. Selected Python packs likewise determine the new environment's package scope. | A seemingly narrow update can remove previously available SDK, browser, document, or science capabilities from the selected managed environment. Old files being retained is different from preserving their active availability. |
| Declared options can disagree with the executed plan | Pure planner inspection shows `components=['git']` returns `options.cleanup=True` while omitting the cleanup step. With `components=['live']` and `cost_free=True`, the requested component list becomes empty, while inventory, verify, and report still run. | Saved selections and diagnostic options can describe operations that were not selected or executed. Removed requests and automatic bookkeeping need explicit, accurate presentation. |
| The readiness and impact metadata contain incorrect or incomplete states | The architecture preview always declares `blocking=False`, although the engine rejects unsupported architectures. `interactive_checkpoint` is true for WinGet rows even when checkpoint review is disabled. OpenAI CLI version lookup uses `openai-cli`, while the active tool key is `openai-api`. | The proposed preview can omit existing version evidence or misstate a gate/checkpoint. It is not an independently validated readiness approval. |
| Named recipe persistence has weaker ownership boundaries | The draft writes a generic root-level `recipes.json`, checks schema and recipe entries without rejecting extra top-level fields, and rewrites the object with only schema and recipes. | A schema-compatible file containing additional user metadata can lose that metadata. A named-recipe extension should preserve unknown data or reject it, and should use the owned workspace rather than introducing a competing persistence location. |
| Shared bookkeeping remains broader than selected components | Inventory and verification are always included. Verification examines existing managed tools and routing. If a runtime is selected, the report operation still writes the shared terminal, workspace inventory, user PATH integration, and shortcut. | Selective execution requires clear shared effects and preservation tests. Filtering installation rows alone does not establish that unselected tools receive no mutation. |

The draft also inherits the existing deterministic temporary-file writer. Any future recipe persistence must check temporary paths and reparse boundaries before writing; validating only the final recipe path is insufficient. The archive is not a certification of that draft or of inherited helpers.

## What can be reused

The draft contains useful design references: explicit dependency reasons, a per-operation impact vocabulary, named selection validation, and an intentional installer pause. These concepts can inform future work after their acceptance criteria are implemented and tested.

Only the read-only metadata concepts are candidates for a small isolated enhancement now, and most are already represented by `studio:f076`–`studio:f079`. No engine, checkpoint, recipe, version, or API changes from the draft were ported. Per-component execution needs coherent dependency resolution, preservation of shared environments, declared shared effects, cancellation behavior, dashboard controls, and meaningful regression evidence before release.

## Major roadmap work still outstanding

The archived patch does not change these statuses:

| Proposal | Current boundary |
| --- | --- |
| `roadmap:F001` — Read-only change-plan preview | Partially represented by a step preview; complete installed/target versions, origins, and planned changes across adapters remain absent. |
| `roadmap:F002` — Per-component opt-in execution | Planned. The current installer includes core steps; the draft does not establish preservation-safe selective execution. |
| `roadmap:F003` — Named toolkit recipes | Partially represented by built-in profiles and one owned selection recipe; multiple named user recipes remain absent. |
| `roadmap:F004` — Preflight readiness gate | Individual diagnostics exist; a unified enforced gate with supported blocking/advisory reasons remains absent. |
| `roadmap:F010` — Installer decision checkpoint | Planned. An API route and waiting event without a complete user flow do not satisfy it. |
| `roadmap:F018` — Immutable resolution-plan export | Planned. Neither a step preview nor the draft pins every adapter's source, version, hash, and platform. |
| `roadmap:F031` — Crash-recovery operation journal | Planned. Incremental diagnostic reports do not establish a safe replay contract. |
| `roadmap:F032` — Interrupted-run reconciliation | Planned. No journal-to-observed-state reconciliation and reviewed continuation workflow was added. |
| `roadmap:F033` — Selective failed-step retry planner | Planned. Read-only failure classification does not execute a selective retry. |
| `roadmap:F036` — Scoped change receipt and undo plan | Planned. Retained files and backup observations do not establish a validated undo receipt. |

The detailed acceptance criteria and complete mappings remain in [FEATURE-PROPOSALS.md](../FEATURE-PROPOSALS.md) and [ROADMAP-STATUS.md](ROADMAP-STATUS.md). Preserving the patch does not add shipped capabilities or mark a proposal complete.

## Verification boundary

This reconciliation records static review and pure planner checks. It does not demonstrate fresh-PC setup, Store or UAC prompts, Windows architecture behavior, desktop sign-in, profile migration, or interrupted-run recovery. Application tests, dashboard observations, real installation reports, and external-account checks are separate evidence classes. Consult the [verification record](../source/VERIFICATION.md) for what was actually exercised and its limits.

The original handoff text was not copied into this repository because it contains local workspace details. The preserved diff contains source changes only. The application's current source and deterministic packaged payload remain the release implementation.
