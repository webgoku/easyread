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


st.set_page_config(page_title="EasyRead", page_icon="📄", layout="centered")

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

    /* Metriche evidenziate */
    [data-testid="stMetric"] {
        background: #faf5ff; border-radius: 12px;
        padding: 16px 20px; border: 1px solid #e9d5ff;
    }
    [data-testid="stMetricLabel"] { font-size: 0.85rem !important; color: #6b7280; }
    [data-testid="stMetricValue"] { font-size: 1.5rem !important; font-weight: 700; color: #4c1d95; }

    /* Card azioni */
    [data-testid="stVerticalBlock"] > [data-testid="stVerticalBlock"] {
        border-radius: 10px;
    }

    /* Bottone nuovo documento */
    .nuovo-doc { text-align: right; margin-bottom: 8px; }

    /* Responsive: compatta su schermi piccoli */
    @media (max-width: 640px) {
        .intestazione .marchio { font-size: 2.6rem; }
        .intestazione .domanda { font-size: 1.2rem; }
        [data-testid="stMetricValue"] { font-size: 1.2rem !important; }
    }
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
            "L'Agenzia delle Entrate ha confrontato la tua dichiarazione dei redditi "
            "del 2024 con i dati del tuo datore di lavoro e ha trovato una differenza.\n\n"
            "Dalla tua dichiarazione risultano 28.450,00 euro di stipendio, ma il datore "
            "di lavoro ne ha comunicati 31.200,00. La differenza è di 2.750,00 euro.\n\n"
            "Per questa differenza ti viene chiesto di versare 644,92 euro, che includono "
            "l'imposta non pagata, una sanzione e gli interessi di mora.\n\n"
            "Se ritieni che ci sia un errore, hai la possibilità di inviare i tuoi documenti "
            "giustificativi tramite il servizio CIVIS. Non sei obbligato a pagare immediatamente."
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
                    description="Se pensi che l'importo sia sbagliato, invia i tuoi documenti tramite il servizio CIVIS sul sito dell'Agenzia delle Entrate.",
                    deadline="31 ottobre 2026",
                    amount=None,
                    priority=2,
                ),
                Action(
                    description="Rivolgiti a un CAF o a un patronato per ricevere assistenza gratuita.",
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
                    definition="È un modulo per pagare le imposte allo Stato. Si compila in banca, alla posta o online sul sito dell'Agenzia delle Entrate.",
                ),
                GlossaryTerm(
                    term="CIVIS",
                    definition="Servizio online dell'Agenzia delle Entrate per inviare documenti e richiedere chiarimenti senza recarsi allo sportello.",
                ),
                GlossaryTerm(
                    term="CAF",
                    definition="Centro di Assistenza Fiscale. Offre supporto gratuito per le pratiche fiscali e la compilazione delle dichiarazioni.",
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

    # Riepilogo cifre in evidenza
    if r.actions.amounts or r.actions.deadlines:
        a, b = st.columns(2)
        if r.actions.amounts:
            a.metric("Da versare", r.actions.amounts[0])
        if r.actions.deadlines:
            b.metric("Entro il", r.actions.deadlines[0])
        st.write("")

    st.subheader("Di cosa si tratta")
    corpo = "".join(
        f"<p>{par.strip()}</p>"
        for par in r.simplified_text.split("\n\n")
        if par.strip()
    )
    st.markdown(f'<div class="blocco-semplice">{corpo}</div>', unsafe_allow_html=True)

    if r.actions.actions:
        st.subheader("Cosa fare")
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
        "Non fornisce consigli fiscali o legali.**\n\n"
        "Per qualsiasi decisione, rivolgiti a un CAF, a un patronato o a un "
        "commercialista. Molti di questi servizi sono gratuiti.",
        icon="ℹ️",
    )


# ── Intestazione ──────────────────────────────────────────────────────────────

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

st.divider()

# ── Session state ──────────────────────────────────────────────────────────────

if "testo" not in st.session_state:
    st.session_state.testo = ""
if "risultato" not in st.session_state:
    st.session_state.risultato = None

# ── Form di input (nascosta dopo l'analisi) ───────────────────────────────────

if st.session_state.risultato is not None:
    col1, col2 = st.columns([4, 1])
    col1.caption(f"📄 Documento analizzato · {len(st.session_state.testo)} caratteri")
    if col2.button("Nuovo documento", use_container_width=True):
        st.session_state.risultato = None
        st.session_state.testo = ""
        st.rerun()
else:
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
            st.rerun()
        else:
            with st.spinner("Sto leggendo il documento. Ci vogliono alcuni minuti."):
                try:
                    st.session_state.risultato = analizza_davvero(
                        st.session_state.testo, lingua
                    )
                    st.rerun()
                except Exception as errore:
                    st.error(f"Non sono riuscito a leggere il documento: {errore}")

# ── Risultato ─────────────────────────────────────────────────────────────────

if st.session_state.risultato is not None:
    if usa_finto:
        st.warning(
            "**Stai vedendo un risultato di esempio.** Il documento non è stato analizzato. "
            "Per l'analisi reale, disattiva la **Modalità sviluppo** nella barra a sinistra.",
            icon="🧪",
        )
    mostra_risultato(st.session_state.risultato)
