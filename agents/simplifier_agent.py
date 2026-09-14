from .base_agent import BaseAgent
from .models import ClassifierResult


class SimplifierAgent(BaseAgent):
    def run(self, text: str, classifier: ClassifierResult) -> str:
        system = self._load_prompt("simplifier").format(
            document_type=classifier.type_label,
            language=classifier.language,
        )
        return self._chat(system, text)
