#!/usr/bin/env python3
"""Bootstrap project-level Harness Engineering files without overwriting user files."""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "assets" / "project-harness-template"


def project_id(name: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9]+", "-", name.strip().lower()).strip("-")
    return value or "project"


def copy_template(target: Path, name: str) -> tuple[list[str], list[str]]:
    created: list[str] = []
    skipped: list[str] = []
    replacement = {
        "{{PROJECT_NAME}}": name,
        "{{PROJECT_ID}}": project_id(name),
    }
    for source in sorted(TEMPLATE.rglob("*")):
        if source.is_dir():
            continue
        relative = source.relative_to(TEMPLATE)
        destination = target / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.exists():
            skipped.append(str(relative))
            continue
        if source.name == "verify":
            shutil.copy2(source, destination)
            destination.chmod(destination.stat().st_mode | 0o111)
        else:
            content = source.read_text(encoding="utf-8")
            for old, new in replacement.items():
                content = content.replace(old, new)
            destination.write_text(content, encoding="utf-8")
        created.append(str(relative))
    return created, skipped


def main() -> int:
    parser = argparse.ArgumentParser(description="为业务项目生成 Harness Engineering 协作骨架")
    parser.add_argument("target", type=Path, help="目标项目目录；不会覆盖已有文件")
    parser.add_argument("--name", help="项目名称，默认使用目标目录名")
    args = parser.parse_args()

    target = args.target.expanduser().resolve()
    if not target.is_dir():
        print(f"目标目录不存在或不是目录: {target}", file=sys.stderr)
        return 2

    name = args.name or target.name
    created, skipped = copy_template(target, name)
    print(f"已为项目初始化 Harness 配置: {target}")
    print(f"创建 {len(created)} 个文件")
    if skipped:
        print(f"保留已有 {len(skipped)} 个文件: {', '.join(skipped)}")
    print(f"下一步: cd {target} && ./scripts/verify")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
