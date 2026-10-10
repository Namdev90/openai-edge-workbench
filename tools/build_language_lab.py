"""Build original reference fixtures from the checked-in Linguist JSON snapshot.

This developer tool uses only Python's standard library. It never downloads a
compiler, executes a fixture, or changes the Workbench application payload.
"""
from __future__ import annotations

import argparse
import collections
import copy
import json
import os
from pathlib import Path
import re
import stat
import tempfile

ROOT = Path(__file__).resolve().parents[1]
LAB = 'language-stat-experiment'
SCHEMA = 'namu-language-stat-experiment/1'
CATALOG_LIMIT = 2 * 1024 * 1024
FIXTURE_LIMIT = 32 * 1024
REFERENCE_SIGNATURE = 'LANGUAGE LAB REFERENCE FIXTURE\n'
ATTRIBUTE_SIGNATURE = '# Namu Language Lab: explicit classification experiment, not application source.\n'
TYPES = {'programming', 'markup', 'data', 'prose'}
TYPE_GUIDANCE = {
    'programming': 'The upstream category describes a programming notation. GitHub normally includes this category in language statistics. Identifying a notation does not establish that this reference contains a valid program or that a matching compiler or interpreter is installed.',
    'markup': 'The upstream category describes markup or a document/template notation. GitHub normally includes this category in language statistics. Rendering, structural validation and template evaluation are separate tasks; this fixture performs none of them.',
    'data': 'The upstream category describes a data, configuration or serialization notation. GitHub normally excludes this category from language statistics. This isolated experiment explicitly enables detection; that choice does not turn reference metadata into executable source code.',
    'prose': 'The upstream category describes a prose/documentation notation. GitHub normally excludes this category from language statistics. This isolated experiment explicitly enables detection; it does not claim that this repository implements the notation or translates human languages.',
}


def regular_path(path: Path) -> None:
    """Reject links/junctions anywhere along the fixed repository output path."""
    for part in (path, *path.parents):
        try:
            info = part.lstat()
        except FileNotFoundError:
            continue
        if stat.S_ISLNK(info.st_mode) or getattr(info, 'st_file_attributes', 0) & 1024:
            raise ValueError('A linked or reparse path was preserved.')


def bounded_text(value, label, limit=512):
    if not isinstance(value, str) or not value or len(value) > limit or any(ord(c) < 32 or ord(c) == 127 for c in value):
        raise ValueError('Invalid '+label+'.')
    return value


def validate_catalog(catalog):
    if not isinstance(catalog, dict) or set(catalog) != {'schema', 'source', 'counts', 'languages'} or catalog['schema'] != SCHEMA:
        raise ValueError('Unknown language catalog schema.')
    source = catalog['source']
    if not isinstance(source, dict):
        raise ValueError('Catalog provenance must be an object.')
    if source.get('repository') != 'github-linguist/linguist' or source.get('path') != 'lib/linguist/languages.yml':
        raise ValueError('Catalog provenance must identify official Linguist metadata.')
    if not re.fullmatch(r'[0-9a-f]{40}', str(source.get('commit', ''))) or not re.fullmatch(r'[0-9a-f]{64}', str(source.get('sha256', ''))):
        raise ValueError('Catalog provenance needs a pinned commit and SHA-256.')
    url=f"https://raw.githubusercontent.com/{source['repository']}/{source['commit']}/{source['path']}"
    if source.get('url') != url:
        raise ValueError('Catalog source URL must match its pinned provenance.')
    rows=catalog['languages']
    if not isinstance(rows, list) or not rows or len(rows)>2000:
        raise ValueError('Catalog entry count is outside the bounded experiment.')
    names=[];identities=[]
    required={'name','language_id','type','group','aliases','extensions','filenames','color','tm_scope','override_alias','fixture','fixture_bytes','upstream_url'}
    for row in rows:
        if not isinstance(row, dict) or set(row)!=required:
            raise ValueError('A catalog reference has unsupported fields.')
        name=bounded_text(row['name'], 'language name')
        identifier=row['language_id']
        if type(identifier) is not int or not 0<=identifier<2**31:
            raise ValueError('Invalid numeric language identifier.')
        if not isinstance(row['type'],str) or row['type'] not in TYPES:
            raise ValueError('Invalid language category.')
        bounded_text(row['group'],'statistical group')
        bounded_text(row['tm_scope'],'TextMate scope')
        override=bounded_text(row['override_alias'],'language override')
        if override!=re.sub(r'\s+', '-', name) or any(c.isspace() for c in override) or not re.fullmatch(r"[A-Za-z0-9_+.#()/:&*'-]+", override):
            raise ValueError('Unsafe or noncanonical language override.')
        if row['fixture']!=f'fixtures/lang-{identifier}.fixture':
            raise ValueError('A fixture path escaped its numeric identifier.')
        if type(row['fixture_bytes']) is not int or not 0<=row['fixture_bytes']<=FIXTURE_LIMIT:
            raise ValueError('Invalid fixture byte count.')
        if row['color'] is not None and (not isinstance(row['color'],str) or not re.fullmatch(r'#[0-9a-fA-F]{6}', row['color'])):
            raise ValueError('Invalid upstream color.')
        for field in ('aliases','extensions','filenames'):
            values=row[field]
            if not isinstance(values,list) or len(values)>512:
                raise ValueError('Invalid reference list: '+field+'.')
            for value in values:bounded_text(value,field)
            if len(values)!=len(set(values)):
                raise ValueError('Duplicate reference list values: '+field+'.')
        if any(not suffix.startswith('.') for suffix in row['extensions']):
            raise ValueError('Upstream extensions must begin with a dot.')
        expected=f"https://github.com/{source['repository']}/blob/{source['commit']}/{source['path']}#L"
        if not isinstance(row['upstream_url'],str) or not row['upstream_url'].startswith(expected) or not row['upstream_url'][len(expected):].isdecimal():
            raise ValueError('Invalid pinned upstream entry link.')
        names.append(name);identities.append(identifier)
    if names!=sorted(names) or len(set(names))!=len(names) or len(set(identities))!=len(identities):
        raise ValueError('Languages must be uniquely identified and sorted by name.')
    if any(row['group'] not in set(names) for row in rows):
        raise ValueError('A statistical parent is absent from this catalog.')
    counts={'entries':len(rows),'types':dict(sorted(collections.Counter(row['type'] for row in rows).items())),
            'statistical_groups':len({row['group'] for row in rows})}
    actual_counts=catalog['counts']
    if (not isinstance(actual_counts,dict) or set(actual_counts)!=set(counts)
            or type(actual_counts.get('entries')) is not int or type(actual_counts.get('statistical_groups')) is not int
            or not isinstance(actual_counts.get('types'),dict)
            or any(type(value) is not int for value in actual_counts['types'].values()) or actual_counts!=counts):
        raise ValueError('Catalog counts do not match its records.')


