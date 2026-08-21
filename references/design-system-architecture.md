# 设计系统与学习组件架构协议

用于把已确认的页面语义转成可复用的设计系统输入与工程交接。它适用于用户明确要求组件规范、设计系统、设计到代码或可复用前端基础时；不替代 `Prototype UI Contract`，也不在需求尚未 Ready 时提前决定技术栈。

## 1. 分层与边界

设计系统按三层表达，并用 AI 可读取的 Contract 描述布局、插槽和变体，避免把开源库、品牌视觉和业务规则混成一件事：

```text
基础层：shadcn/ui 的开放组件模式 + Radix Primitives 的可访问交互
  ↓
产品层：项目 Token、版式、文案密度与通用组合件
  ↓
领域层：由已确认用户任务和业务规则派生的业务组件
```

- **基础层**解决 Button、Card、Badge、Progress、Dialog、Tabs、Toast、Skeleton、Empty 等通用交互与可访问性，不承载课程完成、权限、评分或解锁规则。
- **产品层**定义语义 Token 和组件变体。颜色、字体、圆角、阴影、插画和动效属于 `visual_flexible`，除非用户已确认品牌规范。
- **领域层**只在功能、状态、字段和验收已经有依据时产生。它可以组合基础组件，但不能以“组件命名”静默补全业务逻辑。

AI 读取设计规范时，优先识别这些结构化字段：`layout_pattern`、`regions`、`slots`、`variants`、`compound_variants`、`states`、`responsive_rules`、`token_refs`、`traces_to`。字段缺失时标记 `pending`，不通过截图或组件名称自行推断。

`shadcn/ui` 是“把可修改组件源码放进项目”的分发方式，Radix 是可访问行为基础；只有用户要求工程接入且当前项目具备对应前端上下文时，才交给 `$shadcn` 或前端实现能力执行安装、注册或代码改动。当前 Skill 只交付规范和映射，不声称组件已经安装或可运行。

## 2. 触发与选择

当出现以下任一请求时读取本协议：

- 用户要求统一设计规范、组件库、Token、设计到代码或前端交接；
- 中保真原型需要从 `prototype-neutral` 升级为已确认的产品 Profile；
- 页面包含反复出现的卡片、状态、导航、表单或反馈模式，需要判断复用边界；
- 用户明确指定 shadcn/ui、Radix、Ant Design、MUI 或已有内部组件库。

先确认或继承以下最小上下文：目标端、产品类型、已有品牌/组件约束、要复用的页面范围。若技术栈未确认，输出“候选基础层”，不能把 React、Tailwind、Radix 或任一包名写成既定研发约束。

默认路由：

| 场景 | 候选基础层 | 领域层策略 |
|---|---|---|
| C 端学习、内容或工具端，需高度自定义 | shadcn/ui + Radix + Tailwind Variants | 建立项目专属学习/内容组件 Profile |
| 教师、运营、内容配置后台 | Ant Design + ProComponents；已有 Material 体系时可选 MUI | 以布局、表单、表格、筛选、审核与权限组件为主 |
| 严格多部件插槽、复合变体或跨框架行为 | Park UI + Ark UI + Panda CSS | 用 anatomy、slot recipe 和 compound variant 描述结构与变体 |
| 用户已有设计系统 | 继承已有库与 Token | 只补缺失的领域组件，不重建基础层 |

这是默认候选而非确认结论；项目可因现有技术栈、团队能力或品牌组件库而改变。

## 2.1 AI 可读的布局与组件 Contract

设计、原型和研发交接统一使用以下字段。它描述“组件由什么组成、如何变体、在什么状态下呈现”，不等于实现代码：

