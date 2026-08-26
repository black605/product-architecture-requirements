# 项目 UI Profile 与证据输入

用于页面规格进入原型前，为当前项目建立独立的 UI 上下文。它回答“本项目的用户、任务、页面与设备约束是什么、哪些设计证据可以继承”，不负责选择具体模具，也不把 Figma、截图或旧页面中的内容推断为业务事实。

## 1. 触发条件

出现以下任一情况时，在生成原型或选择设计系统 Profile 前建立 `ProjectUIProfile`：

- 用户提供 Figma、截图、旧页面、母版、设计规范或历史原型；
- 用户要求生成低保真、中保真、页面框架或可交互原型；
- 当前项目可能复用既有页面结构、模具、组件或设计系统；
- 新项目与历史项目属于相似业务，但目标用户、任务或设备可能不同。

每个 `project_id` 必须拥有独立 `profile_id`。历史项目 Profile 只能作为证据来源，不能直接成为当前项目的权威状态。

## 2. 证据映射

对每个 Figma 节点、截图、页面或规范记录：

| 字段 | 要求 |
|---|---|
| `evidence_id` | 稳定编号，例如 `EVD-UI-001` |
| `source_type` | `figma-node / screenshot / existing-page / written-spec / user-confirmation` |
| `source_ref` | 文件、URL、节点 ID 或用户原话引用 |
| `observed` | 只记录可观察的布局、尺寸、区域、组件和状态 |
| `derived_constraints` | 从证据推导的候选约束，标记 `Inference` 或 `Proposal` |
| `confidence` | `high / medium / low / unavailable` |
| `verification_status` | `verified / pending / inaccessible / superseded` |

Figma 或外部资料暂时无法访问时，只记录引用与 `inaccessible`，不得根据链接标题编造栅格、卡片尺寸或组件内容。截图和页面不能证明权限、算法、完成条件、数据来源或生产能力。

## 3. Profile 最小内容

`ProjectUIProfile` 至少包含：

- 项目与 Profile 身份：`project_id`、`profile_id`、版本和状态；
- 目标用户、核心任务、页面类型、P0/P1/P2 信息层级；
- 必需区域、主操作、关键状态、目标设备与视口；
- 允许继承的结构证据与禁止继承的内容；
- 已确认、候选、待验证和不可访问的证据；
- 对应 `PUI-`、页面、功能和决策的追溯。

详细结构使用 [`../schemas/project-ui-profile.yaml`](../schemas/project-ui-profile.yaml)。未知字段保留 `pending`，不能复制旧项目值补齐。

## 4. 项目隔离与继承

默认允许作为候选继承：

- 栅格、区域关系和页面骨架；
- 通用组件语义、插槽结构与状态表达；
- 已验证且适用于同类设备的可访问性和响应式约束。

默认禁止继承：

- 旧项目文案、样例数据、用户信息和业务名称；
- 图片、插画、图标、音频、视频和品牌资产；
- 品牌色、字体、圆角、阴影和专属 Token；
- 权限、算法、评分、收费、完成、解锁和数据来源规则。

只有用户或权威设计规范明确授权，并记录来源、范围和版本后，禁止项才能转为当前项目的可用证据。即使允许继承，也必须复制为当前项目实例，不能共享可变状态。

## 5. 与 PUI、DS 和模具的关系

```text
产品需求与页面规格
  → PUI Contract：页面必须表达什么
  → ProjectUIProfile：本项目适用的用户、任务、设备和证据边界
  → 模具适配：判断是否存在可复用结构
  → DS Contract：需要时定义组件与 Token 语义
  → 原型生成
```

`ProjectUIProfile` 不是模具、品牌方案或设计系统。它是后续模具适配、候选生成和原型交接的项目级输入。

## 6. 验收

- 当前项目拥有独立 `project_id` 与 `profile_id`；
- 每条外部设计规则可回指证据来源和访问状态；
- 旧项目文案、视觉资产和业务规则默认禁止继承；
- 用户、任务、页面类型、信息层级、区域、设备和状态缺口显式保留；
- Profile 可回指 PUI、页面、功能和 DEC，不建立第二份产品真相；
- 外部资料不可访问时没有伪造提取结果。
