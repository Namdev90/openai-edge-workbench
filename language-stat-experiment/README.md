# The Namu AI language atlas

**836 individually named catalog entries. A complete atlas with no “Other” category.**

[Open the standalone explorer](index.html) · [View the full visual atlas](atlas.svg) · [Inspect the JSON catalog](catalog.json)

GitHub displays HTML source in its repository viewer. Download the repository, then open `language-stat-experiment/index.html` in a browser for the searchable explorer. It works offline with no installation, dependencies or network requests. All records remain visible when JavaScript is disabled. The SVG opens directly in GitHub and shows every label; zoom in for readable detail.

## What this experiment contains

This is an explicit **language-stat classification experiment**, separate from the Windows application. Every entry in the pinned GitHub Linguist catalog has an original, substantial metadata reference. The records describe real classification metadata: identities, aliases, file patterns, parent groups, detection rules and provenance. They are not compiled or validated programs, and they do not imply that Workbench implements or installs every language.

Scoped `.gitattributes` entries deliberately assign each reference fixture to its catalog language and include programming, markup, data and prose classifications in the experiment. These overrides affect the repository's byte-based language statistics. No padding or copied third-party program samples are needed. The fixtures stay outside `source/` and the Windows installation payload.

| Snapshot classification | Entries |
| --- | ---: |
| Programming | 563 |
| Markup | 71 |
| Data | 184 |
| Prose | 18 |

The snapshot contains **754 distinct parent groups**. That is the expected maximum set of grouped classification keys derived from this catalog, not a statement that the live repository language API has already reported that count. GitHub can deploy an older Linguist catalog, combine dialects under parent languages, exclude files, and group its chart labels. Increasing file sizes cannot guarantee a separate native chart label for every entry. The complete atlas above is independent of that grouping and always shows all 836 snapshot entries separately.

“All” here means **every entry in this exact catalog snapshot**, not every language ever invented. New languages require an upstream catalog update before they can be represented faithfully.

## Reproduce and inspect

From the repository root, with Python available:

```text
python tools/build_language_lab.py --check
python tools/verify_language_lab.py
python tools/build_language_atlas.py --check
```

To rebuild these three presentation files after a catalog update:

```text
python tools/build_language_atlas.py
```

The atlas generator uses only the Python standard library and the checked-in catalog. It does not fetch changing upstream data. The HTML includes all entries before its optional local search script runs; filtering never sends data away. No runtime, package, credential or application setting is installed or changed by opening the atlas.

## Provenance

