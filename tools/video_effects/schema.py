"""Validation schemas for mobile video-effect research records."""

from __future__ import annotations

import re
from collections.abc import Mapping


GENERATION_LEVELS = frozenset({
    "faithful_edit",
    "perceptual_effect",
    "generative_rewrite",
})

EDGE_DIFFICULTIES = frozenset({"low", "medium", "high", "research"})

IDEA_STATUSES = frozenset({"idea_only", "reference_backed", "priority"})

IMPLEMENTATION_BOUNDARIES = frozenset({
    "mobile_realtime",
    "mobile_offline",
    "desktop_realtime",
    "desktop_offline",
    "film_postproduction",
    "research_prototype",
    "visual_inspiration",
})

SOURCE_TYPES = frozenset({
    "official_product",
    "official_software",
    "film_mv_ad",
    "paper_project",
    "game_engine",
    "third_party_analysis",
})

_ATOM_SCALARS = (
    "atom_id",
    "name_zh",
    "name_en",
    "family",
    "primitive_type",
    "visible_primitive",
)
_ATOM_LISTS = (
    "required_signals",
    "temporal_state",
    "parameters",
    "failure_modes",
    "mobile_notes",
)

_IDEA_SCALARS = (
    "effect_id",
    "name_zh",
    "name_en",
    "family",
    "visible_effect",
    "interaction",
    "preview_pipeline",
    "post_pipeline",
    "temporal_window",
    "edge_difficulty",
    "generation_level",
    "novelty",
    "shareability",
    "product_value",
    "status",
)
_IDEA_LISTS = (
    "scenarios",
    "target_objects",
    "spatial_scope",
    "trigger_signals",
    "user_controls",
    "required_signals",
    "atom_ids",
    "continuity_challenges",
    "execution_targets",
    "risks",
    "reference_ids",
    "combinable_effect_ids",
)
_IDEA_EMPTY_LISTS = frozenset({
    "trigger_signals",
    "user_controls",
    "reference_ids",
    "combinable_effect_ids",
})

_RECIPE_SCALARS = (
    "recipe_id",
    "name_zh",
    "trigger_logic",
    "combined_effect",
    "why_new",
    "preview_behavior",
    "post_behavior",
)
_RECIPE_LISTS = (
    "component_atom_ids",
    "component_effect_ids",
    "risks",
    "target_scenarios",
)

_PRIORITY_SCALARS = (
    "priority_id",
    "effect_id",
    "problem",
    "experience_story",
    "tensor_or_signal_flow",
    "preview_budget",
    "post_refinement",
    "mobile_product_form",
)
_PRIORITY_LISTS = (
    "interaction_timeline",
    "module_pipeline",
    "recorded_metadata",
    "adjustable_parameters",
    "failure_and_fallback",
    "references",
)

_REFERENCE_SCALARS = (
    "reference_id",
    "title",
    "source_type",
    "product_work_paper",
    "publisher",
    "original_source",
    "access_status",
    "demonstrates",
    "does_not_prove",
    "implementation_boundary",
)
_REFERENCE_LISTS = ("local_files", "effect_ids")

_ENGINEERING_ONLY_PHRASES = (
    "普通视频防抖",
    "普通防抖",
    "ordinary stabilization",
    "普通视频去噪",
    "普通去噪",
    "ordinary denoising",
    "普通 hdr",
    "ordinary hdr",
    "普通超分",
    "ordinary super-resolution",
    "普通自动构图",
    "ordinary auto framing",
    "常规多摄切换",
    "conventional camera switching",
)

_SHA256_PATTERN = re.compile(r"^[0-9a-fA-F]{64}$")


def _require_mapping(record: object) -> Mapping[str, object]:
    if not isinstance(record, Mapping):
        raise ValueError("record must be a Mapping")
    return record


def _require_string(record: Mapping[str, object], field: str) -> str:
    if field not in record:
        raise ValueError(f"{field} is required")
    value = record[field]
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty string")
    return value


def _require_string_list(
    record: Mapping[str, object],
    field: str,
    *,
    allow_empty: bool = False,
) -> list[str]:
    if field not in record:
        raise ValueError(f"{field} is required")
    value = record[field]
    if not isinstance(value, list):
        raise ValueError(f"{field} must be a list")
    if not value and not allow_empty:
        raise ValueError(f"{field} must be a non-empty list")
    for index, item in enumerate(value):
        if not isinstance(item, str) or not item.strip():
            raise ValueError(f"{field}[{index}] must be a non-empty string")
    return value


