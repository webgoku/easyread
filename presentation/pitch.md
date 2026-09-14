# Pitch

## Il problema

Ogni anno milioni di italiani ricevono lettere dalla pubblica amministrazione che non riescono a leggere. Non perché non sappiano leggere — ma perché il linguaggio burocratico è progettato per i giuristi, non per le persone.

Il risultato: scadenze perse, sanzioni evitabili, stress inutile.

## La soluzione

EasyRead è una pipeline di 5 agenti AI specializzati che trasforma qualsiasi documento della PA in linguaggio semplice, estrae le azioni da compiere e verifica che nessun numero sia stato alterato.

In 5 ore di sviluppo, abbiamo costruito uno strumento che:
- riconosce il tipo di documento
- lo riscrive in italiano semplice (o in 5 altre lingue)
- dice esattamente cosa fare, entro quando e quanto pagare
- controlla automaticamente che cifre e date siano identiche all'originale
- spiega i termini tecnici con parole di tutti i giorni

## Il team

[Inserire nomi e ruoli]

## Tecnologie

- **Claude API (Anthropic)** — 5 agenti specializzati orchestrati in sequenza
- **Streamlit** — interfaccia utente accessibile e semplice
- **Python / Pydantic** — orchestrazione e validazione dei dati

## Cosa manca per andare in produzione

- Supporto OCR per documenti scansionati o fotografati
- Integrazione diretta con pagoPA per il pagamento in-app
- Copertura estesa a tutti i formati della PA italiana
