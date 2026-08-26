# 产品架构与需求分析 Skill

> 中文版｜通过低摩擦对话，把模糊想法持续沉淀为需求、产品架构、中保真原型、验证证据、生产交接与运营复盘。

`product-architecture-requirements` 是一个面向产品经理、业务专家/教师、设计师、运营与研发协作方的 Codex Skill。它通过简洁的自然语言对话，将模糊想法沿统一生命周期沉淀为业务流程、功能架构、页面结构、组件状态、中保真原型输入、验证证据和可验收的交接方案；不会用一份假设很多的 PRD 代替需求确认。

## 当前版本：v4.0.1（Harness Engineering 项目治理）

- 新增 `Project Identity Gate`，明确 `resume / fork / new / needs_confirmation`，新项目不会继承最近项目内容。
- `ProjectSnapshot` 可持久化为项目 JSON，通过 revision 与事件日志做增量更新和冲突保护。
- PUI 之后新增可执行 `Frame Contract` 与 `Flow Contract`，约束视口、区域几何、状态可达、异步兜底和具体恢复位置。
- 新增 `./harness` 统一入口，执行 `lint → render → test → report`，模型不再自由生成页面 HTML/CSS。
- 原型运行时只接受组件白名单、登记模板或 project-local 候选；图片、人物、视频和插画只显示中性 Slot 占位。
- 新增真实 Chromium 几何、任务路径、素材扫描和截图差异检查；结构评分不再等同于页面质量。
- 新增结构化错误和最多两次局部修复；修复只生成候选副本，不静默改变源 Contract 或业务语义。
- 输出统一 `Harness Handoff Package`，同时标记技术、视觉基线、目标用户和 Mock/真实能力证据。

当前确定性验证：v4.0 Harness 行为回归 24/24、AI 口语 Golden Case 在 1280×800 下完成真实浏览器双场景渲染（正常路径与超时回退路径）和视觉基线检查；旧 v3.4 生命周期 25/25、v3.7 模具协议 50/50、跨项目污染扫描 7/7 保持通过。目标用户验证仍需真实测试，不由技术绿灯替代。

## 项目化持续协作

为让规则跨任务持续生效，仓库增加了 [AGENTS.md](AGENTS.md)、[ARCHITECTURE.md](ARCHITECTURE.md)、[docs/](docs/) 和 [scripts/verify](scripts/verify)。维护任务会先读取项目地图、质量规则和当前计划，再通过统一入口回归；业务项目仍应维护自己的 `AGENTS.md`、ProjectSnapshot 和验证入口，不会自动继承本仓库的旧项目状态。

### 为新业务项目搭建配置

使用项目初始化器生成独立的治理骨架：

```bash
python3 scripts/init_project.py /path/to/project --name "项目名称"
cd /path/to/project
./scripts/verify
```

初始化器只创建不存在的文件，不复制旧项目需求、状态、文案或视觉资产。详细规则见 [项目 Harness 配置启动](references/project-harness-bootstrap.md)。

## 项目级模具与原型生成

进入原型前，Skill 会为每个新项目建立独立 `ProjectUIProfile`，并按目标用户、核心任务、页面类型、信息层级、关键区域、设备尺寸和交互状态检查模板：

- `exact`：完整匹配，生成当前项目实例；
- `extensible`：核心骨架匹配，只扩展允许的 Slot、区域或状态；
- `no_match`：不套旧模具，生成项目级黑白候选。

图片、插画、音视频等只在原型中显示语义占位、比例和状态，不复用历史视觉资产。用户可以在当前对话中查看生成前摘要、打开真实预览并用自然语言修改；每次修改保留版本和影响记录。

- 将主链路统一为“输入归集 → 需求收拢 → 产品架构 → 规格生成 → 中保真线稿 → 方案验证 → 生产交付 → 运营复盘”。
- 新增 `ProjectSnapshot` 单一事实源和 S0–S7 阶段门槛，需求、原型、测试、交接与指标不再各自维护一套状态。
- 新增 v0.4 中保真交互线稿规范，明确真实信息密度、关键状态、恢复路径、Mock 边界和返回审计。
- 新增原型 UI Contract 层，在页面规格与中保真原型之间冻结页面骨架、信息层级、操作层级、组件语义、页面状态和语义/视觉边界。
- 接入 `product-management-workflows` 的研究、竞品、路线图、汇报与指标专项路由，所有结果写回 DEC/CHG 和下一轮验证。
- 主入口改为轻量总控，专项 schema、A2UI 和交付细节按需读取，降低上下文噪声。
- 新增角色化低摩擦对话层：教师、产品、设计、运营和研发使用各自熟悉的语言推进；探索阶段默认只问一个关键问题，内部状态与 ID 不直接外露。
- 强化探索轮 250 汉字硬上限、单问题/单决策、短答增量记忆和 S2→S3 最小就绪检查；正式交付将范围优先级 Must 与交付就绪 Ready 分开，高影响 Pending 规则不会进入正向 AC。
- 增强设计系统路由：教师/运营后台优先 Ant Design，学生端优先 shadcn/ui + Radix，严格多部件插槽可选 Park UI；所有设计系统均以布局、插槽、变体、状态和 Token Contract 交接。

