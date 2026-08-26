# A2UI Studio Patch Bridge

Studio 是可视化修改与预览界面；本协议让 GUI 修改成为可审计的结构化差异，而不是新的隐式需求来源。它适用于 Slot、Token、变体和压力预设的受控调整。

## 1. 数据流

```text
IntakeEnvelope + DecisionEnvelope + UI Contract
  → 受控 Preview Spec
  → Studio 操作
  → OverridePatch
  → 版本/策略校验
  → 预览结果 + Contract/DEC/CHG 回写
```

Preview 只能证明当前 Contract 在指定输入下被渲染；它不能证明组件已注册、真实接口可用、生产构建通过或用户测试达标。

## 2. OverridePatch

| 字段 | 要求 |
|---|---|
| `patch_id` | 稳定 ID，如 `OVR-001` |
| `baseline` | `intake_id`、`contract_id`、基线版本和对象 ID |
| `actor` | `product / design / system`，不记录个人敏感信息 |
| `operations` | 仅使用允许的操作类型 |
| `tier` | L1 / L2；L3 不生成可应用 Patch |
| `rationale` | 修改原因或关联验证信号 |
| `rollback_to` | L2 必须指向可恢复版本 |
| `verification` | 预览视口、压力用例 ST-ID、结果与未通过项 |
| `decision_link` | 关联 DEC/CHG；L3 必须为 Needs Decision |

允许的 `operations`：

| 操作 | 例子 | 边界 |
|---|---|---|
| `select_variant` | 在 Catalog 允许的 variant 间选择 | 不能创建新 wire ID |
| `set_slot_visibility` | 显示/隐藏 P2 Slot | P0 不能被隐藏；必须满足坍缩规则 |
| `set_slot_order` | 调整 P1/P2 展示顺序 | 不能改变已确认业务流程 |
| `set_slot_priority` | P1 降为 P2 | 不能把 P0 降级；影响理解时需理由 |
| `set_token_alias` | `space.md → space.lg` | 仅已登记 Token，不能填任意 CSS 值 |
| `select_stress_preset` | 选择 ST-01 超长标题 | 只能引用 Contract 已登记 ST-ID |

## 3. 不允许由 Studio 直接修改的内容

以下操作必须创建或修改 DEC/CHG，并在确认后才可能进入新的 Contract/Preview：权限、角色、价格、支付、隐私收集、数据字段语义、学习完成/解锁、评分、推荐规则、对象状态转移、接口/模型承诺、验收口径。

## 4. 版本与冲突

- Patch 应用前必须匹配基线版本；不匹配时显示冲突，不执行静默覆盖。
- 同一 Slot/Token 的并行 Patch 保留为候选分支，由 Owner 选择或合并；不可合并时创建 CHG。
- L1 可直接生成 Draft 版本；L2 必须保留回退点和变更摘要；L3 只能产生 Needs Decision。
- Patch 应用后重跑它引用的 ST-ID；失败时回退或标记 Blocked，不能只保留正常态截图。

## 5. Studio 面板建议

| 面板 | 读取 | 可修改 | 输出 |
|---|---|---|---|
| Slots | Contract Slot 与 P0/P1/P2 | P1/P2 显隐、顺序、优先级 | `OverridePatch.operations` |
| Tokens | 已登记语义 Token | Token alias | 可逆 Patch |
| Stress | 已登记 ST-ID 与预期 | 选择预设 | 验证结果 |
| Decisions | L1/L2/L3 决策 | 仅查看 L3，跳转确认 | DEC/CHG 链接 |
| Preview | 受控 Preview Spec | 不直接编辑业务数据 | 视口与渲染结果 |

## 6. Handoff 回填

下游 Studio/Preview 返回时至少回填 Patch、基线版本、预览输入、视口、ST-ID 结果、回退点、失败项及对应功能/组件。需要 Runtime 组件注册时，继续走 `a2ui-runtime-register`；Studio 成功不能被标为 runtime-registered 或 deployed。
