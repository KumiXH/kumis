"""Build the machine-readable and human-readable mobile video-effect library."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from tools.video_effects import effect_catalog, priority_catalog, recipe_catalog


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PROJECT = ROOT / "daily" / "20260827_录像特效调研"


def _write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def _write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value.rstrip() + "\n", encoding="utf-8", newline="\n")


def _bullet(values: list[str]) -> str:
    return "；".join(values) if values else "无"


def build_stats(
    atoms: list[dict[str, object]],
    ideas: list[dict[str, object]],
    recipes: list[dict[str, object]],
    priorities: list[dict[str, object]],
) -> dict[str, object]:
    return {
        "counts": {
            "atoms": len(atoms),
            "ideas": len(ideas),
            "recipes": len(recipes),
            "priorities": len(priorities),
        },
        "atom_family_counts": dict(Counter(str(row["family"]) for row in atoms)),
        "idea_family_counts": dict(Counter(str(row["family"]) for row in ideas)),
        "generation_level_counts": dict(
            Counter(str(row["generation_level"]) for row in ideas)
        ),
        "edge_difficulty_counts": dict(Counter(str(row["edge_difficulty"]) for row in ideas)),
        "recipe_family_counts": recipe_catalog.validate_recipes(
            recipes,
            {str(row["atom_id"]) for row in atoms},
            {str(row["effect_id"]) for row in ideas},
        )["family_counts"],
        "priority_family_counts": priority_catalog.count_effect_families(priorities),
        "priority_detail_counts": {
            "interaction_timeline_items": sum(len(row["interaction_timeline"]) for row in priorities),
            "module_pipeline_items": sum(len(row["module_pipeline"]) for row in priorities),
            "adjustable_parameter_items": sum(len(row["adjustable_parameters"]) for row in priorities),
            "fallback_items": sum(len(row["failure_and_fallback"]) for row in priorities),
        },
    }


def build_readme(stats: dict[str, object]) -> str:
    counts = stats["counts"]
    return "\n".join(
        (
            "# 手机录像特效玩法库",
            "",
            "本目录以用户可直接看到、操控和分享的录像特效为中心，不把普通防抖、去噪、HDR、超分和常规运镜当作主玩法。",
            "",
            "## 当前规模",
            "",
            f"- 特效原子：{counts['atoms']}",
            f"- 完整玩法：{counts['ideas']}",
            f"- 组合配方：{counts['recipes']}",
            f"- 重点深拆：{counts['priorities']}",
            "",
            "## 阅读入口",
            "",
            "- `report/手机录像特效玩法全量库_20260827.md`：300 个完整玩法的全量检索入口。",
            "- `metadata/priority_effects.jsonl`：50 个重点玩法的实现级拆解。",
            "- `metadata/effect_recipes.jsonl`：200 个跨原子/跨玩法组合配方。",
            "- `metadata/effect_stats.json`：实际统计，不用计划目标冒充完成数量。",
            "",
            "## 使用边界",
            "",
            "预览预算只给出代理分辨率、ROI、实例上限、缓存和降级方向；未经实机测量的时延、帧率、功耗和内存数字不作为结论。生成式玩法还需单独评估身份漂移、几何错误、时序闪烁和事实改写风险。",
        )
    )


def build_full_report(
    ideas: list[dict[str, object]],
    priorities: list[dict[str, object]],
    stats: dict[str, object],
) -> str:
    priority_ids = {str(row["effect_id"]): str(row["priority_id"]) for row in priorities}
    lines = [
        "# 手机录像特效玩法全量库",
        "",
        "本报告列出全部完整玩法。每条玩法均绑定可见结果、交互、实时预览、录后重算、风险和组合入口。",
        "",
        "## 统计",
        "",
        f"- 特效原子：{stats['counts']['atoms']}",
        f"- 完整玩法：{stats['counts']['ideas']}",
        f"- 组合配方：{stats['counts']['recipes']}",
        f"- 重点深拆：{stats['counts']['priorities']}",
        "",
    ]
    by_family = {family: [] for family in effect_catalog.IDEA_FAMILY_ORDER}
    for idea in ideas:
        by_family[str(idea["family"])].append(idea)

    for family in effect_catalog.IDEA_FAMILY_ORDER:
        lines.extend((f"## {family}", ""))
        for idea in by_family[family]:
            effect_id = str(idea["effect_id"])
            lines.extend(
                (
                    f"### {idea['name_zh']}",
                    "",
                    f"- **ID**：`{effect_id}`",
                    f"- **可见效果**：{idea['visible_effect']}",
                    f"- **交互**：{idea['interaction']}",
                    f"- **触发**：{_bullet(idea['trigger_signals'])}",
                    f"- **控制**：{_bullet(idea['user_controls'])}",
                    f"- **实时预览**：{idea['preview_pipeline']}",
                    f"- **录后重算**：{idea['post_pipeline']}",
                    f"- **时间窗口**：{idea['temporal_window']}",
                    f"- **风险**：{_bullet(idea['risks'])}",
                    f"- **组合入口**：{_bullet(idea['combinable_effect_ids'])}",
                    f"- **重点深拆**：{priority_ids.get(effect_id, '未列入重点 50')}",
                    "",
                )
            )
    return "\n".join(lines)


def build_all(project_root: Path = DEFAULT_PROJECT) -> dict[str, Path]:
    project_root = Path(project_root)
    metadata = project_root / "metadata"
    report = project_root / "report"
    atom_path = metadata / "effect_atoms.jsonl"
    idea_path = metadata / "effect_ideas.jsonl"
    recipe_path = metadata / "effect_recipes.jsonl"
    priority_path = metadata / "priority_effects.jsonl"
    stats_path = metadata / "effect_stats.json"
    readme_path = project_root / "README.md"
    full_report_path = report / "手机录像特效玩法全量库_20260827.md"

    atoms = effect_catalog.build_atoms()
    ideas = effect_catalog.build_ideas()
    recipes = recipe_catalog.build_recipes()
    priorities = priority_catalog.build_priorities()
    atom_ids = {str(row["atom_id"]) for row in atoms}
    idea_ids = {str(row["effect_id"]) for row in ideas}

    effect_catalog.validate_atoms(atoms)
    effect_catalog.validate_ideas(ideas, atom_ids)
    recipe_catalog.validate_recipes(recipes, atom_ids, idea_ids)
    priority_catalog.validate_priorities(priorities, idea_ids)

    effect_catalog.write_jsonl(atoms, atom_path)
    effect_catalog.write_ideas_jsonl(ideas, idea_path)
    recipe_catalog.write_jsonl(recipes, recipe_path)
    priority_catalog.write_jsonl(priorities, priority_path)

    stats = build_stats(atoms, ideas, recipes, priorities)
    _write_json(stats_path, stats)
    _write_text(readme_path, build_readme(stats))
    _write_text(full_report_path, build_full_report(ideas, priorities, stats))
    return {
        "atoms": atom_path,
        "ideas": idea_path,
        "recipes": recipe_path,
        "priorities": priority_path,
        "stats": stats_path,
        "readme": readme_path,
        "full_report": full_report_path,
    }


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=DEFAULT_PROJECT)
    args = parser.parse_args(argv)
    outputs = build_all(args.project_root)
    for name, path in outputs.items():
        print(f"{name}: {path}")


if __name__ == "__main__":
    main()
