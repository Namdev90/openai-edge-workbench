"""Stage reproducible release assets without replacing an existing output path."""
from pathlib import Path
import argparse
import base64
import hashlib
import io
import json
import stat
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
COPY_NAMES = (
    'OpenAI-Edge-Workbench-Setup.cmd', 'OpenAI-Edge-Workbench.cmd',
    'Setup.ps1', 'Run.ps1', 'SETUP.md',
)
SOURCE_NAME = 'OpenAI-Edge-Workbench-Source.zip'
CHECKSUM_NAME = 'SHA256SUMS.txt'


def output_path(output):
    """Require a new destination and preserve symlink/junction targets."""
    destination = Path(output).expanduser().absolute()
    for candidate in (destination, *destination.parents):
        try:
            info = candidate.lstat()
        except FileNotFoundError:
            continue
        # lstat's Windows attributes also cover junctions on Python 3.11,
        # which does not yet provide Path.is_junction().
        reparse = getattr(info, 'st_file_attributes', 0) & getattr(stat, 'FILE_ATTRIBUTE_REPARSE_POINT', 0x400)
        if stat.S_ISLNK(info.st_mode) or reparse:
            raise ValueError('Release output must not use a symlink or junction: ' + str(candidate))
    if destination.exists():
        raise FileExistsError('Release output already exists; choose a new directory: ' + str(destination))
    if not destination.parent.is_dir():
        raise ValueError('Create the release output parent directory first: ' + str(destination.parent))
    return destination


def stage_release(output, root=ROOT):
    """Validate inputs before creating a fresh, exclusive output directory.

    Individual artifacts also use exclusive creation. A disk/write error may
    leave a partial new directory. Leave it for inspection instead of deleting
    potentially modified local files; never call it a completed release.
    """
    root = Path(root).resolve()
    destination = output_path(output)
    # Isolated mode prevents PYTHONOPTIMIZE from disabling verifier assertions.
    subprocess.run([sys.executable, '-I', str(root / 'tools/verify_payload.py')], check=True)
    manifest = json.loads((root / 'release.json').read_text(encoding='utf-8'))
    assets = {name: (root / name).read_bytes() for name in COPY_NAMES}
    for name, key in (
        ('OpenAI-Edge-Workbench.cmd', 'launcherSha256'),
        ('OpenAI-Edge-Workbench-Setup.cmd', 'setupLauncherSha256'),
        ('Setup.ps1', 'setupSha256'),
    ):
        if hashlib.sha256(assets[name]).hexdigest() != manifest[key]:
            raise ValueError('Release input changed after verification: ' + name)
    marker = b'\r\n::EDGE_PAYLOAD\r\n'
    launcher = assets['OpenAI-Edge-Workbench.cmd']
    if launcher.count(marker) != 1:
        raise ValueError('Expected exactly one embedded payload marker.')
    payload = base64.b64decode(b''.join(launcher.split(marker, 1)[1].split()), validate=True)
    if hashlib.sha256(payload).hexdigest() != manifest['payloadSha256']:
        raise ValueError('Embedded payload checksum mismatch.')
    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
        if archive.testzip() is not None:
            raise ValueError('Embedded source archive is corrupt.')
    assets[SOURCE_NAME] = payload
    # Retain the established checksum ordering and exact seven-asset contract.
    checksum_names = (*COPY_NAMES[:2], SOURCE_NAME, *COPY_NAMES[2:])
    assets[CHECKSUM_NAME] = ''.join(
        hashlib.sha256(assets[name]).hexdigest() + '  ' + name + '\n'
        for name in checksum_names
    ).encode('utf-8')

    # Repeat checks after verification, then claim the directory exclusively.
    output_path(destination)
    destination.mkdir()
    for name, content in assets.items():
        with (destination / name).open('xb') as stream:
            stream.write(content)
    return manifest['version']


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True,
                        help='New release directory; its parent must already exist.')
    args = parser.parse_args(argv)
    try:
        version = stage_release(args.output)
    except (OSError, ValueError, KeyError, zipfile.BadZipFile, subprocess.CalledProcessError) as error:
        parser.exit(1, 'Release packaging failed: ' + str(error) + '\n'
                    'No existing output is replaced. A failed write can leave a partial new directory; '
                    'inspect it and choose a fresh output path before retrying.\n')
    print(f'Staged seven release assets for {version}.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
