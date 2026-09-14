"""Verifica le funzioni di utilità: parsing JSON dalle risposte LLM e regex del Safety Agent."""

import pytest

from pipeline.base_agent import _extract_json
from pipeline.safety_agent import _extract_amounts, _extract_dates


# ── _extract_json ─────────────────────────────────────────────────────────────

class TestExtractJson:
    def test_json_puro(self):
        raw = '{"chiave": "valore"}'
        assert _extract_json(raw) == '{"chiave": "valore"}'

    def test_markdown_code_block_con_lingua(self):
        raw = '```json\n{"chiave": "valore"}\n```'
        result = _extract_json(raw)
        assert '"chiave"' in result and '"valore"' in result

    def test_markdown_code_block_senza_lingua(self):
        raw = '```\n{"chiave": "valore"}\n```'
        result = _extract_json(raw)
        assert '"chiave"' in result

    def test_testo_prima_e_dopo(self):
        raw = 'Ecco il risultato:\n{"chiave": "valore"}\nFine.'
        result = _extract_json(raw)
        assert '"chiave"' in result

    def test_json_annidato(self):
        raw = '{"esterno": {"interno": 42}}'
        result = _extract_json(raw)
        assert '"esterno"' in result
        assert '"interno"' in result

    def test_nessun_json_solleva_eccezione(self):
        with pytest.raises(ValueError, match="Nessun oggetto JSON"):
            _extract_json("Nessun JSON qui, solo testo.")

    def test_json_su_piu_righe(self):
        raw = '{\n  "chiave": "valore",\n  "numero": 42\n}'
        result = _extract_json(raw)
        assert '"numero"' in result


# ── Safety Agent regex ────────────────────────────────────────────────────────

class TestExtractAmounts:
    def test_importo_con_simbolo_euro(self):
        matches = _extract_amounts("Devi pagare € 29,40 entro 10 giorni.")
        assert any("29,40" in m for m in matches)

    def test_importo_grande_con_punto_separatore(self):
        matches = _extract_amounts("L'importo è € 1.250,00.")
        assert any("1.250,00" in m for m in matches)

    def test_numero_senza_euro_non_catturato(self):
        # Evita falsi positivi su codici fiscali e numeri di telefono
        assert _extract_amounts("Codice: 90.96.123") == []

    def test_piu_importi(self):
        testo = "Imposta € 578,00, sanzione € 57,80, interessi € 9,12."
        matches = _extract_amounts(testo)
        assert len(matches) == 3


class TestExtractDates:
    def test_formato_slash(self):
        matches = _extract_dates("Violazione del 28/07/2026 alle ore 9:32.")
        assert any("28/07/2026" in m for m in matches)

    def test_formato_trattino(self):
        matches = _extract_dates("Scadenza: 07-08-2026.")
        assert any("07-08-2026" in m for m in matches)

    def test_formato_testuale(self):
        matches = _extract_dates("Entro il 31 ottobre 2026.")
        assert any("31 ottobre 2026" in m for m in matches)

    def test_numero_telefono_non_catturato(self):
        # I telefoni usano il punto come separatore — non devono essere date
        assert _extract_dates("Chiama il 06.123.456.78 per info.") == []

    def test_piu_date(self):
        testo = "Infrazione il 28/07/2026. Pagare entro il 07/08/2026."
        matches = _extract_dates(testo)
        assert len(matches) == 2
