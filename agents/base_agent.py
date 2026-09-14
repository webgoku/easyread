from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any, Type, TypeVar

from openai import OpenAI
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


def _extract_json(text: str) -> str:
    """Estrae il primo oggetto JSON da un testo che potrebbe contenerlo tra backtick o testo libero."""
    # Rimuovi blocchi markdown ```json ... ```
    text = re.sub(r"```(?:json)?\s*", "", text).replace("```", "")
    # Trova il primo { e l'ultimo } bilanciati
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError(f"Nessun oggetto JSON trovato nella risposta del modello:\n{text}")
    return text[start : end + 1]

PROMPTS_DIR = Path(__file__).parent / "prompts"

DEFAULT_MODEL = os.getenv("OPENROUTER_MODEL", "mistralai/mistral-7b-instruct")


class BaseAgent:
    def __init__(self, model: str = DEFAULT_MODEL):
        self.model = model
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.environ["OPENROUTER_API_KEY"],
            default_headers={
                "HTTP-Referer": "https://github.com/webgoku/easyread",
                "X-Title": "EasyRead",
            },
        )

    def _load_prompt(self, name: str) -> str:
        return (PROMPTS_DIR / f"{name}.txt").read_text(encoding="utf-8")

    def _chat(self, system: str, user: str, **kwargs: Any) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            **kwargs,
        )
        return response.choices[0].message.content or ""

    def _chat_json(self, system: str, user: str, schema: Type[T], **kwargs: Any) -> T:
        """Chiede al modello JSON valido e lo valida con il modello Pydantic dato."""
        system_with_schema = (
            f"{system}\n\n"
            f"Rispondi SOLO con un oggetto JSON valido che rispetti questo schema:\n"
            f"{json.dumps(schema.model_json_schema(), ensure_ascii=False, indent=2)}\n\n"
            f"Non aggiungere testo prima o dopo il JSON. Non usare markdown o backtick."
        )
        raw = self._chat(system_with_schema, user, **kwargs)
        return schema.model_validate_json(_extract_json(raw))
