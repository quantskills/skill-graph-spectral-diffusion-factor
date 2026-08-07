import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import build_graph


class GraphTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = json.loads((ROOT / "tests/fixtures/minimal_panel/relationships.json").read_text())

    def test_merges_duplicate_undirected_edges(self):
        graph = build_graph.build(self.rows)
        edge = next(item for item in graph["edges"] if {item["source"], item["target"]} == {"A", "B"})
        self.assertEqual(edge["weight"], 2.0)

    def test_self_loop_keeps_node_but_not_edge(self):
        graph = build_graph.build(self.rows)
        self.assertIn("D", graph["nodes"])
        self.assertEqual(graph["degree"].get("D", 0.0), 0.0)

    def test_fingerprint_is_order_invariant(self):
        self.assertEqual(build_graph.build(self.rows)["fingerprint"], build_graph.build(list(reversed(self.rows)))["fingerprint"])

    def test_normalized_neighbors_are_symmetric(self):
        graph = build_graph.build(self.rows)
        neighbors = build_graph.normalized_neighbors(graph)
        ab = dict(neighbors["A"])["B"]
        ba = dict(neighbors["B"])["A"]
        self.assertAlmostEqual(ab, ba)


if __name__ == "__main__":
    unittest.main()
