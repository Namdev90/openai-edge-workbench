"""Thirty explicit, read-only diagnostics for the Workbench feature library.

Diagnostics accept no paths or commands from the browser. Configuration and
credential contents are never inspected. A diagnostic failure is an observation,
not permission to change a user's installation or security settings.
"""
from __future__ import annotations

import collections
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import shutil
import socket
import ssl
import time

from engine import SCHEMA, SEMVER, architecture, choose_dotnet_channel, choose_npm, is_reparse, redact, semver_key


_CATALOG = [
    ('Windows architecture readiness', 'Check operating system and native processor architecture.'),
    ('Memory headroom', 'Measure available physical memory before large installations.'),
    ('Installation disk headroom', 'Measure free space on the Workbench installation volume.'),
    ('Processor topology', 'Inspect physical and logical processor capacity.'),
    ('Pending Windows restart', 'Check restart indicators without changing or restarting Windows.'),
    ('Missing PATH folders', 'Find nonexistent folders in the current process search path.'),
    ('Duplicate PATH folders', 'Find repeated search folders without rewriting PATH.'),
    ('CLI search collisions', 'Find multiple copies of curated command-line tools on PATH.'),
    ('Managed command routing', 'Compare current CLI resolution with Workbench-owned launchers.'),
    ('Active binary availability', 'Check that every selected managed entry point still exists.'),
    ('Owned runtime generations', 'List managed runtime and environment generations eligible for review.'),
    ('Managed storage footprint', 'Measure bounded storage use without reading file contents.'),
    ('Ownership marker health', 'Validate ownership records before any future cleanup decision.'),
    ('Active binary fingerprints', 'Compute current executable fingerprints without claiming a publisher match.'),
    ('GitHub source provenance', 'Inspect the recorded source commit and updater outcome.'),
    ('Executable publisher signatures', 'Inspect Authenticode status of managed Windows executables.'),
    ('npm warning audit', 'Run managed npm version discovery and retain any unexpected diagnostics.'),
    ('npm host isolation', 'Check the separate compatible npm host and nightly tool runtime routing.'),
    ('Python environment isolation', 'Check the selected Python environment without loading user site packages.'),
    ('Python dependency consistency', 'Ask uv to check dependencies in the selected managed environment.'),
    ('Package manager readiness', 'Check curated package-manager availability and startup.'),
    ('Editor AI extension readiness', 'Inspect installed default-profile AI and Python extension IDs.'),
    ('Official Node nightly catalog', 'Compare the selected Node runtime with published nightly builds.'),
    ('Official npm catalog', 'Compare the selected npm with the newest supported public npm package.'),
    ('Official .NET preview catalog', 'Check the advertised preview or release-candidate SDK channel.'),
    ('Playwright browser cache readiness', 'Locate the matching browser executable without launching a personal profile.'),
    ('Official download TLS readiness', 'Check certificate-verified TLS to three fixed publisher hosts.'),
    ('Environment variable presence', 'Show only whether curated routing and authentication variable names are set.'),
    ('Migration coverage counters', 'Summarize preserved editor migration conflicts without reading settings.'),
    ('Dashboard session hygiene', 'Inspect current run state and session-file presence without reading its capability.'),
]

FEATURES = [dict(id=f'f{i:03}', title=title, description=description,
                 category='Diagnostics', effect='read-only')
            for i, (title, description) in enumerate(_CATALOG, 1)]
_IDS = {x['id'] for x in FEATURES}
_NAMES = ('node', 'npm', 'npx', 'python', 'uv', 'codex', 'git', 'gh', 'winget', 'code-insiders')
_ALIASES = {'node': 'node-edge.cmd', 'npm': 'npm.cmd', 'python': 'python-edge.cmd',
            'codex': 'codex-edge.cmd', 'openai-api': 'openai-api.cmd', 'dotnet': 'dotnet-edge.cmd'}
_MAX_ITEMS = 256


