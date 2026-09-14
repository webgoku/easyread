"""EasyRead — interfaccia per leggere facile i documenti della Pubblica Amministrazione."""

import sys
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

QUI = Path(__file__).resolve().parent
RADICE = QUI.parent
sys.path.insert(0, str(QUI))
load_dotenv(RADICE / ".env", override=True)

from pipeline.models import (
    Action,
    ActionResult,
    ClassifierResult,
    DocumentType,
    EasyReadResult,
    GlossaryResult,
    GlossaryTerm,
    SafetyCheck,
)

CARTELLA_ESEMPI = Path(__file__).parent / "samples"

ESEMPI = {
    "Anomalia sui redditi": "anomalia_redditi.txt",
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

LINGUE = {
    "🇮🇹  Italiano": "italiano",
    "🇬🇧  English": "inglese",
    "🇫🇷  Français": "francese",
    "🇪🇸  Español": "spagnolo",
    "🇷🇴  Română": "rumeno",
    "🇸🇦  العربية": "arabo",
}


st.set_page_config(page_title="EasyRead", page_icon="📄", layout="wide")

st.markdown(
    """<style>
    html, body, [class*="css"] { font-size: 18px; }
    .main p, .main li { font-size: 1.05rem; line-height: 1.75; }
    .intestazione { text-align: center; padding: 16px 0 4px; }
    .intestazione .marchio {
        font-size: 3.6rem; font-weight: 800; letter-spacing: -0.03em;
        color: #4c1d95; line-height: 1.1; margin: 0;
    }
    .intestazione .accento {
        width: 76px; height: 4px; background: #7c3aed;
        border-radius: 2px; margin: 20px auto 28px;
    }
    .intestazione .domanda {
        font-size: 1.5rem; font-weight: 600; color: #1f2937;
        margin: 0 0 14px; line-height: 1.35;
    }
    .intestazione .spiega {
        font-size: 1.05rem; color: #6b7280; max-width: 460px;
        margin: 0 auto; line-height: 1.65;
    }
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


def carica_esempio(nome_file: str) -> str:
    percorso = CARTELLA_ESEMPI / nome_file
    if percorso.suffix == ".txt":
        return percorso.read_text(encoding="utf-8")
    return testo_da_pdf(percorso)


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
        glossary=GlossaryResult(
            terms=[
                GlossaryTerm(
                    term="modello F24",
                    definition="È un foglio che si usa per pagare le tasse allo Stato. Puoi compilarlo in banca, alla posta o online.",
                ),
                GlossaryTerm(
                    term="canale CIVIS",
                    definition="È un servizio online dell'Agenzia delle Entrate. Ti permette di inviare documenti e chiedere chiarimenti senza andare allo sportello.",
                ),
                GlossaryTerm(
                    term="CAF",
                    definition="Centro di Assistenza Fiscale. È un ufficio dove persone esperte ti aiutano con le pratiche fiscali, spesso gratuitamente.",
                ),
            ]
        ),
    )


@st.cache_data(show_spinner=False)
def analizza_davvero(testo: str, lingua: str) -> EasyReadResult:
    from pipeline import Orchestrator

    return Orchestrator().process(testo, lingua)


def mostra_risultato(r: EasyReadResult) -> None:
    # Intestazione documento + metric a larghezza piena
    icona = ICONE_TIPO.get(r.classifier.document_type, "📄")
    st.caption(f"{icona}  {r.classifier.type_label}")

    if r.actions.amounts or r.actions.deadlines:
        col_a, col_b, col_c = st.columns([1, 1, 2])
        if r.actions.amounts:
            col_a.metric("Importo principale", r.actions.amounts[0])
        if r.actions.deadlines:
            col_b.metric("Prima scadenza", r.actions.deadlines[0])

    st.divider()

    # Due colonne principali
    col_sx, col_dx = st.columns([1, 1], gap="large")

    with col_sx:
        st.subheader("Cosa dice questo documento")
        corpo = "".join(
            f"<p>{par.strip()}</p>"
            for par in r.simplified_text.split("\n\n")
            if par.strip()
        )
        st.markdown(f'<div class="blocco-semplice">{corpo}</div>', unsafe_allow_html=True)

    with col_dx:
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

    if r.glossary.terms:
        st.subheader("Parole difficili spiegate")
        for voce in r.glossary.terms:
            with st.expander(voce.term):
                st.write(voce.definition)

    st.info(
        "**Questo strumento spiega soltanto cosa c'è scritto nel documento. "
        "Non dà consigli fiscali o legali.**\n\n"
        "Per decidere cosa fare, rivolgiti a un CAF, a un patronato o a un "
        "commercialista. Molti di questi servizi sono gratuiti.",
        icon="ℹ️",
    )

    st.divider()

    (tab_tecnici,) = st.tabs(["🔍 Dettagli tecnici"])
    with tab_tecnici:
        st.caption("Verifica automatica della fedeltà della semplificazione.")
        if r.safety.verified and not r.safety.warnings:
            st.success("Cifre e date corrispondono al documento originale.")
        else:
            st.error("Alcune cifre o date potrebbero non corrispondere. Controlla il documento originale.")
        for avviso in r.safety.warnings:
            st.warning(avviso)
        a, b = st.columns(2)
        a.markdown("**Nel documento originale**")
        a.write(r.safety.amounts_original or "nessun importo")
        a.write(r.safety.dates_original or "nessuna data")
        b.markdown("**Nella nostra spiegazione**")
        b.write(r.safety.amounts_output or "nessun importo")
        b.write(r.safety.dates_output or "nessuna data")


# --- Stato sessione ---
for _chiave, _default in [("vista", "input"), ("risultato", None), ("analisi_finta", False), ("testo", "")]:
    if _chiave not in st.session_state:
        st.session_state[_chiave] = _default

# --- Logo ---
st.markdown(
    """<div class="intestazione">
        <p class="marchio">EasyRead</p>
        <div class="accento"></div>
        <p class="domanda">Hai ricevuto una lettera che non capisci?</p>
        <p class="spiega">Caricala qui: te la spieghiamo con parole semplici
        e ti diciamo cosa devi fare.</p>
    </div>""",
    unsafe_allow_html=True,
)

# --- Tasto Home (solo nella vista risultati) ---
if st.session_state.vista == "risultati":
    col_home, _ = st.columns([2, 5])
    with col_home:
        if st.button("← Analizza un altro documento", key="home"):
            st.session_state.vista = "input"
            st.session_state.risultato = None
            st.rerun()

with st.sidebar:
    st.header("Impostazioni")
    usa_finto = st.toggle(
        "Modalità sviluppo",
        value=True,
        help="Mostra un risultato di esempio senza chiamare l'intelligenza artificiale. "
        "Serve per lavorare sull'interfaccia senza attese.",
    )
    if usa_finto:
        st.error("Risultato finto e sempre uguale.\n\nIl documento non viene letto.", icon="🧪")
    else:
        st.success("Analisi reale del tuo documento.\n\nCirca 3 minuti di attesa.", icon="🤖")

# --- Vista input ---
if st.session_state.vista == "input":
    st.divider()

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
                st.session_state.testo = carica_esempio(nome_file)
        if st.session_state.testo:
            st.caption(f"Documento pronto: {len(st.session_state.testo)} caratteri.")

    st.divider()

    lingua = LINGUE[
        st.selectbox(
            "In che lingua vuoi la spiegazione?",
            list(LINGUE),
            help="Il documento resta in italiano. Cambia solo la lingua della spiegazione.",
        )
    ]

    if st.button(
        "Spiegamelo",
        type="primary",
        use_container_width=True,
        disabled=not st.session_state.testo.strip(),
    ):
        if usa_finto:
            st.session_state.risultato = risultato_finto()
            st.session_state.analisi_finta = True
            st.session_state.vista = "risultati"
            st.rerun()
        else:
            with st.spinner("Sto leggendo il documento. Ci vogliono alcuni minuti."):
                try:
                    st.session_state.risultato = analizza_davvero(st.session_state.testo, lingua)
                    st.session_state.analisi_finta = False
                    st.session_state.vista = "risultati"
                    st.rerun()
                except Exception as errore:
                    st.error(f"Non sono riuscito a leggere il documento: {errore}")

# --- Vista risultati ---
elif st.session_state.vista == "risultati" and st.session_state.risultato:
    if st.session_state.analisi_finta:
        st.warning(
            "**Stai vedendo un risultato finto.** È un esempio fisso scritto nel codice: "
            "non ha letto il tuo documento. Per analizzarlo davvero, spegni "
            "**Modalità sviluppo** nella barra a sinistra.",
            icon="🧪",
        )
    mostra_risultato(st.session_state.risultato)
