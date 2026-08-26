#!/usr/bin/env python3
"""Deterministic prototype harness for product-architecture-requirements.

The harness compiles JSON contracts into a controlled HTML prototype and
verifies the rendered artifact in a real Chromium-based browser. It uses only
the Python standard library for core operation; Pillow is optional for visual
diffs.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from urllib.parse import urlencode
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ASSET_ROOT = ROOT / "assets" / "prototype-harness"
REQUIRED_FILES = {
    "identity": "project-identity.json",
    "snapshot": "project-snapshot.json",
    "frame": "frame-contract.json",
    "flow": "flow-contract.json",
    "fit": "template-fit-decision.json",
    "assets": "asset-slot-contract.json",
    "generation": "generation-request.json",
    "expected": "expected.json",
}
ERROR_TYPES = {
    "CONTRACT_MISSING",
    "CONTRACT_INVALID",
    "LAYOUT_OVERFLOW",
    "REGION_OVERLAP",
    "FLOW_UNREACHABLE",
    "STATE_MISSING",
    "PRIMARY_ACTION_INVALID",
    "ASSET_POLICY_VIOLATION",
    "TRACEABILITY_BROKEN",
    "BROWSER_UNAVAILABLE",
    "VISUAL_REGRESSION",
}
STAGES = {
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
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def source_hash(project_dir: Path) -> str:
    digest = hashlib.sha256()
    for filename in REQUIRED_FILES.values():
        path = project_dir / filename
        if path.is_file():
            digest.update(filename.encode())
            digest.update(path.read_bytes())
    expected_path = project_dir / REQUIRED_FILES["expected"]
    if expected_path.is_file():
        try:
            baseline_ref = read_json(expected_path).get("visual_diff", {}).get("baseline")
        except json.JSONDecodeError:
            baseline_ref = None
        if baseline_ref:
            baseline = (project_dir / baseline_ref).resolve()
            try:
                baseline.relative_to(project_dir.resolve())
            except ValueError:
                baseline = Path("__outside_project__")
            if baseline.is_file():
                digest.update(str(baseline_ref).encode())
                digest.update(baseline.read_bytes())
    return digest.hexdigest()


def error(error_type: str, object_ref: str, evidence: str, *, repairable: bool = False,
          repair_policy: str = "none", attempt: int = 0) -> dict[str, Any]:
    if error_type not in ERROR_TYPES:
        raise ValueError(f"unsupported error type: {error_type}")
    return {
        "type": error_type,
        "object_ref": object_ref,
        "evidence": evidence,
        "impact": "blocked",
        "repairable": repairable,
        "repair_policy": repair_policy,
        "attempt": attempt,
    }


def load_project(project_dir: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    contracts: dict[str, Any] = {}
    errors: list[dict[str, Any]] = []
    for key, filename in REQUIRED_FILES.items():
        path = project_dir / filename
        if not path.is_file():
            errors.append(error("CONTRACT_MISSING", filename, "required project contract is absent"))
            continue
        try:
            contracts[key] = read_json(path)
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(error("CONTRACT_INVALID", filename, f"invalid JSON: {exc}"))
    return contracts, errors


def require(mapping: dict[str, Any], fields: list[str], object_ref: str,
            errors: list[dict[str, Any]]) -> None:
    for field in fields:
        if field not in mapping or mapping[field] in (None, "", "pending"):
            errors.append(error("CONTRACT_INVALID", object_ref, f"missing required field: {field}"))


def numeric(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def rectangles_overlap(a: dict[str, Any], b: dict[str, Any]) -> bool:
    return (
        a["x"] < b["x"] + b["width"]
        and a["x"] + a["width"] > b["x"]
        and a["y"] < b["y"] + b["height"]
        and a["y"] + a["height"] > b["y"]
    )


def validate_identity(contracts: dict[str, Any], errors: list[dict[str, Any]]) -> str | None:
    identity = contracts.get("identity", {})
    require(identity, ["decision_id", "decision", "project_id", "profile_id", "status"], "project-identity", errors)
    decision = identity.get("decision")
    if decision not in {"resume", "fork", "new", "needs_confirmation"}:
        errors.append(error("CONTRACT_INVALID", "project-identity.decision", f"unsupported value: {decision}"))
    if identity.get("status") != "ready":
        errors.append(error("CONTRACT_INVALID", "project-identity.status", "identity gate is not ready"))
    source = identity.get("source_project_id")
    if decision == "new" and source:
        errors.append(error("CONTRACT_INVALID", "project-identity.source_project_id", "new project cannot inherit a source project"))
    if decision in {"resume", "fork"} and not source:
        errors.append(error("CONTRACT_INVALID", "project-identity.source_project_id", f"{decision} requires a source project"))
    prohibited = set(identity.get("inheritance", {}).get("prohibited", []))
    required_prohibited = {"copy", "user_data", "visual_assets", "brand_tokens", "business_rules"}
    if decision in {"new", "fork"} and not required_prohibited.issubset(prohibited):
        errors.append(error("CONTRACT_INVALID", "project-identity.inheritance", "project isolation prohibitions are incomplete"))
    return identity.get("project_id")


def validate_snapshot(contracts: dict[str, Any], project_id: str | None,
                      errors: list[dict[str, Any]]) -> None:
    snapshot = contracts.get("snapshot", {})
    require(snapshot, ["project_id", "revision", "current_stage", "delivery_status", "identity_decision_id", "storage"], "project-snapshot", errors)
    if snapshot.get("project_id") != project_id:
        errors.append(error("CONTRACT_INVALID", "project-snapshot.project_id", "does not match identity decision"))
    if snapshot.get("identity_decision_id") != contracts.get("identity", {}).get("decision_id"):
        errors.append(error("TRACEABILITY_BROKEN", "project-snapshot.identity_decision_id", "does not match Project Identity Gate"))
    if snapshot.get("current_stage") not in STAGES or snapshot.get("delivery_status") not in STAGES:
        errors.append(error("CONTRACT_INVALID", "project-snapshot.stage", "stage/status outside controlled vocabulary"))
    if not isinstance(snapshot.get("revision"), int) or snapshot.get("revision", 0) < 1:
        errors.append(error("CONTRACT_INVALID", "project-snapshot.revision", "revision must be a positive integer"))
    storage = snapshot.get("storage", {})
    require(storage, ["snapshot_path", "event_log_path", "run_root"], "project-snapshot.storage", errors)
    product = snapshot.get("product", {})
    require(product, ["target_user", "expected_outcome", "primary_task", "in_scope", "out_of_scope"], "project-snapshot.product", errors)
    for index, chain in enumerate(snapshot.get("traceability", {}).get("must_chains", []), start=1):
        needed = ["target", "decision", "function", "flow_or_transition", "page_or_entry", "acceptance", "test", "artifact"]
        missing = [item for item in needed if not chain.get(item)]
        if missing:
            errors.append(error("TRACEABILITY_BROKEN", f"must-chain-{index}", f"missing {', '.join(missing)}"))
    if not snapshot.get("traceability", {}).get("must_chains"):
        errors.append(error("TRACEABILITY_BROKEN", "project-snapshot.must_chains", "at least one Must chain is required"))
    contract_refs = snapshot.get("contracts", {})
    expected_refs = {
        "frame": contracts.get("frame", {}).get("contract_id"),
        "flow": contracts.get("flow", {}).get("contract_id"),
        "template_fit": contracts.get("fit", {}).get("decision_id"),
        "asset_slots": contracts.get("assets", {}).get("contract_id"),
        "generation_requests": contracts.get("generation", {}).get("request_id"),
    }
    for key, contract_id in expected_refs.items():
        values = contract_refs.get(key, [])
        values = values if isinstance(values, list) else [values]
        if contract_id and contract_id not in values:
            errors.append(error("TRACEABILITY_BROKEN", f"project-snapshot.contracts.{key}", f"missing current contract {contract_id}"))


def validate_frame(contracts: dict[str, Any], project_id: str | None,
                   errors: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    frame = contracts.get("frame", {})
    require(frame, ["contract_id", "project_id", "version", "status", "viewport", "regions", "primary_action_region", "p0_regions"], "frame-contract", errors)
    if frame.get("project_id") != project_id or frame.get("status") != "ready":
        errors.append(error("CONTRACT_INVALID", "frame-contract", "project mismatch or contract is not ready"))
    viewport = frame.get("viewport", {})
    width, height = viewport.get("width"), viewport.get("height")
    if not numeric(width) or not numeric(height) or width <= 0 or height <= 0:
        errors.append(error("CONTRACT_INVALID", "frame-contract.viewport", "width and height must be positive numbers"))
        width, height = 0, 0
    safe = frame.get("safe_area", {"top": 0, "right": 0, "bottom": 0, "left": 0})
    region_map: dict[str, dict[str, Any]] = {}
    for region in frame.get("regions", []):
        region_id = region.get("region_id")
        if not region_id or region_id in region_map:
            errors.append(error("CONTRACT_INVALID", str(region_id), "region id missing or duplicated"))
            continue
        region_map[region_id] = region
        geometry = region.get("geometry", {})
        if not all(numeric(geometry.get(key)) for key in ("x", "y", "width", "height")):
            errors.append(error("CONTRACT_INVALID", region_id, "geometry must contain numeric x/y/width/height"))
            continue
        if geometry["width"] <= 0 or geometry["height"] <= 0:
            errors.append(error("CONTRACT_INVALID", region_id, "region width/height must be positive"))
            continue
        constraints = region.get("constraints", {})
        for dimension, minimum, maximum in (
            ("width", constraints.get("min_width"), constraints.get("max_width")),
            ("height", constraints.get("min_height"), constraints.get("max_height")),
        ):
            if numeric(minimum) and geometry[dimension] < minimum:
                errors.append(error("CONTRACT_INVALID", region_id, f"{dimension} is below declared minimum"))
            if numeric(maximum) and geometry[dimension] > maximum:
                errors.append(error("CONTRACT_INVALID", region_id, f"{dimension} exceeds declared maximum"))
        outside = (
            geometry["x"] < safe.get("left", 0)
            or geometry["y"] < safe.get("top", 0)
            or geometry["x"] + geometry["width"] > width - safe.get("right", 0)
            or geometry["y"] + geometry["height"] > height - safe.get("bottom", 0)
        )
        if outside and region.get("position_mode") != "overlay":
            repair_policy = region.get("repair_policy", "none")
            errors.append(error(
                "LAYOUT_OVERFLOW",
                region_id,
                f"geometry outside safe viewport {width}x{height}",
                repairable=repair_policy == "shrink-to-safe-area",
                repair_policy=repair_policy,
            ))
        if not region.get("traces_to"):
            errors.append(error("TRACEABILITY_BROKEN", region_id, "region has no PUI/page trace"))
    ids = set(region_map)
    if frame.get("primary_action_region") not in ids:
        errors.append(error("PRIMARY_ACTION_INVALID", "frame-contract.primary_action_region", "unknown region"))
    for region_id in frame.get("p0_regions", []):
        if region_id not in ids:
            errors.append(error("STATE_MISSING", region_id, "P0 region not defined"))
    regions = list(region_map.values())
    for index, left in enumerate(regions):
        for right in regions[index + 1:]:
            if left.get("position_mode") == "overlay" or right.get("position_mode") == "overlay":
                continue
            left_allowed = set(left.get("allowed_overlap_with", []))
            right_allowed = set(right.get("allowed_overlap_with", []))
            if right["region_id"] in left_allowed or left["region_id"] in right_allowed:
                continue
            if all(numeric(left.get("geometry", {}).get(key)) and numeric(right.get("geometry", {}).get(key)) for key in ("x", "y", "width", "height")) and rectangles_overlap(left["geometry"], right["geometry"]):
                errors.append(error("REGION_OVERLAP", f"{left['region_id']}/{right['region_id']}", "non-overlay regions overlap"))
    return region_map


def validate_flow(contracts: dict[str, Any], project_id: str | None,
                  errors: list[dict[str, Any]]) -> set[str]:
    flow = contracts.get("flow", {})
    require(flow, ["contract_id", "project_id", "version", "status", "initial_state", "terminal_states", "states", "transitions", "async_policy", "resume"], "flow-contract", errors)
    if flow.get("project_id") != project_id or flow.get("status") != "ready":
        errors.append(error("CONTRACT_INVALID", "flow-contract", "project mismatch or contract is not ready"))
    states = {item.get("state_id"): item for item in flow.get("states", []) if item.get("state_id")}
    initial = flow.get("initial_state")
    terminals = set(flow.get("terminal_states", []))
    if initial not in states:
        errors.append(error("STATE_MISSING", str(initial), "initial state not defined"))
    if not terminals or not terminals.issubset(states):
        errors.append(error("STATE_MISSING", "terminal_states", "terminal states missing or undefined"))
    graph: dict[str, set[str]] = {state_id: set() for state_id in states}
    outgoing: dict[str, list[dict[str, Any]]] = {state_id: [] for state_id in states}
    for transition in flow.get("transitions", []):
        require(transition, ["transition_id", "from", "event", "trigger", "to", "traces_to"], "flow-transition", errors)
        source, target = transition.get("from"), transition.get("to")
        if source not in states or target not in states:
            errors.append(error("STATE_MISSING", transition.get("transition_id", "transition"), f"undefined state {source}->{target}"))
            continue
        graph[source].add(target)
        outgoing[source].append(transition)
        if not transition.get("traces_to"):
            errors.append(error("TRACEABILITY_BROKEN", transition.get("transition_id", "transition"), "transition trace is empty"))
    reachable: set[str] = set()
    pending = [initial] if initial in states else []
    while pending:
        state_id = pending.pop()
        if state_id in reachable:
            continue
        reachable.add(state_id)
        pending.extend(graph.get(state_id, set()) - reachable)
    for state_id in set(states) - reachable:
        errors.append(error("FLOW_UNREACHABLE", state_id, "state is unreachable from initial state"))
    for state_id, state in states.items():
        if state_id not in terminals and not outgoing.get(state_id):
            errors.append(error("FLOW_UNREACHABLE", state_id, "non-terminal state has no exit"))
        if not state.get("traces_to"):
            errors.append(error("TRACEABILITY_BROKEN", state_id, "state trace is empty"))
        if state.get("type") == "async":
            triggers = {item.get("trigger") for item in outgoing.get(state_id, [])}
            if "timeout" not in triggers or not ({"auto", "action"} & triggers):
                errors.append(error("STATE_MISSING", state_id, "async state requires success and timeout transitions"))
    policy = flow.get("async_policy", {})
    if policy.get("max_retries", 99) > 2:
        errors.append(error("CONTRACT_INVALID", "flow-contract.async_policy", "max_retries cannot exceed 2"))
    resume = flow.get("resume", {})
    if resume.get("persistence") not in {"state-and-step", "state", "not_applicable"}:
        errors.append(error("CONTRACT_INVALID", "flow-contract.resume", "resume persistence must be explicit"))
    if resume.get("fallback_state") not in states:
        errors.append(error("STATE_MISSING", "flow-contract.resume.fallback_state", "fallback state is undefined"))
    return set(states)


def validate_fit_and_assets(contracts: dict[str, Any], project_id: str | None,
                            errors: list[dict[str, Any]]) -> set[str]:
    fit = contracts.get("fit", {})
    require(fit, ["decision_id", "project_id", "profile_id", "status", "result", "next_action"], "template-fit-decision", errors)
    if fit.get("project_id") != project_id or fit.get("status") != "ready":
        errors.append(error("CONTRACT_INVALID", "template-fit-decision", "project mismatch or fit decision is not ready"))
    result = fit.get("result")
    if result not in {"exact", "extensible", "no_match"}:
        errors.append(error("CONTRACT_INVALID", "template-fit-decision.result", f"unsupported result: {result}"))
    registry = read_json(ASSET_ROOT / "templates" / "registry.json")
    registered_templates = [item for item in registry.get("templates", []) if item.get("status") == "registered"]
    template_fields = {"template_id", "version", "scope", "target_users", "primary_tasks", "page_types", "device_profiles", "required_regions", "information_hierarchy", "extension_points", "supported_states"}
    for template in registered_templates:
        missing = [field for field in template_fields if not template.get(field)]
        if missing:
            errors.append(error("CONTRACT_INVALID", template.get("template_id", "template-registry"), f"registered template missing {', '.join(sorted(missing))}"))
        if template.get("business_content_embedded") is not False or template.get("visual_assets_embedded") is not False:
            errors.append(error("ASSET_POLICY_VIOLATION", template.get("template_id", "template-registry"), "registered neutral template embeds business content or visual assets"))
    registered = {item["template_id"] for item in registered_templates}
    selected = fit.get("selected_template_id")
    dimensions = fit.get("dimensions")
    if not dimensions and fit.get("candidates"):
        dimensions = fit["candidates"][0].get("dimensions")
    required_dimensions = {
        "target_users",
        "primary_task",
        "page_type",
        "information_hierarchy",
        "required_regions",
        "device_viewport",
        "interaction_states",
    }
    if not isinstance(dimensions, dict) or not required_dimensions.issubset(dimensions):
        errors.append(error("CONTRACT_INVALID", "template-fit-decision.dimensions", "all seven fit dimensions are required"))
    else:
        invalid_values = {key: value for key, value in dimensions.items() if key in required_dimensions and value not in {"matched", "extensible", "mismatched", "unknown"}}
        if invalid_values:
            errors.append(error("CONTRACT_INVALID", "template-fit-decision.dimensions", f"invalid dimension values: {invalid_values}"))
        if result == "exact" and any(dimensions[key] != "matched" for key in required_dimensions):
            errors.append(error("CONTRACT_INVALID", "template-fit-decision.result", "exact requires seven matched dimensions"))
        if result == "extensible" and any(dimensions[key] not in {"matched", "extensible"} for key in required_dimensions):
            errors.append(error("CONTRACT_INVALID", "template-fit-decision.result", "extensible cannot contain mismatched or unknown dimensions"))
    if result in {"exact", "extensible"} and selected not in registered:
        errors.append(error("CONTRACT_INVALID", "template-fit-decision.selected_template_id", "selected template is not registered"))
    if result == "no_match" and selected:
        errors.append(error("CONTRACT_INVALID", "template-fit-decision.selected_template_id", "no_match cannot select a shared template"))

    asset_contract = contracts.get("assets", {})
    require(asset_contract, ["contract_id", "project_id", "status", "slots", "inheritance"], "asset-slot-contract", errors)
    if asset_contract.get("project_id") != project_id or asset_contract.get("status") != "ready":
        errors.append(error("CONTRACT_INVALID", "asset-slot-contract", "project mismatch or asset contract is not ready"))
    inheritance = asset_contract.get("inheritance", {})
    if inheritance.get("allow_source_assets") or inheritance.get("allow_historical_fallback"):
        errors.append(error("ASSET_POLICY_VIOLATION", "asset-slot-contract.inheritance", "historical/source assets are not allowed in neutral prototype"))
    slots: set[str] = set()
    for slot in asset_contract.get("slots", []):
        slot_id = slot.get("slot_id")
        if not slot_id:
            errors.append(error("CONTRACT_INVALID", "asset-slot", "slot id missing"))
            continue
        slots.add(slot_id)
        if slot.get("source_asset_ids"):
            errors.append(error("ASSET_POLICY_VIOLATION", slot_id, "source assets must be empty for neutral prototype"))
        placeholder = slot.get("placeholder", {})
        if placeholder.get("style") != "neutral-outline":
            errors.append(error("ASSET_POLICY_VIOLATION", slot_id, "placeholder style must be neutral-outline"))
    return slots


def validate_generation(contracts: dict[str, Any], project_id: str | None,
                        region_map: dict[str, dict[str, Any]], flow_states: set[str],
                        asset_slots: set[str], errors: list[dict[str, Any]]) -> None:
    request = contracts.get("generation", {})
    require(request, ["request_id", "project_id", "status", "rendering", "contracts", "pages", "boundaries"], "generation-request", errors)
    if request.get("project_id") != project_id or request.get("status") != "ready-to-generate":
        errors.append(error("CONTRACT_INVALID", "generation-request", "project mismatch or request is not ready"))
    rendering = request.get("rendering", {})
    if rendering.get("mode") != "controlled" or rendering.get("arbitrary_components_allowed") is not False or rendering.get("arbitrary_html_allowed") is not False:
        errors.append(error("CONTRACT_INVALID", "generation-request.rendering", "rendering must be controlled and arbitrary HTML/components disabled"))
    registry = read_json(ASSET_ROOT / "templates" / "registry.json")
    whitelist = set(registry.get("component_whitelist", []))
    seen_states: set[str] = set()
    flow = contracts.get("flow", {})
    action_transitions = {(item.get("from"), item.get("event")) for item in flow.get("transitions", []) if item.get("trigger") == "action"}
    primary_region = contracts.get("frame", {}).get("primary_action_region")
    p0_regions = set(contracts.get("frame", {}).get("p0_regions", []))
    for page in request.get("pages", []):
        state_id = page.get("state_id")
        page_id = page.get("page_id")
        if state_id not in flow_states:
            errors.append(error("STATE_MISSING", str(state_id), "render page state is not in Flow Contract"))
        seen_states.add(state_id)
        primary = 0
        p0 = 0
        for component in page.get("components", []):
            component_id = component.get("component_id", "component")
            component_type = component.get("type")
            if component_type not in whitelist:
                errors.append(error("CONTRACT_INVALID", component_id, f"component type not allowed: {component_type}"))
            if component.get("region_id") not in region_map:
                errors.append(error("CONTRACT_INVALID", component_id, "component targets an unknown region"))
            if component.get("priority") == "P0":
                p0 += 1
                if component.get("region_id") not in p0_regions:
                    errors.append(error("TRACEABILITY_BROKEN", component_id, "P0 component is outside declared P0 regions"))
                if not component.get("traces_to"):
                    errors.append(error("TRACEABILITY_BROKEN", component_id, "P0 component has no trace"))
            if component_type == "action" and component.get("level") == "primary":
                primary += 1
                if component.get("region_id") != primary_region:
                    errors.append(error("PRIMARY_ACTION_INVALID", component_id, "primary action is outside primary_action_region"))
            if component_type == "action" and (state_id, component.get("action_id")) not in action_transitions:
                errors.append(error("FLOW_UNREACHABLE", component_id, "rendered action has no Flow transition from this state"))
            if component_type == "asset-slot" and component.get("slot_id") not in asset_slots:
                errors.append(error("ASSET_POLICY_VIOLATION", component_id, "asset slot is not declared"))
            if any(key in component for key in ("html", "css", "src", "background_image")):
                errors.append(error("ASSET_POLICY_VIOLATION", component_id, "raw HTML/CSS/source assets are forbidden"))
        if primary != 1:
            errors.append(error("PRIMARY_ACTION_INVALID", page_id or str(state_id), f"expected 1 primary action, found {primary}"))
        if p0 == 0:
            errors.append(error("STATE_MISSING", page_id or str(state_id), "page has no P0 component"))
    for state_id in flow_states - seen_states:
        errors.append(error("STATE_MISSING", state_id, "Flow state has no rendered page"))

    fit = contracts.get("fit", {})
    linked = request.get("contracts", {})
    if linked.get("fit_decision_id") != fit.get("decision_id"):
        errors.append(error("TRACEABILITY_BROKEN", "generation-request.fit_decision_id", "does not match TFD"))
    if linked.get("frame_contract_id") != contracts.get("frame", {}).get("contract_id"):
        errors.append(error("TRACEABILITY_BROKEN", "generation-request.frame_contract_id", "does not match Frame Contract"))
    if linked.get("flow_contract_id") != contracts.get("flow", {}).get("contract_id"):
        errors.append(error("TRACEABILITY_BROKEN", "generation-request.flow_contract_id", "does not match Flow Contract"))
    if contracts.get("assets", {}).get("contract_id") not in linked.get("asset_slot_contracts", []):
        errors.append(error("TRACEABILITY_BROKEN", "generation-request.asset_slot_contracts", "does not include current Asset Slot Contract"))
    if fit.get("result") == "no_match" and not linked.get("prototype_candidate_id"):
        errors.append(error("CONTRACT_INVALID", "generation-request.prototype_candidate_id", "no_match requires a project-local candidate"))
    if fit.get("result") in {"exact", "extensible"} and not linked.get("selected_template_instance_id"):
        errors.append(error("CONTRACT_INVALID", "generation-request.selected_template_instance_id", "template match requires a project instance"))
    if fit.get("result") == "no_match" and linked.get("selected_template_instance_id"):
        errors.append(error("CONTRACT_INVALID", "generation-request.selected_template_instance_id", "no_match cannot use a shared template instance"))


def validate_expected(contracts: dict[str, Any], errors: list[dict[str, Any]]) -> None:
    expected = contracts.get("expected", {})
    scenarios = expected.get("scenarios", [])
    required_fields = ["viewport", "terminal_state", "visual_diff"]
    if "scenarios" in expected:
        required_fields.append("scenarios")
    else:
        required_fields.append("action_sequence")
    require(expected, required_fields, "expected", errors)
    flow = contracts.get("flow", {})
    viewport = expected.get("viewport", {})
    frame_viewport = contracts.get("frame", {}).get("viewport", {})
    if viewport.get("width") != frame_viewport.get("width") or viewport.get("height") != frame_viewport.get("height"):
        errors.append(error("CONTRACT_INVALID", "expected.viewport", "does not match Frame Contract viewport"))
    actions = {item.get("event") for item in flow.get("transitions", []) if item.get("trigger") == "action"}
    flow_states = {item.get("state_id") for item in flow.get("states", [])}
    terminals = set(flow.get("terminal_states", []))

    def validate_scenario(scenario: dict[str, Any], label: str) -> None:
        require(scenario, ["scenario_id", "action_sequence", "terminal_state"], label, errors)
        for action_id in scenario.get("action_sequence", []):
            if action_id not in actions:
                errors.append(error("FLOW_UNREACHABLE", f"{label}:{action_id}", "expected action has no action transition"))
        if scenario.get("terminal_state") not in terminals:
            errors.append(error("FLOW_UNREACHABLE", f"{label}:{scenario.get('terminal_state')}", "expected terminal is not a Flow terminal"))
        for state_id in scenario.get("required_states", []):
            if state_id not in flow_states:
                errors.append(error("STATE_MISSING", f"{label}:{state_id}", "required state is not in Flow Contract"))
        async_states = {item.get("state_id") for item in flow.get("states", []) if item.get("type") == "async"}
        for state_id in [*scenario.get("suppress_auto_from", []), *scenario.get("suppress_auto_once_from", [])]:
            if state_id not in async_states:
                errors.append(error("STATE_MISSING", f"{label}:{state_id}", "auto suppression must target an async state"))
        timeout_delay = scenario.get("timeout_delay_ms")
        if timeout_delay is not None and (not numeric(timeout_delay) or timeout_delay <= 0):
            errors.append(error("CONTRACT_INVALID", label, "timeout_delay_ms must be a positive number"))

    if "scenarios" in expected:
        if not isinstance(scenarios, list) or not scenarios:
            errors.append(error("CONTRACT_INVALID", "expected.scenarios", "scenarios must be a non-empty list"))
        else:
            seen_ids: set[str] = set()
            for index, scenario in enumerate(scenarios, start=1):
                if not isinstance(scenario, dict):
                    errors.append(error("CONTRACT_INVALID", f"expected.scenarios[{index}]", "scenario must be an object"))
                    continue
                scenario_id = scenario.get("scenario_id")
                if scenario_id in seen_ids:
                    errors.append(error("CONTRACT_INVALID", f"expected.scenarios[{index}]", "scenario_id must be unique"))
                if scenario_id:
                    seen_ids.add(scenario_id)
                validate_scenario(scenario, f"expected.scenarios[{index}]")
    else:
        validate_scenario(expected, "expected")


def validate_project(project_dir: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    contracts, errors = load_project(project_dir)
    if errors:
        return contracts, errors
    project_id = validate_identity(contracts, errors)
    validate_snapshot(contracts, project_id, errors)
    region_map = validate_frame(contracts, project_id, errors)
    flow_states = validate_flow(contracts, project_id, errors)
    asset_slots = validate_fit_and_assets(contracts, project_id, errors)
    validate_generation(contracts, project_id, region_map, flow_states, asset_slots, errors)
    validate_expected(contracts, errors)
    return contracts, errors


def json_pointer_set(document: dict[str, Any], pointer: str, value: Any) -> None:
    if not pointer.startswith("/"):
        raise ValueError("patch path must be an absolute JSON pointer")
    parts = [item.replace("~1", "/").replace("~0", "~") for item in pointer.lstrip("/").split("/")]
    if not parts or parts[0] not in {"product", "governance", "conversation", "architecture", "prototype", "contracts", "harness", "delivery"}:
        raise ValueError(f"patch root is not allowed: {pointer}")
    current: Any = document
    for part in parts[:-1]:
        if not isinstance(current, dict):
            raise ValueError(f"patch path does not resolve to an object: {pointer}")
        current = current.setdefault(part, {})
    if not isinstance(current, dict):
        raise ValueError(f"patch parent is not an object: {pointer}")
    current[parts[-1]] = value


def record_snapshot_event(project_dir: Path, event_path: Path) -> dict[str, Any]:
    snapshot_path = project_dir / REQUIRED_FILES["snapshot"]
    if not snapshot_path.is_file():
        return {"passed": False, "errors": [error("CONTRACT_MISSING", str(snapshot_path), "snapshot is absent")]}
    try:
        snapshot = read_json(snapshot_path)
        event_data = read_json(event_path)
    except (OSError, json.JSONDecodeError) as exc:
        return {"passed": False, "errors": [error("CONTRACT_INVALID", "snapshot-event", str(exc))]}
    require_fields = ["event_id", "base_revision", "source", "patches"]
    missing = [field for field in require_fields if event_data.get(field) in (None, "", [])]
    if missing:
        return {"passed": False, "errors": [error("CONTRACT_INVALID", "snapshot-event", f"missing {', '.join(missing)}")]}
    if event_data["base_revision"] != snapshot.get("revision"):
        return {"passed": False, "errors": [error("CONTRACT_INVALID", event_data["event_id"], f"revision conflict: expected {snapshot.get('revision')}, received {event_data['base_revision']}")]}
    updated = json.loads(json.dumps(snapshot))
    try:
        for patch in event_data["patches"]:
            if patch.get("op") not in {"add", "replace"}:
                raise ValueError(f"unsupported operation: {patch.get('op')}")
            json_pointer_set(updated, patch.get("path", ""), patch.get("value"))
    except ValueError as exc:
        return {"passed": False, "errors": [error("CONTRACT_INVALID", event_data["event_id"], str(exc))]}
    updated["revision"] = snapshot["revision"] + 1
    updated["persisted_at"] = utc_now()
    updated["source_hash"] = hashlib.sha256(json.dumps(event_data, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    event_log_ref = updated.get("storage", {}).get("event_log_path")
    if not event_log_ref:
        return {"passed": False, "errors": [error("CONTRACT_INVALID", "project-snapshot.storage", "event_log_path is missing")]}
    event_log = (project_dir / event_log_ref).resolve()
    try:
        event_log.relative_to(project_dir.resolve())
    except ValueError:
        return {"passed": False, "errors": [error("CONTRACT_INVALID", "project-snapshot.storage", "event log must stay inside project directory")]}
    temporary = snapshot_path.with_suffix(".json.tmp")
    write_json(temporary, updated)
    temporary.replace(snapshot_path)
    event_log.parent.mkdir(parents=True, exist_ok=True)
    event_record = {**event_data, "applied_revision": updated["revision"], "applied_at": updated["persisted_at"]}
    with event_log.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event_record, ensure_ascii=False) + "\n")
    return {
        "passed": True,
        "event_id": event_data["event_id"],
        "project_id": updated.get("project_id"),
        "previous_revision": snapshot["revision"],
        "revision": updated["revision"],
        "snapshot": str(snapshot_path),
        "event_log": str(event_log),
    }


def attrs(component: dict[str, Any], *extra_classes: str) -> str:
    priority = html.escape(str(component.get("priority", "P1")))
    component_id = html.escape(str(component.get("component_id", "component")))
    classes = " ".join((f"priority-{priority.lower()}", *extra_classes))
    return f'data-component-id="{component_id}" data-priority="{priority}" class="{classes}"'


def render_component(component: dict[str, Any]) -> str:
    kind = component.get("type")
    label = html.escape(str(component.get("label", component.get("text", ""))))
    common = attrs(component)
    if kind == "heading":
        level = min(3, max(1, int(component.get("level", 2))))
        return f"<h{level} {common}>{label}</h{level}>"
    if kind == "text":
        return f"<p {common}>{label}</p>"
    if kind == "meta":
        items = "".join(f"<span>{html.escape(str(item))}</span>" for item in component.get("items", []))
        return f'<div {common}><div class="prototype-meta">{items}</div></div>'
    if kind == "status":
        return f'<div {common}><div class="prototype-status">{label}</div></div>'
    if kind == "progress":
        value = max(0, min(100, int(component.get("value", 0))))
        return (
            f'<div {common}><div class="prototype-progress"><span>{label}</span>'
            f'<div class="prototype-progress-track"><div class="prototype-progress-value" style="width:{value}%"></div></div></div></div>'
        )
    if kind in {"step-list", "card-list"}:
        class_name = "prototype-list" if kind == "step-list" else "prototype-card-list"
        item_class = "prototype-list-item" if kind == "step-list" else "prototype-card"
        items = "".join(f'<li class="{item_class}">{html.escape(str(item))}</li>' for item in component.get("items", []))
        return f'<div {common}><ul class="{class_name}">{items}</ul></div>'
    if kind == "asset-slot":
        slot_id = html.escape(str(component.get("slot_id", "slot")))
        ratio = html.escape(str(component.get("ratio", "unspecified")))
        return f'<div {common}><div class="prototype-asset-slot" data-slot-id="{slot_id}">{label}<br><small>{ratio} · 原型占位</small></div></div>'
    if kind == "input":
        input_id = html.escape(str(component.get("component_id", "input")))
        placeholder = html.escape(str(component.get("placeholder", "")))
        return f'<label {attrs(component, "prototype-input")} for="{input_id}"><span>{label}</span><input id="{input_id}" placeholder="{placeholder}"></label>'
    if kind == "action":
        action_id = html.escape(str(component.get("action_id", "")))
        level = html.escape(str(component.get("level", "secondary")))
        return f'<div {attrs(component, "prototype-action-row")}><button class="prototype-action" data-action-id="{action_id}" data-level="{level}">{label}</button></div>'
    raise ValueError(f"unsupported component type: {kind}")


def render_html(contracts: dict[str, Any]) -> str:
    frame = contracts["frame"]
    request = contracts["generation"]
    regions = {item["region_id"]: item for item in frame["regions"]}
    screens: list[str] = []
    for page in request["pages"]:
        by_region: dict[str, list[dict[str, Any]]] = {region_id: [] for region_id in regions}
        for component in page.get("components", []):
            by_region[component["region_id"]].append(component)
        rendered_regions: list[str] = []
        for region_id, region in regions.items():
            geometry = region["geometry"]
            style = (
                f"left:{geometry['x']}px;top:{geometry['y']}px;width:{geometry['width']}px;"
                f"height:{geometry['height']}px;z-index:{int(region.get('z_index', 1))};"
            )
            components = "".join(render_component(item) for item in by_region[region_id])
            allowed = html.escape(",".join(region.get("allowed_overlap_with", [])))
            rendered_regions.append(
                f'<section class="prototype-region" data-region-id="{html.escape(region_id)}" '
                f'data-position-mode="{html.escape(region.get("position_mode", "flow"))}" '
                f'data-allowed-overlap="{allowed}" style="{style}"><div class="region-content">{components}</div></section>'
            )
        state_id = html.escape(str(page["state_id"]))
        page_id = html.escape(str(page["page_id"]))
        screens.append(f'<article class="prototype-screen" data-state-id="{state_id}" data-page-id="{page_id}" hidden>{"".join(rendered_regions)}</article>')
    shell = (ASSET_ROOT / "shell.html").read_text(encoding="utf-8")
    replacements = {
        "__TITLE__": html.escape(str(request.get("title", "Prototype Harness"))),
        "__PROJECT_ID__": html.escape(str(request["project_id"])),
        "__RUNTIME_CSS__": (ASSET_ROOT / "runtime.css").read_text(encoding="utf-8"),
        "__SCREENS__": "".join(screens),
        "__FLOW_JSON__": json.dumps(contracts["flow"], ensure_ascii=False).replace("</", "<\\/"),
        "__EXPECTED_JSON__": json.dumps(contracts["expected"], ensure_ascii=False).replace("</", "<\\/"),
        "__RUNTIME_JS__": (ASSET_ROOT / "runtime.js").read_text(encoding="utf-8"),
    }
    for key, value in replacements.items():
        shell = shell.replace(key, value)
    return shell


def find_chrome() -> Path | None:
    playwright_shells = sorted(
        (Path.home() / "Library" / "Caches" / "ms-playwright").glob(
            "chromium_headless_shell-*/chrome-headless-shell-*/chrome-headless-shell"
        ),
        reverse=True,
    )
    candidates = [
        os.environ.get("HARNESS_CHROME"),
        *(str(path) for path in playwright_shells),
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
        "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
        shutil.which("google-chrome"),
        shutil.which("chromium"),
        shutil.which("chromium-browser"),
    ]
    for candidate in candidates:
        if candidate and Path(candidate).is_file():
            return Path(candidate)
    return None


def browser_test(html_path: Path, output_dir: Path, expected: dict[str, Any]) -> tuple[dict[str, Any] | None, list[dict[str, Any]], Path | None]:
    chrome = find_chrome()
    if not chrome:
        return None, [error("BROWSER_UNAVAILABLE", "chrome", "set HARNESS_CHROME or install a Chromium browser")], None
    viewport = expected.get("viewport", {})
    width, height = int(viewport.get("width", 1280)), int(viewport.get("height", 800))
    common = [
        str(chrome), "--headless" if chrome.name == "chrome-headless-shell" else "--headless=new", "--disable-gpu", "--hide-scrollbars", "--no-sandbox",
        "--no-first-run", "--no-default-browser-check", "--disable-background-networking",
        "--force-device-scale-factor=1", f"--window-size={width},{height}", "--virtual-time-budget=5000",
    ]
    scenarios = expected.get("scenarios") or [{
        "scenario_id": "default",
        "action_sequence": expected.get("action_sequence", []),
        "terminal_state": expected.get("terminal_state"),
        "required_states": expected.get("required_states", []),
    }]
    scenario_results: list[dict[str, Any]] = []
    all_errors: list[dict[str, Any]] = []
    for scenario in scenarios:
        query = urlencode({"harness_auto": "1", "harness_scenario": scenario.get("scenario_id", "default")})
        url = html_path.resolve().as_uri() + f"?{query}"
        with tempfile.TemporaryDirectory(prefix="harness-chrome-", dir=output_dir) as profile:
            command = common + [f"--user-data-dir={profile}", "--dump-dom", url]
            try:
                completed = subprocess.run(command, capture_output=True, text=True, timeout=30, check=False)
            except subprocess.TimeoutExpired:
                return None, [error("BROWSER_UNAVAILABLE", str(chrome), f"scenario {scenario.get('scenario_id')} timed out after 30 seconds")], None
        if completed.returncode != 0:
            return None, [error("BROWSER_UNAVAILABLE", "chrome", completed.stderr.strip() or f"exit {completed.returncode}")], None
        match = re.search(r'<script id="harness-result" type="application/json">(.*?)</script>', completed.stdout, re.DOTALL)
        if not match:
            return None, [error("CONTRACT_INVALID", "harness-result", f"scenario {scenario.get('scenario_id')} returned no runtime evidence")], None
        try:
            scenario_result = json.loads(html.unescape(match.group(1)))
        except json.JSONDecodeError as exc:
            return None, [error("CONTRACT_INVALID", "harness-result", f"invalid runtime evidence: {exc}")], None
        scenario_result["scenario_id"] = scenario.get("scenario_id", "default")
        scenario_errors = [error(item["type"], item.get("object_ref", "browser"), item.get("evidence", "browser failure")) for item in scenario_result.get("errors", [])]
        scenario_result["errors"] = [dict(item) for item in scenario_result.get("errors", [])]
        scenario_result["passed"] = bool(scenario_result.get("passed")) and not scenario_errors
        scenario_results.append(scenario_result)
        all_errors.extend(scenario_errors)

    primary_scenario = expected.get("screenshot_scenario") or scenarios[0].get("scenario_id", "default")
    screenshot_state = expected.get("screenshot_state", expected.get("terminal_state", ""))
    for scenario in scenarios:
        if scenario.get("scenario_id", "default") == primary_scenario:
            screenshot_state = scenario.get("screenshot_state", screenshot_state)
            break
    screenshot_url = html_path.resolve().as_uri() + "?" + urlencode({"harness_state": screenshot_state})
    screenshot_path = output_dir / "prototype.png"
    with tempfile.TemporaryDirectory(prefix="harness-shot-", dir=output_dir) as profile:
        command = common + [f"--user-data-dir={profile}", f"--screenshot={screenshot_path}", screenshot_url]
        try:
            completed = subprocess.run(command, capture_output=True, text=True, timeout=30, check=False)
        except subprocess.TimeoutExpired:
            return None, all_errors + [error("BROWSER_UNAVAILABLE", str(chrome), "browser screenshot timed out after 30 seconds")], None
    if completed.returncode != 0 or not screenshot_path.is_file():
        all_errors.append(error("BROWSER_UNAVAILABLE", "screenshot", completed.stderr.strip() or "screenshot missing"))
        screenshot_path = None
    visited: list[str] = []
    for scenario_result in scenario_results:
        for state_id in scenario_result.get("visited_states", []):
            if state_id not in visited:
                visited.append(state_id)
    aggregate = {
        "browser": all(item.get("browser") is True for item in scenario_results),
        "viewport": {"width": width, "height": height},
        "current_state": scenario_results[-1].get("current_state") if scenario_results else None,
        "visited_states": visited,
        "task_passed": all(item.get("task_passed") is True for item in scenario_results),
        "errors": [dict(item) for item in all_errors],
        "passed": bool(scenario_results) and all(item.get("passed") is True for item in scenario_results) and not all_errors,
        "scenarios": scenario_results,
    }
    return aggregate, all_errors, screenshot_path


def visual_diff(screenshot: Path | None, project_dir: Path, expected: dict[str, Any],
                update_baseline: bool) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    config = expected.get("visual_diff", {})
    required = bool(config.get("required", False))
    baseline = project_dir / config.get("baseline", "baseline.png")
    if screenshot is None:
        return {"required": required, "status": "missing-screenshot"}, []
    if update_baseline:
        shutil.copy2(screenshot, baseline)
        return {"required": required, "status": "baseline-updated", "baseline": str(baseline)}, []
    if not baseline.is_file():
        failures = [error("VISUAL_REGRESSION", str(baseline), "required visual baseline is missing")] if required else []
        return {"required": required, "status": "baseline-missing", "baseline": str(baseline)}, failures
    try:
        from PIL import Image, ImageChops, ImageStat  # type: ignore
    except ImportError:
        identical = screenshot.read_bytes() == baseline.read_bytes()
        result = {
            "required": required,
            "status": "passed" if identical else "failed",
            "method": "exact-png-fallback",
            "baseline": str(baseline),
        }
        failures = [] if identical else [error("VISUAL_REGRESSION", str(baseline), "PNG bytes differ and Pillow is unavailable")]
        return result, failures
    with Image.open(screenshot).convert("RGB") as actual, Image.open(baseline).convert("RGB") as reference:
        if actual.size != reference.size:
            return {"required": required, "status": "size-mismatch", "actual": actual.size, "baseline": reference.size}, [error("VISUAL_REGRESSION", str(baseline), "screenshot size differs from baseline")]
        diff = ImageChops.difference(actual, reference)
        mean = sum(ImageStat.Stat(diff).mean) / 3 / 255
        histogram = diff.convert("L").histogram()
        changed = sum(histogram[1:]) / (actual.width * actual.height)
    max_mean = float(config.get("max_mean_difference", 0.01))
    max_changed = float(config.get("max_changed_ratio", 0.02))
    passed = mean <= max_mean and changed <= max_changed
    result = {
        "required": required,
        "status": "passed" if passed else "failed",
        "mean_difference": round(mean, 6),
        "changed_ratio": round(changed, 6),
        "thresholds": {"max_mean_difference": max_mean, "max_changed_ratio": max_changed},
        "baseline": str(baseline),
    }
    failures = [] if passed else [error("VISUAL_REGRESSION", str(baseline), f"mean={mean:.6f}, changed={changed:.6f}")]
    return result, failures


def append_trace(output_dir: Path, event_name: str, data: dict[str, Any]) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    record = {"at": utc_now(), "event": event_name, **data}
    with (output_dir / "trace.jsonl").open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def write_report(result: dict[str, Any], output_dir: Path, project_dir: Path) -> None:
    write_json(output_dir / "run-result.json", result)
    status = "PASSED" if result["passed"] else "BLOCKED"
    lines = [
        f"# Prototype Harness Report — {status}",
        "",
        f"- Run: `{result['run_id']}`",
        f"- Project: `{result.get('project_id')}`",
        f"- Source hash: `{result['source_hash']}`",
        f"- Contract lint: `{result['evidence']['contract_lint']}`",
        f"- Browser geometry/task: `{result['evidence']['browser']}`",
        f"- Visual diff: `{result['evidence']['visual_diff'].get('status')}`",
        "",
        "## Errors",
        "",
    ]
    if result["errors"]:
        lines.extend(f"- `{item['type']}` · `{item['object_ref']}` · {item['evidence']}" for item in result["errors"])
    else:
        lines.append("- None")
    (output_dir / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    package = {
        "package_id": f"HPKG-{result['source_hash'][:8].upper()}",
        "project_id": result.get("project_id"),
        "snapshot_revision": result.get("snapshot_revision"),
        "run_id": result["run_id"],
        "release_status": "passed" if result["passed"] else "blocked",
        "artifacts": {
            "frame_contracts": [str(project_dir / REQUIRED_FILES["frame"])],
            "flow_contracts": [str(project_dir / REQUIRED_FILES["flow"])],
            "asset_slot_contracts": [str(project_dir / REQUIRED_FILES["assets"])],
            "prototype_files": [str(output_dir / "prototype.html"), str(output_dir / "prototype.png")],
            "validation_report": str(output_dir / "report.md"),
        },
        "evidence": result["evidence"],
        "boundaries": result.get("boundaries", {}),
    }
    write_json(output_dir / "handoff-package.json", package)


def run_pipeline(project_dir: Path, output_dir: Path, *, update_baseline: bool = False,
                 attempt: int = 0) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    digest = source_hash(project_dir)
    run_id = f"HRUN-{digest[:12].upper()}"
    append_trace(output_dir, "run-start", {"run_id": run_id, "attempt": attempt, "project": str(project_dir)})
    contracts, errors = validate_project(project_dir)
    lint_errors = list(errors)
    append_trace(output_dir, "lint-complete", {"error_count": len(errors)})
    html_path: Path | None = None
    runtime_result = None
    screenshot = None
    visual_result: dict[str, Any] = {"required": False, "status": "not-run"}
    if not errors:
        html_path = output_dir / "prototype.html"
        html_path.write_text(render_html(contracts), encoding="utf-8")
        append_trace(output_dir, "render-complete", {"artifact": str(html_path)})
        runtime_result, browser_errors, screenshot = browser_test(html_path, output_dir, contracts["expected"])
        errors.extend(browser_errors)
        append_trace(output_dir, "browser-test-complete", {"error_count": len(browser_errors), "screenshot": str(screenshot) if screenshot else None})
        visual_result, visual_errors = visual_diff(screenshot, project_dir, contracts["expected"], update_baseline)
        errors.extend(visual_errors)
        append_trace(output_dir, "visual-diff-complete", {"result": visual_result})
    project_id = contracts.get("identity", {}).get("project_id") if contracts else None
    snapshot = contracts.get("snapshot", {}) if contracts else {}
    boundaries = contracts.get("generation", {}).get("boundaries", {}) if contracts else {}
    passed = len(errors) == 0 and bool(runtime_result and runtime_result.get("passed"))
    for index, item in enumerate(errors, start=1):
        item.setdefault("error_id", f"HERR-{digest[:8].upper()}-{index:03d}")
        item.setdefault("run_id", run_id)
        item["attempt"] = attempt
    result = {
        "run_id": run_id,
        "ran_at": utc_now(),
        "attempt": attempt,
        "project_id": project_id,
        "snapshot_revision": snapshot.get("revision"),
        "source_hash": digest,
        "passed": passed,
        "errors": errors,
        "evidence": {
            "contract_lint": "passed" if not lint_errors else "blocked",
            "browser": "passed" if runtime_result and runtime_result.get("passed") else "blocked",
            "browser_result": runtime_result,
            "visual_diff": visual_result,
            "target_user_validation": "not-claimed",
        },
        "artifacts": {
            "html": str(html_path) if html_path else None,
            "screenshot": str(screenshot) if screenshot else None,
            "trace": str(output_dir / "trace.jsonl"),
        },
        "boundaries": boundaries,
    }
    write_report(result, output_dir, project_dir)
    append_trace(output_dir, "run-complete", {"passed": result["passed"], "error_count": len(errors)})
    return result


def apply_local_repairs(project_dir: Path, attempt_dir: Path) -> bool:
    attempt_dir.mkdir(parents=True, exist_ok=True)
    for filename in REQUIRED_FILES.values():
        source = project_dir / filename
        if source.is_file():
            shutil.copy2(source, attempt_dir / filename)
    expected_path = project_dir / REQUIRED_FILES["expected"]
    if expected_path.is_file():
        baseline_ref = read_json(expected_path).get("visual_diff", {}).get("baseline")
        if baseline_ref:
            baseline_source = (project_dir / baseline_ref).resolve()
            try:
                baseline_source.relative_to(project_dir.resolve())
            except ValueError:
                baseline_source = Path("__outside_project__")
            if baseline_source.is_file():
                baseline_target = attempt_dir / baseline_ref
                baseline_target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(baseline_source, baseline_target)
    frame_path = attempt_dir / REQUIRED_FILES["frame"]
    if not frame_path.is_file():
        return False
    frame = read_json(frame_path)
    viewport = frame.get("viewport", {})
    safe = frame.get("safe_area", {"top": 0, "right": 0, "bottom": 0, "left": 0})
    changed = False
    for region in frame.get("regions", []):
        if region.get("repair_policy") != "shrink-to-safe-area":
            continue
        geometry = region.get("geometry", {})
        max_right = viewport.get("width", 0) - safe.get("right", 0)
        max_bottom = viewport.get("height", 0) - safe.get("bottom", 0)
        if numeric(geometry.get("x")) and numeric(geometry.get("width")) and geometry["x"] + geometry["width"] > max_right:
            geometry["width"] = max(1, max_right - geometry["x"])
            changed = True
        if numeric(geometry.get("y")) and numeric(geometry.get("height")) and geometry["y"] + geometry["height"] > max_bottom:
            geometry["height"] = max(1, max_bottom - geometry["y"])
            changed = True
    if changed:
        write_json(frame_path, frame)
    return changed


def run_repair(project_dir: Path, output_dir: Path) -> dict[str, Any]:
    source_result = run_pipeline(project_dir, output_dir / "source", attempt=0)
    if source_result["passed"]:
        source_result["repair"] = {"status": "not-needed", "source_modified": False}
        return source_result
    current = project_dir
    for attempt in range(1, 3):
        attempt_input = output_dir / f"attempt-{attempt}" / "input"
        changed = apply_local_repairs(current, attempt_input)
        if not changed:
            source_result["repair"] = {"status": "not-repairable", "source_modified": False, "attempts": attempt - 1}
            write_json(output_dir / "repair-result.json", source_result)
            return source_result
        result = run_pipeline(attempt_input, output_dir / f"attempt-{attempt}" / "run", attempt=attempt)
        if result["passed"]:
            result["repair"] = {
                "status": "candidate-passed",
                "source_modified": False,
                "attempts": attempt,
                "candidate_contract": str(attempt_input / REQUIRED_FILES["frame"]),
                "release_requires_promotion": True,
            }
            write_json(output_dir / "repair-result.json", result)
            return result
        current = attempt_input
    result["repair"] = {"status": "exhausted", "source_modified": False, "attempts": 2}
    write_json(output_dir / "repair-result.json", result)
    return result


def output_path(project_dir: Path, supplied: str | None) -> Path:
    return Path(supplied).resolve() if supplied else (ROOT / ".harness" / project_dir.name).resolve()


def print_result(result: dict[str, Any]) -> None:
    summary = {
        "run_id": result.get("run_id"),
        "project_id": result.get("project_id"),
        "passed": result.get("passed"),
        "errors": result.get("errors", []),
        "artifacts": result.get("artifacts", {}),
        "repair": result.get("repair"),
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))


def main() -> int:
    parser = argparse.ArgumentParser(description="Controlled prototype production harness")
    subparsers = parser.add_subparsers(dest="command", required=True)
    for command in ("lint", "render", "test", "report", "all", "repair", "snapshot"):
        sub = subparsers.add_parser(command)
        sub.add_argument("--project", required=True, help="directory containing project JSON contracts")
        sub.add_argument("--output", help="run output directory")
        if command in {"test", "all"}:
            sub.add_argument("--update-baseline", action="store_true", help="replace the project visual baseline")
        if command == "snapshot":
            sub.add_argument("--event", required=True, help="JSON event with base_revision and add/replace patches")
    args = parser.parse_args()
    project_dir = Path(args.project).resolve()
    if not project_dir.is_dir():
        print(json.dumps({"passed": False, "error": f"project directory not found: {project_dir}"}, ensure_ascii=False))
        return 2
    if args.command == "snapshot":
        result = record_snapshot_event(project_dir, Path(args.event).resolve())
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result.get("passed") else 1
    out = output_path(project_dir, args.output)
    if args.command == "lint":
        contracts, errors = validate_project(project_dir)
        result = {"project_id": contracts.get("identity", {}).get("project_id"), "passed": not errors, "errors": errors}
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if not errors else 1
    if args.command == "render":
        contracts, errors = validate_project(project_dir)
        if errors:
            print(json.dumps({"passed": False, "errors": errors}, ensure_ascii=False, indent=2))
            return 1
        out.mkdir(parents=True, exist_ok=True)
        artifact = out / "prototype.html"
        artifact.write_text(render_html(contracts), encoding="utf-8")
        print(json.dumps({"passed": True, "artifact": str(artifact)}, ensure_ascii=False, indent=2))
        return 0
    if args.command == "repair":
        result = run_repair(project_dir, out)
    else:
        result = run_pipeline(project_dir, out, update_baseline=bool(getattr(args, "update_baseline", False)))
    print_result(result)
    return 0 if result.get("passed") else 1


if __name__ == "__main__":
    raise SystemExit(main())
