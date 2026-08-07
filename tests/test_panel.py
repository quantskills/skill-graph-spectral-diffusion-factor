import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import build_diffusion_panel
import normalize_factor_panel


class PanelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.panel = json.loads((ROOT / "tests/fixtures/minimal_panel/panel.json").read_text())
        cls.relationships = json.loads((ROOT / "tests/fixtures/minimal_panel/relationships.json").read_text())

    def test_channel_requires_both_fields(self):
        rows = [dict(self.panel[0])]
        rows[0]["cal_daily_rise"] = None
        result = normalize_factor_panel.normalize(rows)
        self.assertIsNone(result[0]["momentum"])

    def test_second_date_has_primary_outputs(self):
        values, diagnostics, graph = build_diffusion_panel.build(self.panel, self.relationships)
        second = [row for row in values if row["date"] == "2026-08-04" and row["symbol"] in {"A", "B", "C"}]
        self.assertEqual(len(second), 3)
        self.assertTrue(all(row["graph_diffusion_confirmation"] is not None for row in second))
        self.assertTrue(all(row["graph_residual_reversal"] is not None for row in second))

    def test_first_date_has_missing_lag(self):
        values, _, _ = build_diffusion_panel.build(self.panel, self.relationships)
        first = [row for row in values if row["date"] == "2026-08-03" and row["symbol"] == "A"][0]
        self.assertEqual(first["factor_status"], "missing_lag")
        self.assertIsNone(first["graph_diffusion_confirmation"])

    def test_isolated_node_stays_unavailable(self):
        values, _, _ = build_diffusion_panel.build(self.panel, self.relationships)
        isolated = [row for row in values if row["symbol"] == "D"]
        self.assertTrue(all(row["factor_status"] == "isolated_node" for row in isolated))


if __name__ == "__main__":
    unittest.main()