def recognition_indexes(catalog):
    indexes={field:collections.defaultdict(list) for field in ('extensions','filenames')}
    for row in catalog['languages']:
        for field,index in indexes.items():
            for value in row[field]:index[value].append(row['name'])
    return indexes


def fixture_text(row,catalog,indexes):
    def items(values):return ', '.join(values) if values else '(none listed in the pinned catalog)'
    grouping=(f"This definition contributes bytes to its own '{row['name']}' statistical bucket."
              if row['group']==row['name'] else
              f"This definition contributes bytes to its parent '{row['group']}' bucket. The native language API therefore need not expose '{row['name']}' as a separate key.")
    collisions=[]
    for field in ('extensions','filenames'):
        for spelling in row[field]:
            other=[name for name in indexes[field][spelling] if name!=row['name']]
            if other:collisions.append(f"- {field[:-1]} {spelling}: also associated with {', '.join(other)}")
    ambiguity='\n'.join(collisions) if collisions else 'No extension or exact-filename collisions are recorded for this definition in this snapshot.'
    primary=row['extensions'][0] if row['extensions'] else '(no primary extension; inspect the exact filename rules)'
    return (
        REFERENCE_SIGNATURE+f"Language: {row['name']}\n"
        'Purpose: original reference metadata for an explicitly labeled GitHub language-stat experiment.\n'
        'Program validity: not claimed. Compilation, interpretation and rendering: not performed.\n\n'
        'IDENTITY AND UPSTREAM CATEGORY\n'
        f"Linguist language ID: {row['language_id']}\nCategory: {row['type']}\nStatistical parent: {row['group']}\n"
        +TYPE_GUIDANCE[row['type']]+'\n\n'
        'RECOGNITION REFERENCE\n'
        f"Primary catalog extension: {primary}\nAll catalog extensions ({len(row['extensions'])}): {items(row['extensions'])}\n"
        f"Exact filenames ({len(row['filenames'])}): {items(row['filenames'])}\n"
        f"Explicit upstream aliases ({len(row['aliases'])}): {items(row['aliases'])}\n"
        'These are recognition hints copied as metadata from the pinned definition; the fixture intentionally has a neutral .fixture suffix. No real executable or configuration filename is created.\n\n'
        'CLASSIFICATION AMBIGUITIES\n'+ambiguity+'\n'
        'A shared spelling is not proof of a language. GitHub also uses filename rules, interpreters, heuristics and classification when no explicit override applies. This reference does not run those interpreters or validate a grammar.\n\n'
        'SYNTAX AND PRESENTATION METADATA\n'
        f"TextMate scope: {row['tm_scope']}\nUpstream color: {row['color'] or '(not defined)'}\n"
        'A grammar scope and display color are presentation metadata, not evidence of compiler support or working application features.\n\n'
        'EXPLICIT STATISTICAL EXPERIMENT\n'
        f"Canonical language override: linguist-language={row['override_alias']}\n"
        'Scoped detectable override: true. Scoped generated/vendored/documentation exclusions: false.\n'
        +grouping+'\n'
        'GitHub counts file bytes, not installed tools, compiled programs or feature coverage. This fixture deliberately participates in that display experiment; its bytes remain reference text. GitHub controls grouping, deployed catalog support and asynchronous refresh.\n\n'
        'PINNED PROVENANCE AND LIMITS\n'
        f"Official definition: {row['upstream_url']}\nCatalog raw URL: {catalog['source']['url']}\n"
        f"Catalog SHA-256: {catalog['source']['sha256']}\n"
        'Metadata derives from the MIT-licensed GitHub Linguist catalog; the adjacent Language Lab README retains the upstream notice. This prose was authored for Namu AI Workbench. No third-party example program was copied. The installation dashboard does not load, ship or execute this fixture.\n'
    )


