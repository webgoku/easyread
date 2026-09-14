from .base_agent import BaseAgent
from .models import ClassifierResult


class ClassifierAgent(BaseAgent):
    def run(self, text: str) -> ClassifierResult:
        system = self._load_prompt("classifier")
        return self._chat_json(system, text, ClassifierResult)
