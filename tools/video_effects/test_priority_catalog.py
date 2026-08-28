"""Contract tests for the priority video-effect deep-dive catalog."""

from __future__ import annotations

import json
import hashlib
import re
import tempfile
import unittest
from pathlib import Path

from tools.video_effects import priority_catalog, schema


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "daily" / "20260827_录像特效调研" / "metadata" / "priority_effects.jsonl"


class PriorityCatalogTests(unittest.TestCase):
    def test_priority_delivery_has_fifty_deep_dive_records(self) -> None:
        self.assertTrue(OUTPUT.exists())
        rows = [json.loads(line) for line in OUTPUT.read_text(encoding="utf-8").splitlines() if line.strip()]
        self.assertEqual(len(rows), 50)
        self.assertEqual(rows[0]["priority_id"], "PRIORITY-REALTIME-LIGHT-TRAIL")
        self.assertEqual(rows[1]["priority_id"], "PRIORITY-GAZE-EYE-CONTACT")

        for row in rows:
            with self.subTest(priority_id=row.get("priority_id")):
                self.assertGreaterEqual(len(row["interaction_timeline"]), 5)
                self.assertGreaterEqual(len(row["module_pipeline"]), 5)
                self.assertGreaterEqual(len(row["adjustable_parameters"]), 6)
                self.assertGreaterEqual(len(row["failure_and_fallback"]), 4)

    def test_priorities_pass_schema_and_reference_known_effects(self) -> None:
        priorities = priority_catalog.build_priorities()
        idea_ids = priority_catalog._source_effect_ids()
        report = priority_catalog.validate_priorities(priorities, idea_ids)
        self.assertEqual(report["count"], 50)
        self.assertEqual(len(report["effect_family_counts"]), 12)
        self.assertEqual(report["timeline_items"], 250)
        self.assertEqual(report["pipeline_items"], 250)
        for priority in priorities:
            with self.subTest(priority_id=priority["priority_id"]):
                self.assertEqual(set(priority), set(priority_catalog.PRIORITY_FIELDS))
                schema.validate_priority(priority, idea_ids)

    def test_priority_cases_are_semantically_distinct(self) -> None:
        priorities = priority_catalog.build_priorities()
        for field in (
            "priority_id",
            "effect_id",
            "problem",
            "experience_story",
            "tensor_or_signal_flow",
            "preview_budget",
            "post_refinement",
            "mobile_product_form",
        ):
            values = [priority[field] for priority in priorities]
            self.assertEqual(len(values), len(set(values)), field)

    def test_preview_budgets_do_not_claim_unmeasured_performance(self) -> None:
        forbidden_measurements = re.compile(
            r"\b\d+(?:\s*[-~]\s*\d+)?\s*(?:ms|fps|mb|gb|w)\b|"
            r"\d+(?:\s*[-~]\s*\d+)?\s*(?:毫秒|帧每秒|帧/秒|兆字节|瓦)|"
            r"(?:延迟|时延)[^；。]*?\d+(?:\s*[-~]\s*\d+)?\s*帧",
            flags=re.IGNORECASE,
        )
        for priority in priority_catalog.build_priorities():
            with self.subTest(priority_id=priority["priority_id"]):
                self.assertIsNone(
                    forbidden_measurements.search(priority["preview_budget"]),
                    priority["preview_budget"],
                )

    def test_committed_output_matches_explicit_specs(self) -> None:
        rows = [json.loads(line) for line in OUTPUT.read_text(encoding="utf-8").splitlines() if line.strip()]
        self.assertEqual(rows, priority_catalog.build_priorities())

    def test_priority_jsonl_is_byte_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            first = Path(temporary_directory) / "first.jsonl"
            second = Path(temporary_directory) / "second.jsonl"
            priority_catalog.write_jsonl(priority_catalog.build_priorities(), first)
            priority_catalog.write_jsonl(priority_catalog.build_priorities(), second)
            first_bytes = first.read_bytes()
            second_bytes = second.read_bytes()
            self.assertEqual(first_bytes, second_bytes)
            self.assertEqual(len(first_bytes.splitlines()), 50)
            self.assertTrue(first_bytes.endswith(b"\n"))
            self.assertEqual(
                hashlib.sha256(first_bytes).hexdigest(),
                hashlib.sha256(second_bytes).hexdigest(),
            )


if __name__ == "__main__":
    unittest.main()
