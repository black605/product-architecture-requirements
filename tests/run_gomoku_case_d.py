#!/usr/bin/env python3
"""Run the end-to-end Gomoku friend-battle regression (case D)."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
CASE_DIR = SKILL_DIR / "tests" / "gomoku-case-d"
SCENARIO_PATH = CASE_DIR / "scenario.json"
RESPONSE_PATH = CASE_DIR / "latest-response.md"
RESULT_PATH = CASE_DIR / "result.json"
MANIFEST_PATH = CASE_DIR / "artifact-manifest.json"
CODEX = Path("/Applications/ChatGPT.app/Contents/Resources/codex")
DEFAULT_PROJECT_DIR = Path("/Users/tal/Documents/ChatGPT/新课件-0818")

ARTIFACT_FILES = {
    "prototype": "Gomoku Friend Battle Prototype.html",
    "development": "Development Tasks and Acceptance Checklist.md",
    "testing": "Test Cases and State Machines.md",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def count_questions(text: str) -> int:
    return len(re.findall(r"[？?]", text))


def all_present(text: str, values: list[str]) -> bool:
    return all(value in text for value in values)


def build_prompt(scenario: dict[str, object], artifact_dir: Path) -> str:
    artifacts = "\n".join(f"- {name}: {artifact_dir / filename}" for name, filename in ARTIFACT_FILES.items())
    return f"""请使用安装在 {SKILL_DIR} 的 $product-architecture-requirements 完成一次只读的正式回归评审。

必须读取：
- {SKILL_DIR / 'SKILL.md'}
- {SKILL_DIR / 'references/cross-skill-delivery.md'}
- {SKILL_DIR / 'references/decision-ledger.md'}
- {SKILL_DIR / 'references/state-test-gates.md'}
- {SCENARIO_PATH}

这是已经完成需求确认的五子棋好友比拼项目，不需要重新提问。权威场景数据如下：
{json.dumps(scenario, ensure_ascii=False, indent=2)}

以下是下游能力已经返回的真实产物，请逐个读取并做返回审计：
{artifacts}

请输出面向评审人的完整回归结果，至少包含：
1. 当前有效 DEC 决策快照与证据类型；
2. 自动触发状态机的原因，以及 GameInvite、TeamSession、MatchSession 的关键转移；
3. 邀请、组队、对局测试与功能/决策追溯；
4. 三类目标产物的 Handoff Manifest 与返回审计，使用 DEL 编号和 Ready/Completed/Blocked 状态；
5. 分别输出“Skill 本次运行表现四维评分”和“下游产物 Ready/Blocked 判定”。四维评分评价 Skill 是否正确引导、建模、穿透和约束，不把输入产物自身缺陷反向算成 Skill 扣分；产物缺陷必须保留在独立的返回审计中。