- Upstream repository: [GitHub Linguist](https://github.com/github-linguist/linguist)
- Pinned catalog: [538da05f034f / lib/linguist/languages.yml](https://github.com/github-linguist/linguist/blob/538da05f034fa5c83bd81df128d144e208898da3/lib/linguist/languages.yml)
- Full commit: `538da05f034fa5c83bd81df128d144e208898da3`
- Source SHA-256: `183243e30496ba53f5f8743b0e39c9f0e0bccc5a32639f7b541cc2285db0e043`
- Local normalized data and per-entry source locations: [catalog.json](catalog.json)
- Native grouping explanation: [How Linguist works](https://github.com/github-linguist/linguist/blob/538da05f034fa5c83bd81df128d144e208898da3/docs/how-linguist-works.md)
- Explicit classification controls: [Linguist overrides](https://github.com/github-linguist/linguist/blob/538da05f034fa5c83bd81df128d144e208898da3/docs/overrides.md)

## Complete entry index

Every entry below links to its detailed reference. “Group” is the statistical parent, which may combine several entries in GitHub's native language data.

| Catalog entry | Classification | Group | Linguist ID |
| --- | --- | --- | ---: |
| [1C Enterprise](fixtures/lang-0.fixture) | programming | 1C Enterprise | 0 |
| [2-Dimensional Array](fixtures/lang-387204628.fixture) | data | 2-Dimensional Array | 387204628 |
| [4D](fixtures/lang-577529595.fixture) | programming | 4D | 577529595 |
| [ABAP](fixtures/lang-1.fixture) | programming | ABAP | 1 |
| [ABAP CDS](fixtures/lang-452681853.fixture) | programming | ABAP CDS | 452681853 |
| [ABNF](fixtures/lang-429.fixture) | data | ABNF | 429 |
| [AGS Script](fixtures/lang-2.fixture) | programming | AGS Script | 2 |
| [AIDL](fixtures/lang-451700185.fixture) | programming | AIDL | 451700185 |
| [AL](fixtures/lang-658971832.fixture) | programming | AL | 658971832 |
| [ALGOL](fixtures/lang-79217948.fixture) | programming | ALGOL | 79217948 |
| [AMPL](fixtures/lang-3.fixture) | programming | AMPL | 3 |
| [ANTLR](fixtures/lang-4.fixture) | programming | ANTLR | 4 |
| [API Blueprint](fixtures/lang-5.fixture) | markup | API Blueprint | 5 |
| [APL](fixtures/lang-6.fixture) | programming | APL | 6 |
| [ASL](fixtures/lang-124996147.fixture) | programming | ASL | 124996147 |
| [ASN.1](fixtures/lang-7.fixture) | data | ASN.1 | 7 |
| [ASP.NET](fixtures/lang-564186416.fixture) | programming | ASP.NET | 564186416 |
| [ATS](fixtures/lang-9.fixture) | programming | ATS | 9 |
| [ActionScript](fixtures/lang-10.fixture) | programming | ActionScript | 10 |
| [Ada](fixtures/lang-11.fixture) | programming | Ada | 11 |
| [Adblock Filter List](fixtures/lang-884614762.fixture) | data | Adblock Filter List | 884614762 |
| [Adobe Font Metrics](fixtures/lang-147198098.fixture) | data | Adobe Font Metrics | 147198098 |
| [Agda](fixtures/lang-12.fixture) | programming | Agda | 12 |
| [Aiken](fixtures/lang-899409497.fixture) | programming | Aiken | 899409497 |
| [Aleo](fixtures/lang-566431048.fixture) | programming | Aleo | 566431048 |
| [Alloy](fixtures/lang-13.fixture) | programming | Alloy | 13 |
| [Alpine Abuild](fixtures/lang-14.fixture) | programming | Shell | 14 |
| [Altium Designer](fixtures/lang-187772328.fixture) | data | Altium Designer | 187772328 |
| [AngelScript](fixtures/lang-389477596.fixture) | programming | AngelScript | 389477596 |
| [Answer Set Programming](fixtures/lang-433009171.fixture) | programming | Answer Set Programming | 433009171 |
| [Ant Build System](fixtures/lang-15.fixture) | data | Ant Build System | 15 |
| [Antlers](fixtures/lang-1067292663.fixture) | markup | Antlers | 1067292663 |
| [ApacheConf](fixtures/lang-16.fixture) | data | ApacheConf | 16 |
| [Apex](fixtures/lang-17.fixture) | programming | Apex | 17 |
| [Apollo Guidance Computer](fixtures/lang-18.fixture) | programming | Assembly | 18 |
| [AppleScript](fixtures/lang-19.fixture) | programming | AppleScript | 19 |
| [Arc](fixtures/lang-20.fixture) | programming | Arc | 20 |
| [ArkTS](fixtures/lang-56341321.fixture) | programming | ArkTS | 56341321 |
| [AsciiDoc](fixtures/lang-22.fixture) | prose | AsciiDoc | 22 |
| [AspectJ](fixtures/lang-23.fixture) | programming | AspectJ | 23 |
| [Assembly](fixtures/lang-24.fixture) | programming | Assembly | 24 |
| [Astro](fixtures/lang-578209015.fixture) | markup | Astro | 578209015 |
| [Asymptote](fixtures/lang-591605007.fixture) | programming | Asymptote | 591605007 |
| [Augeas](fixtures/lang-25.fixture) | programming | Augeas | 25 |
| [AutoHotkey](fixtures/lang-26.fixture) | programming | AutoHotkey | 26 |
| [AutoIt](fixtures/lang-27.fixture) | programming | AutoIt | 27 |
| [Avro IDL](fixtures/lang-785497837.fixture) | data | Avro IDL | 785497837 |
| [Awk](fixtures/lang-28.fixture) | programming | Awk | 28 |
| [B](fixtures/lang-700792152.fixture) | programming | B | 700792152 |
| [B (Formal Method)](fixtures/lang-993355937.fixture) | programming | B (Formal Method) | 993355937 |
| [B4X](fixtures/lang-96642275.fixture) | programming | B4X | 96642275 |
| [BAML](fixtures/lang-502521509.fixture) | programming | BAML | 502521509 |
| [BASIC](fixtures/lang-28923963.fixture) | programming | BASIC | 28923963 |
| [BBCode](fixtures/lang-206921123.fixture) | markup | BBCode | 206921123 |
| [BIRD2](fixtures/lang-584191811.fixture) | data | BIRD2 | 584191811 |
| [BQN](fixtures/lang-330386870.fixture) | programming | BQN | 330386870 |
| [Ballerina](fixtures/lang-720859680.fixture) | programming | Ballerina | 720859680 |
| [Batchfile](fixtures/lang-29.fixture) | programming | Batchfile | 29 |
| [Beef](fixtures/lang-545626333.fixture) | programming | Beef | 545626333 |
| [Befunge](fixtures/lang-30.fixture) | programming | Befunge | 30 |
| [Bend](fixtures/lang-571794812.fixture) | programming | Bend | 571794812 |
| [Berry](fixtures/lang-121855308.fixture) | programming | Berry | 121855308 |
| [BibTeX](fixtures/lang-982188347.fixture) | markup | TeX | 982188347 |
| [BibTeX Style](fixtures/lang-909569041.fixture) | programming | BibTeX Style | 909569041 |
| [Bicep](fixtures/lang-321200902.fixture) | programming | Bicep | 321200902 |
| [Bikeshed](fixtures/lang-1055528081.fixture) | markup | Bikeshed | 1055528081 |
| [Bison](fixtures/lang-31.fixture) | programming | Yacc | 31 |
| [BitBake](fixtures/lang-32.fixture) | programming | BitBake | 32 |
| [Blade](fixtures/lang-33.fixture) | markup | Blade | 33 |
| [BlitzBasic](fixtures/lang-34.fixture) | programming | BlitzBasic | 34 |
| [BlitzMax](fixtures/lang-35.fixture) | programming | BlitzMax | 35 |
| [Blueprint](fixtures/lang-765545512.fixture) | markup | Blueprint | 765545512 |
| [Bluespec](fixtures/lang-36.fixture) | programming | Bluespec | 36 |
| [Bluespec BH](fixtures/lang-641580358.fixture) | programming | Bluespec | 641580358 |
| [Boo](fixtures/lang-37.fixture) | programming | Boo | 37 |
| [Boogie](fixtures/lang-955017407.fixture) | programming | Boogie | 955017407 |
| [Brainfuck](fixtures/lang-38.fixture) | programming | Brainfuck | 38 |
| [BrighterScript](fixtures/lang-943571030.fixture) | programming | BrighterScript | 943571030 |
| [Brightscript](fixtures/lang-39.fixture) | programming | Brightscript | 39 |
| [Browserslist](fixtures/lang-153503348.fixture) | data | Browserslist | 153503348 |
| [Bru](fixtures/lang-906627898.fixture) | markup | Bru | 906627898 |
| [BuildStream](fixtures/lang-84359046.fixture) | data | BuildStream | 84359046 |
| [C](fixtures/lang-41.fixture) | programming | C | 41 |
| [C#](fixtures/lang-42.fixture) | programming | C# | 42 |
| [C++](fixtures/lang-43.fixture) | programming | C++ | 43 |
| [C-ObjDump](fixtures/lang-44.fixture) | data | C-ObjDump | 44 |
| [C2hs Haskell](fixtures/lang-45.fixture) | programming | Haskell | 45 |
| [C3](fixtures/lang-769248603.fixture) | programming | C3 | 769248603 |
| [CAP CDS](fixtures/lang-390788699.fixture) | programming | CAP CDS | 390788699 |
| [CIL](fixtures/lang-29176339.fixture) | data | CIL | 29176339 |
| [CLIPS](fixtures/lang-46.fixture) | programming | CLIPS | 46 |
| [CMake](fixtures/lang-47.fixture) | programming | CMake | 47 |
| [COBOL](fixtures/lang-48.fixture) | programming | COBOL | 48 |
| [CODEOWNERS](fixtures/lang-321684729.fixture) | data | CODEOWNERS | 321684729 |
| [COLLADA](fixtures/lang-49.fixture) | data | COLLADA | 49 |
| [CQL](fixtures/lang-71155397.fixture) | programming | CQL | 71155397 |
| [CSON](fixtures/lang-424.fixture) | data | CSON | 424 |
| [CSS](fixtures/lang-50.fixture) | markup | CSS | 50 |
| [CSV](fixtures/lang-51.fixture) | data | CSV | 51 |
| [CUE](fixtures/lang-356063509.fixture) | programming | CUE | 356063509 |
| [CWeb](fixtures/lang-657332628.fixture) | programming | CWeb | 657332628 |
| [Cabal Config](fixtures/lang-677095381.fixture) | data | Cabal Config | 677095381 |
| [Caddyfile](fixtures/lang-615465151.fixture) | data | Caddyfile | 615465151 |
| [Cadence](fixtures/lang-270184138.fixture) | programming | Cadence | 270184138 |
| [Cairo](fixtures/lang-620599567.fixture) | programming | Cairo | 620599567 |
| [Cairo Zero](fixtures/lang-891399890.fixture) | programming | Cairo | 891399890 |
| [CameLIGO](fixtures/lang-829207807.fixture) | programming | LigoLANG | 829207807 |
| [Cangjie](fixtures/lang-581895317.fixture) | programming | Cangjie | 581895317 |
| [Cap'n Proto](fixtures/lang-52.fixture) | programming | Cap'n Proto | 52 |
| [Carbon](fixtures/lang-55627273.fixture) | programming | Carbon | 55627273 |
| [CartoCSS](fixtures/lang-53.fixture) | programming | CartoCSS | 53 |
| [Ceylon](fixtures/lang-54.fixture) | programming | Ceylon | 54 |
| [Chapel](fixtures/lang-55.fixture) | programming | Chapel | 55 |
| [Charity](fixtures/lang-56.fixture) | programming | Charity | 56 |
| [Checksums](fixtures/lang-372063053.fixture) | data | Checksums | 372063053 |
| [ChucK](fixtures/lang-57.fixture) | programming | ChucK | 57 |
| [Circom](fixtures/lang-1042332086.fixture) | programming | Circom | 1042332086 |
| [Cirru](fixtures/lang-58.fixture) | programming | Cirru | 58 |
| [Clarion](fixtures/lang-59.fixture) | programming | Clarion | 59 |
| [Clarity](fixtures/lang-91493841.fixture) | programming | Clarity | 91493841 |
| [Classic ASP](fixtures/lang-8.fixture) | programming | Classic ASP | 8 |
| [Clean](fixtures/lang-60.fixture) | programming | Clean | 60 |
| [Click](fixtures/lang-61.fixture) | programming | Click | 61 |
| [Clojure](fixtures/lang-62.fixture) | programming | Clojure | 62 |
| [Closure Templates](fixtures/lang-357046146.fixture) | markup | Closure Templates | 357046146 |
| [Cloud Firestore Security Rules](fixtures/lang-407996372.fixture) | data | Cloud Firestore Security Rules | 407996372 |
| [Clue](fixtures/lang-163763508.fixture) | programming | Clue | 163763508 |
| [CoNLL-U](fixtures/lang-421026389.fixture) | data | CoNLL-U | 421026389 |
| [CodeQL](fixtures/lang-424259634.fixture) | programming | CodeQL | 424259634 |
| [CoffeeScript](fixtures/lang-63.fixture) | programming | CoffeeScript | 63 |
| [ColdFusion](fixtures/lang-64.fixture) | programming | ColdFusion | 64 |
| [ColdFusion CFC](fixtures/lang-65.fixture) | programming | ColdFusion | 65 |
| [Common Lisp](fixtures/lang-66.fixture) | programming | Common Lisp | 66 |
| [Common Workflow Language](fixtures/lang-988547172.fixture) | programming | Common Workflow Language | 988547172 |
| [Component Pascal](fixtures/lang-67.fixture) | programming | Component Pascal | 67 |
| [Cooklang](fixtures/lang-788037493.fixture) | markup | Cooklang | 788037493 |
| [Cool](fixtures/lang-68.fixture) | programming | Cool | 68 |
| [Cpp-ObjDump](fixtures/lang-70.fixture) | data | Cpp-ObjDump | 70 |
| [Creole](fixtures/lang-71.fixture) | prose | Creole | 71 |
| [Crystal](fixtures/lang-72.fixture) | programming | Crystal | 72 |
| [Csound](fixtures/lang-73.fixture) | programming | Csound | 73 |
| [Csound Document](fixtures/lang-74.fixture) | programming | Csound Document | 74 |
| [Csound Score](fixtures/lang-75.fixture) | programming | Csound Score | 75 |
| [Cuda](fixtures/lang-77.fixture) | programming | Cuda | 77 |
| [Cue Sheet](fixtures/lang-942714150.fixture) | data | Cue Sheet | 942714150 |
| [Curry](fixtures/lang-439829048.fixture) | programming | Curry | 439829048 |
| [Cycript](fixtures/lang-78.fixture) | programming | Cycript | 78 |
| [Cylc](fixtures/lang-476447814.fixture) | data | INI | 476447814 |
| [Cypher](fixtures/lang-850806976.fixture) | programming | Cypher | 850806976 |
| [Cython](fixtures/lang-79.fixture) | programming | Cython | 79 |
| [D](fixtures/lang-80.fixture) | programming | D | 80 |
| [D-ObjDump](fixtures/lang-81.fixture) | data | D-ObjDump | 81 |
| [D2](fixtures/lang-37531557.fixture) | markup | D2 | 37531557 |
| [DIGITAL Command Language](fixtures/lang-82.fixture) | programming | DIGITAL Command Language | 82 |
| [DM](fixtures/lang-83.fixture) | programming | DM | 83 |
| [DNS Zone](fixtures/lang-84.fixture) | data | DNS Zone | 84 |
| [DTrace](fixtures/lang-85.fixture) | programming | DTrace | 85 |
| [Dafny](fixtures/lang-969323346.fixture) | programming | Dafny | 969323346 |
| [Darcs Patch](fixtures/lang-86.fixture) | data | Darcs Patch | 86 |
| [Dart](fixtures/lang-87.fixture) | programming | Dart | 87 |
| [Daslang](fixtures/lang-648759486.fixture) | programming | Daslang | 648759486 |
| [DataWeave](fixtures/lang-974514097.fixture) | programming | DataWeave | 974514097 |
| [Debian Package Control File](fixtures/lang-527438264.fixture) | data | Debian Package Control File | 527438264 |
| [DenizenScript](fixtures/lang-435000929.fixture) | programming | DenizenScript | 435000929 |
| [Dhall](fixtures/lang-793969321.fixture) | programming | Dhall | 793969321 |
| [Diff](fixtures/lang-88.fixture) | data | Diff | 88 |
| [DirectX 3D File](fixtures/lang-201049282.fixture) | data | DirectX 3D File | 201049282 |
| [Dockerfile](fixtures/lang-89.fixture) | programming | Dockerfile | 89 |
| [Dogescript](fixtures/lang-90.fixture) | programming | Dogescript | 90 |
| [Dotenv](fixtures/lang-111148035.fixture) | data | Dotenv | 111148035 |
| [Dune](fixtures/lang-754574151.fixture) | programming | Dune | 754574151 |
| [Dylan](fixtures/lang-91.fixture) | programming | Dylan | 91 |
| [E](fixtures/lang-92.fixture) | programming | E | 92 |
| [E-mail](fixtures/lang-529653389.fixture) | data | E-mail | 529653389 |
| [EBNF](fixtures/lang-430.fixture) | data | EBNF | 430 |
| [ECL](fixtures/lang-93.fixture) | programming | ECL | 93 |
| [ECLiPSe](fixtures/lang-94.fixture) | programming | Prolog | 94 |
| [EJS](fixtures/lang-95.fixture) | markup | EJS | 95 |
| [EQ](fixtures/lang-96.fixture) | programming | EQ | 96 |
| [Eagle](fixtures/lang-97.fixture) | data | Eagle | 97 |
| [Earthly](fixtures/lang-963512632.fixture) | programming | Earthly | 963512632 |
| [Easybuild](fixtures/lang-342840477.fixture) | data | Python | 342840477 |
| [Ecere Projects](fixtures/lang-98.fixture) | data | JavaScript | 98 |
| [Ecmarkup](fixtures/lang-844766630.fixture) | markup | HTML | 844766630 |
| [Edge](fixtures/lang-460509620.fixture) | markup | Edge | 460509620 |
| [EdgeQL](fixtures/lang-925235833.fixture) | programming | EdgeQL | 925235833 |
| [EditorConfig](fixtures/lang-96139566.fixture) | data | INI | 96139566 |
| [Edje Data Collection](fixtures/lang-342840478.fixture) | data | Edje Data Collection | 342840478 |
| [Eiffel](fixtures/lang-99.fixture) | programming | Eiffel | 99 |
| [Elixir](fixtures/lang-100.fixture) | programming | Elixir | 100 |
| [Elm](fixtures/lang-101.fixture) | programming | Elm | 101 |
| [Elvish](fixtures/lang-570996448.fixture) | programming | Elvish | 570996448 |
| [Elvish Transcript](fixtures/lang-452025714.fixture) | programming | Elvish | 452025714 |
| [Emacs Lisp](fixtures/lang-102.fixture) | programming | Emacs Lisp | 102 |
| [EmberScript](fixtures/lang-103.fixture) | programming | EmberScript | 103 |
| [Erlang](fixtures/lang-104.fixture) | programming | Erlang | 104 |
| [Euphoria](fixtures/lang-880693982.fixture) | programming | Euphoria | 880693982 |
| [F#](fixtures/lang-105.fixture) | programming | F# | 105 |
| [F*](fixtures/lang-336943375.fixture) | programming | F* | 336943375 |
| [FIGlet Font](fixtures/lang-686129783.fixture) | data | FIGlet Font | 686129783 |
| [FIRRTL](fixtures/lang-906694254.fixture) | programming | FIRRTL | 906694254 |
| [FLUX](fixtures/lang-106.fixture) | programming | FLUX | 106 |
| [FPP](fixtures/lang-252360067.fixture) | programming | FPP | 252360067 |
| [Factor](fixtures/lang-108.fixture) | programming | Factor | 108 |
| [Fancy](fixtures/lang-109.fixture) | programming | Fancy | 109 |
| [Fantom](fixtures/lang-110.fixture) | programming | Fantom | 110 |
| [Faust](fixtures/lang-622529198.fixture) | programming | Faust | 622529198 |
| [Fennel](fixtures/lang-239946126.fixture) | programming | Fennel | 239946126 |
| [Filebench WML](fixtures/lang-111.fixture) | programming | Filebench WML | 111 |
| [Filterscript](fixtures/lang-112.fixture) | programming | RenderScript | 112 |
| [FlatBuffers](fixtures/lang-577640576.fixture) | data | FlatBuffers | 577640576 |
| [Flix](fixtures/lang-800935960.fixture) | programming | Flix | 800935960 |
| [Fluent](fixtures/lang-206353404.fixture) | programming | Fluent | 206353404 |
| [Formatted](fixtures/lang-113.fixture) | data | Formatted | 113 |
| [Forth](fixtures/lang-114.fixture) | programming | Forth | 114 |
| [Fortran](fixtures/lang-107.fixture) | programming | Fortran | 107 |
| [Fortran Free Form](fixtures/lang-761352333.fixture) | programming | Fortran | 761352333 |
| [FreeBASIC](fixtures/lang-472896659.fixture) | programming | FreeBASIC | 472896659 |
| [FreeMarker](fixtures/lang-115.fixture) | programming | FreeMarker | 115 |
| [Frege](fixtures/lang-116.fixture) | programming | Frege | 116 |
| [Futhark](fixtures/lang-97358117.fixture) | programming | Futhark | 97358117 |
| [G-code](fixtures/lang-117.fixture) | programming | G-code | 117 |
| [GAML](fixtures/lang-290345951.fixture) | programming | GAML | 290345951 |
| [GAMS](fixtures/lang-118.fixture) | programming | GAMS | 118 |
| [GAP](fixtures/lang-119.fixture) | programming | GAP | 119 |
| [GCC Machine Description](fixtures/lang-121.fixture) | programming | GCC Machine Description | 121 |
| [GDB](fixtures/lang-122.fixture) | programming | GDB | 122 |
| [GDScript](fixtures/lang-123.fixture) | programming | GDScript | 123 |
| [GDShader](fixtures/lang-694638086.fixture) | programming | GDShader | 694638086 |
| [GEDCOM](fixtures/lang-459577965.fixture) | data | GEDCOM | 459577965 |
| [GLSL](fixtures/lang-124.fixture) | programming | GLSL | 124 |
| [GN](fixtures/lang-302957008.fixture) | data | GN | 302957008 |
| [GSC](fixtures/lang-257856279.fixture) | programming | GSC | 257856279 |
| [Game Maker Language](fixtures/lang-125.fixture) | programming | Game Maker Language | 125 |
| [Gemfile.lock](fixtures/lang-907065713.fixture) | data | Gemfile.lock | 907065713 |
| [Gemini](fixtures/lang-310828396.fixture) | prose | Gemini | 310828396 |
| [Genero 4gl](fixtures/lang-986054050.fixture) | programming | Genero 4gl | 986054050 |
| [Genero per](fixtures/lang-902995658.fixture) | markup | Genero per | 902995658 |
| [Genie](fixtures/lang-792408528.fixture) | programming | Genie | 792408528 |
| [Genshi](fixtures/lang-126.fixture) | programming | Genshi | 126 |
| [Gentoo Ebuild](fixtures/lang-127.fixture) | programming | Shell | 127 |
| [Gentoo Eclass](fixtures/lang-128.fixture) | programming | Shell | 128 |
| [Gerber Image](fixtures/lang-404627610.fixture) | data | Gerber Image | 404627610 |
| [Gettext Catalog](fixtures/lang-129.fixture) | prose | Gettext Catalog | 129 |
| [Gherkin](fixtures/lang-76.fixture) | programming | Gherkin | 76 |
| [Git Attributes](fixtures/lang-956324166.fixture) | data | Git Attributes | 956324166 |
| [Git Commit](fixtures/lang-131750475.fixture) | data | Git Commit | 131750475 |
| [Git Config](fixtures/lang-807968997.fixture) | data | INI | 807968997 |
| [Git Revision List](fixtures/lang-461881235.fixture) | data | Git Revision List | 461881235 |
| [Gleam](fixtures/lang-1054258749.fixture) | programming | Gleam | 1054258749 |
| [Glimmer JS](fixtures/lang-5523150.fixture) | programming | JavaScript | 5523150 |
| [Glimmer TS](fixtures/lang-95110458.fixture) | programming | TypeScript | 95110458 |
| [Glyph](fixtures/lang-130.fixture) | programming | Glyph | 130 |
| [Glyph Bitmap Distribution Format](fixtures/lang-997665271.fixture) | data | Glyph Bitmap Distribution Format | 997665271 |
| [Gno](fixtures/lang-279301301.fixture) | programming | Gno | 279301301 |
| [Gnuplot](fixtures/lang-131.fixture) | programming | Gnuplot | 131 |
| [Go](fixtures/lang-132.fixture) | programming | Go | 132 |
| [Go Checksums](fixtures/lang-1054391671.fixture) | data | Go Checksums | 1054391671 |
| [Go Module](fixtures/lang-947461016.fixture) | data | Go Module | 947461016 |
| [Go Template](fixtures/lang-247918769.fixture) | markup | Go Template | 247918769 |
| [Go Workspace](fixtures/lang-934546256.fixture) | data | Go Workspace | 934546256 |
| [Godot Resource](fixtures/lang-738107771.fixture) | data | Godot Resource | 738107771 |
| [Golo](fixtures/lang-133.fixture) | programming | Golo | 133 |
| [Gosu](fixtures/lang-134.fixture) | programming | Gosu | 134 |
| [Grace](fixtures/lang-135.fixture) | programming | Grace | 135 |
| [Gradle](fixtures/lang-136.fixture) | data | Gradle | 136 |
| [Gradle Kotlin DSL](fixtures/lang-432600901.fixture) | data | Gradle | 432600901 |
| [Grammatical Framework](fixtures/lang-137.fixture) | programming | Grammatical Framework | 137 |
| [Graph Modeling Language](fixtures/lang-138.fixture) | data | Graph Modeling Language | 138 |
| [GraphQL](fixtures/lang-139.fixture) | data | GraphQL | 139 |
| [Graphviz (DOT)](fixtures/lang-140.fixture) | data | Graphviz (DOT) | 140 |
| [Groovy](fixtures/lang-142.fixture) | programming | Groovy | 142 |
| [Groovy Server Pages](fixtures/lang-143.fixture) | programming | Groovy | 143 |
| [GtkRC](fixtures/lang-876401352.fixture) | data | GtkRC | 876401352 |
| [HAProxy](fixtures/lang-366607477.fixture) | data | HAProxy | 366607477 |
| [HCL](fixtures/lang-144.fixture) | programming | HCL | 144 |
| [HIP](fixtures/lang-674379998.fixture) | programming | HIP | 674379998 |
| [HLSL](fixtures/lang-145.fixture) | programming | HLSL | 145 |
| [HOCON](fixtures/lang-679725279.fixture) | data | HOCON | 679725279 |
| [HTML](fixtures/lang-146.fixture) | markup | HTML | 146 |
| [HTML+ECR](fixtures/lang-148.fixture) | markup | HTML | 148 |
| [HTML+EEX](fixtures/lang-149.fixture) | markup | HTML | 149 |
| [HTML+ERB](fixtures/lang-150.fixture) | markup | HTML | 150 |
| [HTML+PHP](fixtures/lang-151.fixture) | markup | HTML | 151 |
| [HTML+Razor](fixtures/lang-479039817.fixture) | markup | HTML | 479039817 |
| [HTTP](fixtures/lang-152.fixture) | data | HTTP | 152 |
| [HXML](fixtures/lang-786683730.fixture) | data | HXML | 786683730 |
| [Hack](fixtures/lang-153.fixture) | programming | Hack | 153 |
| [Haml](fixtures/lang-154.fixture) | markup | Haml | 154 |
| [Handlebars](fixtures/lang-155.fixture) | markup | Handlebars | 155 |
| [Harbour](fixtures/lang-156.fixture) | programming | Harbour | 156 |
| [Hare](fixtures/lang-463518941.fixture) | programming | Hare | 463518941 |
| [Haskell](fixtures/lang-157.fixture) | programming | Haskell | 157 |
| [Haxe](fixtures/lang-158.fixture) | programming | Haxe | 158 |
| [HiveQL](fixtures/lang-931814087.fixture) | programming | HiveQL | 931814087 |
| [HolyC](fixtures/lang-928121743.fixture) | programming | HolyC | 928121743 |
| [Hosts File](fixtures/lang-231021894.fixture) | data | Hosts File | 231021894 |
| [Hurl](fixtures/lang-959040217.fixture) | programming | Hurl | 959040217 |
| [Hy](fixtures/lang-159.fixture) | programming | Hy | 159 |
| [HyPhy](fixtures/lang-160.fixture) | programming | HyPhy | 160 |
| [IDL](fixtures/lang-161.fixture) | programming | IDL | 161 |
| [IGOR Pro](fixtures/lang-162.fixture) | programming | IGOR Pro | 162 |
| [IL Assembly](fixtures/lang-592065806.fixture) | programming | IL Assembly | 592065806 |
| [INI](fixtures/lang-163.fixture) | data | INI | 163 |
| [IRC log](fixtures/lang-164.fixture) | data | IRC log | 164 |
| [ISPC](fixtures/lang-327071.fixture) | programming | ISPC | 327071 |
| [Idris](fixtures/lang-165.fixture) | programming | Idris | 165 |
| [Ignore List](fixtures/lang-74444240.fixture) | data | Ignore List | 74444240 |
| [ImHex Pattern Language](fixtures/lang-805861688.fixture) | programming | ImHex Pattern Language | 805861688 |
| [ImageJ Macro](fixtures/lang-575143428.fixture) | programming | ImageJ Macro | 575143428 |
| [Imba](fixtures/lang-1057618448.fixture) | programming | Imba | 1057618448 |
| [Inform 7](fixtures/lang-166.fixture) | programming | Inform 7 | 166 |
| [Ink](fixtures/lang-838252715.fixture) | programming | Ink | 838252715 |
| [Inno Setup](fixtures/lang-167.fixture) | programming | Inno Setup | 167 |
| [Io](fixtures/lang-168.fixture) | programming | Io | 168 |
| [Ioke](fixtures/lang-169.fixture) | programming | Ioke | 169 |
| [Isabelle](fixtures/lang-170.fixture) | programming | Isabelle | 170 |
| [Isabelle ROOT](fixtures/lang-171.fixture) | programming | Isabelle | 171 |
| [J](fixtures/lang-172.fixture) | programming | J | 172 |
| [JAR Manifest](fixtures/lang-447261135.fixture) | data | JAR Manifest | 447261135 |
| [JASS](fixtures/lang-504860504.fixture) | programming | JASS | 504860504 |
| [JCL](fixtures/lang-316620079.fixture) | programming | JCL | 316620079 |
| [JFlex](fixtures/lang-173.fixture) | programming | Lex | 173 |
| [JSON](fixtures/lang-174.fixture) | data | JSON | 174 |
| [JSON with Comments](fixtures/lang-423.fixture) | data | JSON | 423 |
| [JSON5](fixtures/lang-175.fixture) | data | JSON5 | 175 |
| [JSONLD](fixtures/lang-176.fixture) | data | JSONLD | 176 |
| [JSONiq](fixtures/lang-177.fixture) | programming | JSONiq | 177 |
| [Jac](fixtures/lang-235277043.fixture) | programming | Jac | 235277043 |
| [Jai](fixtures/lang-70127133.fixture) | programming | Jai | 70127133 |
| [Janet](fixtures/lang-1028705371.fixture) | programming | Janet | 1028705371 |
| [Jasmin](fixtures/lang-180.fixture) | programming | Jasmin | 180 |
| [Java](fixtures/lang-181.fixture) | programming | Java | 181 |
| [Java Properties](fixtures/lang-519377561.fixture) | data | Java Properties | 519377561 |
| [Java Server Pages](fixtures/lang-182.fixture) | programming | Java | 182 |
| [Java Template Engine](fixtures/lang-599494012.fixture) | programming | Java | 599494012 |
| [JavaScript](fixtures/lang-183.fixture) | programming | JavaScript | 183 |
| [JavaScript+ERB](fixtures/lang-914318960.fixture) | programming | JavaScript | 914318960 |
| [Jest Snapshot](fixtures/lang-774635084.fixture) | data | Jest Snapshot | 774635084 |
| [JetBrains MPS](fixtures/lang-465165328.fixture) | programming | JetBrains MPS | 465165328 |
| [Jinja](fixtures/lang-147.fixture) | markup | Jinja | 147 |
| [Jison](fixtures/lang-284531423.fixture) | programming | Yacc | 284531423 |
| [Jison Lex](fixtures/lang-406395330.fixture) | programming | Lex | 406395330 |
| [Jolie](fixtures/lang-998078858.fixture) | programming | Jolie | 998078858 |
| [Jsonnet](fixtures/lang-664885656.fixture) | programming | Jsonnet | 664885656 |
| [Julia](fixtures/lang-184.fixture) | programming | Julia | 184 |
| [Julia REPL](fixtures/lang-220689142.fixture) | programming | Julia | 220689142 |
| [Jupyter Notebook](fixtures/lang-185.fixture) | markup | Jupyter Notebook | 185 |
| [Just](fixtures/lang-128447695.fixture) | programming | Just | 128447695 |
| [KCL](fixtures/lang-1052003890.fixture) | programming | KCL | 1052003890 |
| [KDL](fixtures/lang-931123626.fixture) | data | KDL | 931123626 |
| [KFramework](fixtures/lang-9479532.fixture) | programming | KFramework | 9479532 |
| [KRL](fixtures/lang-186.fixture) | programming | KRL | 186 |
| [Kaitai Struct](fixtures/lang-818804755.fixture) | programming | Kaitai Struct | 818804755 |
| [KakouneScript](fixtures/lang-603336474.fixture) | programming | KakouneScript | 603336474 |
| [KerboScript](fixtures/lang-59716426.fixture) | programming | KerboScript | 59716426 |
| [KiCad Layout](fixtures/lang-187.fixture) | data | KiCad Layout | 187 |
| [KiCad Legacy Layout](fixtures/lang-140848857.fixture) | data | KiCad Legacy Layout | 140848857 |
| [KiCad Schematic](fixtures/lang-622447435.fixture) | data | KiCad Schematic | 622447435 |
| [Kickstart](fixtures/lang-692635484.fixture) | data | Kickstart | 692635484 |
| [Kit](fixtures/lang-188.fixture) | markup | Kit | 188 |
| [KoLmafia ASH](fixtures/lang-852099832.fixture) | programming | KoLmafia ASH | 852099832 |
| [Koka](fixtures/lang-597930447.fixture) | programming | Koka | 597930447 |
| [Kotlin](fixtures/lang-189.fixture) | programming | Kotlin | 189 |
| [Kusto](fixtures/lang-225697190.fixture) | data | Kusto | 225697190 |
| [LFE](fixtures/lang-190.fixture) | programming | LFE | 190 |
| [LLVM](fixtures/lang-191.fixture) | programming | LLVM | 191 |
| [LLVM TableGen](fixtures/lang-184265095.fixture) | programming | LLVM TableGen | 184265095 |
| [LOLCODE](fixtures/lang-192.fixture) | programming | LOLCODE | 192 |
| [LSL](fixtures/lang-193.fixture) | programming | LSL | 193 |
| [LTspice Symbol](fixtures/lang-1013566805.fixture) | data | LTspice Symbol | 1013566805 |
| [LabVIEW](fixtures/lang-194.fixture) | programming | LabVIEW | 194 |
| [Lambdapi](fixtures/lang-759240513.fixture) | programming | Lambdapi | 759240513 |
| [Langium](fixtures/lang-548603830.fixture) | programming | Langium | 548603830 |
| [Lark](fixtures/lang-758480799.fixture) | data | Lark | 758480799 |
| [Lasso](fixtures/lang-195.fixture) | programming | Lasso | 195 |
| [Latte](fixtures/lang-196.fixture) | markup | Latte | 196 |
| [Lean](fixtures/lang-197.fixture) | programming | Lean | 197 |
| [Lean 4](fixtures/lang-455147478.fixture) | programming | Lean | 455147478 |
| [Leo](fixtures/lang-916034822.fixture) | programming | Leo | 916034822 |
| [Less](fixtures/lang-198.fixture) | markup | Less | 198 |
| [Lex](fixtures/lang-199.fixture) | programming | Lex | 199 |
| [LigoLANG](fixtures/lang-1040646257.fixture) | programming | LigoLANG | 1040646257 |
| [LilyPond](fixtures/lang-200.fixture) | programming | LilyPond | 200 |
| [Limbo](fixtures/lang-201.fixture) | programming | Limbo | 201 |
| [Linear Programming](fixtures/lang-377204539.fixture) | programming | Linear Programming | 377204539 |
| [Linker Script](fixtures/lang-202.fixture) | programming | Linker Script | 202 |
| [Linux Kernel Module](fixtures/lang-203.fixture) | data | Linux Kernel Module | 203 |
| [Liquid](fixtures/lang-204.fixture) | markup | Liquid | 204 |
| [Liquidsoap](fixtures/lang-614641732.fixture) | programming | Liquidsoap | 614641732 |
| [Literate Agda](fixtures/lang-205.fixture) | programming | Agda | 205 |
| [Literate CoffeeScript](fixtures/lang-206.fixture) | programming | CoffeeScript | 206 |
| [Literate Haskell](fixtures/lang-207.fixture) | programming | Haskell | 207 |
| [LiveCode Script](fixtures/lang-891017.fixture) | programming | LiveCode Script | 891017 |
| [LiveScript](fixtures/lang-208.fixture) | programming | LiveScript | 208 |
| [Lobster](fixtures/lang-790066842.fixture) | programming | Lobster | 790066842 |
| [Logos](fixtures/lang-209.fixture) | programming | Logos | 209 |
| [Logtalk](fixtures/lang-210.fixture) | programming | Logtalk | 210 |
| [LookML](fixtures/lang-211.fixture) | programming | LookML | 211 |
| [LoomScript](fixtures/lang-212.fixture) | programming | LoomScript | 212 |
| [Lua](fixtures/lang-213.fixture) | programming | Lua | 213 |
| [Luau](fixtures/lang-365050359.fixture) | programming | Luau | 365050359 |
| [M](fixtures/lang-214.fixture) | programming | M | 214 |
| [M3U](fixtures/lang-89638692.fixture) | data | M3U | 89638692 |
| [M4](fixtures/lang-215.fixture) | programming | M4 | 215 |
| [M4Sugar](fixtures/lang-216.fixture) | programming | M4 | 216 |
| [MATLAB](fixtures/lang-225.fixture) | programming | MATLAB | 225 |
| [MAXScript](fixtures/lang-217.fixture) | programming | MAXScript | 217 |
| [MDX](fixtures/lang-512838272.fixture) | markup | MDX | 512838272 |
| [MLIR](fixtures/lang-448253929.fixture) | programming | MLIR | 448253929 |
| [MQL4](fixtures/lang-426.fixture) | programming | MQL4 | 426 |
| [MQL5](fixtures/lang-427.fixture) | programming | MQL5 | 427 |
| [MTML](fixtures/lang-218.fixture) | markup | MTML | 218 |
| [MUF](fixtures/lang-219.fixture) | programming | Forth | 219 |
| [Macaulay2](fixtures/lang-34167825.fixture) | programming | Macaulay2 | 34167825 |
| [Makefile](fixtures/lang-220.fixture) | programming | Makefile | 220 |
| [Mako](fixtures/lang-221.fixture) | programming | Mako | 221 |
| [Markdown](fixtures/lang-222.fixture) | prose | Markdown | 222 |
| [Marko](fixtures/lang-932782397.fixture) | markup | Marko | 932782397 |
| [Mask](fixtures/lang-223.fixture) | markup | Mask | 223 |
| [Mathematical Programming System](fixtures/lang-429002699.fixture) | programming | Mathematical Programming System | 429002699 |
| [Maven POM](fixtures/lang-226.fixture) | data | XML | 226 |
| [Max](fixtures/lang-227.fixture) | programming | Max | 227 |
| [MeTTa](fixtures/lang-1037612668.fixture) | programming | MeTTa | 1037612668 |
| [Mercury](fixtures/lang-229.fixture) | programming | Mercury | 229 |
| [Mermaid](fixtures/lang-385992043.fixture) | markup | Mermaid | 385992043 |
| [Meson](fixtures/lang-799141244.fixture) | programming | Meson | 799141244 |
| [Metal](fixtures/lang-230.fixture) | programming | Metal | 230 |
| [Microsoft Developer Studio Project](fixtures/lang-800983837.fixture) | data | Microsoft Developer Studio Project | 800983837 |
| [Microsoft Visual Studio Solution](fixtures/lang-849523096.fixture) | data | Microsoft Visual Studio Solution | 849523096 |
| [MiniD](fixtures/lang-231.fixture) | programming | MiniD | 231 |
| [MiniScript](fixtures/lang-704299647.fixture) | programming | MiniScript | 704299647 |
| [MiniYAML](fixtures/lang-4896465.fixture) | data | MiniYAML | 4896465 |
| [MiniZinc](fixtures/lang-238874535.fixture) | programming | MiniZinc | 238874535 |
| [MiniZinc Data](fixtures/lang-938193433.fixture) | data | MiniZinc Data | 938193433 |
| [Mint](fixtures/lang-968740319.fixture) | programming | Mint | 968740319 |
| [Mirah](fixtures/lang-232.fixture) | programming | Mirah | 232 |
| [Modelica](fixtures/lang-233.fixture) | programming | Modelica | 233 |
| [Modula-2](fixtures/lang-234.fixture) | programming | Modula-2 | 234 |
| [Modula-3](fixtures/lang-564743864.fixture) | programming | Modula-3 | 564743864 |
| [Module Management System](fixtures/lang-235.fixture) | programming | Module Management System | 235 |
| [Mojo](fixtures/lang-1045019587.fixture) | programming | Mojo | 1045019587 |
| [Monkey](fixtures/lang-236.fixture) | programming | Monkey | 236 |
| [Monkey C](fixtures/lang-231751931.fixture) | programming | Monkey C | 231751931 |
| [Moocode](fixtures/lang-237.fixture) | programming | Moocode | 237 |
| [MoonBit](fixtures/lang-181453007.fixture) | programming | MoonBit | 181453007 |
| [MoonScript](fixtures/lang-238.fixture) | programming | MoonScript | 238 |
| [Motoko](fixtures/lang-202937027.fixture) | programming | Motoko | 202937027 |
| [Motorola 68K Assembly](fixtures/lang-477582706.fixture) | programming | Assembly | 477582706 |
| [Move](fixtures/lang-638334599.fixture) | programming | Move | 638334599 |
| [Muse](fixtures/lang-474864066.fixture) | prose | Muse | 474864066 |
| [Mustache](fixtures/lang-638334590.fixture) | markup | Mustache | 638334590 |
| [Myghty](fixtures/lang-239.fixture) | programming | Myghty | 239 |
| [NASL](fixtures/lang-171666519.fixture) | programming | NASL | 171666519 |
| [NCL](fixtures/lang-240.fixture) | programming | NCL | 240 |
| [NEON](fixtures/lang-481192983.fixture) | data | NEON | 481192983 |
| [NL](fixtures/lang-241.fixture) | data | NL | 241 |
| [NMODL](fixtures/lang-136456478.fixture) | programming | NMODL | 136456478 |
| [NPM Config](fixtures/lang-685022663.fixture) | data | INI | 685022663 |
| [NSIS](fixtures/lang-242.fixture) | programming | NSIS | 242 |
| [NWScript](fixtures/lang-731233819.fixture) | programming | NWScript | 731233819 |
| [Nasal](fixtures/lang-178322513.fixture) | programming | Nasal | 178322513 |
| [Nearley](fixtures/lang-521429430.fixture) | programming | Nearley | 521429430 |
| [Nemerle](fixtures/lang-243.fixture) | programming | Nemerle | 243 |
| [NetLinx](fixtures/lang-244.fixture) | programming | NetLinx | 244 |
| [NetLinx+ERB](fixtures/lang-245.fixture) | programming | NetLinx+ERB | 245 |
| [NetLogo](fixtures/lang-246.fixture) | programming | NetLogo | 246 |
| [NewLisp](fixtures/lang-247.fixture) | programming | NewLisp | 247 |
| [Nextflow](fixtures/lang-506780613.fixture) | programming | Nextflow | 506780613 |
| [Nginx](fixtures/lang-248.fixture) | data | Nginx | 248 |
| [Nickel](fixtures/lang-1067292664.fixture) | programming | Nickel | 1067292664 |
| [Nim](fixtures/lang-249.fixture) | programming | Nim | 249 |
| [Ninja](fixtures/lang-250.fixture) | data | Ninja | 250 |
| [Nit](fixtures/lang-251.fixture) | programming | Nit | 251 |
| [Nix](fixtures/lang-252.fixture) | programming | Nix | 252 |
| [Noir](fixtures/lang-813068465.fixture) | programming | Noir | 813068465 |
| [Nu](fixtures/lang-253.fixture) | programming | Nu | 253 |
| [NumPy](fixtures/lang-254.fixture) | programming | Python | 254 |
| [Nunjucks](fixtures/lang-461856962.fixture) | markup | Nunjucks | 461856962 |
| [Nushell](fixtures/lang-446573572.fixture) | programming | Nushell | 446573572 |
| [OASv2-json](fixtures/lang-834374816.fixture) | data | OpenAPI Specification v2 | 834374816 |
| [OASv2-yaml](fixtures/lang-105187618.fixture) | data | OpenAPI Specification v2 | 105187618 |
| [OASv3-json](fixtures/lang-980062566.fixture) | data | OpenAPI Specification v3 | 980062566 |
| [OASv3-yaml](fixtures/lang-51239111.fixture) | data | OpenAPI Specification v3 | 51239111 |
| [OCaml](fixtures/lang-255.fixture) | programming | OCaml | 255 |
| [OMNeT++ MSG](fixtures/lang-664100008.fixture) | programming | OMNeT++ MSG | 664100008 |
| [OMNeT++ NED](fixtures/lang-924868392.fixture) | programming | OMNeT++ NED | 924868392 |
| [Oberon](fixtures/lang-677210597.fixture) | programming | Oberon | 677210597 |
| [ObjDump](fixtures/lang-256.fixture) | data | ObjDump | 256 |
| [Object Data Instance Notation](fixtures/lang-985227236.fixture) | data | Object Data Instance Notation | 985227236 |
| [ObjectScript](fixtures/lang-202735509.fixture) | programming | ObjectScript | 202735509 |
| [Objective-C](fixtures/lang-257.fixture) | programming | Objective-C | 257 |
| [Objective-C++](fixtures/lang-258.fixture) | programming | Objective-C++ | 258 |
| [Objective-J](fixtures/lang-259.fixture) | programming | Objective-J | 259 |
| [Odin](fixtures/lang-889244082.fixture) | programming | Odin | 889244082 |
| [Omgrofl](fixtures/lang-260.fixture) | programming | Omgrofl | 260 |
| [Opa](fixtures/lang-261.fixture) | programming | Opa | 261 |
| [Opal](fixtures/lang-262.fixture) | programming | Opal | 262 |
| [Open Policy Agent](fixtures/lang-840483232.fixture) | programming | Open Policy Agent | 840483232 |
| [OpenAPI Specification v2](fixtures/lang-848295328.fixture) | data | OpenAPI Specification v2 | 848295328 |
| [OpenAPI Specification v3](fixtures/lang-557959099.fixture) | data | OpenAPI Specification v3 | 557959099 |
| [OpenCL](fixtures/lang-263.fixture) | programming | C | 263 |
| [OpenEdge ABL](fixtures/lang-264.fixture) | programming | OpenEdge ABL | 264 |
| [OpenQASM](fixtures/lang-153739399.fixture) | programming | OpenQASM | 153739399 |
| [OpenRC runscript](fixtures/lang-265.fixture) | programming | Shell | 265 |
| [OpenSCAD](fixtures/lang-266.fixture) | programming | OpenSCAD | 266 |
| [OpenStep Property List](fixtures/lang-598917541.fixture) | data | OpenStep Property List | 598917541 |
| [OpenType Feature File](fixtures/lang-374317347.fixture) | data | OpenType Feature File | 374317347 |
| [Option List](fixtures/lang-723589315.fixture) | data | Option List | 723589315 |
| [Org](fixtures/lang-267.fixture) | prose | Org | 267 |
| [OverPy](fixtures/lang-492781155.fixture) | programming | OverPy | 492781155 |
| [OverpassQL](fixtures/lang-689079655.fixture) | programming | OverpassQL | 689079655 |
| [Ox](fixtures/lang-268.fixture) | programming | Ox | 268 |
| [Oxygene](fixtures/lang-269.fixture) | programming | Oxygene | 269 |
| [Oz](fixtures/lang-270.fixture) | programming | Oz | 270 |
| [P4](fixtures/lang-348895984.fixture) | programming | P4 | 348895984 |
| [PDDL](fixtures/lang-736235603.fixture) | programming | PDDL | 736235603 |
| [PEG.js](fixtures/lang-81442128.fixture) | programming | PEG.js | 81442128 |
| [PHP](fixtures/lang-272.fixture) | programming | PHP | 272 |
| [PLSQL](fixtures/lang-273.fixture) | programming | PLSQL | 273 |
| [PLpgSQL](fixtures/lang-274.fixture) | programming | PLpgSQL | 274 |
| [POV-Ray SDL](fixtures/lang-275.fixture) | programming | POV-Ray SDL | 275 |
| [Pact](fixtures/lang-756774415.fixture) | programming | Pact | 756774415 |
| [Pan](fixtures/lang-276.fixture) | programming | Pan | 276 |
| [Papyrus](fixtures/lang-277.fixture) | programming | Papyrus | 277 |
| [Parrot](fixtures/lang-278.fixture) | programming | Parrot | 278 |
| [Parrot Assembly](fixtures/lang-279.fixture) | programming | Parrot | 279 |
| [Parrot Internal Representation](fixtures/lang-280.fixture) | programming | Parrot | 280 |
| [Pascal](fixtures/lang-281.fixture) | programming | Pascal | 281 |
| [Pawn](fixtures/lang-271.fixture) | programming | Pawn | 271 |
| [Pep8](fixtures/lang-840372442.fixture) | programming | Pep8 | 840372442 |
| [Perl](fixtures/lang-282.fixture) | programming | Perl | 282 |
| [Pic](fixtures/lang-425.fixture) | markup | Roff | 425 |
| [Pickle](fixtures/lang-284.fixture) | data | Pickle | 284 |
| [PicoLisp](fixtures/lang-285.fixture) | programming | PicoLisp | 285 |
| [PigLatin](fixtures/lang-286.fixture) | programming | PigLatin | 286 |
| [Pike](fixtures/lang-287.fixture) | programming | Pike | 287 |
| [Pip Requirements](fixtures/lang-684385621.fixture) | data | Pip Requirements | 684385621 |
| [Pkl](fixtures/lang-288822799.fixture) | programming | Pkl | 288822799 |
| [PlantUML](fixtures/lang-833504686.fixture) | data | PlantUML | 833504686 |
| [Pod](fixtures/lang-288.fixture) | prose | Pod | 288 |
| [Pod 6](fixtures/lang-155357471.fixture) | prose | Pod 6 | 155357471 |
| [PogoScript](fixtures/lang-289.fixture) | programming | PogoScript | 289 |
| [Polar](fixtures/lang-839112914.fixture) | programming | Polar | 839112914 |
| [Pony](fixtures/lang-290.fixture) | programming | Pony | 290 |
| [Portugol](fixtures/lang-832391833.fixture) | programming | Portugol | 832391833 |
| [PostCSS](fixtures/lang-262764437.fixture) | markup | CSS | 262764437 |
| [PostScript](fixtures/lang-291.fixture) | markup | PostScript | 291 |
| [Power Query](fixtures/lang-37496382.fixture) | programming | Power Query | 37496382 |
| [PowerBuilder](fixtures/lang-292.fixture) | programming | PowerBuilder | 292 |
| [PowerShell](fixtures/lang-293.fixture) | programming | PowerShell | 293 |
| [Praat](fixtures/lang-106029007.fixture) | programming | Praat | 106029007 |
| [Prisma](fixtures/lang-499933428.fixture) | data | Prisma | 499933428 |
| [Pro*C](fixtures/lang-991047534.fixture) | programming | Pro*C | 991047534 |
| [Processing](fixtures/lang-294.fixture) | programming | Processing | 294 |
| [Procfile](fixtures/lang-305313959.fixture) | programming | Procfile | 305313959 |
| [Proguard](fixtures/lang-716513858.fixture) | data | Proguard | 716513858 |
| [Prolog](fixtures/lang-295.fixture) | programming | Prolog | 295 |
| [Promela](fixtures/lang-441858312.fixture) | programming | Promela | 441858312 |
| [Propeller Spin](fixtures/lang-296.fixture) | programming | Propeller Spin | 296 |
| [Protocol Buffer](fixtures/lang-297.fixture) | data | Protocol Buffer | 297 |
| [Protocol Buffer Text Format](fixtures/lang-436568854.fixture) | data | Protocol Buffer Text Format | 436568854 |
| [Public Key](fixtures/lang-298.fixture) | data | Public Key | 298 |
| [Pug](fixtures/lang-179.fixture) | markup | Pug | 179 |
| [Puppet](fixtures/lang-299.fixture) | programming | Puppet | 299 |
| [Pure Data](fixtures/lang-300.fixture) | data | Pure Data | 300 |
| [PureBasic](fixtures/lang-301.fixture) | programming | PureBasic | 301 |
| [PureScript](fixtures/lang-302.fixture) | programming | PureScript | 302 |
| [Pyret](fixtures/lang-252961827.fixture) | programming | Pyret | 252961827 |
| [Python](fixtures/lang-303.fixture) | programming | Python | 303 |
| [Python console](fixtures/lang-428.fixture) | programming | Python | 428 |
| [Python traceback](fixtures/lang-304.fixture) | data | Python | 304 |
| [Q#](fixtures/lang-697448245.fixture) | programming | Q# | 697448245 |
| [QML](fixtures/lang-305.fixture) | programming | QML | 305 |
| [QMake](fixtures/lang-306.fixture) | programming | QMake | 306 |
| [Qt Script](fixtures/lang-558193693.fixture) | programming | Qt Script | 558193693 |
| [Quake](fixtures/lang-375265331.fixture) | programming | Quake | 375265331 |
| [QuakeC](fixtures/lang-472308069.fixture) | programming | QuakeC | 472308069 |
| [Quartus Simulation IP](fixtures/lang-828144309.fixture) | data | Quartus Simulation IP | 828144309 |
| [QuickBASIC](fixtures/lang-593107205.fixture) | programming | QuickBASIC | 593107205 |
| [Quint](fixtures/lang-562056483.fixture) | programming | Quint | 562056483 |
| [R](fixtures/lang-307.fixture) | programming | R | 307 |
| [RAML](fixtures/lang-308.fixture) | markup | RAML | 308 |
| [RAScript](fixtures/lang-601118790.fixture) | programming | RAScript | 601118790 |
| [RBS](fixtures/lang-899227493.fixture) | data | Ruby | 899227493 |
| [RDoc](fixtures/lang-309.fixture) | prose | RDoc | 309 |
| [REALbasic](fixtures/lang-310.fixture) | programming | REALbasic | 310 |
| [REXX](fixtures/lang-311.fixture) | programming | REXX | 311 |
| [RMarkdown](fixtures/lang-313.fixture) | prose | RMarkdown | 313 |
| [RON](fixtures/lang-587855233.fixture) | data | RON | 587855233 |
| [ROS Interface](fixtures/lang-809230569.fixture) | data | ROS Interface | 809230569 |
| [RPC](fixtures/lang-1031374237.fixture) | programming | RPC | 1031374237 |
| [RPGLE](fixtures/lang-609977990.fixture) | programming | RPGLE | 609977990 |
| [RPM Spec](fixtures/lang-314.fixture) | data | RPM Spec | 314 |
| [RUNOFF](fixtures/lang-315.fixture) | markup | RUNOFF | 315 |
| [Racket](fixtures/lang-316.fixture) | programming | Racket | 316 |
| [Ragel](fixtures/lang-317.fixture) | programming | Ragel | 317 |
| [Raku](fixtures/lang-283.fixture) | programming | Raku | 283 |
| [Rascal](fixtures/lang-173616037.fixture) | programming | Rascal | 173616037 |
| [Raw token data](fixtures/lang-318.fixture) | data | Raw token data | 318 |
| [ReScript](fixtures/lang-501875647.fixture) | programming | ReScript | 501875647 |
| [Readline Config](fixtures/lang-538732839.fixture) | data | INI | 538732839 |
| [Reason](fixtures/lang-869538413.fixture) | programming | Reason | 869538413 |
| [ReasonLIGO](fixtures/lang-319002153.fixture) | programming | LigoLANG | 319002153 |
| [Rebol](fixtures/lang-319.fixture) | programming | Rebol | 319 |
| [Record Jar](fixtures/lang-865765202.fixture) | data | Record Jar | 865765202 |
| [Red](fixtures/lang-320.fixture) | programming | Red | 320 |
| [Redcode](fixtures/lang-321.fixture) | programming | Redcode | 321 |
| [Redirect Rules](fixtures/lang-1020148948.fixture) | data | Redirect Rules | 1020148948 |
| [Redscript](fixtures/lang-686691365.fixture) | programming | Redscript | 686691365 |
| [Regular Expression](fixtures/lang-363378884.fixture) | data | Regular Expression | 363378884 |
| [Ren'Py](fixtures/lang-322.fixture) | programming | Ren'Py | 322 |
| [RenderScript](fixtures/lang-323.fixture) | programming | RenderScript | 323 |
| [Rez](fixtures/lang-498022874.fixture) | programming | Rez | 498022874 |
| [Rhai](fixtures/lang-713228814.fixture) | programming | Rhai | 713228814 |
| [Rich Text Format](fixtures/lang-51601661.fixture) | markup | Rich Text Format | 51601661 |
| [Ring](fixtures/lang-431.fixture) | programming | Ring | 431 |
| [Riot](fixtures/lang-878396783.fixture) | markup | Riot | 878396783 |
| [RobotFramework](fixtures/lang-324.fixture) | programming | RobotFramework | 324 |
| [Robots Exclusion Rules](fixtures/lang-674736065.fixture) | data | Robots Exclusion Rules | 674736065 |
| [Roc](fixtures/lang-440182480.fixture) | programming | Roc | 440182480 |
| [Rocq Prover](fixtures/lang-69.fixture) | programming | Rocq Prover | 69 |
| [Roff](fixtures/lang-141.fixture) | markup | Roff | 141 |
| [Roff Manpage](fixtures/lang-612669833.fixture) | markup | Roff | 612669833 |
| [Rouge](fixtures/lang-325.fixture) | programming | Rouge | 325 |
| [RouterOS Script](fixtures/lang-592853203.fixture) | programming | RouterOS Script | 592853203 |
| [Ruby](fixtures/lang-326.fixture) | programming | Ruby | 326 |
| [Rust](fixtures/lang-327.fixture) | programming | Rust | 327 |
| [SAS](fixtures/lang-328.fixture) | programming | SAS | 328 |
| [SCSS](fixtures/lang-329.fixture) | markup | SCSS | 329 |
| [SELinux Policy](fixtures/lang-880010326.fixture) | data | SELinux Policy | 880010326 |
| [SIP](fixtures/lang-796891177.fixture) | programming | SIP | 796891177 |
| [SMT](fixtures/lang-330.fixture) | programming | SMT | 330 |
| [SPARQL](fixtures/lang-331.fixture) | data | SPARQL | 331 |
| [SQF](fixtures/lang-332.fixture) | programming | SQF | 332 |
| [SQL](fixtures/lang-333.fixture) | data | SQL | 333 |
| [SQLPL](fixtures/lang-334.fixture) | programming | SQLPL | 334 |
| [SRecode Template](fixtures/lang-335.fixture) | markup | SRecode Template | 335 |
| [SSH Config](fixtures/lang-554920715.fixture) | data | INI | 554920715 |
| [STAR](fixtures/lang-424510560.fixture) | data | STAR | 424510560 |
| [STL](fixtures/lang-455361735.fixture) | data | STL | 455361735 |
| [STON](fixtures/lang-336.fixture) | data | Smalltalk | 336 |
| [SVG](fixtures/lang-337.fixture) | data | SVG | 337 |
| [SWIG](fixtures/lang-1066250075.fixture) | programming | SWIG | 1066250075 |
| [Sage](fixtures/lang-338.fixture) | programming | Sage | 338 |
| [Sail](fixtures/lang-1029438153.fixture) | programming | Sail | 1029438153 |
| [Salt](fixtures/lang-339.fixture) | programming | Salt | 339 |
| [Sass](fixtures/lang-340.fixture) | markup | Sass | 340 |
| [Scala](fixtures/lang-341.fixture) | programming | Scala | 341 |
| [Scaml](fixtures/lang-342.fixture) | markup | Scaml | 342 |
| [Scenic](fixtures/lang-619814037.fixture) | programming | Scenic | 619814037 |
| [Scheme](fixtures/lang-343.fixture) | programming | Scheme | 343 |
| [Scilab](fixtures/lang-344.fixture) | programming | Scilab | 344 |
| [Self](fixtures/lang-345.fixture) | programming | Self | 345 |
| [ShaderLab](fixtures/lang-664257356.fixture) | programming | ShaderLab | 664257356 |
| [Shell](fixtures/lang-346.fixture) | programming | Shell | 346 |
| [ShellCheck Config](fixtures/lang-687511714.fixture) | data | ShellCheck Config | 687511714 |
| [ShellSession](fixtures/lang-347.fixture) | programming | ShellSession | 347 |
| [Shen](fixtures/lang-348.fixture) | programming | Shen | 348 |
| [Sieve](fixtures/lang-208976687.fixture) | programming | Sieve | 208976687 |
| [Simple File Verification](fixtures/lang-735623761.fixture) | data | Checksums | 735623761 |
| [Singularity](fixtures/lang-987024632.fixture) | programming | Singularity | 987024632 |
| [Slang](fixtures/lang-239357863.fixture) | programming | Slang | 239357863 |
| [Slash](fixtures/lang-349.fixture) | programming | Slash | 349 |
| [Slice](fixtures/lang-894641667.fixture) | programming | Slice | 894641667 |
| [Slim](fixtures/lang-350.fixture) | markup | Slim | 350 |
| [Slint](fixtures/lang-119900149.fixture) | markup | Slint | 119900149 |
| [SmPL](fixtures/lang-164123055.fixture) | programming | SmPL | 164123055 |
| [Smali](fixtures/lang-351.fixture) | programming | Smali | 351 |
| [Smalltalk](fixtures/lang-352.fixture) | programming | Smalltalk | 352 |
| [Smarty](fixtures/lang-353.fixture) | programming | Smarty | 353 |
| [Smithy](fixtures/lang-1027892786.fixture) | programming | Smithy | 1027892786 |
| [Snakemake](fixtures/lang-151241392.fixture) | programming | Python | 151241392 |
| [Solidity](fixtures/lang-237469032.fixture) | programming | Solidity | 237469032 |
| [Soong](fixtures/lang-222900098.fixture) | data | Soong | 222900098 |
| [SourcePawn](fixtures/lang-354.fixture) | programming | SourcePawn | 354 |
| [SpiceDB Schema](fixtures/lang-864005057.fixture) | data | SpiceDB Schema | 864005057 |
| [Spline Font Database](fixtures/lang-767169629.fixture) | data | Spline Font Database | 767169629 |
| [Squirrel](fixtures/lang-355.fixture) | programming | Squirrel | 355 |
| [Stan](fixtures/lang-356.fixture) | programming | Stan | 356 |
| [Standard ML](fixtures/lang-357.fixture) | programming | Standard ML | 357 |
| [Starlark](fixtures/lang-960266174.fixture) | programming | Starlark | 960266174 |
| [Stata](fixtures/lang-358.fixture) | programming | Stata | 358 |
| [StringTemplate](fixtures/lang-89855901.fixture) | markup | StringTemplate | 89855901 |
| [Stylus](fixtures/lang-359.fixture) | markup | Stylus | 359 |
| [SubRip Text](fixtures/lang-360.fixture) | data | SubRip Text | 360 |
| [SugarSS](fixtures/lang-826404698.fixture) | markup | SugarSS | 826404698 |
| [SuperCollider](fixtures/lang-361.fixture) | programming | SuperCollider | 361 |
| [SurrealQL](fixtures/lang-735141027.fixture) | programming | SurrealQL | 735141027 |
| [Survex data](fixtures/lang-24470517.fixture) | data | Survex data | 24470517 |
| [Svelte](fixtures/lang-928734530.fixture) | markup | Svelte | 928734530 |
| [Sway](fixtures/lang-271471144.fixture) | programming | Sway | 271471144 |
| [Sweave](fixtures/lang-558779190.fixture) | prose | Sweave | 558779190 |
| [Swift](fixtures/lang-362.fixture) | programming | Swift | 362 |
| [SystemVerilog](fixtures/lang-363.fixture) | programming | SystemVerilog | 363 |
| [TI Program](fixtures/lang-422.fixture) | programming | TI Program | 422 |
| [TL-Verilog](fixtures/lang-118656070.fixture) | programming | TL-Verilog | 118656070 |
| [TLA](fixtures/lang-364.fixture) | programming | TLA | 364 |
| [TMDL](fixtures/lang-769162295.fixture) | data | TMDL | 769162295 |
| [TOML](fixtures/lang-365.fixture) | data | TOML | 365 |
| [TSPLIB data](fixtures/lang-89289301.fixture) | data | TSPLIB data | 89289301 |
| [TSQL](fixtures/lang-918334941.fixture) | programming | TSQL | 918334941 |
| [TSV](fixtures/lang-1035892117.fixture) | data | TSV | 1035892117 |
| [TSX](fixtures/lang-94901924.fixture) | programming | TypeScript | 94901924 |
| [TXL](fixtures/lang-366.fixture) | programming | TXL | 366 |
| [Tact](fixtures/lang-606708469.fixture) | programming | Tact | 606708469 |
| [Talon](fixtures/lang-959889508.fixture) | programming | Talon | 959889508 |
| [Tape](fixtures/lang-516874200.fixture) | programming | Tape | 516874200 |
| [Tcl](fixtures/lang-367.fixture) | programming | Tcl | 367 |
| [Tcsh](fixtures/lang-368.fixture) | programming | Shell | 368 |
| [TeX](fixtures/lang-369.fixture) | markup | TeX | 369 |
| [Tea](fixtures/lang-370.fixture) | markup | Tea | 370 |
| [Teal](fixtures/lang-719038619.fixture) | programming | Teal | 719038619 |
| [Terra](fixtures/lang-371.fixture) | programming | Terra | 371 |
| [Terraform Template](fixtures/lang-856832701.fixture) | markup | HCL | 856832701 |
| [Texinfo](fixtures/lang-988020015.fixture) | prose | Texinfo | 988020015 |
| [Text](fixtures/lang-372.fixture) | prose | Text | 372 |
| [TextGrid](fixtures/lang-965696054.fixture) | data | TextGrid | 965696054 |
| [TextMate Properties](fixtures/lang-981795023.fixture) | data | TextMate Properties | 981795023 |
| [Textile](fixtures/lang-373.fixture) | prose | Textile | 373 |
| [Thrift](fixtures/lang-374.fixture) | programming | Thrift | 374 |
| [Toit](fixtures/lang-356554395.fixture) | programming | Toit | 356554395 |
| [Tolk](fixtures/lang-678673060.fixture) | programming | Tolk | 678673060 |
| [Tor Config](fixtures/lang-1016912802.fixture) | data | Tor Config | 1016912802 |
| [Tree-sitter Query](fixtures/lang-436081647.fixture) | programming | Tree-sitter Query | 436081647 |
| [Turing](fixtures/lang-375.fixture) | programming | Turing | 375 |
| [Turtle](fixtures/lang-376.fixture) | data | Turtle | 376 |
| [Twig](fixtures/lang-377.fixture) | markup | Twig | 377 |
| [Type Language](fixtures/lang-632765617.fixture) | data | Type Language | 632765617 |
| [TypeScript](fixtures/lang-378.fixture) | programming | TypeScript | 378 |
| [TypeSpec](fixtures/lang-952272597.fixture) | programming | TypeSpec | 952272597 |
| [Typst](fixtures/lang-704730682.fixture) | programming | Typst | 704730682 |
| [Unified Parallel C](fixtures/lang-379.fixture) | programming | C | 379 |
| [Unity3D Asset](fixtures/lang-380.fixture) | data | Unity3D Asset | 380 |
| [Unix Assembly](fixtures/lang-120.fixture) | programming | Assembly | 120 |
| [Uno](fixtures/lang-381.fixture) | programming | Uno | 381 |
| [UnrealScript](fixtures/lang-382.fixture) | programming | UnrealScript | 382 |
| [Untyped Plutus Core](fixtures/lang-1061635506.fixture) | programming | Untyped Plutus Core | 1061635506 |
| [UrWeb](fixtures/lang-383.fixture) | programming | UrWeb | 383 |
| [V](fixtures/lang-603371597.fixture) | programming | V | 603371597 |
| [VBA](fixtures/lang-399230729.fixture) | programming | VBA | 399230729 |
| [VBScript](fixtures/lang-408016005.fixture) | programming | VBScript | 408016005 |
| [VCL](fixtures/lang-384.fixture) | programming | VCL | 384 |
| [VHDL](fixtures/lang-385.fixture) | programming | VHDL | 385 |
| [Vala](fixtures/lang-386.fixture) | programming | Vala | 386 |
| [Valve Data Format](fixtures/lang-544060961.fixture) | data | Valve Data Format | 544060961 |
| [Velocity Template Language](fixtures/lang-292377326.fixture) | markup | Velocity Template Language | 292377326 |
| [Vento](fixtures/lang-757053899.fixture) | markup | Vento | 757053899 |
| [Verilog](fixtures/lang-387.fixture) | programming | Verilog | 387 |
| [Verse](fixtures/lang-180832205.fixture) | programming | Verse | 180832205 |
| [Vespa Schema Definition](fixtures/lang-587879709.fixture) | data | Vespa Schema Definition | 587879709 |
| [Vim Help File](fixtures/lang-508563686.fixture) | prose | Vim Help File | 508563686 |
| [Vim Snippet](fixtures/lang-81265970.fixture) | markup | Vim Snippet | 81265970 |
| [Vim script](fixtures/lang-388.fixture) | programming | Vim script | 388 |
| [Visual Basic .NET](fixtures/lang-389.fixture) | programming | Visual Basic .NET | 389 |
| [Visual Basic 6.0](fixtures/lang-679594952.fixture) | programming | Visual Basic 6.0 | 679594952 |
| [Volt](fixtures/lang-390.fixture) | programming | Volt | 390 |
| [Vue](fixtures/lang-391.fixture) | markup | Vue | 391 |
| [Vyper](fixtures/lang-1055641948.fixture) | programming | Vyper | 1055641948 |
| [WDL](fixtures/lang-374521672.fixture) | programming | WDL | 374521672 |
| [WGSL](fixtures/lang-836605993.fixture) | programming | WGSL | 836605993 |
| [Wavefront Material](fixtures/lang-392.fixture) | data | Wavefront Material | 392 |
| [Wavefront Object](fixtures/lang-393.fixture) | data | Wavefront Object | 393 |
| [Web Ontology Language](fixtures/lang-394.fixture) | data | Web Ontology Language | 394 |
| [WebAssembly](fixtures/lang-956556503.fixture) | programming | WebAssembly | 956556503 |
| [WebAssembly Interface Type](fixtures/lang-134534086.fixture) | data | WebAssembly Interface Type | 134534086 |
| [WebIDL](fixtures/lang-395.fixture) | programming | WebIDL | 395 |
| [WebVTT](fixtures/lang-658679714.fixture) | data | WebVTT | 658679714 |
| [Wget Config](fixtures/lang-668457123.fixture) | data | INI | 668457123 |
| [Whiley](fixtures/lang-888779559.fixture) | programming | Whiley | 888779559 |
| [Wikitext](fixtures/lang-228.fixture) | prose | Wikitext | 228 |
| [Win32 Message File](fixtures/lang-950967261.fixture) | data | Win32 Message File | 950967261 |
| [Windows Registry Entries](fixtures/lang-969674868.fixture) | data | Windows Registry Entries | 969674868 |
| [Witcher Script](fixtures/lang-686821385.fixture) | programming | Witcher Script | 686821385 |
| [Wolfram Language](fixtures/lang-224.fixture) | programming | Wolfram Language | 224 |
| [Wollok](fixtures/lang-632745969.fixture) | programming | Wollok | 632745969 |
| [World of Warcraft Addon Data](fixtures/lang-396.fixture) | data | World of Warcraft Addon Data | 396 |
| [Wren](fixtures/lang-713580619.fixture) | programming | Wren | 713580619 |
| [X BitMap](fixtures/lang-782911107.fixture) | data | C | 782911107 |
| [X Font Directory Index](fixtures/lang-208700028.fixture) | data | X Font Directory Index | 208700028 |
| [X PixMap](fixtures/lang-781846279.fixture) | data | C | 781846279 |
| [X10](fixtures/lang-397.fixture) | programming | X10 | 397 |
| [XC](fixtures/lang-398.fixture) | programming | XC | 398 |
| [XCompose](fixtures/lang-225167241.fixture) | data | XCompose | 225167241 |
| [XML](fixtures/lang-399.fixture) | data | XML | 399 |
| [XML Property List](fixtures/lang-75622871.fixture) | data | XML | 75622871 |
| [XPages](fixtures/lang-400.fixture) | data | XPages | 400 |
| [XProc](fixtures/lang-401.fixture) | programming | XProc | 401 |
| [XQuery](fixtures/lang-402.fixture) | programming | XQuery | 402 |
| [XS](fixtures/lang-403.fixture) | programming | XS | 403 |
| [XSLT](fixtures/lang-404.fixture) | programming | XSLT | 404 |
| [Xmake](fixtures/lang-225223071.fixture) | programming | Xmake | 225223071 |
| [Xojo](fixtures/lang-405.fixture) | programming | Xojo | 405 |
| [Xonsh](fixtures/lang-614078284.fixture) | programming | Xonsh | 614078284 |
| [Xtend](fixtures/lang-406.fixture) | programming | Xtend | 406 |
| [YAML](fixtures/lang-407.fixture) | data | YAML | 407 |
| [YANG](fixtures/lang-408.fixture) | data | YANG | 408 |
| [YARA](fixtures/lang-805122868.fixture) | programming | YARA | 805122868 |
| [YASnippet](fixtures/lang-378760102.fixture) | markup | YASnippet | 378760102 |
| [Yacc](fixtures/lang-409.fixture) | programming | Yacc | 409 |
| [Yul](fixtures/lang-237469033.fixture) | programming | Yul | 237469033 |
| [ZAP](fixtures/lang-952972794.fixture) | programming | ZAP | 952972794 |
| [ZIL](fixtures/lang-973483626.fixture) | programming | ZIL | 973483626 |
| [Zeek](fixtures/lang-40.fixture) | programming | Zeek | 40 |
| [ZenScript](fixtures/lang-494938890.fixture) | programming | ZenScript | 494938890 |
| [Zephir](fixtures/lang-410.fixture) | programming | Zephir | 410 |
| [Zig](fixtures/lang-646424281.fixture) | programming | Zig | 646424281 |
| [Zimpl](fixtures/lang-411.fixture) | programming | Zimpl | 411 |
| [Zmodel](fixtures/lang-803760908.fixture) | data | Zmodel | 803760908 |
| [cURL Config](fixtures/lang-992375436.fixture) | data | INI | 992375436 |
| [crontab](fixtures/lang-705203557.fixture) | data | crontab | 705203557 |
| [desktop](fixtures/lang-412.fixture) | data | INI | 412 |
| [dircolors](fixtures/lang-691605112.fixture) | data | dircolors | 691605112 |
| [eC](fixtures/lang-413.fixture) | programming | eC | 413 |
| [edn](fixtures/lang-414.fixture) | data | edn | 414 |
| [fish](fixtures/lang-415.fixture) | programming | Shell | 415 |
| [hoon](fixtures/lang-560883276.fixture) | programming | hoon | 560883276 |
| [iCalendar](fixtures/lang-98384424.fixture) | data | iCalendar | 98384424 |
| [jq](fixtures/lang-905371884.fixture) | programming | jq | 905371884 |
| [kvlang](fixtures/lang-970675279.fixture) | markup | kvlang | 970675279 |
| [mIRC Script](fixtures/lang-517654727.fixture) | programming | mIRC Script | 517654727 |
| [mcfunction](fixtures/lang-462488745.fixture) | programming | mcfunction | 462488745 |
| [mdsvex](fixtures/lang-566198445.fixture) | markup | mdsvex | 566198445 |
| [mupad](fixtures/lang-416.fixture) | programming | mupad | 416 |
| [nanorc](fixtures/lang-775996197.fixture) | data | INI | 775996197 |
| [nesC](fixtures/lang-417.fixture) | programming | nesC | 417 |
| [ooc](fixtures/lang-418.fixture) | programming | ooc | 418 |
| [pkg-config](fixtures/lang-925023573.fixture) | data | pkg-config | 925023573 |
| [q](fixtures/lang-970539067.fixture) | programming | q | 970539067 |
| [reStructuredText](fixtures/lang-419.fixture) | prose | reStructuredText | 419 |
| [sed](fixtures/lang-847830017.fixture) | programming | sed | 847830017 |
| [templ](fixtures/lang-795579337.fixture) | markup | templ | 795579337 |
| [ucode](fixtures/lang-365454253.fixture) | programming | ucode | 365454253 |
| [vCard](fixtures/lang-851476558.fixture) | data | vCard | 851476558 |
| [wisp](fixtures/lang-420.fixture) | programming | wisp | 420 |
| [xBase](fixtures/lang-421.fixture) | programming | xBase | 421 |

## Metadata license

The catalog metadata is derived from GitHub Linguist, licensed under MIT. The following upstream notice applies to that metadata; it does not assign a new license to the rest of Workbench. [Pinned upstream license](https://github.com/github-linguist/linguist/blob/538da05f034fa5c83bd81df128d144e208898da3/LICENSE).

```text
Copyright (c) 2017 GitHub, Inc.

Permission is hereby granted, free of charge, to any person
obtaining a copy of this software and associated documentation
files (the "Software"), to deal in the Software without
restriction, including without limitation the rights to use,
copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.
```
