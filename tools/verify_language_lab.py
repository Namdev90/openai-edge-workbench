"""Verify Language Lab metadata, original fixtures and narrowly scoped attributes.

Offline and standard-library-only. Native GitHub stats must be observed separately
after publication; this check does not impersonate GitHub's deployed Linguist.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
from build_language_lab import LAB, ROOT, build, generated_files, load_catalog, regular_path


def verify(root=ROOT,check_git=True):
    root=Path(root);catalog=load_catalog(root);folder=root/LAB
    result=build(root,check=True)
    refreshed,expected=generated_files(catalog)
    if catalog!=refreshed:raise ValueError('Catalog byte counts differ from generated fixtures.')
    fixtures=folder/'fixtures';regular_path(fixtures)
    actual=[]
    for path in fixtures.iterdir():
        regular_path(path)
        if not path.is_file():raise ValueError('Only regular reference files belong in the fixture directory.')
        actual.append(path.relative_to(folder).as_posix())
    if set(actual)!={row['fixture'] for row in catalog['languages']}:
        raise ValueError('Fixture files do not exactly cover the catalog.')
    for row in catalog['languages']:
        data=expected[row['fixture']]
        if not data or b'\r' in data or b'\0' in data or len(data)!=row['fixture_bytes']:
            raise ValueError('Invalid fixture encoding or byte correspondence.')
        if b'Program validity: not claimed.' not in data or b'No third-party example program was copied.' not in data:
            raise ValueError('A fixture lost its transparent reference scope.')
    if check_git:
        paths=[f"{LAB}/{row['fixture']}" for row in catalog['languages']]
        names=['linguist-language','linguist-detectable','linguist-generated','linguist-vendored','linguist-documentation']
        process=subprocess.run(['git','check-attr','-z','--stdin',*names],cwd=root,
                               input=('\0'.join(paths)+'\0').encode(),capture_output=True,timeout=20,check=True)
        pieces=process.stdout.decode('utf-8').split('\0')
        if pieces[-1]!='' or (len(pieces)-1)%3:raise ValueError('Git returned malformed attributes evidence.')
        observed={}
        for at in range(0,len(pieces)-1,3):observed[pieces[at],pieces[at+1]]=pieces[at+2]
        for row,path in zip(catalog['languages'],paths):
            for name,value in zip(names,[row['override_alias'],'true','false','false','false']):
                if observed.get((path,name))!=value:raise ValueError('Effective Git attributes differ from the scoped experiment.')
        presentation=subprocess.run(['git','check-attr','-z','--stdin','linguist-generated','linguist-documentation'],cwd=root,
                                    input=b'language-stat-experiment/index.html\0language-stat-experiment/atlas.svg\0language-stat-experiment/catalog.json\0language-stat-experiment/README.md\0',
                                    capture_output=True,timeout=20,check=True)
        values=presentation.stdout.decode('utf-8').split('\0')
        for at in range(0,len(values)-1,3):
            name,attribute,value=values[at:at+3]
            expected_value='true' if attribute=='linguist-generated' or name.endswith('/README.md') else 'unspecified'
            if value!=expected_value:raise ValueError('Generated presentation or documentation is not excluded from the fixture experiment.')
        # Verify the nested rules leave actual application source unclassified.
        outside=subprocess.run(['git','check-attr','-z','--stdin',*names],cwd=root,
                               input=b'source/engine.py\0source/app.js\0Setup.ps1\0',capture_output=True,timeout=20,check=True)
        values=outside.stdout.decode('utf-8').split('\0')
        if any(values[at+2]!='unspecified' for at in range(0,len(values)-1,3)):
            raise ValueError('Language Lab classification escaped into application paths.')
    result['catalog_sha256']=hashlib.sha256(expected['catalog.json']).hexdigest()
    result['native_github_statistics']='Not observed by this offline verifier; grouped deployed results require the repository languages API.'
    return result


if __name__=='__main__':print(json.dumps(verify(),indent=2,sort_keys=True))
