#!/usr/bin/env python3
"""Behavioral release checks for the executable prototype harness."""

from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HARNESS = ROOT / "harness"
GOLDEN = ROOT / "tests" / "golden" / "ai-speaking-1280"


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([str(HARNESS), *args], cwd=ROOT, text=True, capture_output=True, timeout=60, check=False)


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def save(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def has_error(output: str, error_type: str) -> bool:
    try:
        return any(item.get("type") == error_type for item in json.loads(output).get("errors", []))
    except json.JSONDecodeError:
        return False


def main() -> int:
    checks: dict[str, bool] = {}
    with tempfile.TemporaryDirectory(prefix="product-harness-v40-") as temp:
        temp_root = Path(temp)
        project = temp_root / "golden"
        shutil.copytree(GOLDEN, project)

        lint = run("lint", "--project", str(project))
        checks["01_golden_contract_lint"] = lint.returncode == 0 and json.loads(lint.stdout).get("passed") is True

        output = temp_root / "run"
        pipeline = run("all", "--project", str(project), "--output", str(output))
        result = load(output / "run-result.json") if (output / "run-result.json").is_file() else {}
        checks["02_real_browser_pipeline"] = pipeline.returncode == 0 and result.get("passed") is True
        checks["03_geometry_and_task_evidence"] = (
            result.get("evidence", {}).get("browser_result", {}).get("current_state") == "LEARNING_REPORT"
            and result.get("evidence", {}).get("browser_result", {}).get("task_passed") is True
            and not result.get("evidence", {}).get("browser_result", {}).get("errors")
        )
        checks["04_visual_baseline_gate"] = result.get("evidence", {}).get("visual_diff", {}).get("status") == "passed"
        checks["05_release_artifacts"] = all((output / name).is_file() for name in ("prototype.html", "prototype.png", "report.md", "run-result.json", "handoff-package.json", "trace.jsonl"))
        html_text = (output / "prototype.html").read_text(encoding="utf-8") if (output / "prototype.html").is_file() else ""
        checks["06_controlled_output_has_no_media"] = not any(token in html_text.lower() for token in ("<img", "<svg", "<video", "<audio", "<canvas"))

        invalid_identity = temp_root / "invalid-identity"
        shutil.copytree(project, invalid_identity)
        identity = load(invalid_identity / "project-identity.json")
        identity["decision"] = "resume"
        identity["source_project_id"] = None
        save(invalid_identity / "project-identity.json", identity)
        failed = run("lint", "--project", str(invalid_identity))
        checks["07_identity_gate_fails_closed"] = failed.returncode != 0 and has_error(failed.stdout, "CONTRACT_INVALID")

        overflow = temp_root / "overflow"
        shutil.copytree(project, overflow)
        frame = load(overflow / "frame-contract.json")
        frame["safe_area"]["right"] = 24
        main_region = next(item for item in frame["regions"] if item["region_id"] == "REG-MAIN")
        main_region["geometry"]["width"] = 980
        save(overflow / "frame-contract.json", frame)
        failed = run("lint", "--project", str(overflow))
        checks["08_layout_overflow_detected"] = failed.returncode != 0 and has_error(failed.stdout, "LAYOUT_OVERFLOW")
        original_width = load(overflow / "frame-contract.json")["regions"][2]["geometry"]["width"]
        repair_output = temp_root / "repair"
        repaired = run("repair", "--project", str(overflow), "--output", str(repair_output))
        repair_result = load(repair_output / "repair-result.json") if (repair_output / "repair-result.json").is_file() else {}
        checks["09_limited_repair_candidate"] = repaired.returncode == 0 and repair_result.get("repair", {}).get("status") == "candidate-passed"
        checks["10_repair_does_not_mutate_source"] = load(overflow / "frame-contract.json")["regions"][2]["geometry"]["width"] == original_width

        asset_violation = temp_root / "asset"
        shutil.copytree(project, asset_violation)
        generation = load(asset_violation / "generation-request.json")
        generation["pages"][0]["components"][0]["src"] = "old-project.png"
        save(asset_violation / "generation-request.json", generation)
        failed = run("lint", "--project", str(asset_violation))
        checks["11_asset_policy_detected"] = failed.returncode != 0 and has_error(failed.stdout, "ASSET_POLICY_VIOLATION")

        broken_flow = temp_root / "flow"
        shutil.copytree(project, broken_flow)
        flow = load(broken_flow / "flow-contract.json")
        flow["transitions"] = [item for item in flow["transitions"] if item["transition_id"] != "TR-009"]
        save(broken_flow / "flow-contract.json", flow)
        failed = run("lint", "--project", str(broken_flow))
        checks["12_unreachable_flow_detected"] = failed.returncode != 0 and has_error(failed.stdout, "FLOW_UNREACHABLE")

        fit_violation = temp_root / "fit"
        shutil.copytree(project, fit_violation)
        fit = load(fit_violation / "template-fit-decision.json")
        fit["selected_template_id"] = "TPL-OLD-PROJECT"
        save(fit_violation / "template-fit-decision.json", fit)
        failed = run("lint", "--project", str(fit_violation))
        checks["13_no_match_cannot_select_old_template"] = failed.returncode != 0 and has_error(failed.stdout, "CONTRACT_INVALID")

        exact_project = temp_root / "exact"
        shutil.copytree(project, exact_project)
        exact_fit = load(exact_project / "template-fit-decision.json")
        exact_fit["result"] = "exact"
        exact_fit["selected_template_id"] = "TPL-NEUTRAL-IMMERSIVE-STAGE-001"
        exact_fit["selected_template_version"] = "v1.0.0"
        exact_fit["next_action"] = "create_project_instance"
        exact_fit["dimensions"] = {key: "matched" for key in exact_fit["dimensions"]}
        save(exact_project / "template-fit-decision.json", exact_fit)
        exact_generation = load(exact_project / "generation-request.json")
        exact_generation["contracts"]["selected_template_instance_id"] = "TINST-001"
        exact_generation["contracts"]["prototype_candidate_id"] = None
        save(exact_project / "generation-request.json", exact_generation)
        exact = run("lint", "--project", str(exact_project))
        checks["14_exact_registered_template_passes"] = exact.returncode == 0 and json.loads(exact.stdout).get("passed") is True

        extensible_project = temp_root / "extensible"
        shutil.copytree(exact_project, extensible_project)
        extensible_fit = load(extensible_project / "template-fit-decision.json")
        extensible_fit["result"] = "extensible"
        extensible_fit["dimensions"]["information_hierarchy"] = "extensible"
        extensible_fit["next_action"] = "create_extended_project_instance"
        save(extensible_project / "template-fit-decision.json", extensible_fit)
        extensible = run("lint", "--project", str(extensible_project))
        checks["15_extensible_registered_template_passes"] = extensible.returncode == 0 and json.loads(extensible.stdout).get("passed") is True

        extensible_fit["dimensions"]["primary_task"] = "mismatched"
        save(extensible_project / "template-fit-decision.json", extensible_fit)
        failed = run("lint", "--project", str(extensible_project))
        checks["16_extensible_mismatch_fails_closed"] = failed.returncode != 0 and has_error(failed.stdout, "CONTRACT_INVALID")

        snapshot_project = temp_root / "snapshot"
        shutil.copytree(project, snapshot_project)
        event = snapshot_project / "event.json"
        save(event, {
            "event_id": "EVT-001",
            "base_revision": 1,
            "source": "user-confirmation",
            "patches": [{"op": "replace", "path": "/product/expected_outcome", "value": "完成复习并看到待加强项"}],
        })
        recorded = run("snapshot", "--project", str(snapshot_project), "--event", str(event))
        checks["17_snapshot_revision_persisted"] = recorded.returncode == 0 and load(snapshot_project / "project-snapshot.json").get("revision") == 2
        checks["18_snapshot_event_log_written"] = (snapshot_project / ".harness" / "events.jsonl").is_file()
        conflict = run("snapshot", "--project", str(snapshot_project), "--event", str(event))
        checks["19_snapshot_conflict_fails_closed"] = conflict.returncode != 0 and has_error(conflict.stdout, "CONTRACT_INVALID")

        handoff = load(output / "handoff-package.json") if (output / "handoff-package.json").is_file() else {}
        checks["20_handoff_separates_user_evidence"] = handoff.get("evidence", {}).get("target_user_validation") == "not-claimed"
        checks["21_handoff_has_semantic_boundaries"] = bool(handoff.get("boundaries", {}).get("semantic_locked")) and bool(handoff.get("boundaries", {}).get("visual_flexible"))
        checks["22_trace_binds_source_hash"] = bool(result.get("source_hash")) and result.get("run_id", "").startswith("HRUN-")
        scenario_results = result.get("evidence", {}).get("browser_result", {}).get("scenarios", [])
        scenario_map = {item.get("scenario_id"): item for item in scenario_results}
        checks["23_timeout_scenario_evidence"] = (
            scenario_map.get("timeout-retry-path", {}).get("passed") is True
            and "GENERATION_TIMEOUT" in scenario_map.get("timeout-retry-path", {}).get("visited_states", [])
            and scenario_map.get("timeout-retry-path", {}).get("current_state") == "LEARNING_REPORT"
        )
        checks["24_all_behavioral_checks_pass"] = all(checks.values())

    summary = {
        "suite": "v4.0-executable-prototype-harness",
        "checks": checks,
        "passed": all(checks.values()),
        "summary": f"{sum(checks.values())}/{len(checks)} checks passed",
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if summary["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
