from .classifier_agent import ClassifierAgent
from .simplifier_agent import SimplifierAgent
from .action_agent import ActionAgent
from .safety_agent import SafetyAgent
from .glossary_agent import GlossaryAgent
from .models import EasyReadResult


class Orchestrator:
    """Pipeline principale: Classifier → Simplifier → Action → Safety → Glossary."""

    def __init__(self, model: str | None = None):
        kwargs = {"model": model} if model else {}
        self.classifier = ClassifierAgent(**kwargs)
        self.simplifier = SimplifierAgent(**kwargs)
        self.action = ActionAgent(**kwargs)
        self.safety = SafetyAgent(**kwargs)
        self.glossary = GlossaryAgent(**kwargs)

    def process(self, text: str, lingua_output: str = "italiano") -> EasyReadResult:
        classifier_result = self.classifier.run(text)
        simplified = self.simplifier.run(text, classifier_result, lingua_output)
        actions = self.action.run(text, simplified, classifier_result, lingua_output)
        safety = self.safety.run(text, simplified, actions)
        glossary = self.glossary.run(simplified, lingua_output)

        return EasyReadResult(
            original_text=text,
            classifier=classifier_result,
            simplified_text=simplified,
            actions=actions,
            safety=safety,
            glossary=glossary,
        )
