"""EasyRead — interfaccia per leggere facile i documenti della Pubblica Amministrazione."""

import sys
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

QUI = Path(__file__).resolve().parent
RADICE = QUI.parent
sys.path.insert(0, str(QUI))
load_dotenv(RADICE / ".env", override=True)

from pipeline.models import DocumentType, EasyReadResult


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


st.set_page_config(
    page_title="EasyRead",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={},
)

# ── CSS globale ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* Nasconde elementi Streamlit non necessari */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
[data-testid="stDecoration"]  { display: none; }
[data-testid="stDeployButton"]{ display: none; }
[data-testid="stHeader"] { background: transparent !important; border-bottom: none !important; }
/* Sidebar e toggle nascosti — nessuna opzione da mostrare */
[data-testid="stSidebar"]       { display: none !important; }
[data-testid="collapsedControl"]{ display: none !important; }

/* Sfondo pagina */
.stApp { background: #F0EDF8; }

/* Fade-in della card al caricamento */
@keyframes fadeSlideIn {
    from { opacity: 0; transform: translateY(16px); }
    to   { opacity: 1; transform: translateY(0); }
}
.block-container {
    animation: fadeSlideIn 0.35s ease-out;
}

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

/* Metriche evidenziate */
[data-testid="stMetric"] {
    background: #4C1D95;
    border-radius: 14px;
    padding: 20px 24px;
    border: none;
}
[data-testid="stMetricLabel"] {
    font-size: 1rem !important;
    color: #DDD6FE !important;
    font-weight: 500 !important;
}
[data-testid="stMetricValue"] {
    font-size: 2rem !important;
    font-weight: 800 !important;
    color: #FFFFFF !important;
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

/* Alert scadenza */
.alert-scadenza {
    display: flex; align-items: flex-start; gap: 14px;
    padding: 16px 20px; border-radius: 14px; margin: 12px 0 20px;
}
.alert-scadenza .icona { font-size: 1.8rem; flex-shrink: 0; line-height: 1; }
.alert-scadenza .testo strong {
    display: block; font-size: 1.05rem; font-weight: 700; margin-bottom: 3px;
}
.alert-scadenza .testo p { margin: 0; font-size: 0.95rem; opacity: 0.9; }
.alert-scaduta  { background: #FEF2F2; border-left: 5px solid #EF4444; color: #991B1B; }
.alert-urgente  { background: #FFF7ED; border-left: 5px solid #F97316; color: #9A3412; }
.alert-vicina   { background: #FEFCE8; border-left: 5px solid #EAB308; color: #854D0E; }

/* Testo base */
html, body, [class*="css"] { font-size: 18px; }
.main p, .main li { font-size: 1.05rem; line-height: 1.75; }
</style>
""", unsafe_allow_html=True)


# ── Footer fisso ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
.easyread-footer {
    position: fixed;
    bottom: 0; left: 0; right: 0;
    text-align: center;
    padding: 8px 0;
    font-size: 0.75rem;
    color: #9CA3AF;
    background: transparent;
    z-index: 100;
    pointer-events: none;
}
</style>
<div class="easyread-footer">
    EasyRead v1.0 &nbsp;·&nbsp; Hagenthon 2026 — Tema 01 Accessibilità Digitale &nbsp;·&nbsp; © 2026
</div>
""", unsafe_allow_html=True)

# ── Funzioni (logica invariata) ──────────────────────────────────────────────

def testo_da_pdf(percorso_o_file) -> str:
    from pypdf import PdfReader
    return "\n".join(p.extract_text() or "" for p in PdfReader(percorso_o_file).pages)




def analizza_davvero(testo: str, lingua: str, on_step=None) -> EasyReadResult:
    from pipeline import Orchestrator
    return Orchestrator().process(testo, lingua, on_step=on_step)


def trascrivi_immagine(file) -> str:
    """Invia la foto a Claude Vision e restituisce il testo trascritto."""
    import anthropic, base64
    dati = base64.standard_b64encode(file.read()).decode("utf-8")
    media_type = file.type  # "image/jpeg", "image/png", ecc.
    client = anthropic.Anthropic()
    msg = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=4096,
        messages=[{
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {"type": "base64", "media_type": media_type, "data": dati},
                },
                {
                    "type": "text",
                    "text": (
                        "Trascrivi fedelmente tutto il testo visibile in questa immagine, "
                        "mantenendo la struttura originale (titoli, paragrafi, elenchi). "
                        "Rispondi solo con il testo trascritto, senza commenti o spiegazioni."
                    ),
                },
            ],
        }],
    )
    return msg.content[0].text


import re as _re
from datetime import date as _date, datetime as _datetime

_MESI_IT = {
    "gennaio": 1, "febbraio": 2, "marzo": 3, "aprile": 4,
    "maggio": 5, "giugno": 6, "luglio": 7, "agosto": 8,
    "settembre": 9, "ottobre": 10, "novembre": 11, "dicembre": 12,
}

def _parse_deadline(testo: str) -> _date | None:
    """Converte una stringa data in formato italiano in un oggetto date."""
    t = testo.strip()
    # gg/mm/aaaa  o  gg-mm-aaaa
    m = _re.match(r"^(\d{1,2})[/\-](\d{1,2})[/\-](\d{4})$", t)
    if m:
        try:
            return _date(int(m.group(3)), int(m.group(2)), int(m.group(1)))
        except ValueError:
            pass
    # gg mese aaaa  (es. "31 ottobre 2026")
    m = _re.match(r"^(\d{1,2})\s+([a-zà-ù]+)\s+(\d{4})$", t.lower())
    if m:
        mese = _MESI_IT.get(m.group(2))
        if mese:
            try:
                return _date(int(m.group(3)), mese, int(m.group(1)))
            except ValueError:
                pass
    return None


def _mostra_alert_scadenza(deadlines: list[str]) -> None:
    """Mostra un banner colorato se la scadenza è vicina o già passata."""
    oggi = _date.today()
    for testo_data in deadlines:
        dt = _parse_deadline(testo_data)
        if dt is None:
            continue
        delta = (dt - oggi).days
        if delta < 0:
            html = (
                f'<div class="alert-scadenza alert-scaduta">'
                f'<span class="icona">🚨</span>'
                f'<div class="testo"><strong>Scadenza superata</strong>'
                f'<p>La scadenza del {testo_data} è già passata da {abs(delta)} giorn{"o" if abs(delta)==1 else "i"}. '
                f'Contatta subito un CAF o un patronato.</p></div></div>'
            )
        elif delta <= 7:
            html = (
                f'<div class="alert-scadenza alert-urgente">'
                f'<span class="icona">⚠️</span>'
                f'<div class="testo"><strong>Scadenza urgente — {delta} giorn{"o" if delta==1 else "i"} rimast{"o" if delta==1 else "i"}</strong>'
                f'<p>Devi agire entro il {testo_data}. Non aspettare.</p></div></div>'
            )
        elif delta <= 30:
            html = (
                f'<div class="alert-scadenza alert-vicina">'
                f'<span class="icona">📅</span>'
                f'<div class="testo"><strong>Scadenza vicina — {delta} giorni rimasti</strong>'
                f'<p>Hai tempo fino al {testo_data}. Organizzati per tempo.</p></div></div>'
            )
        else:
            continue
        st.markdown(html, unsafe_allow_html=True)
        break  # mostra solo la prima scadenza con alert


def _md_to_html(testo: str) -> str:
    """Converte markdown bold in HTML e normalizza i paragrafi."""
    paragrafi = []
    for par in testo.split("\n\n"):
        par = par.strip()
        if not par:
            continue
        # **Titolo** su riga singola → titoletto in grassetto
        if _re.match(r"^\*\*.+\*\*$", par):
            contenuto = par.strip("*")
            paragrafi.append(f"<p><strong>{contenuto}</strong></p>")
        else:
            # **testo** inline → <strong>
            par = _re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", par)
            # newline singoli → <br>
            par = par.replace("\n", "<br>")
            paragrafi.append(f"<p>{par}</p>")
    return "".join(paragrafi)


def mostra_risultato(r: EasyReadResult) -> None:
    icona = ICONE_TIPO.get(r.classifier.document_type, "📄")
    st.caption(f"{icona}  {r.classifier.type_label}")

    _mostra_alert_scadenza(r.actions.deadlines)

    # Riepilogo cifre in evidenza, in base allo stato del pagamento
    status = r.actions.payment_status
    importo = r.actions.amounts[0] if r.actions.amounts else None
    scadenza = r.actions.deadlines[0] if r.actions.deadlines else None

    if status == "gia_pagato":
        msg = f"Hai già pagato {importo}." if importo else "Il pagamento risulta già effettuato."
        st.success(f"**Pagamento già effettuato** — {msg} Non devi fare nulla.", icon="✅")
        if scadenza:
            st.metric("Data scadenza", scadenza)
    elif status == "parzialmente_pagato":
        col_a, col_b, col_c = st.columns([1, 1, 2])
        if importo:
            col_a.metric("Saldo residuo", importo)
        if scadenza:
            col_b.metric("Entro il", scadenza)
    elif status == "da_pagare":
        col_a, col_b, col_c = st.columns([1, 1, 2])
        if importo:
            col_a.metric("Da versare", importo)
        if scadenza:
            col_b.metric("Entro il", scadenza)
    elif r.actions.amounts or r.actions.deadlines:
        col_a, col_b, col_c = st.columns([1, 1, 2])
        if importo:
            col_a.metric("Importo principale", importo)
        if scadenza:
            col_b.metric("Prima scadenza", scadenza)

    st.divider()

    col_sx, col_dx = st.columns([1, 1], gap="large")

    with col_sx:
        st.subheader("Cosa dice questo documento")
        st.markdown(
            f'<div class="blocco-semplice">{_md_to_html(r.simplified_text)}</div>',
            unsafe_allow_html=True,
        )

    with col_dx:
        st.subheader("Cosa devi fare")
        if r.actions.actions:
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
        else:
            st.success(
                "Per questo documento non devi fare nulla. "
                "Conservalo per i tuoi archivi.",
                icon="✅",
            )

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
    ("testo", ""),
    ("scelta_tipo", "pdf"),  # valori: "pdf" | "foto" | "testo"
    ("lingua_analisi", "italiano"),
]:
    if _k not in st.session_state:
        st.session_state[_k] = _v


