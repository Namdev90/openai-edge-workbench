# Migration record

The current production launcher is `OpenAI-Edge-Workbench.cmd`; its 15 readable payload files are published under `source/`. Legacy artifacts are archived under `legacy/` to keep the project separate from AMReye.AI.

- `legacy/initial-audit/` originated in an earlier single-script audit.
- `legacy/namu-ai-edge/` is a snapshot of 12 added files from `Namdev90/amreye-ai`, branch `namu-ai-edge`, commit `0c6ea0a11ba2baad5753758a3cf6b12e3356d89c`.
- `legacy/openai-device-manager/` is a snapshot of eight files from branch `openai-device-manager`, commit `0feaf6995d445ad6da8859a3a6ae8481750f1200`.

**The legacy scripts are archived, not used for installation**, because their bootstrappers refer to old repository branches. The app is independent and unofficial; no AMReye.AI application files, secrets or active workflows were imported.

Source deletion is performed only after the new GitHub destination is confirmed and the original branch heads are unchanged. Historical Git history and workflow logs may remain available even after branch removal.
