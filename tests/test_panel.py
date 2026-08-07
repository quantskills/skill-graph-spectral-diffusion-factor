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
        values, _ = build_diffusion_panel.build(self.panel, self.relationships, allow_static_fixture=True)
        second = [row for row in values if row["date"] == "2026-08-04" and row["symbol"] in {"A", "B", "C"}]
        self.assertEqual(len(second), 3)
        self.assertTrue(all(row["graph_diffusion_confirmation"] is not None for row in second))
        self.assertTrue(all(row["graph_residual_reversal"] is not None for row in second))

    def test_first_date_has_missing_lag(self):
        values, _ = build_diffusion_panel.build(self.panel, self.relationships, allow_static_fixture=True)
        first = [row for row in values if row["date"] == "2026-08-03" and row["symbol"] == "A"][0]
        self.assertEqual(first["factor_status"], "missing_lag")
        self.assertIsNone(first["graph_diffusion_confirmation"])

    def test_panel_nodes_are_not_replaced_by_graph_nodes(self):
        panel = [dict(self.panel[0]), dict(self.panel[0], symbol="Z")]
        values, _ = build_diffusion_panel.build(panel, [{"source": "A", "target": "B", "layer": "industry", "weight": 1}], allow_static_fixture=True)
        self.assertEqual({row["symbol"] for row in values}, {"A", "Z"})

    def test_isolated_node_stays_unavailable(self):
        values, _ = build_diffusion_panel.build(self.panel, self.relationships, allow_static_fixture=True)
        isolated = [row for row in values if row["symbol"] == "D"]
        self.assertTrue(all(row["factor_status"] == "isolated_node" for row in isolated))

    def test_configured_channel_fields_are_applied(self):
        panel = []
        for row in self.panel:
            item = dict(row)
            item["custom_momentum"] = item["momentum"]
            panel.append(item)
        config = {
            "channels": {
                "momentum": ["custom_momentum"],
                "liquidity": ["liquidity", "cal_10d_120d_turnover_ratio"],
                "risk": ["residual_volatility", "cal_30d_close_std_ratio"],
            }
        }
        values, _ = build_diffusion_panel.build(panel, self.relationships, config=config, allow_static_fixture=True)
        later = [row for row in values if row["date"] == "2026-08-04"]
        self.assertTrue(any(row["factor_status"] == "available" for row in later))

    def test_min_degree_blocks_low_degree_nodes(self):
        values, _ = build_diffusion_panel.build(
            self.panel, self.relationships, config={"min_degree": 10.0}, allow_static_fixture=True,
        )
        self.assertTrue(all(row["factor_status"] in {"below_min_degree", "isolated_node"} for row in values))

    def test_correlation_layer_fails_closed(self):
        with self.assertRaises(ValueError):
            build_diffusion_panel.build(
                self.panel, self.relationships, config={"graph_layers": ["correlation"]}, allow_static_fixture=True,
            )


if __name__ == "__main__":
    unittest.main()
