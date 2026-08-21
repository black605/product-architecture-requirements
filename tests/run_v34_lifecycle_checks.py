#!/usr/bin/env python3
"""Deterministic contract checks for the v3.4 lifecycle architecture."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def contains_all(text: str, values: list[str]) -> bool:
    return all(value in text for value in values)


def main() -> int:
    skill = read("SKILL.md")
    lifecycle = read("references/lifecycle-orchestration.md")
    snapshot = read("references/project-snapshot.md")
    convergence = read("references/requirements-convergence.md")
    low_friction = read("references/low-friction-dialogue.md")
    design_system = read("references/design-system-architecture.md")
    role_cases_v2 = json.loads(read("tests/role-dialogue-50-v2.json"))
    medium = read("references/medium-fidelity-handoff.md")
    ui_contract = read("references/prototype-ui-contract.md")
    operations = read("references/product-operations-loop.md")
    cross_skill = read("references/cross-skill-delivery.md")
    evidence = read("references/prototype-validation-evidence.md")
    production = read("references/production-handoff.md")
    cases = read("tests/v3.4-lifecycle-cases.md")
    adversarial = read("tests/adversarial-cases.md")
    platforms = "\n".join(
        read(path)
        for path in (
            "agents/openai.yaml",
            "platform/coze-config.md",
            "platform/dify-config.md",
            "platform/gpts-instructions.md",
        )
    )

    stages = [f"S{index}" for index in range(8)]
    statuses = [
        "Exploring",
        "Needs Decision",
        "Ready for Architecture",
        "Ready for Specification",
        "Ready for Prototype",
        "In Validation",
        "Validation Passed",
        "Handoff Ready",
        "Blocked",
        "Superseded",
    ]
    snapshot_fields = [
        "project_id:",
        "current_stage:",
        "delivery_status:",
        "product:",
        "evidence:",
        "governance:",
        "architecture:",
        "delivery:",
        "next_gate:",
    ]
    id_prefixes = ["OBJ-", "DEC-", "CHG-", "F-", "FL-", "TR-", "P-", "C-", "AC-", "T-", "ART-"]
    routed_refs = [
        "lifecycle-orchestration.md",
        "project-snapshot.md",
        "requirements-convergence.md",
        "low-friction-dialogue.md",
        "medium-fidelity-handoff.md",
        "prototype-ui-contract.md",
        "design-system-architecture.md",
        "product-operations-loop.md",
    ]

    checks = {
        "entrypoint_is_progressive": len(skill.splitlines()) <= 220 and all(value in skill for value in routed_refs),
        "lifecycle_has_s0_s7": contains_all(lifecycle, stages) and lifecycle.count("| S") >= 8,
        "status_vocabulary_complete": contains_all(skill + lifecycle, statuses),
        "snapshot_schema_complete": contains_all(snapshot, snapshot_fields),
        "stable_ids_complete": contains_all(snapshot, id_prefixes),
        "confirmed_names_are_stable_interfaces": contains_all(skill + snapshot, ["权威资料", "原样保留", "不能只用同义"]),
        "must_trace_reaches_artifact": contains_all(skill + snapshot, ["DEC", "F", "TR", "P", "AC", "T", "ART"]),
        "question_budget_and_l3_gate": contains_all(skill + convergence, ["严禁超过两个", "L3", "不能静默补全"]),
        "low_friction_role_dialogue_routed": contains_all(
            skill + low_friction,
            ["低摩擦自然语言对话", "教师/业务专家", "UI/UX 设计师", "运营", "研发/技术负责人", "Gate 未通过时", "硬上限 250 个汉字", "不展示 `S0–S7`"],
        ),
        "dialogue_quality_v347_complete": contains_all(
            skill + low_friction + convergence + lifecycle + snapshot,
            ["250 个汉字", "单一决策检查", "confirmed_summary", "turn_delta", "目标用户", "预期结果", "唯一主任务", "首期边界", "核心规则"],
        ),
        "role_dialogue_v2_has_50_cases": len(role_cases_v2) == 50
        and {item.get("role") for item in role_cases_v2}
        == {"教师/业务专家", "产品经理", "UI/UX 设计师", "运营", "研发/技术负责人"}
        and all(item.get("mode") in {"exploration", "delivery"} for item in role_cases_v2),
        "medium_fidelity_ready_gate": contains_all(medium, ["Ready for Prototype", "真实信息密度", "Mock/真实边界", "返回审计"]),
        "prototype_ui_contract_complete": contains_all(
            ui_contract,
            ["页面骨架", "P0/P1/P2", "操作层级", "组件语义", "页面状态", "上下游边界", "prototype-neutral", "semantic_locked", "visual_flexible", "pending_decisions", "forbidden_assumptions"],
        ),
        "prototype_gate_uses_contract": contains_all(
            skill + medium,
            ["prototype-ui-contract.md", "PUI-", "prototype-only", "Ready for Prototype"],
        ),
        "design_system_ai_contract_complete": contains_all(
            skill + design_system + adversarial,
            ["Ant Design", "shadcn/ui", "Park UI", "layout_pattern", "regions", "slots", "variants", "states", "responsive_rules", "token_refs", "traces_to"],
        ),
        "three_evidence_layers_separate": contains_all(skill + evidence, ["技术行为", "目标用户", "交接完整性", "一类证据不能替代另一类"]),
        "prototype_change_returns_to_decision": contains_all(medium + lifecycle, ["DEC/CHG", "退回", "重新过 Gate"]),
        "ui_contract_regression_case_present": "## 用例 H：原型 UI Contract 语义边界" in adversarial,
        "handoff_uses_snapshot_and_art_ids": contains_all(cross_skill + production, ["ProjectSnapshot", "ART-ID", "DEC/F/P/TR/AC/T"]),
        "operations_routes_five_workflows": contains_all(
            operations,
            ["User Research Synthesis", "Competitive Analysis", "Roadmap Management", "Stakeholder Updates", "Metrics Review"],
        ),
        "feature_spec_not_parallel_truth": "不调用其 Feature Spec 建立第二份 PRD" in skill and "不另建一套 PRD" in operations,
        "metrics_loop_has_actions": contains_all(operations, ["Continue", "Adjust", "Investigate", "Stop/Defer", "DEC/CHG"]),
        "platforms_preserve_lifecycle": contains_all(platforms, ["ProjectSnapshot", "DEC/CHG", "S0", "S7"]),
        "five_regression_scenarios_present": len(re.findall(r"^## [H-L]：", cases, re.MULTILINE)) == 5,
        "legacy_state_and_delivery_gates_preserved": contains_all(
            skill,
            ["自动读取", "Must 转移", "正向、守卫拒绝和恢复/终态测试", "Handoff Manifest", "返回审计"],
        ),
    }

    result = {
        "suite": "v3.4-lifecycle",
        "checks": checks,
        "passed": all(checks.values()),
        "summary": f"{sum(checks.values())}/{len(checks)} checks passed",
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
