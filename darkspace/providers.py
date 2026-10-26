import json
import urllib.request

from pydantic import BaseModel

from darkspace.models import ModelRef, ProviderResult


class GenerateResponse(BaseModel):
    response: str
    done_reason: str | None = None


class Tag(BaseModel):
    name: str
    digest: str


class Tags(BaseModel):
    models: tuple[Tag, ...]


class Version(BaseModel):
    version: str


def request(path: str, payload: dict[str, object] | None = None, timeout: int = 600) -> bytes:
    body = None if payload is None else json.dumps(payload).encode()
    query = urllib.request.Request(
        "http://127.0.0.1:11434" + path,
        data=body,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(query, timeout=timeout) as response:
        result = response.read()
    if not isinstance(result, bytes):
        raise TypeError("The public inference provider returned a non-byte response.")
    return result


def runtime_version() -> str:
    return Version.model_validate_json(request("/api/version", timeout=10)).version


def verify_model(model: ModelRef) -> None:
    tags = Tags.model_validate_json(request("/api/tags", timeout=10))
    actual = next((tag.digest for tag in tags.models if tag.name == model.tag), None)
    if actual is None or actual.removeprefix("sha256:") != model.digest.removeprefix("sha256:"):
        raise ValueError(
            f"Pinned model missing or digest changed: {model.tag}. Pull and verify it first."
        )


def generate(payload: dict[str, object]) -> ProviderResult:
    try:
        result = GenerateResponse.model_validate_json(request("/api/generate", payload))
        return ProviderResult(text=result.response, done_reason=result.done_reason)
    except (OSError, ValueError, TypeError) as error:
        return ProviderResult(text="", error=f"{type(error).__name__}: {error}")
