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

    def test_point_in_time_events_ignore_future_and_apply_inactivation(self):
        rows = [
            {"source": "A", "target": "B", "layer": "industry", "effective_date": "2026-08-02", "active": True},
            {"source": "A", "target": "B", "layer": "industry", "effective_date": "2026-08-04", "active": False},
            {"source": "B", "target": "C", "layer": "industry", "effective_date": "2026-08-05", "active": True},
        ]
        before = build_graph.build(rows, nodes=["A", "B", "C"], date="2026-08-03")
        after = build_graph.build(rows, nodes=["A", "B", "C"], date="2026-08-04")
        self.assertEqual([(edge["source"], edge["target"]) for edge in before["edges"]], [("A", "B")])
        self.assertEqual(after["edges"], [])
        self.assertNotEqual(before["fingerprint"], after["fingerprint"])

    def test_formal_mode_rejects_static_rows(self):
        with self.assertRaises(ValueError):
            build_graph.build(self.rows, nodes=["A", "B"], date="2026-08-03")

    def test_layer_weight_changes_edge_weight(self):
        graph = build_graph.build(
            [{"source": "A", "target": "B", "layer": "concept", "effective_date": "2026-08-01", "weight": 2}],
            layer_weights={"concept": 0.25}, nodes=["A", "B"], date="2026-08-03",
        )
        self.assertEqual(graph["edges"][0]["weight"], 0.5)


if __name__ == "__main__":
    unittest.main()
