# DEC-2026-08-24：将 Harness 规则项目化

- 状态：Confirmed
- Owner：Skill 维护者
- 影响范围：项目协作、需求追溯、质量验证、版本交付

## 背景

仅依赖对话上下文无法保证跨任务持续遵循项目目标、质量门槛、已知缺口和安全边界。现有 Skill 已有 Harness、Contract 和测试资产，需要一个项目级入口把这些能力组织起来。

## 决策

在 Skill 仓库根目录采用 `AGENTS.md + ARCHITECTURE.md + docs/ + scripts/verify` 的最小治理结构：

- `AGENTS.md` 固化 Agent 协作规则和项目地图；
- `ARCHITECTURE.md` 固化模块边界和依赖方向；
- `docs/` 保存产品基线、计划、设计决策和质量规则；
- `scripts/verify` 作为统一质量证据入口；
- `SKILL.md` 负责在维护本仓库或进入目标项目时路由读取这些规则。

## 取舍

- 不把所有协议复制到 `AGENTS.md`，避免入口膨胀和规则分叉。
- 不用文档存在性替代真实 Harness、浏览器和任务验证。
- 不自动把当前项目文档安装到所有业务项目；业务项目应建立自己的 `AGENTS.md` 和 `ProjectSnapshot`。

## 预期结果

后续任务能够从文件读取稳定上下文，完成后能通过统一命令返回验证证据；重复缺陷可以沉淀为 Schema、规则或测试，而不是依赖提醒模型“再认真一点”。
