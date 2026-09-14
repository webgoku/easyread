from .base_agent import BaseAgent
from .models import GlossaryResult


class GlossaryAgent(BaseAgent):
    def run(self, simplified_text: str, lingua_output: str = "italiano") -> GlossaryResult:
        system = self._load_prompt("glossary").format(lingua_output=lingua_output)
        return self._chat_json(system, simplified_text, GlossaryResult)
