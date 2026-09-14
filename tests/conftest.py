import sys
from pathlib import Path

# Rende importabile `pipeline.*` senza installare il pacchetto
sys.path.insert(0, str(Path(__file__).parent.parent / "app"))