def _validate_shape(
    record: object,
    *,
    scalar_fields: tuple[str, ...],
    list_fields: tuple[str, ...],
    empty_list_fields: frozenset[str] = frozenset(),
) -> Mapping[str, object]:
    mapping = _require_mapping(record)
    for field in scalar_fields:
        _require_string(mapping, field)
    for field in list_fields:
        _require_string_list(mapping, field, allow_empty=field in empty_list_fields)
    return mapping


def _require_id(value: str, field: str, prefix: str) -> None:
    pattern = rf"{re.escape(prefix)}[A-Z0-9][A-Z0-9_-]*"
    if re.fullmatch(pattern, value) is None:
        raise ValueError(f"{field} must match {prefix}[A-Z0-9][A-Z0-9_-]*")


def _require_id_list(values: list[str], field: str, prefix: str) -> None:
    for value in values:
        _require_id(value, field, prefix)


def _require_unique(values: list[str], field: str) -> None:
    if len(values) != len(set(values)):
        raise ValueError(f"{field} must not contain duplicate IDs")


def _require_enum(value: str, field: str, choices: frozenset[str]) -> None:
    if value not in choices:
        allowed = ", ".join(sorted(choices))
        raise ValueError(f"{field} must be one of: {allowed}")


def _require_reference_set(values: object, field: str) -> set[str]:
    if not isinstance(values, set):
        raise ValueError(f"{field} reference collection must be a set")
    if any(not isinstance(value, str) or not value.strip() for value in values):
        raise ValueError(f"{field} reference set must contain non-empty strings")
    return values


def _require_known(values: list[str], valid_ids: object, field: str) -> None:
    known = _require_reference_set(valid_ids, field)
    missing = sorted(set(values) - known)
    if missing:
        raise ValueError(f"{field} contains unknown references: {', '.join(missing)}")


def _normalize_text(value: str) -> str:
    return " ".join(value.split()).casefold()


def _iter_record_text(
    record: Mapping[str, object],
    *,
    excluded_fields: frozenset[str] = frozenset(),
):
    for field, value in record.items():
        if field in excluded_fields:
            continue
        if isinstance(value, str):
            yield value
        elif isinstance(value, list):
            yield from (item for item in value if isinstance(item, str))


def _claims_mobile_realtime_implementation(value: str) -> bool:
    text = _normalize_text(value)
    if (
        re.search(r"\bnot\b", text)
        or "no evidence" in text
        or "未" in text
        or "不" in text
        or "并非" in text
    ):
        return False

    chinese_claim = (
        "手机" in text
        and "实时" in text
        and any(term in text for term in ("实现", "量产", "运行", "部署"))
    )
    english_claim = (
        any(term in text for term in ("mobile", "phone", "smartphone"))
        and any(term in text for term in ("real time", "real-time"))
        and any(
            term in text
            for term in ("implemented", "production", "runs", "running", "deployed")
        )
    )
    return chinese_claim or english_claim


def validate_atom(record: Mapping[str, object]) -> None:
    """Validate a visible video-effect primitive."""

    mapping = _validate_shape(record, scalar_fields=_ATOM_SCALARS, list_fields=_ATOM_LISTS)
    _require_id(mapping["atom_id"], "atom_id", "ATOM-")


def validate_idea(
    record: Mapping[str, object],
    atom_ids: set[str] | None = None,
) -> None:
    """Validate a complete, interactive mobile video-effect idea."""

    mapping = _validate_shape(
        record,
        scalar_fields=_IDEA_SCALARS,
        list_fields=_IDEA_LISTS,
        empty_list_fields=_IDEA_EMPTY_LISTS,
    )
    _require_id(mapping["effect_id"], "effect_id", "FX-")
    _require_id_list(mapping["atom_ids"], "atom_ids", "ATOM-")
    _require_id_list(mapping["reference_ids"], "reference_ids", "REF-")
    _require_id_list(mapping["combinable_effect_ids"], "combinable_effect_ids", "FX-")
    _require_enum(mapping["generation_level"], "generation_level", GENERATION_LEVELS)
    _require_enum(mapping["edge_difficulty"], "edge_difficulty", EDGE_DIFFICULTIES)
    _require_enum(mapping["status"], "status", IDEA_STATUSES)

    if not mapping["trigger_signals"] and not mapping["user_controls"]:
        raise ValueError("trigger_signals or user_controls must provide an interaction trigger")
    if atom_ids is not None:
        _require_known(mapping["atom_ids"], atom_ids, "atom_ids")

    engineering_phrases = {_normalize_text(phrase) for phrase in _ENGINEERING_ONLY_PHRASES}
    for field in ("name_zh", "name_en", "visible_effect"):
        if _normalize_text(mapping[field]) in engineering_phrases:
            raise ValueError(
                f"{field} is an engineering-only feature and cannot be the main effect 主玩法"
            )