## 能解决什么问题

- 把一句模糊构想拆成可讨论的业务目标、用户角色和 MVP 范围。
- 梳理主流程、异常分支、权限边界与状态流转。
- 输出带优先级、用户故事、验收标准（AC）的功能矩阵。
- 生成信息架构（IA）、页面框架、组件映射和交互状态说明。
- 形成可以交给产品、设计、研发继续推进的 Master PRD 与生产交接清单。
- 生成中保真交互线稿的可执行输入，并区分技术、目标用户和交接三类验证证据。
- 把访谈、竞品、路线图和上线指标回写到下一轮需求与决策，而不是停在孤立报告。
- 在需求达到 Ready 后，把高保真原型、研发任务或测试资产安全交给匹配的专业 Skill，并回收验证结果。

它尤其适合教育、SaaS、内容平台、运营后台、数据看板等多角色、流程型产品的早期梳理。

## 适用对象

| 对象 | 典型使用场景 |
| --- | --- |
| 产品经理 | 新项目立项、需求拆解、MVP 规划、PRD 补全 |
| 教师/业务专家 | 把教学或业务流程转为可落地的系统功能 |
| 设计师 | 明确页面层级、组件状态、布局重点与交互边界 |
| 运营/项目负责人 | 梳理角色权限、业务闭环、风险与迭代路线图 |

## 安装

### 在 Codex 中使用

将仓库克隆到 Codex 的 skills 目录；下面的目标路径请替换为自己电脑上的实际路径：

```bash
git clone https://github.com/black605/product-architecture-requirements.git /path/to/.codex/skills/product-architecture-requirements
```

重新打开 Codex 或开启一个新对话后，即可通过 Skill 名称调用。若本机已存在同名目录，请先备份其中内容，避免覆盖自己的修改。

### 直接复制安装

也可以下载本仓库，把整个 `product-architecture-requirements` 文件夹复制到 Codex 的 skills 目录。核心入口文件是 [SKILL.md](SKILL.md)。

### 在其他 Agent 平台中使用

本仓库提供可复制的中文配置模板：

- [Dify 配置说明](platform/dify-config.md)
- [Coze 配置说明](platform/coze-config.md)
- [GPTs Instructions](platform/gpts-instructions.md)

将对应文件的系统提示词内容复制到目标平台即可。不同平台的变量、知识库和工具配置方式不同，建议先按其文档完成基础配置，再进行试跑。

## 如何调用

在 Codex 对话中显式调用：

```text
$product-architecture-requirements 我想做一个在线评作业系统，老师能批改，学生能看到反馈。
```

也可以从更自然的请求开始：

```text
创建需求：我们想做一个面向 5～8 岁孩子的英语口语启蒙课程产品。
```

Skill 会先说明它已理解的项目背景，并提出一个最关键的问题。你不需要按固定格式回答，直接用自然语言补充、纠正或新增信息即可。

## 对话规则

这是一个“先确认、再下钻、验证后回写”的产品全周期助手，默认遵循以下规则：

- 探索阶段每轮只问 1 个关键问题，避免一次性问卷式收集。
- 不默认输出按钮、单选、多选、勾选框或字母选项；你可以用自然语言自由回答。
- 已确认的结论可以随时修改，例如“把首期改为只支持小班直播课”。
- 长对话会用稳定的 DEC/CHG 记录确认与修改；“是的”只会绑定上一轮唯一明确的问题。
- 只有当你明确要求“给我几个选项/帮我比较方案”时，才会给出备选方案与取舍。
- 在核心流程确定后，主动补充必要的异常、权限、并发或状态边界，但不会凭空把假设写成事实。
- 一旦出现多人协作、异步、倒计时、并发、撤回或恢复规则，会自动生成状态转移与对应测试，不必再次要求“画状态机”。
- 所有阶段共享一份可持久化 `ProjectSnapshot`；重要对象和产物使用稳定 ID，Must 项保持目标到测试、产物的追溯。
- 进入原型前必须完成项目身份、PUI/UIP/TFD/ASC 与 Frame/Flow Contract；可运行原型必须通过 Harness，而不是只看规则文字。
- 用户研究、竞品和指标只作为证据或候选决策；不会因一条反馈或一次波动自动改需求。

