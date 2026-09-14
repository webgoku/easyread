# Autonomia & Limiti

## Cosa Giulia riesce a fare adesso da sola

- Capisce immediatamente se deve pagare e quanto
- Sa entro quando farlo e come (pagoPA, banca, posta)
- Distingue "devo agire subito" da "posso contestare"
- Identifica i termini tecnici grazie al glossario integrato

## Dove abbiamo tenuto un occhio umano

- I prompt del Simplifier e dell'Action Agent sono stati scritti e rivisti manualmente dal team
- Il Safety Agent segnala automaticamente se un importo o una data cambia tra originale e output, ma la verifica finale spetta all'utente
- I documenti di esempio usati per i test sono fac-simile ufficiali con dati fittizi — nessun dato personale reale

## Limiti che restano

| Limite | Dettaglio |
|---|---|
| Solo testo leggibile | Non funziona con foto di documenti o scansioni sfocate — manca il supporto OCR |
| Spiega, non accompagna | Dice cosa fare, ma non guida l'utente passo per passo nell'eseguirlo (es. nel flusso pagoPA) |
| Casi ambigui non gestiti | Se il documento contiene errori dell'ente o informazioni contraddittorie, l'output potrebbe essere incompleto |
| Tipi di documento limitati | Copre i formati più comuni (Agenzia delle Entrate, INPS, Comune, bollette, multe) ma non tutti i documenti della PA |
