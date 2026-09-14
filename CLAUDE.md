# EasyRead

Traduce documenti della Pubblica Amministrazione italiana in linguaggio semplice,
spiegando cosa dicono, cosa fare e a chi rivolgersi. Prototipo per Hagenthon 2026
(Tema 01 — Accessibilità Digitale).

## Divisione del lavoro

Siamo in due e lavoriamo in parallelo. **Prima di modificare un file fuori dal
proprio perimetro, avvisare l'altro.**

| Perimetro | Contenuto |
|---|---|
| `app/pipeline/` | Agenti, prompt, orchestratore |
| `app/streamlit_app.py` | Interfaccia utente |
| `agents/*.md` | Documentazione di progettazione degli agenti (non è codice) |
| `presentation/` | Materiali per la giuria |

`app/pipeline/models.py` è **il contratto tra le due metà**: i prompt devono produrre
quelle forme, la UI le consuma. Modificarlo impatta entrambi — comunicarlo sempre.

## Vincoli della sfida — non negoziabili

Sono i criteri su cui la giuria valuta, non preferenze di stile.

1. **Mai dare consigli fiscali o legali.** Si spiega solo cosa il documento dice.
   Ogni risultato deve rimandare a CAF, patronato o commercialista.
2. **Semplificare senza tradire.** Il significato dell'originale non cambia.
3. **Importi e date restano identici all'originale.** Mai arrotondati, mai
   riformattati, mai tradotti — nemmeno quando la spiegazione esce in un'altra lingua.
   Il Safety Agent confronta `amounts_output` con `amounts_original`: se si alterano,
   la verifica fallisce e si perde la prova che la semplificazione è fedele.
4. **Niente dati personali reali** nei documenti di esempio. Si usano fac-simile
   ufficiali dell'Agenzia con dati fittizi.

## Convenzioni

- **Tutto in italiano**: codice, commenti, messaggi di commit, testi della UI.
- **Nomi di enti e moduli non si traducono** (`modello F24`, `CIVIS`, `Agenzia delle
  Entrate`): l'utente deve riconoscerli sui documenti e sui siti veri. Semmai si
  aggiunge una spiegazione tra parentesi.
- **La UI parla a chi fatica a leggere.** Frasi brevi, niente gergo, niente termini
  tecnici nei messaggi a schermo.
- **File di esempio in UTF-8.** Su Windows `read_text()` senza encoding esplicito usa
  cp1252 e rovina gli accenti: passare sempre `encoding="utf-8"`.

## Come si avvia

```powershell
pip install -r app/requirements.txt
copy .env.example .env     # poi inserire ANTHROPIC_API_KEY
streamlit run app/streamlit_app.py
```

Il toggle **Modalità sviluppo** restituisce un risultato finto senza chiamare l'API:
serve a lavorare sulla UI senza attese e senza costi. **Va spento prima della demo.**

## Trappole già incontrate

- **Gli ID dei modelli non vogliono il suffisso con la data.** `claude-haiku-4-5`,
  non `claude-haiku-4-5-20251001`.
- **`load_dotenv()` va chiamato nell'entry point.** Gli agenti leggono
  `os.environ[...]` direttamente: senza, vanno in `KeyError`.
- **Una analisi = 4 chiamate al modello** (classifier, simplifier, action, safety).
  Streamlit riesegue lo script a ogni interazione: senza `@st.cache_data` si
  moltiplicano le chiamate a ogni click.
