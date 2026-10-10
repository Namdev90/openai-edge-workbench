from pathlib import Path, PurePosixPath
from hashlib import sha256
from zipfile import ZipFile
import base64, io, json
root=Path(__file__).resolve().parents[1]
manifest=json.loads((root/'release.json').read_text())
cmd=(root/'OpenAI-Edge-Workbench.cmd').read_bytes()
assert sha256(cmd).hexdigest()==manifest['launcherSha256'],'Launcher checksum mismatch'
assert sha256((root/'Setup.ps1').read_bytes()).hexdigest()==manifest['setupSha256'],'Setup checksum mismatch'
mark=b'\r\n::EDGE_PAYLOAD\r\n'
assert cmd.count(mark)==1,'Payload marker mismatch'
data=base64.b64decode(b''.join(cmd.split(mark)[1].split()),validate=True)
assert sha256(data).hexdigest()==manifest['payloadSha256'],'Payload checksum mismatch'
with ZipFile(io.BytesIO(data)) as z:
    assert z.testzip() is None
    assert len(z.namelist())==len(set(z.namelist()))
    assert set(z.namelist())==set(manifest['sourceFiles'])
    for name in z.namelist():
        assert '..' not in PurePosixPath(name).parts and not name.startswith('/') and ':' not in name and '\\' not in name
        assert z.read(name)==(root/'source'/name).read_bytes(),'Source differs: '+name
        assert sha256(z.read(name)).hexdigest()==manifest['sourceFiles'][name]
print(f'{len(manifest["sourceFiles"])} embedded source files verified byte-for-byte.')
first=root/'OpenAI-Edge-Workbench-Setup.cmd'
if first.exists():
    line=next(s for s in first.read_text().splitlines() if '-EncodedCommand ' in s)
    decoded=base64.b64decode(line.split('-EncodedCommand ',1)[1]).decode('utf-16le')
    assert decoded==(root/'tools/first-stage.ps1').read_text(),'Setup CMD differs from readable first-stage source'
    assert len(line)<8191,'CMD command line too long'
    print('Setup CMD matches readable commit-pinned first-stage source.')
