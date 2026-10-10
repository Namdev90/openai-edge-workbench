"""Regenerate the source manifest after edits and before publishing."""
from pathlib import Path
import hashlib,json
root=Path(__file__).resolve().parent
files=['Edge.ps1','install.ps1','catalog.json','README.md','IMPLEMENTATION.md','Build-Release.py','tests/Test-Edge.ps1','tests/test_distribution.py']
manifest={'schema':2,'version':'2.0.0','files':{n:hashlib.sha256((root/n).read_bytes()).hexdigest() for n in files}}
(root/'release.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
print(json.dumps(manifest,indent=2))
