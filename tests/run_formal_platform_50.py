#!/usr/bin/env python3
"""Run 50 real one-round conversations against the installed Codex runtime.

The runner deliberately invokes the platform executable instead of fabricating
assistant replies. Each record contains the exact user input, the captured final
assistant message, execution metadata, and lightweight constraint checks.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import os
import re
import subprocess
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = SKILL_DIR / "tests" / "formal-platform-50"
PROJECT_DIR = Path("/Users/tal/Documents/ChatGPT/新课件-0818")
CODEX = "/Applications/ChatGPT.app/Contents/Resources/codex"
MODEL = os.environ.get("FORMAL_PLATFORM_MODEL", "gpt-5.6-luna")

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

PROJECT_CONTEXT = """
当前项目已知事实：产品是“学而思密卷 · 2026 高考备考专区”，当前页面有数学、语文、英语学科入口，包含备考方案、真题实战、真题模拟和资料类内容卡片，设计画布约为 1280×860，整体是温暖的新中式备考视觉方向。上述是页面与项目资料事实，不等同于已确认的业务规则。""".strip()


def source_snapshot() -> dict[str, object]:
    """Bind runtime evidence to the exact behavior and validator sources."""
    candidates = [SKILL_DIR / "SKILL.md"]
    for pattern in (
        "platform/*.md",
        "references/*.md",
        "schemas/*",
        "tests/*.py",
        "tests/prototype-template-50.json",
        "tests/fixtures/**/*",
    ):
        candidates.extend(SKILL_DIR.glob(pattern))
    files = sorted({path for path in candidates if path.is_file()})
    digest = hashlib.sha256()
    manifest: list[dict[str, str]] = []
    for path in files:
        relative = path.relative_to(SKILL_DIR).as_posix()
        content = path.read_bytes()
        file_hash = hashlib.sha256(content).hexdigest()
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(content)
        digest.update(b"\0")
        manifest.append({"path": relative, "sha256": file_hash})
    commit = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=SKILL_DIR, text=True, capture_output=True, check=False
    ).stdout.strip() or None
    return {"sha256": digest.hexdigest(), "git_commit": commit, "files": manifest}

CASES = [
    "我想做一个给高中生用的高考备考内容专区。",
    "这个专区要高级一点，最好让学生一打开就知道先学什么。",
    "学生现在找真题、资料和课程很乱，我想把它们放到一个页面。",
    "请帮我判断这个页面应该做成内容展示页，还是完整学习产品。",
    "数学、语文、英语都要放进去，但我还没想好怎么组织。",
    "我想按一轮复习、二轮复习、冲刺来分阶段。",
    "卡片上有‘2026最新’‘精选’‘适合冲刺’，希望学生点卡片就能开始。",
    "当前页面已经有真题实战、真题模拟和备考方案，下一步应该补什么功能？",
    "先只服务学生，老师和运营人员以后再考虑。",
    "不同地区、年级和考试年份的内容可能不能让所有人看到。",
    "老师想布置一套作业，学生在线完成后能看到结果。",
    "教师需要批量导入题目和学生名单，请拆解流程。",
    "客观题自动判分，主观题由老师批改，规则还没定。",
    "学生可以保存草稿、限时作答，也可能允许重新提交。",
    "老师想查看班级完成率和错题情况，但不希望学生看到别人的数据。",
    "作业发布后如果发现题目有问题，老师能不能替换题目？",
    "一个学生同时参加多个班级，作业权限怎么处理？",
    "学生提交失败或网络中断时，系统应该怎么兜底？",
    "请把作答会话、提交记录、评分结果、解析反馈和复习任务拆成对象。",
    "我们要把在线评作业和当前高考备考专区关联起来。",
    "做一个多租户 SaaS 机构分销体系，涉及多级分润和退款撤回。",
    "不同机构只能看自己的订单，但总部需要跨机构看汇总。",
    "退款和分润同时发生时，怎么定义状态和异常流程？",
    "分润计算可能被重复请求，产品需求里要怎么写并发规则？",
    "机构管理员离职后，临时授权和历史操作记录怎么处理？",
    "数据大屏和后台控制台要支持多视图切换和复杂动效。",
    "数据大屏加载很慢，要设计 Skeleton、空态、错误态和刷新提示。",
    "控制台有表格、抽屉、筛选器和批量操作，请给组件级需求。",
    "多视图切换时筛选条件是否共享，我还没有决定。",
    "大屏需要自动轮播，但用户也能手动暂停，怎么定义状态机？",
    "我想做一个课程内容运营后台，支持创建、审核、发布和下线。",
    "内容有草稿、待审核、已发布、已下线、已过期和已归档状态。",
    "运营要批量替换旧资料，同时保留学生历史学习记录。",
    "‘最新’和‘精选’标签由谁维护，什么时候失效？",
    "内容支持预览、下载和分享，但版权规则还没确定。",
    "搜索要支持学科、年级、地区、考试年份和内容类型筛选。",
    "搜索结果不能泄露无权限内容，没结果时要给用户下一步。",
    "推荐可以是人工精选、规则筛选或算法推荐，请帮我先做需求级方案。",
    "学生中途退出后，要能从最近有效位置继续学习。",
    "错题要能回到原试卷、解析和复习任务，且不能重复堆积。",
    "请把当前高考备考专区拆成业务架构、产品架构和候选技术架构。",
    "请输出当前项目的角色权限矩阵，但不要擅自增加家长角色。",
    "请给出当前项目一期 MVP，区分展示页能力和真正学习闭环。",
    "请设计首页信息架构，要求每个一级模块都能回指业务目标。",
    "请给备考内容卡片定义唯一主任务、状态、去向和验收标准。",
    "请给学习阶段定义目标、入口、完成条件、解锁规则和返回上一阶段方式。",
    "请把页面布局映射到 AntD/Tailwind 风格组件，但不要写 React 或 CSS 代码。",
    "请列出当前项目最重要的空状态、错误状态、无权限状态和降级策略。",
    "请生成交给产品、设计和前端共同评审的下一步需求清单。",
    "如果信息不足，请先做最小澄清，不要直接生成完整 PRD。",
]


def load_cases(path: Path) -> list[dict[str, object]]:
    """Load role-aware cases without changing the historical default suite.

    Each JSON item may be a plain string or an object with `role`, `journey`,
    `confirmed_context`, `focus`, and `user_input`. The object form embeds only
    user-confirmed context, so each ephemeral run can exercise a real dialogue
    turn without inventing earlier assistant replies.
    """
    raw_cases = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw_cases, list):
        raise SystemExit("cases JSON must be a list")
    loaded: list[dict[str, object]] = []
    for index, item in enumerate(raw_cases, start=1):
        if isinstance(item, str):
            loaded.append({"user_input": item, "role": "未说明角色", "journey": "默认套件", "focus": "标准约束", "mode": "standard", "confirmed_context": []})
            continue
        if not isinstance(item, dict) or not isinstance(item.get("user_input"), str):
            raise SystemExit(f"invalid case at index {index}: expected user_input")
        context = item.get("confirmed_context", [])
        if not isinstance(context, list) or not all(isinstance(value, str) for value in context):
            raise SystemExit(f"invalid confirmed_context at index {index}")
        role = str(item.get("role", "未说明角色"))
        journey = str(item.get("journey", "未命名会话路径"))
        focus = str(item.get("focus", "低摩擦自然语言承接"))
        history = "\n".join(f"- {value}" for value in context) or "- 尚无已确认内容"
        mode = str(item.get("mode", "standard"))
        if mode not in {"standard", "exploration", "delivery"}:
            raise SystemExit(f"invalid mode at index {index}: {mode}")
        loaded.append({
            "user_input": item["user_input"],
            "role": role,
            "journey": journey,
            "focus": focus,
            "mode": mode,
            "confirmed_context": context,
            "rendered_input": (
                f"【当前沟通角色】{role}\n"
                f"【会话路径】{journey}\n"
                f"【本轮关注点】{focus}\n"
                f"【此前已确认的用户信息】\n{history}\n\n"
                f"【用户本轮表达】\n{item['user_input']}"
            ),
        })
    return loaded


def prompt_for(round_no: int, user_input: str, project_context: str = PROJECT_CONTEXT) -> str:
    return f"""你是正式平台上的产品架构与需求分析 Skill 运行实例。
