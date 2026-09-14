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

    def process(
        self,
        text: str,
        lingua_output: str = "italiano",
        on_step: callable = None,
    ) -> EasyReadResult:
        def _step(msg: str) -> None:
            if on_step:
                on_step(msg)

        _step("🔍 Identifico il tipo di documento…")
        classifier_result = self.classifier.run(text)

        _step("✍️ Semplifico il testo in parole semplici…")
        simplified = self.simplifier.run(text, classifier_result, lingua_output)

        _step("📋 Estraggo le azioni da intraprendere…")
        actions = self.action.run(text, simplified, classifier_result, lingua_output)

        _step("🛡️ Verifico che numeri e date siano corretti…")
        safety = self.safety.run(text, simplified, actions)

        _step("📖 Preparo il glossario dei termini difficili…")
        glossary = self.glossary.run(simplified, lingua_output)

        return EasyReadResult(
            original_text=text,
            classifier=classifier_result,
            simplified_text=simplified,
            actions=actions,
            safety=safety,
            glossary=glossary,
        )
