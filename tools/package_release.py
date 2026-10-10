"""Stage reproducible release assets from an already verified repository build."""
from pathlib import Path
import argparse, base64, hashlib, json, shutil, subprocess, sys, zipfile, io
ROOT=Path(__file__).resolve().parents[1]

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    subprocess.run([sys.executable,str(ROOT/'tools/verify_payload.py')],check=True)
    manifest=json.loads((ROOT/'release.json').read_text());out=args.output.resolve();out.mkdir(parents=True,exist_ok=True)
    for name in ('OpenAI-Edge-Workbench-Setup.cmd','OpenAI-Edge-Workbench.cmd','Setup.ps1','Run.ps1','SETUP.md'):
        shutil.copyfile(ROOT/name,out/name)
    payload=base64.b64decode(b''.join((ROOT/'OpenAI-Edge-Workbench.cmd').read_bytes().split(b'\r\n::EDGE_PAYLOAD\r\n')[1].split()),validate=True)
    assert hashlib.sha256(payload).hexdigest()==manifest['payloadSha256']
    with zipfile.ZipFile(io.BytesIO(payload)) as archive:assert archive.testzip() is None
    (out/'OpenAI-Edge-Workbench-Source.zip').write_bytes(payload)
    names=['OpenAI-Edge-Workbench-Setup.cmd','OpenAI-Edge-Workbench.cmd','OpenAI-Edge-Workbench-Source.zip','Setup.ps1','Run.ps1','SETUP.md']
    (out/'SHA256SUMS.txt').write_text(''.join(hashlib.sha256((out/name).read_bytes()).hexdigest()+'  '+name+'\n' for name in names),encoding='utf-8',newline='\n')
    print(f'Staged seven release assets for {manifest["version"]}.')
