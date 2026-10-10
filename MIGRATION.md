# Standalone migration and review, 10 October 2026

The browser Workbench source and self-contained launcher were recovered through repository commit 44c3c10b7332341d1a57d486be80bfce9acd47ea, published by a concurrent session while this review was underway. Its source was reviewed and repackaged into the active 2.0.1-preview.1 release. The original ChatGPT sandbox links were not directly downloadable through the accessible conversation reader; repository recovery is the provenance.

The initial audit script is preserved under legacy/initial-audit/. Independently audited historical snapshots:

- legacy/namu-ai-edge/: source head 0c6ea0a11ba2baad5753758a3cf6b12e3356d89c, including its isolated workflow, launcher, catalog and tests.
- legacy/openai-device-manager/: source head 0feaf6995d445ad6da8859a3a6ae8481750f1200, including its workflow, launcher, tests and GUI preview.

All 20 branch-snapshot files match their original Git blobs and independently computed SHA256 hashes. Historical bootstrappers are inert and still show their original endpoints for provenance. They are excluded from active payload execution.

Cleanup is based on every unique commit, not merely the current file tree. The namu-ai-edge branch has only tool-specific additions/modifications and is eligible for removal after destination verification. The openai-device-manager branch includes unrelated AMReye.AI file deletions in its unique history, so it must be preserved.

A concurrent session reset both old branch tips to unchanged AMReye.AI main. This review restores the original openai-device-manager tip with a lease check to preserve that mixed history. The eligible namu-ai-edge branch can then be removed using an exact-head lease. No AMReye.AI main changes, unrelated repository changes or user credential/configuration migrations are performed by repository cleanup.

migration-audit.json records original heads, unique commits and changes, archive hashes, final cleanup and main verification. Setup.ps1, deterministic payload generation, fresh SDK candidate activation and junction protections are reviewed additions to the recovered browser Workbench.
