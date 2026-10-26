"""Public-data compute only. Run in the authorized free Colab GPU notebook."""

import hashlib
import os
import shutil
import subprocess
import sys
import tarfile
import time
import urllib.request
from pathlib import Path

VERSION = "0.40.11"
URL = f"https://github.com/ollama/ollama/releases/download/v{VERSION}/ollama-linux-amd64.tar.zst"
SHA256 = "7bedab90dd122661be78798e9f0edf37fccf0cccf2699d2c58ea1a3afdc04b6d"
ROOT = Path("/content/darkspace-public")


def main() -> None:
    if not Path("/content").is_dir():
        raise SystemExit("This bootstrap is for the authorized Colab runtime only.")
    subprocess.run(
        ["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader"], check=True
    )
    if shutil.disk_usage("/content").free < 25_000_000_000:
        raise SystemExit("At least 25 GB free disk is required for public model weights.")
    ROOT.mkdir(exist_ok=True)
    archive = ROOT / "ollama.tar.zst"
    if not archive.exists():
        print("Downloading the pinned official public-model runtime (1.51 GB).", flush=True)
        urllib.request.urlretrieve(URL, archive)
    with archive.open("rb") as stream:
        actual = hashlib.file_digest(stream, "sha256").hexdigest()
    if actual != SHA256:
        raise SystemExit("Runtime checksum mismatch; refusing to run it.")
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "--quiet", "zstandard==0.25.0"], check=True
    )
    import zstandard

    with (
        archive.open("rb") as stream,
        zstandard.ZstdDecompressor().stream_reader(stream) as reader,
        tarfile.open(fileobj=reader, mode="r|") as bundle,
    ):
        bundle.extractall(ROOT, filter="data")
    environment = {
        **os.environ,
        "OLLAMA_HOST": "127.0.0.1:11434",
        "OLLAMA_MODELS": str(ROOT / "models"),
        "OLLAMA_NUM_PARALLEL": "1",
        "OLLAMA_MAX_LOADED_MODELS": "1",
    }
    with (ROOT / "ollama.log").open("ab") as log:
        subprocess.Popen(
            [str(ROOT / "bin/ollama"), "serve"], env=environment, stdout=log, stderr=log
        )
    for _ in range(30):
        try:
            with urllib.request.urlopen(
                "http://127.0.0.1:11434/api/version", timeout=2
            ) as response:
                print("Public runtime ready:", response.read().decode(), flush=True)
                print("No personal ideas, profiles or answers have been supplied.", flush=True)
                return
        except OSError:
            time.sleep(1)
    raise SystemExit("Public model runtime did not start; inspect the local runtime log.")


if __name__ == "__main__":
    main()