```yaml
ai_ui_contract:
  contract_id: DS-001
  target_surface: teacher-console
  foundation: ant-design
  layout:
    layout_pattern: app-shell
    regions:
      - id: header
        purpose: 全局身份与页面级操作
      - id: sider
        purpose: 模块导航
      - id: content
        purpose: 当前主任务
    responsive_rules: [desktop-landscape, collapse-sider-below-lg]
  component:
    name: CourseCard
    semantic_role: 课程内容对象摘要
    slots: [root, cover, badge, title, meta, progress, actions]
    required_slots: [root, title, actions]
    variants:
      density: [comfortable, compact]
      status: [default, featured, locked, completed]
    compound_variants:
      - when: {status: locked, density: compact}
        effect: actions_disabled
    states: [loading, empty, error, disabled]
    token_refs: [surface, foreground, primary, spacing-md]
    traces_to: [F-001, P-001, AC-001]
  boundary:
    semantic_locked: [课程主任务, 状态含义, 主操作]
    visual_flexible: [颜色, 字体, 圆角, 阴影, 插画]
    pending_decisions: []
    implementation_authorized: false
```

`layout_pattern` 描述页面级骨架，如 `app-shell`、`dashboard`、`content-detail`、`split-pane`；`regions` 描述区域职责；`slots` 描述组件内部插槽；`variants` 描述单一变体轴；`compound_variants` 描述组合条件。变体不能替代权限、完成、评分、解锁或数据规则。

## 3. SpeakUp 学员端 Profile

当产品是面向儿童或学生的口语/课程学习端，且用户选择该 Profile 时，使用以下名称和复用边界。`SpeakUp` 是该 Profile 的名称，不是所有教育产品的默认品牌。

### 3.1 基础组件映射

| 基础组件 | 用途 | 领域组件可组合它的方式 |
|---|---|---|
| Button | 唯一主操作、次操作、返回和危险操作 | 继续学习、开始跟读、再次练习、查看结果 |
| Card | 信息对象和任务分组 | 课程单元、词汇、场景任务、学习结果 |
| Badge | 短状态标识 | 进行中、已完成、未解锁、约需时长 |
| Progress | 可量化进度 | 单元进度、场景轮次、练习完成度 |
| Dialog / AlertDialog | 临时说明、确认或需要专注的阻断 | 退出未完成任务、麦克风权限说明；危险操作才使用确认 |
| Toast / Alert | 短反馈与页面内风险反馈 | 播放示范、评分失败、网络恢复；P0 失败不能只用 Toast |
| Skeleton / Empty | 加载与无课程状态 | 课程列表准备中、暂未获得学习内容 |
| Tabs / ScrollArea | 同级导航和长内容容器 | 仅在已确认存在同级学习视图时使用 |

基础组件必须继承 `PUI` 中的主次操作、禁用原因、键盘/触控路径和状态出口。组件库的默认样式不能覆盖已确认的信息优先级。

### 3.2 SpeakUp 领域组件目录

| 组件语义 | 组合基础 | 必需输入 | 关键状态 | 不得自行决定 |
|---|---|---|---|---|
| `CoursePath` | Card + Progress + Badge | 单元顺序、可达状态、当前项 | locked / active / completed | 解锁条件、跳关规则 |
| `LearningTaskStep` | Button + Badge | 任务名称、顺序、完成度 | current / done / disabled | 是否可跳过、完成判定 |
| `SentencePractice` | Card + Button + Progress | 目标句、示范入口、评分结果 | ready / recording / scoring / passed / retry | 评分模型、阈值、音频保留 |
| `PronunciationFeedback` | Alert + Button | 分数或结果、问题项、下一步 | pass / repractice / support | 纠错依据、连续失败阈值 |
| `SupportPractice` | Card + Button | 已确认的辅助任务、返回完整任务入口 | active / finished | 完成即通过与否 |
| `ScenarioDialogue` | Card + Progress + Alert | 场景目标、轮次、输入/识别结果 | in_progress / redirected / complete / error | 自由对话范围、语义判定规则 |
| `LearningResume` | Card + Button | 最近未完成位置、继续入口 | resumable / unavailable | 跨端同步、进度写入时机 |
| `LearningCompletion` | Card + Badge + Progress | 已完成任务和下一步 | completed / next_locked / next_ready | 自动解锁与奖励策略 |

若某项目没有评分、录音或对话，不生成对应组件；若项目不是学习端，也不要套用这些名称。

### 3.3 Token 约束

使用语义 Token，而不是把具体颜色当作业务规则：

