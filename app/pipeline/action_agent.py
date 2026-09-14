from .base_agent import BaseAgent
from .models import ActionResult, ClassifierResult


class ActionAgent(BaseAgent):
    def run(
        self,
        original_text: str,
        simplified_text: str,
        classifier: ClassifierResult,
        lingua_output: str = "italiano",
    ) -> ActionResult:
        system = self._load_prompt("action").format(
            document_type=classifier.type_label,
            lingua_output=lingua_output,
        )
        user = f"TESTO ORIGINALE:\n{original_text}\n\nTESTO SEMPLIFICATO:\n{simplified_text}"
        return self._chat_json(system, user, ActionResult)
