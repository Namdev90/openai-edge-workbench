# Project history

This is a navigation record for the inspected `main` snapshot at [4118f8a](https://github.com/Namdev90/openai-edge-workbench/commit/4118f8ab0f52646c8abbac7fc88625668cc3187b). It supplements the [changelog](../CHANGELOG.md), not the Git commit graph. Dates below are GitHub UTC timestamps; human-authored release headings may use a different local date.

## Origins and migration

- [Initial standalone repository, 10 October 2026](https://github.com/Namdev90/openai-edge-workbench/commit/4cda3f6f44bd5d5a8952a0d8733ab95f6d65d829).
- [Readable GUI, tests and verified setup](https://github.com/Namdev90/openai-edge-workbench/commit/44c3c10b7332341d1a57d486be80bfce9acd47ea).
- [Historical Namu AI Edge migration completed](https://github.com/Namdev90/openai-edge-workbench/commit/a95fe29980af359c2dd7fcb6261bc6393d8991ec).
- [Historical Device Manager migration completed](https://github.com/Namdev90/openai-edge-workbench/commit/e28d6852e01e5fe93fcdebd83c8d08e04fe26f08).

Namu AI Workbench is separate from AMReye.AI. The retained `legacy/` sources and [migration audit](../migration-audit.json) explain lineage; they are not the active application or evidence that every historical branch was merged. See [migration](../MIGRATION.md) and [handoff reconciliation](HANDOFF-RECONCILIATION.md) before modifying archives.

## Merged work

| Merged (UTC) | Pull request | Recorded subject |
| --- | --- | --- |
| 2026-10-10 13:20:16 | [#1](https://github.com/Namdev90/openai-edge-workbench/pull/1) | docs: propose 100 new Workbench capabilities and delivery roadmap |
| 2026-10-10 14:15:28 | [#2](https://github.com/Namdev90/openai-edge-workbench/pull/2) | feat: add Namu AI Feature Studio and optional report assistance |
| 2026-10-10 14:40:32 | [#3](https://github.com/Namdev90/openai-edge-workbench/pull/3) | fix: reliable Windows dashboard denial and NoLaunch verification |
| 2026-10-10 15:44:26 | [#4](https://github.com/Namdev90/openai-edge-workbench/pull/4) | Add all-catalog language atlas and transparent GitHub stats experiment |
| 2026-10-10 16:40:53 | [#5](https://github.com/Namdev90/openai-edge-workbench/pull/5) | Give Workbench a tactile instrument console |
| 2026-10-10 18:52:31 | [#6](https://github.com/Namdev90/openai-edge-workbench/pull/6) | Unify the dashboard and GitHub visual identity |

PR #1's 100 proposals and PR #2's 100 implemented actions remain different catalogs. PR #4 adds metadata fixtures and an atlas, not hundreds of working language implementations. These boundaries are documented in the [roadmap status](ROADMAP-STATUS.md) and [atlas guide](../language-stat-experiment/README.md).

## Published preview ledger

| Release | Published (UTC) | Recorded source target |
| --- | --- | --- |
| [v2.0.1-preview.1](https://github.com/Namdev90/openai-edge-workbench/releases/tag/v2.0.1-preview.1) | 2026-10-10 08:17:15 | [d8935e3](https://github.com/Namdev90/openai-edge-workbench/commit/d8935e3ef67fb9a8cca478794206b8ea87b5611b) |
| [v2.0.2-preview.1](https://github.com/Namdev90/openai-edge-workbench/releases/tag/v2.0.2-preview.1) | 2026-10-10 11:02:46 | [2cd0c70](https://github.com/Namdev90/openai-edge-workbench/commit/2cd0c70491921627ebc5461b30313a9a513ef493) |
| [v2.0.3-preview.1](https://github.com/Namdev90/openai-edge-workbench/releases/tag/v2.0.3-preview.1) | 2026-10-10 12:15:10 | [06d2001](https://github.com/Namdev90/openai-edge-workbench/commit/06d2001f7ff1b7327181d1ea169baee34a1e75c4) |
| [v2.0.4-preview.1](https://github.com/Namdev90/openai-edge-workbench/releases/tag/v2.0.4-preview.1) | 2026-10-10 12:54:17 | [e24318b](https://github.com/Namdev90/openai-edge-workbench/commit/e24318beb4b2db0cd62fef62e48c1eee96a93593) |
| [v3.0.0-preview.1](https://github.com/Namdev90/openai-edge-workbench/releases/tag/v3.0.0-preview.1) | 2026-10-10 14:16:07 | [6c9463b](https://github.com/Namdev90/openai-edge-workbench/commit/6c9463b2fe6a711259f71782c6f5c7b19816ee49) |
| [v3.0.0-preview.2](https://github.com/Namdev90/openai-edge-workbench/releases/tag/v3.0.0-preview.2) | 2026-10-10 14:41:03 | [de8a68a](https://github.com/Namdev90/openai-edge-workbench/commit/de8a68a7c619d6c13ab09dadd52523b91b19dc86) |
| [v3.0.0-preview.3](https://github.com/Namdev90/openai-edge-workbench/releases/tag/v3.0.0-preview.3) | 2026-10-10 16:41:14 | [00c904c](https://github.com/Namdev90/openai-edge-workbench/commit/00c904c1e43ed3afde14561c2770fdf3c9773630) |
| [v3.0.0-preview.4](https://github.com/Namdev90/openai-edge-workbench/releases/tag/v3.0.0-preview.4) | 2026-10-10 18:52:51 | [4118f8a](https://github.com/Namdev90/openai-edge-workbench/commit/4118f8ab0f52646c8abbac7fc88625668cc3187b) |

Every listed release is marked prerelease. The repository's inspected latest preview is `v3.0.0-preview.4`. This ledger does not create a new software version or claim these historical packages were reinstalled during documentation review.

## How to verify or extend this record

1. Start with the [complete main history](https://github.com/Namdev90/openai-edge-workbench/commits/main/), the linked PR and the associated diff.
2. Match a release to its target commit and manifest rather than assigning a version based only on a branch name.
3. Link dated tests and observations from [source verification](../source/VERIFICATION.md). Keep automated tests, real Windows observations and cloud account tests separate.
4. Add new milestones with their actual evidence. Do not backfill authors, tests, release dates or events from inference.

Existing branches can remain after merging. A branch's presence alone does not establish unfinished work or a new release. Preserve historical changelog entries and source bytes when adding this navigation.
