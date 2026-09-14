import re

from .base_agent import BaseAgent
from .models import ActionResult, SafetyCheck


# Date: solo formato gg/mm/aaaa o "30 novembre 2024" — esclude numeri di telefono
_DATE_RE = re.compile(
    r"\b(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4}"
    r"|\d{1,2}\s+(?:gennaio|febbraio|marzo|aprile|maggio|giugno|luglio|agosto"
    r"|settembre|ottobre|novembre|dicembre)\s+\d{4})\b",
    re.IGNORECASE,
)
# Importi: richiede il simbolo € oppure almeno 4 cifre — evita di catturare "90.96"
_AMOUNT_RE = re.compile(r"€\s*\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})", re.IGNORECASE)


def _extract_dates(text: str) -> list[str]:
    return _DATE_RE.findall(text)


def _extract_amounts(text: str) -> list[str]:
    return _AMOUNT_RE.findall(text)


class SafetyAgent(BaseAgent):
    def run(self, original_text: str, simplified_text: str, actions: ActionResult) -> SafetyCheck:
        output_combined = simplified_text + " " + " ".join(
            f"{a.description} {a.deadline or ''} {a.amount or ''}" for a in actions.actions
        )

        dates_orig = list(dict.fromkeys(_extract_dates(original_text)))
        dates_out = list(dict.fromkeys(_extract_dates(output_combined)))
        amounts_orig = list(dict.fromkeys(_extract_amounts(original_text)))
        amounts_out = list(dict.fromkeys(_extract_amounts(output_combined)))

        # Chiedi all'LLM di verificare le discrepanze semantiche residue
        system = self._load_prompt("safety")
        user = (
            f"ORIGINALE:\n{original_text}\n\n"
            f"OUTPUT AGENTI (semplificato + azioni):\n{output_combined}\n\n"
            f"Date originale: {dates_orig}\n"
            f"Date output: {dates_out}\n"
            f"Importi originale: {amounts_orig}\n"
            f"Importi output: {amounts_out}"
        )
        result = self._chat_json(system, user, SafetyCheck)

        # Sovrascrivi le liste estratte con quelle regex (più affidabili per numeri/date)
        result.amounts_original = amounts_orig
        result.amounts_output = amounts_out
        result.dates_original = dates_orig
        result.dates_output = dates_out
        return result
