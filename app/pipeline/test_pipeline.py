"""
Script di test rapido per provare la pipeline degli agenti in locale.
Esegui dalla ROOT del progetto:

    cd c:/0_HACKHATON/easyread
    python -m app.pipeline.test_pipeline
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))

from app.pipeline import Orchestrator

DOCUMENTO_ESEMPIO = """
Agenzia delle Entrate - Riscossione
Raccomandata A/R

Contribuente: Mario Rossi
Codice Fiscale: RSSMRA80A01H501Z

AVVISO DI ACCERTAMENTO N. 2024/12345

Le comunichiamo che a seguito di controllo automatizzato della sua dichiarazione
dei redditi per l'anno d'imposta 2022, risulta un'imposta non versata pari a
€ 1.250,00 oltre a sanzioni di € 312,50 e interessi di € 45,80.

Totale dovuto: € 1.608,30

La invitiamo a regolarizzare la sua posizione entro il 30 novembre 2024.
In caso di mancato pagamento entro tale data, si procederà all'iscrizione a ruolo
con aggravio di ulteriori sanzioni.

Per informazioni: 800.90.96.96 oppure www.agenziaentrate.gov.it
"""

if __name__ == "__main__":
    print("Avvio pipeline EasyRead...\n")
    result = Orchestrator().process(DOCUMENTO_ESEMPIO)

    print(f"TIPO DOCUMENTO: {result.classifier.type_label} (confidenza: {result.classifier.confidence:.0%})")
    print(f"\nTESTO SEMPLIFICATO:\n{result.simplified_text}")
    print(f"\nAZIONI ({len(result.actions.actions)}):")
    for i, a in enumerate(result.actions.actions, 1):
        scadenza = f" — entro {a.deadline}" if a.deadline else ""
        importo = f" ({a.amount})" if a.amount else ""
        print(f"  {i}. [P{a.priority}] {a.description}{scadenza}{importo}")
    print(f"\nSAFETY: {'OK' if result.safety.verified else 'ATTENZIONE'}")
    if result.safety.warnings:
        for w in result.safety.warnings:
            print(f"  ⚠ {w}")
