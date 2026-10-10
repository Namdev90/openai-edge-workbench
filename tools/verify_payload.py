from pathlib import Path
from hashlib import sha256
from zipfile import ZipFile
import base64
import io

root=Path(__file__).resolve().parents[1]
cmd=(root/"OpenAI-Edge-Workbench.cmd").read_bytes()
mark=b"\r\n::EDGE_PAYLOAD\r\n"
assert cmd.count(mark)==1, "Launcher payload marker count mismatch"
data=base64.b64decode(b"".join(cmd.split(mark)[1].split()),validate=True)
assert sha256(data).hexdigest()=="009a3889e944bc8923c68a3411af47e37c882a65211002e8dfb7aa293a2c7f0a", "Payload checksum mismatch"
with ZipFile(io.BytesIO(data)) as z:
    assert z.testzip() is None
    names=z.namelist()
    assert len(names)==15
    for name in names:
        assert ".." not in Path(name).parts and not name.startswith("/")
        assert z.read(name)==(root/"source"/name).read_bytes(), "Source differs: "+name
print("15 embedded payload source files verified.")
