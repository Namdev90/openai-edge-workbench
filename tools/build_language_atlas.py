#!/usr/bin/env python3
"""Render the complete, local-only language atlas from the pinned catalog.

These views describe Linguist classification records. They do not imply that
Workbench implements, compiles, or installs every represented language.
"""

from __future__ import annotations

import argparse
from collections import Counter
from html import escape
import json
from pathlib import Path
import re
import textwrap


ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT / "language-stat-experiment"
TYPE_COLORS = {"programming": "#66dfbf", "markup": "#a6b8ff", "data": "#ffc68a", "prose": "#f2a4d3"}
LICENSE = '''Copyright (c) 2017 GitHub, Inc.

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
OTHER DEALINGS IN THE SOFTWARE.'''


def html(value: object) -> str:
    return escape(str(value), quote=True)


def color(entry: dict) -> str:
    candidate = entry.get("color") or ""
    return candidate if re.fullmatch(r"#[0-9a-fA-F]{6}", candidate) else TYPE_COLORS[entry["type"]]


def md(value: object) -> str:
    return str(value).replace("\\", "\\\\").replace("|", "\\|").replace("[", "\\[").replace("]", "\\]").replace("<", "&lt;").replace(">", "&gt;").replace("\n", " ")


def load_catalog(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    source = data["source"]
    if source["repository"] != "github-linguist/linguist" or not re.fullmatch(r"[0-9a-f]{40}", source["commit"]):
        raise ValueError("Expected a pinned official Linguist catalog")
    if not re.fullmatch(r"[0-9a-f]{64}", source["sha256"]):
        raise ValueError("Missing catalog digest")
    seen = set()
    for entry in data["languages"]:
        ident = entry["language_id"]
        if not isinstance(ident, int) or ident in seen:
            raise ValueError("Language IDs must be unique integers")
        seen.add(ident)
        if entry["type"] not in TYPE_COLORS:
            raise ValueError("Unknown language classification")
        if entry["fixture"] != f"fixtures/lang-{ident}.fixture":
            raise ValueError("Fixture links must stay inside the experiment")
        upstream = entry.get("upstream_url", "")
        prefix = f"https://github.com/github-linguist/linguist/blob/{source['commit']}/lib/linguist/languages.yml#L"
        if not upstream.startswith(prefix) or not upstream[len(prefix):].isdigit():
            raise ValueError("Source links must point to the pinned catalog")
    if len(seen) != data["counts"]["entries"]:
        raise ValueError("Catalog count does not match its records")
    return data


def card(entry: dict) -> str:
    search = " ".join([entry["name"], str(entry["language_id"]), entry["group"], entry["type"], *entry["aliases"], *entry["extensions"], *entry["filenames"]])
    exts = entry["extensions"]
    examples = ", ".join(exts[:6]) if exts else "No extension rule in this snapshot"
    if len(exts) > 6:
        examples += f" · +{len(exts) - 6} more in record"
    aliases = ", ".join(entry["aliases"]) or "No additional aliases"
    grouping = "Own statistical group" if entry["group"] == entry["name"] else "Grouped under " + entry["group"]
    return f'''<article class="language-card" id="language-{entry['language_id']}" data-language-id="{entry['language_id']}" data-name="{html(entry['name'])}" data-type="{html(entry['type'])}" data-group="{html(entry['group'])}" data-search="{html(search)}" style="--language-color:{color(entry)}">
  <div class="card-eyebrow"><span class="type-dot"></span><span>{html(entry['type'])}</span><span class="identifier">#{entry['language_id']}</span></div>
  <h3>{html(entry['name'])}</h3>
  <p class="grouping">{html(grouping)}</p>
  <dl><dt>File patterns</dt><dd>{html(examples)}</dd><dt>Aliases</dt><dd>{html(aliases)}</dd></dl>
  <div class="card-links"><a href="{html(entry['fixture'])}">Reference record <span aria-hidden="true">↗</span></a><a href="{html(entry['upstream_url'])}" target="_blank" rel="noopener noreferrer" aria-label="Pinned Linguist source for {html(entry['name'])}">Source <span aria-hidden="true">↗</span></a></div>
</article>'''


HTML_TEMPLATE = r'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="dark light">
<meta name="description" content="Every entry in a pinned GitHub Linguist catalog, individually searchable. An explicit Namu AI Workbench language-stat experiment.">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; base-uri 'none'; form-action 'none'; connect-src 'none'; img-src data:;">
<title>Language Atlas · Namu AI Workbench</title>
<style>
:root{color-scheme:dark;--bg:#0b1017;--surface:#121b25;--text:#edf4f4;--muted:#a6b5bd;--line:#293642;--accent:#66dfbf;--soft:#19382f;--shadow:0 18px 50px #0003;font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--text);line-height:1.6}a{color:inherit;text-underline-offset:4px}button,input,select{font:inherit}button,a,input,select,summary{-webkit-tap-highlight-color:transparent}a:focus-visible,button:focus-visible,input:focus-visible,select:focus-visible,summary:focus-visible{outline:3px solid var(--accent);outline-offset:4px}a:hover{color:var(--accent)}.skip-link{position:absolute;top:-100px;left:20px;z-index:20;background:var(--accent);color:#0b1017;padding:10px 18px;border-radius:8px}.skip-link:focus{top:16px}.shell{max-width:1480px;margin:auto;padding:0 40px}.masthead{display:flex;align-items:center;justify-content:space-between;gap:20px;padding:26px 0;border-bottom:1px solid var(--line)}.brand{text-decoration:none;font-weight:750;letter-spacing:-.03em;font-size:20px}.brand-mark{display:inline-grid;place-items:center;background:var(--accent);color:#102018;width:30px;height:30px;border-radius:10px;margin-right:10px;font-size:18px;vertical-align:middle}.masthead nav{display:flex;gap:24px;flex-wrap:wrap;font-size:13px;color:var(--muted)}.hero{padding:72px 0 38px;position:relative}.eyebrow{display:flex;align-items:center;gap:10px;text-transform:uppercase;font-size:11px;font-weight:750;letter-spacing:.16em;color:var(--accent);margin:0 0 20px}.eyebrow::before{content:"";width:25px;height:2px;background:currentColor}h1{font-size:clamp(42px,6.5vw,88px);line-height:1.04;letter-spacing:-.065em;margin:0;max-width:1100px;font-weight:730}h1 span{color:var(--accent)}.hero-copy{max-width:770px;color:var(--muted);font-size:18px;line-height:1.75;margin:25px 0 0}.hero-copy strong{color:var(--text);font-weight:550}.metrics{display:grid;grid-template-columns:repeat(4,1fr);border:1px solid var(--line);border-radius:18px;overflow:hidden;margin:35px 0 24px;background:var(--surface)}.metric{padding:24px 28px}.metric+.metric{border-left:1px solid var(--line)}.metric strong{display:block;font-size:34px;letter-spacing:-.045em;font-weight:650;line-height:1.2}.metric span{display:block;color:var(--muted);font-size:12px;margin-top:9px;letter-spacing:.015em}.scope{display:grid;grid-template-columns:1fr auto;gap:20px;align-items:start;border-left:3px solid var(--accent);padding:16px 20px;margin:0 0 40px;background:linear-gradient(90deg,#19382f66,transparent);border-radius:0 10px 10px 0}.scope p{font-size:13px;max-width:950px;margin:0;color:var(--muted)}.scope strong{color:var(--text)}.scope a{font-size:13px;white-space:nowrap}.controls{position:sticky;top:0;z-index:5;background:var(--bg);border-top:1px solid var(--line);border-bottom:1px solid var(--line);padding:18px 0;display:grid;grid-template-columns:minmax(220px,2fr) repeat(3,minmax(130px,1fr));gap:12px}.control label{display:block;font-size:10px;text-transform:uppercase;letter-spacing:.12em;color:var(--muted);font-weight:700;margin-bottom:6px}.control input,.control select{width:100%;height:46px;padding:10px 12px;border:1px solid var(--line);border-radius:9px;color:var(--text);background:var(--surface);min-width:0}.control input::placeholder{color:#84959f}.control input[type=search]::-webkit-search-cancel-button{cursor:pointer}.results-bar{display:flex;justify-content:space-between;align-items:center;gap:20px;padding:23px 0;font-size:13px;color:var(--muted)}.results-bar strong{color:var(--text);font-weight:550}.quiet-button{background:transparent;color:var(--text);border:1px solid var(--line);border-radius:8px;padding:7px 12px;cursor:pointer;font-size:12px}.quiet-button:hover{background:var(--surface)}.language-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:14px;padding-bottom:45px}.language-card{position:relative;min-width:0;display:flex;flex-direction:column;border:1px solid var(--line);border-radius:13px;background:var(--surface);padding:21px;box-shadow:0 5px 15px #0001;transition:transform .16s ease,border-color .16s ease}.language-card:hover{transform:translateY(-3px);border-color:#506471}.card-eyebrow{display:flex;align-items:center;gap:7px;font-size:10px;text-transform:uppercase;letter-spacing:.075em;color:var(--muted);line-height:1.2}.type-dot{width:7px;height:7px;border-radius:50%;background:var(--language-color);flex:none}.identifier{margin-left:auto;font:10px ui-monospace,SFMono-Regular,Consolas,monospace;color:#9caeb9;letter-spacing:0}.language-card h3{font-size:20px;line-height:1.25;letter-spacing:-.03em;margin:17px 0 8px;overflow-wrap:anywhere;font-weight:650}.grouping{font-size:11px;margin:0 0 17px;color:var(--muted);overflow-wrap:anywhere}.language-card dl{margin:0 0 20px}.language-card dt{font-size:9px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:#94a8b5;margin-top:12px}.language-card dd{margin:3px 0 0;font-size:11px;color:#d1dbe0;line-height:1.65;overflow-wrap:anywhere}.card-links{display:flex;justify-content:space-between;gap:12px;margin-top:auto;padding-top:14px;border-top:1px solid var(--line);font-size:10px}.card-links a{text-decoration:none}.card-links a:first-child{color:var(--accent)}.empty-state{padding:70px 20px;text-align:center;border:1px dashed var(--line);border-radius:15px;margin-bottom:40px}.empty-state h3{font-size:24px;margin:0 0 8px}.empty-state p{color:var(--muted);margin:0}.method{border-top:1px solid var(--line);padding:40px 0;display:grid;grid-template-columns:1fr 2fr;gap:70px}.method h2{font-size:28px;letter-spacing:-.04em;margin:0 0 8px}.method .subtle{font-size:12px;color:var(--muted);margin:0}.method-content p{font-size:13px;color:var(--muted);margin:0 0 16px}.method-content strong{color:var(--text)}.method-content code{font-size:11px;background:var(--surface);padding:2px 5px;border-radius:4px;overflow-wrap:anywhere}.method-content summary{cursor:pointer;font-size:13px;color:var(--text)}.method-content details p{margin:15px 0 0}.source-digest{word-break:break-all}.footer{display:flex;justify-content:space-between;gap:20px;padding:26px 0 35px;border-top:1px solid var(--line);color:var(--muted);font-size:11px}.noscript{padding:14px 18px;border:1px solid var(--line);border-radius:9px;color:var(--muted);font-size:13px}[hidden]{display:none!important}
@media(min-width:1600px){.language-grid{grid-template-columns:repeat(5,minmax(0,1fr))}}
@media(max-width:1100px){.language-grid{grid-template-columns:repeat(3,minmax(0,1fr))}.metric{padding:22px}.controls{grid-template-columns:2fr 1fr 1fr}.control:last-child{grid-column:1/-1;display:flex;align-items:center;gap:14px}.control:last-child label{margin:0;white-space:nowrap}.control:last-child select{max-width:250px;height:36px;padding:5px 10px}.method{gap:30px}}
@media(max-width:760px){.shell{padding:0 22px}.masthead{align-items:flex-start}.masthead nav{gap:12px;font-size:11px;justify-content:flex-end}.hero{padding-top:46px}.hero-copy{font-size:15px}.metrics{grid-template-columns:repeat(2,1fr)}.metric:nth-child(3){border-left:0;border-top:1px solid var(--line)}.metric:nth-child(4){border-top:1px solid var(--line)}.metric strong{font-size:30px}.scope{grid-template-columns:1fr;gap:8px}.language-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.controls{position:relative;grid-template-columns:1fr 1fr}.control:first-child{grid-column:1/-1}.control:last-child{grid-column:auto;display:block}.control:last-child label{margin-bottom:6px}.control:last-child select{height:46px;padding:10px 12px;max-width:none}.method{grid-template-columns:1fr;gap:20px}}
@media(max-width:460px){.shell{padding:0 16px}.brand{font-size:16px}.brand-mark{width:26px;height:26px;margin-right:6px}.masthead nav a:first-child{display:none}.hero{padding-top:38px}.language-grid{grid-template-columns:1fr}.metric{padding:18px}.metric span{font-size:11px}.language-card{padding:23px}.results-bar{align-items:flex-start}.footer{flex-direction:column;gap:8px}.scope{margin-bottom:28px}}
@media(prefers-reduced-motion:reduce){*{scroll-behavior:auto!important;transition:none!important}.language-card:hover{transform:none}}
@media print{:root{--bg:white;--surface:white;--text:#111;--muted:#444;--line:#bbb;--accent:#176b55}body{background:white}.shell{max-width:none;padding:0}.masthead nav,.controls,.results-bar button,.skip-link{display:none}.hero{padding:20px 0}.hero h1{font-size:44px}.language-grid{grid-template-columns:repeat(3,minmax(0,1fr));gap:8px}.language-card{break-inside:avoid;box-shadow:none;padding:12px}.language-card h3{font-size:16px}.language-card dd,.language-card dt,.identifier{color:#333}.method{display:block}.footer{margin-top:20px}}
</style>
</head>
<body>
<a class="skip-link" href="#explorer">Skip to language explorer</a>
<div class="shell">
<header class="masthead"><a class="brand" href="https://github.com/Namdev90/openai-edge-workbench"><span class="brand-mark" aria-hidden="true">n</span>Namu AI</a><nav aria-label="Atlas resources"><a href="#method">About this experiment</a><a href="atlas.svg">Full visual atlas ↗</a><a href="catalog.json">JSON catalog ↗</a></nav></header>
<main>
<section class="hero" aria-labelledby="atlas-title"><p class="eyebrow">Workbench / language-stat experiment</p><h1 id="atlas-title">A world of languages.<br><span>Every entry, visible.</span></h1><p class="hero-copy">Explore <strong>@@COUNT@@ individually named records</strong> from a pinned GitHub Linguist catalog. From familiar tools to wonderfully obscure formats, this atlas gives every entry its own place.</p></section>
<div class="metrics" aria-label="Catalog summary"><div class="metric"><strong>@@COUNT@@</strong><span>Catalog entries</span></div><div class="metric"><strong>@@GROUPS@@</strong><span>Potential statistical groups</span></div><div class="metric"><strong>4</strong><span>Catalog classifications</span></div><div class="metric"><strong>100%</strong><span>Snapshot entries shown here</span></div></div>
<aside class="scope"><p><strong>A classification experiment.</strong> The records are detailed metadata references, not programs compiled in every language. GitHub may group languages together or under “Other”; this atlas lists every snapshot entry separately. Workbench’s installed tools and supported features are documented in the main project.</p><a href="#method">How to read this atlas ↓</a></aside>
<section id="explorer" aria-labelledby="explorer-heading"><h2 id="explorer-heading" class="eyebrow">Explore the catalog</h2>
<noscript><p class="noscript">All records are visible below. Search, filters and sorting require JavaScript; the catalog and reference links work without it.</p></noscript>
<div class="controls" id="controls" hidden><div class="control"><label for="search">Find a language</label><input id="search" type="search" placeholder="Name, alias, extension, filename or ID" autocomplete="off" spellcheck="false" aria-controls="languages"></div><div class="control"><label for="type">Classification</label><select id="type" aria-controls="languages"><option value="">All classifications</option value="programming">Programming · @@PROGRAMMING@@</option><option value="markup">Markup · @@MARKUP@@</option><option value="data">Data · @@DATA@@</option><option value="prose">Prose · @@PROSE@@</option></select></div><div class="control"><label for="group">Statistical group</label><select id="group" aria-controls="languages"><option value="">All groups</option>@@GROUP_OPTIONS@@</select></div><div class="control"><label for="sort">Order</label><select id="sort" aria-controls="languages"><option value="name">Name · A to Z</option><option value="type">Classification</option><option value="group">Statistical group</option><option value="id">Linguist ID</option></select></div></div>
<div class="results-bar"><div id="result-count" role="status" aria-live="polite"><strong>@@COUNT@@</strong> of @@COUNT@@ records · all entries shown individually</div><button type="button" class="quiet-button" id="reset" hidden>Reset filters</button></div>
<div class="language-grid" id="languages">@@CARDS@@</div><div class="empty-state" id="empty" hidden><h3>No matching records</h3><p>Try a shorter name, a file extension, or reset the filters.</p></div>
</section>
<section class="method" id="method" aria-labelledby="method-heading"><div><h2 id="method-heading">The map, explained.</h2><p class="subtle">A complete snapshot. Clear boundaries.</p></div><div class="method-content"><p><strong>What each card represents.</strong> One entry in GitHub Linguist’s language catalog, including programming, markup, data and prose. Each reference records classification rules, aliases, filename patterns, its parent group, and provenance. Some entries describe formats or dialects rather than independent programming languages.</p><p><strong>What the native chart represents.</strong> This isolated lab uses explicit per-file Linguist classification overrides. Its substantial reference fixtures intentionally affect the repository’s byte-based language statistics. They are synthetic reference documents, not evidence of @@COUNT@@ working language implementations. GitHub combines parent groups, may use an older catalog, and controls its own chart grouping. The @@GROUPS@@ potential groups are an expectation derived from this snapshot, not a verified count of GitHub’s live results.</p><p><strong>What remains operational.</strong> The lab sits outside the application source and is not installed by the Windows launcher. It adds no language runtimes, accounts, background requests or package dependencies. This page works offline, and its search stays in this browser. External source links open only when selected.</p><details><summary>Inspect the pinned source and reproducible build</summary><p>Catalog: <a href="@@SOURCE_URL@@" target="_blank" rel="noopener noreferrer">github-linguist/linguist · @@COMMIT_SHORT@@</a><br>Source SHA-256: <code class="source-digest">@@SHA@@</code><br>Catalog data: <a href="catalog.json">catalog.json</a> · <a href="README.md#metadata-license">metadata license</a><br>Build: <code>python tools/build_language_atlas.py</code><br>Verify generated views: <code>python tools/build_language_atlas.py --check</code></p></details></div></section>
</main><footer class="footer"><span>Namu AI Workbench · independent community project</span><span>Every catalog entry has a card. No “Other” category in this atlas.</span></footer>
</div>
<script>
'use strict';
(() => {
  const grid = document.getElementById('languages');
  const cards = Array.from(grid.querySelectorAll('.language-card'));
  const search = document.getElementById('search');
  const type = document.getElementById('type');
  const group = document.getElementById('group');
  const sort = document.getElementById('sort');
  const reset = document.getElementById('reset');
  const count = document.getElementById('result-count');
  const empty = document.getElementById('empty');
  const compare = new Intl.Collator('en', {numeric: true, sensitivity: 'base'}).compare;
  const records = cards.map(card => ({card, name: card.dataset.name, type: card.dataset.type, group: card.dataset.group, id: Number(card.dataset.languageId), search: card.dataset.search.toLocaleLowerCase('en')}));
  function update(reorder = false) {
    const query = search.value.trim().toLocaleLowerCase('en');
    const tokens = query.split(/\s+/).filter(Boolean);
    let visible = 0;
    for (const record of records) {
      const matches = (!type.value || record.type === type.value) && (!group.value || record.group === group.value) && tokens.every(token => record.search.includes(token));
      record.card.hidden = !matches;
      visible += Number(matches);
    }
    if (reorder) {
      const key = sort.value;
      const ordered = records.slice().sort((a, b) => key === 'id' ? a.id - b.id : compare(a[key], b[key]) || compare(a.name, b.name));
      const fragment = document.createDocumentFragment();
      for (const record of ordered) fragment.appendChild(record.card);
      grid.appendChild(fragment);
    }
    count.textContent = `${visible} of ${records.length} records · ${visible === records.length ? 'all entries shown individually' : 'filtered view'}`;
    empty.hidden = visible !== 0;
  }
  search.addEventListener('input', () => update());
  type.addEventListener('change', () => update());
  group.addEventListener('change', () => update());
  sort.addEventListener('change', () => update(true));
  reset.addEventListener('click', () => {search.value = ''; type.value = ''; group.value = ''; sort.value = 'name'; update(true); search.focus();});
  document.getElementById('controls').hidden = false;
  reset.hidden = false;
})();
</script>
</body>
</html>
'''


def build_html(data: dict) -> str:
    entries = data["languages"]
    groups = sorted({entry["group"] for entry in entries}, key=str.casefold)
    types = Counter(entry["type"] for entry in entries)
    replacements = {
        "COUNT": str(len(entries)), "GROUPS": str(len(groups)),
        **{key.upper(): str(value) for key, value in types.items()},
        "GROUP_OPTIONS": "".join(f'<option value="{html(group)}">{html(group)}</option>' for group in groups),
        "CARDS": "\n".join(card(entry) for entry in entries),
        "SOURCE_URL": html(f"https://github.com/github-linguist/linguist/blob/{data['source']['commit']}/{data['source']['path']}"),
        "COMMIT_SHORT": html(data["source"]["commit"][:12]), "SHA": html(data["source"]["sha256"]),
    }
    result = HTML_TEMPLATE
    for key, value in replacements.items():
        result = result.replace(f"@@{key}@@", value)
    if re.search(r"@@[A-Z_]+@@", result):
        raise ValueError("Unresolved atlas placeholder")
    return result


def build_svg(data: dict) -> str:
    entries = data["languages"]
    columns, card_width, card_height, gap, margin = 8, 210, 112, 12, 32
    width = margin * 2 + columns * card_width + (columns - 1) * gap
    rows = (len(entries) + columns - 1) // columns
    top = 220
    height = top + rows * (card_height + gap) + 95
    output = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title description">',
              f'<title id="title">Namu AI language atlas: all {len(entries)} Linguist catalog entries</title>',
              '<desc id="description">Every pinned catalog entry is named individually. Colors follow Linguist metadata when available, otherwise classification. These are metadata reference fixtures, not executable implementations. Native GitHub statistics may combine parent groups.</desc>',
              '<style>text{font-family:system-ui,-apple-system,Segoe UI,sans-serif}.name{fill:#edf4f4;font-size:14px;font-weight:650}.meta{fill:#adbdc8;font-size:10px}.label{fill:#66dfbf;font-size:11px;letter-spacing:2px}</style>',
              f'<rect width="{width}" height="{height}" fill="#0b1017"/>',
              '<text x="32" y="43" class="label">NAMU AI / LANGUAGE-STAT EXPERIMENT</text>',
              '<text x="30" y="103" fill="#edf4f4" font-size="48" font-weight="700">Every entry, visible.</text>',
              f'<text x="32" y="139" fill="#adbdc8" font-size="15">{len(entries)} catalog entries · {data["counts"]["statistical_groups"]} potential parent groups · no “Other” category in this atlas</text>',
              '<text x="32" y="168" fill="#adbdc8" font-size="12">Detailed metadata references. No claim of compiled programs or installed support in every language. Zoom in to explore.</text>',
              f'<text x="32" y="190" class="meta">Pinned Linguist source: {html(data["source"]["commit"])} · alphabetical catalog order</text>']
    for position, entry in enumerate(entries):
        x = margin + (position % columns) * (card_width + gap)
        y = top + (position // columns) * (card_height + gap)
        lines = textwrap.wrap(entry["name"], width=23, break_long_words=True, break_on_hyphens=False) or [entry["name"]]
        if len(lines) > 3:
            raise ValueError(f"SVG label needs more space: {entry['name']}")
        output.append(f'<g id="language-{entry["language_id"]}" data-language-id="{entry["language_id"]}"><title>{html(entry["name"])} · {html(entry["type"])} · group: {html(entry["group"])}</title>')
        output.append(f'<rect x="{x}" y="{y}" width="{card_width}" height="{card_height}" rx="9" fill="#121b25" stroke="#293642"/>')
        output.append(f'<circle cx="{x + 15}" cy="{y + 18}" r="3.5" fill="{color(entry)}"/><text x="{x + 26}" y="{y + 22}" class="meta">{html(entry["type"])}</text><text x="{x + card_width - 13}" y="{y + 22}" class="meta" text-anchor="end">#{entry["language_id"]}</text>')
        output.append(f'<text x="{x + 13}" y="{y + 48}" class="name" aria-label="{html(entry["name"])}">')
        for index, line in enumerate(lines):
            output.append(f'<tspan x="{x + 13}" dy="{0 if index == 0 else 17}">{html(line)}</tspan>')
        output.append('</text>')
        group_text = "Own statistical group" if entry["group"] == entry["name"] else "↳ " + entry["group"]
        # Full group names remain in the accessible title and the searchable HTML.
        if len(group_text) > 30:
            group_text = group_text[:27] + "…"
        output.append(f'<text x="{x + 13}" y="{y + 98}" class="meta">{html(group_text)}</text></g>')
    footer_y = height - 48
    output.append(f'<text x="32" y="{footer_y}" fill="#adbdc8" font-size="13">Complete catalog snapshot · Search and inspect every full record in index.html · Metadata: GitHub Linguist (MIT)</text>')
    output.append(f'<text x="32" y="{footer_y + 23}" class="meta">This isolated experiment changes native language byte statistics. The atlas does not claim that every language is used by the Workbench application.</text></svg>')
    return "\n".join(output) + "\n"


def build_readme(data: dict) -> str:
    entries = data["languages"]
    source = data["source"]
    pinned_url = f"https://github.com/github-linguist/linguist/blob/{source['commit']}/{source['path']}"
    parts = [f'''# The Namu AI language atlas

**{len(entries)} individually named catalog entries. A complete atlas with no “Other” category.**

[Open the standalone explorer](index.html) · [View the full visual atlas](atlas.svg) · [Inspect the JSON catalog](catalog.json)

GitHub displays HTML source in its repository viewer. Download the repository, then open `language-stat-experiment/index.html` in a browser for the searchable explorer. It works offline with no installation, dependencies or network requests. All records remain visible when JavaScript is disabled. The SVG opens directly in GitHub and shows every label; zoom in for readable detail.

## What this experiment contains

This is an explicit **language-stat classification experiment**, separate from the Windows application. Every entry in the pinned GitHub Linguist catalog has an original, substantial metadata reference. The records describe real classification metadata: identities, aliases, file patterns, parent groups, detection rules and provenance. They are not compiled or validated programs, and they do not imply that Workbench implements or installs every language.

Scoped `.gitattributes` entries deliberately assign each reference fixture to its catalog language and include programming, markup, data and prose classifications in the experiment. These overrides affect the repository's byte-based language statistics. No padding or copied third-party program samples are needed. The fixtures stay outside `source/` and the Windows installation payload.

| Snapshot classification | Entries |
| --- | ---: |
''']
    types = Counter(entry["type"] for entry in entries)
    for category in ("programming", "markup", "data", "prose"):
        parts.append(f"| {category.title()} | {types[category]} |\n")
    parts.append(f'''
The snapshot contains **{data['counts']['statistical_groups']} distinct parent groups**. That is the expected maximum set of grouped classification keys derived from this catalog, not a statement that the live repository language API has already reported that count. GitHub can deploy an older Linguist catalog, combine dialects under parent languages, exclude files, and group its chart labels. Increasing file sizes cannot guarantee a separate native chart label for every entry. The complete atlas above is independent of that grouping and always shows all {len(entries)} snapshot entries separately.

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
- Pinned catalog: [{source['commit'][:12]} / {md(source['path'])}]({pinned_url})
- Full commit: `{source['commit']}`
- Source SHA-256: `{source['sha256']}`
- Local normalized data and per-entry source locations: [catalog.json](catalog.json)
- Native grouping explanation: [How Linguist works](https://github.com/github-linguist/linguist/blob/{source['commit']}/docs/how-linguist-works.md)
- Explicit classification controls: [Linguist overrides](https://github.com/github-linguist/linguist/blob/{source['commit']}/docs/overrides.md)

## Complete entry index

Every entry below links to its detailed reference. “Group” is the statistical parent, which may combine several entries in GitHub's native language data.

| Catalog entry | Classification | Group | Linguist ID |
| --- | --- | --- | ---: |
''')
    for entry in entries:
        parts.append(f"| [{md(entry['name'])}]({entry['fixture']}) | {md(entry['type'])} | {md(entry['group'])} | {entry['language_id']} |\n")
    parts.append(f'''
## Metadata license

The catalog metadata is derived from GitHub Linguist, licensed under MIT. The following upstream notice applies to that metadata; it does not assign a new license to the rest of Workbench. [Pinned upstream license](https://github.com/github-linguist/linguist/blob/{source['commit']}/LICENSE).

```text
{LICENSE}
```
''')
    return "".join(parts)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Fail if the generated views differ; never write files")
    args = parser.parse_args()
    data = load_catalog(LAB / "catalog.json")
    generated = {"index.html": build_html(data), "atlas.svg": build_svg(data), "README.md": build_readme(data)}
    mismatches = []
    for filename, content in generated.items():
        path = LAB / filename
        expected = content.encode("utf-8")
        if args.check:
            if not path.is_file() or path.read_bytes() != expected:
                mismatches.append(str(path.relative_to(ROOT)))
        else:
            path.write_bytes(expected)
    if mismatches:
        print("Atlas output differs: " + ", ".join(mismatches))
        return 1
    print(f"{'Verified' if args.check else 'Built'} complete atlas: {len(data['languages'])} HTML cards, SVG labels and README index entries")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