约束：
- 本次是只读评审，不修改文件、不发布、不推送；
- 不输出 React/CSS/后端实现代码；Mermaid 状态图可以使用；
- 不把文档中的 Needs Decision 或未勾选项说成已验收；
- 已确认信息足够，不提出新问题；若发现缺口，标记影响和责任，不自行补规则。
"""


def run_runtime(scenario: dict[str, object], artifact_dir: Path, project_dir: Path) -> dict[str, object]:
    if not CODEX.exists():
        raise SystemExit(f"Codex runtime not found: {CODEX}")
    with tempfile.NamedTemporaryFile(prefix="gomoku-case-d-", suffix=".md", delete=False) as handle:
        output_path = Path(handle.name)
    command = [
        str(CODEX),
        "exec",
        "--json",
        "--ephemeral",
        "--skip-git-repo-check",
        "-s",
        "read-only",
        "-C",
        str(project_dir),
        "-o",
        str(output_path),
        "-",
    ]
    try:
        result = subprocess.run(
            command,
            input=build_prompt(scenario, artifact_dir),
            text=True,
            capture_output=True,
            timeout=300,
            check=False,
        )
        response = output_path.read_text(encoding="utf-8") if output_path.exists() else ""
        RESPONSE_PATH.write_text(response, encoding="utf-8")
        return {
            "exit_code": result.returncode,
            "response_bytes": len(response.encode("utf-8")),
            "platform_output_present": bool((result.stdout + result.stderr).strip()),
        }
    finally:
        output_path.unlink(missing_ok=True)


def static_checks() -> dict[str, bool]:
    skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
    adversarial = (SKILL_DIR / "tests" / "adversarial-cases.md").read_text(encoding="utf-8")
    required_files = [
        SKILL_DIR / "references" / "cross-skill-delivery.md",
        SKILL_DIR / "references" / "decision-ledger.md",
        SKILL_DIR / "references" / "state-test-gates.md",
    ]
    return {
        "references_exist": all(path.exists() for path in required_files),
        "references_routed_from_skill": all(path.name in skill for path in required_files),
        "case_d_is_gomoku": "## 用例 D：五子棋好友比拼" in adversarial,
        "legacy_education_case_preserved": "## 用例 F：教育内容功能迭代" in adversarial,
        "cross_skill_ready_gate_present": all_present(skill, ["Handoff Manifest", "返回审计", "需求达到 Ready"]),
        "decision_ledger_gate_present": all_present(skill, ["DEC/CHG", "Superseded", "唯一明确"]),
        "state_test_gate_present": all_present(skill, ["自动读取", "Must 转移", "正向、守卫拒绝和恢复/终态测试"]),
    }


def artifact_checks(artifact_dir: Path, scenario: dict[str, object]) -> tuple[dict[str, bool], dict[str, object]]:
    paths = {name: artifact_dir / filename for name, filename in ARTIFACT_FILES.items()}
    texts = {name: path.read_text(encoding="utf-8") if path.exists() else "" for name, path in paths.items()}
    prototype = texts["prototype"]
    development = texts["development"]
    testing = texts["testing"]
    required_routes = list(scenario["required_routes"])
    required_features = list(scenario["required_feature_ids"])
    test_ids = set(re.findall(r"\b[A-Z]{2}-\d{3}\b", testing))
    checks = {
        "all_artifacts_exist": all(path.is_file() for path in paths.values()),
        "prototype_has_six_pages": len(set(re.findall(r'data-page="(home|friends|add|messages|lobby|game)"', prototype))) == 6,
        "routes_are_traced": all_present(development + testing, required_routes),
        "features_f01_f09_present": all_present(development, required_features),
        "key_timing_rules_present": all_present(development + testing, ["15 秒", "5 分钟", "双方准备"]),
        "concurrent_invite_rule_present": "对方已进入对弈中" in development + testing,
        "state_machines_present": testing.count("stateDiagram-v2") >= 4,
        "test_case_volume_sufficient": len(test_ids) >= 60,
        "domain_test_families_present": all(any(value.startswith(prefix) for value in test_ids) for prefix in ("IN-", "TM-", "GM-")),
        "handoff_statuses_present": all_present(development, ["Ready", "Blocked", "Needs Decision"]),
    }
    manifest = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "artifact_dir": str(artifact_dir),
        "files": {
            name: {
                "path": str(path),
                "exists": path.is_file(),
                "size": path.stat().st_size if path.exists() else 0,
                "sha256": sha256(path) if path.is_file() else None,
            }
            for name, path in paths.items()
        },
    }
    return checks, manifest


def runtime_checks(response: str, scenario: dict[str, object]) -> dict[str, bool]:
    decision_ids = set(re.findall(r"\bDEC-\d{3}\b", response))
    test_ids = set(re.findall(r"\b(?:IN|TM|GM)-\d{3}\b", response))
    no_impl = re.search(
        r"```(?:tsx|jsx|javascript|css|python|sql|java|go)\b|import\s+React\b|<div\b|function\s+\w+\s*\(",
        response,
        re.IGNORECASE,
    ) is None
    return {
        "response_present": bool(response.strip()),
        "no_redundant_questions": count_questions(response) <= 2,
        "decision_ledger_complete": len(decision_ids) >= len(scenario["confirmed_decisions"]),
        "confirmed_evidence_label_present": "Confirmed" in response or "已确认" in response,
        "cross_skill_manifest_present": bool(re.search(r"Handoff Manifest|交付清单", response, re.IGNORECASE)) and bool(re.search(r"\bDEL-\d{3}\b", response)),
        "three_deliverables_audited": all_present(response, ["高保真", "研发", "测试"]),
        "state_trigger_explained": all_present(response, ["GameInvite", "TeamSession", "MatchSession"]),
        "state_diagrams_or_transitions_present": response.count("stateDiagram-v2") >= 1 and response.count("-->") >= 6,
        "test_trace_present": len(test_ids) >= 3 and all(any(value.startswith(prefix) for value in test_ids) for prefix in ("IN-", "TM-", "GM-")),
        "key_rules_preserved": all_present(response, ["15 秒", "5 分钟", "双方准备", "对方已进入对弈中", "学习机横屏", "暖色"]),
        "scope_boundary_preserved": all_present(response, ["好友互通", "消息中心", "不阻塞"]),
        "no_implementation_code": no_impl,
        "read_only_boundary_preserved": not any(value in response for value in ("已修改文件", "已发布文件", "已推送文件")) and (
            "不可作为发布终版" in response
            or "不可称为生产终版" in response
            or "不可标记为发布完成" in response
            or "未修改、发布或推送" in response
        ),
        "unverified_work_not_reported_done": "Needs Decision" in response and ("未验收" in response or "未勾选" in response or "阻塞" in response),
        "four_dimension_score_present": (
            "引导" in response
            and ("架构" in response or "建模" in response)
            and ("UI/UX" in response or "设计穿透" in response or "| 穿透 |" in response)
            and "约束" in response
        ),
        "skill_and_artifact_scores_separated": ("Skill" in response or "技能" in response) and "Blocked" in response,
    }


def score_groups(static: dict[str, bool], runtime: dict[str, bool], artifact: dict[str, bool]) -> dict[str, int]:
    groups = {
        "elicitation": [
            static["decision_ledger_gate_present"],
            runtime["no_redundant_questions"],
            runtime["decision_ledger_complete"],
            runtime["confirmed_evidence_label_present"],
        ],
        "architecture": [
            static["state_test_gate_present"],
            runtime["state_trigger_explained"],
            runtime["key_rules_preserved"],
            runtime["scope_boundary_preserved"],
            artifact["features_f01_f09_present"],
            artifact["concurrent_invite_rule_present"],
        ],
        "ui_ux": [
            runtime["cross_skill_manifest_present"],
            runtime["three_deliverables_audited"],
            artifact["prototype_has_six_pages"],
            artifact["routes_are_traced"],
            artifact["state_machines_present"],
        ],
        "constraint": [
            static["cross_skill_ready_gate_present"],
            runtime["no_implementation_code"],
            runtime["read_only_boundary_preserved"],
            runtime["unverified_work_not_reported_done"],
            runtime["skill_and_artifact_scores_separated"],
            artifact["handoff_statuses_present"],
        ],
    }
    return {name: round(25 * sum(values) / len(values)) for name, values in groups.items()}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-runtime", action="store_true")
    parser.add_argument("--artifact-dir", type=Path, required=True)
    parser.add_argument("--project-dir", type=Path, default=DEFAULT_PROJECT_DIR)
    args = parser.parse_args()

    scenario = json.loads(SCENARIO_PATH.read_text(encoding="utf-8"))
    previous_result = json.loads(RESULT_PATH.read_text(encoding="utf-8")) if RESULT_PATH.exists() else {}
    runtime_meta: dict[str, object] = dict(previous_result.get("runtime", {"executed": False}))
    if args.run_runtime:
        runtime_meta = {"executed": True, **run_runtime(scenario, args.artifact_dir, args.project_dir)}

    response = RESPONSE_PATH.read_text(encoding="utf-8") if RESPONSE_PATH.exists() else ""
    static = static_checks()
    artifact, manifest = artifact_checks(args.artifact_dir, scenario)
    runtime = runtime_checks(response, scenario)
    scores = score_groups(static, runtime, artifact)
    total = sum(scores.values())
    passed = (
        total >= 90
        and min(scores.values()) >= 15
        and all(static.values())
        and all(artifact.values())
        and all(runtime.values())
        and (not args.run_runtime or runtime_meta.get("exit_code") == 0)
    )
    result = {
        "case_id": "D",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "runtime": runtime_meta,
        "checks": {"static": static, "runtime": runtime, "artifacts": artifact},
        "scores": {**scores, "total": total},
        "passed": passed,
    }
    RESULT_PATH.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
