import hashlib
import json
from pathlib import Path

from pydantic import Field

from darkspace.models import Record


class ProtocolLock(Record):
    protocol: str
    files: dict[str, str]
    sha256: str = Field(pattern=r"^[0-9a-f]{64}$")


def file_digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def freeze(root: Path, paths: tuple[str, ...]) -> ProtocolLock:
    files = {name: file_digest(root / name) for name in sorted(paths)}
    encoded = json.dumps(files, sort_keys=True, separators=(",", ":")).encode()
    return ProtocolLock(
        protocol="darkspace-evaluation-v1", files=files, sha256=hashlib.sha256(encoded).hexdigest()
    )


def verify(root: Path, lock: ProtocolLock) -> str:
    for name in lock.files:
        resolved = (root / name).resolve()
        if not resolved.is_relative_to(root.resolve()):
            raise ValueError("Protocol lock contains a path outside the public project.")
    current = freeze(root, tuple(lock.files))
    if current != lock:
        raise ValueError(
            "Frozen protocol inputs changed. Record a new protocol before generating or collecting data."
        )
    return lock.sha256
