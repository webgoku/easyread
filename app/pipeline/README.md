# app/pipeline/ — Pipeline Python di EasyRead

Questo modulo contiene il codice Python che orchestra la semplificazione dei documenti PA.

## Come funziona

L'utente incolla un documento nell'app Streamlit. La pipeline lo processa in 4 step sequenziali e restituisce un oggetto `EasyReadResult` pronto per la UI.

```
testo grezzo
    │
    ▼
ClassifierAgent   →  tipo documento, lingua, confidenza
    │
    ▼
SimplifierAgent   →  testo in italiano B1
    │
    ▼
ActionAgent       →  azioni[], scadenze[], importi[]
    │
    ▼
SafetyAgent       →  verified (bool), warnings[]
    │
    ▼
EasyReadResult    →  oggetto unico per la UI
```

## Uso dall'app Streamlit

```python
from app.pipeline import Orchestrator

result = Orchestrator().process(testo_documento)

# Cosa è successo
print(result.classifier.type_label)      # "Avviso Agenzia delle Entrate"

# Testo semplificato
print(result.simplified_text)

# Azioni da fare
for azione in result.actions.actions:
    print(azione.description, azione.deadline, azione.amount)

# Esito verifica sicurezza
if not result.safety.verified:
    print("ATTENZIONE:", result.safety.warnings)
```

## File

| File | Ruolo |
|---|---|
| `models.py` | Strutture dati Pydantic (ClassifierResult, ActionResult, EasyReadResult…) |
| `base_agent.py` | Client Anthropic, metodi `_chat()` e `_chat_json()` |
| `orchestrator.py` | Chiama i 4 agenti in sequenza |
| `classifier_agent.py` | Step 1: riconosce tipo e lingua del documento |
| `simplifier_agent.py` | Step 2: riscrive in italiano B1 |
| `action_agent.py` | Step 3: estrae azioni, scadenze, importi (output strutturato) |
| `safety_agent.py` | Step 4: verifica numeri/date via regex + LLM |
| `prompts/*.txt` | System prompt di ogni agente (testo puro) |
| `requirements.txt` | Dipendenze Python del modulo |
| `test_pipeline.py` | Script di test standalone |

## Setup e test rapido

```powershell
# Dalla root del progetto
pip install -r app/pipeline/requirements.txt
python -m app.pipeline.test_pipeline
```

Assicurati di avere un file `.env` nella root con:
```
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-haiku-4-5-20251001
```

Vedi `.env.example` per il template completo.

## Configurazione modello

Il modello si imposta tramite variabile d'ambiente `ANTHROPIC_MODEL`.
Default: `claude-haiku-4-5-20251001` (economico, veloce, ottimo per questa pipeline).

## Note sul SafetyAgent

Usa due livelli di verifica:
1. **Regex** — estrae date (formato `gg/mm/aaaa` o `30 novembre 2024`) e importi (richiede simbolo `€`) sia dall'originale sia dall'output, poi li confronta.
2. **LLM** — chiede al modello di verificare discrepanze semantiche non catturabili con regex (es. un importo parafrasato).

Se `safety.verified == False`, l'app deve mostrare un disclaimer visibile all'utente prima del risultato.

## Agenti Claude per il debug

La versione interattiva di questi agenti (per debug e sviluppo) si trova in [`agents/`](../../agents/README.md).
