# agents/ — Agenti Claude per EasyRead

Questa cartella contiene le definizioni degli agenti Claude usati durante lo sviluppo di EasyRead.

## Cosa sono questi file?

Ogni file `.md` definisce un **agente Claude specializzato** che puoi invocare direttamente in Claude Code durante il debug o lo sviluppo. Non sono codice Python: sono istruzioni per Claude.

Il formato è:
```
---
name: nome-agente
description: cosa fa, quando usarlo
---

System prompt dell'agente...
```

## A cosa servono in pratica?

Il codice Python in `app/pipeline/` chiama questi stessi agenti in modo automatico e concatenato. Gli agenti `.md` sono la versione **manuale e interattiva** degli stessi — utili quando vuoi:

- **Testare un singolo step** senza girare tutta la pipeline
- **Fare debug**: se il simplifier produce output strano, lo invochi da solo con quel documento specifico
- **Affinare i prompt**: modifichi il `.md`, testi la risposta, itero — senza toccare il codice Python

## Gli agenti disponibili

| File | Cosa fa | Quando usarlo |
|---|---|---|
| `classifier.md` | Classifica il tipo di documento PA (Agenzia Entrate, INPS, Comune, bolletta, multa) e rileva la lingua | Primo step — capire con che documento abbiamo a che fare |
| `simplifier.md` | Riscrive il documento in italiano semplice livello B1 seguendo le linee guida Easy Read | Secondo step — semplificazione accessibile |
| `action-extractor.md` | Estrae le azioni concrete che l'utente deve fare, con scadenze e importi | Terzo step — "cosa devo fare e quando" |
| `safety-checker.md` | Verifica che il testo semplificato non contenga errori fattuali rispetto all'originale (importi sbagliati, date inventate, ecc.) | Quarto step — controllo qualità |

## Come usarli in Claude Code

Apri Claude Code nella root del progetto e scrivi ad esempio:

```
Usa l'agente classifier su questo testo:
"Agenzia delle Entrate - Riscossione. Contribuente: Mario Rossi..."
```

Oppure per testare un prompt modificato:

```
Usa l'agente simplifier su questo documento e dimmi se la semplificazione
mantiene tutti gli importi originali.
```

## Relazione con il codice Python

```
agents/classifier.md        ←→    app/pipeline/classifier_agent.py
agents/simplifier.md        ←→    app/pipeline/simplifier_agent.py
agents/action-extractor.md  ←→    app/pipeline/action_agent.py
agents/safety-checker.md    ←→    app/pipeline/safety_agent.py
```

I prompt nei file `.md` e quelli in `app/pipeline/prompts/*.txt` sono allineati.
Se modifichi un prompt, aggiornali entrambi per mantenere coerenza.
