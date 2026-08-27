"""Tests for the mobile video-effects research schemas."""

from __future__ import annotations

import unittest

from tools.video_effects import schema


ATOM_FIELDS = (
    "atom_id",
    "name_zh",
    "name_en",
    "family",
    "primitive_type",
    "visible_primitive",
    "required_signals",
    "temporal_state",
    "parameters",
    "failure_modes",
    "mobile_notes",
)

IDEA_FIELDS = (
    "effect_id",
    "name_zh",
    "name_en",
    "family",
    "visible_effect",
    "scenarios",
    "target_objects",
    "spatial_scope",
    "trigger_signals",
    "interaction",
    "user_controls",
    "preview_pipeline",
    "post_pipeline",
    "required_signals",
    "atom_ids",
    "temporal_window",
    "continuity_challenges",
    "edge_difficulty",
    "execution_targets",
    "generation_level",
    "risks",
    "novelty",
    "shareability",
    "product_value",
    "reference_ids",
    "combinable_effect_ids",
    "status",
)

RECIPE_FIELDS = (
    "recipe_id",
    "name_zh",
    "component_atom_ids",
    "component_effect_ids",
    "trigger_logic",
    "combined_effect",
    "why_new",
    "preview_behavior",
    "post_behavior",
    "risks",
    "target_scenarios",
)

PRIORITY_FIELDS = (
    "priority_id",
    "effect_id",
    "problem",
    "experience_story",
    "interaction_timeline",
    "module_pipeline",
    "tensor_or_signal_flow",
    "preview_budget",
    "recorded_metadata",
    "post_refinement",
    "adjustable_parameters",
    "failure_and_fallback",
    "mobile_product_form",
    "references",
)

REFERENCE_FIELDS = (
    "reference_id",
    "title",
    "source_type",
    "product_work_paper",
    "publisher",
    "year",
    "original_source",
    "access_status",
    "local_files",
    "effect_ids",
    "demonstrates",
    "does_not_prove",
    "implementation_boundary",
    "sha256",
)

VALID_ATOM_IDS = {"ATOM-LIGHT-TRAIL", "ATOM-DEPTH-ECHO"}
VALID_IDEA_IDS = {"FX-LIGHT-TRAIL"}


def valid_atom() -> dict[str, object]:
    return {
        "atom_id": "ATOM-LIGHT-TRAIL",
        "name_zh": "光轨时间累积",
        "name_en": "Light Trail Accumulation",
        "family": "temporal_light",
        "primitive_type": "temporal_accumulation",
        "visible_primitive": "移动亮点在画面中形成可见的连续光轨",
        "required_signals": ["rgb_video", "gyroscope"],
        "temporal_state": ["previous_frame", "trail_buffer"],
        "parameters": ["trail_length", "decay_rate"],
        "failure_modes": ["高光过曝时光轨粘连"],
        "mobile_notes": ["预览使用半分辨率历史缓冲"],
    }


def valid_idea() -> dict[str, object]:
    return {
        "effect_id": "FX-LIGHT-TRAIL",
        "name_zh": "光轨抖动稳定",
        "name_en": "Light Trail Motion Lock",
        "family": "temporal_light",
        "visible_effect": "手持移动时光轨被锁定成清晰可见的发光路径",
        "scenarios": ["夜景街拍"],
        "target_objects": ["点光源"],
        "spatial_scope": ["tracked_object", "background"],
        "trigger_signals": ["按住快门并平移手机"],
        "interaction": "用户拖动取景器中的光源以锁定光轨起点",
        "user_controls": ["光轨长度", "衰减速度"],
        "preview_pipeline": "低分辨率检测、跟踪并累积光轨预览",
        "post_pipeline": "原分辨率重跟踪并细化遮挡边界",
        "required_signals": ["rgb_video", "gyroscope"],
        "atom_ids": ["ATOM-LIGHT-TRAIL"],
        "temporal_window": "最近 24 帧滚动窗口",
        "continuity_challenges": ["遮挡后光轨身份恢复"],
        "edge_difficulty": "high",
        "execution_targets": ["mobile_preview", "mobile_post"],
        "generation_level": "perceptual_effect",
        "risks": ["快速摇摄时轨迹断裂"],
        "novelty": "将轨迹稳定作为可见光绘交互的一部分",
        "shareability": "可生成一眼可辨识的动态光绘短片",
        "product_value": "适合作为夜景录像模式中的独立创作玩法",
        "reference_ids": [],
        "combinable_effect_ids": [],
        "status": "idea_only",
    }


