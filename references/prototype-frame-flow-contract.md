# 可执行 Frame / Flow Contract

用于把 PUI 的页面语义编译为可机械校验的空间和行为约束。PUI 继续回答“必须表达什么”，Frame Contract 回答“区域在目标视口如何成立”，Flow Contract 回答“任务、状态和恢复如何可达”。

## 1. Frame Contract

结构使用 [`../schemas/frame-contract.yaml`](../schemas/frame-contract.yaml)，至少包含：

- 目标 viewport、方向、safe area 与网格；
- 每个 region 的 `x/y/width/height`、最小/最大尺寸；
- `fixed / flow / overlay / scroll` 定位模式；
- z-index、overflow、滚动、允许重叠对象和局部修复策略；
- P0 区域、唯一主操作区域、素材 Slot 与 PUI/页面追溯。

`ready` 的 Frame 必须满足：非 overlay 区域不越界、不意外重叠；P0 与主操作在目标视口可见；滚动容器明确；极端内容不会把主操作推出安全区。像素值是当前原型视口的可执行约束，仍属于 `prototype-only`，不等于最终视觉 Token。

## 2. Flow Contract

结构使用 [`../schemas/flow-contract.yaml`](../schemas/flow-contract.yaml)，至少包含：

- 唯一初始状态和明确终态；
- 页面/步骤、进入条件、事件、守卫、目标状态与失败出口；
- 返回、取消、恢复位置和跨设备/断网策略；
- loading、listening、generating、timeout、fallback、completed 等适用状态；
- 异步状态的超时、重试上限、fallback 和可观察反馈；
- 每条 Must 转移与 DEC/F/P/AC/T 的追溯。

`ready` 的 Flow 必须满足：所有 Must 状态从初始状态可达；非终态存在合法出口；异步状态存在超时与 fallback；恢复指向具体状态或步骤，不能只写“继续学习”。

## 3. 编译与失败规则

```text
PUI + UIP + TFD + ASC
  → Frame Contract + Flow Contract
  → Schema/语义校验
  → 受控 Generation Request
  → 确定性渲染
```

出现以下任一错误时，不得进入原型生成：缺少 Contract、项目身份不一致、viewport 非数值、P0 无区域、主操作不唯一、状态不可达、异步无兜底、禁止素材进入请求或追溯断裂。

## 4. 变更分级

- L1：间距、可逆密度和样例内容，可修改 Frame 实例并重渲染。
- L2：区域比例、可选区块和恢复反馈，修改 Frame/Flow 后必须重跑任务验证。
- L3：主任务、P0、权限、完成规则、收费或算法语义，先创建 DEC/CHG 并退回上游。

任何自动修复只能作用于明确标记 `repairable` 的局部几何，最多两次；不得自动修改 L3 语义。
