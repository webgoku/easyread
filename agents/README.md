# agents/ — Agenti Claude per lo sviluppo

Questa cartella contiene le definizioni degli agenti Claude utilizzati durante lo sviluppo di EasyRead.

Ogni file `.md` descrive un agente specializzato con il suo ruolo, le istruzioni di sistema e gli strumenti a disposizione.

## Agenti disponibili

| File | Ruolo |
|---|---|
| `classifier.md` | Classifica il tipo di documento PA ricevuto |
| `simplifier.md` | Riscrive il documento in italiano semplice (livello B1) |
| `action_extractor.md` | Estrae azioni, scadenze e importi dal documento |
| `safety_checker.md` | Verifica che i dati nell'output corrispondano all'originale |

## Pipeline Python

Il codice Python che orchestra questi agenti si trova in [`app/pipeline/`](../app/pipeline/).
