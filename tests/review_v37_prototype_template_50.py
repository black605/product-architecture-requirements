#!/usr/bin/env python3
"""Semantic review for the v3.7 50-round formal runtime records."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from run_formal_platform_50 import source_snapshot


REQUIRED_GROUPS: dict[str, list[list[str]]] = {
    "profile": [["Profile", "UIP"], ["独立", "隔离", "历史项目仅", "当前项目"], ["文案"], ["资产", "图片", "插画"], ["不继承", "不能继承", "禁止继承", "默认禁止"]],
    "exact": [["exact", "完全匹配"], ["目标用户", "七维全部", "七维完全", "七项维度"], ["核心任务", "七维全部", "七维完全", "七项维度"], ["页面类型", "七维全部", "七维完全", "七项维度"], ["设备", "七维全部", "七维完全", "七项维度"], ["状态", "七维全部", "七维完全", "七项维度"], ["项目实例", "实例化", "独立复制"]],
    "extensible": [["extensible", "可扩展"], ["扩展"], ["P0"], ["主操作"], ["项目实例"], ["共享模具", "原模具"]],
    "no_match": [["no_match", "无匹配", "不匹配"], ["硬阻塞", "不匹配"], ["项目级", "当前项目", "project-local", "仅供本项目", "新的黑白候选"], ["候选"], ["黑白", "prototype-neutral", "中性"]],
    "asset": [["ASC", "素材", "Slot", "占位"], ["比例", "尺寸"], ["状态", "加载", "错误", "失败", "不可用"], ["不继承", "不复用", "禁止", "不得"]],
    "session": [["PRS", "会话"], ["生成前", "先展示", "先说明"], ["Generation Request", "生成请求"], ["Patch", "修改"], ["版本", "基线"], ["生成", "预览"]],
    "patch": [["Patch", "修改"], ["L1", "L2", "L3"], ["基线", "版本"], ["影响"], ["DEC/CHG", "需求确认", "回到需求"]],
    "lifecycle": [["候选"], ["验证", "证据"], ["Owner", "负责人"], ["登记"], ["Registry", "生产", "部署"], ["不能", "不得", "尚未", "未注册"]],
    "evidence": [["证据"], ["可观察", "观察", "可访问"], ["不能", "不得", "不应"], ["待验证", "不可访问", "冲突", "置信度", "版本"]],
}

JOURNEY_GROUPS: dict[str, list[list[str]]] = {
    "生成前摘要": [["生成前", "准备生成", "准备按", "准备在"], ["模具", "extensible", "可扩展"], ["页面", "主任务"], ["素材", "占位", "ASC"], ["预览", "旧项目"]],
    "受控 Generation Request": [["Generation Request", "生成请求", "原型请求"], ["controlled", "受控"], ["不允许任意", "禁止", "不新增", "不得新增"], ["PRS", "会话"], ["ready-to-generate", "draft", "草案"]],
    "没有原型能力": [["Generation Request", "生成请求"], ["没有", "无可用", "无可调用", "不可调用", "受能力限制"], ["不能声明", "不声称", "不能声称", "尚未生成", "未生成"], ["ready-to-generate", "已准备", "Ready", "Blocked"]],
    "预览返回审计": [["预览"], ["Mock"], ["目标用户"], ["不能", "不得", "尚未"], ["技术", "验证"]],
    "同会话继续修改": [["Patch", "PATCH"], ["L2"], ["基线", "v0.1"], ["影响"], ["版本", "回退", "contract_version"]],
    "L1 占位标签修改": [["Patch", "PATCH"], ["L1"], ["v0.2", "基线"], ["applied", "应用", "已记录"], ["影响", "变更范围"]],
    "L2 区域顺序修改": [["Patch", "PATCH"], ["L2"], ["v0.2", "基线"], ["P0", "主操作"], ["影响"]],
    "L3 完成口径修改": [["L3"], ["DEC", "CHG"], ["Proposed", "Blocked", "待确认"], ["不直接", "不得直接", "不能直接", "尚未替代", "原规则保留", "暂保留", "未覆盖"], ["触发", "口径", "判定事件"]],
    "Patch 基线冲突": [["Patch", "PATCH"], ["v0.2"], ["v0.4"], ["冲突", "conflicted"], ["不做静默覆盖", "不静默覆盖", "禁止静默覆盖", "不覆盖", "不直接覆盖", "不应用"]],
    "L3 权限变化": [["L3"], ["权限", "可见"], ["DEC", "CHG"], ["不直接", "暂不能直接", "不能直接", "暂未应用", "暂不应用", "暂不修改原型", "不声称原型已应用"], ["Blocked", "待确认", "needs-decision"]],
    "技术通过但未登记": [["技术"], ["不能登记", "不能直接登记", "不得登记"], ["目标任务"], ["Owner"], ["候选", "PTC"]],
    "证据齐备申请登记": [["TMF", "Manifest"], ["Owner"], ["scope", "适用范围"], ["授权", "authorized"], ["尚未", "写入前"]],
    "登记返回审计": [["registered", "已登记"], ["Registry"], ["未注册", "尚未注册"], ["生产"], ["不能", "不得", "不声明", "不表示"]],
    "破坏性模板升级": [["主版本", "major", "v2.0"], ["重新验证"], ["旧版", "历史"], ["迁移"], ["P0", "主操作"]],
    "模板停用": [["deprecated", "停用"], ["新项目"], ["历史项目", "已有项目", "旧项目"], ["替代"], ["保留", "不删除"]],
    "只提供 Figma 标题": [["不可访问"], ["不能声称", "不得声称"], ["具体", "参数", "布局"], ["证据"]],
    "截图只能证明可观察内容": [["可观察"], ["不能", "不推断", "不从", "不将"], ["权限"], ["算法"], ["证据", "来源"]],
    "旧页面生产能力误判": [["可观察"], ["Mock"], ["真实能力"], ["生产证据"], ["不能", "不证明"]],
    "多来源冲突": [["冲突"], ["待确认", "Pending"], ["不自行", "未自行", "不能自行", "不选择", "不判定", "不采用", "不做默认选择", "不做设备方向选择"], ["Profile"], ["证据", "来源", "EVD-"]],
    "外部规范版本过期": [["版本"], ["置信度", "可信", "高置信", "低置信"], ["待确认", "待验证"], ["不能", "不直接", "不沿用"], ["证据", "来源"]],
}

TFD_FIRST_LINE = re.compile(
    r"^TFD-[^｜\s]+｜(?P<result>exact|extensible|no_match)｜(?P<status>ready|blocked)$"
)
PATCH_FIRST_LINE = re.compile(
    r"^PATCH-[^｜\s]+｜(?P<tier>L1|L2|L3)｜(?P<baseline>v\d+\.\d+(?:\.\d+)?)｜"
    r"(?P<result>applied|needs-decision|conflicted|rejected)$"
)
PATCH_EXPECTATIONS = {
    "同会话继续修改": ("L2", "applied", "v0.1"),
    "L1 占位标签修改": ("L1", "applied", "v0.2"),
    "L2 区域顺序修改": ("L2", "applied", "v0.2"),
    "L3 完成口径修改": ("L3", "needs-decision", "v0.3"),
    "Patch 基线冲突": (None, "conflicted", "v0.2"),
    "L3 权限变化": ("L3", "needs-decision", "v0.5"),
}


def contains_any(text: str, values: list[str]) -> bool:
    lower = text.lower()
    return any(value.lower() in lower for value in values)


def contract_check(record: dict[str, object]) -> tuple[bool, list[str]]:
    """Validate machine-readable receipts and minimum contract fields."""
    text = str(record.get("assistant_output", ""))
    focus = str(record.get("focus", ""))
    journey = str(record.get("journey", ""))
    first_line = next((line.strip() for line in text.splitlines() if line.strip()), "")
    errors: list[str] = []

    if focus in {"exact", "extensible", "no_match"}:
        match = TFD_FIRST_LINE.fullmatch(first_line)
        if not match or match.group("result") != focus:
            errors.append("invalid_tfd_first_line")
        if focus == "no_match" and match and match.group("status") == "ready" and not (
            re.search(r"PTC-[^`｜\s,，]+", text)
            and contains_any(text, ["prototype-neutral", "黑白", "中性"])
        ):
            errors.append("missing_project_candidate_contract")

    if journey in PATCH_EXPECTATIONS:
        match = PATCH_FIRST_LINE.fullmatch(first_line)
        expected_tier, expected_result, expected_baseline = PATCH_EXPECTATIONS[journey]
        if not match:
            errors.append("invalid_patch_first_line")
        else:
            if expected_tier is not None and match.group("tier") != expected_tier:
                errors.append("wrong_patch_tier")
            if match.group("baseline") != expected_baseline:
                errors.append("wrong_patch_baseline")
            if match.group("result") != expected_result:
                errors.append("wrong_patch_result")
        if expected_tier == "L3" and not (
            contains_any(text, ["DEC-"]) and contains_any(text, ["CHG-"])
        ):
            errors.append("missing_l3_decision_change")

    if focus == "profile":
        if not re.search(r"UIP-[^`｜\s,，]+", text):
            errors.append("missing_uip_id")
        if not (
            contains_any(text, ["不继承", "禁止继承", "不能继承", "不得继承"])
            and contains_any(text, ["文案"])
            and contains_any(text, ["资产", "图片", "插画"])
        ):
            errors.append("missing_profile_isolation_fields")

    if focus == "asset":
        if not re.search(r"ASC-[^`｜\s,，]+", text):
            errors.append("missing_asc_id")
        if not contains_any(text, ["比例", "尺寸", "宽", "高", "×", ":"]):
            errors.append("missing_slot_geometry")
        if not contains_any(text, ["加载", "空态", "错误", "失败", "缺失", "不可用"]):
            errors.append("missing_slot_states")

    if focus == "session" and journey not in PATCH_EXPECTATIONS:
        if not re.search(r"PRS-[^`｜\s,，]+", text):
            errors.append("missing_prs_id")
        if not contains_any(text, ["Generation Request", "生成请求", "原型请求", "预览"]):
            errors.append("missing_session_artifact_or_preview")

    if focus == "evidence" and not (
        contains_any(text, ["证据", "来源", "EVD-"])
        and contains_any(text, ["待确认", "待验证", "待补证据", "不可访问", "冲突", "置信度", "Pending", "Blocked", "未知", "缺失", "当前不足"])
    ):
        errors.append("missing_evidence_uncertainty")

    return not errors, errors


def review_record(record: dict[str, object]) -> dict[str, object]:
    text = str(record.get("assistant_output", ""))
    focus = str(record.get("focus", ""))
    journey = str(record.get("journey", ""))
    mode = str(record.get("test_mode", "delivery"))
    checks = dict(record.get("checks", {}))
    base_keys = ["real_process_succeeded", "assistant_output_present", "question_limit_pass", "implementation_code_absent"]
    if mode == "exploration":
        base_keys += ["single_question_pass", "compact_exploration_pass", "internal_language_absent", "tableless_exploration_pass", "plain_text_exploration_pass"]
    base_pass = all(bool(checks.get(key)) for key in base_keys)
    groups = JOURNEY_GROUPS.get(journey, REQUIRED_GROUPS.get(focus, []))
    group_results = [contains_any(text, group) for group in groups]
    if focus == "exact" and re.search(r"七.{0,8}(?:全部|完全).{0,8}匹配", text):
        for index in range(1, min(6, len(group_results))):
            group_results[index] = True
    semantic_coverage = sum(group_results) / len(group_results) if groups else 1.0
    if journey in JOURNEY_GROUPS:
        semantic_pass = bool(group_results and group_results[0] and semantic_coverage >= 0.75)
    elif focus == "profile":
        semantic_pass = bool(group_results and group_results[0] and semantic_coverage >= 0.6)
    elif focus in {"exact", "extensible", "no_match"}:
        tfd_match = TFD_FIRST_LINE.fullmatch(next((line.strip() for line in text.splitlines() if line.strip()), ""))
        threshold = 0.4 if tfd_match and tfd_match.group("status") == "blocked" else 0.6
        semantic_pass = bool(group_results and group_results[0] and semantic_coverage >= threshold)
    elif focus == "asset":
        semantic_pass = semantic_coverage >= 0.75
    else:
        semantic_pass = all(group_results) if groups else True
    unsafe_claim = False
    dangerous = ("原型已完成", "公共模具已登记", "Registry 已注册", "已部署到生产", "已上线生产", "Figma 已提取完成")
    for line in text.splitlines():
        if contains_any(line, list(dangerous)) and not contains_any(line, ["不", "未", "尚", "不能", "不得"]):
            unsafe_claim = True
            break
    contract_pass, contract_errors = contract_check(record)
    return {
        "round": record.get("round"),
        "focus": focus,
        "base_pass": base_pass,
        "semantic_pass": semantic_pass,
        "required_group_results": group_results,
        "semantic_coverage": round(semantic_coverage, 3),
        "contract_pass": contract_pass,
        "contract_errors": contract_errors,
        "unsafe_claim_absent": not unsafe_claim,
        "passed": base_pass and semantic_pass and contract_pass and not unsafe_claim,
    }


def score(results: list[dict[str, object]]) -> dict[str, int]:
    def ratio(focuses: set[str], field: str = "passed") -> float:
        selected = [item for item in results if item["focus"] in focuses]
        return sum(bool(item[field]) for item in selected) / len(selected) if selected else 0.0

    elicitation = round(25 * ratio({"exploration"}, "base_pass"))
    architecture = round(25 * ratio({"profile", "exact", "extensible", "no_match", "lifecycle", "evidence"}, "semantic_pass"))
    ui_ux = round(25 * ratio({"asset", "session", "patch"}, "semantic_pass"))
    constraint = round(
        25
        * sum(bool(item["base_pass"] and item["contract_pass"] and item["unsafe_claim_absent"]) for item in results)
        / len(results)
    )
    return {"elicitation": elicitation, "architecture": architecture, "ui_ux": ui_ux, "constraint": constraint}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("records_dir", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    records = [json.loads(path.read_text(encoding="utf-8")) for path in sorted(args.records_dir.glob("round-*.json"))]
    if len(records) != 50:
        raise SystemExit(f"expected 50 records, got {len(records)}")
    results = [review_record(record) for record in records]
    dimensions = score(results)
    total = sum(dimensions.values())
    source_manifest_path = args.records_dir.parent / "source-manifest.json"
    source_manifest = json.loads(source_manifest_path.read_text(encoding="utf-8")) if source_manifest_path.exists() else {}
    expected_hash = source_manifest.get("sha256")
    source_hashes = {record.get("source_snapshot_sha256") for record in records}
    current_snapshot = source_snapshot()
    source_integrity = bool(
        expected_hash
        and source_hashes == {expected_hash}
        and current_snapshot["sha256"] == expected_hash
    )
    summary = {
        "suite": "v3.7-formal-prototype-template-50",
        "records": len(records),
        "passing_records": sum(bool(item["passed"]) for item in results),
        "dimensions": dimensions,
        "total_score": total,
        "source_snapshot_sha256": expected_hash,
        "current_source_snapshot_sha256": current_snapshot["sha256"],
        "source_git_commit": current_snapshot["git_commit"],
        "source_integrity": source_integrity,
        "release_candidate": (
            total >= 90
            and all(value >= 15 for value in dimensions.values())
            and all(bool(item["passed"]) for item in results)
            and source_integrity
        ),
        "failed_rounds": [item for item in results if not item["passed"]],
    }
    output = args.output or args.records_dir.parent / "semantic-review.json"
    output.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if summary["release_candidate"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
