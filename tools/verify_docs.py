"""Verify active documentation links, assets and proposal/catalog identity."""
from pathlib import Path
import re, urllib.parse, xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
if __name__=='__main__':
    files=[ROOT/name for name in ('README.md','CONTRIBUTING.md','SECURITY.md','FEATURE-PROPOSALS.md')]
    files+=list((ROOT/'docs').glob('*.md'))
    checked=0
    for path in files:
        content=path.read_text(encoding='utf-8')
        links=re.findall(r'\]\(([^\s)]+)(?:\s+[^)]*)?\)',content)+re.findall(r'(?:src|href)="([^"]+)"',content)
        for link in links:
            parsed=urllib.parse.urlsplit(link)
            if parsed.scheme or not parsed.path:continue
            target=(path.parent/urllib.parse.unquote(parsed.path)).resolve()
            assert target.is_relative_to(ROOT) and target.exists(),f'Broken repository link in {path.relative_to(ROOT)}: {link}'
            checked+=1
    proposal=(ROOT/'FEATURE-PROPOSALS.md').read_text(encoding='utf-8')
    ids=re.findall(r'^\| (F\d{3}) \|',proposal,re.M)
    assert ids==[f'F{i:03}' for i in range(1,101)],'Roadmap IDs were lost or conflated with the implemented catalog.'
    for path in (ROOT/'docs/assets').glob('*.svg'):ET.parse(path)
    for path in (ROOT/'docs/assets').glob('*.png'):assert path.read_bytes().startswith(b'\x89PNG\r\n\x1a\n'),f'Invalid screenshot: {path.name}'
    for path in (ROOT/'docs/assets').glob('*.jpg'):
        data=path.read_bytes()
        assert data.startswith(b'\xff\xd8\xff') and data.endswith(b'\xff\xd9'),f'Invalid screenshot: {path.name}'
    print(f'{checked} active documentation links, SVG/PNG/JPEG assets and 100 separate roadmap IDs verified.')
