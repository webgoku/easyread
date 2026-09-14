from .base_agent import BaseAgent
from .models import ClassifierResult


class SimplifierAgent(BaseAgent):
    def run(
        self, text: str, classifier: ClassifierResult, lingua_output: str = "italiano"
    ) -> str:
        system = self._load_prompt("simplifier").format(
            document_type=classifier.type_label,
            language=classifier.language,
            lingua_output=lingua_output,
        )
        return self._chat(system, text)
