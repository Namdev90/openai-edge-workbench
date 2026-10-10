"""OpenAI Edge Workbench: explicit, inspectable Windows maintenance operations.

No account creation, blanket uninstall, arbitrary remote commands or credential export.
Standard library only. Workload dependencies live in Workbench-owned environments.
"""
from __future__ import annotations

import base64
import collections
import contextlib
import dataclasses
import datetime as dt
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import platform
import queue
import re
import shutil
import socket
import stat
import subprocess
import sys
import threading
import time
import tomllib
import urllib.error
import urllib.parse
import urllib.request
import uuid
import zipfile

VERSION = '2.0.4-preview.1'
SCHEMA = 'openai-edge-workbench/2'
ROOT_NAME = 'OpenAI-Edge-Workbench'
DOCS_MCP = 'https://developers.openai.com/mcp'
TRUSTED_HOSTS = frozenset({
    'nodejs.org', 'registry.npmjs.org', 'api.github.com', 'github.com',
    'release-assets.githubusercontent.com', 'objects.githubusercontent.com',
    'pypi.org', 'files.pythonhosted.org', 'builds.dotnet.microsoft.com', 'dl.google.com',
    'dotnetcli.azureedge.net', 'dot.net', 'aka.ms', 'learn.chatgpt.com',
})
ANSI = re.compile(r'\x1b\[[0-?]*[ -/]*[@-~]')
SEMVER = re.compile(r'^(?:v|rust-v)?(\d+)\.(\d+)\.(\d+)(?:-([0-9A-Za-z.-]+))?(?:\+[0-9A-Za-z.-]+)?$')
PYVER = re.compile(r'^(\d+)\.(\d+)\.(\d+)(?:(a|b|rc)(\d+))?$')
PRE_CHANNELS = {'alpha','beta','rc','pre','preview','next','canary','nightly','dev','experimental','insider','insiders'}
PYTHON_PACKS = {
    'core': ('openai', 'openai-agents'),
    'documents': ('python-docx','openpyxl','python-pptx','reportlab','pypdf','pymupdf','pillow','pandas','numpy','matplotlib','plotly','duckdb','jupyterlab','nbconvert'),
    'science': ('biopython','scipy','sympy','scikit-learn'),
}
PYTHON_IMPORTS = dict(zip(
    sum(PYTHON_PACKS.values(), ()),
    ('openai','agents','docx','openpyxl','pptx','reportlab','pypdf','pymupdf','PIL','pandas','numpy','matplotlib','plotly','duckdb','jupyterlab','nbconvert','Bio','scipy','sympy','sklearn'),
))


def utc() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds')


def semver_key(text: str) -> tuple:
    m = SEMVER.fullmatch(text)
    if not m:
        raise ValueError(f'Not a supported semantic version: {text[:80]}')
    pre = m[4]
    parts = tuple((0, int(x)) if x.isdecimal() else (1, x.lower()) for x in (pre or '').split('.') if x)
    return (int(m[1]), int(m[2]), int(m[3]), 1 if pre is None else 0, parts)


def choose_npm(meta: dict) -> str:
    candidates = []
    for v, info in meta.get('versions', {}).items():
        m = SEMVER.fullmatch(v)
        if not m or info.get('deprecated'):
            continue
        if m[4] and re.split(r'[.-]', m[4])[0].lower() not in PRE_CHANNELS:
            # Platform-specific npm wrapper versions are not alternative channels.
            continue
        if m[4] and set(re.split(r'[.-]', m[4].lower())) & {'linux','darwin','windows','win32','win','x64','x86','arm64','aarch64','musl'}:
            continue
        candidates.append(v)
    if not candidates:
        raise ValueError('No supported public package version was found; no invented tag or fallback used.')
    return max(candidates, key=semver_key)


def choose_dotnet_channel(index:dict) -> str:
    channels=[x for x in index.get('releases-index',[]) if x.get('support-phase') in ('preview','go-live') and re.fullmatch(r'\d+\.\d+',str(x.get('channel-version',''))) and SEMVER.fullmatch(str(x.get('latest-sdk',''))) and SEMVER.fullmatch(x['latest-sdk'])[4] is not None]
    if not channels:raise OperationError('No advertised .NET preview/RC channel found. No stable SDK substituted.')
    return max(channels,key=lambda x:tuple(map(int,x['channel-version'].split('.'))))['channel-version']


def dotnet_sdk_version(output:str,channel:str) -> str:
    versions=[line.strip() for line in output.splitlines() if SEMVER.fullmatch(line.strip())]
    if len(versions)!=1 or not versions[0].startswith(channel+'.') or SEMVER.fullmatch(versions[0])[4] is None:
        raise OperationError('Exact selected-channel .NET development SDK execution was not verified; previous SDK remains selected.')
    return versions[0]


def python_key(text: str) -> tuple:
    m = PYVER.fullmatch(text)
    if not m:
        raise ValueError('Unrecognized CPython release version')
    return (int(m[1]), int(m[2]), int(m[3]), {'a':0,'b':1,'rc':2,None:3}[m[4]], int(m[5] or 0))


def choose_python(data: list[dict], arch: str) -> dict:
    cpu = 'aarch64' if arch == 'arm64' else 'x86_64'
    candidates = []
    for item in data:
        key = str(item.get('key', ''))
        v = str(item.get('version', ''))
        if key.startswith('cpython-') and f'-windows-{cpu}-' in key and '+' not in key and PYVER.fullmatch(v):
            candidates.append(item)
    if not candidates:
        raise ValueError('No normal CPython build for this Windows architecture in the uv catalog.')
    return max(candidates, key=lambda i: python_key(str(i['version'])))


def compatible_python_candidates(data: list[dict], arch: str) -> list[dict]:
    """Latest normal release in each minor; no superseded previews or patch rollback."""
    cpu = 'aarch64' if arch == 'arm64' else 'x86_64'
    latest = {}
    for item in data:
        key = str(item.get('key', '')); version = str(item.get('version', ''))
        if not (key.startswith('cpython-') and f'-windows-{cpu}-' in key and '+' not in key and PYVER.fullmatch(version)):
            continue
        parsed = python_key(version)
        if parsed[:2] < (3, 11):
            continue
        minor = parsed[:2]
        if minor not in latest or parsed > python_key(str(latest[minor]['version'])):
            latest[minor] = item
    if not latest:
        raise OperationError('No normal CPython 3.11+ release for this Windows architecture in the uv download catalog.')
    return sorted(latest.values(), key=lambda item: python_key(str(item['version'])), reverse=True)


def selected_python_packages(options: dict) -> list[str]:
    packages = list(PYTHON_PACKS['core'])
    if options.get('toolkit'): packages.extend(PYTHON_PACKS['documents'])
    if options.get('science'): packages.extend(PYTHON_PACKS['science'])
    return packages


def python_resolution_incompatible(result: CommandResult) -> bool:
    """An actual resolver proof can reject a target; transport/other errors cannot."""
    out = ANSI.sub('', result.out)
    transport = r'(?i)(failed to (?:fetch|download|connect)|request failed|certificate|tls|connection (?:reset|refused)|timed? ?out|network is unreachable|\b(?:401|403|429|5\d\d)\b)'
    return (result.code == 1 and not result.timeout
            and re.search(r'(?i)no solution found when resolving dependencies', out) is not None
            and re.search(r'(?i)requirements are unsatisfiable', out) is not None
            and re.search(transport, out) is None)


def version_matches(actual: str, expected: str) -> bool:
    return bool(expected and re.search(r'(?<![\w.])'+re.escape(expected)+r'(?![\w.+-])', actual))


def redact(text: object) -> str:
    s = ANSI.sub('', str(text))
    # Report creation never reads tokens from auth files; this is defense in depth.
    for key, value in os.environ.items():
        if len(value) >= 8 and re.search(r'(TOKEN|SECRET|PASSWORD|API_KEY)$', key, re.I):
            s = s.replace(value, '[REDACTED]')
    s = re.sub(r'(?i)\b(?:sk-(?:proj-|svcacct-)?[A-Za-z0-9_-]{8,}|gh[pousr]_[A-Za-z0-9_]{8,}|github_pat_[A-Za-z0-9_]+|xox[baprs]-[A-Za-z0-9-]+)\b', '[REDACTED]', s)
    s = re.sub(r'(?i)(\bbearer\s+)\S+', r'\1[REDACTED]', s)
    s = re.sub(r'(?i)([\"\']?(?:access_token|refresh_token|id_token|api_key|password|client_secret|authorization)[\"\']?\s*[:=]\s*)[^\r\n,}]+', r'\1[REDACTED]', s)
    s = re.sub(r'https?://[^\s<>\"\']+', lambda m: redact_url(m[0]), s)
    s = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b', '[EMAIL]', s)
    for p in sorted({str(Path.home()), os.environ.get('USERPROFILE',''), os.environ.get('LOCALAPPDATA','')}, key=len, reverse=True):
        if p and len(p) > 3:
            s = re.sub(re.escape(p), lambda _: '[USER]', s, flags=re.I)
    s = re.sub(r'(?i)[A-Z]:\\Users\\[^\\\s"\']+', r'C:\\Users\\[USER]', s)
    return s


def redact_url(url: str) -> str:
    try:
        p = urllib.parse.urlsplit(url)
        host = p.hostname or ''
        if p.port:
            host += ':'+str(p.port)
        return urllib.parse.urlunsplit((p.scheme,host,p.path,'[REDACTED]' if p.query else '', '[REDACTED]' if p.fragment else ''))
    except ValueError:
        return '[URL REDACTED]'


def trusted_url(url: str) -> bool:
    try:
        p = urllib.parse.urlsplit(url)
        return p.scheme == 'https' and p.hostname in TRUSTED_HOSTS and not p.username and not p.password and p.port in (None,443)
    except ValueError:
        return False


class TrustedRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if not trusted_url(newurl):
            raise ValueError('Refusing a download redirect to an unlisted origin.')
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def is_reparse(path: Path) -> bool:
    try:
        return path.is_symlink() or bool(getattr(path.lstat(), 'st_file_attributes', 0) & getattr(stat, 'FILE_ATTRIBUTE_REPARSE_POINT', 1024))
    except FileNotFoundError:
        return False


def assert_regular_path(path: Path) -> None:
    path = Path(os.path.abspath(path))
    if any(is_reparse(p) for p in (path, *path.parents)):
        raise ValueError('Refusing a symlink or junction in a managed path.')


def contains_reparse(path: Path) -> bool:
    for root, dirs, files in os.walk(path, followlinks=False):
        if any(is_reparse(Path(root, name)) for name in (*dirs, *files)):
            return True
    return False


def safe_extract(archive: Path, target: Path) -> None:
    assert_regular_path(target)
    target = target.resolve()
    target.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive) as z:
        entries = z.infolist()
        if sum(i.file_size for i in entries) > 8*1024**3 or len(entries) > 100000:
            raise ValueError('Archive exceeds extraction budget.')
        for item in entries:
            raw = item.filename.replace('\\','/')
            rel = PurePosixPath(raw)
            mode = item.external_attr >> 16
            if rel.is_absolute() or '..' in rel.parts or ':' in raw or stat.S_ISLNK(mode):
                raise ValueError('Unsafe path or symlink in download archive.')
            dest = target.joinpath(*rel.parts)
            if not dest.resolve().is_relative_to(target):
                raise ValueError('Archive escapes its destination.')
        z.extractall(target)


def merge_missing(source: Path, target: Path) -> dict:
    result = {'copied': [], 'identical': [], 'conflicts': [], 'skipped': []}
    assert_regular_path(source); assert_regular_path(target)
    if not source.is_dir():
        return result
    target.mkdir(parents=True, exist_ok=True)
    excluded = {'globalstorage','workspacestorage','history','sync','auth.json','.git'}
    for root, dirs, files in os.walk(source, followlinks=False):
        dirs[:] = [d for d in dirs if d.lower() not in excluded and not Path(root,d).is_symlink() and not getattr(Path(root,d),'is_junction',lambda:False)()]
        for name in files:
            src = Path(root,name)
            rel = src.relative_to(source)
            if name.lower() in excluded or src.is_symlink():
                result['skipped'].append(rel.as_posix()); continue
            # Copy configuration text/snippets only, never browser state or databases.
            if src.suffix.lower() not in ('.json','.jsonc','.code-snippets','.md'):
                result['skipped'].append(rel.as_posix()); continue
            dest = target/rel
            if not dest.resolve().is_relative_to(target.resolve()):
                result['skipped'].append(rel.as_posix()); continue
            if dest.exists():
                same = not dest.is_symlink() and src.read_bytes() == dest.read_bytes()
                result['identical' if same else 'conflicts'].append(rel.as_posix()); continue
            if not dest.resolve().is_relative_to(target.resolve()):
                result['skipped'].append(rel.as_posix()); continue
            dest.parent.mkdir(parents=True,exist_ok=True)
            shutil.copy2(src,dest); result['copied'].append(rel.as_posix())
    return result


