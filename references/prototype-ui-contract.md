# 原型 UI Contract

用于 S3「规格生成」到 S4「中保真交互线稿」之间的页面语义交接。它把页面结构、信息优先级、操作层级、组件语义和关键状态冻结为可评审约束，再交给原型能力表达。

本 Contract 是需求级页面协议，不是最终视觉稿、前端组件实现、设计系统、A2UI Runtime Contract、Registry 注册记录或生产代码。它回答“页面必须表达什么、用户必须能完成什么、状态必须如何反馈”，不锁死品牌色、字体、插画和实现方式。

## 1. 触发条件与阶段门槛

以下任一情况发生时，在进入中保真原型前建立 Prototype UI Contract：

- 已完成页面清单，需要验证页面骨架、信息层级或操作路径；
- 用户要求做中保真、交互原型、页面高保真前置稿或设计交接；
- 页面包含多区域布局、多个主操作、状态反馈、权限差异或异常恢复；
- 现有截图、Figma、页面原型或旧产品结构需要被继承、拆解或重构。

达到 `Ready for Prototype` 前，每个 Must 页面至少需要：

1. 页面目标、目标角色、进入条件、主任务和出口；
2. 顶栏、侧栏、内容区、工具区、浮层等区域关系；
3. P0/P1/P2 信息优先级；
4. 主操作、次操作、危险操作、返回/取消路径；
5. 加载、空、错误、无权限、禁用、部分数据和极端内容的处理；
6. `semantic_locked`、`visual_flexible`、`pending_decisions` 和 `forbidden_assumptions`；
7. 页面与功能、决策、验收标准的追溯关系。

若高影响业务规则仍未确认，只交付 Draft 或阻塞表，不用 Contract 或原型外观替代决策。

## 2. Contract 的六类职责

### 2.1 页面骨架

定义区域之间的关系和页面空间职责；PUI 不规定最终像素值，进入原型时由 Frame Contract 为目标视口提供可执行几何：

- 顶栏：全局身份、全局导航、页面级上下文或全局操作；
- 侧栏/标签区：模块导航、视图切换或筛选入口；
- 内容区：完成页面主任务所需的核心信息和操作；
- 工具区：筛选、批量操作、排序、视图切换或辅助操作；
- 浮层/抽屉/弹窗：临时任务、确认、详情或局部编辑；
- 状态反馈区：加载、错误、成功、权限和恢复提示。

每个区域要说明 `purpose`、内容优先级、进入条件、退出方式和是否固定/滚动。不能只列“有一个侧栏”，还要说明侧栏承载什么业务语义。

### 2.2 信息层级

对字段、区块和反馈划分：

- `P0`：缺失会使主任务无法理解、开始或完成；
- `P1`：帮助判断、补充操作或提高效率，但主任务仍可在缺失时保留；
- `P2`：辅助信息、扩展操作或低频内容，可折叠、省略或延后加载。

P0 缺失不得渲染为成功态；P1 缺失保留稳定主结构并说明替代表现；P2 缺失自动坍缩，不留下无意义空白。字段来源、缺失行为和最长内容应在组件或页面状态中注明。

### 2.3 操作层级

定义用户在页面上“先做什么、还可以做什么、哪些操作有风险”：

- `primary`：当前页面唯一主任务对应的主操作；
- `secondary`：查看、筛选、保存、继续等辅助操作；
- `destructive`：删除、撤回、下线、重置等有损或不可逆操作；
- `cancel_or_back`：取消、返回、关闭和恢复上一状态的路径。

同一页面不能出现两个无法区分优先级的同级主操作。危险操作必须说明确认、撤销、权限和失败后的可见反馈；返回或取消不能静默丢失已输入内容。

### 2.4 原型组件语义

组件名称只表示承载的业务语义，不代表已经选定技术库或完成组件注册。例如：

