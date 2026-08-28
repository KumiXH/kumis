"""Contract tests for evidence records and concept storyboards."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from PIL import Image

from tools.video_effects import build_references, schema


ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / "daily" / "20260827_录像特效调研"
REFERENCE_MANIFEST = PROJECT / "references" / "reference_manifest.jsonl"
STORYBOARD_MANIFEST = PROJECT / "figures" / "effect_storyboards" / "storyboard_manifest.jsonl"


class ReferenceAndStoryboardTests(unittest.TestCase):
    def test_reference_specs_cover_all_priority_effects(self) -> None:
        records = build_references.build_reference_records()
        for record in records:
            schema.validate_reference(record)

        priorities = build_references.read_jsonl(
            PROJECT / "metadata" / "priority_effects.jsonl"
        )
        covered = {
            effect_id
            for record in records
            for effect_id in record["effect_ids"]
        }
        self.assertFalse(
            sorted({row["effect_id"] for row in priorities} - covered),
            "every priority case needs at least one bounded real reference",
        )

    def test_committed_reference_manifest_matches_specs(self) -> None:
        rows = build_references.read_jsonl(REFERENCE_MANIFEST)
        self.assertEqual(rows, build_references.build_reference_records())
        self.assertGreaterEqual(len(rows), 12)

    def test_storyboards_exist_for_all_fifty_priority_cases(self) -> None:
        rows = build_references.read_jsonl(STORYBOARD_MANIFEST)
        self.assertEqual(len(rows), 50)
        self.assertEqual(rows[0]["priority_id"], "PRIORITY-REALTIME-LIGHT-TRAIL")
        self.assertEqual(rows[1]["priority_id"], "PRIORITY-GAZE-EYE-CONTACT")

        for row in rows:
            with self.subTest(priority_id=row["priority_id"]):
                image_path = ROOT / row["image_path"]
                self.assertTrue(image_path.exists(), image_path)
                self.assertEqual(row["visual_status"], "本项目概念分镜")
                with Image.open(image_path) as image:
                    self.assertGreaterEqual(image.width, 1500)
                    self.assertGreaterEqual(image.height, 600)
                    self.assertEqual(image.mode, "RGB")

    def test_evidence_cards_are_explicit_about_scope(self) -> None:
        records = build_references.build_reference_records()
        self.assertTrue(all(record["does_not_prove"] for record in records))
        self.assertTrue(all(record["demonstrates"] for record in records))
        forbidden = ("证明手机实时量产", "proves mobile realtime production")
        joined = "\n".join(
            str(value)
            for record in records
            for value in record.values()
            if isinstance(value, str)
        ).casefold()
        self.assertFalse(any(value.casefold() in joined for value in forbidden))


if __name__ == "__main__":
    unittest.main()
