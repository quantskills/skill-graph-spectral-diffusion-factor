import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import build_graph
import compute_spectral_features as spectral


class SpectralTests(unittest.TestCase):
    def setUp(self):
        self.graph = build_graph.build([
            {"source": "A", "target": "B", "layer": "industry", "weight": 1},
            {"source": "B", "target": "C", "layer": "industry", "weight": 1},
            {"source": "D", "target": "D", "layer": "industry", "weight": 1},
        ])

    def test_robust_z_constant_is_zero(self):
        self.assertEqual(spectral.robust_z({"A": 1, "B": 1}), {"A": 0.0, "B": 0.0})

    def test_low_high_decomposition(self):
        result = spectral.compute({"A": -1, "B": 0, "C": 1}, {"A": -2, "B": 0, "C": 2}, self.graph, 2)
        for node in ("A", "B", "C"):
            self.assertAlmostEqual(result[node]["standardized"], result[node]["low"] + result[node]["high"])

    def test_isolated_node_fails_closed(self):
        result = spectral.compute({"A": 1, "B": 2, "C": 3, "D": 4}, {"A": 0, "B": 1, "C": 2, "D": 3}, self.graph)
        self.assertEqual(result["D"]["status"], "isolated_node")
        self.assertIsNone(result["D"]["low"])

    def test_missing_previous_signal_blocks_lag(self):
        result = spectral.compute({"A": 1, "B": 2, "C": 3}, {"A": 0, "B": 1}, self.graph)
        self.assertEqual(result["C"]["status"], "missing_lag")
        self.assertIsNone(result["C"]["neighbor_lag"])


if __name__ == "__main__":
    unittest.main()