| 原型组件语义 | 可以承载的业务含义 | 不应静默决定的内容 |
|---|---|---|
| Card | 一个内容对象、任务或状态摘要 | 点击后一定进入详情还是直接开始 |
| List/Table | 多个对象的比较、筛选或批量管理 | 排序权威、分页规则或数据来源 |
| Form | 创建、编辑或提交业务对象 | 必填规则、保存时机和校验口径 |
| Modal/Drawer | 临时确认、局部编辑或上下文详情 | 是否允许绕过当前流程或改变权限 |
| Tabs/Segmented | 已确认的同级视图或内容分区 | 各视图是否共享筛选、状态和数据 |
| Alert/Toast | 业务结果、风险提示或恢复建议 | 用提示替代页面内关键状态 |
| Empty/Skeleton/Error | 数据尚未可见、没有结果或加载失败 | 把失败或空数据伪装成正常态 |

### 2.5 页面状态

至少为适用页面定义以下状态：

- `loading`：数据或页面正在准备；
- `empty`：尚未创建、筛选无结果或没有可展示数据；
- `error`：加载、提交或外部依赖失败；
- `no_permission`：已识别身份但没有访问或操作权限；
- `disabled`：操作存在但因前置条件、状态或权限暂不可用；
- `partial_data`：部分区域可用，部分区域等待、失败或无数据；
- `extreme_content`：长文本、字段缺失、极值、超多标签或大批量数据。

每个状态都必须有可观察表现和用户下一步：重试、返回、申请权限、继续、重新开始、查看原因或等待。若某状态不适用，写明原因，不能仅删除字段。

### 2.6 上下游边界

Contract 输出三类边界：

- `semantic_locked`：最终设计、原型实现和研发必须继承的页面任务、信息优先级、主次操作、字段含义、状态和异常出口；
- `visual_flexible`：最终设计可以替换的品牌色、字体、圆角、阴影、插画、图标和动效风格；
- `pending_decisions` / `forbidden_assumptions`：仍需业务确认或禁止下游自行决定的权限、数据来源、算法、收费、完成/解锁和验收规则。

下游可以重做外观，但不得静默改变 `semantic_locked`；如果交互变化会改变业务语义，必须创建 DEC/CHG 并退回对应阶段。

## 3. 默认展示规范：`prototype-neutral`

`prototype-neutral` 只用于统一原型展示、控制信息密度和支撑评审，不是品牌设计方向。下游可以替换全部视觉值，但不能借此改变语义、层级和状态。

```yaml
prototype_style:
  name: prototype-neutral
  purpose: 原型展示，不是最终视觉设计
  status: prototype-only

  color:
    background: 中性浅灰
    surface: 白色
    text: 深灰
    primary_action: 单一蓝色
    semantic: 成功/警告/错误使用语义色

  typography:
    page_title: 24
    section_title: 18
    body: 14
    auxiliary: 12

  spacing:
    base: 4
    common: [8, 12, 16, 24, 32]

  radius:
    control: 6
    card: 8

  decoration:
    gradients: 禁止
    illustration: 非必要不使用
    shadow: 只用于层级区分
    animation: 只表达状态与反馈
```

样式规则的验收重点是：层级可读、状态可区分、主操作明确、长内容不破坏结构、键盘/触控有可操作路径。它不要求最终品牌插画、最终 Token、生产动画或正式组件库。

## 4. 标准数据结构

以下结构可写入 ProjectSnapshot、Handoff Manifest 或单独的 `.md`/`.yaml` 文件。`PUI-` 是 Contract 的稳定 ID；页面、组件、功能和决策继续使用已有 `P-`、`C-`、`F-`、`DEC-` ID。

```yaml
prototype_ui_contract:
  contract_id: PUI-001
  version: v0.1
  fidelity: medium
  status: draft # draft / ready / superseded / blocked

  context:
    platform: desktop
    viewport: 1440x900
    primary_user:
    primary_task:
    ui_profile_id:

  template_fit:
    decision_id:
    result: pending # exact / extensible / no_match
    selected_template_id:

  prototype_candidate:
    candidate_id:
    asset_slot_contracts: []

  executable_contracts:
    frame_contract_id: FRM-001
    flow_contract_id: FLOW-001

  page:
    page_id: P-001
    purpose:
    entry:
    exit:
    regions: [] # 语义区域；像素几何位于 Frame Contract

  information_hierarchy:
    p0: []
    p1: []
    p2: []

  action_hierarchy:
    primary:
    secondary: []
    destructive: []
    cancel_or_back:

  components:
    - component_id: C-001
      semantic_role:
      required_fields: []
      optional_fields: []
      actions: []
      variants: []
      states: []

  state_matrix:
    loading:
    empty:
    error:
    no_permission:
    disabled:
    partial_data:
    extreme_content:

  handoff:
    semantic_locked: []
    visual_flexible: []
    pending_decisions: []
    forbidden_assumptions: []
```