def valid_recipe() -> dict[str, object]:
    return {
        "recipe_id": "RECIPE-LIGHT-ECHO",
        "name_zh": "光轨空间回声",
        "component_atom_ids": ["ATOM-LIGHT-TRAIL"],
        "component_effect_ids": ["FX-LIGHT-TRAIL"],
        "trigger_logic": "检测到用户环绕主体移动并按住录制键时启动",
        "combined_effect": "主体边缘保持清晰，同时移动光源在不同深度留下分层空间回声",
        "why_new": "它把时间光轨与深度分层绑定，使轨迹能够绕过主体而不是简单覆盖画面",
        "preview_behavior": "预览展示短历史光轨和粗粒度前后景遮挡",
        "post_behavior": "录制后使用完整历史窗口细化深度边缘和轨迹连续性",
        "risks": ["单目深度错误导致光轨穿透主体"],
        "target_scenarios": ["夜间人像环绕拍摄"],
    }


def valid_priority() -> dict[str, object]:
    return {
        "priority_id": "PRIORITY-LIGHT-TRAIL",
        "effect_id": "FX-LIGHT-TRAIL",
        "problem": "普通手机录像难以在手持运动中获得可控且连续的光绘轨迹",
        "experience_story": "用户锁定光源后绕场景移动，实时看到光轨被固定在空间中",
        "interaction_timeline": ["0 秒点选光源", "1-4 秒按住录制并移动", "结束后调整轨迹长度"],
        "module_pipeline": ["光源检测", "运动补偿", "时域累积", "遮挡合成"],
        "tensor_or_signal_flow": "RGB 帧与陀螺仪姿态进入跟踪器，轨迹掩码流入时域合成器",
        "preview_budget": "720p 预览保持 30 fps，历史缓冲限制为 24 帧",
        "recorded_metadata": ["相机姿态", "光源轨迹", "轨迹置信度"],
        "post_refinement": "在原分辨率重建轨迹并修复短时遮挡",
        "adjustable_parameters": ["轨迹长度", "亮度", "衰减曲线"],
        "failure_and_fallback": ["跟踪丢失时冻结最后可信轨迹并提示重新锁定"],
        "mobile_product_form": "相机录像模式中的光绘工具，支持录后无损调参",
        "references": [],
    }


def valid_reference() -> dict[str, object]:
    return {
        "reference_id": "REF-LIGHT-TRAIL-PAPER",
        "title": "Interactive Long Exposure Video",
        "source_type": "paper_project",
        "product_work_paper": "research paper",
        "publisher": "Example Conference",
        "year": 2025,
        "original_source": "https://example.org/light-trail",
        "access_status": "public abstract verified",
        "local_files": [],
        "effect_ids": ["FX-LIGHT-TRAIL"],
        "demonstrates": "时域轨迹累积可以产生连续可见的光绘效果",
        "does_not_prove": "未证明消费级手机上的实时性能或量产可行性",
        "implementation_boundary": "research_prototype",
        "sha256": "",
    }


