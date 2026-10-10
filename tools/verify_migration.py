from pathlib import Path
import hashlib,json
root=Path(__file__).resolve().parents[1]
audit=json.loads((root/'migration-audit.json').read_text())
count=0
for record in audit['records']:
    for f in record['files']:
        path=root/f['archivePath']
        assert path.resolve().is_relative_to((root/'legacy').resolve())
        assert hashlib.sha256(path.read_bytes()).hexdigest()==f['sha256'],f['archivePath']
        count+=1
print(f'{count} historical source files match independently audited SHA256 hashes.')
draft=root/'legacy/maintenance-planning/Workbench-UNTESTED-implementation.patch'
assert hashlib.sha256(draft.read_bytes()).hexdigest()=='1232193732a6572e9809da1ce3d2f24ebc19d0ad9ab3b4efcef4042c5ff6bbac','Archived maintenance draft changed.'
print('One separate untested maintenance draft is preserved byte-for-byte outside executable source.')