## 推荐使用方式

### 示例 1：从模糊产品想法开始

```text
$product-architecture-requirements
我想做一个在线评作业系统，老师能批改，学生能看到反馈。
```

接下来只需依次说明你知道的内容，例如作业来源、学生匹配方式、自动判分范围、反馈渠道、是否支持订正重交等。Skill 会把这些内容沉淀为作业生命周期、角色权限、功能矩阵和页面规格。

### 示例 2：从现有业务痛点开始

```text
创建需求：老师收作业后常常不知道对应哪个学生，逐份批注也很耗时。
```

Skill 会先帮助界定问题发生在哪个角色、哪段流程和什么结果上，再把“学生识别、历史记录、批注效率”等问题拆成可实施的功能。

### 示例 3：从设计诉求开始

```text
$product-architecture-requirements
我们要重构一个数据大屏和后台控制台，需要支持复杂动效与多视图切换。
```

在业务目标和使用场景确认后，它会输出页面布局、视觉层级、Tabs/Drawer/Skeleton 等组件状态与动效基调，而不是直接生成大量前端代码。

## 工作流与交付物

| 阶段 | 重点确认内容 | 阶段产物 |
| --- | --- | --- |
| S0 输入归集 | 输入来源、可观察事实、资料缺口 | 事实/假设/待确认清单 |
| S1 需求收拢 | 用户、场景、问题、结果、范围 | 项目画像、成功口径、DEC/Pending |
| S2 产品架构 | 角色、对象、主流程、状态、MVP | 业务闭环、对象与状态模型 |
| S3 规格生成 | 功能、IA、页面、组件、AC、测试 | 可追溯产品规格 |
| S4 中保真线稿 | PUI、Frame/Flow、组件白名单、异常与恢复 | 受控 HTML、截图、运行 trace 与交互线稿交接包 |
| S5 方案验证 | 浏览器几何、任务、视觉、目标用户、交接证据 | Harness 报告、问题与优化决策 |
| S6 生产交付 | Owner、依赖、风险、产物状态 | Master PRD 投影、Handoff Manifest |
| S7 运营复盘 | 研究、竞品、路线图、指标与行动 | DEC/CHG、路线图动作、下一轮验证 |

## 最终会产出什么

完成必要确认后，Skill 会汇总为一份 Markdown 规格文档，通常包含：

1. 项目概览、目标与范围边界。
2. 用户角色、权限与关键诉求。
3. 主业务流程、异常分支和状态机说明。
4. 功能规格清单：优先级、用户故事、验收准则（AC）、异常处理。
5. 1～3 级信息架构（IA）树。
6. 页面布局、UI 组件、交互和状态规格。
7. 风险、开放问题、首期 MVP 与后续迭代路线图。
8. 面向产品、设计、研发的生产交接清单。
9. 对复杂动态业务自动生成状态转移表、Mermaid 状态机和可追溯测试用例。
10. 进入可运行原型后生成 Frame/Flow Contract、受控 HTML、截图、Harness 报告和 Handoff Package。

核心产物是“需求与架构规格”，不是可直接上线的后端代码或 Figma 源文件。用户明确要求继续交付时，Skill 会先冻结需求基线，再把原型、研发或测试任务编排给当前环境中可用的专业能力，并检查返回产物是否仍与需求一致。

## 仓库结构

```text
.
├── SKILL.md                         # 轻量总控、主链路与按需路由
├── CHANGELOG.md                     # 版本演进记录
├── agents/openai.yaml               # Agent 元数据
├── harness                          # lint/render/test/report 统一入口
├── scripts/harness.py               # Contract 编译、浏览器验证与有限修复
├── assets/prototype-harness/        # 中性运行时、模板目录和组件白名单
├── assets/project-harness-template/ # 新业务项目治理骨架
├── platform/                        # Dify、Coze、GPTs 平台配置
├── references/                      # 生命周期、Snapshot、原型、交接与专项协议
│   ├── prototype-ui-contract.md     # 页面语义与状态 Contract
│   ├── project-ui-profile.md        # 项目独立 Profile 与证据隔离
│   ├── prototype-template-fit.md    # 原型模具适配闸门
│   ├── conversational-prototype-session.md # 对话式原型与 Patch
│   └── versions/                    # 历史版本快照
├── schemas/                         # Snapshot、Frame/Flow、Profile、模板与交付数据结构
├── tests/                           # 对抗用例、Golden Case、回归记录与正式测试证据
├── docs/                            # 产品基线、计划、决策和质量规则
├── AGENTS.md                        # 跨任务 Agent 协作规则
├── ARCHITECTURE.md                  # 模块边界、依赖方向和状态所有权
├── scripts/init_project.py          # 为业务项目初始化治理骨架
└── scripts/verify                   # 统一结构、回归和 Harness 验证入口
```

