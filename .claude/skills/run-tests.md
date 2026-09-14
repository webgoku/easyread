---
description: Esegue la suite pytest di EasyRead, interpreta i risultati nel contesto della pipeline e segnala eventuali regressioni con indicazioni specifiche su cosa potrebbe averle causate.
---

## Istruzioni

1. Esegui i test dalla root del progetto:

```bash
python -m pytest tests/ -v --tb=short 2>&1
```

2. Interpreta l'output seguendo questa mappa:

| File di test | Cosa copre | Regressione tipica |
|---|---|---|
| `test_models.py` | Validazione Pydantic di tutti i modelli | Modifica a `models.py` senza aggiornare i test |
| `test_utils.py` | `_extract_json` + regex Safety Agent | Cambio al formato di risposta LLM o alle regex |
| `test_pipeline_mock.py` | Pipeline completa con LLM mockato | Cambio all'orchestratore o all'ordine degli agenti |

3. Per ogni test fallito:
   - Mostra il nome del test e il messaggio di errore completo
   - Identifica il file sorgente coinvolto
   - Spiega in una frase cosa potrebbe aver causato la regressione
   - Proponi la correzione minimale

4. Se tutti i test passano, conferma con:
   - Numero di test eseguiti
   - Tempo totale
   - Nota "Nessuna regressione rilevata — sicuro per il commit"

## Note

- I test **non fanno chiamate API reali**: usano mock di `BaseAgent._chat`
- `ANTHROPIC_API_KEY` non è necessaria per eseguire i test
- Il tempo atteso è ~2 secondi per l'intera suite
- Per test più veloci (solo smoke test): `python -m pytest tests/test_models.py -q`
