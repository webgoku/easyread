"""
Hook PostToolUse — Edit / Write

Viene eseguito automaticamente da Claude Code dopo ogni modifica a un file.
Legge il tool input da stdin (JSON) e decide cosa fare in base al file modificato:

  models.py        → lancia l'intera suite pytest (è il contratto tra pipeline e UI)
  app/pipeline/*.py → lancia pytest per verificare che la pipeline non si rompa
  prompts/*.txt    → verifica che payment_status sia ancora definito nel prompt action
  altri file .py   → controllo sintattico rapido con py_compile
"""

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent


def run(cmd: list[str]) -> int:
    result = subprocess.run(cmd, cwd=ROOT)
    return result.returncode


def main() -> None:
    try:
        payload = json.load(sys.stdin)
        file_path = payload.get("tool_input", {}).get("file_path", "")
    except Exception:
        return  # stdin vuoto o non JSON — nessuna azione

    path = Path(file_path)

    # ── models.py: contratto pipeline↔UI — esegui l'intera suite ──────────────
    if path.name == "models.py":
        print("\n[Hook] models.py modificato — verifico che i test passino ancora…")
        rc = run([sys.executable, "-m", "pytest", "tests/", "-q", "--tb=short"])
        if rc != 0:
            print("[Hook] ⚠️  ATTENZIONE: alcuni test sono falliti dopo la modifica a models.py.")
            print("[Hook]    models.py è il contratto tra pipeline e UI — aggiorna anche i test.")
        else:
            print("[Hook] ✅  Tutti i test passano.")
        return

    # ── pipeline Python: esegui la suite ──────────────────────────────────────
    if "app/pipeline" in file_path.replace("\\", "/") and path.suffix == ".py":
        print("\n[Hook] File pipeline modificato — eseguo i test di regressione…")
        rc = run([sys.executable, "-m", "pytest", "tests/", "-q", "--tb=line"])
        if rc != 0:
            print("[Hook] ⚠️  Regressione rilevata. Controlla i test prima di committare.")
        else:
            print("[Hook] ✅  Nessuna regressione.")
        return

    # ── prompt action.txt: verifica che payment_status sia presente ───────────
    if "action.txt" in file_path:
        content = Path(file_path).read_text(encoding="utf-8") if Path(file_path).exists() else ""
        if "payment_status" not in content:
            print("\n[Hook] ⚠️  ATTENZIONE: action.txt non menziona 'payment_status'.")
            print("[Hook]    Il campo è obbligatorio in ActionResult — aggiungilo al prompt.")
        else:
            print("[Hook] ✅  payment_status presente nel prompt action.")
        return

    # ── qualsiasi altro .py: controllo sintattico rapido ─────────────────────
    if path.suffix == ".py" and Path(file_path).exists():
        rc = run([sys.executable, "-m", "py_compile", file_path])
        if rc != 0:
            print(f"\n[Hook] ⚠️  Errore di sintassi in {path.name}.")


if __name__ == "__main__":
    main()
