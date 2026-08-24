# 原型生产 Harness

用于 S4–S6 将已 Ready 的项目 Contract 编译为确定性中保真页面，并用真实浏览器、任务路径和发布门槛验证结果。它不允许模型自由编写页面 HTML/CSS，也不把技术通过等同于目标用户通过。

## 1. 运行结构

```text
ProjectIdentity + ProjectSnapshot
  → PUI/UIP/TFD/ASC
  → Frame/Flow Contract
  → 受控 Generation Request
  → 模板路由或 project-local 候选
  → 确定性 Renderer
  → lint / render / test / report
  → Handoff Package
```

运行时资产位于 `assets/prototype-harness/`，统一入口为仓库根目录 `./harness`。项目目录必须包含 `project-identity.json`、`project-snapshot.json`、`frame-contract.json`、`flow-contract.json`、`template-fit-decision.json`、`generation-request.json` 和 `expected.json`。

## 2. 命令

```bash
./harness lint --project <project-dir>
./harness render --project <project-dir> --output <run-dir>
./harness test --project <project-dir> --output <run-dir>
./harness report --project <project-dir> --output <run-dir>
./harness all --project <project-dir> --output <run-dir>
./harness repair --project <project-dir> --output <run-dir>
./harness snapshot --project <project-dir> --event <event.json>
```

- `lint`：检查身份、字段、几何、状态可达、素材政策、组件白名单和追溯。
- `render`：只组合登记模板、项目候选、语义组件和 Slot；输出自包含 HTML。
- `test`：在真实 Chromium/Chrome 中检查溢出、遮挡、P0、唯一主操作、任务路径、恢复、异步兜底、素材政策和视觉基线。
- `report`：生成结构化错误、证据与发布结论。
- `repair`：只在运行副本中应用白名单局部修复，最多两次；不静默覆盖源 Contract。
- `snapshot`：按 `base_revision` 追加 add/replace 事件，冲突时拒绝写入。

## 3. 模板路由

模板目录只提供候选，不提供全局默认业务页面：

```text
exact       → 克隆登记模板实例并清空内容
extensible  → 克隆实例并应用声明过的插槽/区域 Patch
no_match    → 通用网格 + project-local PTC，不读取旧项目页面
```

新模具必须先作为项目候选通过结构、隔离、真实渲染和目标任务验证，再提交登记。Golden Case 是测试资产，不自动成为共享模板。

## 4. 结构化错误与有限修复

错误类型固定为：

- `CONTRACT_MISSING` / `CONTRACT_INVALID`
- `LAYOUT_OVERFLOW` / `REGION_OVERLAP`
- `FLOW_UNREACHABLE` / `STATE_MISSING`
- `PRIMARY_ACTION_INVALID`
- `ASSET_POLICY_VIOLATION`
- `TRACEABILITY_BROKEN`
- `BROWSER_UNAVAILABLE` / `VISUAL_REGRESSION`

每条错误包含对象、证据、影响、可修复性和建议动作。自动修复只处理 Contract 明确授权的 `shrink-to-safe-area` 等局部几何；语义、流程、权限、P0 和业务规则错误始终返回人工决策。

## 5. 发布硬门槛

发布候选必须同时满足：

1. Skill 结构与文档协议检查通过；
2. 所有项目 Contract lint 通过；
3. 真实浏览器无横向溢出、非预期重叠和素材违规；
4. Golden Case 主任务完整可达，恢复和异步失败有出口；
5. 截图视觉差异在声明阈值内；
6. Must 追溯链完整；
7. 目标用户证据与技术证据分开声明。

关键词、文件存在性和 Schema 文本检查只属于基础门槛，不能替代真实产物验证。

## 6. 失败回流

每个真实项目失败都要沉淀为：一个标准错误类型、一条可执行规则、一个最小复现 fixture 和一条回归测试。只修复导致失败的 Contract、模板区域或运行时规则，禁止以整页重写掩盖根因。
