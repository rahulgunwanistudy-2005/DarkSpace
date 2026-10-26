import hashlib
import json
import random
import re
from typing import Literal

from pydantic import BaseModel, ValidationError

from darkspace.models import Attempt, Idea, ProviderResult, Sample, SamplingConfig

SYSTEM = (
    "You propose one feasible beginner hackathon project. Do not name existing projects or claim "
    "knowledge of submissions. Return only JSON with keys idea, audience, problem, mechanism. "
    "idea is one sentence of at most 45 words. The other values are short descriptions of that "
    "sentence. Do not include commentary."
)
CONTROL = "I'm a beginner. Give me an app idea I can build with an AI coding agent."
PERSONAS = (
    "student",
    "teacher",
    "healthcare worker",
    "accessibility advocate",
    "community volunteer",
    "small business owner",
    "researcher",
    "designer",
    "software developer",
    "local government worker",
    "caregiver",
    "job seeker",
)
SEEDS = (11, 23, 47, 89)
REPAIR = (
    "Repair this text into the required JSON shape without adding or changing the idea. "
    "Return only JSON."
)


def canonical(value: BaseModel | dict[str, object] | list[object]) -> bytes:
    content = value.model_dump(mode="json") if isinstance(value, BaseModel) else value
    return json.dumps(
        content, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode()


def digest(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def prompt(persona: str, task: str, template: Literal[1, 2]) -> str:
    if template == 1:
        return (
            f"Builder perspective: {persona}.\nTask: {task}\n"
            "Propose one project this builder could make with an AI coding agent."
        )
    return (
        f"Consider a beginner building from the perspective of a {persona}.\n"
        f"Their task is: {task}\n"
        "What single project could they implement with an AI coding agent?"
    )


def attempts(config: SamplingConfig) -> tuple[Attempt, ...]:
    task = config.brief if config.arm == "event" else CONTROL
    result = []
    for model in config.models:
        for persona in PERSONAS:
            for template in (1, 2):
                for seed in SEEDS:
                    typed_template: Literal[1, 2] = 1 if template == 1 else 2
                    user_prompt = prompt(persona, task, typed_template)
                    identity: dict[str, object] = {
                        "model": model.digest,
                        "persona": persona,
                        "template": template,
                        "seed": seed,
                        "arm": config.arm,
                        "prompt": user_prompt,
                    }
                    result.append(
                        Attempt(
                            id=digest(canonical(identity)),
                            model=model,
                            persona=persona,
                            template=typed_template,
                            seed=seed,
                            arm=config.arm,
                            prompt=user_prompt,
                        )
                    )
    return tuple(result)


def request_payload(attempt: Attempt, repair_text: str | None = None) -> dict[str, object]:
    return {
        "model": attempt.model.tag,
        "system": SYSTEM,
        "prompt": attempt.prompt if repair_text is None else f"{REPAIR}\n\n{repair_text}",
        "format": "json",
        "stream": False,
        "keep_alive": "5m",
        "options": {
            "seed": attempt.seed,
            "temperature": 0.9 if repair_text is None else 0,
            "top_p": 0.95,
            "num_predict": 220,
            "num_ctx": 4096,
        },
    }


def parse(result: ProviderResult) -> tuple[Idea | None, str | None]:
    if result.error is not None:
        return None, result.error
    if result.done_reason == "length":
        return None, "Output reached its token limit."
    try:
        return Idea.model_validate_json(result.text), None
    except ValidationError as error:
        return None, str(error)


def assemble(
    attempt: Attempt, initial: ProviderResult, repair: ProviderResult | None = None
) -> Sample:
    parsed, error = parse(initial)
    if parsed is not None:
        return Sample(attempt=attempt, initial=initial, parsed=parsed, status="valid")
    if initial.error is not None:
        return Sample(attempt=attempt, initial=initial, status="provider_error", parse_error=error)
    if repair is not None:
        fixed, repair_error = parse(repair)
        original_match = re.search(r'"idea"\s*:\s*("(?:[^"\\]|\\.)*")', initial.text)
        original_idea: object = None
        if original_match is not None:
            original_idea = json.loads(original_match.group(1))
        if fixed is not None and fixed.idea != original_idea:
            fixed, repair_error = (
                None,
                "Repair could not be verified to preserve the original idea exactly.",
            )
        return Sample(
            attempt=attempt,
            initial=initial,
            repair=repair,
            parsed=fixed,
            status="repaired" if fixed is not None else "invalid",
            parse_error=repair_error,
        )
    return Sample(attempt=attempt, initial=initial, status="invalid", parse_error=error)


def ordered_arms() -> tuple[str, str]:
    arms = ["event", "control"]
    random.Random(42).shuffle(arms)
    return arms[0], arms[1]
