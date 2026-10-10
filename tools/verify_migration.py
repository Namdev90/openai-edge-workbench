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
