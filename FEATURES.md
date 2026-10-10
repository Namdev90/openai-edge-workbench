# Namu AI feature reconciliation

Checked against the active source and recovered legacy snapshots on 10 October 2026. All known recoverable project source is in this standalone repository. This is not a claim that every original ChatGPT attachment was separately downloadable, or that every historical feature is active.

| Component | Preserved source | Active implementation |
| --- | --- | --- |
| Browser Workbench | source/ | Active graphical installer, updater and report |
| Namu AI Edge | legacy/namu-ai-edge/ | Historical PowerShell/Windows Forms app; not executed |
| Device Manager | legacy/openai-device-manager/ | Historical PowerShell/Windows Forms app; not executed |
| Initial audit/repair | legacy/initial-audit/ | Historical reference; not executed |

20 branch-snapshot files retain their original independently audited hashes. See MIGRATION.md and migration-audit.json. The namu-ai-edge branch was removed after exclusive-project history verification; the mixed-history openai-device-manager branch was preserved. AMReye.AI main was not changed.

| Historical capability | Current status |
| --- | --- |
| Published-source self-update, checksums, offline regression checks | Active in Setup.ps1 and the desktop updater |
| Short download-and-launch command | Active in Run.ps1; opens the graphical dashboard with all packs selected |
| ChatGPT desktop, Git, GitHub CLI, uv, VS Code Insiders, PowerShell/Terminal Preview | Active explicit Store/WinGet channels |
| Node nightly and Codex/OpenAI/Agents/MCP/Playwright development packages | Active private runtime and environments; compatible npm host isolated |
| Python prereleases and document/science packs | Active full selected-pack wheel preflight and hashed dependency lock; newest compatible interpreter |
| .NET daily SDK | Active optional pack; selected by Run.ps1/all-tools mode |
| Browser runtime test, editor settings/extension migration | Active; conflicts preserved; only default-profile extensions |
| Codex/GitHub sign-in, provider inventory, docs MCP, live model test | Active with distinct evidence; MCP inventory is not a complete service test |
| Redacted repair/report handoff and owned-generation cleanup | Active; private reports remain local |
| Weekly scheduled task | Not merged; active application registers no maintenance task |
| LibreOffice, ImageMagick, Zotero from Namu AI Edge | Archived catalog only; not in the active installation plan |
| Go and ripgrep from Device Manager | Archived catalog only; not in the active installation plan |
| Old global Codex removal after live test | Not merged; active app preserves unrelated/global installations |
| Separate Audit-only, rollback, sign-in buttons of legacy native GUI | Not combined; active browser app has its own controls and validated cached-code fallback |

All tools means every supported active pack, not every application ever mentioned in old project discussions. The setup does not guarantee unpublished/private development builds or automatic cloud account permissions.
