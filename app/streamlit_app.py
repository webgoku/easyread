"""EasyRead — interfaccia per leggere facile i documenti della Pubblica Amministrazione."""

import sys
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

RADICE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RADICE))
load_dotenv(RADICE / ".env", override=True)

from agents.models import (
    Action,
    ActionResult,
    ClassifierResult,
    DocumentType,
    EasyReadResult,
    SafetyCheck,
)

CARTELLA_ESEMPI = Path(__file__).parent / "samples"

ESEMPI = {
    "Anomalia sui redditi": "anomalia_redditi.pdf",
    "Dichiarazione integrativa": "integrativa_altri_redditi.pdf",
}

ICONE_TIPO = {
    DocumentType.AGENZIA_ENTRATE: "🏛️",
    DocumentType.INPS: "👥",
    DocumentType.COMUNE: "🏢",
    DocumentType.BOLLETTA: "💡",
    DocumentType.MULTA: "🚗",
    DocumentType.ALTRO: "📄",
}

PRIORITA = {
    1: ("🔴", "Urgente"),
    2: ("🟡", "Da fare"),
    3: ("🟢", "Se vuoi"),
}


st.set_page_config(page_title="EasyRead", page_icon="📄", layout="centered")

st.markdown(
    """<style>
    html, body, [class*="css"] { font-size: 18px; }
    .main p, .main li { font-size: 1.05rem; line-height: 1.75; }
    .blocco-semplice {
        background: #f7f4ff; border-left: 5px solid #7c3aed;
        padding: 20px 24px; border-radius: 10px; margin: 8px 0 20px;
    }
    .blocco-semplice p { margin-bottom: 0.9rem; }
    </style>""",
    unsafe_allow_html=True,
)


def testo_da_pdf(percorso_o_file) -> str:
    from pypdf import PdfReader

    return "\n".join(p.extract_text() or "" for p in PdfReader(percorso_o_file).pages)


def risultato_finto() -> EasyReadResult:
    """Esempio realistico usato per sviluppare la UI senza chiamare l'LLM."""
    return EasyReadResult(
        original_text="(testo originale del documento)",
        classifier=ClassifierResult(
            document_type=DocumentType.AGENZIA_ENTRATE,
            language="it",
            confidence=0.96,
            type_label="Comunicazione di irregolarità — Agenzia delle Entrate",
        ),
        simplified_text=(
            "L'Agenzia delle Entrate ha controllato la tua dichiarazione dei redditi "
            "del 2024 e ha trovato una differenza.\n\n"
            "Tu hai dichiarato 28.450,00 euro di stipendio. Al tuo datore di lavoro "
            "però risultano 31.200,00 euro. Mancano quindi 2.750,00 euro.\n\n"
            "Per questo motivo devi pagare 644,92 euro in più. Questa cifra comprende "
            "l'imposta non pagata, una sanzione cioè una multa, e gli interessi.\n\n"
            "Se pensi che ci sia un errore, puoi mandare i tuoi documenti e spiegare "
            "la tua situazione. Non sei obbligato a pagare subito."
        ),
        actions=ActionResult(
            actions=[
                Action(
                    description="Paga 644,92 euro con il modello F24. Puoi farlo in banca, alla posta o dal tabaccaio.",
                    deadline="31 ottobre 2026",
                    amount="644,92 €",
                    priority=1,
                ),
                Action(
                    description="Se pensi che l'importo sia sbagliato, manda i tuoi documenti tramite il canale CIVIS sul sito dell'Agenzia.",
                    deadline="31 ottobre 2026",
                    amount=None,
                    priority=2,
                ),
                Action(
                    description="Fatti aiutare da un CAF o da un patronato: il servizio è gratuito.",
                    deadline=None,
                    amount=None,
                    priority=3,
                ),
            ],
            deadlines=["31 ottobre 2026"],
            amounts=["644,92 €", "578,00 €", "57,80 €", "9,12 €", "2.750,00 €"],
        ),
        safety=SafetyCheck(
            verified=True,
            warnings=[],
            amounts_original=["644,92", "578,00", "57,80", "9,12", "2.750,00"],
            amounts_output=["644,92", "578,00", "57,80", "9,12", "2.750,00"],
            dates_original=["31/10/2026"],
            dates_output=["31 ottobre 2026"],
        ),
    )


@st.cache_data(show_spinner=False)
def analizza_davvero(testo: str) -> EasyReadResult:
    from agents import Orchestrator

    return Orchestrator().process(testo)


