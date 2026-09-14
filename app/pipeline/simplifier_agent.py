from .base_agent import BaseAgent
from .models import ClassifierResult, DocumentType

_ISTRUZIONE_MULTA = """
ISTRUZIONE SPECIALE — questo documento è una multa:
Dopo aver spiegato la violazione, aggiungi obbligatoriamente un paragrafo separato che inizia con
"Perché ti hanno multato:" e spiega in 1-2 frasi semplici e concrete cosa vieta o prescrive
l'articolo citato nel documento (es. art. 158 C.d.S. = divieto di sosta in doppia fila,
sugli attraversamenti pedonali, davanti ai passi carrabili, ecc.).
Usa la tua conoscenza del Codice della Strada; se non sei sicuro dell'articolo, scrivi
"L'articolo [numero] del Codice della Strada regola [tema generale]" senza inventare dettagli.
"""


class SimplifierAgent(BaseAgent):
    def run(
        self, text: str, classifier: ClassifierResult, lingua_output: str = "italiano"
    ) -> str:
        system = self._load_prompt("simplifier").format(
            document_type=classifier.type_label,
            language=classifier.language,
            lingua_output=lingua_output,
        )
        if classifier.document_type == DocumentType.MULTA:
            system += _ISTRUZIONE_MULTA
        return self._chat(system, text)
