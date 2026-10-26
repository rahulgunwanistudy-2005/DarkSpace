"""Explicit public-text patterns. No generative labels or hidden semantic merging."""

import re

from pydantic import BaseModel, ConfigDict


class Rule(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    id: str
    label: str
    pattern: str
    topic: str | None
    question: str


class Codebook(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    id: str
    interpretation: str
    development_source: str
    rules: tuple[Rule, ...]


def assign(text: str, codebook: Codebook) -> tuple[str, ...]:
    return tuple(rule.id for rule in codebook.rules if re.search(rule.pattern, text, re.IGNORECASE))
