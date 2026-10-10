# Namu AI Edge implementation and verification

Intent: Windows one-command/one-click GUI maintenance, aggressive PUBLIC prereleases, GitHub self-updates, weekly local scheduling, diagnostic handoff. No repeated authorization questions for this build.

Architecture: a small GitHub bootstrap resolves a single commit, verifies SHA256 checksums on the source files, executes its pure-function/parse tests, then atomically selects the build. A Windows Forms dashboard starts a separate PowerShell worker and reads redacted JSONL events. Package IDs and SDKs are an explicit catalog, not arbitrary web-search installer results.

Tasks: version selection and redaction tests; subprocess runner and log schema; supported package adapters and reversible migration; GUI and weekly scheduler; bootstrap and distribution checks; Windows CI on isolated GitHub branch.

Rulings: use an isolated branch of the already-connected repository because repository creation is not exposed by this connector. No modification of AMReye.AI main. Only manage tools in the catalog, and report other tools instead of guessing how to install them. Self-update means downloading published tested code, not autonomously inventing arbitrary new code. No automatic publishing of private logs. Existing Headroom routing is inspected but not restored. Node nightlies are private runtime copies; Python SDKs are in a managed environment, not all project venvs.

Checks: Python distribution validation runs in the build environment. PowerShell regression/parse tests and GUI-construction smoke tests are included for Windows and CI. Full app installation, desktop rendering, user login, OAuth, scheduler execution and cloud integration must be verified on the target Windows laptop. Package-manager success and network reachability are not complete functional validation.
