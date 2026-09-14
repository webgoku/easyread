# Skill: sync-prompts

Verifica e mantieni allineati i prompt tra `app/pipeline/prompts/*.txt` e `agents/*.md`.

## Problema che risolve

I prompt del progetto esistono in due posti:
- `app/pipeline/prompts/*.txt` — usati dal codice Python a runtime
- `agents/*.md` — usati dagli agenti Claude durante lo sviluppo interattivo

Se vengono modificati in un posto solo, i due divergono e lo sviluppo interattivo
produce risultati diversi dalla pipeline automatica.

## Passi

1. Leggi i 4 file di prompt Python:
   - `app/pipeline/prompts/classifier.txt`
   - `app/pipeline/prompts/simplifier.txt`
   - `app/pipeline/prompts/action.txt`
   - `app/pipeline/prompts/safety.txt`

2. Leggi i 4 file agente Claude:
   - `agents/classifier.md`
   - `agents/simplifier.md`
   - `agents/action-extractor.md`
   - `agents/safety-checker.md`

3. Per ogni coppia, confronta il corpo del prompt (ignora il frontmatter `---` nei `.md`).
   Segnala qualsiasi differenza trovata, specificando quale dei due è più aggiornato
   (basati su contenuto, non su data file).

4. Se ci sono differenze, chiedi all'utente quale versione è quella corretta
   e aggiorna l'altra di conseguenza.

5. Conferma che tutti e 4 i prompt sono ora allineati.
