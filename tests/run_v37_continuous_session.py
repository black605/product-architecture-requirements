#!/usr/bin/env python3
"""Run a real three-turn PRS session and verify version continuity."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

from run_formal_platform_50 import CODEX, MODEL, PATCH_FIRST_LINE, SKILL_DIR, extract_thread_id, source_snapshot


DEFAULT_OUTPUT = SKILL_DIR / "tests" / "continuous-session" / "v3.7.0-release"


def invoke(command: list[str], prompt: str, output_file: Path) -> tuple[str, str, int, float]:
    started = time.monotonic()
    result = subprocess.run(
        command,
        input=prompt,
        text=True,
        capture_output=True,
        timeout=240,
        check=False,
    )
    output = output_file.read_text(encoding="utf-8").strip() if output_file.exists() else ""
    raw = result.stdout + ("\n" + result.stderr if result.stderr else "")
    return output, raw, result.returncode, round(time.monotonic() - started, 2)


def first_line(text: str) -> str:
    return next((line.strip() for line in text.splitlines() if line.strip()), "")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    snapshot = source_snapshot()

    prompts = [
        f"""你是正式平台上的产品架构与需求分析 Skill 运行实例。请读取并严格遵循：{SKILL_DIR / 'SKILL.md'}
不要修改任何文件，不要联网，不生成代码。

当前已确认：项目为学生课后复习详情页；PUI/UIP/ASC 均 Ready；TFD-900 的结论是 extensible/ready；同一原型会话为 PRS-900；当前受控 Generation Request 和原型 Contract 基线是 v0.1；唯一主任务是查看重点后开始练习；页面已有练习区和练习结果区，薄弱知识点是 P2 区域并位于练习前；模板允许 P2 区域换序与无内容时坍缩，P0 和唯一主操作不变；当前环境没有原型重渲染能力。

请先给出生成前摘要和受控 Generation Request 状态，不要假装页面已经生成。""",
        "把薄弱知识点移到练习结果后面；没有薄弱项时整块隐藏。继续沿用当前会话，不要让我重述项目背景。",
        "再改一下：学生只要看完重点就自动算完成，不需要做练习。继续基于上一版处理。",
    ]

    turns: list[dict[str, object]] = []
    with tempfile.TemporaryDirectory(prefix="v37-prs-session-") as runtime_dir:
        session_id: str | None = None
        for index, prompt in enumerate(prompts, start=1):
            output_file = args.output / f"turn-{index}.txt"
            if index == 1:
                command = [
                    CODEX, "exec", "-m", MODEL, "--json", "--skip-git-repo-check",
                    "-s", "read-only", "-C", runtime_dir, "-o", str(output_file), "-",
                ]
            else:
                if not session_id:
                    raise SystemExit("initial turn did not return a resumable session id")
                command = [
                    CODEX, "exec", "resume", "-m", MODEL, "--json", "--skip-git-repo-check",
                    "-o", str(output_file), session_id, "-",
                ]
            output, raw, exit_code, duration = invoke(command, prompt, output_file)
            returned_session_id = extract_thread_id(raw)
            if index == 1:
                session_id = returned_session_id
            turns.append(
                {
                    "turn": index,
                    "prompt": prompt,
                    "assistant_output": output,
                    "first_line": first_line(output),
                    "exit_code": exit_code,
                    "duration_seconds": duration,
                    "thread_id": returned_session_id,
                }
            )

    turn1, turn2, turn3 = turns
    turn2_match = PATCH_FIRST_LINE.fullmatch(str(turn2["first_line"]))
    turn3_match = PATCH_FIRST_LINE.fullmatch(str(turn3["first_line"]))
    checks = {
        "all_turns_succeeded": all(turn["exit_code"] == 0 for turn in turns),
        "same_runtime_thread": bool(session_id and all(turn["thread_id"] == session_id for turn in turns)),
        "turn1_restores_prs_and_baseline": "PRS-900" in str(turn1["assistant_output"]) and "v0.1" in str(turn1["assistant_output"]),
        "turn1_has_controlled_request_boundary": (
            "Generation Request" in str(turn1["assistant_output"])
            and not re.search(r"(?m)^(?!.*(?:未|不|尚未)).*原型已(?:完成|生成)", str(turn1["assistant_output"]))
        ),
        "turn2_is_l2_patch_from_v01": bool(
            turn2_match
            and turn2_match.group("tier") == "L2"
            and turn2_match.group("baseline") == "v0.1"
            and turn2_match.group("result") == "applied"
        ),
        "turn2_advances_to_v02": "v0.2" in str(turn2["assistant_output"]),
        "turn3_is_l3_decision_from_v02": bool(
            turn3_match
            and turn3_match.group("tier") == "L3"
            and turn3_match.group("baseline") == "v0.2"
            and turn3_match.group("result") == "needs-decision"
        ),
        "turn3_creates_dec_and_chg": "DEC-" in str(turn3["assistant_output"]) and "CHG-" in str(turn3["assistant_output"]),
    }
    result = {
        "suite": "v3.7-continuous-prs-session",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "model": MODEL,
        "source_snapshot_sha256": snapshot["sha256"],
        "source_git_commit": snapshot["git_commit"],
        "session_id": session_id,
        "turns": turns,
        "checks": checks,
        "passed": all(checks.values()),
        "summary": f"{sum(checks.values())}/{len(checks)} checks passed",
    }
    (args.output / "result.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
