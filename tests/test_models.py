"""Verifica che i modelli Pydantic validino correttamente i dati della pipeline."""

import pytest
from pydantic import ValidationError

from pipeline.models import (
    Action,
    ActionResult,
    ClassifierResult,
    DocumentType,
    GlossaryResult,
    GlossaryTerm,
    SafetyCheck,
)


class TestDocumentType:
    def test_valori_stringa(self):
        assert DocumentType.MULTA == "multa"
        assert DocumentType.AGENZIA_ENTRATE == "agenzia_entrate"
        assert DocumentType.BOLLETTA == "bolletta"

    def test_tutti_i_tipi_definiti(self):
        attesi = {"agenzia_entrate", "inps", "comune", "bolletta", "multa", "altro"}
        assert {t.value for t in DocumentType} == attesi


class TestClassifierResult:
    def test_valido(self):
        r = ClassifierResult(
            document_type=DocumentType.MULTA,
            language="it",
            confidence=0.95,
            type_label="Verbale di infrazione al C.d.S.",
        )
        assert r.document_type == DocumentType.MULTA
        assert r.confidence == pytest.approx(0.95)

    def test_confidenza_troppo_alta(self):
        with pytest.raises(ValidationError):
            ClassifierResult(
                document_type=DocumentType.MULTA,
                language="it",
                confidence=1.5,
                type_label="Test",
            )

    def test_confidenza_negativa(self):
        with pytest.raises(ValidationError):
            ClassifierResult(
                document_type=DocumentType.ALTRO,
                language="it",
                confidence=-0.1,
                type_label="Test",
            )

    def test_tipo_documento_non_valido(self):
        with pytest.raises(ValidationError):
            ClassifierResult(
                document_type="tipo_inventato",
                language="it",
                confidence=0.8,
                type_label="Test",
            )


class TestAction:
    def test_valida_con_campi_opzionali(self):
        a = Action(description="Paga la multa", priority=1)
        assert a.deadline is None
        assert a.amount is None

    def test_priorita_1_valida(self):
        Action(description="Test", priority=1)

    def test_priorita_3_valida(self):
        Action(description="Test", priority=3)

    def test_priorita_zero_non_valida(self):
        with pytest.raises(ValidationError):
            Action(description="Test", priority=0)

    def test_priorita_quattro_non_valida(self):
        with pytest.raises(ValidationError):
            Action(description="Test", priority=4)


class TestActionResult:
    def _base(self, **kwargs):
        return ActionResult(actions=[], deadlines=[], amounts=[], **kwargs)

    def test_payment_status_da_pagare(self):
        r = self._base(payment_status="da_pagare")
        assert r.payment_status == "da_pagare"

    def test_payment_status_gia_pagato(self):
        r = self._base(payment_status="gia_pagato")
        assert r.payment_status == "gia_pagato"

    def test_payment_status_parzialmente_pagato(self):
        r = self._base(payment_status="parzialmente_pagato")
        assert r.payment_status == "parzialmente_pagato"

    def test_payment_status_non_applicabile(self):
        r = self._base(payment_status="non_applicabile")
        assert r.payment_status == "non_applicabile"

    def test_payment_status_non_valido(self):
        with pytest.raises(ValidationError):
            self._base(payment_status="sconosciuto")

    def test_payment_status_obbligatorio(self):
        """Senza payment_status la validazione deve fallire (campo required)."""
        with pytest.raises(ValidationError):
            ActionResult(actions=[], deadlines=[], amounts=[])


class TestSafetyCheck:
    def test_verificato_senza_warning(self):
        s = SafetyCheck(
            verified=True,
            warnings=[],
            amounts_original=["€ 29,40"],
            amounts_output=["€ 29,40"],
            dates_original=["28/07/2026"],
            dates_output=["28/07/2026"],
        )
        assert s.verified is True
        assert s.warnings == []

    def test_non_verificato_con_warning(self):
        s = SafetyCheck(
            verified=False,
            warnings=["Importo modificato da 29,40 a 30,00"],
            amounts_original=["€ 29,40"],
            amounts_output=["€ 30,00"],
            dates_original=[],
            dates_output=[],
        )
        assert s.verified is False
        assert len(s.warnings) == 1


class TestGlossaryResult:
    def test_lista_vuota(self):
        g = GlossaryResult(terms=[])
        assert g.terms == []

    def test_un_termine(self):
        g = GlossaryResult(
            terms=[GlossaryTerm(term="F24", definition="Modello di pagamento delle imposte.")]
        )
        assert g.terms[0].term == "F24"
