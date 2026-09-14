"""
Test di integrazione della pipeline completa con LLM mockato.
Verifica che Classifier → Simplifier → Action → Safety → Glossary
producano un EasyReadResult valido senza effettuare chiamate API reali.
"""

import json
import os
from unittest.mock import patch

import pytest

# ── Risposte predefinite per ogni agente ─────────────────────────────────────

TESTO_MULTA = (
    "Comune di Roma — Corpo di Polizia Locale. "
    "Verbale n. PL263562067. "
    "Il giorno 28/07/2026 alle 09:32 in Via Regina Margherita 72 "
    "il veicolo targa DS712CD ha violato l'art. 158 comma 2 C.d.S. "
    "Importo: € 29,40 (ridotto del 30%). Pagare entro il 07/08/2026."
)

_RISPOSTA_CLASSIFIER = json.dumps({
    "document_type": "multa",
    "language": "it",
    "confidence": 0.97,
    "type_label": "Verbale di infrazione al Codice della Strada",
})

_RISPOSTA_SIMPLIFIER = (
    "Questo documento ti informa che hai ricevuto una multa di € 29,40.\n\n"
    "La violazione è avvenuta il 28/07/2026 in Via Regina Margherita 72 a Roma.\n\n"
    "Devi pagare € 29,40 entro il 07/08/2026.\n\n"
    "Perché ti hanno multato: L'articolo 158 del Codice della Strada "
    "vieta la sosta in doppia fila e sugli attraversamenti pedonali."
)

_RISPOSTA_ACTION = json.dumps({
    "actions": [
        {
            "description": "Paga la multa di € 29,40 seguendo le istruzioni sull'avviso.",
            "deadline": "07/08/2026",
            "amount": "€ 29,40",
            "priority": 1,
        }
    ],
    "deadlines": ["07/08/2026"],
    "amounts": ["€ 29,40"],
    "payment_status": "da_pagare",
})

_RISPOSTA_SAFETY = json.dumps({
    "verified": True,
    "warnings": [],
    "amounts_original": ["€ 29,40"],
    "amounts_output": ["€ 29,40"],
    "dates_original": ["28/07/2026", "07/08/2026"],
    "dates_output": ["28/07/2026", "07/08/2026"],
})

_RISPOSTA_GLOSSARY = json.dumps({
    "terms": [
        {
            "term": "C.d.S.",
            "definition": "Codice della Strada, la legge italiana che regola la circolazione.",
        }
    ]
})

RISPOSTE_IN_ORDINE = [
    _RISPOSTA_CLASSIFIER,
    _RISPOSTA_SIMPLIFIER,
    _RISPOSTA_ACTION,
    _RISPOSTA_SAFETY,
    _RISPOSTA_GLOSSARY,
]


# ── Fixture ───────────────────────────────────────────────────────────────────

@pytest.fixture
def orchestratore():
    """Orchestrator con API Anthropic e _chat completamente mockati."""
    env = {"ANTHROPIC_API_KEY": "chiave-di-test"}
    with patch.dict(os.environ, env):
        with patch("anthropic.Anthropic"):
            with patch(
                "pipeline.base_agent.BaseAgent._chat",
                side_effect=RISPOSTE_IN_ORDINE,
            ):
                from pipeline.orchestrator import Orchestrator
                yield Orchestrator()


# ── Test ──────────────────────────────────────────────────────────────────────

class TestOrchestrator:
    def test_restituisce_easy_read_result(self, orchestratore):
        from pipeline.models import EasyReadResult
        result = orchestratore.process(TESTO_MULTA, "italiano")
        assert isinstance(result, EasyReadResult)

    def test_testo_originale_preservato(self, orchestratore):
        result = orchestratore.process(TESTO_MULTA, "italiano")
        assert result.original_text == TESTO_MULTA

    def test_classifier_tipo_documento(self, orchestratore):
        from pipeline.models import DocumentType
        result = orchestratore.process(TESTO_MULTA, "italiano")
        assert result.classifier.document_type == DocumentType.MULTA
        assert result.classifier.language == "it"
        assert result.classifier.confidence == pytest.approx(0.97)

    def test_testo_semplificato_non_vuoto(self, orchestratore):
        result = orchestratore.process(TESTO_MULTA, "italiano")
        assert len(result.simplified_text) > 0

    def test_azioni_estratte(self, orchestratore):
        result = orchestratore.process(TESTO_MULTA, "italiano")
        assert len(result.actions.actions) == 1
        azione = result.actions.actions[0]
        assert azione.priority == 1
        assert azione.deadline is not None
        assert azione.amount is not None

    def test_payment_status_da_pagare(self, orchestratore):
        result = orchestratore.process(TESTO_MULTA, "italiano")
        assert result.actions.payment_status == "da_pagare"

    def test_safety_verificato(self, orchestratore):
        result = orchestratore.process(TESTO_MULTA, "italiano")
        assert result.safety.verified is True
        assert result.safety.warnings == []

    def test_safety_importi_estratti_dal_testo(self, orchestratore):
        """Il Safety Agent estrae importi/date via regex — non dal JSON dell'LLM."""
        result = orchestratore.process(TESTO_MULTA, "italiano")
        # Il testo originale contiene "€ 29,40" → la regex la trova
        assert any("29,40" in imp for imp in result.safety.amounts_original)

    def test_safety_date_estratte_dal_testo(self, orchestratore):
        result = orchestratore.process(TESTO_MULTA, "italiano")
        assert any("28/07/2026" in d for d in result.safety.dates_original)

    def test_glossario_popolato(self, orchestratore):
        result = orchestratore.process(TESTO_MULTA, "italiano")
        assert len(result.glossary.terms) == 1
        assert result.glossary.terms[0].term == "C.d.S."
