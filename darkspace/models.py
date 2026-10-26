from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, model_validator


class Record(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class ModelRef(Record):
    tag: str
    digest: str = Field(pattern=r"^sha256:[0-9a-f]{64}$")
    released: date
    release_source: HttpUrl


class SamplingConfig(Record):
    protocol: Literal["darkspace-evaluation-v1"]
    event: str = Field(min_length=1)
    event_start: date
    brief: str = Field(min_length=20)
    brief_source: HttpUrl
    brief_scope: str = Field(min_length=1)
    models: tuple[ModelRef, ...]
    arm: Literal["event", "control"]
    seed: Literal[42] = 42

    @model_validator(mode="after")
    def check_models(self) -> "SamplingConfig":
        required = {
            "llama3.1:8b-instruct-q4_K_M",
            "qwen2.5:7b-instruct-q4_K_M",
            "mistral:7b-instruct-v0.3-q4_K_M",
            "gemma3:4b-it-q4_K_M",
        }
        if {model.tag for model in self.models} != required or len(self.models) != 4:
            raise ValueError("Protocol v1 requires exactly the four frozen sampling models.")
        if any(model.released >= self.event_start for model in self.models):
            raise ValueError("A model is not released strictly before the event start.")
        return self


class Attempt(Record):
    id: str
    model: ModelRef
    persona: str
    template: Literal[1, 2]
    seed: int
    arm: Literal["event", "control"]
    prompt: str


class Idea(Record):
    idea: str = Field(min_length=12, max_length=1000)
    audience: str = Field(min_length=1)
    problem: str = Field(min_length=1)
    mechanism: str = Field(min_length=1)

    @model_validator(mode="after")
    def word_limit(self) -> "Idea":
        if len(self.idea.split()) > 45:
            raise ValueError("The idea exceeds the frozen 45-word limit.")
        return self


class ProviderResult(Record):
    text: str
    error: str | None = None
    done_reason: str | None = None


class Sample(Record):
    attempt: Attempt
    initial: ProviderResult
    repair: ProviderResult | None = None
    parsed: Idea | None = None
    status: Literal["valid", "repaired", "invalid", "provider_error"]
    parse_error: str | None = None


class AccessEvidence(Record):
    event: str
    authorized_route: HttpUrl
    license_evidence: str = Field(min_length=20)
    historical_license_verified: bool
    robots_verified: bool
    pre_event_brief_verified: bool
    protocol_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")

    @model_validator(mode="after")
    def access_gate(self) -> "AccessEvidence":
        if not all(
            [self.historical_license_verified, self.robots_verified, self.pre_event_brief_verified]
        ):
            raise ValueError(
                "Historical collection is blocked until every access gate is verified."
            )
        return self