def validate_recipe(
    record: Mapping[str, object],
    atom_ids: set[str],
    idea_ids: set[str],
) -> None:
    """Validate a novel combination recipe across effect components."""

    mapping = _validate_shape(
        record,
        scalar_fields=_RECIPE_SCALARS,
        list_fields=_RECIPE_LISTS,
    )
    _require_id(mapping["recipe_id"], "recipe_id", "RECIPE-")
    _require_id_list(mapping["component_atom_ids"], "component_atom_ids", "ATOM-")
    _require_id_list(mapping["component_effect_ids"], "component_effect_ids", "FX-")
    _require_unique(mapping["component_atom_ids"], "component_atom_ids")
    _require_unique(mapping["component_effect_ids"], "component_effect_ids")
    _require_known(mapping["component_atom_ids"], atom_ids, "component_atom_ids")
    _require_known(mapping["component_effect_ids"], idea_ids, "component_effect_ids")

    components = {
        *(f"atom:{value}" for value in mapping["component_atom_ids"]),
        *(f"effect:{value}" for value in mapping["component_effect_ids"]),
    }
    if len(components) < 2:
        raise ValueError("component_atom_ids and component_effect_ids need at least two distinct components")

    for field, minimum in (("combined_effect", 16), ("why_new", 20)):
        compact = "".join(mapping[field].split())
        if len(compact) < minimum:
            raise ValueError(f"{field} is too short to explain a novel combination")


def validate_priority(record: Mapping[str, object], idea_ids: set[str]) -> None:
    """Validate a priority case with an implementation-level experience story."""

    mapping = _validate_shape(
        record,
        scalar_fields=_PRIORITY_SCALARS,
        list_fields=_PRIORITY_LISTS,
        empty_list_fields=frozenset({"references"}),
    )
    _require_id(mapping["priority_id"], "priority_id", "PRIORITY-")
    _require_id(mapping["effect_id"], "effect_id", "FX-")
    _require_id_list(mapping["references"], "references", "REF-")
    _require_known([mapping["effect_id"]], idea_ids, "effect_id")


def validate_reference(record: Mapping[str, object]) -> None:
    """Validate a real source and the boundary of what it demonstrates."""

    mapping = _validate_shape(
        record,
        scalar_fields=_REFERENCE_SCALARS,
        list_fields=_REFERENCE_LISTS,
        empty_list_fields=frozenset({"local_files"}),
    )
    _require_id(mapping["reference_id"], "reference_id", "REF-")
    _require_id_list(mapping["effect_ids"], "effect_ids", "FX-")
    _require_enum(mapping["source_type"], "source_type", SOURCE_TYPES)
    _require_enum(
        mapping["implementation_boundary"],
        "implementation_boundary",
        IMPLEMENTATION_BOUNDARIES,
    )

    if "year" not in mapping:
        raise ValueError("year is required")
    year = mapping["year"]
    if isinstance(year, bool) or not (
        isinstance(year, int) or isinstance(year, str) and bool(year.strip())
    ):
        raise ValueError("year must be an int or a non-empty string")

    if "sha256" not in mapping:
        raise ValueError("sha256 is required")
    sha256 = mapping["sha256"]
    if not isinstance(sha256, str):
        raise ValueError("sha256 must be a string")
    if sha256 and not _SHA256_PATTERN.fullmatch(sha256):
        raise ValueError("sha256 must be empty or exactly 64 hexadecimal characters")

    if mapping["implementation_boundary"] in {"film_postproduction", "visual_inspiration"}:
        text_fields = _iter_record_text(
            mapping,
            excluded_fields=frozenset({"does_not_prove"}),
        )
        if any(_claims_mobile_realtime_implementation(text) for text in text_fields):
            raise ValueError(
                "implementation_boundary cannot claim mobile real-time production or implementation"
            )