def summarize_codex_doctor(output: str) -> dict:
    """Keep advertised structured warnings visible without interpreting them as repairs."""
    try:
        data=json.loads(output)
        if not isinstance(data,dict) or not isinstance(data.get('checks'),dict):raise ValueError('Unsupported doctor schema')
        rows=[];counts=collections.Counter()
        for key,row in data['checks'].items():
            if not isinstance(row,dict) or not isinstance(row.get('status'),str):raise ValueError('Malformed doctor check')
            status=row['status'];counts[status]+=1
            if status!='ok':
                safe={name:row[name] for name in ('category','summary','details','remediation','issues') if name in row}
                def protect(value):
                    if isinstance(value,str):return redact(value)
                    if isinstance(value,dict):return {name:protect(item) for name,item in value.items()}
                    if isinstance(value,list):return [protect(item) for item in value]
                    return value
                safe=protect(safe)
                rows.append({'id':str(key),'status':status,**safe})
        return {'overall_status':data.get('overallStatus','unknown'),'counts':dict(counts),'non_ok_checks':rows,
                'warning_count':counts['warning'],'failure_count':counts['failure']+counts['failed']+counts['error'],
                'scope':'Doctor observations only; no security exclusions, credential changes or history repairs applied.'}
    except (ValueError,TypeError) as exc:
        raise OperationError('Advertised Codex doctor JSON was not valid; diagnostics remain unverified.') from exc


def default_options() -> dict:
    return {'toolkit':True, 'browser':True, 'science':True, 'dotnet':False,
            'migrate':True, 'cleanup':True, 'live':True, 'docs_mcp':True}


def build_plan(options: dict) -> list[dict]:
    plan = []
    def add(key, name, kind='special', **kw):
        plan.append({'id':key,'name':name,'kind':kind,**kw})
    def wing(key,name,package,channel='Latest in WinGet catalog'):
        add(key,name,'winget',package=package,source='winget',channel=channel)
    add('inventory','Inventory and configuration backup')
    add('chatgpt','Current ChatGPT desktop app','winget',package='9PLM9XGG6VKS',source='msstore',channel='Latest publicly offered Store build')
    wing('git','Git','Git.Git')
    wing('gh','GitHub CLI','GitHub.cli')
    wing('uv','uv package manager','astral-sh.uv')
    wing('powershell','PowerShell Preview','Microsoft.PowerShell.Preview','Preview')
    wing('editor','VS Code Insiders','Microsoft.VisualStudioCode.Insiders','Insiders')
    wing('terminal','Windows Terminal Preview','Microsoft.WindowsTerminal.Preview','Preview')
    wing('webview','WebView2 runtime','Microsoft.EdgeWebView2Runtime','Latest public Evergreen runtime')
    add('node','Node.js official nightly + compatible npm')
    add('codex','Codex CLI - newest public npm build')
    add('openai-cli','Official OpenAI API CLI')
    add('python','Newest compatible CPython for selected packs')
    add('javascript','OpenAI JavaScript / Agents / Codex SDKs')
    add('python-packages','OpenAI Python / Agents SDKs')
    add('extensions','Codex, Python and Jupyter preview extensions')
    if options.get('toolkit'):
        wing('archive','7-Zip','7zip.7zip')
        wing('pandoc','Pandoc document converter','JohnMacFarlane.Pandoc')
        wing('ffmpeg','FFmpeg Windows build','Gyan.FFmpeg')
        wing('powertoys','PowerToys','Microsoft.PowerToys')
        add('documents','Document, PDF, spreadsheet and data libraries')
    if options.get('browser'):
        wing('canary','Chrome Canary','Google.Chrome.Canary','Canary')
        add('playwright','Playwright development build + Chromium')
    if options.get('science'):
        add('science','Scientific Python and Biopython')
    if options.get('dotnet'):
        add('dotnet','Newest advertised .NET preview channel - daily SDK')
    if options.get('migrate'):
        add('migrate','Migrate non-conflicting editor settings and extensions')
    if options.get('docs_mcp'):
        add('docs-mcp','Connect official read-only OpenAI documentation MCP')
    add('verify','Version, routing, authentication and functional checks')
    if options.get('live'):
        add('live','One read-only Codex model round trip (uses quota)')
    if options.get('cleanup'):
        add('cleanup','Clean old Workbench-owned generations')
    add('report','Write final diagnostic report and tool shortcuts')
    return plan


@dataclasses.dataclass
class CommandResult:
    code: int
    out: str
    timeout: bool = False


class OperationError(RuntimeError):
    pass


class StopRun(RuntimeError):
    pass


def atomic_json(path: Path, obj: object) -> None:
    path.parent.mkdir(parents=True,exist_ok=True)
    tmp = path.with_name(path.name+'.tmp')
    tmp.write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf-8')
    os.replace(tmp,path)


def atomic_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_name(path.name+'.tmp')
    tmp.write_text(text,encoding='utf-8')
    os.replace(tmp,path)


def ps_literal(value: object) -> str:
    return "'"+str(value).replace("'","''")+"'"


def architecture() -> str:
    arch = os.environ.get('PROCESSOR_ARCHITEW6432',os.environ.get('PROCESSOR_ARCHITECTURE',platform.machine())).lower()
    if arch in ('arm64','aarch64'): return 'arm64'
    if arch in ('amd64','x86_64'): return 'x64'
    raise OperationError('Only 64-bit Windows x64 and ARM64 are supported.')