请先读取并遵循：{SKILL_DIR / 'SKILL.md'}
不要修改任何文件，不要联网，不要生成后端代码或设计源文件。

这是第 {round_no}/50 轮真实对话测试。{project_context}

本轮要求：
1. 只处理本轮用户输入，输出给最终用户的正式回复；
2. 探索阶段单轮只提出 1 个核心问题；
3. 区分用户确认、暂定方向与待确认内容，不能把假设写成事实；非专业角色可用自然语言表达，不要求展示内部标签；
4. 若本轮信息足够，交付当前阶段最小的结构化产物；若不足，只追问最影响方案的缺口；
5. 不要为了套模板而输出完整 PRD，回复控制在 1200 字以内。
6. 若本轮涉及原型模具适配或原型回改，第一非空行必须严格使用 SKILL.md 规定的 TFD/PATCH 固定回执，不在此前增加标题或解释；PATCH 第三段只能写 vX.Y 版本号。
7. 交付 Profile、素材 Slot、项目候选、原型会话或模板生命周期记录时，必须显示 UIP/ASC/PTC/PRS/TMF 对象 ID；Profile 必须明确旧文案与旧视觉资产均默认不继承；素材 Slot 必须显示比例/尺寸/安全区字段，未知就标 Pending；L3 回改必须同时显示 DEC 与 CHG 对象 ID。

