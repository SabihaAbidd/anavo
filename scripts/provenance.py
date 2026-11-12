"""Bind validation evidence to runtime source, independently of Git write access."""
import hashlib
from pathlib import Path


def source_fingerprint(root=None):
    root=Path(root) if root is not None else Path(__file__).resolve().parent.parent
    files=[root/"requirements.txt",root/"requirements-lock.txt"]
    for folder in ("src","backend","scripts","tests"):
        files.extend((root/folder).rglob("*.py"))
    digest=hashlib.sha256()
    for path in sorted(files,key=lambda p:p.relative_to(root).as_posix()):
        if path.is_file():
            digest.update(path.relative_to(root).as_posix().encode())
            digest.update(b"\0")
            # Checkout newline conversion must not make CI evidence incomparable.
            digest.update(path.read_bytes().replace(b"\r\n",b"\n"))
            digest.update(b"\0")
    return digest.hexdigest()