def mostra_risultato(r: EasyReadResult) -> None:
    icona = ICONE_TIPO.get(r.classifier.document_type, "📄")
    st.caption(f"{icona}  {r.classifier.type_label}")

    st.subheader("Cosa dice questo documento")
    corpo = "".join(
        f"<p>{par.strip()}</p>"
        for par in r.simplified_text.split("\n\n")
        if par.strip()
    )
    st.markdown(f'<div class="blocco-semplice">{corpo}</div>', unsafe_allow_html=True)

    if r.actions.amounts or r.actions.deadlines:
        a, b = st.columns(2)
        if r.actions.amounts:
            a.metric("Importo principale", r.actions.amounts[0])
        if r.actions.deadlines:
            b.metric("Prima scadenza", r.actions.deadlines[0])

    if r.actions.actions:
        st.subheader("Cosa devi fare")
        ordinate = sorted(r.actions.actions, key=lambda x: x.priority)
        for i, azione in enumerate(ordinate, 1):
            pallino, etichetta = PRIORITA.get(azione.priority, ("⚪", ""))
            with st.container(border=True):
                st.markdown(f"**{i}. {azione.description}**")
                dettagli = [f"{pallino} {etichetta}"]
                if azione.deadline:
                    dettagli.append(f"📅 entro il {azione.deadline}")
                if azione.amount:
                    dettagli.append(f"💶 {azione.amount}")
                st.caption("  ·  ".join(dettagli))

    st.subheader("Abbiamo controllato i numeri")
    if r.safety.verified and not r.safety.warnings:
        st.success(
            "Le cifre e le date qui sopra sono le stesse del documento originale. "
            "Non abbiamo cambiato nulla."
        )
    else:
        st.error(
            "Attenzione: alcune cifre o date potrebbero non corrispondere. "
            "Controlla sempre il documento originale."
        )
    for avviso in r.safety.warnings:
        st.warning(avviso)

    with st.expander("Vedi il confronto con l'originale"):
        a, b = st.columns(2)
        a.markdown("**Nel documento originale**")
        a.write(r.safety.amounts_original or "nessun importo")
        a.write(r.safety.dates_original or "nessuna data")
        b.markdown("**Nella nostra spiegazione**")
        b.write(r.safety.amounts_output or "nessun importo")
        b.write(r.safety.dates_output or "nessuna data")

    st.info(
        "**Questo strumento spiega soltanto cosa c'è scritto nel documento. "
        "Non dà consigli fiscali o legali.**\n\n"
        "Per decidere cosa fare, rivolgiti a un CAF, a un patronato o a un "
        "commercialista. Molti di questi servizi sono gratuiti.",
        icon="ℹ️",
    )


st.title("📄 EasyRead")
st.markdown("### Hai ricevuto una lettera che non capisci?")
st.write("Caricala qui. Ti spieghiamo con parole semplici cosa dice e cosa devi fare.")

with st.sidebar:
    st.header("Impostazioni")
    usa_finto = st.toggle(
        "Modalità sviluppo",
        value=True,
        help="Mostra un risultato di esempio senza chiamare l'intelligenza artificiale. "
        "Serve per lavorare sull'interfaccia senza attese.",
    )
    if usa_finto:
        st.caption("⚡ Dati finti, risposta immediata.")
    else:
        st.caption("🐢 Chiamate reali: circa 3 minuti a documento.")

st.divider()

if "testo" not in st.session_state:
    st.session_state.testo = ""

scelta = st.radio(
    "Come vuoi darci il documento?",
    ["Carica un PDF", "Scrivi o incolla il testo", "Usa un esempio"],
    horizontal=True,
)

if scelta == "Carica un PDF":
    caricato = st.file_uploader("Scegli il file", type="pdf")
    if caricato:
        st.session_state.testo = testo_da_pdf(caricato)
        st.success(f"Documento letto: {len(st.session_state.testo)} caratteri.")

elif scelta == "Scrivi o incolla il testo":
    st.session_state.testo = st.text_area(
        "Copia qui il testo della lettera",
        value=st.session_state.testo,
        height=220,
    )

else:
    for etichetta, nome_file in ESEMPI.items():
        if st.button(etichetta, use_container_width=True):
            st.session_state.testo = testo_da_pdf(CARTELLA_ESEMPI / nome_file)
    if st.session_state.testo:
        st.caption(f"Documento pronto: {len(st.session_state.testo)} caratteri.")

st.divider()

if st.button(
    "Spiegamelo",
    type="primary",
    use_container_width=True,
    disabled=not st.session_state.testo.strip(),
):
    if usa_finto:
        mostra_risultato(risultato_finto())
    else:
        with st.spinner("Sto leggendo il documento. Ci vogliono alcuni minuti."):
            try:
                mostra_risultato(analizza_davvero(st.session_state.testo))
            except Exception as errore:
                st.error(f"Non sono riuscito a leggere il documento: {errore}")