def attribute_text(catalog):
    lines=[ATTRIBUTE_SIGNATURE.rstrip('\n'),
           '# Every .fixture is original reference text, not a validated program.',
           '# These overrides are restricted to numeric fixtures in this folder.',
           '# Generated metadata intentionally participates in the experiment; see README.md.',
           '.gitattributes text eol=lf',
           'index.html linguist-generated=true',
           'atlas.svg text eol=lf linguist-generated=true',
           'catalog.json linguist-generated=true',
           'README.md linguist-generated=true linguist-documentation=true']
    for row in catalog['languages']:
        lines.append(f"{row['fixture']} text eol=lf linguist-language={row['override_alias']} linguist-detectable=true linguist-generated=false linguist-vendored=false linguist-documentation=false")
    return '\n'.join(lines)+'\n'


def generated_files(catalog):
    validate_catalog(catalog)
    refreshed=copy.deepcopy(catalog);indexes=recognition_indexes(refreshed);files={}
    for row in refreshed['languages']:
        content=fixture_text(row,refreshed,indexes).encode('utf-8')
        if len(content)>FIXTURE_LIMIT:raise ValueError('Detailed fixture exceeds the bounded reference size.')
        row['fixture_bytes']=len(content);files[row['fixture']]=content
    files['.gitattributes']=attribute_text(refreshed).encode('utf-8')
    files['catalog.json']=(json.dumps(refreshed,indent=2,ensure_ascii=False,sort_keys=True)+'\n').encode('utf-8')
    if len(files['catalog.json'])>CATALOG_LIMIT or sum(map(len,files.values()))>8*1024*1024:
        raise ValueError('The language experiment exceeded its total size bound.')
    return refreshed,files


def load_catalog(root=ROOT):
    path=Path(root)/LAB/'catalog.json';regular_path(path)
    with path.open('rb') as stream:content=stream.read(CATALOG_LIMIT+1)
    if len(content)>CATALOG_LIMIT:raise ValueError('Catalog is oversized.')
    catalog=json.loads(content);validate_catalog(catalog)
    return catalog


def atomic_output(path,content):
    regular_path(path)
    path.parent.mkdir(parents=True,exist_ok=True);regular_path(path.parent)
    if path.exists():
        if not path.is_file():raise ValueError('A non-file output was preserved.')
        expected=(REFERENCE_SIGNATURE if path.suffix=='.fixture' else ATTRIBUTE_SIGNATURE if path.name=='.gitattributes' else None)
        if expected:
            with path.open('rb') as stream:prefix=stream.read(len(expected.encode()))
            if prefix!=expected.encode():raise ValueError('A foreign generated output was preserved.')
    descriptor,name=tempfile.mkstemp(prefix='.language-lab-',suffix='.tmp',dir=path.parent)
    temporary=Path(name);info=os.fstat(descriptor);identity=(info.st_dev,info.st_ino)
    try:
        with os.fdopen(descriptor,'wb') as stream:stream.write(content)
        regular_path(path);regular_path(temporary)
        os.replace(temporary,path)
    finally:
        try:
            regular_path(temporary)
            info=temporary.stat()
            if (info.st_dev,info.st_ino)==identity:temporary.unlink()
        except (OSError,ValueError):pass


def build(root=ROOT,check=False):
    catalog=load_catalog(root);refreshed,files=generated_files(catalog);folder=Path(root)/LAB
    if check:
        for name,content in files.items():
            path=folder/name;regular_path(path)
            if not path.is_file() or path.read_bytes()!=content:
                raise ValueError('Language Lab output differs from its deterministic catalog: '+name)
    else:
        for name,content in files.items():atomic_output(folder/name,content)
    return {'entries':refreshed['counts']['entries'],'statistical_groups':refreshed['counts']['statistical_groups'],
            'fixture_bytes':sum(row['fixture_bytes'] for row in refreshed['languages']),
            'generated_bytes':sum(map(len,files.values()))}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--check',action='store_true')
    args=parser.parse_args();print(json.dumps(build(check=args.check),sort_keys=True))