def _scrub(value):
    if isinstance(value, str):
        return redact(value)[:12000]
    if isinstance(value, dict):
        return {redact(k): '[REDACTED]' if re.fullmatch(r'access_token|refresh_token|id_token|api_key|password|client_secret|authorization', str(k), re.I) else _scrub(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_scrub(x) for x in value[:_MAX_ITEMS]]
    if value is None or isinstance(value, (bool, int, float)):
        return value
    return redact(str(value))[:2000]


def _result(summary, data, warnings=()):
    result = {'summary': summary, 'data': data}
    if warnings:
        result['warnings'] = list(warnings)
    return _scrub(result)


def _error_text(exc):
    # Windows OSError.__str__ represents filenames with doubled backslashes.
    # Keep the actual OS failure/code, not an escaped private filename that a
    # normal-path redactor cannot reliably recognize.
    if isinstance(exc, OSError) and getattr(exc, 'filename', None):
        code = getattr(exc, 'winerror', None) or getattr(exc, 'errno', None)
        return f'OS error {code}: {exc.strerror or type(exc).__name__}'
    return redact(str(exc))


def _tools(ctx):
    tools = getattr(ctx.workbench, 'active', {})
    if not isinstance(tools, dict):
        raise ValueError('Managed tool state is malformed.')
    return tools


def _managed(ctx, raw):
    """Never execute or inspect a path outside the managed installation."""
    if not isinstance(raw, (str, Path)):
        raise ValueError('Managed path must be a path string.')
    p = Path(raw)
    if not p.is_absolute():
        raise ValueError('Managed path must be absolute.')
    p = Path(os.path.abspath(p))
    root = Path(os.path.abspath(ctx.root))
    if not p.is_relative_to(root) or p == root:
        raise ValueError('Managed path escaped the Workbench installation.')
    ctx.safe_path(p)
    return p


def _command_for(ctx, name):
    record = _tools(ctx).get(name)
    if not isinstance(record, dict):
        raise ValueError(f'No selected {name} environment is available.')
    argv = record.get('command')
    if not isinstance(argv, list) or not 1 <= len(argv) <= 3:
        raise ValueError('Managed tool command has an invalid shape.')
    paths = [_managed(ctx, x) for x in argv]
    names = [p.name.lower() for p in paths]
    allowed = {'node': ['node.exe'], 'npm': ['node.exe', 'npm-cli.js'],
               'python': ['python.exe'], 'codex': ['node.exe', 'codex.js'],
               'dotnet': ['dotnet.exe']}
    if name == 'openai-api':
        valid_names = len(names) == 1 and bool(re.fullmatch(r'openai(?:-api)?\.exe', names[0]))
    else:
        valid_names = name in allowed and names == allowed[name]
    if not valid_names or any(p.relative_to(ctx.root).parts[0] not in ('runtimes', 'environments') for p in paths):
        raise ValueError('Managed entry point is outside the fixed tool catalog.')
    if not all(p.is_file() for p in paths):
        raise ValueError('Selected managed entry point is missing.')
    # The state describes entry point files, never caller-supplied arguments.
    if any(p.suffix.lower() not in ('.exe', '.js', '.py', '.cmd') for p in paths):
        raise ValueError('Unsupported managed entry point type.')
    return [str(p) for p in paths]


def _execute(ctx, argv, *, timeout=20):
    try:
        result = ctx.command(argv, timeout=timeout)
    except (OSError, ValueError, TimeoutError) as exc:
        return {'exit_code': -1, 'output': _error_text(exc), 'ok': False}
    if isinstance(result, dict) and result.get('exit_code') is None:
        return {'exit_code': -1, 'output': redact(result.get('output', 'Diagnostic did not execute.'))[:12000], 'ok': False}
    if not isinstance(result, dict) or not isinstance(result.get('exit_code'), int):
        return {'exit_code': -1, 'output': 'Command returned malformed evidence.', 'ok': False}
    return {'exit_code': result['exit_code'], 'output': redact(result.get('output', ''))[:12000],
            'ok': result['exit_code'] == 0}


def _json_command(ctx, argv):
    r = _execute(ctx, argv)
    if not r['ok']:
        raise ValueError('Read-only query failed: ' + r['output'])
    try:
        data = json.loads(r['output'])
    except (ValueError, TypeError) as exc:
        raise ValueError('Read-only query did not return unambiguous JSON.') from exc
    return data


def _powershell(ctx, script):
    if os.name != 'nt':
        raise ValueError('This diagnostic requires Windows; no Windows observation was made.')
    exe = Path(os.environ.get('SystemRoot', r'C:\Windows')) / 'System32/WindowsPowerShell/v1.0/powershell.exe'
    ctx.safe_path(exe)
    if not exe.is_file():
        raise ValueError('Native Windows PowerShell is unavailable.')
    modules = ['Microsoft.PowerShell.Management', 'Microsoft.PowerShell.Utility', 'Microsoft.PowerShell.Security']
    if 'Get-CimInstance' in script:
        modules.append('CimCmdlets')
    if 'Get-AppxPackage' in script:
        modules.append('Appx')
    imports = ''.join("Import-Module ([IO.Path]::Combine($PSHOME,'Modules/" + name + '/' + name + ".psd1')) -ErrorAction Stop;" for name in modules)
    return _json_command(ctx, [str(exe), '-NoLogo', '-NoProfile', '-NonInteractive', '-Command',
                               "$ErrorActionPreference='Stop';" + imports + script])


def _read_json(ctx, path):
    path = _managed(ctx, path)
    if path.stat().st_size > 256 * 1024:
        raise ValueError('Managed metadata exceeds the diagnostic size limit.')
    data = json.loads(path.read_text(encoding='utf-8-sig'))
    if not isinstance(data, dict):
        raise ValueError('Managed metadata is not an object.')
    return data


def _path_entries():
    entries = os.environ.get('PATH', '').split(os.pathsep)
    return [(i, Path(x.strip().strip('"'))) for i, x in enumerate(entries[:_MAX_ITEMS]) if x.strip().strip('"')]


def _generations(ctx):
    generations = []; refused = []; truncated = False
    for group in ('runtimes', 'environments'):
        base = _managed(ctx, Path(ctx.root) / group)
        if not base.is_dir():
            continue
        children = sorted(base.iterdir())
        truncated = truncated or len(children) > _MAX_ITEMS
        for child in children[:_MAX_ITEMS]:
            if is_reparse(child):
                refused.append(str(child.relative_to(ctx.root))); continue
            _managed(ctx, child)
            if not child.is_dir():
                continue
            if group == 'environments':
                generations.append(child)
            else:
                candidates = sorted(child.iterdir())
                truncated = truncated or len(candidates) > _MAX_ITEMS
                for generation in candidates[:_MAX_ITEMS]:
                    if is_reparse(generation):
                        refused.append(str(generation.relative_to(ctx.root))); continue
                    _managed(ctx, generation)
                    if generation.is_dir():
                        generations.append(generation)
            if len(generations) >= _MAX_ITEMS:
                return generations[:_MAX_ITEMS], True, refused[:_MAX_ITEMS]
    return generations, truncated, refused[:_MAX_ITEMS]


def _curated(ctx, name, args):
    if name not in ('uv', 'git', 'gh', 'winget', 'code-insiders'):
        raise ValueError('Executable is outside the diagnostic catalog.')
    exe = shutil.which(name)
    if not exe:
        return {'available': False, 'ok': False, 'output': 'Executable unavailable.'}
    try:
        ctx.safe_path(Path(exe))
    except (OSError, ValueError) as exc:
        # WindowsApps aliases are intentionally reparse points. Inspect the
        # fixed registered Microsoft package instead of following that alias.
        if name == 'winget' and os.name == 'nt' and args == ['--version']:
            script = "$p=Get-AppxPackage -Name Microsoft.DesktopAppInstaller|Sort-Object Version -Descending|Select-Object -First 1;if(!$p){throw 'Registered Microsoft WinGet package unavailable.'};$exe=Join-Path $p.InstallLocation 'winget.exe';if(!(Test-Path -LiteralPath $exe -PathType Leaf)){throw 'Registered WinGet executable unavailable.'};if((Get-Item -LiteralPath $exe).Attributes -band [IO.FileAttributes]::ReparsePoint){throw 'Registered WinGet executable is a reparse point.'};$s=Get-AuthenticodeSignature -LiteralPath $exe;if($s.Status.ToString() -ne 'Valid' -or !$s.SignerCertificate -or $s.SignerCertificate.Subject -notmatch 'Microsoft'){throw 'Registered WinGet publisher signature could not be verified.'};$out=& $exe --version;[pscustomobject]@{available=$true;exit_code=$LASTEXITCODE;output=($out -join [Environment]::NewLine);ok=($LASTEXITCODE -eq 0);resolution='Registered signed Microsoft package'}|ConvertTo-Json -Compress"
            try:
                data = _powershell(ctx, script)
                if not isinstance(data, dict) or not isinstance(data.get('ok'), bool) or not isinstance(data.get('exit_code'), int):
                    raise ValueError('Registered WinGet query returned malformed evidence.')
                return data
            except (OSError, ValueError) as fallback_exc:
                return {'available': True, 'ok': False, 'output': _error_text(fallback_exc)}
        return {'available': True, 'ok': False, 'output': 'Curated executable path was refused: ' + _error_text(exc)}
    return {'available': True, **_execute(ctx, [exe, *args])}


def _diagnose(feature_id, ctx):
    tools = _tools(ctx)
    if feature_id == 'f001':
        machine = platform.machine().lower()
        try:
            native = architecture()
        except RuntimeError:
            native = 'unsupported'
        supported = platform.system() == 'Windows' and native in ('x64', 'arm64')
        return _result('Native platform readiness checked.',
                       {'system': platform.system(), 'machine': machine, 'native_architecture': native, 'supported': supported},
                       () if supported else ['Workbench installations require 64-bit Windows x64 or ARM64.'])
    if feature_id == 'f002':
        data = _powershell(ctx, "$x=Get-CimInstance Win32_OperatingSystem;[pscustomobject]@{total_kib=[long]$x.TotalVisibleMemorySize;free_kib=[long]$x.FreePhysicalMemory}|ConvertTo-Json -Compress")
        if not isinstance(data, dict) or not all(isinstance(data.get(k), int) and data[k] >= 0 for k in ('total_kib', 'free_kib')) or not 0 <= data['free_kib'] <= data['total_kib'] or data['total_kib'] == 0:
            raise ValueError('Windows memory observation has an invalid shape.')
        return _result('Physical memory measured.', data, () if data['free_kib'] >= 2 * 1024**2 else ['Less than 2 GiB physical memory is currently free.'])
    if feature_id == 'f003':
        ctx.safe_path(Path(ctx.root))
        usage = shutil.disk_usage(ctx.root)
        return _result('Installation volume free space measured.', {'total_bytes': usage.total, 'used_bytes': usage.used, 'free_bytes': usage.free},
                       () if usage.free >= 4 * 1024**3 else ['Less than 4 GiB free on the installation volume.'])
    if feature_id == 'f004':
        data = _powershell(ctx, "@(Get-CimInstance Win32_Processor|Select-Object NumberOfCores,NumberOfLogicalProcessors,AddressWidth)|ConvertTo-Json -Compress")
        rows = data if isinstance(data, list) else [data]
        if not rows or any(not isinstance(x, dict) or not all(isinstance(x.get(k), int) and x[k] > 0 for k in ('NumberOfCores', 'NumberOfLogicalProcessors', 'AddressWidth')) for x in rows):
            raise ValueError('Processor observation has an invalid shape.')
        return _result('Processor topology inspected.', {'processors': rows, 'logical_total': sum(x['NumberOfLogicalProcessors'] for x in rows)})
    if feature_id == 'f005':
        script = "[pscustomobject]@{component_servicing=(Test-Path 'HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Component Based Servicing\\RebootPending');windows_update=(Test-Path 'HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\WindowsUpdate\\Auto Update\\RebootRequired');pending_file_rename=([bool](Get-ItemProperty 'HKLM:\\SYSTEM\\CurrentControlSet\\Control\\Session Manager' -Name PendingFileRenameOperations -ErrorAction SilentlyContinue))}|ConvertTo-Json -Compress"
        data = _powershell(ctx, script)
        if not isinstance(data, dict) or not all(isinstance(data.get(k), bool) for k in ('component_servicing', 'windows_update', 'pending_file_rename')):
            raise ValueError('Restart indicator observation has an invalid shape.')
        return _result('Windows restart indicators inspected; no restart initiated.', data,
                       ['At least one Windows component indicates a pending restart.'] if any(data.values()) else [])
    if feature_id == 'f006':
        missing = [{'position': i} for i, p in _path_entries() if not p.is_dir()]
        return _result('Current-process PATH folder existence checked.', {'missing': missing, 'scope': 'Current process PATH only; no machine/user values exported.'},
                       [f'{len(missing)} PATH folders are unavailable.'] if missing else [])
    if feature_id == 'f007':
        grouped = collections.defaultdict(list)
        for i, p in _path_entries():
            grouped[os.path.normcase(os.path.abspath(p))].append(i)
        duplicates = [{'positions': indices} for indices in grouped.values() if len(indices) > 1]
        return _result('Repeated PATH search folders inspected.', {'duplicates': duplicates}, [f'{len(duplicates)} duplicate search folders found.'] if duplicates else [])
    if feature_id == 'f008':
        collisions = {}
        suffixes = ('.exe', '.cmd', '.bat', '') if os.name == 'nt' else ('',)
        for name in _NAMES:
            matches = []; seen = set()
            for position, directory in _path_entries():
                for suffix in suffixes:
                    candidate = directory / (name + suffix)
                    if candidate.is_file() and not is_reparse(candidate):
                        raw = os.path.abspath(candidate)
                        if raw not in seen:
                            seen.add(raw)
                            matches.append({'path_position': position, 'entry_name': name + suffix})
            if len(matches) > 1:
                collisions[name] = matches[:20]
        return _result('Curated CLI search collisions inspected.', {'collisions': collisions}, ['Multiple copies can resolve differently in other terminals.'] if collisions else [])
    if feature_id == 'f009':
        records = []
        for name, alias in _ALIASES.items():
            if name not in tools:
                continue
            expected = _managed(ctx, Path(ctx.root) / 'bin' / alias)
            found = shutil.which(alias) if os.name == 'nt' else None
            matches = bool(found and os.path.normcase(os.path.abspath(found)) == os.path.normcase(str(expected)))
            records.append({'tool': name, 'launcher_present': expected.is_file(), 'managed_launcher': alias,
                            'resolution_scope': 'managed' if matches else 'other installation' if found else 'unavailable', 'matches_managed_launcher': matches})
        return _result('Managed launcher routing checked for the current process.', records,
                       ['Some current-process launchers do not resolve to the managed directory. Use Edge Terminal for its explicit routing.'] if any(not x['matches_managed_launcher'] for x in records) else [])
    if feature_id == 'f010':
        records = []
        for name in sorted(tools)[:_MAX_ITEMS]:
            entry = tools[name]
            if isinstance(entry, dict) and 'path' in entry and 'command' not in entry:
                path = _managed(ctx, entry['path'])
                records.append({'tool': name, 'kind': 'workspace', 'available': path.is_dir()})
                continue
            try:
                paths = _command_for(ctx, name)
                records.append({'tool': name, 'kind': 'entry point', 'available': True, 'paths': paths})
            except ValueError as exc:
                records.append({'tool': name, 'available': False, 'reason': str(exc)})
        return _result('Selected managed entry points checked.', records,
                       ['One or more selected entry points are unavailable or outside the managed boundary.'] if any(not x['available'] for x in records) else ([] if records else ['No selected managed entry points are recorded.']))
    if feature_id == 'f011':
        generations, truncated, refused = _generations(ctx)
        active_paths = []
        for record in tools.values():
            if isinstance(record, dict):
                for raw in record.get('command', []) if isinstance(record.get('command', []), list) else []:
                    active_paths.append(_managed(ctx, raw))
                if record.get('path'):
                    active_paths.append(_managed(ctx, record['path']))
        records = [{'directory': str(p.relative_to(ctx.root)), 'active': any(a.is_relative_to(p) for a in active_paths), 'regular_marker_present': not is_reparse(p / '.workbench-owned.json') and (p / '.workbench-owned.json').is_file()} for p in generations]
        warnings = (['Generation inventory reached its safety limit.'] if truncated else []) + (['Reparse aliases were excluded and preserved; their targets were not followed.'] if refused else [])
        return _result('Managed generation inventory inspected; nothing removed.', {'generations': records, 'truncated': truncated, 'excluded_reparse_paths': refused}, warnings)
    if feature_id == 'f012':
        counts = {}; scanned = 0; bounded = False; excluded = 0
        deadline = time.monotonic() + 15
        for group in ('runtimes', 'environments', 'downloads', 'setup'):
            base = _managed(ctx, Path(ctx.root) / group); total = 0; files = 0
            if base.is_dir():
                for directory, subdirs, filenames in os.walk(base, followlinks=False):
                    _managed(ctx, Path(directory))
                    regular = [n for n in subdirs if not is_reparse(Path(directory) / n)]
                    excluded += len(subdirs) - len(regular); subdirs[:] = regular
                    for name in filenames:
                        # The containing directory was verified above. lstat
                        # observes the file itself without following a link.
                        p = Path(directory) / name
                        if is_reparse(p):
                            excluded += 1; continue
                        if not p.is_file():
                            continue
                        total += p.stat().st_size; files += 1; scanned += 1
                        if scanned >= 20000 or time.monotonic() >= deadline:
                            bounded = True; break
                    if bounded:
                        break
            counts[group] = {'bytes': total, 'files': files}
            if bounded:
                break
        warnings = (['Scan capped at 20,000 files or 15 seconds; totals are partial.'] if bounded else []) + (['Reparse entries were excluded; their targets were not followed.'] if excluded else [])
        return _result('Managed storage measured without reading file contents.', {'groups': counts, 'partial': bounded, 'scanned_files': scanned, 'excluded_reparse_entries': excluded}, warnings)
    if feature_id == 'f013':
        generations, truncated, refused = _generations(ctx); records = []
        for generation in generations:
            marker = generation / '.workbench-owned.json'
            try:
                data = _read_json(ctx, marker)
                valid = data.get('owned_by') == SCHEMA and isinstance(data.get('version'), str) and 0 < len(data['version']) <= 300
                records.append({'directory': str(generation.relative_to(ctx.root)), 'valid': valid})
            except (OSError, ValueError) as exc:
                records.append({'directory': str(generation.relative_to(ctx.root)), 'valid': False, 'reason': _error_text(exc)})
        warnings = (['Invalid or missing markers must be preserved for review.'] if any(not x['valid'] for x in records) else []) + (['Reparse aliases were excluded and preserved; their targets were not followed.'] if refused else [])
        return _result('Ownership records inspected; no cleanup permission inferred.', {'markers': records, 'partial': truncated, 'excluded_reparse_paths': refused}, warnings)
    if feature_id == 'f014':
        fingerprints = []; seen = set(); total = 0
        for name in sorted(tools)[:_MAX_ITEMS]:
            if not isinstance(tools[name], dict) or 'command' not in tools[name]:
                continue
            for raw in _command_for(ctx, name):
                p = _managed(ctx, raw)
                if p in seen:
                    continue
                seen.add(p); size = p.stat().st_size
                if size > 128 * 1024**2 or total + size > 512 * 1024**2:
                    fingerprints.append({'tool': name, 'file': str(p.relative_to(ctx.root)), 'skipped': 'Fingerprint size limit.'}); continue
                digest = hashlib.sha256()
                with p.open('rb') as stream:
                    for block in iter(lambda: stream.read(1024 * 1024), b''):
                        digest.update(block)
                total += size
                fingerprints.append({'tool': name, 'file': str(p.relative_to(ctx.root)), 'bytes': size, 'sha256': digest.hexdigest()})
        return _result('Current managed entry point fingerprints computed.', {'files': fingerprints, 'publisher_comparison': 'Not performed; a fingerprint alone does not prove publisher authenticity.'}, [] if fingerprints else ['No selected managed entry points are available to fingerprint.'])
    if feature_id == 'f015':
        status = _read_json(ctx, Path(ctx.root) / 'Setup-Status.json')
        commit = status.get('commit', '')
        valid = isinstance(commit, str) and bool(re.fullmatch(r'[a-f0-9]{40}', commit))
        projection = {k: status.get(k) for k in ('repository', 'commit', 'state', 'utc')}
        projection['valid_commit_identity'] = valid
        return _result('Updater provenance record inspected; no remote freshness claim made.', projection,
                       ['Source commit is invalid or the last updater did not verify a fresh GitHub commit.'] if not valid or status.get('state') != 'VERIFIED_GITHUB_COMMIT' else [])
    if feature_id == 'f016':
        paths = sorted({str(_managed(ctx, x)) for name in tools if isinstance(tools[name], dict) and 'command' in tools[name] for x in _command_for(ctx, name) if str(x).lower().endswith('.exe')})
        if not paths:
            return _result('No selected managed Windows executable is available for signature inspection.', [])
        quoted = ','.join("'" + p.replace("'", "''") + "'" for p in paths[:20])
        script = "@(" + quoted + ")|ForEach-Object{$s=Get-AuthenticodeSignature -LiteralPath $_;[pscustomobject]@{file=[IO.Path]::GetFileName($_);status=$s.Status.ToString();publisher=$(if($s.SignerCertificate){$s.SignerCertificate.Subject}else{''})}}|ConvertTo-Json -Compress"
        data = _powershell(ctx, script); rows = data if isinstance(data, list) else [data]
        if any(not isinstance(x, dict) or not isinstance(x.get('status'), str) for x in rows):
            raise ValueError('Signature query returned malformed evidence.')
        return _result('Executable Authenticode signatures inspected.', rows,
                       ['At least one selected executable has no Valid Authenticode status. Hash-based publisher verification is a separate check.'] if any(x['status'] != 'Valid' for x in rows) else [])
    if feature_id == 'f017':
        r = _execute(ctx, [*_command_for(ctx, 'npm'), '--version'])
        lines = [x.strip() for x in r['output'].splitlines() if x.strip()]
        versions = [x for x in lines if SEMVER.fullmatch(x)]
        clean = r['ok'] and len(lines) == 1 and len(versions) == 1 and versions[0] == tools['npm'].get('version')
        return _result('Managed npm version output checked for warnings.', {**r, 'clean_version_output': clean, 'expected_version': tools['npm'].get('version')},
                       [] if clean else ['npm startup failed, emitted diagnostics, or did not match the selected version. No warning was suppressed.'])
    if feature_id == 'f018':
        npm = _command_for(ctx, 'npm'); node = _command_for(ctx, 'node')
        host = _managed(ctx, npm[0]); nightly = _managed(ctx, node[0]); same = host == nightly
        versions = {k: tools[k].get('version') for k in ('node', 'npm')}
        data = {'versions': versions, 'npm_host_version': tools['npm'].get('host_version'), 'npm_engine_range': tools['npm'].get('engines'), 'separate_host': not same, 'host_inside_private_runtime': host.is_relative_to(Path(ctx.root) / 'runtimes'), 'nightly_selected': 'nightly' in str(versions['node'])}
        return _result('npm host routing inspected; no runtime changed.', data,
                       ['The selected Node tool runtime is not a nightly build.'] if not data['nightly_selected'] else [])
    if feature_id == 'f019':
        argv = _command_for(ctx, 'python')
        script = "import json,sys,site,pathlib;root=pathlib.Path(" + repr(str(ctx.root)) + ");print(json.dumps({'prefix_is_managed':pathlib.Path(sys.prefix).is_relative_to(root),'virtual_environment':sys.prefix!=sys.base_prefix,'user_site_enabled':site.ENABLE_USER_SITE,'isolated':bool(sys.flags.isolated)}))"
        data = _json_command(ctx, [*argv, '-I', '-B', '-c', script])
        if not isinstance(data, dict) or not all(isinstance(data.get(k), bool) for k in ('prefix_is_managed', 'virtual_environment', 'isolated', 'user_site_enabled')):
            raise ValueError('Python isolation query returned malformed evidence.')
        isolated = data['isolated'] and data['user_site_enabled'] is False and data['prefix_is_managed'] and data['virtual_environment']
        return _result('Managed Python isolation exercised without user startup hooks.', {'environment_isolated': isolated, 'user_site_enabled': data.get('user_site_enabled'), 'isolated_flag': data.get('isolated')}, [] if isolated else ['Selected Python did not demonstrate an isolated managed virtual environment.'])
    if feature_id == 'f020':
        py = _command_for(ctx, 'python')[0]
        r = _curated(ctx, 'uv', ['--no-config', 'pip', 'check', '--python', py])
        return _result('Selected environment dependency consistency inspected.', r, [] if r['ok'] else ['Dependency consistency could not be confirmed; no packages were changed.'])
    if feature_id == 'f021':
        results = {name: _curated(ctx, name, ['--version']) for name in ('winget', 'uv', 'git', 'gh')}
        return _result('Curated package manager startup checked.', results,
                       ['One or more package managers are unavailable or failed startup.'] if any(not x['ok'] for x in results.values()) else [])
    if feature_id == 'f022':
        r = _curated(ctx, 'code-insiders', ['--list-extensions', '--show-versions'])
        wanted = ('openai.chatgpt', 'ms-python.python', 'ms-toolsai.jupyter')
        found = {name: [x.strip() for x in r['output'].splitlines() if x.lower().startswith(name + '@')] for name in wanted}
        return _result('Insiders default-profile extension readiness inspected.', {'query_succeeded': r['ok'], 'extensions': found},
                       ['Editor query failed or a curated extension is missing. Other profile membership and sign-in were not exercised.'] if not r['ok'] or any(not x for x in found.values()) else [])
    if feature_id == 'f023':
        catalog = ctx.fetch_json('https://nodejs.org/download/nightly/index.json')
        if not isinstance(catalog, list):
            raise ValueError('Official Node catalog has an invalid shape.')
        arch = architecture()
        versions = [x['version'] for x in catalog if isinstance(x, dict) and isinstance(x.get('version'), str) and SEMVER.fullmatch(x['version']) and 'nightly' in x['version'] and f'win-{arch}-zip' in x.get('files', [])]
        if not versions:
            raise ValueError('No matching public Node nightly archive was observed.')
        newest = max(versions, key=semver_key); selected = tools.get('node', {}).get('version')
        return _result('Published official Node nightly catalog compared.', {'architecture': arch, 'newest_published': newest, 'selected': selected, 'current': selected == newest}, [] if selected == newest else ['A different published Node nightly is available; this check did not install it.'])
    if feature_id == 'f024':
        catalog = ctx.fetch_json('https://registry.npmjs.org/npm')
        if not isinstance(catalog, dict):
            raise ValueError('Official npm catalog has an invalid shape.')
        newest = choose_npm(catalog); selected = tools.get('npm', {}).get('version')
        metadata = catalog.get('versions', {}).get(newest, {})
        engines = metadata.get('engines', {}) if isinstance(metadata, dict) else {}
        return _result('Published npm catalog compared.', {'newest_supported_package': newest, 'selected': selected, 'node_engine_range': engines.get('node'), 'current': selected == newest}, [] if selected == newest else ['A different supported npm package is published; host compatibility must be checked before installation.'])
    if feature_id == 'f025':
        catalog = ctx.fetch_json('https://builds.dotnet.microsoft.com/dotnet/release-metadata/releases-index.json')
        if not isinstance(catalog, dict):
            raise ValueError('Official .NET catalog has an invalid shape.')
        channel = choose_dotnet_channel(catalog)
        record = next(x for x in catalog['releases-index'] if x.get('channel-version') == channel)
        return _result('Official development .NET channel observed.', {'channel': channel, 'catalog_sdk': record.get('latest-sdk'), 'support_phase': record.get('support-phase'), 'selected_daily_sdk': tools.get('dotnet', {}).get('version'), 'scope': 'Release metadata does not establish the newest daily build identity.'})
    if feature_id == 'f026':
        javascript = tools.get('javascript')
        if not isinstance(javascript, dict) or not javascript.get('path'):
            raise ValueError('Selected JavaScript workspace is unavailable.')
        base = _managed(ctx, javascript['path']); package = _managed(ctx, base / 'node_modules/playwright')
        if not package.is_dir():
            raise ValueError('Selected workspace has no Playwright package.')
        script = "const p=require(" + json.dumps(str(package)) + ");const f=require('fs');const e=p.chromium.executablePath();console.log(JSON.stringify({browser_executable_present:f.existsSync(e),browser_file:require('path').basename(e)}));"
        data = _json_command(ctx, [*_command_for(ctx, 'node'), '-e', script])
        if not isinstance(data, dict) or not isinstance(data.get('browser_executable_present'), bool):
            raise ValueError('Browser cache query returned malformed evidence.')
        return _result('Matching Playwright browser executable readiness inspected.', data, [] if data['browser_executable_present'] else ['The matched Chromium cache executable is unavailable. Browser launch was not exercised by this diagnostic.'])
    if feature_id == 'f027':
        observations = []
        for host in ('nodejs.org', 'registry.npmjs.org', 'builds.dotnet.microsoft.com'):
            try:
                with socket.create_connection((host, 443), timeout=5) as raw:
                    with ssl.create_default_context().wrap_socket(raw, server_hostname=host) as connection:
                        certificate = connection.getpeercert()
                        observations.append({'host': host, 'certificate_verified': True, 'protocol': connection.version(), 'certificate_expires': certificate.get('notAfter')})
            except (OSError, ssl.SSLError) as exc:
                observations.append({'host': host, 'certificate_verified': False, 'error': str(exc)})
        return _result('Fixed publisher-host certificate-verified TLS probed.', observations,
                       ['One or more publisher TLS connections failed. A TLS connection does not prove a download or sign-in works.'] if any(not x['certificate_verified'] for x in observations) else [])
    if feature_id == 'f028':
        names = ('OPENAI_API_KEY', 'GH_TOKEN', 'GITHUB_TOKEN', 'CODEX_HOME', 'HTTP_PROXY', 'HTTPS_PROXY', 'NO_PROXY', 'NODE_EXTRA_CA_CERTS', 'SSL_CERT_FILE', 'UV_PYTHON_INSTALL_DIR')
        return _result('Curated environment variable names inspected; values were not read or exported.', {name: name in os.environ for name in names})
    if feature_id == 'f029':
        report = ctx.latest_report()
        migrations = report.get('migrations', {}) if isinstance(report, dict) else {}
        files = migrations.get('editor_files', {}) if isinstance(migrations, dict) else {}
        extensions = migrations.get('editor_extensions', {}) if isinstance(migrations, dict) else {}
        if not isinstance(files, dict) or not isinstance(extensions, dict):
            raise ValueError('Migration report has an invalid shape.')
        counts = {}
        for key in ('copied', 'conflicts', 'skipped'):
            values = files.get(key, [])
            if not isinstance(values, list):
                raise ValueError('Migration counts have an invalid shape.')
            counts[key] = len(values)
        failed = extensions.get('failed', [])
        if not isinstance(failed, list):
            raise ValueError('Extension migration count has an invalid shape.')
        counts.update(extension_failures=len(failed), migration_record_present=bool(files or extensions))
        return _result('Latest preserved migration observations summarized.', counts,
                       ['Retained configuration conflicts or extension failures require review.'] if counts['conflicts'] or counts['extension_failures'] else ([] if counts['migration_record_present'] else ['No editor migration observation is present in the latest report.']))
    if feature_id == 'f030':
        snap = ctx.snapshot()
        if not isinstance(snap, dict) or not all(isinstance(snap.get(k), bool) for k in ('started', 'finished', 'cancel_requested')):
            raise ValueError('Dashboard snapshot has an invalid shape.')
        session = _managed(ctx, Path(ctx.root) / 'local-session.json')
        lock = _managed(ctx, Path(ctx.root) / 'workbench.lock')
        data = {k: snap[k] for k in ('started', 'finished', 'cancel_requested')}
        data.update(session_file_present=session.is_file(), lock_file_present=lock.is_file(), stale_lock_assumed=False,
                    note='Lock-file presence does not indicate a held OS lock. Session capabilities were not read or probed.')
        return _result('Dashboard lifecycle and session-file hygiene inspected.', data,
                       ['A cancellation was requested while an installation run is unfinished.'] if snap['cancel_requested'] and snap['started'] and not snap['finished'] else [])
    raise ValueError('Unknown diagnostic feature.')


def run(feature_id, ctx, payload):
    """Execute a named diagnostic; failures remain explicit, redacted observations."""
    if not isinstance(feature_id, str) or feature_id not in _IDS:
        raise ValueError('Unknown diagnostic feature.')
    if not isinstance(payload, dict) or set(payload) - {'run_id'}:
        raise ValueError('Diagnostics accept only an optional completed report selection.')
    if 'run_id' in payload and (not isinstance(payload['run_id'], str) or not re.fullmatch(r'\d{8}-\d{6}-[a-f0-9]{6}', payload['run_id'])):
        raise ValueError('Completed report identity is malformed.')
    if getattr(ctx, 'simulate', False):
        return _result('SIMULATED: diagnostic was not executed.', {'executed': False},
                       ['Simulation does not establish machine, network, runtime or report health.'])
    try:
        return _diagnose(feature_id, ctx)
    except (OSError, ValueError, KeyError, TypeError, AttributeError, RuntimeError) as exc:
        return _result('Diagnostic unavailable; no change was made.', {'available': False, 'error': _error_text(exc)},
                       ['The requested observation could not be verified. Review the reported error.'])
