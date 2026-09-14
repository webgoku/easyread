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

# ── CSS globale ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* Chrome Streamlit */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
[data-testid="stHeader"]    { display: none; }
[data-testid="stToolbar"]   { display: none; }
[data-testid="stDecoration"]{ display: none; }

/* Sfondo pagina */
.stApp { background: #F0EDF8; }

/* Pulsante primary → viola (sovrascrive il rosso di Streamlit) */
button[data-testid="baseButton-primary"],
.stButton button[kind="primary"] {
    background-color: #6C3BF5 !important;
    border-color:     #6C3BF5 !important;
    color: white !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
}
button[data-testid="baseButton-primary"]:hover,
.stButton button[kind="primary"]:hover {
    background-color: #4C1D95 !important;
    border-color:     #4C1D95 !important;
}

/* Pulsante secondary → bordo grigio, hover viola */
button[data-testid="baseButton-secondary"],
.stButton button[kind="secondary"] {
    border-radius: 10px !important;
    border-color: #D1D5DB !important;
    color: #6B7280 !important;
    font-weight: 500 !important;
}
button[data-testid="baseButton-secondary"]:hover,
.stButton button[kind="secondary"]:hover {
    border-color: #6C3BF5 !important;
    color: #6C3BF5 !important;
    background-color: #F5F1FF !important;
}

/* Hero */
.hero {
    text-align: center;
    padding: 40px 0 28px;
}
.hero .brand {
    font-size: 4rem;
    font-weight: 800;
    color: #4C1D95;
    letter-spacing: -0.04em;
    line-height: 1;
    margin: 0;
}
.hero .accent-bar {
    width: 52px; height: 4px;
    background: #6C3BF5;
    border-radius: 2px;
    margin: 14px auto 18px;
}
.hero .headline {
    font-size: 1.4rem;
    font-weight: 600;
    color: #1F2937;
    margin: 0 0 8px;
}
.hero .subline {
    font-size: 0.98rem;
    color: #6B7280;
    max-width: 400px;
    margin: 0 auto 20px;
    line-height: 1.65;
}
.hero .badges {
    display: flex;
    gap: 8px;
    justify-content: center;
    flex-wrap: wrap;
}
.hero .badge {
    background: #F5F1FF;
    color: #6C3BF5;
    border: 1px solid #DDD6FE;
    border-radius: 20px;
    padding: 4px 14px;
    font-size: 0.8rem;
    font-weight: 500;
}

/* Etichetta sezione */
.sezione-label {
    font-size: 0.88rem;
    font-weight: 600;
    color: #6B7280;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-bottom: 6px;
}

/* Drop zone file uploader */
[data-testid="stFileUploaderDropzone"] {
    border: 2px dashed #C4B5FD !important;
    border-radius: 14px !important;
    background: #FAFAFA !important;
}
[data-testid="stFileUploaderDropzone"]:hover {
    border-color: #6C3BF5 !important;
    background: #F5F1FF !important;
}

/* Privacy note */
.privacy-note {
    text-align: center;
    color: #9CA3AF;
    font-size: 0.78rem;
    margin-top: 4px;
}

/* Blocco risultati */
.blocco-semplice {
    background: #F7F4FF;
    border-left: 5px solid #7C3AED;
    padding: 20px 24px;
    border-radius: 10px;
    margin: 8px 0 20px;
}
.blocco-semplice p { margin-bottom: 0.9rem; }

/* Testo base */
html, body, [class*="css"] { font-size: 18px; }
.main p, .main li { font-size: 1.05rem; line-height: 1.75; }
</style>
""", unsafe_allow_html=True)


# ── Funzioni (logica invariata) ──────────────────────────────────────────────

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
    icona = ICONE_TIPO.get(r.classifier.document_type, "📄")
    st.caption(f"{icona}  {r.classifier.type_label}")

    if r.actions.amounts or r.actions.deadlines:
        col_a, col_b, col_c = st.columns([1, 1, 2])
        if r.actions.amounts:
            col_a.metric("Importo principale", r.actions.amounts[0])
        if r.actions.deadlines:
            col_b.metric("Prima scadenza", r.actions.deadlines[0])

    st.divider()

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

    with st.expander("🔍 Dettagli tecnici", expanded=False):
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


# ── Stato sessione ───────────────────────────────────────────────────────────
for _k, _v in [
    ("vista", "input"),
    ("risultato", None),
    ("analisi_finta", False),
    ("testo", ""),
    ("scelta_tipo", "pdf"),
    ("lingua_analisi", "italiano"),
]:
    if _k not in st.session_state:
        st.session_state[_k] = _v

# ── Sidebar ──────────────────────────────────────────────────────────────────
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

# ── Tasto Home (solo nella vista risultati) ──────────────────────────────────
if st.session_state.vista == "risultati":
    col_home, _ = st.columns([2, 5])
    with col_home:
        if st.button("← Analizza un altro documento", key="home"):
            st.session_state.vista = "input"
            st.session_state.risultato = None
            st.rerun()

# ════════════════════════════════════════════════════════════
# VISTA INPUT — pagina di caricamento
# ════════════════════════════════════════════════════════════
if st.session_state.vista == "input":

    # CSS specifico per la vista input: card centrata su sfondo colorato
    st.markdown("""
    <style>
    .block-container {
        max-width: 880px !important;
        margin: 0 auto !important;
        background: white !important;
        border-radius: 22px !important;
        box-shadow: 0 6px 32px rgba(108, 59, 245, 0.10) !important;
        border: 1px solid #EDE9FE !important;
        padding: 0 3rem 3rem !important;
    }
    /* Aumenta l'altezza del CTA */
    div[data-testid="stButton"] button[data-testid="baseButton-primary"] {
        height: 52px !important;
        font-size: 1.05rem !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # ── Hero ─────────────────────────────────────────────────
    st.markdown("""
    <div class="hero">
        <p class="brand">EasyRead</p>
        <div class="accent-bar"></div>
        <p class="headline">Hai ricevuto una lettera che non capisci?</p>
        <p class="subline">Caricala qui: te la spieghiamo con parole semplici
        e ti diciamo cosa devi fare.</p>
        <div class="badges">
            <span class="badge">Multa</span>
            <span class="badge">INPS</span>
            <span class="badge">Agenzia delle Entrate</span>
            <span class="badge">Comunicazioni bancarie</span>
            <span class="badge">Bollette</span>
            <span class="badge">Comune</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # ── Selezione tipo input ─────────────────────────────────
    st.markdown('<p class="sezione-label">Come vuoi darci il documento?</p>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3, gap="small")
    with c1:
        if st.button(
            "📄  Carica PDF",
            type="primary" if st.session_state.scelta_tipo == "pdf" else "secondary",
            use_container_width=True,
            key="btn_pdf",
        ):
            st.session_state.scelta_tipo = "pdf"
    with c2:
        if st.button(
            "✏️  Incolla testo",
            type="primary" if st.session_state.scelta_tipo == "testo" else "secondary",
            use_container_width=True,
            key="btn_testo",
        ):
            st.session_state.scelta_tipo = "testo"
    with c3:
        if st.button(
            "✨  Prova un esempio",
            type="primary" if st.session_state.scelta_tipo == "esempio" else "secondary",
            use_container_width=True,
            key="btn_esempio",
        ):
            st.session_state.scelta_tipo = "esempio"

    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)

    # ── Widget in base alla scelta ───────────────────────────
    scelta = st.session_state.scelta_tipo

    if scelta == "pdf":
        caricato = st.file_uploader(
            "Trascina qui il tuo PDF oppure clicca per sceglierlo",
            type="pdf",
            label_visibility="visible",
        )
        if caricato:
            st.session_state.testo = testo_da_pdf(caricato)
            st.success(f"Documento caricato: {len(st.session_state.testo):,} caratteri.")

    elif scelta == "testo":
        st.session_state.testo = st.text_area(
            "Testo del documento",
            value=st.session_state.testo,
            height=220,
            placeholder="Incolla qui il testo della lettera o del documento…",
            label_visibility="collapsed",
        )

    else:  # esempio
        st.markdown('<p class="sezione-label">Scegli un documento di esempio</p>', unsafe_allow_html=True)
        for etichetta, nome_file in ESEMPI.items():
            if st.button(etichetta, use_container_width=True, key=f"es_{nome_file}"):
                st.session_state.testo = carica_esempio(nome_file)
        if st.session_state.testo:
            st.success(f"Documento pronto: {len(st.session_state.testo):,} caratteri.")

    st.markdown("<div style='margin-top: 24px;'></div>", unsafe_allow_html=True)
    st.divider()

    # ── Lingua ───────────────────────────────────────────────
    st.markdown('<p class="sezione-label">In che lingua vuoi la spiegazione?</p>', unsafe_allow_html=True)
    lingua = LINGUE[
        st.selectbox(
            "lingua",
            list(LINGUE),
            label_visibility="collapsed",
            help="Il documento resta in italiano. Cambia solo la lingua della spiegazione.",
        )
    ]

    st.markdown("<div style='margin-top: 24px;'></div>", unsafe_allow_html=True)

    # ── CTA ──────────────────────────────────────────────────
    if st.button(
        "Spiegami questo documento",
        type="primary",
        use_container_width=True,
        disabled=not st.session_state.testo.strip(),
    ):
        st.session_state.lingua_analisi = lingua
        st.session_state.vista = "caricamento"
        st.rerun()

    st.markdown(
        '<p class="privacy-note">🔒 Il documento viene elaborato solo per generare la spiegazione.</p>',
        unsafe_allow_html=True,
    )

# ════════════════════════════════════════════════════════════
# VISTA CARICAMENTO — spinner mentre l'analisi gira
# ════════════════════════════════════════════════════════════
elif st.session_state.vista == "caricamento":
    # CSS per ingrandire e centrare lo spinner nativo di Streamlit
    st.markdown("""
    <style>
    .block-container { background: transparent !important; max-width:100% !important;
        box-shadow:none !important; border:none !important; border-radius:0 !important; }
    [data-testid="stSpinner"] {
        display: flex; flex-direction: column;
        align-items: center; justify-content: center;
        height: 70vh;
    }
    [data-testid="stSpinner"] > div {
        display: flex; flex-direction: column;
        align-items: center; gap: 20px;
    }
    [data-testid="stSpinner"] svg {
        width: 64px !important; height: 64px !important;
        color: #6C3BF5 !important;
    }
    [data-testid="stSpinner"] p {
        font-size: 1.1rem !important; color: #6B7280 !important;
        font-weight: 500 !important;
    }
    </style>
    """, unsafe_allow_html=True)

    import time
    with st.spinner("Sto analizzando il documento…"):
        try:
            if usa_finto:
                time.sleep(1.5)  # rende lo spinner visibile in modalità sviluppo
                st.session_state.risultato = risultato_finto()
                st.session_state.analisi_finta = True
            else:
                st.session_state.risultato = analizza_davvero(
                    st.session_state.testo, st.session_state.lingua_analisi
                )
                st.session_state.analisi_finta = False
            st.session_state.vista = "risultati"
        except Exception as errore:
            st.error(f"Non sono riuscito a leggere il documento: {errore}")
            st.session_state.vista = "input"
    st.rerun()

# ════════════════════════════════════════════════════════════
# VISTA RISULTATI
# ════════════════════════════════════════════════════════════
elif st.session_state.vista == "risultati" and st.session_state.risultato:
    # Reset stili della card input che potrebbero persistere nel DOM
    st.markdown("""
    <style>
    .block-container {
        background: transparent !important;
        max-width: 100% !important;
        box-shadow: none !important;
        border: none !important;
        border-radius: 0 !important;
        padding: 2rem 3rem !important;
    }
    </style>
    """, unsafe_allow_html=True)
    if st.session_state.analisi_finta:
        st.warning(
            "**Stai vedendo un risultato finto.** È un esempio fisso scritto nel codice: "
            "non ha letto il tuo documento. Per analizzarlo davvero, spegni "
            "**Modalità sviluppo** nella barra a sinistra.",
            icon="🧪",
        )
    mostra_risultato(st.session_state.risultato)
