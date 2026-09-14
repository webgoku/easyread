"""Implementazioni Python degli agenti EasyRead."""

import json
import re


def parse_json(text: str) -> dict:
    """Estrae JSON da una risposta LLM, con fallback per testo libero."""
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        return json.loads(match.group(0))
    raise ValueError(f"Nessun JSON trovato nella risposta LLM: {text[:300]}")
