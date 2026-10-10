# Implemented Feature Studio catalog

Exactly **100 actions**: 30 diagnostics, 35 report analyses, 25 planning/export actions (including ten profiles), and ten dashboard controls. These are implemented operations, presets and preferences, not 100 software installers.

IDs below use the `studio:` namespace. The separate proposal snapshot uses `roadmap:Fnnn`; see [status reconciliation](ROADMAP-STATUS.md).

Profiles change optional selections only after explicit Apply; core components remain included. No studio analysis makes a model request. Simulation skips native diagnostic commands and network checks. Reports and downloads remain local.

| ID | Action | Effect | Requirement |
| --- | --- | --- | --- |
| studio:f001 | Windows architecture readiness | read-only | Local Windows environment; missing evidence is reported |
| studio:f002 | Memory headroom | read-only | Local Windows environment; missing evidence is reported |
| studio:f003 | Installation disk headroom | read-only | Local Windows environment; missing evidence is reported |
| studio:f004 | Processor topology | read-only | Local Windows environment; missing evidence is reported |
| studio:f005 | Pending Windows restart | read-only | Local Windows environment; missing evidence is reported |
| studio:f006 | Missing PATH folders | read-only | Local Windows environment; missing evidence is reported |
| studio:f007 | Duplicate PATH folders | read-only | Local Windows environment; missing evidence is reported |
| studio:f008 | CLI search collisions | read-only | Local Windows environment; missing evidence is reported |
| studio:f009 | Managed command routing | read-only | Local Windows environment; missing evidence is reported |
| studio:f010 | Active binary availability | read-only | Local Windows environment; missing evidence is reported |
| studio:f011 | Owned runtime generations | read-only | Local Windows environment; missing evidence is reported |
| studio:f012 | Managed storage footprint | read-only | Local Windows environment; missing evidence is reported |
| studio:f013 | Ownership marker health | read-only | Local Windows environment; missing evidence is reported |
| studio:f014 | Active binary fingerprints | read-only | Local Windows environment; missing evidence is reported |
| studio:f015 | GitHub source provenance | read-only | Local Windows environment; missing evidence is reported |
| studio:f016 | Executable publisher signatures | read-only | Local Windows environment; missing evidence is reported |
| studio:f017 | npm warning audit | read-only | Local Windows environment; missing evidence is reported |
| studio:f018 | npm host isolation | read-only | Local Windows environment; missing evidence is reported |
| studio:f019 | Python environment isolation | read-only | Local Windows environment; missing evidence is reported |
| studio:f020 | Python dependency consistency | read-only | Local Windows environment; missing evidence is reported |
| studio:f021 | Package manager readiness | read-only | Local Windows environment; missing evidence is reported |
| studio:f022 | Editor AI extension readiness | read-only | Local Windows environment; missing evidence is reported |
| studio:f023 | Official Node nightly catalog | read-only | Internet access to the named official catalog |
| studio:f024 | Official npm catalog | read-only | Internet access to the named official catalog |
| studio:f025 | Official .NET preview catalog | read-only | Internet access to the named official catalog |
| studio:f026 | Playwright browser cache readiness | read-only | Local Windows environment; missing evidence is reported |
| studio:f027 | Official download TLS readiness | read-only | Local Windows environment; missing evidence is reported |
| studio:f028 | Environment variable presence | read-only | Local Windows environment; missing evidence is reported |
| studio:f029 | Migration coverage counters | read-only | Local Windows environment; missing evidence is reported |
| studio:f030 | Dashboard session hygiene | read-only | Local Windows environment; missing evidence is reported |
| studio:f031 | Installation outcome overview | read-only | Completed diagnostic; comparisons need a preceding run |
| studio:f032 | Failed-step triage | read-only | Completed diagnostic; comparisons need a preceding run |
| studio:f033 | Review-needed queue | read-only | Completed diagnostic; comparisons need a preceding run |
| studio:f034 | Codex doctor observations | read-only | Completed diagnostic; comparisons need a preceding run |
| studio:f035 | Transport and service access | read-only | Completed diagnostic; comparisons need a preceding run |
| studio:f036 | Sign-in evidence scope | read-only | Completed diagnostic; comparisons need a preceding run |
| studio:f037 | Python compatibility decision | read-only | Completed diagnostic; comparisons need a preceding run |
| studio:f038 | npm host compatibility | read-only | Completed diagnostic; comparisons need a preceding run |
| studio:f039 | Development-channel inventory | read-only | Completed diagnostic; comparisons need a preceding run |
| studio:f040 | Selected and skipped scope | read-only | Completed diagnostic; comparisons need a preceding run |
| studio:f041 | Installation timeline | read-only | Completed diagnostic; comparisons need a preceding run |
| studio:f042 | Installation bottlenecks | read-only | Completed diagnostic; comparisons need a preceding run |
| studio:f043 | Command exit-code audit | read-only | Completed diagnostic; comparisons need a preceding run |
| studio:f044 | Timeout and retry evidence | read-only | Completed diagnostic; comparisons need a preceding run |
| studio:f045 | Failure recovery classification | read-only | Completed diagnostic; comparisons need a preceding run |
| studio:f046 | Application update provenance | read-only | Completed diagnostic; comparisons need a preceding run |
| studio:f047 | Active version manifest | read-only | Completed diagnostic; comparisons need a preceding run |
| studio:f048 | Package source provenance | read-only | Completed diagnostic; comparisons need a preceding run |
| studio:f049 | Migration conflict review | read-only | Completed diagnostic; comparisons need a preceding run |
| studio:f050 | Migration coverage assessment | read-only | Completed diagnostic; comparisons need a preceding run |
| studio:f051 | Retained original applications | read-only | Completed diagnostic; comparisons need a preceding run |
| studio:f052 | Backup evidence summary | read-only | Completed diagnostic; comparisons need a preceding run |
| studio:f053 | Managed cleanup evidence | read-only | Completed diagnostic; comparisons need a preceding run |
| studio:f054 | Live model and quota scope | read-only | Completed diagnostic; comparisons need a preceding run |
| studio:f055 | Provider and environment routing | read-only | Completed diagnostic; comparisons need a preceding run |
| studio:f056 | MCP functional coverage | read-only | Completed diagnostic; comparisons need a preceding run |
| studio:f057 | Verification boundary audit | read-only | Completed diagnostic; comparisons need a preceding run |
| studio:f058 | Installation status drift | read-only | Completed diagnostic; comparisons need a preceding run |
| studio:f059 | Managed version drift | read-only | Completed diagnostic; comparisons need a preceding run |
| studio:f060 | Recurring installation problems | read-only | Completed diagnostic; comparisons need a preceding run |
| studio:f061 | Run outcome history | read-only | Completed diagnostic; comparisons need a preceding run |
| studio:f062 | Verification evidence matrix | read-only | Completed diagnostic; comparisons need a preceding run |
| studio:f063 | Stopped-run impact | read-only | Completed diagnostic; comparisons need a preceding run |
| studio:f064 | Catalog and installed reconciliation | read-only | Completed diagnostic; comparisons need a preceding run |
| studio:f065 | Readiness evidence checklist | read-only | Completed diagnostic; comparisons need a preceding run |
| studio:f066 | AI essentials profile | preview | Dashboard session |
| studio:f067 | Browser lab profile | preview | Dashboard session |
| studio:f068 | Document desk profile | preview | Dashboard session |
| studio:f069 | Science lab profile | preview | Dashboard session |
| studio:f070 | .NET lab profile | preview | Dashboard session |
| studio:f071 | Full workshop without model requests profile | preview | Dashboard session |
| studio:f072 | Documentation connection profile | preview | Dashboard session |
| studio:f073 | Editor migration profile | preview | Dashboard session |
| studio:f074 | Full workshop with connection test profile | preview | Dashboard session |
| studio:f075 | Research builder profile | preview | Dashboard session |
| studio:f076 | Preview selected installation plan | read-only | Dashboard session |
| studio:f077 | Inspect tool dependency map | read-only | Dashboard session |
| studio:f078 | Review network and approval requirements | read-only | Dashboard session |
| studio:f079 | Inspect runtime isolation boundaries | read-only | Dashboard session |
| studio:f080 | Export checksum-pinned setup command | local export | Dashboard session |
| studio:f081 | Export report as JSON | local export | Completed diagnostic; comparisons need a preceding run |
| studio:f082 | Export report as Markdown | local export | Completed diagnostic; comparisons need a preceding run |
| studio:f083 | Export report as CSV | local export | Completed diagnostic; comparisons need a preceding run |
| studio:f084 | Export portable HTML report | local export | Completed diagnostic; comparisons need a preceding run |
| studio:f085 | Export sanitized support bundle | local export | Completed diagnostic; comparisons need a preceding run |
| studio:f086 | Export two-run comparison | local export | Completed diagnostic; comparisons need a preceding run |
| studio:f087 | Save a local selection recipe | local settings | Installation idle; validated Workbench-owned recipe path |
| studio:f088 | Load local selection recipe | read-only | A saved local selection recipe |
| studio:f089 | Remove local selection recipe | local settings | Installation idle; validated Workbench-owned recipe path |
| studio:f090 | Review feature execution history | read-only | Dashboard session |
| studio:f091 | Search feature library | browser preference | Dashboard session |
| studio:f092 | Filter feature categories | browser preference | Dashboard session |
| studio:f093 | Pin favorite features | browser preference | Dashboard session |
| studio:f094 | View favorites only | browser preference | Dashboard session |
| studio:f095 | Choose display density | browser preference | Dashboard session |
| studio:f096 | Adjust dashboard text size | browser preference | Dashboard session |
| studio:f097 | Choose reduced motion | browser preference | Dashboard session |
| studio:f098 | Search live operation log | browser preference | Dashboard session |
| studio:f099 | Filter log severity | browser preference | Dashboard session |
| studio:f100 | Open keyboard command palette | browser preference | Dashboard session |

## Catalog contract

Every ID maps to one registered handler or one active browser control. Server jobs admit at most two concurrent actions. The code and offline fixture tests establish callable behavior; they do not certify every laptop, account, desktop UI or external publisher. [Verification](../source/VERIFICATION.md) records those evidence classes separately.

Generated by `python tools/feature_catalog.py`; check with `--check`.
