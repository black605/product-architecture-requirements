# 对话式原型会话

用于需求已经达到原型门槛，且用户希望在当前对话中生成、查看和持续修改黑白低/中保真原型时。它把需求确认、模具决策、生成请求、预览、自然语言修改和变更回写保持在同一个 `PRS-` 会话中，避免一次性黑盒生成。

## 1. 启动门槛

- 当前 `ProjectSnapshot` 达到 `Ready for Prototype`；
- PUI、项目独立 UIP 和状态为 `ready` 的 TFD 已存在；
- `exact/extensible` 已创建当前项目模板实例，或 `no_match` 已存在 `ready-for-prototype` 的 PTC；
- 影响布局的素材已建立 ASC 或标记 `not_applicable`；
- 本轮原型要验证的页面、路径、状态和成功判据明确。

未满足时只说明缺少的最高影响项并继续需求对话，不生成看似完整的页面。

## 2. 会话流程

```text
建立 PRS- 会话
  → 展示生成前摘要
  → 生成受控 PrototypeGenerationRequest
  → 调用可用原型能力
  → 返回可打开预览与证据状态
  → 用户自然语言修改
  → Patch 分级与影响检查
  → 重渲染或退回 DEC/CHG
  → 验证与交接
```

### 2.1 生成前摘要

生成前必须让用户看见：

- 本轮页面和核心任务；
- 选中模具及 `exact/extensible/no_match` 结论；
- 可扩展项或候选模具范围；
- 页面骨架、P0/P1/P2 和唯一主操作；
- 素材占位及旧项目内容隔离；
- `semantic_locked`、Mock/Pending 和本轮验证目标。

摘要用于快速纠偏，不要求用户填写 Schema 或理解内部 ID。信息已在本轮确认且没有变化时不重复索要确认。

### 2.2 受控生成请求

使用 [`../schemas/prototype-generation-request.yaml`](../schemas/prototype-generation-request.yaml)。模型只填写已允许的页面、区域、组件语义、插槽、变体、状态和素材占位引用；布局和渲染由确定性的模板/组件能力完成。禁止自由生成未登记组件、任意业务动作或未经 Contract 支持的页面。

当前环境没有可用原型能力时，只输出完整 Generation Request 与 Handoff Manifest，状态保持 `ready-to-generate`，不能声称页面已生成。

## 3. 自然语言 Patch

用户可以直接说“把重点卡片放到练习前”“这里增加图片占位”“错误时给重试入口”。每次修改记录：

| 字段 | 要求 |
|---|---|
| `patch_id` | 稳定编号和基线版本 |
| `user_intent` | 用户原话或准确摘要 |
| `tier` | L1 / L2 / L3 |
| `targets` | 页面、区域、Slot、状态或 Contract |
| `before/after` | 结构化变化，不只保存截图 |
| `impact` | PUI、UIP、TFD、PTC、ASC、AC、测试和产物 |
| `result` | applied / needs-decision / rejected / conflicted |

- L1：间距、密度、占位标签、样例长度等可逆表达，可直接 Patch 并提供回改入口。
- L2：区域顺序、可选插槽、允许变体和状态表达，可在 Contract 范围内 Patch，并重新执行适配和压力检查。
- L3：主任务、P0、权限、收费、算法、完成/解锁、数据语义和验收口径，创建 DEC/CHG，相关 TFD/原型版本降级并退回上游。

Patch 必须匹配当前基线版本；冲突时保留候选分支，不静默覆盖后来的用户修改。

`applied` 表示结构化 Contract 与 Generation Request 已更新，并立即递增其版本；下一次 Patch 必须以这个新 Contract 版本为基线。若当前没有重渲染能力，产物版本保持旧值或 `unavailable`，分别显示 `contract_version` 与 `artifact_version`，不得因为产物未更新而让 Contract 版本停留在旧基线，也不得声称页面已生成。

### 3.1 用户可见 Patch 回执

每次原型回改至少显示四项，不能只复述新页面效果。首行的等级和结果必须使用下列枚举原文，不用“已记录、暂定、处理完成”等词替代：

```text
PATCH-ID｜L1/L2/L3｜vX.Y｜applied/needs-decision/conflicted/rejected
变化：目标区域或规则的 before → after
影响：PUI/UIP/TFD/PTC/ASC/AC/测试/产物中的适用项
状态：PRS-ID｜contract_version｜artifact_version/退回 DEC/CHG 的原因
```

首行第三段只允许当前 Contract 基线版本，例如 `v0.2`；不得写 `PRS-ID / v0.2`、页面名或“当前评审基线”。

若 L3 表达包含“看完、有效、完成、自动、可见”等尚未定义的触发或口径，首行结果固定为 `needs-decision`，第二行固定登记 `DEC-ID / CHG-ID｜Proposed/Blocked`；无法分配正式编号时使用 `DEC-待登记 / CHG-待登记`，不得省略。保留旧 Confirmed 规则；不得先说“已确认改为”再追问定义。涉及新权限或新数据可见范围时，不先把入口写成暂定页面方案。

## 4. 版本与证据状态

`PRS-` 使用：`draft / ready-to-generate / generated / in-review / validated / blocked / superseded`。这些状态分别记录：

- Generation Request 已准备；
- 文件或预览真实生成；
- 页面可打开且技术行为通过；
- 目标用户任务是否验证；
- 交接审计是否完成。

“generated”只证明产物存在；不能替代技术回归、目标用户验证或生产部署。

## 5. 返回审计

每次生成或 Patch 返回后检查：

1. 预览是否使用当前项目实例、Profile、TFD/PTC 和 ASC；
2. P0、唯一主操作、关键状态和异常出口是否保留；
3. 页面是否混入旧文案、资产、用户数据或未确认规则；
4. 每个变化是否记录 Patch、版本和影响；
5. 新业务规则是否正确退回 DEC/CHG；
6. 输出路径、可打开性、Mock 边界和验证状态是否真实。

## 6. 验收

- 原型生成前的关键决策对用户可见；
- 生成请求只引用允许的模板、组件、Slot、状态和变体；
- 用户可用自然语言修改，不需要手工编辑 Schema；
- L1/L2 修改可回退，L3 修改不会在页面中静默生效；
- 每次预览都绑定 `PRS-`、基线版本和 Patch 历史；
- 连续修改测试必须在同一正式运行时会话中执行，证明前一轮 `PRS-`、基线版本和 Patch 结果能被下一轮正确承接；
- 没有可用生成能力时不伪造原型完成状态。
