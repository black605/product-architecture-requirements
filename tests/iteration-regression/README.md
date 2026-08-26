# A2UI 工业化路线 · 正式 Skill 回归记录

本目录保存 `product-architecture-requirements` 每轮优化后的独立正式运行时记录。每条记录由 `run_formal_platform_50.py` 通过 Codex CLI 的 ephemeral、read-only 会话生成，非人工拼接回复。

## 结果总览

| 版本 | 优化能力 | 正式案例 | 通过 | 记录目录 |
|---|---|---:|---:|---|
| v2.8.0 | A2UI 输入与决策协议 | 20 | 20 | `v2.8.0/` |
| v2.9.0 | 防御性 UI Contract | 20 | 20 | `v2.9.0/` |
| v3.0.0 | Studio Patch Bridge | 20 | 20 | `v3.0.0/` |
| v3.1.0 | Runtime Quality Gate | 20 | 20 | `v3.1.0/` |
| v3.2.0 | Asset Bundle Handoff | 20 | 20 | `v3.2.0/` |
| **合计** |  | **100** | **100** |  |

执行日期：2026-08-20。正式运行模型由各轮 `run-summary.json` 记录；本轮为 `gpt-5.6-luna`。

## 每条记录的硬性检查

- 独立 Codex CLI 会话执行成功；
- 存在最终回复；
- 提问数不超过 2；
- 回复含已知事实、暂定假设或待确认等不确定性标签；
- 未输出后端/设计源文件实现代码。

这些检查验证 Skill 的运行约束和基础交互边界，不证明真实 A2UI Runtime、Schema 服务、Catalog、Bit、目标应用消费或生产部署已经存在。相应状态仍必须由 `a2ui-runtime-audit`、`a2ui-runtime-register`、`a2ui-bit-lifecycle` 或 `a2ui-component-release` 的实际证据验证。

## 补充完整交付回归

在五轮 20 例批次之外，已重跑跨 Skill 完整交付用例 D：`tests/gomoku-case-d/result.json` 为 `passed: true`，四维评分 100/100。该回归核验 DEC/CHG、状态机、Handoff Manifest、三类真实下游产物的 Blocked 判定，以及只读审计的外部动作边界。它仍不把下游产物的 Blocked 状态说成生产完成。

## 可重复执行

```bash
python3 tests/run_formal_platform_50.py \
  --rounds 1-20 \
  --expect-count 20 \
  --workers 4 \
  --output tests/iteration-regression/<version>
```

使用新的输出目录，避免历史记录与本轮结果混合。`--expect-count` 默认等于选中的轮次数，因此同一运行器既支持完整 50 轮，也支持本路线要求的 20 轮批次。
