# A2UI Asset Bundle Handoff

Bundle 将需求控制面交付给 A2UI 设计、运行时和工程团队。它可以包含代码候选，但不执行仓库写入、PR、Catalog 注册、Bit export 或部署，除非用户另行明确授权。

## 1. Bundle Manifest

| 字段 | 要求 |
|---|---|
| `bundle_id` | 稳定 ID，如 `BND-001` |
| `baseline` | 需求版本、DEC/CHG、`intake_id`、`contract_id`、功能/页面/组件 ID |
| `scope` | 本次允许生成与禁止推断的范围 |
| `artifacts` | 每个产物的类型、路径/返回位置、来源、状态与 Owner |
| `contracts` | Slot、Token、Schema、Action、Asset、模板/路由策略的引用 |
| `quality` | 压力用例、无障碍、编译、测试、视觉/运行时证据 |
| `lifecycle` | 组件/Bundle 的分层状态与每层证明 |
| `external_actions` | PR、注册、export、部署；默认 `not-authorized` |
| `risks_and_gaps` | 未决项、依赖、失败项和恢复路径 |

## 2. 允许的产物类型

| 类型 | Bundle 可以交付 | 不能声称 |
|---|---|---|
| UI 候选 | 受控 TSX/模板候选、Props/Slot 说明、组件测试 | 已被目标项目消费 |
| Token | CSS Variables、Tailwind 扩展或语义 Token 配方 | 已在生产主题生效 |
| Contract | JSON Schema、Catalog/Registry 意图、模板 allowlist | 已注册可被模型调用 |
| 测试 | 单元、交互、压力、无障碍、验收追溯 | 生产服务已通过 |
| 文档 | Handoff、功能追溯、Owner、非目标、运行说明 | 业务规则已经用户确认 |

## 3. 生命周期证据

| 状态 | 最低证据 | 不代表 |
|---|---|---|
| `draft` | Manifest 与候选产物存在 | 可运行或可复用 |
| `local-validated` | 本地编译/测试/视觉检查记录 | 已注册或已发布 |
| `runtime-registered` | Catalog、Schema、模板、Registry、Renderer 一致 | 已被目标应用使用 |
| `tagged-awaiting-export` | 本地不可变版本/标签存在 | 已远程分发 |
| `exported` | 远程组件库确认可见 | 被任一运行时消费 |
| `consumed-by-runtime` | 目标应用有直接 import/resolver 证据 | 生产 API/部署可用 |
| `deployment-ready` | 生产依赖、路由、凭据/环境与发布检查均通过 | 已完成外部发布动作 |

## 4. Bundle 验收

Bundle 至少验证：

1. 每个 P0 功能有产物或明确 Blocked 原因；
2. 每个组件能回指功能、页面、Contract、DEC/CHG 和测试；
3. Token/Schema/组件 ID 无冲突，且允许的页面模板与 Variant 一致；
4. P0 状态、压力用例与 fallback 有测试或待执行说明；
5. 未确认 L3 规则、未授权外部动作与真实服务/部署状态清楚分离；
6. 产物路径可打开或明确未生成，不能使用模糊“已导出”结论。

## 5. 交付状态与授权

默认把所有外部动作设为 `not-authorized`。只有用户明确授权了目标仓库/目录、远程 Scope 或部署环境，并且质量门槛满足时，才可由对应专业 Skill 执行。运行报告必须分开写：本地文件变更、远程发布、目标应用消费、生产部署。
