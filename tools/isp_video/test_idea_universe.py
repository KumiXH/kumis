"""Regression checks for the deterministic mobile-video idea universe."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from build_idea_universe import AXES, make_legacy_ideas, make_native_ideas, make_prior_ideas, make_variants, validate


class IdeaUniverseTests(unittest.TestCase):
    def test_native_ideas_are_large_and_unique(self) -> None:
        ideas = make_native_ideas()
        self.assertGreaterEqual(len(ideas), 800)
        self.assertEqual(len(ideas), len({row["idea_id"] for row in ideas}))
        self.assertEqual(len(ideas), len({row["name_zh"] for row in ideas}))

    def test_prior_examples_are_preserved(self) -> None:
        text = "\n".join(row["name_zh"] for row in make_prior_ideas())
        for term in ["计算底片", "对象级快门", "动态星芒", "虚拟光", "多手机", "Event", "生成"]:
            self.assertIn(term, text)

    def test_every_idea_receives_all_single_axis_variants(self) -> None:
        ideas = make_prior_ideas()[:3] + make_native_ideas()[:3]
        variants = make_variants(ideas)
        expected = len(ideas) * sum(len(axis["values"]) for axis in AXES.values())
        self.assertEqual(expected, len(variants))
        self.assertEqual(len(variants), len({row["variant_id"] for row in variants}))

    def test_validation_accepts_complete_minimal_legacy_set(self) -> None:
        legacy = [{
            "id": "OP-001",
            "name_zh": "动态星芒方向",
            "family": "computational_optics",
            "family_zh": "计算光学与虚拟镜头",
            "input_signals": ["video"],
            "scenarios": ["夜景"],
            "truth_boundary": "perceptual",
            "algorithm_family": ["rendering"],
            "failure_modes": ["闪烁"],
        }]
        ideas = make_legacy_ideas(legacy) + make_prior_ideas() + make_native_ideas()
        variants = make_variants(ideas)
        result = validate(ideas, variants, len(legacy))
        self.assertTrue(result["legacy_complete"])
        self.assertTrue(result["axis_counts_match"])


if __name__ == "__main__":
    unittest.main()