class Workbench:
    def __init__(self, root: Path, *, simulate: bool=False):
        assert_regular_path(root)
        self.root = root.resolve()
        self.root.mkdir(parents=True,exist_ok=True)
        self.simulate = simulate
        self.lock = threading.RLock()
        self.cancel = threading.Event()
        self.started = False
        self.finished = False
        self.current = ''
        self.log_seq = 0
        self.logs = collections.deque(maxlen=1200)
        self.results: list[dict] = []
        self.options = default_options()
        self.plan: list[dict] = []
        self.active = {}
        self.python_candidate = None; self.python_candidate_failed = False
        self.js_candidate = None; self.js_candidate_failed = False
        self.state_file = self.root/'state.json'
        self.state = {'schema':SCHEMA,'tools':{}}
        if self.state_file.exists():
            try:
                state=json.loads(self.state_file.read_text(encoding='utf-8'))
                if state.get('schema') == SCHEMA: self.state=state
            except (OSError, ValueError): pass
        self.active = dict(self.state.get('tools',{}))
        self.run_id = dt.datetime.now().strftime('%Y%m%d-%H%M%S')+'-'+uuid.uuid4().hex[:6]
        self.run_dir = self.root/'reports'/self.run_id
        self.run_dir.mkdir(parents=True,exist_ok=True)
        self.report = {'schema':SCHEMA,'workbench_version':VERSION,'started_utc':utc(),
                       'platform':platform.platform(),'simulated':simulate,'run_id':self.run_id,
                       'policy':'Newest published supported development build. Python is preflight-selected for all requested wheels; no silent stable retry after an installation fails.',
                       'coverage':{},'checks':{},'migrations':{},'limitations':[
                           'Desktop UI, same-account identity, cloud OAuth and individual plugin actions require signed-in checks.',
                           'A successful installer or TCP/HTTP probe is not an end-to-end feature test.',
                           'WinGet apps are latest in the selected catalog/channel, not a proof of every upstream unpublished build.',
                           'No project dependency, credential, cookie or native Work/proxy configuration is replaced.',
                           'Only this catalog is managed. New products and private beta access require a future catalog update.',
                       ]}
        provenance=self.root/'Setup-Status.json'
        if provenance.is_file():
            with contextlib.suppress(OSError,ValueError):
                status=json.loads(provenance.read_text(encoding='utf-8-sig'))
                self.report['code_update']={k:redact(status.get(k,'')) for k in ('repository','commit','state','utc','error')}
        self.env = dict(os.environ)
        self.env.update({'PYTHONUTF8':'1','PYTHONIOENCODING':'utf-8','NO_COLOR':'1','CI':'1',
                         'UV_NO_CONFIG':'1','UV_PYTHON_INSTALL_DIR':str(self.root/'runtimes'/'uv-python')})
        self.current_result: dict | None = None

    def log(self, message: str, level: str='info') -> None:
        message = redact(message).replace('\x00','')[:10000]
        with self.lock:
            self.log_seq += 1
            event = {'seq':self.log_seq,'time':utc(),'level':level,'message':message}
            self.logs.append(event)
            with (self.run_dir/'Activity-redacted.jsonl').open('a',encoding='utf-8') as f:
                f.write(json.dumps(event,ensure_ascii=False)+'\n')

    def snapshot(self, after: int=0) -> dict:
        with self.lock:
            return {'version':VERSION,'run_id':self.run_id,'started':self.started,'finished':self.finished,
                    'current':self.current,'cancel_requested':self.cancel.is_set(),
                    'plan':self.plan or build_plan(self.options),'options':dict(self.options),
                    'results':json.loads(json.dumps(self.results)),
                    'logs':[x for x in self.logs if x['seq']>after],
                    'completed':len([x for x in self.results if x['status']!='RUNNING']),
                    'total':len(self.plan) if self.plan else len(build_plan(self.options)),
                    'report_ready':(self.run_dir/'Paste-Into-ChatGPT.txt').exists(),
                    'terminal_ready':(self.root/'Open-Edge-Terminal.cmd').is_file(),
                    'report_location':str(self.run_dir)}

    def run_command(self, argv: list[str|Path], *, timeout: int=900, quiet: bool=False,
                    cwd: Path|None=None, env: dict|None=None, label: str='') -> CommandResult:
        args=[str(x) for x in argv]
        if not args: raise ValueError('Empty command')
        if os.name=='nt' and args[0].lower().endswith(('.cmd','.bat')):
            body='& '+' '.join(ps_literal(x) for x in args)+'; exit $LASTEXITCODE'
            args=self.ps_args(body)
        self.log('RUN: '+(label or ' '.join(args)))
        flags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0
        try:
            proc=subprocess.Popen(args,cwd=str(cwd or self.root),env=env or self.env,
                                  stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,
                                  creationflags=flags)
        except (OSError,ValueError) as exc:
            if self.current_result is not None:
                self.current_result.setdefault('commands',[]).append({'label':label or redact(' '.join(args)), 'exit_code':-1, 'timed_out':False, 'tail':redact(str(exc))})
            return CommandResult(-1,str(exc))
        q: queue.Queue = queue.Queue()
        def read_output():
            try:
                for line in iter(proc.stdout.readline,b''):
                    q.put(line.decode('utf-8',errors='replace').rstrip())
            finally:
                proc.stdout.close()
                q.put(None)
        threading.Thread(target=read_output,daemon=True).start()
        started=time.monotonic(); lines=[]; length=0; ended=False; timed_out=False
        while not ended or proc.poll() is None:
            try:
                line=q.get(timeout=.2)
                if line is None: ended=True
                else:
                    length+=len(line)
                    if length<4*1024*1024:lines.append(line)
                    if not quiet:self.log(line)
            except queue.Empty:pass
            if time.monotonic()-started>timeout:
                timed_out=True
                # Stop further mutations. Killing the manager does not prove its installer children stopped.
                self.cancel.set()
                with contextlib.suppress(OSError):proc.kill()
                self.log('TIMEOUT. Remaining operations stopped. A child installer may still be active; inspect it before rerunning.','error')
                break
        with contextlib.suppress(subprocess.TimeoutExpired):proc.wait(timeout=3)
        result=CommandResult(proc.returncode if proc.returncode is not None else -2,'\n'.join(lines),timed_out)
        if self.current_result is not None:
            self.current_result.setdefault('commands',[]).append({'label':label or redact(' '.join(str(x) for x in argv)),
                    'exit_code':result.code,'timed_out':timed_out,
                    'tail':redact(result.out[-2200:]) if result.code!=0 else ''})
        return result

    @staticmethod
    def ps_args(body: str) -> list[str]:
        exe=str(Path(os.environ.get('SystemRoot',r'C:\Windows'))/'System32'/'WindowsPowerShell'/'v1.0'/'powershell.exe')
        # Nested Windows PowerShell can inherit PS7 module search paths. Load the
        # matching native modules and return text, not CLIXML, to JSON consumers.
        wrapped=("$ErrorActionPreference='Stop'; $ProgressPreference='SilentlyContinue'; "
                 "[Console]::OutputEncoding=[System.Text.UTF8Encoding]::new($false); try { "
                 "Import-Module ([IO.Path]::Combine($PSHOME,'Modules\\Microsoft.PowerShell.Utility\\Microsoft.PowerShell.Utility.psd1')) -ErrorAction Stop; "
                 "Import-Module ([IO.Path]::Combine($PSHOME,'Modules\\Microsoft.PowerShell.Security\\Microsoft.PowerShell.Security.psd1')) -ErrorAction Stop; "
                 "Import-Module ([IO.Path]::Combine($PSHOME,'Modules\\Microsoft.PowerShell.Management\\Microsoft.PowerShell.Management.psd1')) -ErrorAction Stop; "
                 +body+" } catch { [Console]::Error.WriteLine($_.Exception.Message); exit 1 }")
        return [exe,'-NoLogo','-NoProfile','-NonInteractive','-OutputFormat','Text','-ExecutionPolicy','Bypass','-EncodedCommand',base64.b64encode(wrapped.encode('utf-16le')).decode()]

    def ps(self, body: str, *, timeout=120, label='Windows configuration query') -> CommandResult:
        return self.run_command(self.ps_args(body),timeout=timeout,quiet=True,label=label)

    def ps_json(self, body: str, *, label: str):
        result=self.require(self.ps(body,label=label),label)
        try:
            return json.loads(result.out.lstrip('\ufeff'))
        except (ValueError,TypeError) as exc:
            raise OperationError(label+' did not return valid JSON; no dependent configuration was changed.') from exc

    def require(self,result:CommandResult,what:str) -> CommandResult:
        if result.timeout: raise StopRun(what+' timed out; remaining operations stopped.')
        if result.code!=0:raise OperationError(what+f' failed (exit {result.code}). '+redact(result.out[-1400:]))
        return result

    def find(self, name: str) -> str|None:
        found=shutil.which(name,path=self.env.get('PATH',''))
        if found:return found
        local=Path(os.environ.get('LOCALAPPDATA',str(Path.home())))
        pf=Path(os.environ.get('ProgramFiles',r'C:\Program Files'))
        candidates={
          'uv.exe':[Path.home()/'.local/bin/uv.exe',local/'Microsoft/WinGet/Links/uv.exe'],
          'git.exe':[pf/'Git/cmd/git.exe',local/'Programs/Git/cmd/git.exe'],
          'gh.exe':[pf/'GitHub CLI/gh.exe'],
          'code-insiders.cmd':[local/'Programs/Microsoft VS Code Insiders/bin/code-insiders.cmd',pf/'Microsoft VS Code Insiders/bin/code-insiders.cmd'],
          'code.cmd':[local/'Programs/Microsoft VS Code/bin/code.cmd',pf/'Microsoft VS Code/bin/code.cmd'],
          'pwsh-preview.exe':[pf/'PowerShell/7-preview/pwsh.exe'],
          'winget.exe':[local/'Microsoft/WindowsApps/winget.exe'],
        }.get(name,[])
        return next((str(x) for x in candidates if x.is_file()),None)

    def refresh_path(self):
        if os.name!='nt': return
        r=self.ps("[Environment]::GetEnvironmentVariable('Path','Machine')+';'+[Environment]::GetEnvironmentVariable('Path','User')",label='Refresh current process PATH')
        if r.code==0:
            paths=[str(self.root/'bin'),r.out.strip()]
            if self.active.get('node'):paths.insert(0,str(Path(self.active['node']['command'][0]).parent))
            self.env['PATH']=';'.join(paths)

    def fetch(self, url: str, destination: Path|None=None, expected_sha256: str|None=None, *, max_bytes:int=32*1024**2):
        if not trusted_url(url):raise OperationError('Untrusted download URL: '+redact(url))
        req=urllib.request.Request(url,headers={'User-Agent':f'OpenAI-Edge-Workbench/{VERSION}','Accept':'application/json' if destination is None else '*/*'})
        opener=urllib.request.build_opener(TrustedRedirect())
        last=None
        for attempt in range(3):
            try:
                with opener.open(req,timeout=45) as resp:
                    if not trusted_url(resp.url):raise OperationError('Download changed to an unlisted origin.')
                    chunks=[]; size=0; digest=hashlib.sha256(); written=None
                    tmp=destination.with_suffix(destination.suffix+'.partial') if destination else None
                    if tmp:tmp.parent.mkdir(parents=True,exist_ok=True);written=tmp.open('wb')
                    try:
                        while True:
                            data=resp.read(256*1024)
                            if not data:break
                            size+=len(data)
                            if size>max_bytes:raise OperationError('Download exceeded its size limit.')
                            digest.update(data)
                            if written:written.write(data)
                            else:chunks.append(data)
                    finally:
                        if written:written.close()
                    if expected_sha256 and digest.hexdigest().lower()!=expected_sha256.lower():
                        if tmp:tmp.unlink(missing_ok=True)
                        raise OperationError('SHA-256 mismatch. The downloaded artifact was not executed.')
                    if tmp:
                        os.replace(tmp,destination)
                        self.log(f'Download complete: {destination.name} ({size//1024:,} KiB), SHA-256 {digest.hexdigest()}')
                        return destination
                    return b''.join(chunks)
            except (urllib.error.HTTPError,urllib.error.URLError,TimeoutError,OSError) as exc:
                last=exc
                if isinstance(exc,urllib.error.HTTPError) and exc.code in (401,403,404):break
                if attempt<2:time.sleep(1+attempt)
        raise OperationError('Download failed: '+redact(str(last)))

    def get_json(self,url):
        return json.loads(self.fetch(url).decode('utf-8'))

    def save_state(self):
        self.state['tools']=self.active;self.state['updated_utc']=utc()
        atomic_json(self.state_file,self.state)

    def activate(self,name:str,version:str,command:list[str|Path],source:str):
        self.active[name]={'version':version,'command':[str(x) for x in command],'source':source}
        self.save_state()
        self.current_result.update({'actual':version,'source':source})

    def start(self,options:dict) -> bool:
        with self.lock:
            if self.started:return False
            unknown=set(options)-set(default_options())
            if unknown or any(type(v) is not bool for v in options.values()):raise ValueError('Invalid option')
            self.options={**default_options(),**options}
            self.started=True;self.plan=build_plan(self.options)
        threading.Thread(target=self.execute,daemon=False).start()
        return True

    def execute(self):
        self.report['options']=self.options
        try:
            if os.name!='nt' and not self.simulate:raise StopRun('This installer requires Windows; no system changes were made.')
            for item in self.plan:
                if self.cancel.is_set():break
                with self.lock:
                    self.current=item['name'];row={**item,'status':'RUNNING','started_utc':utc(),'detail':''}
                    self.results.append(row);self.current_result=row
                self.log('STEP: '+item['name'])
                try:
                    if self.simulate:
                        self.log('SIMULATION ONLY: no installation or network operation.');time.sleep(.015)
                        row['status']='SIMULATED';row['detail']='Demo record, not laptop evidence.'
                    elif item['kind']=='winget':self.install_winget(item)
                    else:getattr(self,'step_'+item['id'].replace('-','_'))()
                    if row['status']=='RUNNING':row['status']='VERIFIED'
                except StopRun as exc:
                    row['status']='STOPPED';row['detail']=redact(str(exc));self.cancel.set()
                    self.log(row['detail'],'error')
                except Exception as exc:
                    if item['id'] in ('python','python-packages','documents','science'):self.python_candidate_failed=True
                    if item['id'] in ('javascript','playwright'):self.js_candidate_failed=True
                    row['status']='FAILED';row['detail']=redact(str(exc))
                    self.log(row['detail'],'error')
                finally:
                    row['finished_utc']=utc();self.write_report(final=False)
            done={x['id'] for x in self.results}
            for item in self.plan:
                if item['id'] not in done:self.results.append({**item,'status':'NOT_RUN','detail':'Run stopped before this step.'})
        except Exception as exc:
            self.report['fatal_error']=redact(str(exc));self.log(str(exc),'error')
        finally:
            with self.lock:
                self.current='Stopped' if self.cancel.is_set() else 'Finished'
                self.report['finished_utc']=utc()
                try:
                    self.write_report(final=True)
                except OSError as exc:
                    self.report['report_error']=redact(str(exc))
                    self.log('Final report could not be saved: '+redact(str(exc)),'error')
                finally:self.finished=True
            if not self.report.get('report_error'):
                self.log('Report ready: Paste-Into-ChatGPT.txt. Review it before sharing.')

    def write_report(self,*,final:bool):
        with self.lock:
            data={**self.report,'final':final,'stopped':self.cancel.is_set(),'results':self.results,
                  'managed_tools':self.active,
                  'totals':dict(collections.Counter(x['status'] for x in self.results)),
                  'recent_activity':list(self.logs)[-30:]}
            # Redaction operates on text for safe display. JSON is serialized separately from recursive redaction.
            def scrub(x):
                if isinstance(x,str):return redact(x)
                if isinstance(x,list):return [scrub(y) for y in x]
                if isinstance(x,dict):return {str(k):scrub(v) for k,v in x.items()}
                return x
            safe_data=scrub(data)
            atomic_json(self.run_dir/'Diagnostic.json',safe_data)
            text='=== BEGIN OPENAI EDGE DIAGNOSTIC ===\n'+json.dumps(safe_data,ensure_ascii=False,indent=2)+'\n=== END OPENAI EDGE DIAGNOSTIC ===\n'
            atomic_text(self.run_dir/'Paste-Into-ChatGPT.txt',text)
            atomic_text(self.root/'LATEST-REPORT.txt',str(self.run_dir/'Paste-Into-ChatGPT.txt'))

    def step_inventory(self):
        self.arch=architecture()
        self.refresh_path()
        self.report['architecture']=self.arch
        self.report['bootstrap_python']=sys.version.split()[0]
        if shutil.disk_usage(self.root).free<4*1024**3:
            raise StopRun('Less than 4 GiB free. Free space before installing the selected toolkit.')
        appx=self.ps("@(Get-AppxPackage | Where-Object {$_.Name -match '^OpenAI\\.'} | Select-Object Name,@{n='Version';e={$_.Version.ToString()}},Status) | ConvertTo-Json -Compress",label='Inventory OpenAI Store packages')
        if appx.code==0:
            with contextlib.suppress(ValueError):self.report['appx_before']=json.loads(appx.out or '[]')
        codex_home=Path(os.environ.get('CODEX_HOME',str(Path.home()/'.codex'))).expanduser()
        self.codex_home=codex_home
        backup=self.root/'private-backups'/self.run_id
        backup.mkdir(parents=True,exist_ok=True)
        copied=[]
        for src,rel in [(codex_home/'config.toml','codex-config.toml'),
                        (codex_home/'AGENTS.md','codex-AGENTS.md')]:
            if src.is_file() and not src.is_symlink():
                shutil.copy2(src,backup/rel);copied.append(rel)
        # Settings may contain secrets: local backups are not included in reports.
        self.report['private_backup_files']=copied
        self.report['checks']['codex_home_shared']={'path':str(codex_home),'custom_CODEX_HOME':bool(os.environ.get('CODEX_HOME')),
            'note':'Existing native configuration is reused. WSL homes are not rewritten or linked automatically.'}
        detected={}
        for name in ('codex','openai','node','python','rtk','headroom','uv','git','gh','code','code-insiders','antigravity'):
            r=self.run_command(['where.exe',name],quiet=True,timeout=20,label='Locate '+name)
            detected[name]=r.out.splitlines() if r.code==0 else []
        self.report['commands_before']=detected
        self.report['coverage']['existing_helpers']='Headroom, RTK, Caveman, Antigravity, hooks and native Work routing: inspect only; no guessed migration or proxy reset.'
        self.report['coverage']['classic_app']='Classic is not removed automatically: cloud identity and unsynced local data cannot be verified by an installer.'
        self.current_result['detail']='Inventory captured; local configuration backup made without exporting its contents.'

    def install_terminal_preview_local(self, version: str) -> list[dict]:
        """Recover a completed URI timeout using the same signed Preview payload."""
        if not re.fullmatch(r'\d+\.\d+\.\d+\.\d+',version):
            raise OperationError('Terminal Preview local recovery requires a known exact catalog version.')
        release_url='https://api.github.com/repos/microsoft/terminal/releases/tags/v'+version
        release=self.get_json(release_url)
        if release.get('draft') or release.get('tag_name')!='v'+version:
            raise OperationError('The official Terminal release metadata does not match the selected Preview version.')
        name='Microsoft.WindowsTerminalPreview_'+version+'_8wekyb3d8bbwe.msixbundle'
        assets=[asset for asset in release.get('assets',[]) if asset.get('name')==name]
        if len(assets)!=1:raise OperationError('The official release has no unique exact Terminal Preview bundle; no alternative build installed.')
        asset=assets[0]
        url='https://github.com/microsoft/terminal/releases/download/v'+version+'/'+name
        digest=asset.get('digest','')
        if asset.get('browser_download_url')!=url or not isinstance(digest,str) or not re.fullmatch(r'sha256:[0-9a-fA-F]{64}',digest):
            raise OperationError('An exact official Terminal Preview asset URL and published SHA256 digest are required for local recovery.')
        sha=digest.split(':',1)[1].lower()
        download=self.root/'downloads'/name
        assert_regular_path(download)
        self.fetch(url,download,sha,max_bytes=512*1024**2)
        signature=self.ps_json("$s=Get-AuthenticodeSignature -LiteralPath "+ps_literal(download)+"; [pscustomobject]@{status=$s.Status.ToString();subject=if($s.SignerCertificate){$s.SignerCertificate.Subject}else{''}} | ConvertTo-Json -Compress",label='Verify official Terminal Preview bundle Microsoft signature')
        evidence={'reason':'Completed WinGet WININET_E_TIMEOUT (0x80072EE2); retry exact Preview payload as a local file','version':version,'release_metadata':release_url,'asset_url':url,'sha256':sha,'signature':signature}
        self.current_result['local_recovery']=evidence
        subject='CN=Microsoft Corporation, O=Microsoft Corporation, L=Redmond, S=Washington, C=US'
        if not isinstance(signature,dict) or signature.get('status')!='Valid' or signature.get('subject')!=subject:
            raise OperationError('The downloaded Terminal Preview bundle has no verified valid Microsoft Corporation signature; it was not installed.')
        # Recheck the hash immediately before Add-AppxPackage. Windows validates
        # the package signature and framework dependencies normally; no bypass,
        # force-close, or dependency-skipping option is supplied.
        body="Import-Module ([IO.Path]::Combine($PSHOME,'Modules\\Appx\\Appx.psd1')) -ErrorAction Stop; $path="+ps_literal(download)+"; if((Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash -ine "+ps_literal(sha)+") {throw 'Terminal bundle checksum changed; installation not attempted'}; $s=Get-AuthenticodeSignature -LiteralPath $path; if($s.Status.ToString() -ne 'Valid' -or $s.SignerCertificate.Subject -ne "+ps_literal(subject)+") {throw 'Terminal bundle signature changed; installation not attempted'}; Add-AppxPackage -Path $path -ErrorAction Stop; $packages=@(Get-AppxPackage -Name Microsoft.WindowsTerminalPreview | Select-Object Name,@{n='version';e={$_.Version.ToString()}},@{n='status';e={$_.Status.ToString()}}); ConvertTo-Json -InputObject $packages -Compress"
        if self.cancel.is_set():raise StopRun('Stopped before local Terminal Preview installation.')
        registrations=self.ps_json(body,label='Install exact signed local Terminal Preview bundle and verify AppX registration')
        if not isinstance(registrations,list) or not any(isinstance(row,dict) and row.get('Name')=='Microsoft.WindowsTerminalPreview' and row.get('version')==version and row.get('status')=='Ok' for row in registrations):
            raise OperationError('Local Terminal installation returned, but the exact Preview AppX name, version, and healthy status were not verified.')
        evidence['registrations']=registrations
        return registrations

    def canary_registration(self) -> dict:
        # WinGet's Canary manifest historically used ProductCode "Google Chrome",
        # so an ordinary Chrome uninstall entry cannot establish Canary presence.
        body=r"""$arp=@(Get-ChildItem 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall','HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall','HKLM:\Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall' -ErrorAction SilentlyContinue | Get-ItemProperty -ErrorAction SilentlyContinue | Where-Object {$_.DisplayName -eq 'Google Chrome Canary' -or $_.DisplayName -eq 'Google Chrome' -or $_.InstallLocation -match 'Chrome SxS'} | Select-Object DisplayName,DisplayVersion,InstallLocation);
        $target=Join-Path $env:LOCALAPPDATA 'Google\Chrome SxS\Application\chrome.exe';
        $canary=@($target,(Join-Path $env:ProgramFiles 'Google\Chrome SxS\Application\chrome.exe'),(Join-Path ${env:ProgramFiles(x86)} 'Google\Chrome SxS\Application\chrome.exe'));
        $stable=@((Join-Path $env:LOCALAPPDATA 'Google\Chrome\Application\chrome.exe'),(Join-Path $env:ProgramFiles 'Google\Chrome\Application\chrome.exe'),(Join-Path ${env:ProgramFiles(x86)} 'Google\Chrome\Application\chrome.exe'));
        foreach($registration in $arp) {
          if($registration.InstallLocation) {
            $paths=@([IO.Path]::Combine($registration.InstallLocation,'chrome.exe'),[IO.Path]::Combine($registration.InstallLocation,'Application\chrome.exe'))
            if($registration.InstallLocation -match '(?i)(?:^|[\\/])Chrome SxS(?:[\\/]|$)') {$canary+=$paths}
            elseif($registration.DisplayName -eq 'Google Chrome') {$stable+=$paths}
          }
        }
        function Read-ChromeFiles($paths,$inspectSigner) {
          foreach($path in @($paths | Select-Object -Unique)) {
            if([IO.File]::Exists($path)) {
              $version=[Diagnostics.FileVersionInfo]::GetVersionInfo($path); $signature=$null
              if($inspectSigner) {
                $s=Get-AuthenticodeSignature -LiteralPath $path
                $signature=[pscustomobject]@{status=$s.Status.ToString();subject=if($s.SignerCertificate){$s.SignerCertificate.Subject}else{''};simple_name=if($s.SignerCertificate){$s.SignerCertificate.GetNameInfo([Security.Cryptography.X509Certificates.X509NameType]::SimpleName,$false)}else{''}}
              }
              [pscustomobject]@{path=$path;version=$version.ProductVersion;signature=$signature}
            }
          }
        }
        $files=@(Read-ChromeFiles $canary $true); $stableFiles=@(Read-ChromeFiles $stable $false);
        $registered=@($arp | Where-Object {$_.DisplayName -eq 'Google Chrome Canary' -or $_.InstallLocation -match '(?i)(?:^|[\\/])Chrome SxS(?:[\\/]|$)'});
        [pscustomobject]@{target_path=$target;target_scope='user';executables=$files;registrations=$registered;stable_executables=$stableFiles} | ConvertTo-Json -Depth 5 -Compress"""
        result=self.ps_json(body,label='Verify Chrome Canary SxS binary versions and separate Chrome registrations')
        if not isinstance(result,dict) or result.get('target_scope')!='user' or not isinstance(result.get('target_path'),str) or any(not isinstance(result.get(key),list) for key in ('executables','registrations','stable_executables')):
            raise OperationError('Chrome channel inspection returned an unexpected result; no browser update attempted.')
        for key in ('executables','stable_executables'):
            if any(not isinstance(row,dict) or not isinstance(row.get('path'),str) or not re.fullmatch(r'\d+\.\d+\.\d+\.\d+',str(row.get('version',''))) for row in result[key]):
                raise OperationError('Chrome binary inspection returned an ambiguous version; no browser update attempted.')
        if not re.search(r'(?i)[\\/]Google[\\/]Chrome SxS[\\/]Application[\\/]chrome\.exe$',result['target_path']) or any(not re.search(r'(?i)[\\/]Chrome SxS[\\/](?:Application[\\/])?chrome\.exe$',row['path']) for row in result['executables']):
            raise OperationError('Canary evidence did not refer to the expected SxS executable paths; ordinary Chrome was not accepted as Canary.')
        return result

    @staticmethod
    def canary_user_binary(inspection: dict) -> dict|None:
        target=inspection['target_path'].casefold()
        records=[row for row in inspection['executables'] if row['path'].casefold()==target]
        if not records:return None
        if len({row['version'] for row in records})!=1:raise OperationError('Per-user Canary binary version was ambiguous; installation not attempted.')
        binary=records[0];signature=binary.get('signature')
        if not isinstance(signature,dict) or signature.get('status')!='Valid' or signature.get('simple_name')!='Google LLC' or not re.search(r'(?:^|,\s*)O=Google LLC(?:,|$)',str(signature.get('subject',''))):
            raise OperationError('The existing per-user Canary SxS file has no verified valid Google LLC signature. It was preserved for review.')
        return binary

    def install_canary_local(self, version: str, before: dict) -> dict:
        """Install only the exact signed Google side-by-side build in the catalog."""
        if not re.fullmatch(r'\d+\.\d+\.\d+\.\d+',version):
            raise OperationError('Canary installation requires a known exact catalog version; browser channels were preserved.')
        arch=getattr(self,'arch',None) or architecture()
        if arch not in ('x64','arm64'):raise OperationError('No supported Canary installer architecture selected.')
        path='manifests/g/Google/Chrome/Canary/'+version+'/Google.Chrome.Canary.installer.yaml'
        meta_url='https://api.github.com/repos/microsoft/winget-pkgs/contents/'+path
        metadata=self.get_json(meta_url)
        if not isinstance(metadata,dict) or metadata.get('encoding')!='base64' or metadata.get('path')!=path or not isinstance(metadata.get('content'),str) or len(metadata['content'])>512*1024:
            raise OperationError('Exact official WinGet Canary installer metadata was not available; no browser channel substituted.')
        try:
            manifest=base64.b64decode(re.sub(r'\s+','',metadata['content']),validate=True).decode('utf-8-sig')
        except (ValueError,UnicodeError) as exc:
            raise OperationError('Official Canary metadata could not be decoded; no browser update attempted.') from exc
        # This intentionally supports a narrow manifest shape, rather than loading
        # arbitrary YAML or inferring switches from a different package/channel.
        for key,value in (('PackageIdentifier','Google.Chrome.Canary'),('PackageVersion',version),('InstallerType','exe'),('Scope','user')):
            if re.findall(r'(?m)^'+key+r':\s*(\S[^\r\n]*)\s*$',manifest)!=[value]:
                raise OperationError('Canary manifest identity, version, installer type, or user scope was ambiguous; no browser update attempted.')
        switches=re.search(r'(?m)^InstallerSwitches:\r?\n((?:[ \t].*(?:\r?\n|$))+)',manifest)
        if not switches or re.findall(r'(?m)^\s+Custom:\s*([^\r\n]*)$',switches[1])!=['--chrome-sxs --do-not-launch-chrome'] or any(re.match(r'\s+([^:]+):',line).group(1) not in ('Custom','Log') for line in switches[1].splitlines() if re.match(r'\s+([^:]+):',line)):
            raise OperationError('Official Canary side-by-side switches were not uniquely verified; no browser update attempted.')
        if not re.search(r'(?m)^InstallModes:\r?\n- silent\r?$',manifest):
            raise OperationError('Official Canary silent install mode was not verified; no browser update attempted.')
        blocks=re.findall(r'(?ms)^- Architecture:\s*(x64|arm64|x86)\r?\n(.*?)(?=^- Architecture:|\Z)',manifest)
        selected=[body for cpu,body in blocks if cpu==arch]
        if len(selected)!=1:raise OperationError('Official Canary architecture selection was ambiguous; no browser update attempted.')
        urls=re.findall(r'(?m)^  InstallerUrl:\s*(\S+)\s*$',selected[0])
        hashes=re.findall(r'(?m)^  InstallerSha256:\s*([0-9a-fA-F]{64})\s*$',selected[0])
        if len(urls)!=1 or len(hashes)!=1:raise OperationError('Exact Canary installer URL and SHA256 are required; no browser update attempted.')
        url=urls[0];parsed=urllib.parse.urlsplit(url)
        if parsed.scheme!='https' or parsed.netloc!='dl.google.com' or parsed.query or parsed.fragment or not re.fullmatch(r'/release2/chrome/[a-z0-9]+_'+re.escape(version)+'/'+re.escape(version)+r'_chrome_installer_uncompressed\.exe',parsed.path):
            raise OperationError('Canary installer metadata did not identify the expected exact official Google download; no browser update attempted.')
        sha=hashes[0].lower();download=self.root/'downloads'/('canary-'+version+'-'+arch+'.exe')
        assert_regular_path(download)
        self.fetch(url,download,sha,max_bytes=512*1024**2)
        signature=self.ps_json("$s=Get-AuthenticodeSignature -LiteralPath "+ps_literal(download)+"; [pscustomobject]@{status=$s.Status.ToString();subject=if($s.SignerCertificate){$s.SignerCertificate.Subject}else{''};simple_name=if($s.SignerCertificate){$s.SignerCertificate.GetNameInfo([Security.Cryptography.X509Certificates.X509NameType]::SimpleName,$false)}else{''}} | ConvertTo-Json -Compress",label='Verify exact Canary installer Google signature')
        evidence={'source_manifest':meta_url,'version':version,'architecture':arch,'url':url,'sha256':sha,'signature':signature,'switches':['--chrome-sxs','--do-not-launch-chrome'],'before':before}
        self.current_result['channel_install']=evidence
        if not isinstance(signature,dict) or signature.get('status')!='Valid' or signature.get('simple_name')!='Google LLC' or not re.search(r'(?:^|,\s*)O=Google LLC(?:,|$)',str(signature.get('subject',''))):
            raise OperationError('A valid Google LLC signer and organization are required; the browser installer was not run.')
        body="$path="+ps_literal(download)+"; if((Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash -ine "+ps_literal(sha)+") {throw 'Canary checksum changed; installer not run'}; $s=Get-AuthenticodeSignature -LiteralPath $path; if($s.Status.ToString() -ne 'Valid' -or $s.SignerCertificate.GetNameInfo([Security.Cryptography.X509Certificates.X509NameType]::SimpleName,$false) -ne 'Google LLC' -or $s.SignerCertificate.Subject -notmatch '(?:^|,\\s*)O=Google LLC(?:,|$)') {throw 'Canary signature changed; installer not run'}; & $path '--chrome-sxs' '--do-not-launch-chrome' | Out-Null; if($LASTEXITCODE -ne 0 -and $LASTEXITCODE -ne 3){throw ('Canary installer failed with exit '+$LASTEXITCODE)}; 'CANARY_INSTALL_COMPLETED'"
        if self.cancel.is_set():raise StopRun('Stopped before local Canary side-by-side installation.')
        self.require(self.ps(body,timeout=900,label='Install exact verified Canary side-by-side without launching Chrome'),'Official Canary side-by-side installation')
        after=self.canary_registration();evidence['after']=after
        binary=self.canary_user_binary(after)
        if not binary or binary['version']!=version:
            raise OperationError('Installer returned but the exact Chrome Canary SxS binary version was not verified.')
        stable=lambda data:{row['path'].casefold():row['version'] for row in data['stable_executables']}
        if stable(after)!=stable(before):raise OperationError('Stable Chrome binary versions changed during Canary installation; further browser actions stopped for review.')
        return after

    def webview_registration(self) -> list[dict]:
        # Evergreen may be hidden from WinGet's installed-app inventory. Microsoft
        # documents these EdgeUpdate pv values as the runtime presence check.
        key=r'SOFTWARE\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}'
        body=r"""$locations=@(
          @{Hive='LocalMachine';View='Registry32';Location='HKEY_LOCAL_MACHINE\SOFTWARE\WOW6432Node\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}'},
          @{Hive='CurrentUser';View='Default';Location='HKEY_CURRENT_USER\Software\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}'}
        ); $found=@(foreach($location in $locations) {
          $base=$null; $key=$null
          try {
            $hive=[Enum]::Parse([Microsoft.Win32.RegistryHive],$location.Hive)
            $view=[Enum]::Parse([Microsoft.Win32.RegistryView],$location.View)
            $base=[Microsoft.Win32.RegistryKey]::OpenBaseKey($hive,$view)
            $key=$base.OpenSubKey(KEY_PATH,$false)
            if($key) {
              $pv=$key.GetValue('pv',$null,[Microsoft.Win32.RegistryValueOptions]::DoNotExpandEnvironmentNames)
              if($pv -is [string]) { [pscustomobject]@{location=$location.Location;version=$pv} }
            }
          } finally { if($key){$key.Dispose()}; if($base){$base.Dispose()} }
        }); ConvertTo-Json -InputObject @($found) -Compress""".replace('KEY_PATH',ps_literal(key))
        result=self.require(self.ps(body,label='Verify WebView2 Evergreen EdgeUpdate registry registration'),'WebView2 registration query')
        try:
            rows=json.loads(result.out)
        except ValueError as exc:
            raise OperationError('WebView2 registration query returned invalid JSON; runtime presence is not verified.') from exc
        if not isinstance(rows,list) or any(not isinstance(row,dict) for row in rows):
            raise OperationError('WebView2 registration query returned an unexpected result; runtime presence is not verified.')
        return [row for row in rows if re.fullmatch(r'\d+\.\d+\.\d+\.\d+',str(row.get('version',''))) and any(int(n)>0 for n in row['version'].split('.'))]

    def install_winget(self,item:dict):
        wing=self.find('winget.exe')
        if not wing:raise OperationError('Microsoft App Installer / WinGet is unavailable. Open Microsoft Store and install App Installer, then rerun.')
        common=['--id',item['package'],'--exact','--source',item['source'],'--accept-source-agreements','--disable-interactivity']
        before=self.run_command([wing,'list',*common],quiet=True,timeout=90,label='Installed package query: '+item['package'])
        version_query=self.run_command([wing,'show',*common,'--versions'],quiet=True,timeout=90,label='Published versions in selected channel: '+item['package'])
        available=[]
        if version_query.code==0:
            available=re.findall(r'(?m)^\s*(v?\d+(?:\.\d+){1,4}(?:[-+][A-Za-z0-9.-]+)?)\s*$',ANSI.sub('',version_query.out))
        self.current_result['expected']=available[0] if available else 'Catalog-managed; exact target unavailable'
        def parse_list(output):
            for line in ANSI.sub('',output).splitlines():
                match=re.search(re.escape(item['package'])+r'\s+(\S+)',line,re.I)
                if match:return match[1]
            return ''
        self.current_result['before']=parse_list(before.out)
        if item['id']=='canary':
            channel=self.canary_registration()
            self.current_result['channel_registration_check']=channel
            binary=self.canary_user_binary(channel)
            actual=binary['version'] if binary else ''
            self.current_result['winget_correlated_before']=self.current_result['before']
            self.current_result['before']=actual or 'Canary SxS binary not found'
            if not available:
                self.current_result.update(status='CHANNEL_NOT_VERIFIED',actual=actual or 'not found',detail='An exact Canary catalog target was unavailable. Browser channels were preserved; use the official Chrome Canary download at https://www.google.com/chrome/canary/.')
                return
            target=available[0]
            if not re.fullmatch(r'\d+\.\d+\.\d+\.\d+',target):
                self.current_result.update(status='CHANNEL_NOT_VERIFIED',actual=actual or 'not found',detail='An unambiguous four-part Canary catalog target was unavailable. Browser channels were preserved; use https://www.google.com/chrome/canary/.')
                return
            if actual!=target:
                if actual and tuple(map(int,actual.split('.')))>tuple(map(int,target.split('.'))):
                    self.current_result.update(status='INSTALLED_CHECK_NEEDED',actual=actual,detail='The actual Canary SxS binary is newer than the selected WinGet catalog. It was preserved without a downgrade; independent latestness remains unverified.')
                    return
                channel=self.install_canary_local(target,channel)
                actual=self.canary_user_binary(channel)['version']
            if actual!=target:raise OperationError('Canary recovery did not return the exact selected per-user binary version; latestness was not verified.')
            self.current_result.update(status='VERIFIED',actual=actual,detail='Per-user Chrome Canary SxS binary and valid Google signature match the exact selected catalog version. Other installation scopes were inspected only; browser UI not exercised.')
            return
        action='upgrade' if before.code==0 else 'install'
        args=[wing,action,*common,'--accept-package-agreements','--silent']
        if action=='upgrade':args+=['--include-unknown']
        for attempt in range(3):
            if self.cancel.is_set():raise StopRun('Stopped before the next WinGet attempt.')
            suffix=(' (retry '+str(attempt)+')') if attempt else ''
            r=self.run_command(args,timeout=1200,label=action+' '+item['name']+' ['+item['channel']+']'+suffix)
            if r.timeout:raise StopRun('WinGet timed out. Another installer process may still be running.')
            # A completed installer reporting WININET_E_TIMEOUT can be retried.
            # Do not retry a killed manager, signature errors, policy failures, or
            # arbitrary installer errors, and retain exactly the selected channel.
            transient=(r.code & 0xffffffff)==0x80072EE2
            if not transient or attempt==2:break
            delay=(5,15)[attempt]
            self.current_result.setdefault('retries',[]).append({'attempt':attempt+1,'reason':'WININET_E_TIMEOUT (0x80072EE2)','delay_seconds':delay,'package':item['package'],'source':item['source'],'channel':item['channel']})
            self.log('The selected package installer reported a network timeout. Retrying the same package and channel in '+str(delay)+' seconds.','warning')
            if self.cancel.wait(delay):raise StopRun('Stopped during the WinGet retry delay.')
        # WinGet's no-applicable-update code is not a network/install success.
        no_update=(r.code & 0xffffffff)==0x8A15002B and before.code==0
        local_terminal=None
        if r.code not in (0,3010,1641) and not no_update:
            if item['id']=='terminal' and (r.code & 0xffffffff)==0x80072EE2 and available:
                self.log('WinGet completed three timeout attempts. Recovering the exact same official Terminal Preview bundle from a verified local file.','warning')
                local_terminal=self.install_terminal_preview_local(available[0])
            else:self.require(r,'WinGet '+action+' '+item['package'])
        self.refresh_path()
        after=self.run_command([wing,'list',*common],quiet=True,timeout=90,label='Verify registered package: '+item['package'])
        actual=parse_list(after.out)
        if local_terminal:
            actual=available[0]
            self.current_result['registration_check']={'method':'Exact Terminal Preview AppX name, version, and healthy status','registrations':local_terminal,'winget_inventory_exit_code':after.code}
        if item['id']=='webview':
            registrations=self.webview_registration()
            self.current_result['registration_check']={'method':'Microsoft-documented EdgeUpdate Clients pv registry values','registrations':registrations,'winget_inventory_exit_code':after.code}
            if not registrations:raise OperationError('Installer returned, but neither the per-user nor per-machine WebView2 Evergreen registry key contains a valid runtime version.')
            actual=max((row['version'] for row in registrations),key=lambda version:tuple(map(int,version.split('.'))))
        self.current_result['actual']=actual or ('present; exact version not parsed' if after.code==0 else 'not found')
        if after.code!=0 and item['id']!='webview' and not local_terminal:raise OperationError('Installer returned, but registration could not be confirmed. '+redact(after.out[-1200:]))
        if actual and available and actual.lstrip('v')==available[0].lstrip('v'):
            self.current_result['status']='VERIFIED'
            self.current_result['detail']='Registered version matches the selected package catalog. Desktop UI not exercised.'
        elif no_update and actual and available:
            self.current_result['status']='VERSION_MISMATCH'
            self.current_result['detail']='WinGet reports no applicable update, but registered version '+actual+' differs from selected catalog version '+available[0]+'. Latestness is not verified; the original package and channel were preserved.'
        elif no_update:
            self.current_result['status']='CATALOG_CURRENT'
            self.current_result['detail']='WinGet reports no applicable update; package registration confirmed. Independent upstream latestness not proved.'
        else:
            self.current_result['status']='INSTALLED_CHECK_NEEDED'
            self.current_result['detail']='Package registration confirmed; exact latest-version comparison or GUI check remains outstanding.'
        if r.code in (3010,1641):
            self.report['reboot_requested_by_installer']=True
            self.log('An installer requested restart. Workbench will not initiate a reboot.','warning')
        if item['id']=='chatgpt':
            self.report['coverage']['desktop']='Current app ID 9PLM9XGG6VKS requested. Bundled agent updates are separate from the managed npm Codex CLI.'

    def node_archive(self,version:str,arch:str,*,nightly:bool) -> Path:
        if not SEMVER.fullmatch(version) or arch not in ('x64','arm64'):raise OperationError('Invalid official Node archive identity.')
        filename=f'node-{version}-win-{arch}.zip'
        directory=self.root/'runtimes'/('node' if nightly else 'npm-host')/f'{version}-{arch}'
        assert_regular_path(directory)
        exe=directory/f'node-{version}-win-{arch}'/'node.exe'
        marker=directory/'.workbench-owned.json'
        if not (marker.is_file() and exe.is_file()):
            if directory.exists():raise OperationError('An incomplete/unowned Node destination exists. It has been preserved for review: '+str(directory))
            base=f'https://nodejs.org/'+('download/nightly/' if nightly else 'dist/')+version+'/'
            sums=self.fetch(base+'SHASUMS256.txt').decode('utf-8')
            match=re.search(r'(?im)^([0-9a-f]{64})\s+\*?'+re.escape(filename)+r'\s*$',sums)
            if not match:raise OperationError('Official SHA-256 entry for Node ZIP was not found.')
            download=self.root/'downloads'/filename
            self.fetch(base+filename,download,match[1],max_bytes=512*1024**2)
            safe_extract(download,directory)
            atomic_json(marker,{'owned_by':SCHEMA,'version':version,'archive_sha256':match[1]})
        checked=self.require(self.run_command([exe,'--version'],timeout=40,label='Test exact official Node '+version),'Node executable')
        if not version_matches(checked.out,version):raise OperationError('Downloaded Node version does not match the requested archive.')
        return exe

    @staticmethod
    def npm_version_output(output:str) -> tuple[str,list[str]]:
        npm_lines=[clean for line in output.splitlines() if (clean:=ANSI.sub('',line).strip())]
        npm_versions=[line for line in npm_lines if line[0].isdigit() and SEMVER.fullmatch(line)]
        if len(npm_versions)!=1:raise OperationError('Bundled npm did not return one unambiguous version line. Its diagnostic output was not stored as a version.')
        npm_version=npm_versions[0]
        npm_diagnostics=[line for line in npm_lines if line!=npm_version]
        return npm_version,npm_diagnostics

    def step_node(self):
        source='https://nodejs.org/download/nightly/index.json'
        arch=getattr(self,'arch',None) or architecture()
        candidates=[x for x in self.get_json(source) if 'win-'+arch+'-zip' in x.get('files',[]) and SEMVER.fullmatch(str(x.get('version',''))) and 'nightly' in x['version']]
        if not candidates:raise OperationError('No official Node nightly ZIP is published for this architecture. No stable tool-runtime fallback attempted.')
        version=max(candidates,key=lambda x:semver_key(x['version']))['version']
        self.current_result.update(expected=version,source=source)
        exe=self.node_archive(version,arch,nightly=True)
        npm_meta=self.npm_meta('npm');npm_version=choose_npm(npm_meta)
        engines=npm_meta['versions'][npm_version].get('engines',{}).get('node')
        if not isinstance(engines,str) or not engines:raise OperationError('Newest npm has no declared Node engine range; previous managed pair preserved.')
        stable=[x['version'] for x in self.get_json('https://nodejs.org/dist/index.json') if 'win-'+arch+'-zip' in x.get('files',[]) and SEMVER.fullmatch(str(x.get('version',''))) and SEMVER.fullmatch(x['version'])[4] is None]
        choice_file=self.run_dir/'npm-node-candidates.json'
        atomic_json(choice_file,{'engines':engines,'nightly':version,'hosts':stable})
        semver=exe.parent/'node_modules/npm/node_modules/semver'
        if not (semver/'index.js').is_file():raise OperationError('Official bundled npm semver evaluator missing; compatibility was not guessed.')
        code="const fs=require('fs'),s=require(process.argv[1]),d=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));if(!s.validRange(d.engines))throw Error('Invalid npm engine range');const acceptsNightly=s.satisfies(d.nightly,d.engines);const hosts=d.hosts.filter(v=>s.satisfies(v,d.engines)).sort(s.rcompare);console.log(JSON.stringify({host:acceptsNightly?d.nightly:hosts[0],nightly_accepted:acceptsNightly}));"
        result=self.require(self.run_command([exe,'-e',code,semver,choice_file],timeout=40,label='Evaluate newest npm declared engines with official npm semver'),'npm compatibility preflight')
        try:choice=json.loads(result.out)
        except ValueError as exc:raise OperationError('npm compatibility preflight returned invalid JSON; previous pair preserved.') from exc
        if not isinstance(choice,dict) or type(choice.get('nightly_accepted')) is not bool:raise OperationError('npm compatibility preflight returned an unexpected shape; previous pair preserved.')
        host_version=choice.get('host')
        if host_version not in ([version] if choice.get('nightly_accepted') else stable):raise OperationError('No published compatible npm Node host; previous pair preserved.')
        host=exe if choice.get('nightly_accepted') else self.node_archive(host_version,arch,nightly=False)
        bootstrap=host.parent/'node_modules/npm/bin/npm-cli.js'
        env={**self.env,'PATH':str(host.parent)+os.pathsep+self.env.get('PATH','')}
        boot=self.require(self.run_command([host,bootstrap,'--version'],env=env,timeout=40,label='Verify compatible npm bootstrap host'),'npm bootstrap')
        _,warnings=self.npm_version_output(boot.out)
        if warnings:raise OperationError('The npm bootstrap host emitted diagnostics; package manager was not replaced.')
        directory=self.root/'runtimes/npm'/npm_version;assert_regular_path(directory)
        marker=directory/'.workbench-owned.json';npmjs=directory/'node_modules/npm/bin/npm-cli.js'
        if not (marker.is_file() and npmjs.is_file()):
            if directory.exists():raise OperationError('Incomplete/unowned npm destination preserved for review.')
            directory.mkdir(parents=True)
            if self.cancel.is_set():raise StopRun('Stopped before private npm installation.')
            self.require(self.run_command([host,bootstrap,'install','--prefix',directory,'npm@'+npm_version,'--registry','https://registry.npmjs.org','--ignore-scripts','--no-fund','--no-audit'],env=env,timeout=600,label='Install exact newest official npm into private prefix'),'Private npm installation')
            info=json.loads((directory/'node_modules/npm/package.json').read_text(encoding='utf-8'))
            if info.get('name')!='npm' or info.get('version')!=npm_version or info.get('engines',{}).get('node')!=engines:raise OperationError('Installed npm identity/engine metadata differs from preflight.')
            atomic_json(marker,{'owned_by':SCHEMA,'version':npm_version})
        nr=self.require(self.run_command([host,npmjs,'--version'],env=env,timeout=40,label='Verify newest npm on declared compatible host without warnings'),'Compatible npm execution')
        actual,diagnostics=self.npm_version_output(nr.out)
        if actual!=npm_version or diagnostics:raise OperationError('Newest npm version or warning-free compatibility verification failed; previous pair preserved.')
        if self.cancel.is_set():raise StopRun('Stopped before activating verified Node/npm pair.')
        self.active['node']={'version':version,'command':[str(exe)],'source':source}
        self.active['npm']={'version':npm_version,'command':[str(host),str(npmjs)],'source':'https://registry.npmjs.org/npm','host_version':host_version,'engines':engines,'diagnostics':[]}
        self.env['PATH']=str(exe.parent)+os.pathsep+self.env.get('PATH','')
        self.save_state()
        self.current_result.update(actual=version,npm_version=npm_version,npm_host_version=host_version,npm_engines=engines,nightly_accepted_by_npm=choice['nightly_accepted'],detail=f'Node {version} retained for nightly tools. npm {npm_version} runs on its declared compatible private host {host_version}; actual execution produced no diagnostics. The separate package-manager host does not replace the nightly tool runtime.')

    def npm_environment(self) -> dict:
        command=self.npm_command()
        return {**self.env,'PATH':str(Path(command[1]).parents[2]/'.bin')+os.pathsep+str(Path(command[0]).parent)+os.pathsep+self.env.get('PATH','')}

    def npm_command(self) -> list[str]:
        command=self.active.get('npm',{}).get('command')
        if not command or not all(Path(x).is_file() for x in command[:2]):raise OperationError('Managed Node/npm did not initialize. Its failure must be repaired first.')
        return command

    def npm_meta(self,name:str) -> dict:
        url='https://registry.npmjs.org/'+urllib.parse.quote(name,safe='@')
        meta=self.get_json(url)
        if meta.get('name')!=name:raise OperationError('Registry package identity mismatch.')
        return meta

    def step_codex(self):
        meta=self.npm_meta('@openai/codex');version=choose_npm(meta)
        self.current_result['expected']=version
        directory=self.root/'runtimes/codex'/version
        entry=directory/'node_modules/@openai/codex/bin/codex.js'
        marker=directory/'.workbench-owned.json'
        directory.mkdir(parents=True,exist_ok=True)
        if not (marker.is_file() and entry.is_file()):
            self.require(self.run_command([*self.npm_command(),'install','--global','--prefix',directory,
                '@openai/codex@'+version,'--registry','https://registry.npmjs.org','--no-fund','--no-audit'],
                env=self.npm_environment(),timeout=1200,label='Install exact official Codex '+version),'Codex package installation')
            atomic_json(marker,{'owned_by':SCHEMA,'version':version})
        if not entry.is_file():raise OperationError('Official Codex npm entry point missing after installation.')
        cmd=[self.active['node']['command'][0],str(entry)]
        check=self.require(self.run_command([*cmd,'--version'],timeout=60,label='Verify exact Codex build'),'Codex executable')
        if not version_matches(check.out,version):raise OperationError('Codex executable version does not match the requested npm release.')
        self.activate('codex',version,cmd,'https://registry.npmjs.org/@openai%2Fcodex')
        self.current_result['detail']='Exact build runs. Existing CODEX_HOME is reused; original binaries remain until their dependents can be checked.'

    def step_openai_cli(self):
        source='https://api.github.com/repos/openai/openai-cli/releases?per_page=100'
        releases=self.get_json(source)
        valid=[x for x in releases if not x.get('draft') and SEMVER.fullmatch(x.get('tag_name',''))]
        if not valid:raise OperationError('No supported OpenAI API CLI release metadata found.')
        release=max(valid,key=lambda r:semver_key(r['tag_name']))
        arch=(getattr(self,'arch',None) or architecture())
        cpus=('arm64','aarch64') if arch=='arm64' else ('amd64','x86_64','x64')
        assets=[x for x in release.get('assets',[]) if 'windows' in x['name'].lower() and x['name'].lower().endswith('.zip') and any(cpu in x['name'].lower() for cpu in cpus)]
        self.current_result['expected']=release['tag_name']
        if len(assets)!=1:
            self.current_result.update(status='NOT_AVAILABLE',detail='Latest release has no single identifiable Windows ZIP for this architecture. No unofficial replacement installed.')
            return
        asset=assets[0];digest=asset.get('digest') or ''
        sha=digest.removeprefix('sha256:') if digest.startswith('sha256:') else ''
        if not re.fullmatch(r'[0-9a-fA-F]{64}',sha):
            checksum=next((a for a in release['assets'] if re.fullmatch(r'(?i)(?:.*_)?(?:checksums|sha256sums|sha256sum)(?:\.txt)?',a['name'])),None)
            if checksum:
                sums=self.fetch(checksum['browser_download_url']).decode('utf-8')
                m=re.search(r'(?im)^([0-9a-f]{64})\s+\*?'+re.escape(asset['name'])+r'\s*$',sums)
                if m:sha=m[1]
        if not re.fullmatch(r'[0-9a-fA-F]{64}',sha):raise OperationError('No publisher-release SHA-256 for this CLI ZIP. Download not executed.')
        target=self.root/'runtimes/openai-cli'/release['tag_name']
        if not (target/'.workbench-owned.json').is_file():
            if target.exists():raise OperationError('Unowned API CLI destination exists; review it before replacing.')
            zip_path=self.root/'downloads'/asset['name']
            self.fetch(asset['browser_download_url'],zip_path,sha,max_bytes=512*1024**2)
            safe_extract(zip_path,target)
            atomic_json(target/'.workbench-owned.json',{'owned_by':SCHEMA,'version':release['tag_name'],'sha256':sha})
        exes=list(target.rglob('openai.exe'))
        if len(exes)!=1:raise OperationError('Cannot uniquely identify openai.exe in its release archive.')
        self.require(self.run_command([exes[0],'--help'],timeout=45,label='Test OpenAI API CLI startup'),'OpenAI API CLI startup')
        self.activate('openai-api',release['tag_name'],[exes[0]],release['html_url'])
        self.current_result['detail']='Release archive integrity and CLI startup verified. No API credentials created and no API call made.'

    def step_python(self):
        uv=self.find('uv.exe')
        if not uv:raise OperationError('uv is unavailable. Repair the uv installation first.')
        self.uv=uv
        catalog=self.require(self.run_command([uv,'python','list','--all-versions','--only-downloads','--output-format','json'],quiet=True,timeout=120,label='Discover published CPython downloads including prereleases'),'uv Python catalog')
        data=json.loads(catalog.out)
        arch=getattr(self,'arch',None) or architecture()
        selected=self.preflight_python(data,arch,uv)
        if self.cancel.is_set():raise StopRun('Stopped after Python compatibility preflight; no interpreter was installed.')
        version=selected['version'];key=selected['key']
        self.current_result['expected']=version
        self.require(self.run_command([uv,'python','install','--no-bin','--no-registry',key],timeout=1200,label='Install compatible selected CPython '+version),'CPython installation')
        if self.cancel.is_set():raise StopRun('Stopped after the current Python installation; no candidate environment was created.')
        directory=self.root/'environments'/('python-'+version+'-'+self.run_id)
        assert_regular_path(directory)
        py=directory/'Scripts/python.exe'
        if not py.is_file():
            self.require(self.run_command([uv,'venv','--managed-python','--python',key,directory],timeout=300,label='Create isolated Python SDK environment'),'Isolated Python environment')
        checked=self.require(self.run_command([py,'-c','import platform; print(platform.python_version())'],timeout=40,label='Verify Python build'),'Python execution')
        if not version_matches(checked.out,version):raise OperationError('Python interpreter does not match selected release.')
        atomic_json(directory/'.workbench-owned.json',{'owned_by':SCHEMA,'version':version})
        self.python_candidate={'version':version,'command':[str(py)],'source':'uv download catalog; full selected package compatibility preflight',
            'requirements_sha256':self.report['python_compatibility']['requirements_sha256'],'packages':selected_python_packages(self.options)}
        self.current_result['actual']=version
        self.current_result['detail']='Newest CPython with a complete binary-wheel solution for the selected packs; prereleases included in the search. Compatibility choice was recorded before installation.'

    def preflight_python(self, data: list[dict], arch: str, uv: str) -> dict:
        packages=selected_python_packages(self.options)
        source=self.run_dir/'Python-selected-packages.in'
        assert_regular_path(source)
        source.write_text('\n'.join(packages)+'\n',encoding='utf-8')
        target='aarch64-pc-windows-msvc' if arch=='arm64' else 'x86_64-pc-windows-msvc'
        evidence={'policy':'Newest published normal CPython minor with a complete compatible wheel solution, including development releases. Selection occurs before installation; no retry after a failed install.',
                  'packages':packages,'target':target,'index':'https://pypi.org/simple','attempts':[]}
        self.report['python_compatibility']=evidence
        candidates=compatible_python_candidates(data,arch)
        for candidate in candidates:
            if self.cancel.is_set():raise StopRun('Stopped before Python compatibility preflight.')
            version=str(candidate['version'])
            lock=self.run_dir/('Python-resolved-'+version+'.txt')
            assert_regular_path(lock)
            result=self.run_command([uv,'pip','compile',source,'--python',sys.executable,
                '--python-version',version,'--python-platform',target,'--no-python-downloads',
                '--prerelease','allow','--resolution','highest','--default-index','https://pypi.org/simple',
                '--only-binary',':all:','--generate-hashes','--no-header','--no-annotate',
                '--output-file',lock],quiet=True,timeout=900,label='Preflight complete selected Python packs for CPython '+version)
            attempt={'version':version,'key':candidate['key'],'exit_code':result.code}
            evidence['attempts'].append(attempt)
            if result.timeout:raise StopRun('Python compatibility resolution timed out; no interpreter was selected.')
            if result.code==0:
                if not lock.is_file():raise OperationError('Python resolver did not produce its requirements lock. No interpreter was selected.')
                content=lock.read_bytes()
                pins=dict(re.findall(r'^([A-Za-z0-9_.-]+)==([^\s;\\]+)',content.decode('utf-8'),re.M))
                if not all(package in pins for package in packages) or b'--hash=sha256:' not in content:
                    raise OperationError('Python compatibility lock is incomplete or unhashed. No interpreter was selected.')
                attempt['status']='COMPATIBLE'
                evidence.update({'selected_version':version,'selected_key':candidate['key'],
                    'newest_catalog_version':str(candidates[0]['version']),
                    'selection_reason':'Newest catalog release whose entire selected package set resolves to compatible binary wheels.',
                    'requirements_sha256':hashlib.sha256(content).hexdigest(),
                    'requirements_lock':str(lock),'resolved_versions':pins})
                self.python_requirements_lock=lock
                self.log('Python compatibility preflight selected '+version+' for all '+str(len(packages))+' requested packages before installing an interpreter.')
                self.current_result['compatibility']=evidence
                return candidate
            if python_resolution_incompatible(result):
                attempt.update({'status':'INCOMPATIBLE','reason':redact(result.out[-6000:])})
                self.log('CPython '+version+' has no complete binary-wheel solution for the selected packs; recorded resolver proof.','warning')
                continue
            attempt.update({'status':'PREFLIGHT_ERROR','reason':redact(result.out[-2000:])})
            self.require(result,'Python compatibility preflight; an operational error cannot justify selecting an older release')
        raise OperationError('No published CPython 3.11+ release resolves the complete selected package set to binary wheels. See python_compatibility resolver evidence. Existing environments remain selected.')

    def install_python_packages(self, packages: list[str]):
        try:
            return self._install_python_packages(packages)
        except Exception:
            self.python_candidate_failed = True
            raise

    def _install_python_packages(self, packages: list[str]):
        py=(self.python_candidate or {}).get('command',[None])[0]
        uv=self.find('uv.exe')
        if not uv or not py or not Path(py).is_file():raise OperationError('Managed Python/uv unavailable. No default interpreter was modified.')
        lock=getattr(self,'python_requirements_lock',None)
        if not lock or not Path(lock).is_file():raise OperationError('Complete selected Python pack compatibility lock is missing. Rerun Python preflight; no unplanned resolution was attempted.')
        if hashlib.sha256(Path(lock).read_bytes()).hexdigest()!=self.python_candidate.get('requirements_sha256'):
            raise OperationError('Python compatibility lock changed after selection; candidate was not installed.')
        if not getattr(self,'python_lock_installed',False):
            if self.cancel.is_set():raise StopRun('Stopped before installing Python packages.')
            self.require(self.run_command([uv,'pip','install','--python',py,'--default-index','https://pypi.org/simple',
                '--only-binary',':all:','--require-hashes','--requirements',lock],timeout=1800,
                label='Install exact preflight-resolved full selected Python pack set'),'Resolved Python package installation; no older interpreter retry')
            self.require(self.run_command([uv,'pip','check','--python',py],timeout=120,label='Check complete Python pack dependency consistency'),'Python dependency consistency')
            self.python_lock_installed=True
        imports=[PYTHON_IMPORTS[name] for name in packages]
        code='import importlib,importlib.metadata as m,json; names='+repr(packages)+'; modules='+repr(imports)+'; [importlib.import_module(n) for n in modules]; print(json.dumps({n:m.version(n) for n in names}))'
        versions=self.require(self.run_command([py,'-c',code],quiet=True,timeout=180,label='Verify selected Python package imports and installed versions'),'Python package imports')
        actual=json.loads(versions.out.splitlines()[-1])
        expected=self.report['python_compatibility']['resolved_versions']
        if any(actual.get(name)!=expected.get(name) for name in packages):raise OperationError('Installed Python packages do not match the compatibility lock.')
        self.current_result['versions']=actual
        self.current_result['expected']='Exact preflight-resolved published versions; prereleases allowed; SHA-256 locked binary wheels'
        self.current_result['detail']='All selected packs installed together from the compatibility lock. This pack imports successfully and its versions match; individual APIs have not all been exercised.'

    def step_python_packages(self):self.install_python_packages(list(PYTHON_PACKS['core']))
    def step_documents(self):
        self.install_python_packages(list(PYTHON_PACKS['documents']))
    def step_science(self):self.install_python_packages(list(PYTHON_PACKS['science']))

    def install_js_packages(self,packages:list[str]):
        base=self.root/'environments'/('javascript-'+self.run_id)
        assert_regular_path(base)
        base.mkdir(parents=True,exist_ok=True)
        manifest=base/'package.json'
        if not manifest.exists():atomic_json(manifest,{'name':'openai-edge-workbench-tools','private':True,'version':'1.0.0'})
        versions={};failed=[]
        for name in packages:
            if self.cancel.is_set():raise StopRun('Stopped after current JavaScript package operation.')
            try:
                v=choose_npm(self.npm_meta(name))
                r=self.run_command([*self.npm_command(),'install','--prefix',base,'--save-exact',name+'@'+v,
                    '--registry','https://registry.npmjs.org','--no-fund','--no-audit'],env=self.npm_environment(),timeout=1200,label='Install exact JavaScript build '+name+'@'+v)
                self.require(r,'JavaScript package '+name)
                info=json.loads((base/'node_modules'/name/'package.json').read_text(encoding='utf-8'))
                if info.get('version')!=v:raise OperationError('Package version mismatch')
                versions[name]=v
            except StopRun:raise
            except Exception as exc:
                failed.append(name);self.log(str(exc),'error')
        self.current_result['versions']=versions
        if failed:
            self.js_candidate_failed=True
            raise OperationError('JavaScript installs failed: '+', '.join(failed))
        complete=dict((self.js_candidate or {}).get('versions',{})); complete.update(versions)
        self.js_candidate={'version':','.join(f'{k}@{v}' for k,v in complete.items()),'versions':complete,'path':str(base),'source':'https://registry.npmjs.org'}
        return base

    def step_javascript(self):
        self.install_js_packages(['openai','@openai/agents','@openai/codex-sdk'])
        self.current_result['detail']='Exact newest package versions installed into the private Workbench workspace; user projects untouched.'

    def step_extensions(self):
        code=self.find('code-insiders.cmd')
        if not code:raise OperationError('VS Code Insiders CLI unavailable.')
        help_result=self.run_command([code,'--help'],quiet=True,timeout=60,label='Discover editor extension CLI capabilities')
        if '--pre-release' not in help_result.out:raise OperationError('Installed editor CLI does not advertise --pre-release; not substituting a stable extension install.')
        failed=[]
        for ext in ('openai.chatgpt','ms-python.python','ms-toolsai.jupyter'):
            if self.cancel.is_set():raise StopRun('Stopped after current extension operation.')
            r=self.run_command([code,'--install-extension',ext,'--pre-release','--force'],timeout=600,label='Install/update preview extension '+ext)
            if r.code!=0:failed.append(ext)
        listed=self.require(self.run_command([code,'--list-extensions','--show-versions'],quiet=True,timeout=120,label='Verify preview extension installation'),'Extension inventory')
        self.current_result['extensions']=[s.strip() for s in listed.out.splitlines() if re.match(r'^(openai\.chatgpt|ms-python\.python|ms-toolsai\.jupyter)@',s,re.I)]
        for ext in ('openai.chatgpt','ms-python.python','ms-toolsai.jupyter'):
            if not any(s.lower().startswith(ext+'@') for s in self.current_result['extensions']):failed.append(ext)
        if failed:raise OperationError('Preview extension installation unconfirmed for: '+', '.join(sorted(set(failed))))
        self.current_result['detail']='Pre-release requested through the publisher marketplace. An extension with no public prerelease may be offered as stable by the editor.'

    def step_playwright(self):
        base=self.install_js_packages(['playwright'])
        node=self.active['node']['command'][0]
        cli=base/'node_modules/playwright/cli.js'
        self.require(self.run_command([node,cli,'install','chromium'],timeout=1200,label='Install Chromium matched to the selected Playwright build'),'Playwright Chromium installation')
        test="const { chromium }=require('playwright');(async()=>{const b=await chromium.launch({headless:true});try{const p=await b.newPage();await p.goto('data:text/html,<title>WORKBENCH_OK</title>');if(await p.title()!=='WORKBENCH_OK')throw Error('Title mismatch');console.log('BROWSER_OK')}finally{await b.close()}})().catch(e=>{console.error(e.message);process.exit(1)})"
        r=self.require(self.run_command([node,'-e',test],cwd=base,timeout=120,label='Exercise browser launch and local page navigation'),'Browser smoke test')
        if 'BROWSER_OK' not in r.out:raise OperationError('Browser verification marker missing.')
        self.current_result['detail']='Matched Chromium launched and loaded a local test page. No personal browser profile or remote debugging port was used.'

    def step_migrate(self):
        appdata=Path(os.environ.get('APPDATA',str(Path.home())))
        source=appdata/'Code/User';target=appdata/'Code - Insiders/User'
        # Never copy browser tokens, storage databases, or profiles across agents.
        result=merge_missing(source,target)
        self.report['migrations']['editor_files']=result
        old=self.find('code.cmd');new=self.find('code-insiders.cmd')
        installed=[];failed=[]
        if old and new:
            r=self.run_command([old,'--list-extensions'],quiet=True,timeout=120,label='Read existing default-profile extension IDs')
            if r.code==0:
                for line in r.out.splitlines():
                    ext=line.strip()
                    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9-]*\.[A-Za-z0-9][A-Za-z0-9-]*',ext):continue
                    if self.cancel.is_set():raise StopRun('Stopped after current extension migration.')
                    # Existing user-selected extensions only; unknown new extension IDs are not invented.
                    rr=self.run_command([new,'--install-extension',ext,'--pre-release'],timeout=600,label='Migrate existing extension '+ext)
                    (installed if rr.code==0 else failed).append(ext)
            else:failed.append('existing extension inventory unavailable')
        self.report['migrations']['editor_extensions']={'installed':installed,'failed':failed,
            'scope':'Default profile only; other profile extension memberships require editor Settings Sync or manual checks.'}
        self.report['migrations']['retained']=[
            'Original VS Code retained: all profiles, workspaces, logins and project dependencies cannot be proved migrated.',
            'ChatGPT Classic retained until new app sign-in and local-data migration are confirmed.',
            'Old system runtimes/global SDKs retained where other programs may depend on them.',
            'Headroom/RTK/Caveman settings and existing provider configuration preserved.',
        ]
        self.current_result['detail']=f"Copied {len(result['copied'])} configuration files, retained {len(result['conflicts'])} target conflicts. Updated {len(installed)} default-profile extensions. Original programs not deleted speculatively."
        if failed or result['conflicts']:self.current_result['status']='REVIEW_NEEDED'

    def codex_command(self):
        cmd=self.active.get('codex',{}).get('command')
        if not cmd or not all(Path(x).is_file() for x in cmd):raise OperationError('Managed Codex CLI is unavailable.')
        return cmd

    def step_docs_mcp(self):
        home=getattr(self,'codex_home',Path(os.environ.get('CODEX_HOME',str(Path.home()/'.codex'))))
        path=home/'config.toml';config={}
        if path.is_file():
            try:config=tomllib.loads(path.read_text(encoding='utf-8-sig'))
            except (ValueError,OSError) as exc:raise OperationError('Existing Codex config could not be parsed; it was not overwritten.') from exc
        servers=config.get('mcp_servers',{})
        if any(isinstance(v,dict) and v.get('url','').rstrip('/')==DOCS_MCP.rstrip('/') for v in servers.values()):
            self.current_result['detail']='Official docs MCP already configured; no duplicate was added.';return
        if 'openaiDeveloperDocs' in servers:raise OperationError('MCP name openaiDeveloperDocs already belongs to another configuration. Preserved instead of overwritten.')
        r=self.require(self.run_command([*self.codex_command(),'mcp','add','openaiDeveloperDocs','--url',DOCS_MCP],timeout=120,quiet=True,label='Add official read-only docs MCP'),'Docs MCP configuration')
        if not path.is_file():raise OperationError('MCP command returned but config file not found.')
        updated=tomllib.loads(path.read_text(encoding='utf-8-sig'))
        if updated.get('mcp_servers',{}).get('openaiDeveloperDocs',{}).get('url')!=DOCS_MCP:
            raise OperationError('Docs MCP URL was not verified in the resulting config.')
        self.current_result['detail']='Official docs MCP configuration verified. Protocol-level tool access is not established by this config check.'

    def step_dotnet(self):
        # Optional task-specific SDK. The endpoint chooses the newest preview channel at run time.
        index=self.get_json('https://builds.dotnet.microsoft.com/dotnet/release-metadata/releases-index.json')
        channel=choose_dotnet_channel(index)
        script=self.root/'downloads/dotnet-install.ps1'
        self.fetch('https://builds.dotnet.microsoft.com/dotnet/scripts/v1/dotnet-install.ps1',script,max_bytes=4*1024**2)
        sig=self.ps("$s=Get-AuthenticodeSignature -LiteralPath "+ps_literal(script)+"; [pscustomobject]@{Status=$s.Status.ToString();Subject=if($s.SignerCertificate){$s.SignerCertificate.Subject}else{''}} | ConvertTo-Json -Compress",label='Verify Microsoft SDK installer signature')
        self.require(sig,'SDK installer signature check')
        signed=json.loads(sig.out)
        if signed.get('Status')!='Valid' or 'Microsoft' not in signed.get('Subject',''):
            raise OperationError('Daily SDK installer signature could not be verified as Microsoft. Script not executed.')
        target=self.root/'runtimes/dotnet'/channel
        assert_regular_path(target)
        body='& '+ps_literal(script)+' -Channel '+ps_literal(channel)+' -Quality daily -Architecture '+ps_literal((getattr(self,'arch',None) or architecture()))+' -InstallDir '+ps_literal(target)+' -NoPath; if(-not $?) {exit 1}'
        self.require(self.run_command(self.ps_args(body),timeout=1800,label='Install .NET daily SDK from discovered preview channel '+channel),'.NET daily SDK')
        exe=target/'dotnet.exe'
        env={**self.env,'DOTNET_CLI_HOME':str(self.root/'workspace/dotnet-home'),'DOTNET_CLI_TELEMETRY_OPTOUT':'1','DOTNET_SKIP_FIRST_TIME_EXPERIENCE':'1','DOTNET_NOLOGO':'1'}
        check=self.require(self.run_command([exe,'--version'],env=env,cwd=target,timeout=60,label='Verify selected-channel .NET development SDK executable'),'.NET SDK startup')
        version=dotnet_sdk_version(check.out,channel)
        self.activate('dotnet',version,[exe],'Microsoft dotnet-install -Quality daily / '+channel)

    def step_verify(self):
        checks=self.report['checks']
        if self.active.get('codex'):
            cmd=self.codex_command()
            version=self.run_command([*cmd,'--version'],quiet=True,timeout=60,label='Post-install Codex version check')
            checks['codex_version']={'expected':self.active['codex']['version'],'actual_output':redact(version.out),
                                     'passed':version.code==0 and version_matches(version.out,self.active['codex']['version'])}
            auth=self.run_command([*cmd,'login','status'],quiet=True,timeout=60,label='Read Codex sign-in status without exposing credentials')
            checks['codex_sign_in']={'exit_code':auth.code,'state':('ChatGPT login configured' if auth.code==0 and 'chatgpt' in auth.out.lower() else 'Authentication configured; method not confirmed' if auth.code==0 else 'Not confirmed; open Edge Terminal and run codex login'),
                                     'same_account_across_apps':'NOT_VERIFIED'}
            help_result=self.run_command([*cmd,'--help'],quiet=True,timeout=60,label='Discover diagnostic commands supported by installed Codex')
            if re.search(r'(?m)^\s+doctor(?:\s|$)',help_result.out):
                doctor_help=self.run_command([*cmd,'doctor','--help'],quiet=True,timeout=60,label='Discover advertised structured doctor output')
                if doctor_help.code==0 and '--json' in doctor_help.out:
                    doctor=self.run_command([*cmd,'doctor','--json'],quiet=True,timeout=180,label='Run advertised structured Codex doctor diagnostics')
                    try:summary=summarize_codex_doctor(doctor.out)
                    except OperationError as exc:summary={'state':'UNVERIFIED','detail':str(exc)}
                    checks['codex_doctor']={'exit_code':doctor.code,**summary}
                    if summary.get('warning_count') or summary.get('failure_count'):
                        self.log(f"Codex doctor: {summary.get('warning_count',0)} warning checks and {summary.get('failure_count',0)} failure checks; see structured report. No automatic security/history edits.",'warning')
                else:
                    doctor=self.run_command([*cmd,'doctor'],quiet=True,timeout=180,label='Run advertised Codex doctor diagnostics')
                    checks['codex_doctor']={'exit_code':doctor.code,'structured_output':'Not advertised','output_tail':redact(doctor.out[-2500:])}
            else:checks['codex_doctor']={'state':'Not advertised by this build; no guessed diagnostic command executed.'}
        gh=self.find('gh.exe')
        if gh:
            result=self.run_command([gh,'auth','status'],quiet=True,timeout=60,label='Check GitHub CLI sign-in')
            checks['github_sign_in']={'configured':result.code==0,'note':'Account identity not exported. Run gh auth login to connect when absent.'}
        config_path=getattr(self,'codex_home',Path(os.environ.get('CODEX_HOME',str(Path.home()/'.codex'))))/'config.toml'
        if config_path.is_file():
            try:
                config=tomllib.loads(config_path.read_text(encoding='utf-8-sig'))
                summary=[]
                for name,value in config.get('mcp_servers',{}).items():
                    if not isinstance(value,dict):continue
                    server={'name':name,'enabled':value.get('enabled',True),'type':'remote' if 'url' in value else 'local-process','functional_status':'NOT_TESTED'}
                    if value.get('command'):
                        server['command_basename']=Path(value['command']).name
                        server['command_located']=bool(shutil.which(value['command'],path=self.env.get('PATH','')) or Path(value['command']).is_file())
                    summary.append(server)
                checks['mcp_configuration']=summary
                provider=config.get('model_provider','default')
                checks['provider']={'name':provider,'configuration_preserved':True}
                providers=config.get('model_providers',{})
                if isinstance(providers.get(provider),dict):
                    data=providers[provider]
                    url=data.get('base_url') or data.get('openai_base_url')
                    if url:
                        parsed=urllib.parse.urlsplit(str(url))
                        if parsed.hostname in ('localhost','127.0.0.1','::1'):
                            port=parsed.port or (443 if parsed.scheme=='https' else 80)
                            reachable=False
                            with contextlib.suppress(OSError):
                                with socket.create_connection((parsed.hostname,port),timeout=2):reachable=True
                            checks['active_local_provider']={'port':port,'listening':reachable,'service_identity':'NOT_VERIFIED'}
                            if not reachable:self.log('The configured local model provider has no reachable listener. Routing was preserved, not silently replaced.','warning')
            except Exception as exc:checks['codex_config_parse']={'passed':False,'detail':redact(str(exc))}
        # Reachability only: HTTP errors still demonstrate transport, not successful service use.
        endpoints={}
        for name,url in [('ChatGPT','https://chatgpt.com/'),('OpenAI API','https://api.openai.com/v1/models'),('OpenAI sign-in','https://auth.openai.com/'),('Docs MCP',DOCS_MCP)]:
            try:
                request=urllib.request.Request(url,method='HEAD',headers={'User-Agent':'OpenAI-Edge-Workbench/'+VERSION})
                with urllib.request.urlopen(request,timeout=12) as response:
                    endpoints[name]={'http_status':response.status,'transport_reached':True,'auth_or_protocol_verified':False}
            except urllib.error.HTTPError as exc:endpoints[name]={'http_status':exc.code,'transport_reached':True,'auth_or_protocol_verified':False}
            except Exception as exc:endpoints[name]={'transport_reached':False,'detail':redact(str(exc)),'auth_or_protocol_verified':False}
        checks['network']=endpoints
        candidate=self.python_candidate if not self.python_candidate_failed else self.active.get('python')
        if candidate:
            py=candidate['command'][0]
            smoke=self.run_command([py,'-c',"import openai,agents;print('SDK_IMPORT_OK')"],quiet=True,timeout=60,label='Verify Python OpenAI SDK imports')
            checks['python_sdk_imports']={'passed':smoke.code==0 and 'SDK_IMPORT_OK' in smoke.out,'exit_code':smoke.code}
        self.current_result['detail']='Recorded separate checks for binary execution, SDK import, local routing, sign-in and transport. Cloud plugin actions and desktop UI remain unverified.'
        self.current_result['status']='REVIEW_NEEDED'

    def step_live(self):
        cmd=self.codex_command()
        help_result=self.require(self.run_command([*cmd,'exec','--help'],quiet=True,timeout=60,label='Discover read-only live-test flags'),'Codex exec help')
        needed=['--sandbox','--skip-git-repo-check','--output-last-message','--cd']
        if not all(x in help_result.out for x in needed):raise OperationError('Installed Codex does not advertise all required read-only test flags. Model test not attempted.')
        temp=self.root/'smoke-tests'/self.run_id;temp.mkdir(parents=True,exist_ok=True)
        reply=temp/'reply.txt'
        args=[*cmd,'exec','--cd',temp,'--skip-git-repo-check','--sandbox','read-only','--output-last-message',reply]
        if '--ephemeral' in help_result.out:args.append('--ephemeral')
        # Use the real current provider/config, not an unrelated clean default that hides broken routing.
        args+=['Reply exactly CONNECTION_OK. Do not inspect files, call tools, run commands, or include any other text.']
        r=self.run_command(args,quiet=True,timeout=240,label='One read-only Codex request using existing account/provider (uses quota)')
        text=reply.read_text(encoding='utf-8').strip() if reply.is_file() else ''
        passed=r.code==0 and text=='CONNECTION_OK'
        self.report['checks']['codex_live']={'passed':passed,'exit_code':r.code,'expected_marker':'CONNECTION_OK','quota_consumed_or_attempted':True,
            'scope':'One model request through this CLI configuration; not a test of every plugin or desktop feature.'}
        if not passed:raise OperationError('Configured Codex model round trip was not verified. Review sign-in, entitlements, model availability and provider routing. '+redact(r.out[-1500:]))
        self.current_result['detail']='Authenticated model round trip returned the exact expected marker. No API key was created.'

    def step_cleanup(self):
        removed=[];retained=[]
        for family in ('node','npm-host','npm','codex','openai-cli'):
            parent=self.root/'runtimes'/family
            assert_regular_path(parent)
            if not parent.is_dir():continue
            dirs=[p for p in parent.iterdir() if p.is_dir() and not p.is_symlink() and not getattr(p,'is_junction',lambda:False)() and (p/'.workbench-owned.json').is_file()]
            dirs.sort(key=lambda p:p.stat().st_mtime,reverse=True)
            active_paths=[Path(arg).resolve() for tool in self.active.values() for arg in tool.get('command',[]) if Path(arg).is_file()]
            keep=set(dirs[:2])
            for p in dirs:
                if any(a.is_relative_to(p.resolve()) for a in active_paths) or Path(sys.executable).resolve().is_relative_to(p.resolve()):keep.add(p)
            for p in dirs:
                if p in keep:retained.append(p.name);continue
                marker=json.loads((p/'.workbench-owned.json').read_text(encoding='utf-8'))
                if marker.get('owned_by')!=SCHEMA:continue
                if not p.resolve().is_relative_to((self.root/'runtimes').resolve()):raise OperationError('Cleanup path escaped the managed root.')
                assert_regular_path(p)
                if contains_reparse(p):
                    retained.append(p.name);self.log('Retained managed generation containing a junction/symlink: '+p.name,'warning');continue
                try:shutil.rmtree(p);removed.append(family+'/'+p.name)
                except OSError:self.log('An old managed generation is busy; retained: '+p.name,'warning')
        self.current_result.update(removed=removed,retained=retained,detail='Only unused Workbench-owned runtime generations removed; two newest generations retained. System apps, projects and SDKs were not removed.')

    def activate_candidates(self):
        if self.python_candidate and not self.python_candidate_failed:
            py=self.python_candidate['command'][0]
            checked=self.run_command([py,'-c',"import openai,agents;print('SDK_IMPORT_OK')"],quiet=True,timeout=60,label='Verify candidate SDK imports before activation')
            if checked.code == 0 and 'SDK_IMPORT_OK' in checked.out:
                self.active['python']=self.python_candidate
                self.python_candidate=None
            else:
                self.python_candidate_failed=True
                self.log('Candidate Python SDK imports failed. Previous managed Python remains selected.','error')
        if self.js_candidate and not self.js_candidate_failed:
            self.active['javascript']=self.js_candidate
            self.js_candidate=None
        self.save_state()

    def step_report(self):
        self.activate_candidates()
        bin_dir=self.root/'bin';bin_dir.mkdir(parents=True,exist_ok=True)
        def bat_path(text):return str(text).replace('%','%%')
        aliases={'codex':['codex','codex-edge'],'openai-api':['openai-api'],'python':['python-edge'],'node':['node-edge'],'npm':['npm','npm-edge'],'dotnet':['dotnet-edge']}
        for name,names in aliases.items():
            if not self.active.get(name):continue
            command=self.active[name]['command']
            for alias in names:
                line=' '.join('"'+bat_path(x)+'"' for x in command)
                text='@echo off\r\nchcp 65001 >nul\r\n'+line+' %*\r\nexit /b %errorlevel%\r\n'
                (bin_dir/(alias+'.cmd')).write_bytes(text.encode('utf-8'))
        if self.active.get('npm'):
            host,cli=self.active['npm']['command'][:2]
            npx=Path(cli).with_name('npx-cli.js')
            if npx.is_file():
                (bin_dir/'npx.cmd').write_bytes(('@echo off\r\n"'+bat_path(host)+'" "'+bat_path(npx)+'" %*\r\nexit /b %errorlevel%\r\n').encode('utf-8'))
        path_parts=[str(bin_dir)]
        for name in ('python','node'):
            if self.active.get(name):path_parts.append(str(Path(self.active[name]['command'][0]).parent))
        workspace=self.root/'workspace';workspace.mkdir(parents=True,exist_ok=True)
        terminal=self.root/'Open-Edge-Terminal.cmd'
        terminal.write_bytes(('@echo off\r\nchcp 65001 >nul\r\nset "PATH='+';'.join(bat_path(x) for x in path_parts)+';%PATH%"\r\ncd /d "'+bat_path(workspace)+'"\r\necho OpenAI Edge Workbench - this terminal uses managed nightly/preview tools.\r\ncmd.exe /k\r\n').encode('utf-8'))
        tools='OpenAI Edge Workbench managed tools\n\n'+'\n'.join(f"{k}: {v.get('version','')}\n  {' '.join(v.get('command',[]))}" for k,v in self.active.items())
        (workspace/'WORKBENCH-TOOLS.txt').write_text(tools+'\n\nUse the Open-Edge-Terminal launcher. Existing projects and global Codex settings are unchanged.\n',encoding='utf-8')
        if os.name=='nt':
            # Only the tool shim directory is added; no broad global runtime replacement.
            previous=self.root/'private-backups'/'user-path-before-workbench.json'
            assert_regular_path(previous)
            if not previous.exists():
                saved=self.ps_json("[pscustomobject]@{path=[Environment]::GetEnvironmentVariable('Path','User')} | ConvertTo-Json -Compress",label='Back up original user PATH')
                if not isinstance(saved,dict) or 'path' not in saved or (saved['path'] is not None and not isinstance(saved['path'],str)):
                    raise OperationError('User PATH backup has an invalid shape; PATH was not changed.')
                atomic_json(previous,saved)
            try:
                saved=json.loads(previous.read_text(encoding='utf-8'))
            except (OSError,ValueError) as exc:
                raise OperationError('Existing user PATH backup is unreadable; PATH was not changed.') from exc
            if not isinstance(saved,dict) or 'path' not in saved or (saved['path'] is not None and not isinstance(saved['path'],str)):
                raise OperationError('Existing user PATH backup has an invalid shape; PATH was not changed.')
            p=ps_literal(bin_dir)
            code="$p="+p+"; $old=[Environment]::GetEnvironmentVariable('Path','User'); $parts=@($old -split ';' | Where-Object {$_ -and $_.TrimEnd('\\') -ine $p.TrimEnd('\\')}); [Environment]::SetEnvironmentVariable('Path',(($p)+ ';'+($parts -join ';')),'User'); 'USER_PATH_UPDATED'"
            r=self.ps(code,label='Make managed CLI shims available to future user processes')
            self.report['checks']['user_path_update']={'passed':r.code==0 and 'USER_PATH_UPDATED' in r.out,'scope':'Only Workbench bin prepended to USER Path. Machine PATH may still shadow it; use Edge Terminal.'}
            if not self.report['checks']['user_path_update']['passed']:
                raise OperationError('Managed tool launchers were written, but the user PATH update was not confirmed. Use Open-Edge-Terminal.cmd.')
            self.report['checks']['restart_apps']='Close and reopen ChatGPT/editor/terminals to inherit environment changes. No application was force-closed.'
            shortcut_code="$w=New-Object -ComObject WScript.Shell; $desktop=[Environment]::GetFolderPath('Desktop'); $s=$w.CreateShortcut((Join-Path $desktop 'OpenAI Edge Terminal.lnk')); $s.TargetPath="+ps_literal(terminal)+"; $s.WorkingDirectory="+ps_literal(workspace)+"; $s.Save()"
            self.ps(shortcut_code,label='Create Edge Terminal desktop shortcut')
        self.current_result['detail']='Tool launchers and reports written. Use Copy report in the dashboard; review redaction before sharing.'
