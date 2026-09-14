# Skill: test-pipeline

Esegui il test della pipeline EasyRead e interpreta l'output.

## Passi

1. Assicurati di essere nella root del progetto (`c:/0_HACKHATON/easyread`).

2. Verifica che esista il file `.env` con `ANTHROPIC_API_KEY` e `ANTHROPIC_MODEL`.
   Se manca, avvisa l'utente e fermati.

3. Esegui il test:
   ```
   python -m app.pipeline.test_pipeline
   ```

4. Analizza l'output e riporta:
   - **Classificazione**: tipo documento rilevato e confidenza — è corretta?
   - **Semplificazione**: il testo è in italiano B1? Tutti gli importi e le date originali sono presenti?
   - **Azioni**: le azioni estratte sono complete? Ci sono duplicati o azioni mancanti?
   - **Safety**: il risultato è OK o ci sono warning? I warning sono falsi positivi o errori reali?

5. Se c'è un errore Python:
   - Errore di import → verifica che le dipendenze siano installate (`pip install -r app/pipeline/requirements.txt`)
   - `ANTHROPIC_API_KEY` non trovata → il `.env` non viene caricato, controlla il path
   - `ValidationError` Pydantic → il modello ha restituito JSON malformato, mostra il raw response
   - `RateLimitError` → il modello è occupato, riprova tra qualche secondo

6. Se il test passa, suggerisci eventuali miglioramenti osservati nell'output.
