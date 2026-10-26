"""Download only the four public protocol models, checking pinned manifest digests."""

import hashlib
import json
import urllib.request

MODELS = (
    (
        "llama3.1:8b-instruct-q4_K_M",
        "46e0c10c039e019119339687c3c1757cc81b9da49709a3b3924863ba87ca666e",
    ),
    (
        "qwen2.5:7b-instruct-q4_K_M",
        "845dbda0ea48ed749caafd9e6037047aa19acfcfd82e704d7ca97d631a0b697e",
    ),
    (
        "mistral:7b-instruct-v0.3-q4_K_M",
        "6577803aa9a036369e481d648a2baebb381ebc6e897f2bb9a766a2aa7bfbc1cf",
    ),
    ("gemma3:4b-it-q4_K_M", "68ceab7e468a31c988b44d5a4984a0e21f58c4f7158c6ce29c1804babac38df7"),
)


for name, expected in MODELS:
    family, tag = name.split(":", 1)
    manifest_url = f"https://registry.ollama.ai/v2/library/{family}/manifests/{tag}"
    with urllib.request.urlopen(manifest_url, timeout=60) as response:
        raw_manifest = response.read()
    if hashlib.sha256(raw_manifest).hexdigest() != expected:
        raise RuntimeError(f"Registry manifest changed: {name}; refusing substitution.")
    print(f"Downloading pinned public weights: {name}", flush=True)
    query = urllib.request.Request(
        "http://127.0.0.1:11434/api/pull",
        data=json.dumps({"model": name, "stream": False}).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(query, timeout=1200) as response:
        result = json.load(response)
    if result.get("status") != "success":
        raise RuntimeError(f"Public weight download failed: {name}: {result}")
    with urllib.request.urlopen("http://127.0.0.1:11434/api/tags", timeout=10) as response:
        actual = next(
            (item["digest"] for item in json.load(response)["models"] if item["name"] == name), None
        )
    if actual is None or actual.removeprefix("sha256:") != expected:
        raise RuntimeError(f"Downloaded model digest mismatch: {name}: {actual}")
    print(f"Verified public weights: {name}", flush=True)

print(
    "All four public models are ready. No inference or backtest has run in this step.", flush=True
)