```yaml
design_tokens:
  color:
    background: 页面背景
    surface: 卡片与浮层表面
    foreground: 主文字
    muted: 辅助文字
    primary: 唯一主操作
    success: 完成/通过
    warning: 需要注意或复练
    destructive: 失败或不可逆风险
    border: 分隔与可编辑边界
  spacing:
    base: 4
    scale: [4, 8, 12, 16, 24, 32]
  radius:
    control: token
    card: token
  motion:
    use: 只表达录音、加载、状态转移与完成反馈
    reduce_motion: required
```

教育端应在颜色之外提供文字、图标、形状或位置提示，不能只靠红绿区分评分和完成状态。触控目标、焦点样式、读屏名称和低动效偏好是基础层验收项；具体像素值由目标设备与品牌约束决定。

## 4. 设计系统 Contract

当需要交给设计或研发时，在 `PUI Contract` 之后追加一个 `DS-` Contract。它只冻结布局/组件复用和 Token 语义，不把候选实现说成已安装组件。

```yaml
design_system_contract:
  contract_id: DS-001
  status: draft # draft / ready / superseded / blocked
  applies_to: [P-001, P-002]

  target_surface: teacher-console
  layout:
    pattern: app-shell
    regions: [header, sider, content]
    responsive_rules: [desktop-landscape]

  foundation:
    status: candidate # candidate / confirmed
    client: learner # learner / teacher / operations
    library: shadcn-ui
    primitive: radix
    implementation_authorized: false

  product_profile:
    name: SpeakUp
    status: candidate
    target_device: learning-machine

  semantic_tokens:
    required: [background, surface, foreground, muted, primary, success, warning, destructive, border]
    confirmed_values: []

  component_map:
    base: [Button, Card, Badge, Progress, Dialog, Toast, Skeleton, Empty]
    domain:
      - component_id: C-021
        semantic_role: SentencePractice
        composes: [Card, Button, Progress, Alert]
        slots: [root, prompt, example, recorder, feedback, actions]
        variants: [ready, recording, scoring, passed, retry]
        compound_variants: []
        traces_to: [F-012, PUI-003]
        required_states: [ready, recording, scoring, passed, retry, error]
        forbidden_assumptions: [score_threshold, audio_retention]

  handoff:
    semantic_locked: []
    visual_flexible: []
    pending_decisions: []
    implementation_boundary: "candidate mapping only; no package or registry is installed"
```

`foundation.status` 只有在用户或现有工程明确确认后才能为 `confirmed`。`implementation_authorized` 默认为 `false`；用户要求安装或改工程时才走下游执行，并在返回审计中记录真实证据。

## 5. S4–S6 交付与验收

### S4 原型

原型可采用已选 Profile 的 Token 和组件层级，但必须保留 `PUI` 的 `semantic_locked`。若仍是候选 Profile，应在交接包而非用户页面上标记 `candidate`；不能把视觉升级误报为已接入 shadcn/Radix。

### S5 验证

除原有任务与状态验证外，检查：

- P0 信息在长文本、禁用或错误状态下仍可读、可操作；
- 主操作、完成、失败和锁定不只通过颜色传达；
- 录音、加载等动效在 `prefers-reduced-motion` 下仍有明确状态；
- 领域组件的每个关键状态回指 `F/TR/AC/T`；
- 基础组件替换没有改变已确认的解锁、评分、保存、权限或完成语义。

### S6 交接

交付 `DS-` Contract、布局/插槽/变体字段、Token 清单、基础/领域组件映射、状态矩阵、PUI 追溯和实现授权状态。只有下游工程返回真实依赖、组件文件、构建或运行证据时，才能说明已完成库接入；否则只称为候选规范或原型级实现。

## 6. 反模式

- 不因使用 shadcn/ui 就默认 React、Tailwind、Radix 已安装；
- 不把 `Button`、`Card` 的外观变化当作需求确认；
- 不因组件名为 `SentencePractice` 就默认评分、录音存储、连续失败或通关阈值；
- 不把学习端 Profile 套用到教师/运营后台；
- 不把 Ant Design 与 shadcn/ui 混在同一用户端而没有边界；
- 不把原型中的本地状态、样例 Token 或视觉截图当作生产组件库、Registry 或上线证据。