# ── Tasto Home (solo nella vista risultati) ──────────────────────────────────
if st.session_state.vista == "risultati":
    col_home, _ = st.columns([2, 5])
    with col_home:
        if st.button("← Analizza un altro documento", key="home"):
            st.session_state.vista = "input"
            st.session_state.risultato = None
            st.session_state.testo = ""
            st.session_state.scelta_tipo = "pdf"
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
        margin: 2.5rem auto !important;
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
            st.rerun()
    with c2:
        if st.button(
            "📷  Carica foto",
            type="primary" if st.session_state.scelta_tipo == "foto" else "secondary",
            use_container_width=True,
            key="btn_foto",
        ):
            st.session_state.scelta_tipo = "foto"
            st.rerun()
    with c3:
        if st.button(
            "✏️  Incolla testo",
            type="primary" if st.session_state.scelta_tipo == "testo" else "secondary",
            use_container_width=True,
            key="btn_testo",
        ):
            st.session_state.scelta_tipo = "testo"
            st.rerun()

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

    elif scelta == "foto":
        foto = st.file_uploader(
            "Carica una foto del documento (JPG, PNG, WEBP)",
            type=["jpg", "jpeg", "png", "webp"],
            label_visibility="visible",
        )
        if foto:
            with st.spinner("Leggo il testo dalla foto…"):
                st.session_state.testo = trascrivi_immagine(foto)
            st.success(f"Foto letta: {len(st.session_state.testo):,} caratteri trascritti.")

    elif scelta == "testo":
        st.session_state.testo = st.text_area(
            "Testo del documento",
            value=st.session_state.testo,
            height=220,
            placeholder="Incolla qui il testo della lettera o del documento…",
            label_visibility="collapsed",
        )


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
    .block-container {
        max-width: 880px !important;
        margin: 2.5rem auto !important;
        background: white !important;
        border-radius: 22px !important;
        box-shadow: 0 6px 32px rgba(108, 59, 245, 0.10) !important;
        border: 1px solid #EDE9FE !important;
        padding: 0 3rem 3rem !important;
    }
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

    try:
        with st.status("Sto leggendo il documento…", expanded=True) as stato:
            def on_step(msg: str) -> None:
                st.write(msg)
                stato.update(label=msg)

            st.session_state.risultato = analizza_davvero(
                st.session_state.testo,
                st.session_state.lingua_analisi,
                on_step=on_step,
            )
            stato.update(label="✅ Analisi completata!", state="complete")
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
    mostra_risultato(st.session_state.risultato)
