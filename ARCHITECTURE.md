# 架构说明

## 目标

本项目把模糊需求编译成可追溯的产品规格和可验证的中保真原型：

```text
自然语言/资料
→ Project Identity
→ ProjectSnapshot
→ 需求与业务流程
→ 产品/页面/组件 Contract
→ Frame/Flow/Asset Contract
→ 受控原型 Harness
→ 浏览器与任务验证
→ Handoff Package
```

## 模块边界

| 层 | 目录/文件 | 职责 | 不负责 |
| --- | --- | --- | --- |
| 入口层 | `SKILL.md` | 路由、阶段门槛、交互约束和交付边界 | 维护每个领域的全部细节 |
| 协议层 | `references/` | 需求、对话、Contract、模具、交接和治理规则 | 直接生成生产代码 |
| 数据契约层 | `schemas/` | 定义 Snapshot、Identity、Frame、Flow、Asset、Handoff 等结构 | 保存某个项目的运行状态 |
| 运行层 | `harness`、`scripts/harness.py` | 编译受控原型、渲染、浏览器检查、报告和有限局部修复 | 静默改写业务语义 |
| 资产层 | `assets/prototype-harness/` | 提供中性 Shell、运行时、组件白名单和占位表达 | 充当品牌视觉资产库 |
| 项目状态层 | `docs/` 与目标项目运行目录 | 保存决策、计划、质量规则和项目事实 | 依赖聊天上下文作为唯一状态 |
| 验证层 | `tests/`、`scripts/verify` | 回归、隔离、模具、Harness 和 Golden Case 验证 | 把静态检查冒充用户验证 |
| 平台适配层 | `platform/` | 提供 Dify、Coze、GPTs 等配置映射 | 改变核心需求语义 |

## 依赖方向

```text
SKILL.md
  ↓ 路由
references/ ──→ schemas/
  ↓                  ↓
ProjectSnapshot → harness/runtime
                         ↓
                    generated prototype
                         ↓
                  tests / handoff report
```

- `SKILL.md` 可以路由到参考协议，但不应复制整份协议。
- `references/` 可以引用 Schema 字段，但不得绕过 Contract 直接规定运行时实现细节。
- Harness 只消费已通过身份、Snapshot、Frame、Flow、模板适配和素材政策的输入。
- 测试应验证可观察行为和边界，不以关键词存在作为主要发布证据。
- 生成项目与共享模板隔离；`no_match` 只能生成 project-local 候选，不能自动注册为公共模具。

## 状态所有权

- 需求、决策、范围、阶段：`ProjectSnapshot` 与 `docs/decisions/`。
- 实施目标和进度：`docs/plans/`。
- 页面几何、状态和交互：Frame/Flow Contract。
- 原型运行结果：Harness 输出目录和报告。
- 发布是否通过：`docs/quality.md` 定义的证据，而不是聊天中的口头结论。

## 变更原则

每次变更应回答四件事：改了什么、为什么改、会防止什么问题、跑了什么验证。跨层变化必须检查需求、Contract、运行时、测试和交接是否漂移；高影响业务规则不能由原型样例或视觉占位静默决定。
