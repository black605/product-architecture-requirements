#!/usr/bin/env python3
"""Deterministic release checks for the v3.5-v3.7 prototype-template workflow."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def exists(relative: str) -> bool:
    return (ROOT / relative).is_file()


def has_all(text: str, values: list[str]) -> bool:
    return all(value in text for value in values)


def main() -> int:
    skill = read("SKILL.md")
    snapshot = read("references/project-snapshot.md")
    profile = read("references/project-ui-profile.md")
    catalog = read("references/prototype-template-catalog.md")
    fit = read("references/prototype-template-fit.md")
    candidate = read("references/prototype-candidate-generation.md")
    assets = read("references/prototype-asset-slots.md")
    session = read("references/conversational-prototype-session.md")
    lifecycle = read("references/prototype-template-lifecycle.md")
    medium = read("references/medium-fidelity-handoff.md")
    runtime = read("references/a2ui-runtime-quality-gate.md")
    cross_skill = read("references/cross-skill-delivery.md")
    profile_schema = read("schemas/project-ui-profile.yaml")
    template_schema = read("schemas/template-definition.yaml")
    fit_schema = read("schemas/template-fit-decision.yaml")
    asset_schema = read("schemas/asset-slot-contract.yaml")
    candidate_schema = read("schemas/prototype-candidate.yaml")
    generation_schema = read("schemas/prototype-generation-request.yaml")
    manifest_schema = read("schemas/template-manifest.yaml")
    adversarial = read("tests/adversarial-cases.md")
    platforms = "\n".join(read(path) for path in (
        "platform/dify-config.md", "platform/coze-config.md", "platform/gpts-instructions.md"
    ))

    checks = {
        "01_entrypoint_progressive": len(skill.splitlines()) <= 220,
        "02_route_project_profile": "project-ui-profile.md" in skill,
        "03_route_template_catalog": "prototype-template-catalog.md" in skill,
        "04_route_template_fit": "prototype-template-fit.md" in skill,
        "05_route_candidate_generation": "prototype-candidate-generation.md" in skill,
        "06_route_asset_slots": "prototype-asset-slots.md" in skill,
        "07_route_conversation_session": "conversational-prototype-session.md" in skill,
        "08_route_template_lifecycle": "prototype-template-lifecycle.md" in skill,
        "09_snapshot_prototype_state": has_all(snapshot, ["prototype:", "ui_profile:", "template_fit_decisions:", "sessions:", "template_manifests:"]),
        "10_snapshot_stable_ids": has_all(snapshot, ["`UIP-`", "`TFD-`", "`ASC-`", "`PTC-`", "`PRS-`"]),
        "11_profile_schema_identity": has_all(profile_schema, ["profile_id: UIP-001", "project_id: PROJECT-001"]),
        "12_profile_is_project_independent": has_all(profile, ["独立", "每个 `project_id`", "历史项目 Profile"]),
        "13_profile_blocks_copy": has_all(profile_schema, ["copy: true", "sample_data: true", "business_rules: true"]),
        "14_profile_blocks_assets": has_all(profile_schema, ["visual_assets: true", "brand_tokens: true", "user_data: true"]),
        "15_inaccessible_evidence_not_invented": has_all(profile, ["inaccessible", "不得根据链接标题编造"]),
        "16_template_declares_seven_dimensions": has_all(template_schema, ["target_users:", "primary_tasks:", "page_types:", "information_hierarchy:", "required_regions:", "device_profiles:", "supported_states:"]),
        "17_template_has_no_embedded_content": has_all(template_schema, ["copy_embedded: false", "visual_assets_embedded: false", "business_rules_embedded: false"]),
        "18_fit_compares_seven_dimensions": has_all(fit, ["目标用户", "核心任务", "页面类型", "信息层级", "关键区域", "设备尺寸", "交互状态"]),
        "19_fit_has_three_results": has_all(fit, ["`exact`", "`extensible`", "`no_match`"]),
        "20_fit_has_hard_blockers": has_all(fit, ["硬阻塞项", "核心任务", "P0", "作用域"]),
        "21_fit_schema_has_enum_outputs": has_all(fit_schema, ["result: no_match", "selected_template_id:", "hard_blockers:", "required_extensions:"]),
        "22_exact_case_exists": exists("tests/exact-template-match.md"),
        "23_extensible_case_exists": exists("tests/extensible-template-match.md"),
        "24_no_match_case_exists": exists("tests/no-template-match.md"),
        "25_cross_project_case_exists": all(exists(path) for path in ["tests/cross-project-isolation.md", "tests/run_v37_isolation_scan.py", "tests/fixtures/cross-project/teacher-review-candidate.html"]),
        "26_asset_schema_has_geometry": has_all(asset_schema, ["aspect_ratio:", "min_size:", "max_size:", "safe_area:"]),
        "27_asset_schema_has_states": has_all(asset_schema, ["loading:", "empty:", "error:", "unavailable:", "extreme_content:"]),
        "28_asset_blocks_historical_fallback": has_all(asset_schema, ["allow_source_assets: false", "allow_historical_fallback: false"]),
        "29_candidate_is_project_local": has_all(candidate_schema, ["candidate_id: PTC-001", "scope: project-local"]),
        "30_candidate_is_neutral_and_asset_free": has_all(candidate_schema, ["profile: prototype-neutral", "visual_assets_included: false", "brand_tokens_included: false"]),
        "31_candidate_has_contamination_scan": has_all(candidate_schema, ["historical_copy_found: false", "historical_assets_found: false", "unconfirmed_business_rules_found: false"]),
        "32_medium_gate_requires_pui_uip_tfd": has_all(medium, ["`PUI-`", "`UIP-`", "`TFD-`"]),
        "33_medium_gate_handles_no_match": has_all(medium, ["`no_match`", "`ready-for-prototype`", "`PTC-`"]),
        "34_medium_gate_requires_asset_contract": has_all(medium, ["`ASC-`", "not_applicable"]),
        "35_generation_request_links_contracts": has_all(generation_schema, ["profile_id: UIP-001", "fit_decision_id: TFD-001", "prototype_candidate_id:", "asset_slot_contracts:"]),
        "36_generation_is_controlled": has_all(generation_schema, ["mode: controlled", "arbitrary_components_allowed: false", "arbitrary_business_actions_allowed: false"]),
        "37_session_has_pre_generation_summary": has_all(session, ["生成前摘要", "选中模具", "semantic_locked"]),
        "38_session_has_patch_tiers": has_all(session, ["L1", "L2", "L3", "before/after"]),
        "39_l3_returns_to_decision": has_all(session, ["创建 DEC/CHG", "退回上游"]),
        "40_conversation_case_exists": all(exists(path) for path in ["tests/conversational-prototype.md", "tests/run_v37_continuous_session.py"]),
        "41_lifecycle_states_complete": has_all(lifecycle + template_schema + manifest_schema, ["project-candidate", "in-validation", "validated", "registration-requested", "registered", "deprecated", "superseded"]),
        "42_manifest_has_owner_and_evidence": has_all(manifest_schema, ["owner: pending", "structural_audit:", "technical_validation:", "target_task_validation:"]),
        "43_registration_is_not_automatic": has_all(lifecycle, ["不能自动成为 shared", "authorized", "真实目录"]),
        "44_registry_and_deployment_are_separate": has_all(lifecycle, ["A2UI Registry", "生产部署", "分别记录"]),
        "45_lifecycle_case_exists": exists("tests/template-lifecycle.md"),
        "46_runtime_inherits_fit_decision": has_all(runtime, ["exact", "extensible", "no_match", "继承上游 `TFD-`"]),
        "47_cross_skill_has_conversation_handoff": has_all(cross_skill, ["`PRS-ID`", "Generation Request", "禁止继承项"]),
        "48_cross_skill_has_template_manifest": has_all(cross_skill, ["`TMF-ID`", "登记授权", "返回审计"]),
        "49_platforms_include_template_gate": has_all(platforms, ["ProjectUIProfile", "TemplateFitDecision", "exact", "extensible", "no_match"]),
        "50_adversarial_case_k_present": "## 用例 K：跨项目模具适配与对话原型" in adversarial,
    }

    if len(checks) != 50:
        raise RuntimeError(f"expected 50 checks, got {len(checks)}")
    result = {
        "suite": "v3.7-prototype-template",
        "checks": checks,
        "passed": all(checks.values()),
        "summary": f"{sum(checks.values())}/{len(checks)} checks passed",
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
