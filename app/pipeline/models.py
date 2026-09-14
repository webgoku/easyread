from __future__ import annotations

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class DocumentType(str, Enum):
    AGENZIA_ENTRATE = "agenzia_entrate"
    INPS = "inps"
    COMUNE = "comune"
    BOLLETTA = "bolletta"
    MULTA = "multa"
    ALTRO = "altro"


class ClassifierResult(BaseModel):
    document_type: DocumentType
    language: str = Field(description="Codice lingua ISO 639-1, es. 'it', 'en'")
    confidence: float = Field(ge=0.0, le=1.0)
    type_label: str = Field(description="Etichetta leggibile, es. 'Avviso Agenzia delle Entrate'")


class Action(BaseModel):
    description: str = Field(description="Cosa deve fare l'utente, in italiano semplice")
    deadline: Optional[str] = Field(default=None, description="Scadenza in formato leggibile, es. '31 ottobre 2026'")
    amount: Optional[str] = Field(default=None, description="Importo collegato, es. '€ 120,00'")
    priority: int = Field(ge=1, le=3, description="1=urgente, 2=normale, 3=facoltativo")


class ActionResult(BaseModel):
    actions: list[Action]
    deadlines: list[str] = Field(description="Tutte le scadenze trovate nel documento")
    amounts: list[str] = Field(description="Tutti gli importi trovati nel documento")


class SafetyCheck(BaseModel):
    verified: bool = Field(description="True se tutti i numeri/date dell'output coincidono con l'originale")
    warnings: list[str] = Field(description="Discrepanze trovate, vuoto se verified=True")
    amounts_original: list[str]
    amounts_output: list[str]
    dates_original: list[str]
    dates_output: list[str]


class GlossaryTerm(BaseModel):
    term: str = Field(description="Il termine tecnico esatto come appare nel testo")
    definition: str = Field(description="Spiegazione breve in parole semplici")


class GlossaryResult(BaseModel):
    terms: list[GlossaryTerm] = Field(description="Lista dei termini tecnici trovati, vuota se nessuno")


class EasyReadResult(BaseModel):
    original_text: str
    classifier: ClassifierResult
    simplified_text: str
    actions: ActionResult
    safety: SafetyCheck
    glossary: GlossaryResult
