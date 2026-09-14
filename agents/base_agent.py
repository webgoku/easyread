from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any, Type, TypeVar

import anthropic
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)

PROMPTS_DIR = Path(__file__).parent / "prompts"


def _extract_json(text: str) -> str:
    text = re.sub(r"```(?:json)?\s*", "", text).replace("```", "")
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError(f"Nessun oggetto JSON trovato nella risposta del modello:\n{text}")
    return text[start : end + 1]


class BaseAgent:
    def __init__(self, model: str | None = None):
        self.model = model or os.getenv("ANTHROPIC_MODEL", "claude-haiku-4-5-20251001")
        self.client = anthropic.Anthropic(
            api_key=os.environ["ANTHROPIC_API_KEY"],
        )

    def _load_prompt(self, name: str) -> str:
        return (PROMPTS_DIR / f"{name}.txt").read_text(encoding="utf-8")

    def _chat(self, system: str, user: str, **kwargs: Any) -> str:
        message = self.client.messages.create(
            model=self.model,
            max_tokens=2048,
            system=system,
            messages=[{"role": "user", "content": user}],
            **kwargs,
        )
        return message.content[0].text

    def _chat_json(self, system: str, user: str, schema: Type[T], **kwargs: Any) -> T:
        system_with_schema = (
            f"{system}\n\n"
            f"Rispondi SOLO con un oggetto JSON valido che rispetti questo schema:\n"
            f"{json.dumps(schema.model_json_schema(), ensure_ascii=False, indent=2)}\n\n"
            f"Non aggiungere testo prima o dopo il JSON. Non usare markdown o backtick."
        )
        raw = self._chat(system_with_schema, user, **kwargs)
        return schema.model_validate_json(_extract_json(raw))