class SchemaTests(unittest.TestCase):
    def assert_field_error(self, field: str, callable_, *args) -> None:
        with self.assertRaisesRegex(ValueError, field):
            callable_(*args)

    def test_effect_atom_requires_visible_primitive(self) -> None:
        record = valid_atom()
        record["visible_primitive"] = ""
        self.assert_field_error("visible_primitive", schema.validate_atom, record)

    def test_effect_idea_requires_trigger_or_control(self) -> None:
        record = valid_idea()
        record["trigger_signals"] = []
        record["user_controls"] = []
        with self.assertRaisesRegex(ValueError, "trigger"):
            schema.validate_idea(record, {"ATOM-LIGHT-TRAIL"})

        for field in ("trigger_signals", "user_controls"):
            with self.subTest(nonempty_field=field):
                one_input = valid_idea()
                other = "user_controls" if field == "trigger_signals" else "trigger_signals"
                one_input[other] = []
                schema.validate_idea(one_input, {"ATOM-LIGHT-TRAIL"})

    def test_effect_idea_rejects_engineering_only_feature(self) -> None:
        rejected_phrases = (
            "普通视频防抖",
            "普通防抖",
            "ordinary stabilization",
            "普通视频去噪",
            "普通去噪",
            "ordinary denoising",
            "普通 HDR",
            "ordinary HDR",
            "普通超分",
            "ordinary super-resolution",
            "普通自动构图",
            "ordinary auto framing",
            "常规多摄切换",
            "conventional camera switching",
        )
        for field in ("name_zh", "name_en", "visible_effect"):
            for phrase in rejected_phrases:
                with self.subTest(field=field, phrase=phrase):
                    record = valid_idea()
                    record[field] = f"  {phrase.upper()}  " if phrase.isascii() else phrase
                    with self.assertRaisesRegex(ValueError, "engineering|主玩法"):
                        schema.validate_idea(record, {"ATOM-LIGHT-TRAIL"})

        spaced = valid_idea()
        spaced["name_en"] = "  ordinary\t   stabilization  "
        with self.assertRaisesRegex(ValueError, "engineering|主玩法"):
            schema.validate_idea(spaced, {"ATOM-LIGHT-TRAIL"})

        multiline = valid_idea()
        multiline["visible_effect"] = "创意光轨\n普通防抖"
        with self.assertRaisesRegex(ValueError, "engineering|主玩法"):
            schema.validate_idea(multiline, {"ATOM-LIGHT-TRAIL"})

        wrapped_values = (
            "普通防抖。",
            "主玩法是普通防抖",
            "功能是普通视频去噪",
            "效果是普通 HDR",
            "This is ordinary stabilization",
            "The main effect is ordinary denoising",
            "Main effect is ordinary HDR",
        )
        for field in ("name_zh", "name_en", "visible_effect"):
            for value in wrapped_values:
                with self.subTest(field=field, wrapped=value):
                    record = valid_idea()
                    record[field] = value
                    with self.assertRaisesRegex(ValueError, "engineering|主玩法"):
                        schema.validate_idea(record, {"ATOM-LIGHT-TRAIL"})

        allowed_values = (
            "Extraordinary Stabilization Light Trails",
            "Not ordinary stabilization: creates light trails",
            "普通防抖基础上的光轨特效",
            "Not ordinary stabilization",
            "Not an ordinary stabilization",
            "不是普通防抖",
            "并非普通防抖",
            "不属于普通防抖",
        )
        for field in ("name_zh", "name_en", "visible_effect"):
            for value in allowed_values:
                with self.subTest(field=field, value=value):
                    record = valid_idea()
                    record[field] = value
                    schema.validate_idea(record, {"ATOM-LIGHT-TRAIL"})

    def test_recipe_requires_novel_combined_effect(self) -> None:
        for field, value in (("combined_effect", "简单拼接"), ("why_new", "两个效果放一起")):
            with self.subTest(field=field):
                record = valid_recipe()
                record[field] = value
                self.assert_field_error(
                    field,
                    schema.validate_recipe,
                    record,
                    VALID_ATOM_IDS,
                    VALID_IDEA_IDS,
                )

    def test_recipe_novelty_lengths_ignore_whitespace_at_exact_boundaries(self) -> None:
        cases = (
            ("combined_effect", "12345 67890 abcde", False),
            ("combined_effect", "12345 67890 abcdef", True),
            ("why_new", "12345 67890 abcde fghi", False),
            ("why_new", "12345 67890 abcde fghij", True),
        )
        for field, value, accepted in cases:
            with self.subTest(field=field, value=value, accepted=accepted):
                record = valid_recipe()
                record[field] = value
                if accepted:
                    schema.validate_recipe(record, VALID_ATOM_IDS, VALID_IDEA_IDS)
                else:
                    self.assert_field_error(
                        field,
                        schema.validate_recipe,
                        record,
                        VALID_ATOM_IDS,
                        VALID_IDEA_IDS,
                    )

    def test_all_five_valid_records_pass(self) -> None:
        schema.validate_atom(valid_atom())
        schema.validate_idea(valid_idea(), {"ATOM-LIGHT-TRAIL"})
        schema.validate_recipe(
            valid_recipe(),
            VALID_ATOM_IDS,
            VALID_IDEA_IDS,
        )
        schema.validate_priority(valid_priority(), {"FX-LIGHT-TRAIL"})
        schema.validate_reference(valid_reference())

        reference = valid_reference()
        reference["year"] = "2025"
        reference["sha256"] = "a" * 64
        schema.validate_reference(reference)

    def test_missing_required_fields_are_rejected_individually(self) -> None:
        cases = (
            (valid_atom, ATOM_FIELDS, schema.validate_atom, ()),
            (valid_idea, IDEA_FIELDS, schema.validate_idea, ({"ATOM-LIGHT-TRAIL"},)),
            (
                valid_recipe,
                RECIPE_FIELDS,
                schema.validate_recipe,
                (VALID_ATOM_IDS, VALID_IDEA_IDS),
            ),
            (valid_priority, PRIORITY_FIELDS, schema.validate_priority, ({"FX-LIGHT-TRAIL"},)),
            (valid_reference, REFERENCE_FIELDS, schema.validate_reference, ()),
        )
        for factory, fields, validator, args in cases:
            for field in fields:
                with self.subTest(validator=validator.__name__, field=field):
                    record = factory()
                    del record[field]
                    self.assert_field_error(field, validator, record, *args)

    def test_non_mapping_inputs_raise_contextual_value_error(self) -> None:
        cases = (
            (schema.validate_atom, ()),
            (schema.validate_idea, (None,)),
            (schema.validate_recipe, (set(), set())),
            (schema.validate_priority, (set(),)),
            (schema.validate_reference, ()),
        )
        for validator, args in cases:
            for value in ([], "record", True, None):
                with self.subTest(validator=validator.__name__, value=value):
                    with self.assertRaisesRegex(ValueError, "record|Mapping"):
                        validator(value, *args)

    def test_scalar_and_list_type_boundaries(self) -> None:
        cases = (
            (
                valid_atom,
                schema.validate_atom,
                (),
                ("atom_id", "name_zh", "name_en", "family", "primitive_type", "visible_primitive"),
                ("required_signals", "temporal_state", "parameters", "failure_modes", "mobile_notes"),
            ),
            (
                valid_idea,
                schema.validate_idea,
                ({"ATOM-LIGHT-TRAIL"},),
                (
                    "effect_id", "name_zh", "name_en", "family", "visible_effect", "interaction",
                    "preview_pipeline", "post_pipeline", "temporal_window", "edge_difficulty",
                    "generation_level", "novelty", "shareability", "product_value", "status",
                ),
                (
                    "scenarios", "target_objects", "spatial_scope", "trigger_signals", "user_controls",
                    "required_signals", "atom_ids", "continuity_challenges", "execution_targets", "risks",
                    "reference_ids", "combinable_effect_ids",
                ),
            ),
            (
                valid_recipe,
                schema.validate_recipe,
                (VALID_ATOM_IDS, VALID_IDEA_IDS),
                (
                    "recipe_id", "name_zh", "trigger_logic", "combined_effect", "why_new",
                    "preview_behavior", "post_behavior",
                ),
                ("component_atom_ids", "component_effect_ids", "risks", "target_scenarios"),
            ),
            (
                valid_priority,
                schema.validate_priority,
                ({"FX-LIGHT-TRAIL"},),
                (
                    "priority_id", "effect_id", "problem", "experience_story", "tensor_or_signal_flow",
                    "preview_budget", "post_refinement", "mobile_product_form",
                ),
                (
                    "interaction_timeline", "module_pipeline", "recorded_metadata", "adjustable_parameters",
                    "failure_and_fallback", "references",
                ),
            ),
            (
                valid_reference,
                schema.validate_reference,
                (),
                (
                    "reference_id", "title", "source_type", "product_work_paper", "publisher",
                    "original_source", "access_status", "demonstrates", "does_not_prove",
                    "implementation_boundary", "sha256",
                ),
                ("local_files", "effect_ids"),
            ),
        )
        for factory, validator, args, scalar_fields, list_fields in cases:
            for field in scalar_fields:
                for bad_value in ([], True, None, "   "):
                    with self.subTest(validator=validator.__name__, field=field, value=bad_value):
                        record = factory()
                        record[field] = bad_value
                        self.assert_field_error(field, validator, record, *args)
            for field in list_fields:
                for bad_value in ("not-a-list", True, None):
                    with self.subTest(validator=validator.__name__, field=field, value=bad_value):
                        record = factory()
                        record[field] = bad_value
                        self.assert_field_error(field, validator, record, *args)

        for bad_year in ([], True, None, "   "):
            with self.subTest(field="year", value=bad_year):
                record = valid_reference()
                record["year"] = bad_year
                self.assert_field_error("year", schema.validate_reference, record)

    def test_list_elements_must_be_nonempty_strings(self) -> None:
        cases = (
            (valid_atom, schema.validate_atom, (), ("required_signals", "temporal_state", "parameters", "failure_modes", "mobile_notes")),
            (
                valid_idea,
                schema.validate_idea,
                ({"ATOM-LIGHT-TRAIL"},),
                (
                    "scenarios", "target_objects", "spatial_scope", "trigger_signals", "user_controls",
                    "required_signals", "atom_ids", "continuity_challenges", "execution_targets", "risks",
                    "reference_ids", "combinable_effect_ids",
                ),
            ),
            (
                valid_recipe,
                schema.validate_recipe,
                (VALID_ATOM_IDS, VALID_IDEA_IDS),
                ("component_atom_ids", "component_effect_ids", "risks", "target_scenarios"),
            ),
            (
                valid_priority,
                schema.validate_priority,
                ({"FX-LIGHT-TRAIL"},),
                ("interaction_timeline", "module_pipeline", "recorded_metadata", "adjustable_parameters", "failure_and_fallback", "references"),
            ),
            (valid_reference, schema.validate_reference, (), ("local_files", "effect_ids")),
        )
        for factory, validator, args, fields in cases:
            for field in fields:
                for bad_item in ("", "   ", 7, None, True):
                    with self.subTest(validator=validator.__name__, field=field, item=bad_item):
                        record = factory()
                        record[field] = [bad_item]
                        self.assert_field_error(field, validator, record, *args)

    def test_id_prefixes_are_enforced(self) -> None:
        cases = (
            (valid_atom, schema.validate_atom, (), "atom_id"),
            (valid_idea, schema.validate_idea, ({"ATOM-LIGHT-TRAIL"},), "effect_id"),
            (
                valid_recipe,
                schema.validate_recipe,
                (VALID_ATOM_IDS, VALID_IDEA_IDS),
                "recipe_id",
            ),
            (valid_priority, schema.validate_priority, ({"FX-LIGHT-TRAIL"},), "priority_id"),
            (valid_reference, schema.validate_reference, (), "reference_id"),
        )
        for factory, validator, args, field in cases:
            with self.subTest(field=field):
                record = factory()
                record[field] = "WRONG-001"
                self.assert_field_error(field, validator, record, *args)

    def test_ids_require_complete_uppercase_format_without_surrounding_space(self) -> None:
        scalar_cases = (
            (valid_atom, schema.validate_atom, (), "atom_id", "ATOM-"),
            (valid_idea, schema.validate_idea, (VALID_ATOM_IDS,), "effect_id", "FX-"),
            (valid_recipe, schema.validate_recipe, (VALID_ATOM_IDS, VALID_IDEA_IDS), "recipe_id", "RECIPE-"),
            (valid_priority, schema.validate_priority, (VALID_IDEA_IDS,), "priority_id", "PRIORITY-"),
            (valid_priority, schema.validate_priority, (VALID_IDEA_IDS,), "effect_id", "FX-"),
            (valid_reference, schema.validate_reference, (), "reference_id", "REF-"),
        )
        for factory, validator, args, field, bare_prefix in scalar_cases:
            for bad_value in (
                bare_prefix,
                f"{bare_prefix} ",
                f"{bare_prefix}BAD ",
                f" {bare_prefix}BAD",
                f"{bare_prefix.lower()}bad",
            ):
                with self.subTest(field=field, value=bad_value):
                    record = factory()
                    record[field] = bad_value
                    self.assert_field_error(field, validator, record, *args)

        list_cases = (
            (valid_idea, schema.validate_idea, (VALID_ATOM_IDS,), "atom_ids", "ATOM-"),
            (valid_idea, schema.validate_idea, (VALID_ATOM_IDS,), "reference_ids", "REF-"),
            (valid_idea, schema.validate_idea, (VALID_ATOM_IDS,), "combinable_effect_ids", "FX-"),
            (valid_recipe, schema.validate_recipe, (VALID_ATOM_IDS, VALID_IDEA_IDS), "component_atom_ids", "ATOM-"),
            (valid_recipe, schema.validate_recipe, (VALID_ATOM_IDS, VALID_IDEA_IDS), "component_effect_ids", "FX-"),
            (valid_priority, schema.validate_priority, (VALID_IDEA_IDS,), "references", "REF-"),
            (valid_reference, schema.validate_reference, (), "effect_ids", "FX-"),
        )
        for factory, validator, args, field, bare_prefix in list_cases:
            for bad_value in (bare_prefix, f"{bare_prefix} ", f"{bare_prefix}BAD "):
                with self.subTest(field=field, value=bad_value):
                    record = factory()
                    record[field] = [bad_value]
                    self.assert_field_error(field, validator, record, *args)

        schema.validate_atom(valid_atom())
        schema.validate_idea(valid_idea(), VALID_ATOM_IDS)
        schema.validate_recipe(valid_recipe(), VALID_ATOM_IDS, VALID_IDEA_IDS)
        schema.validate_priority(valid_priority(), VALID_IDEA_IDS)
        schema.validate_reference(valid_reference())

    def test_enums_are_enforced(self) -> None:
        for field in ("generation_level", "edge_difficulty", "status"):
            with self.subTest(field=field):
                record = valid_idea()
                record[field] = "unsupported"
                self.assert_field_error(field, schema.validate_idea, record, {"ATOM-LIGHT-TRAIL"})

        for field in ("source_type", "implementation_boundary"):
            with self.subTest(field=field):
                record = valid_reference()
                record[field] = "unsupported"
                self.assert_field_error(field, schema.validate_reference, record)

    def test_references_must_exist(self) -> None:
        idea = valid_idea()
        idea["atom_ids"] = ["ATOM-MISSING"]
        self.assert_field_error("atom_ids", schema.validate_idea, idea, {"ATOM-LIGHT-TRAIL"})

        recipe = valid_recipe()
        recipe["component_atom_ids"] = ["ATOM-MISSING"]
        self.assert_field_error(
            "component_atom_ids",
            schema.validate_recipe,
            recipe,
            VALID_ATOM_IDS,
            VALID_IDEA_IDS,
        )

        recipe = valid_recipe()
        recipe["component_effect_ids"] = ["FX-MISSING"]
        self.assert_field_error(
            "component_effect_ids",
            schema.validate_recipe,
            recipe,
            {"ATOM-LIGHT-TRAIL"},
            {"FX-LIGHT-TRAIL"},
        )

        priority = valid_priority()
        priority["effect_id"] = "FX-MISSING"
        self.assert_field_error("effect_id", schema.validate_priority, priority, {"FX-LIGHT-TRAIL"})

    def test_reference_collections_reject_wrong_types_with_context(self) -> None:
        cases = (
            (schema.validate_idea, valid_idea(), ([],), "atom_ids"),
            (schema.validate_recipe, valid_recipe(), (None, VALID_IDEA_IDS), "component_atom_ids"),
            (schema.validate_recipe, valid_recipe(), (VALID_ATOM_IDS, True), "component_effect_ids"),
            (schema.validate_priority, valid_priority(), ("FX-LIGHT-TRAIL",), "effect_id"),
        )
        for validator, record, args, field in cases:
            with self.subTest(validator=validator.__name__, field=field):
                self.assert_field_error(field, validator, record, *args)

    def test_recipe_requires_two_distinct_components(self) -> None:
        valid_cases = (
            (["ATOM-LIGHT-TRAIL", "ATOM-DEPTH-ECHO"], []),
            ([], ["FX-LIGHT-TRAIL", "FX-DEPTH-ECHO"]),
            (["ATOM-LIGHT-TRAIL"], ["FX-LIGHT-TRAIL"]),
        )
        for atom_ids, effect_ids in valid_cases:
            with self.subTest(atom_ids=atom_ids, effect_ids=effect_ids):
                record = valid_recipe()
                record["component_atom_ids"] = atom_ids
                record["component_effect_ids"] = effect_ids
                schema.validate_recipe(
                    record,
                    VALID_ATOM_IDS,
                    {"FX-LIGHT-TRAIL", "FX-DEPTH-ECHO"},
                )

        invalid_cases = (
            (["ATOM-LIGHT-TRAIL"], []),
            ([], ["FX-LIGHT-TRAIL"]),
            ([], []),
        )
        for atom_ids, effect_ids in invalid_cases:
            with self.subTest(atom_ids=atom_ids, effect_ids=effect_ids):
                record = valid_recipe()
                record["component_atom_ids"] = atom_ids
                record["component_effect_ids"] = effect_ids
                with self.assertRaisesRegex(ValueError, "component"):
                    schema.validate_recipe(record, VALID_ATOM_IDS, VALID_IDEA_IDS)

    def test_recipe_rejects_duplicate_ids_within_each_component_list(self) -> None:
        cases = (
            (
                "component_atom_ids",
                ["ATOM-LIGHT-TRAIL", "ATOM-LIGHT-TRAIL"],
                ["FX-LIGHT-TRAIL"],
            ),
            (
                "component_effect_ids",
                ["ATOM-LIGHT-TRAIL"],
                ["FX-LIGHT-TRAIL", "FX-LIGHT-TRAIL"],
            ),
        )
        for field, atom_ids, effect_ids in cases:
            with self.subTest(field=field):
                record = valid_recipe()
                record["component_atom_ids"] = atom_ids
                record["component_effect_ids"] = effect_ids
                self.assert_field_error(
                    field,
                    schema.validate_recipe,
                    record,
                    VALID_ATOM_IDS,
                    VALID_IDEA_IDS,
                )

    def test_only_documented_list_fields_may_be_empty(self) -> None:
        allowed_empty = (
            (valid_idea, schema.validate_idea, ({"ATOM-LIGHT-TRAIL"},), "reference_ids"),
            (valid_idea, schema.validate_idea, ({"ATOM-LIGHT-TRAIL"},), "combinable_effect_ids"),
            (valid_priority, schema.validate_priority, ({"FX-LIGHT-TRAIL"},), "references"),
            (valid_reference, schema.validate_reference, (), "local_files"),
        )
        for factory, validator, args, field in allowed_empty:
            with self.subTest(allowed=field):
                record = factory()
                record[field] = []
                validator(record, *args)

        rejected_empty = (
            (valid_atom, schema.validate_atom, (), "required_signals"),
            (valid_idea, schema.validate_idea, ({"ATOM-LIGHT-TRAIL"},), "scenarios"),
            (valid_priority, schema.validate_priority, ({"FX-LIGHT-TRAIL"},), "module_pipeline"),
            (valid_reference, schema.validate_reference, (), "effect_ids"),
        )
        for factory, validator, args, field in rejected_empty:
            with self.subTest(rejected=field):
                record = factory()
                record[field] = []
                self.assert_field_error(field, validator, record, *args)

    def test_priority_key_lists_cannot_be_empty(self) -> None:
        for field in (
            "interaction_timeline",
            "module_pipeline",
            "recorded_metadata",
            "adjustable_parameters",
            "failure_and_fallback",
        ):
            with self.subTest(field=field):
                record = valid_priority()
                record[field] = []
                self.assert_field_error(field, schema.validate_priority, record, {"FX-LIGHT-TRAIL"})

    def test_priority_references_require_ref_prefix_when_present(self) -> None:
        record = valid_priority()
        record["references"] = ["REF-LIGHT-TRAIL-PAPER"]
        schema.validate_priority(record, {"FX-LIGHT-TRAIL"})

        record["references"] = ["SOURCE-LIGHT-TRAIL"]
        self.assert_field_error(
            "references",
            schema.validate_priority,
            record,
            {"FX-LIGHT-TRAIL"},
        )

    def test_sha256_must_be_empty_or_64_hex_characters(self) -> None:
        for bad_value in ("abc", "g" * 64, "a" * 63, "a" * 65):
            with self.subTest(value=bad_value):
                record = valid_reference()
                record["sha256"] = bad_value
                self.assert_field_error("sha256", schema.validate_reference, record)

    def test_film_inspiration_cannot_claim_mobile_realtime_implementation(self) -> None:
        claims = (
            "implemented realtime on mobile",
            "works in real time on smartphones",
            "runs in real time on a smartphone",
            "已在手机实时实现",
            "已在手机实时量产",
            "not available on desktop, implemented realtime on mobile",
            "cannot run on desktop, works in real time on smartphones",
            "没有桌面版本，已在手机实时实现",
            "并非桌面实时实现，而是在手机实时运行",
            "implemented realtime on desktop and mobile",
            "works in real time on desktop and smartphones",
            "runs in real time on desktop and mobile",
            "not available on desktop and implemented realtime on mobile",
        )
        for boundary in ("film_postproduction", "visual_inspiration"):
            for claim in claims:
                with self.subTest(boundary=boundary, claim=claim):
                    record = valid_reference()
                    record["implementation_boundary"] = boundary
                    record["demonstrates"] = claim
                    with self.assertRaisesRegex(ValueError, "implementation_boundary"):
                        schema.validate_reference(record)

        list_field_claim = valid_reference()
        list_field_claim["implementation_boundary"] = "film_postproduction"
        list_field_claim["local_files"] = ["this runs in real time on a smartphone"]
        with self.assertRaisesRegex(ValueError, "implementation_boundary"):
            schema.validate_reference(list_field_claim)

        mixed_claim = valid_reference()
        mixed_claim["implementation_boundary"] = "visual_inspiration"
        mixed_claim["publisher"] = "not available on desktop, but implemented realtime on mobile"
        with self.assertRaisesRegex(ValueError, "implementation_boundary"):
            schema.validate_reference(mixed_claim)

        negative_claims = (
            "This was not implemented in real time on mobile",
            "cannot be deployed in real time on mobile",
            "没有在手机实时实现",
            "未证明手机实时实现",
            "runs in real time on desktop, not mobile",
            "automobile real-time rendering",
        )
        for claim in negative_claims:
            with self.subTest(claim=claim):
                disclaimer = valid_reference()
                disclaimer["implementation_boundary"] = "film_postproduction"
                disclaimer["demonstrates"] = claim
                schema.validate_reference(disclaimer)

        excluded_disclaimer = valid_reference()
        excluded_disclaimer["implementation_boundary"] = "film_postproduction"
        excluded_disclaimer["does_not_prove"] = "手机实时实现并已经量产部署"
        schema.validate_reference(excluded_disclaimer)


if __name__ == "__main__":
    unittest.main()