用户输入：
{user_input}
"""


def extract_thread_id(raw: str) -> str | None:
    patterns = [
        r"session id:\s*([0-9a-f-]{20,})",
        r'"thread_id"\s*:\s*"([0-9a-f-]{20,})"',
        r'"id"\s*:\s*"([0-9a-f-]{20,})"',
    ]
    for pattern in patterns:
        match = re.search(pattern, raw, re.IGNORECASE)
        if match:
            return match.group(1)
    return None


def count_questions(text: str) -> int:
    """Count visible interrogative sentences, independent of Markdown layout."""
    return len(re.findall(r"[？?]+", text))


def evaluate_output(
    assistant_output: str,
    mode: str = "standard",
    focus: str = "",
    journey: str = "",
) -> dict[str, object]:
    question_count = count_questions(assistant_output)
    chinese_char_count = len(re.findall(r"[\u4e00-\u9fff]", assistant_output))
    internal_language = re.search(
        r"(?<![\w-])(?:S[0-7]|Needs Decision|Ready (?:Gate|for \w+)|ProjectSnapshot|DEC-\d+|CHG-\d+|PUI-\d+)\b",
        assistant_output,
    )
    markdown_table = re.search(r"^\s*\|.+\|\s*$", assistant_output, re.MULTILINE)
    structured_markdown = re.search(r"^\s*(?:#{1,6}\s|[-*]\s+|\d+[.)]\s+)", assistant_output, re.MULTILINE)
    implementation_code = re.search(
        r"```(?:tsx|jsx|javascript|css|python|sql|java|go)\b|import\s+React\b|function\s+\w+\s*\(|<div\b",
        assistant_output,
        re.IGNORECASE,
    )
    blocked_trace_violation = re.search(
        r"(?im)^(?:\s*[-*]\s*)?(?:`?(?:TR|AC)[-_A-Z0-9]*`?|.*\bGiven\b.*\bThen\b|.*→.*)[^\n]*(?:暂定|尚未确认|按.{0,12}确认|具体.{0,20}待确认|规则.{0,20}待确认|是否.{0,15}待确认|由实现决定|进入\s*A\s*或\s*B)",
        assistant_output,
    )
    high_impact_bypass = re.search(r"待确认但不影响[^\n]*(?:Must|骨架|规格|验收)", assistant_output, re.IGNORECASE)
    first_line = next((line.strip() for line in assistant_output.splitlines() if line.strip()), "")
    contract_format_pass = True
    contract_format_type = "not_applicable"
    if focus in {"exact", "extensible", "no_match"}:
        contract_format_type = "TFD"
        match = TFD_FIRST_LINE.fullmatch(first_line)
        contract_format_pass = bool(match and match.group("result") == focus)
    elif journey in PATCH_EXPECTATIONS:
        contract_format_type = "PATCH"
        expected_tier, expected_result, expected_baseline = PATCH_EXPECTATIONS[journey]
        match = PATCH_FIRST_LINE.fullmatch(first_line)
        contract_format_pass = bool(
            match
            and (expected_tier is None or match.group("tier") == expected_tier)
            and match.group("baseline") == expected_baseline
            and match.group("result") == expected_result
        )
    return {
        "real_process_succeeded": True,
        "assistant_output_present": bool(assistant_output.strip()),
        "question_count": question_count,
        "question_limit_pass": question_count <= 2,
        "single_question_pass": mode != "exploration" or question_count <= 1,
        "chinese_char_count": chinese_char_count,
        "compact_exploration_pass": mode != "exploration" or chinese_char_count <= 250,
        "internal_language_absent": mode != "exploration" or internal_language is None,
        "tableless_exploration_pass": mode != "exploration" or markdown_table is None,
        "plain_text_exploration_pass": mode != "exploration" or structured_markdown is None,
        "uncertainty_labels_present": any(
            label in assistant_output
            for label in (
                "已知事实", "已确认", "已确定", "待确认", "还需要确认", "暂定假设", "暂定方向", "暂定",
                "已改成", "已记录", "已更新", "当前交付", "当前判断", "当前边界", "判断", "结论", "目前", "还需确认", "尚未确定", "暂不确定", "不能当作事实",
                "目前只确认", "目前只能确认", "当前只确认", "未定", "仍未确定", "待具体化", "暂不展开", "暂不能",
                "暂作为", "还需要确认",
                "Fact", "Confirmed", "Inference", "Proposal", "Assumption", "Pending",
            )
        ),
        "blocked_trace_absent": blocked_trace_violation is None,
        "high_impact_bypass_absent": high_impact_bypass is None,
        "implementation_code_absent": implementation_code is None,
        "contract_first_line": first_line,
        "contract_format_type": contract_format_type,
        "contract_format_pass": contract_format_pass,
    }


def run_case(
    item: tuple[int, dict[str, object]],
    output_dir: Path,
    project_context: str = PROJECT_CONTEXT,
    snapshot: dict[str, object] | None = None,
) -> dict[str, object]:
    round_no, case = item
    user_input = str(case.get("rendered_input") or case["user_input"])
    mode = str(case.get("mode", "standard"))
    started = datetime.now(timezone.utc)
    start_clock = time.monotonic()
    output_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(prefix=f"skill-{round_no:03d}-", suffix=".txt", delete=False) as handle:
        final_path = Path(handle.name)
    try:
        with tempfile.TemporaryDirectory(prefix=f"role-dialogue-{round_no:03d}-") as runtime_dir:
            command = [
                CODEX,
                "exec",
                "-m",
                MODEL,
                "--json",
                "--ephemeral",
                "--skip-git-repo-check",
                "-s",
                "read-only",
                "-C",
                runtime_dir,
                "-o",
                str(final_path),
                "-",
            ]
            result = subprocess.run(
                command,
                input=prompt_for(round_no, user_input, project_context),
                text=True,
                capture_output=True,
                timeout=180,
                check=False,
            )
        assistant_output = final_path.read_text(encoding="utf-8") if final_path.exists() else ""
        raw_platform_output = result.stdout + ("\n" + result.stderr if result.stderr else "")
        checks = evaluate_output(
            assistant_output,
            mode,
            str(case.get("focus", "")),
            str(case.get("journey", "")),
        )
        checks["real_process_succeeded"] = result.returncode == 0
        record: dict[str, object] = {
            "round": round_no,
            "platform": "Codex CLI formal runtime",
            "model": MODEL,
            "started_at": started.isoformat(),
            "duration_seconds": round(time.monotonic() - start_clock, 2),
            "exit_code": result.returncode,
            "thread_id": extract_thread_id(raw_platform_output),
            "runtime_workspace": "isolated temporary directory",
            "source_snapshot_sha256": (snapshot or {}).get("sha256"),
            "source_git_commit": (snapshot or {}).get("git_commit"),
            "role": case.get("role"),
            "journey": case.get("journey"),
            "focus": case.get("focus"),
            "test_mode": mode,
            "user_input": user_input,
            "assistant_output": assistant_output.strip(),
            "checks": checks,
        }
        (output_dir / f"round-{round_no:03d}.json").write_text(
            json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        return record
    finally:
        final_path.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--rounds", default="1-50", help="rounds to execute, e.g. 38 or 1-10,15")
    parser.add_argument("--expect-count", type=int, help="expected passing rounds; defaults to the selected round count")
    parser.add_argument("--cases-json", type=Path, help="optional role-aware JSON case file; default suite remains unchanged")
    parser.add_argument(
        "--project-context",
        default=PROJECT_CONTEXT,
        help="shared project context for the default suite; pass an empty string for cross-domain role tests",
    )
    args = parser.parse_args()
    cases = load_cases(args.cases_json) if args.cases_json else [
        {"user_input": value, "role": "未说明角色", "journey": "默认套件", "focus": "标准约束", "mode": "standard", "confirmed_context": []}
        for value in CASES
    ]
    if len(cases) != 50:
        raise SystemExit(f"expected 50 cases, got {len(cases)}")
    selected: set[int] = set()
    for part in args.rounds.split(","):
        if "-" in part:
            start, end = (int(value) for value in part.split("-", 1))
            selected.update(range(start, end + 1))
        else:
            selected.add(int(part))
    if not selected or min(selected) < 1 or max(selected) > len(cases):
        raise SystemExit("rounds must be within 1-50")
    args.output.mkdir(parents=True, exist_ok=True)
    snapshot = source_snapshot()
    (args.output / "source-manifest.json").write_text(
        json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    records: list[dict[str, object]] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
        futures = [
            pool.submit(run_case, (number, cases[number - 1]), args.output / "records", args.project_context, snapshot)
            for number in sorted(selected)
        ]
        for future in concurrent.futures.as_completed(futures):
            records.append(future.result())
    for record_path in sorted((args.output / "records").glob("round-*.json")):
        record = json.loads(record_path.read_text(encoding="utf-8"))
        if int(record["round"]) not in selected:
            record["checks"] = evaluate_output(
                str(record.get("assistant_output", "")),
                str(record.get("test_mode", "standard")),
                str(record.get("focus", "")),
                str(record.get("journey", "")),
            )
            record_path.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            records.append(record)
    records.sort(key=lambda record: int(record["round"]))
    (args.output / "dialogues.jsonl").write_text(
        "".join(json.dumps(record, ensure_ascii=False) + "\n" for record in records), encoding="utf-8"
    )
    shared_hard_checks = (
        "real_process_succeeded", "assistant_output_present", "question_limit_pass",
        "blocked_trace_absent", "high_impact_bypass_absent", "implementation_code_absent",
        "contract_format_pass",
    )
    exploration_hard_checks = (
        "single_question_pass", "compact_exploration_pass", "internal_language_absent",
        "tableless_exploration_pass", "plain_text_exploration_pass", "uncertainty_labels_present",
    )

    def hard_pass(record: dict[str, object]) -> bool:
        keys = shared_hard_checks + (exploration_hard_checks if record.get("test_mode") == "exploration" else ())
        return all(bool(record["checks"].get(key)) for key in keys)

    passed = sum(1 for record in records if hard_pass(record))
    selected_passed = sum(
        1
        for record in records
        if int(record["round"]) in selected and hard_pass(record)
    )
    expected_count = args.expect_count if args.expect_count is not None else len(selected)
    summary = {
        "platform": "Codex CLI formal runtime",
        "model": MODEL,
        "requested_rounds": len(selected),
        "executed_rounds_this_invocation": len(selected),
        "selected_passing_rounds": selected_passed,
        "completed_rounds": len(records),
        "fully_passing_rounds": passed,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_snapshot_sha256": snapshot["sha256"],
        "source_git_commit": snapshot["git_commit"],
        "source_file_count": len(snapshot["files"]),
        "command": "codex exec --json --ephemeral --skip-git-repo-check -s read-only -C isolated-temp -o final -",
        "note": "每条记录均由正式运行时独立执行；本文件不包含人工拼接的 assistant 回复，并绑定同一源码快照。",
    }
    (args.output / "run-summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (args.output / "README.md").write_text(
        "# 正式平台 50 轮真实对话记录\n\n"
        "本目录由 `run_formal_platform_50.py` 调用 Codex CLI 正式运行时生成。每轮是一个独立会话，保存了用户输入、平台返回的最终 assistant 消息、会话标识、退出码和约束检查。\n\n"
        f"- 请求轮次：{len(selected)}\n- 期望本次通过：{expected_count}\n- 本次通过：{selected_passed}\n- 累计完成轮次：{len(records)}\n- 累计轻量检查通过：{passed}\n- 目标 Skill：`{SKILL_DIR / 'SKILL.md'}`\n\n"
        "机器检查验证运行成功、输出存在、提问上限、探索轮字数/纯文本/内部词边界、固定 TFD/Patch 首行格式、事实与待确认表达，以及未生成代码块；它不替代人工产品评审。\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, ensure_ascii=False))
    return 0 if selected_passed == expected_count else 1


if __name__ == "__main__":
    raise SystemExit(main())
