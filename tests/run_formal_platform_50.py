#!/usr/bin/env python3
"""Run 50 real one-round conversations against the installed Codex runtime.

The runner deliberately invokes the platform executable instead of fabricating
assistant replies. Each record contains the exact user input, the captured final
assistant message, execution metadata, and lightweight constraint checks.
"""

from __future__ import annotations

import argparse
import concurrent.futures
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

PROJECT_CONTEXT = """
当前项目已知事实：产品是“学而思密卷 · 2026 高考备考专区”，当前页面有数学、语文、英语学科入口，包含备考方案、真题实战、真题模拟和资料类内容卡片，设计画布约为 1280×860，整体是温暖的新中式备考视觉方向。上述是页面与项目资料事实，不等同于已确认的业务规则。""".strip()

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


def prompt_for(round_no: int, user_input: str) -> str:
    return f"""你是正式平台上的产品架构与需求分析 Skill 运行实例。
请先读取并遵循：{SKILL_DIR / 'SKILL.md'}
不要修改任何文件，不要联网，不要生成后端代码或设计源文件。

这是第 {round_no}/50 轮真实对话测试。{PROJECT_CONTEXT}

本轮要求：
1. 只处理本轮用户输入，输出给最终用户的正式回复；
2. 单轮最多提出 2 个核心问题；
3. 区分“已知事实 / 暂定假设 / 待确认项”，不能把假设写成事实；
4. 若本轮信息足够，交付当前阶段最小的结构化产物；若不足，只追问最影响方案的缺口；
5. 不要为了套模板而输出完整 PRD，回复控制在 1200 字以内。

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
    """Count top-level question items, not every punctuation mark."""
    lines = text.splitlines()
    in_question_section = False
    count = 0
    numbered_with_punctuation = 0
    bullets_with_punctuation = 0
    for line in lines:
        if re.match(r"^#{1,6}\s", line):
            in_question_section = bool(re.search(r"问题|确认|下一步", line))
            continue
        if in_question_section and re.match(r"^\s{0,3}\d+[.)]\s+", line):
            count += 1
        elif in_question_section and re.match(r"^[-*]\s+", line) and re.search(r"[？?]", line):
            count += 1
        elif re.match(r"^\s{0,3}\d+[.)]\s+", line) and re.search(r"[？?]", line):
            numbered_with_punctuation += 1
        elif re.match(r"^[-*]\s+", line) and re.search(r"[？?]", line):
            bullets_with_punctuation += 1
    return count or numbered_with_punctuation or bullets_with_punctuation


def evaluate_output(assistant_output: str) -> dict[str, object]:
    question_count = count_questions(assistant_output)
    implementation_code = re.search(
        r"```(?:tsx|jsx|javascript|css|python|sql|java|go)\b|import\s+React\b|function\s+\w+\s*\(|<div\b",
        assistant_output,
        re.IGNORECASE,
    )
    return {
        "real_process_succeeded": True,
        "assistant_output_present": bool(assistant_output.strip()),
        "question_count": question_count,
        "question_limit_pass": question_count <= 2,
        "uncertainty_labels_present": any(label in assistant_output for label in ("已知事实", "待确认", "暂定假设")),
        "implementation_code_absent": implementation_code is None,
    }


def run_case(item: tuple[int, str], output_dir: Path) -> dict[str, object]:
    round_no, user_input = item
    started = datetime.now(timezone.utc)
    start_clock = time.monotonic()
    output_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(prefix=f"skill-{round_no:03d}-", suffix=".txt", delete=False) as handle:
        final_path = Path(handle.name)
    command = [
        CODEX,
        "exec",
        "--json",
        "--ephemeral",
        "--skip-git-repo-check",
        "-s",
        "read-only",
        "-C",
        str(PROJECT_DIR),
        "-o",
        str(final_path),
        "-",
    ]
    try:
        result = subprocess.run(
            command,
            input=prompt_for(round_no, user_input),
            text=True,
            capture_output=True,
            timeout=180,
            check=False,
        )
        assistant_output = final_path.read_text(encoding="utf-8") if final_path.exists() else ""
        raw_platform_output = result.stdout + ("\n" + result.stderr if result.stderr else "")
        checks = evaluate_output(assistant_output)
        checks["real_process_succeeded"] = result.returncode == 0
        record: dict[str, object] = {
            "round": round_no,
            "platform": "Codex CLI formal runtime",
            "model": MODEL,
            "started_at": started.isoformat(),
            "duration_seconds": round(time.monotonic() - start_clock, 2),
            "exit_code": result.returncode,
            "thread_id": extract_thread_id(raw_platform_output),
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
    args = parser.parse_args()
    if len(CASES) != 50:
        raise SystemExit(f"expected 50 cases, got {len(CASES)}")
    selected: set[int] = set()
    for part in args.rounds.split(","):
        if "-" in part:
            start, end = (int(value) for value in part.split("-", 1))
            selected.update(range(start, end + 1))
        else:
            selected.add(int(part))
    if not selected or min(selected) < 1 or max(selected) > 50:
        raise SystemExit("rounds must be within 1-50")
    args.output.mkdir(parents=True, exist_ok=True)
    records: list[dict[str, object]] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
        futures = [pool.submit(run_case, (number, CASES[number - 1]), args.output / "records") for number in sorted(selected)]
        for future in concurrent.futures.as_completed(futures):
            records.append(future.result())
    for record_path in sorted((args.output / "records").glob("round-*.json")):
        record = json.loads(record_path.read_text(encoding="utf-8"))
        if int(record["round"]) not in selected:
            record["checks"] = evaluate_output(str(record.get("assistant_output", "")))
            record_path.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            records.append(record)
    records.sort(key=lambda record: int(record["round"]))
    (args.output / "dialogues.jsonl").write_text(
        "".join(json.dumps(record, ensure_ascii=False) + "\n" for record in records), encoding="utf-8"
    )
    hard_checks = ("real_process_succeeded", "assistant_output_present", "question_limit_pass", "uncertainty_labels_present", "implementation_code_absent")
    passed = sum(1 for record in records if all(bool(record["checks"].get(key)) for key in hard_checks))
    summary = {
        "platform": "Codex CLI formal runtime",
        "model": MODEL,
        "requested_rounds": 50,
        "executed_rounds_this_invocation": len(selected),
        "completed_rounds": len(records),
        "fully_passing_rounds": passed,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "command": "codex exec --json --ephemeral --skip-git-repo-check -s read-only -C project -o final -",
        "note": "每条记录均由正式运行时独立执行；本文件不包含人工拼接的 assistant 回复。",
    }
    (args.output / "run-summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (args.output / "README.md").write_text(
        "# 正式平台 50 轮真实对话记录\n\n"
        "本目录由 `run_formal_platform_50.py` 调用 Codex CLI 正式运行时生成。每轮是一个独立会话，保存了用户输入、平台返回的最终 assistant 消息、会话标识、退出码和约束检查。\n\n"
        f"- 请求轮次：50\n- 完成轮次：{len(records)}\n- 全量轻量检查通过：{passed}\n- 目标 Skill：`{SKILL_DIR / 'SKILL.md'}`\n\n"
        "轻量检查只验证运行成功、输出存在、提问上限、事实/待确认标签和未生成代码块；它不替代人工产品评审。\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, ensure_ascii=False))
    return 0 if len(records) == 50 and passed == 50 else 1


if __name__ == "__main__":
    raise SystemExit(main())
