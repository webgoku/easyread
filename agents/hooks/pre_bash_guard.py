"""
Hook PreToolUse — Bash

Intercetta comandi Bash potenzialmente distruttivi o rischiosi prima
che Claude li esegua, emettendo un avviso leggibile nei log.

Comandi monitorati:
  git push --force  → può sovrascrivere la storia remota condivisa
  rm -rf            → eliminazione ricorsiva irreversibile
  git reset --hard  → scarta modifiche non committate
"""

import json
import sys


PATTERN_RISCHIOSI = [
    ("git push --force",  "⚠️  Force push: sovrascrive la storia remota. Conferma l'intenzione."),
    ("git push -f",       "⚠️  Force push: sovrascrive la storia remota. Conferma l'intenzione."),
    ("rm -rf",            "⚠️  Eliminazione ricorsiva irreversibile. Controlla il percorso."),
    ("git reset --hard",  "⚠️  Reset hard: le modifiche non committate andranno perse."),
    ("git clean -f",      "⚠️  git clean -f: i file non tracciati verranno eliminati."),
    ("DROP TABLE",        "⚠️  Operazione distruttiva su database rilevata."),
]


def main() -> None:
    try:
        payload = json.load(sys.stdin)
        comando = payload.get("tool_input", {}).get("command", "")
    except Exception:
        return

    for pattern, messaggio in PATTERN_RISCHIOSI:
        if pattern.lower() in comando.lower():
            print(f"\n[Hook] {messaggio}")
            print(f"[Hook] Comando: {comando.strip()}")


if __name__ == "__main__":
    main()