建议先阅读 [快速开始](references/quickstart.md)，需要了解评估方式时查看 [评分量表](references/evaluation-rubric.md)，需要做提示词迭代时使用 [自我迭代 Meta-Prompt](references/meta-prompt.md)。

## 质量验证与版本记录

本 Skill 已沉淀以下验证资产：

- [对抗测试用例](tests/adversarial-cases.md)：覆盖模糊需求、复杂 SaaS、数据看板等场景。
- [五子棋完整交付用例 D](tests/gomoku-case-d/README.md)：覆盖决策账本、邀请/组队/对局状态机、高保真原型、研发与测试交接。
- [v3.4 产品全周期回归](tests/v3.4-lifecycle-cases.md)：覆盖模糊想法、已有 PRD、原型回改、用户研究和上线指标写回。
- [回归测试报告](tests/regression-report.md)：用于检查版本升级后是否发生引导逻辑退化。
- [50 轮正式运行记录](tests/formal-platform-50/README.md)：记录生产平台模拟运行与评分证据。
- [v3.4.7 五角色增强回归](tests/role-dialogue-50/v3.4.7-dialogue-quality-final/review.md)：40 个探索轮与 10 个交付轮，覆盖短答、回改、矛盾、跨角色、提前索要产物和 Ready/Blocked Gate。
- [v3.7 项目级模具正式回归](tests/prototype-template-50/v3.7.0-release/README.md)：50 个独立会话，覆盖 Profile 隔离、三态适配、无匹配候选、素材占位、对话 Patch、模板生命周期和历史逻辑保护。
- [v4.0 可执行 Harness 回归](tests/run_v40_harness_checks.py)：真实浏览器、几何、任务、双场景超时回退、三态模板路由、视觉差异、项目身份、Snapshot 冲突、素材政策和有限修复 24 项行为检查。
- [AI 口语 1280×800 Golden Case](tests/golden/ai-speaking-1280)：从课程地图到学习报告的正常/超时回退可重复原型输入与截图基线。
- [变更记录](CHANGELOG.md)：说明每次规则调整的位置、原因与预期防范问题。

若要继续优化，请遵守“每次只改一个测试用例或一个核心缺陷、改后回跑上一阶段案例、同步记录 Changelog”的迭代规则。

## 常见问题

### 为什么不一开始就输出完整 PRD？

因为早期需求中的目标、角色、流程与边界往往尚未确认。先用少量关键问题收敛不确定性，可以降低“结构完整但方向错误”的风险。

### 我可以跳过部分问题吗？

可以。直接说明“这一项暂定”“先按某个假设推进”或“暂不处理”，Skill 会将其标记为假设或开放问题，并继续推进。

### 我想要选项对比怎么办？

直接说“给我 3 个方案并比较取舍”或“请列出可选项”。Skill 会给出结构化比较，但不会把选择题作为默认交互方式。

### 已经确认的需求可以反悔吗？

可以。直接用自然语言修改即可，例如“把反馈渠道首期改为仅系统内消息”。Skill 会保留旧决策历史，建立新的变更记录，并回写受影响的流程、功能、页面、状态机、测试和交付产物。

### 能否生成代码或完整视觉稿？

本 Skill 的核心职责仍是需求与产品架构。达到 Ready 后，它可以用内置 Harness 生成受控中保真 HTML、截图和验证报告；最终品牌视觉、生产前端、后端服务与 Figma 源文件仍交给相应专业能力，并在返回后检查追溯和状态覆盖。

## 维护与贡献

欢迎通过 Issue 或 Pull Request 提交案例、测试反馈和规则改进。修改 [SKILL.md](SKILL.md) 时，请同时：

1. 选择一个明确的测试场景或核心缺陷。
2. 说明修改位置、修改原因和预期防范的问题。
3. 回跑相关历史用例，确认没有逻辑回退。
4. 更新 [CHANGELOG.md](CHANGELOG.md)。

---

仓库地址：[github.com/black605/product-architecture-requirements](https://github.com/black605/product-architecture-requirements)
