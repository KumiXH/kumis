"""Integration tests for the unified video-effect research library."""

from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from tools.video_effects import build_library, effect_catalog


ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / "daily" / "20260827_录像特效调研"
STATS = PROJECT / "metadata" / "effect_stats.json"
README = PROJECT / "README.md"
FULL_REPORT = PROJECT / "report" / "手机录像特效玩法全量库_20260827.md"


class BuildLibraryTests(unittest.TestCase):
    def test_build_outputs_match_catalog_counts_and_cover_every_idea(self) -> None:
        self.assertTrue(STATS.exists())
        self.assertTrue(README.exists())
        self.assertTrue(FULL_REPORT.exists())
        stats = json.loads(STATS.read_text(encoding="utf-8"))
        self.assertEqual(stats["counts"], {"atoms": 120, "ideas": 300, "recipes": 200, "priorities": 50})
        self.assertEqual(set(stats["idea_family_counts"]), set(effect_catalog.IDEA_FAMILY_ORDER))

        report = FULL_REPORT.read_text(encoding="utf-8")
        for family in effect_catalog.IDEA_FAMILY_ORDER:
            self.assertIn(f"## {family}", report)
        for idea in effect_catalog.build_ideas():
            self.assertIn(idea["effect_id"], report)
            self.assertIn(idea["visible_effect"], report)

    def test_repeated_build_is_byte_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory) / "library"
            first = build_library.build_all(project_root=root)
            first_hashes = {
                name: hashlib.sha256(path.read_bytes()).hexdigest()
                for name, path in first.items()
            }
            second = build_library.build_all(project_root=root)
            second_hashes = {
                name: hashlib.sha256(path.read_bytes()).hexdigest()
                for name, path in second.items()
            }
            self.assertEqual(first_hashes, second_hashes)


if __name__ == "__main__":
    unittest.main()
