# 业务项目 Harness 配置启动

当用户希望让 Harness Engineering 规则跨任务持续生效，且当前目标是一个新的业务项目时，使用仓库内的初始化器生成项目级骨架；不要默认把当前 Skill 仓库的历史需求、文案、视觉资产或业务状态复制到新项目。

## 初始化命令

```bash
python3 /Users/tal/.codex/skills/product-architecture-requirements/scripts/init_project.py /path/to/project --name "项目名称"
```

初始化器只创建不存在的文件，不覆盖目标项目已有内容。默认生成：

```text
项目/
├── AGENTS.md
├── ARCHITECTURE.md
├── docs/
│   ├── product-specs/README.md
│   ├── plans/README.md
│   ├── decisions/README.md
│   └── quality.md
└── scripts/verify
```

## 初始化后动作

1. 在 `docs/product-specs/` 写入目标用户、核心任务、首期范围、暂不做和验收标准。
2. 在 `ARCHITECTURE.md` 补充模块边界、依赖方向和运行环境。
3. 高影响选择写入 `docs/decisions/`，实施过程写入 `docs/plans/`。
4. 为 `scripts/verify` 接入项目专属测试，或设置 `PROJECT_VERIFY_COMMAND`。
5. 运行 `./scripts/verify`，把实际结果写回计划或质量记录。

## 隔离规则

初始化器只提供协作骨架，不复制来源项目的 ProjectSnapshot、DEC/CHG、用户数据、业务规则、视觉资产、品牌 Token 或原型模具。若确需复用旧项目结构，必须先由当前 Skill 完成 `resume/fork/new/needs_confirmation` 判断，并将允许继承项记录在项目决策中。
