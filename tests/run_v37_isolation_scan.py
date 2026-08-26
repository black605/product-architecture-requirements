#!/usr/bin/env python3
"""Scan a project-local candidate for historical-project contamination."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
FIXTURE = ROOT / "fixtures" / "cross-project"


def main() -> int:
    source = json.loads((FIXTURE / "student-source.json").read_text(encoding="utf-8"))
    candidate = (FIXTURE / "teacher-review-candidate.html").read_text(encoding="utf-8")
    forbidden = [
        *source["copy"],
        *source["visual_assets"],
        *source["brand_tokens"],
        *source["business_rules"],
        source["project_id"],
    ]
    checks = {
        "project_is_independent": 'data-project-id="PROJECT-TEACHER-NEW"' in candidate,
        "scope_is_project_local": 'data-scope="project-local"' in candidate,
        "profile_is_neutral": 'data-profile="prototype-neutral"' in candidate,
        "semantic_regions_present": candidate.count("data-semantic-role=") >= 4,
        "asset_slot_is_placeholder": 'data-asset-slot="ASC-TEACHER-001"' in candidate,
        "no_embedded_image": "<img" not in candidate and "background-image" not in candidate,
        "historical_content_absent": not any(value in candidate for value in forbidden),
    }
    result = {
        "suite": "v3.7-cross-project-isolation-scan",
        "candidate": str((FIXTURE / "teacher-review-candidate.html").relative_to(ROOT.parent)),
        "forbidden_source": str((FIXTURE / "student-source.json").relative_to(ROOT.parent)),
        "checks": checks,
        "passed": all(checks.values()),
        "summary": f"{sum(checks.values())}/{len(checks)} checks passed",
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
