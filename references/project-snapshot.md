# ProjectSnapshot 权威状态模型

`ProjectSnapshot` 是需求、原型、交接和复盘共享的单一事实源。它不是要求用户填写的表单；由 Skill 根据对话和资料逐步维护，对用户只展示本轮新增或变化。

## 1. 最小结构

```yaml
project_id:
current_stage:
delivery_status:
product:
  target_user:
  scenario:
  problem:
  expected_outcome:
  in_scope: []
  out_of_scope: []
evidence:
  facts: []
  assumptions: []
  research_findings: []
  pending_validation: []
governance:
  decisions: []
  changes: []
  open_questions: []
  blockers: []
conversation:
  confirmed_summary: []
  turn_delta: []
architecture:
  objects: []
  roles: []
  flows: []
  states: []
  functions: []
  pages: []
  components: []
  prototype_ui_contracts: []
prototype:
  ui_profile:
  evidence_map: []
  template_fit_decisions: []
  asset_slot_contracts: []
  candidates: []
  sessions: []
  template_manifests: []
delivery:
  artifacts: []
  validation_results: []
  owners: []
  dependencies: []
  next_gate:
```

未知字段留空或标记 `pending`，不得用常识补成事实。普通回复不必完整打印 YAML；进入跨 Skill 交付、版本冻结或生产交接时才输出完整快照或其 Manifest 投影。

## 2. 证据类型

每条关键结论只能使用一种主标签：

| 标签 | 含义 |
|---|---|
| Fact | 用户原话、可观察材料或已验证系统事实 |
| Confirmed | 有权角色明确确认且已进入 DEC |
| Inference | 基于现有事实的分析推断 |
| Proposal | 可供选择的候选建议 |
| Assumption | 为推进而采用、可替换且待验证的默认 |
| Pending | 需要确认或补证据 |

截图、Figma、竞品页面和样例数据只能证明可观察内容，不能证明权限、数据来源、算法、完成规则或生产能力。

## 3. 稳定 ID 与追溯链

| 前缀 | 对象 |
|---|---|
| `OBJ-` | 业务对象 |
| `DEC-` | 决策 |
| `CHG-` | 变更 |
| `F-` | 功能 |
| `FL-` | 业务或用户流程 |
| `TR-` | 状态转移 |
| `P-` | 页面 |
| `C-` | 组件 |
| `AC-` | 验收标准 |
| `T-` | 测试 |
| `ART-` | 交付产物 |
| `PUI-` | 原型 UI Contract |
| `UIP-` | 项目 UI Profile |
| `TFD-` | 模具适配决策 |
| `ASC-` | 素材占位 Contract |
| `PTC-` | 项目级候选模具 |
| `PRS-` | 对话式原型会话 |

编号创建后不复用、不因排序变化而改变。领域已有稳定测试前缀（如 `IN-`、`TM-`、`GM-`）时可继续使用，但必须能回指 `DEC/F/TR/AC`。

用户原话或权威资料中已经确认的范围项、对象名、功能名和状态名也是稳定接口。快照、Handoff Manifest 和返回审计必须原样保留这些名称；可在后面补充解释或别名，但不得只用近义词代替，避免下游追溯和自动校验丢失。

Must 项至少形成：

```text
目标/用户任务 → DEC → F → FL/TR → P → C → AC → T → ART
```

组件不是所有功能的必经节点；系统任务或后台规则可以从页面直接追溯到 AC/T，但必须明确其系统入口。

## 4. 更新规则

- 新事实：追加来源与时间/版本，不覆盖旧证据。
- 用户确认：按 `references/decision-ledger.md` 建立 DEC；只有 `Confirmed` 可作为既定业务规则。
- 用户回改：原 DEC 标为 `Superseded`，创建新 DEC 和 CHG，并传播影响。
- 下游回传：新增 ART、验证结果和偏差；下游提出的新规则只能进入 Proposal/Pending。
- 用户研究或指标结果：进入 `research_findings`，关联样本、时间窗和置信度，再决定是否创建 DEC/CHG。
- 任何阶段只维护一个权威 `open_questions` 列表；同一问题不得在“待确认”“下一步”“风险”中重复制造三个状态。
- 每轮先更新 `turn_delta`，再将仍有效的结论压缩进 `confirmed_summary`；普通回复只展示本轮变化与一个下一问，不重复打印没有变化的历史摘要。

## 5. 快照视图

根据受众投影同一份快照，不创建平行真相：

- 产品评审：目标、范围、DEC、功能、风险和版本。
- 设计交接：页面、组件、状态、内容优先级和未决视觉项。
- 原型语义交接：PUI Contract、页面骨架、P0/P1/P2、操作层级、状态矩阵和语义/视觉边界。
- 原型项目交接：独立 UI Profile、设计证据、继承边界、模具适配、素材占位、候选模具和会话版本。
- 研发交接：对象、规则、状态、依赖、AC 和非功能要求。
- 测试交接：DEC/F/TR/AC/T 追溯与环境/数据清理。
- 运营复盘：指标、研究发现、路线图动作和待验证假设。
