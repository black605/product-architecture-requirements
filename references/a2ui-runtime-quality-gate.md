# A2UI Runtime Quality Gate

本规范定义从已确认意图到受控 A2UI 组件候选的需求级质量闸门。它不替代真实运行时审计，也不声称某个服务、Zod Schema、Renderer 或部署已存在。

## 1. 受控路径与证据状态

```text
Intent / DEC
  → Route Policy
  → Catalog Match
  → Candidate Envelope
  → Normalize
  → Schema Gate
  → Repair（有限）
  → Registry / Renderer
  → Fallback 或 User-visible Result
```

每层分别记录 `planned / locally-verified / runtime-verified / production-verified / unavailable`。前一层存在文档或代码，不能推导后一层已经通过。

## 2. Schema Gate

| 检查 | 必须验证 | 拒绝后的处理 |
|---|---|---|
| 结构 | 顶层对象、稳定 ID、版本、必填 Slot | 返回结构化校验错误 |
| 枚举 | variant、模板、动作类型来自 allowlist | 不允许自由字符串降级为可渲染组件 |
| Slot | P0 必填、P1/P2 与坍缩规则一致、长度/数量满足 Contract | 指向对应 Contract/Slot 规则 |
| Action | payload 属于允许策略，失败/重试边界存在 | 禁止未知动作进入 Renderer |
| Asset | assetId、alt、fallback、比例/安全区（适用时） | 使用已声明 fallback，不生成任意资产路径 |
| Policy | 页面模板、角色/范围、Registry 允许该 Variant | 拒绝并给出不泄露策略细节的 fallback |

## 3. 有限自愈

自愈是对候选 Envelope 的结构修复，不是重新猜测业务需求。

- 只回传脱敏后的结构化错误码、字段路径、允许枚举和值域；不得回传密钥、完整用户数据或内部策略。
- 最大尝试次数、超时和成本预算必须在 Handoff 中声明；默认建议不超过 2 次修复。
- 修复可补齐 L1 格式性缺失或选择允许的 fallback；不得自行确认 L3 决策、创建新 Variant 或改变业务状态。
- 任一修复后必须重新执行完整 Schema Gate；超过上限、策略拒绝或依赖不可用时 fail closed。

## 4. Catalog Match First

| 结果 | 行为 | 禁止事项 |
|---|---|---|
| `exact` 完全匹配 | 使用已注册 component/variant/模板组合 | 不覆盖 Slot 约束 |
| `extensible` 可扩展匹配 | 在明确扩展点和适配规则下映射并记录依据 | 不把近似视觉相似当作兼容 |
| `no_match` 无匹配 | 返回候选或创建受控注册 Handoff | 临时插入 Catalog/Registry 或渲染未注册组件 |
| 策略拒绝 | 显示允许的 fallback，并记录拒绝类别 | 暴露权限/安全策略详情 |

Catalog 缓存的键必须至少包含 component、variant、模板、协议版本和适用范围；缓存命中只说明候选复用，不证明资产、服务或部署状态。

Runtime 的 Catalog Match 必须继承上游 `TFD-`，不能在运行时把原型阶段的 `no_match` 静默改成可用模板。

## 5. Fallback 与用户可见反馈

fallback 必须保留当前用户可理解的核心结果或下一步，且不能假装渲染成功。最低字段：`reason_category`、`safe_message`、`retry_allowed`、`next_action`、`correlation_id`（如允许记录）。对敏感数据仅展示最小必要信息。

## 6. 运行时 Handoff 与审计

Handoff 至少包含：Route Policy、Catalog/Schema/Template/Registry 预期 ID、允许 Action、修复上限、Fallback、资产回退、会话连续性边界、日志脱敏规则和验收证据。真实运行前后使用 `a2ui-runtime-audit` 分别核验本地 Preview、服务响应和生产路由；没有证据时保持 `unavailable`。