字段为空时必须标记 `pending` 或 `not_applicable`，不得用示例内容伪造已确认规则。`status: ready` 只能在页面目标、主任务、信息层级、操作层级和适用状态均有依据时使用。

## 5. 运行流程与最小输入

| 步骤 | 最小输入 | Skill 输出 |
|---|---|---|
| 1. 页面范围 | 产品目标、用户、核心任务 | 页面清单与页面目标 |
| 2. 页面骨架 | 截图、Figma、已有页面或口述结构 | 顶栏、侧栏、内容区、工具区和浮层关系 |
| 3. 信息分级 | 页面字段、真实样例内容或内容类型 | P0/P1/P2 与缺失行为 |
| 4. 操作分级 | 用户要完成的任务、危险操作和返回需求 | 主次操作、确认、取消和恢复路径 |
| 5. 状态补全 | 已知异常、权限和业务状态 | 页面状态矩阵与测试输入 |
| 6. 原型表达 | 目标设备、视口、密度和旧页面继承约束 | 独立 `UIP-` 与 `prototype-neutral` 展示边界 |
| 7. 模具适配 | PUI、UIP 与允许范围内的模板目录 | `TFD-`、逐项匹配依据和 exact/extensible/no_match |
| 8. 中保真输出 | Contract、目标页面和验证目标 | 可评审中保真交互线稿 |
| 9. 下游交接 | 目标角色和下游产物 | 语义锁定、视觉可变、待确认与禁止推断清单 |

用户最少只需提供：产品面向谁、用户在页面完成什么、页面/截图/Figma、目标设备尺寸、主要字段和操作、是否继承现有页面结构。其余信息由 Skill 逐轮提取，每轮最多询问一个关键问题。

## 6. 与中保真原型和下游能力的关系

```text
S3 功能/页面规格
  → PUI Contract（语义、层级、操作、状态）
  → UIP + TFD（项目隔离、证据与模具适配）
  → Frame/Flow Contract（可执行几何、状态与恢复）
  → S4 中保真交互线稿（可操作表达）
  → S5 技术/用户/交接验证
  → S6 设计、研发、测试交接
```

- 中保真原型可以调整低风险布局、文案和视觉候选，但必须保留 Contract 的语义锁定项；
- 原型发现新的业务规则时，创建 DEC/CHG，降低受影响交付状态并退回对应阶段；
- 最终视觉设计可以替换 `visual_flexible`，不能静默改变 `semantic_locked`；
- 需要 A2UI 输入、Studio、Runtime 或 Asset Bundle 时，Contract 作为上游需求语义输入，仍须遵守对应 A2UI 专项协议；
- 当前 Contract 不涉及生产组件库、Registry、MCP、接口实现或部署状态。

## 7. 验收清单

- 每个页面能回指至少一个功能和用户任务；
- 每个原型组件都有明确业务语义、字段来源和适用状态；
- 每个页面只有一个可识别的主操作；
- 返回、取消、危险操作和失败恢复有明确路径；
- 加载、空、错误、无权限、禁用、部分数据和极端内容状态有出口；
- `prototype-neutral` 被标记为 `prototype-only`，不会被误认为品牌设计；
- 最终设计能区分必须继承的语义和可以重做的视觉；
- 未确认的权限、数据、算法、收费、完成/解锁和验收规则仍保持 Pending；
- Contract、页面、功能、DEC、AC 和验证任务可以相互追溯；
- Ready 页面拥有同项目、同 revision 的 Frame/Flow Contract，且 lint 通过；
- 没有把 Contract 当成生产组件注册、前端实现或上线证据。
