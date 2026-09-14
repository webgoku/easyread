from .classifier_agent import ClassifierAgent
from .simplifier_agent import SimplifierAgent
from .action_agent import ActionAgent
from .safety_agent import SafetyAgent
from .models import EasyReadResult


class Orchestrator:
    """Pipeline principale: Classifier → Simplifier → Action → Safety."""

    def __init__(self, model: str | None = None):
        kwargs = {"model": model} if model else {}
        self.classifier = ClassifierAgent(**kwargs)
        self.simplifier = SimplifierAgent(**kwargs)
        self.action = ActionAgent(**kwargs)
        self.safety = SafetyAgent(**kwargs)

    def process(self, text: str) -> EasyReadResult:
        classifier_result = self.classifier.run(text)
        simplified = self.simplifier.run(text, classifier_result)
        actions = self.action.run(text, simplified, classifier_result)
        safety = self.safety.run(text, simplified, actions)

        return EasyReadResult(
            original_text=text,
            classifier=classifier_result,
            simplified_text=simplified,
            actions=actions,
            safety=safety,
        )
