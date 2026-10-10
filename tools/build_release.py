"""Build a deterministic self-contained launcher and its readable-source manifest."""
from pathlib import Path
import base64, hashlib, io, json, re, textwrap, zipfile
root=Path(__file__).resolve().parents[1]
version=re.search(r"(?m)^VERSION = '([^']+)'$",(root/'source/engine.py').read_text())[1]
files=sorted(p for p in (root/'source').rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix in {'.py','.ps1','.js','.html','.css','.md'})
payload=io.BytesIO()
with zipfile.ZipFile(payload,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    for p in files:
        info=zipfile.ZipInfo(p.relative_to(root/'source').as_posix(),date_time=(2026,10,10,0,0,0))
        info.compress_type=zipfile.ZIP_DEFLATED
        z.writestr(info,p.read_bytes())
data=payload.getvalue();digest=hashlib.sha256(data).hexdigest()
loader=(root/'tools/launcher-loader.ps1').read_text().replace('__PAYLOAD_SHA256__',digest).replace('__RELEASE_VERSION__',version)
encoded=base64.b64encode(loader.encode('utf-16le')).decode()
line='"%SystemRoot%\\System32\\WindowsPowerShell\\v1.0\\powershell.exe" -NoLogo -NoProfile -OutputFormat Text -STA -ExecutionPolicy Bypass -EncodedCommand '+encoded
assert len(line)<8191,'CMD command-line limit exceeded'
header='@echo off\r\nsetlocal DisableDelayedExpansion\r\nset "EDGE_SELF=%~f0"\r\n'+line+'\r\nexit /b %errorlevel%\r\n\r\n::EDGE_PAYLOAD\r\n'
cmd=(header+'\r\n'.join(textwrap.wrap(base64.b64encode(data).decode(),76))+'\r\n').encode('ascii')
(root/'OpenAI-Edge-Workbench.cmd').write_bytes(cmd)
stage=(root/'tools/first-stage.ps1').read_text()
stage_encoded=base64.b64encode(stage.encode('utf-16le')).decode()
stage_line='"%SystemRoot%\\System32\\WindowsPowerShell\\v1.0\\powershell.exe" -NoProfile -OutputFormat Text -STA -ExecutionPolicy Bypass -EncodedCommand '+stage_encoded
assert len(stage_line)<8191,'Setup CMD command-line limit exceeded'
setup_cmd=('@echo off\r\nsetlocal DisableDelayedExpansion\r\n'+stage_line+'\r\nexit /b %errorlevel%\r\n').encode('ascii')
(root/'OpenAI-Edge-Workbench-Setup.cmd').write_bytes(setup_cmd)
manifest={'schema':1,'version':version,'launcherSha256':hashlib.sha256(cmd).hexdigest(),'payloadSha256':digest,'setupSha256':hashlib.sha256((root/'Setup.ps1').read_bytes()).hexdigest(),'setupLauncherSha256':hashlib.sha256(setup_cmd).hexdigest(),'sourceFiles':{p.relative_to(root/'source').as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in files}}
(root/'release.json').write_bytes((json.dumps(manifest,indent=2)+'\n').encode())
print(f'Built {len(files)} source files; launcher {len(cmd)} bytes; command line {len(line)} characters')
