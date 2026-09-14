# agents/ — Orchestrazione EasyRead

## Pipeline

```
input (testo grezzo)
        │
        ▼
ClassifierAgent   →  DocumentType, lingua, confidenza
        │
        ▼
SimplifierAgent   →  testo in italiano B1
        │
        ▼
ActionAgent       →  azioni[], scadenze[], importi[]
        │
        ▼
SafetyAgent       →  verified, warnings[]
        │
        ▼
EasyReadResult    →  oggetto unico restituito all'app
```

## File

| File | Ruolo |
|---|---|
| `models.py` | Pydantic models condivisi |
| `base_agent.py` | Client OpenRouter, `_chat()` e `_chat_json()` |
| `classifier_agent.py` | Riconosce tipo documento |
| `simplifier_agent.py` | Riscrive in italiano B1 |
| `action_agent.py` | Estrae azioni/scadenze/importi (structured output) |
| `safety_agent.py` | Verifica numeri/date via regex + LLM |
| `orchestrator.py` | Chiama gli agenti in sequenza |
| `prompts/*.txt` | Prompt di sistema per ogni agente |

## Uso

```python
from agents import Orchestrator

result = Orchestrator().process(testo_documento)
print(result.simplified_text)
print(result.actions.actions)
print(result.safety.verified)
```

## Configurazione

Variabili d'ambiente richieste (vedi `.env.example` in `app/`):

| Variabile | Descrizione |
|---|---|
| `OPENROUTER_API_KEY` | Chiave API OpenRouter (obbligatoria) |
| `OPENROUTER_MODEL` | Modello da usare (default: `mistralai/mistral-7b-instruct`) |

## Note sul Safety Agent

Il `SafetyAgent` usa due livelli di verifica:
1. **Regex** — estrae date e importi sia dall'originale sia dall'output e li confronta.
2. **LLM** — chiede al modello di verificare discrepanze semantiche non catturabili con regex.

In caso di `verified=False`, l'app deve mostrare un disclaimer visibile all'utente.
