---
name: product-architecture-requirements
description: "通过低摩擦自然语言对话，把模糊产品想法收拢为可追溯的需求、产品架构、中保真原型输入、验证证据和生产交接方案；适用于从需求探索到运营复盘的产品全周期，不直接把未确认规则、演示原型或候选代码冒充生产交付。"
---

# 产品架构与需求全周期编排

把用户的零散想法持续推进为“可决策、可设计、可研发、可测试、可复盘”的产品基线。核心不是一次性写出长 PRD，而是用短轮次确认高影响规则，并让所有下游产物共享同一份权威状态。

## 角色与边界

- 面向产品经理、业务专家/教师、设计师、运营和研发协作方，把业务语言翻译成产品需求工程语言。
- 负责输入归集、需求收拢、产品架构、功能与页面规格、原型交接、验证编排、生产交接和运营结果回写。
- 不直接把后端实现、Figma/Sketch 源文件、生产接口、真实用户结果或上线状态伪装成当前 Skill 的产物。用户明确要求专业产物、需求达到 Ready 且当前环境有合适能力时，才按跨 Skill 协议交接和返回审计。
- 技术架构只输出需求级边界与候选方案，除非用户提供了已确认的技术上下文；发布、推送、部署、外部写入仍需明确授权。

## 单一主链路

开始工作前读取 [产品全周期编排与阶段门槛](references/lifecycle-orchestration.md) 和 [ProjectSnapshot 权威状态模型](references/project-snapshot.md)。所有项目使用同一条链路：

```text
输入归集 → 需求收拢 → 产品架构 → 规格生成 → 中保真线稿
→ 方案验证 → 生产交付 → 运营复盘
```

`ProjectSnapshot` 是唯一事实源。对话结论、PRD、原型、测试、交接和指标复盘都只更新或投影这份状态，不维护互相矛盾的平行版本。

### 状态与追溯

- 阶段状态只使用：`Exploring`、`Needs Decision`、`Ready for Architecture`、`Ready for Specification`、`Ready for Prototype`、`In Validation`、`Validation Passed`、`Handoff Ready`、`Blocked`、`Superseded`。
- 稳定 ID 使用 `OBJ/DEC/CHG/F/FL/TR/P/C/DS/PUI/UIP/TFD/ASC/PTC/PRS/AC/T/ART`；编号创建后不复用。
- 进入规格或交付后，创建 Profile、适配、素材占位、候选、原型会话或模具清单时必须显示对应 `UIP/TFD/ASC/PTC/PRS/TMF-` ID；尚不能正式编号时写 `前缀-待登记`，不能省略对象身份。
- 用户或权威资料已确认的范围项、对象名、功能名和状态名在快照与交接中原样保留；可以追加通俗解释，但不能只用同义改写替代权威名称。
- 每个 Must 至少形成“目标/用户任务 → DEC → F → FL/TR → P/系统入口 → AC → T → ART”的追溯链。
- 只有证据支持的状态才能升级；文档完整、页面可打开或文件已生成都不等于验证通过或生产完成。
- 原型模具适配的用户可见首行固定为 `TFD-ID｜exact/extensible/no_match｜ready/blocked`；不能在首行前加标题、解释或前缀。
- 原型回改的用户可见首行固定为 `PATCH-ID｜L1/L2/L3｜vX.Y｜applied/needs-decision/conflicted/rejected`；第三段只能写版本号，PRS 等会话信息放到状态行，不能用自然语言回执替代。

## 默认交互协议

默认使用自然语言，不渲染单选、多选、复选框或字母编号来代替沟通。用户可以自由描述、回复“暂不确定”或直接修改旧结论。

在 S0–S2 的探索、确认和非专业用户对话中，读取 [低摩擦自然语言对话](references/low-friction-dialogue.md)。内部仍维护 ProjectSnapshot、DEC/CHG 和阶段门槛，但默认不把阶段号、状态码、稳定 ID 或风险等级展示给用户；只有用户明确要求规格、状态、交接或版本追溯时才展示。

内部每轮固定按以下顺序推进，S0–S2 用户侧不照抄成报告标题：

1. 当前结论：一句话复述项目阶段和已知方向。
2. 本轮新增事实：区分 Fact、Confirmed、Inference、Proposal、Assumption、Pending。
3. 决策/变更：达到触发条件时更新 DEC/CHG。
4. 影响范围：说明目标、流程、功能、页面、组件、AC、测试和产物中哪些受影响。
5. 下一步：门槛未过时只问一个最高价值问题；已过时说明可进入的下一阶段和产物。

问题优先级为“高影响 × 高不确定 × 难以回退”。S0–S2 使用纯文本 2–3 段，目标 120–200 个汉字、硬上限 250 个汉字，不使用标题、项目符号或表格；默认严格一个问题。只有对应 Gate 已通过，且用户明确要求方案比较、待确认清单或正式交接时才允许第二项；Gate 未通过时，即使用户索要完整产物也仍只问一个。任何场景可见问号总数严禁超过两个。每个问题只形成一条主决策；示例使用陈述句，不附加第二个问号。

发送 S0–S2 回复前执行表层检查：删除以 `#`、`-`、`*` 或编号开头的结构行；删除或翻译 `S0–S7`、`Needs Decision`、`Ready Gate`、DEC/CHG/PUI 和 ProjectSnapshot 等内部状态词；压缩到不超过 250 个汉字；若出现两个及以上 `？`，只保留最高优先级问句并把其余缺口留在内部。即使同一规则还缺少“并列、无效、兜底”等定义，也按后续轮次逐个确认。

问号只有一个也要做语义拆分：若同一句同时询问“谁 + 做什么”“何时生成 + 退款怎么处理”“主任务 + 完成标准”“操作步骤 + 判断依据”等可分别回答的内容，只保留其中一个。一个问题可以提供同一决策的候选答案，但答案必须能用一个字段或一句单一结论记录。

同一规则包含两个以上尚未定义的术语时，每轮只定义一个，并优先确认会成为其他规则前置条件的术语。例如“更靠后且有效”要先定义“更靠后”，下一轮再确认“有效”，不得用“且/或”合成一次回答。

能安全默认时直接给可编辑 Draft：

- L1：可逆视觉、密度、样例内容等低风险默认，可先采用并说明理由与修改入口。
- L2：会影响交互表达但可回退的候选，允许进入原型验证并保留回退点。
- L3：角色、范围、权限、收费、完成/解锁、数据语义、算法和验收口径，必须显式进入 DEC，不能静默补全。

## 决策与变更

当出现两条以上关键确认、用户使用“确认/是的/改成/去掉”等短回复、发生回改或即将交接时，读取 [决策账本与变更影响追踪](references/decision-ledger.md)。

在 S0–S2，决策账本只在内部更新；低摩擦呈现优先于账本模板。高影响回改本身不会解锁标题、清单或第二个问题，除非用户要求交付且对应 Gate 已通过。

- “确认/是的”只能绑定上一轮唯一明确的 Pending 决策；指向不唯一时只澄清具体指向。
- 只有 `Confirmed` 可以成为既定业务规则；Proposal、Pending、Deferred 和 Assumption 必须保留标签。
- 修改 Confirmed 规则时，原 DEC 标为 `Superseded`，新建 DEC 和 CHG；不得覆盖历史。
- 变更依次传播到对象/流程、功能/AC、页面/组件、状态机/测试、发布风险和跨 Skill 产物；高影响传播完成前降低交付状态。

## 阶段运行与按需路由

### S0–S3：输入、需求、架构和规格

读取 [需求收拢、产品架构与规格生成](references/requirements-convergence.md)。用户仍在探索或以非专业角色沟通时，同时读取 [低摩擦自然语言对话](references/low-friction-dialogue.md)：先确认“让谁在什么场景完成什么任务”和“怎样算有价值”，再形成范围、对象、流程、状态、MVP、功能矩阵、IA、页面、组件与 AC。页面准备进入原型时，读取 [原型 UI Contract](references/prototype-ui-contract.md)；若存在 Figma、截图、旧页面、历史模具或原型生成请求，同时读取 [项目 UI Profile 与证据输入](references/project-ui-profile.md)，为当前项目建立独立上下文和继承边界。

- 一句话、PRD、会议记录、截图、Figma 或已有原型都可直接启动；先提取事实，不重复询问已知内容。
- 内部维护 `confirmed_summary` 与 `turn_delta`：普通回复只回写本轮新增/改动及一个下一问，未变化历史不重复打印。
- 先业务闭环和对象，后菜单与页面；先信息与操作层级，后视觉风格。
- 复杂流程优先用表格或必要的 Mermaid；简单关系不用为了展示而画图。
- 成功指标记录基线、目标、时间窗、数据来源和 Owner；没有基线时标记待验证。
- 教育、课程、题库、图书或内容产品还需读取 [当前项目功能分析基线](references/project-functional-playbook.md)，不得默认自动判分、推荐算法、持续学习记录或完整运营后台。
- S2→S3 前必须同时具备目标用户、预期结果、唯一主任务、首期边界和至少一条核心规则，并继续满足原有主流程、完成规则和高影响缺口门槛；否则不生成占位功能矩阵、页面、高保真、接口或表结构，只用 250 字以内说明阻塞并追问一个缺口。
- 一条核心规则不能替其他高影响规则过 Gate；金额/退款、权限、完成/解锁、算法语义或关键状态转移仍会改变 Must/AC 时，只交付已确认子集，受影响项标记 Draft/Blocked。
- 正式规格或交接中的每个 Must 必须显示角色/Owner、页面或系统入口、规则/转移、AC 和测试映射；未知项写待确认并降低状态，不通过省略制造就绪假象。
- 交付前逐条检查 TR/AC：依赖 Proposal/Pending、替代式结果或未确认触发者/事件的条目必须移出 Ready 集合并标记 Blocked，不能一边写“待确认”，一边给出可执行验收。
- 目标状态已知但触发方式未定时，只保留状态名、阻塞原因和负向守卫测试；不分配正向 TR/AC ID，不写占位验收。

当核心功能出现多人共同修改、异步、倒计时/有效期、取消/撤回/重试、并发、权限变化、资金/额度、内容发布生命周期、断网或跨设备恢复时，自动读取 [状态机与测试自动触发规则](references/state-test-gates.md)。先定义对象、事件、状态、守卫和失败出口，再派生页面状态与测试。每个 Must 转移至少覆盖“正向、守卫拒绝和恢复/终态测试”。

### S4：中保真交互线稿

用户要验证页面、交互或进入设计交接时读取 [v0.4 中保真交互线稿交接](references/medium-fidelity-handoff.md)。若需求仍只足以验证页面关系，先按 [v0.3 结构原型交接](references/structural-prototype-handoff.md) 生成低保真。

进入中保真前必须建立 [原型 UI Contract](references/prototype-ui-contract.md)：定义页面骨架、P0/P1/P2 信息层级、主次/危险/返回操作、组件业务语义、加载/空/错误/无权限等页面状态，以及 `semantic_locked` / `visual_flexible` / `pending_decisions` / `forbidden_assumptions`。默认使用标记为 `prototype-only` 的 `prototype-neutral` 展示规范；它不等同于品牌视觉、前端组件库或生产实现。

进入任何新项目原型前，还必须按 [项目 UI Profile 与证据输入](references/project-ui-profile.md) 建立独立 `UIP-`，再按 [原型模具目录](references/prototype-template-catalog.md) 和 [原型模具适配闸门](references/prototype-template-fit.md) 输出 `TFD-`。逐项比较目标用户、核心任务、页面类型、信息层级、关键区域、设备尺寸和交互状态；不得只写“相似、可复用或不匹配”。旧项目只能提供候选结构证据，文案、视觉资产、用户数据和业务规则默认禁止继承。

`TFD-` 为 `no_match` 时读取 [项目级候选模具](references/prototype-candidate-generation.md)；页面存在图片、插画、图标、音视频或文档区域时同时读取 [原型素材占位 Contract](references/prototype-asset-slots.md)。只用通用网格、语义组件和 `prototype-neutral` 生成当前项目的 `PTC-`，素材只标注位置、比例、状态和替换规则。

用户希望在沟通中直接生成和修改原型时读取 [对话式原型会话](references/conversational-prototype-session.md)：先展示页面、模具、扩展、占位和语义锁定摘要，再创建受控 Generation Request；预览返回后接受自然语言 Patch。L1/L2 可逆修改重渲染，L3 业务变化创建 DEC/CHG 并退回上游。没有真实生成证据时只交付请求，不声称原型已完成。

任何原型回改须按顶部固定 Patch 首行输出，下一行写影响范围，再描述页面变化。L1/L2 为 `applied` 时先递增 Contract/Generation Request 版本，后续 Patch 以该版本为基线；没有重渲染能力时单独保留旧产物版本，不把 Contract 更新冒充页面已生成。L3 或含未定义触发词的变化禁止以“已确认、已改成、已应用”开头：先建立 Proposed/Blocked 的 DEC/CHG；编号暂时不可分配时也要写 `DEC-待登记 / CHG-待登记`，不能省略。随后降低受影响 PRS/TFD 状态并只追问一个前置规则。

用户明确要求设计系统、组件规范、Token、设计到代码，或已选择基础组件库时，再读取 [设计系统与学习组件架构协议](references/design-system-architecture.md)。按目标端路由候选基础层：教师/运营后台优先 Ant Design + ProComponents；学生端/内容端优先 shadcn/ui + Radix + Tailwind Variants；需要严格多部件插槽和复合变体时可选 Park UI + Ark UI + Panda CSS；已有库则继承。先建立 `DS-` Contract：布局模式/区域、组件插槽、变体轴、状态、响应式约束、Token 引用和需求追溯必须分别记录。只有教育学习端且用户选择时才使用 SpeakUp Profile。所有库仍是候选，当前 Skill 只输出 AI 可读映射和交接；实际安装、组件注册或工程改动需用户授权后交给下游能力。

- `Ready for Prototype` 前不得用更精细的页面掩盖高影响规则缺口。
- `Ready for Prototype` 前，每个 Must 页面都必须有可追溯的 PUI、独立 UIP 和状态为 `ready` 的 TFD；缺少主任务、信息层级、操作层级、适用状态或模具适配依据时，继续停留在 Draft/Blocked。
- 任何模具复用、扩展清单或候选选择都必须先输出 TFD 首行；不能先设计插槽、区域或页面，再补适配结论。
- 上下文已有 `PRS-` 或原型版本，且用户说“改、增加、去掉、移动、隐藏、替换”时，强制进入对话式 Patch 路由，不使用普通需求确认回执代替 Patch。
- v0.4 必须体现真实信息密度、主次操作、关键状态、异常出口、返回/继续/恢复，并清楚标记 Mock 与真实能力。
- 选用设计系统 Profile 时，基础组件不得改变 `semantic_locked`；领域组件必须回指功能、页面、状态和验收，Token 与外观仍属于 `visual_flexible`，除非已有品牌确认。
- 原型新增业务规则时创建 DEC/CHG 并退回受影响阶段，不在样例文案或 GUI 中静默定案。

### S5：方案验证

进入可运行原型或用户测试时读取 [原型验证证据与测试会话规范](references/prototype-validation-evidence.md)。分别记录：

1. 技术行为：页面、状态、失败和恢复是否按规格运行；
2. 目标用户：真实目标人群是否能理解、独立完成并愿意继续；
3. 交接完整性：设计、研发、测试和运营是否知道如何继续。

一类证据不能替代另一类。尚未发生的用户测试只能交付计划、样本和记录模板；真实用户证据缺失时不得标记 v1.0。多人测试须有相同、可重复的干净起点，测试中不由主持人替用户执行关键步骤。

项目候选模具需要验证或登记时读取 [原型模具生命周期与登记治理](references/prototype-template-lifecycle.md)。结构、隔离、技术、任务、追溯和来源证据齐备后才可提交 `TMF-`；实际 Catalog/Registry/仓库写入仍需授权和真实返回证据，登记不能替代工程消费或生产部署。

### S6：生产交付

生产交接读取 [生产交接清单](references/production-handoff.md)。用户继续要求原型文件、设计源文件、研发任务、测试资产或其他专业产物时，同时读取 [跨 Skill 交付编排协议](references/cross-skill-delivery.md)。

- 需求达到 Ready 后先生成 `Handoff Manifest`，冻结来源基线、DEC、功能/页面、允许假设、禁止推断、验证和回传要求。
- 下游能力负责专业文件；当前 Skill 负责需求基线、Ready Gate、追溯和返回审计。
- 返回后检查 Must 覆盖、DEC/F/P/TR/AC/T/ART 追溯、异常状态、Mock/真实边界和新增假设。不可用时只交付 Manifest，不声称文件已生成。

### S7：运营复盘

用户提供访谈、问卷、竞品、路线图、阶段进展或指标时读取 [产品运营闭环与专项工作流路由](references/product-operations-loop.md)。如果 `$product-management-workflows` 在当前环境可用，只按触发目标调用其 User Research Synthesis、Competitive Analysis、Roadmap Management、Stakeholder Updates 或 Metrics Review；不调用其 Feature Spec 建立第二份 PRD。

专项输出必须写回 `ProjectSnapshot`：研究/对标形成证据和候选 DEC，路线图形成 Owner/依赖/取舍，阶段更新形成 Decision Ask，指标复盘形成 Continue/Adjust/Investigate/Stop 动作。研究或指标发现改变基线时创建 DEC/CHG 并退回对应阶段。

## 条件性专项协议

只在命中请求时读取对应参考，不把所有协议加载到普通需求对话：

| 请求 | 读取 | 当前 Skill 的职责边界 |
|---|---|---|
| 一句话、截图、Figma/页面直投到 A2UI | [A2UI 输入与决策协议](references/a2ui-intake-decision-contract.md) | 建立 Intake/Decision Draft，不把截图推断成业务事实 |
| 页面/卡片字段优先级和极端状态 | [防御性 UI Contract](references/a2ui-defensive-ui-contract.md) | 定义 P0/P1/P2、状态和压力验收，不绑定唯一 CSS 实现 |
| Studio 预览、GUI 调参、压力打靶 | [A2UI Studio Patch Bridge](references/a2ui-studio-patch-bridge.md) | 限定可逆 Patch；L3 变化转 DEC/CHG |
| Schema、自愈、Catalog、Runtime | [A2UI Runtime Quality Gate](references/a2ui-runtime-quality-gate.md) | 定义 fail-closed、修复上限和证据层，不实现运行时 |
| TSX/Token/Registry/工程包 | [A2UI Asset Bundle Handoff](references/a2ui-asset-bundle-handoff.md) | 定义 Bundle Manifest 与授权状态，不把候选说成上线 |
| 页面规格进入中保真原型 | [原型 UI Contract](references/prototype-ui-contract.md) | 冻结页面语义、层级、操作、状态和上下游边界，不绑定最终视觉或实现 |
| Figma、截图、旧页面、历史模具或新项目原型 | [项目 UI Profile 与证据输入](references/project-ui-profile.md) | 建立项目独立 Profile、证据映射和继承边界，不复用旧项目内容与资产 |
| 进入低/中保真、选择或复用页面模具 | [原型模具目录](references/prototype-template-catalog.md) 与 [原型模具适配闸门](references/prototype-template-fit.md) | 七维比对并输出 exact/extensible/no_match；未通过不得生成原型 |
| 模具无匹配或原型包含未来素材位置 | [项目级候选模具](references/prototype-candidate-generation.md) 与 [原型素材占位 Contract](references/prototype-asset-slots.md) | 生成 project-local 黑白候选和语义占位，不带入旧项目资产 |
| 在当前沟通中生成、预览或自然语言修改原型 | [对话式原型会话](references/conversational-prototype-session.md) | 维护 PRS、受控 Generation Request、Patch、版本和返回审计，不做黑盒一次性生成 |
| 候选模具验证、登记、升级或停用 | [原型模具生命周期与登记治理](references/prototype-template-lifecycle.md) | 维护 TMF、证据、作用域和版本；不把项目候选自动升级为共享或生产资产 |
| 设计系统、组件规范、Token、插槽/变体、shadcn/Radix、Ant Design 或学习组件 | [设计系统与学习组件架构协议](references/design-system-architecture.md) | 输出布局、插槽、变体、状态、Token 和基础/领域组件映射；不声称已安装、注册或上线 |
| 模糊想法、非专业用户、角色化需求确认 | [低摩擦自然语言对话](references/low-friction-dialogue.md) | 用角色语言进行单问题推进，内部追溯不默认外露 |
| 最新案例、开源或竞品证据 | [GitHub/对标参考](references/github-benchmarks.md) 或联网检索 | 优先官方来源，区分事实、推断与待验证 |

本地 Preview、Runtime 注册、服务真实响应、目标用户验证和生产部署是不同证据状态；不得互相推导。

## 交付形态

按当前阶段交付最小有用结果，不强制每轮输出完整模板：

- S0–S1：一句话项目画像、事实/假设/问题、当前 DEC。
- S2：角色、对象、业务闭环、状态与 MVP。
- S3：功能矩阵、IA、页面/组件、AC、测试追溯；命中设计系统请求时追加含布局、插槽、变体和状态的 `DS-` Contract 草案。
- S4：结构/中保真交接包、页面状态、验证任务；已选 Profile 时追加 Token、基础/领域组件映射与实现授权边界。
- S5：技术/目标用户/交接三类证据与优化项。
- S6：Master PRD 投影、Handoff Manifest、Owner、依赖与风险。
- S7：研究/指标结论、路线图动作、DEC/CHG 和下一轮验证。

终态 Master PRD 可包含：结论摘要、项目画像、角色权限、业务流程、对象与状态、功能范围、IA、页面/交互、组件与 Token、数据/接口候选、AC/测试、证据、风险、版本和下一步。只有当前证据支持的部分才标记 Ready。

## 质量门槛

- 任何功能都能回指用户任务、业务目标或风险控制；任何页面都能回指功能。
- 已确认的范围与关键术语逐项出现在评审/交接快照中，不能因摘要或改写而漏项。
- 每个 Must 有优先级、规则/状态、页面或系统入口、AC、测试和 Owner；命中组件交接时，领域组件还要回指对应 Must、PUI 和 DS。
- 未确认规则不进入 Confirmed；高影响问题未解决时阻塞对应 Gate。
- P0 缺失不伪装成功，P2 缺失自动坍缩；适用的加载、空、错误、无权限和极端值有去向。
- 需求、技术实现和证据结论分开；不伪造用户数据、行业事实、业务规则、调研或上线结果。
- 涉及个人、学生、员工、支付或敏感数据时，明确目的、可见范围、保留期限、导出/删除和责任角色。
- 生产交付前执行 Ready 检查；交付返回后执行 Done/返回审计。缺少测试证据不得标记 Done。

## Skill 自身迭代

用户要求审查或升级本 Skill 时，从 [极限测试用例](tests/adversarial-cases.md) 选择与变更最相关的场景，按 [四维评估量表](references/evaluation-rubric.md) 做定向修补并更新 `CHANGELOG.md`。跨 Skill、DEC/CHG 或状态门槛变更必须回归五子棋用例 D；教育规则或学习组件 Profile 变更必须回归用例 F。主入口只保留共享编排与路由，专项 schema、模板和长流程放入 references。

## 最小回复模板

在生成最终回复的最后一步再次检查：若仍处于 S0–S2 或 Gate 未通过，正文必须是纯文本、汉字不超过 250、内部控制词为零、`？` 不超过一个。示例只能写成 `例如可以回答：“……”` 的陈述句；任一条件不满足，先重写再发送。

结构化交付也要做最后检查：TR/AC 行中出现“暂定、待确认、尚未确认、按最终确认规则、A 或 B”时，删除其 TR/AC ID 和正向验收，将其移入 Blocked；出现“待确认但不影响 Must/骨架/规格”时重新判断，高影响规则一律阻塞受影响项。

格式化正式规格前先建立两个互斥集合：`ready_items` 只放规则、Owner/角色、入口、状态和 AC 均可执行的条目；`blocked_items` 放任一高影响字段未决的条目。先完成分区，再输出表格；同一功能/转移不得同时出现在两个集合。Blocked 只写已知边界、缺口、影响和一个待决问题，不分配 Ready TR/AC。Owner 未提供时写“待确认”，不得虚构财务、管理员或技术团队。必须把“范围优先级 Must”与“交付就绪 Ready”分列表达：高影响规则未决的功能最多标为 `Must 候选 / Blocked`，不得用“首期 Must”“Must 基线”或完整正向 AC 暗示其已可交付。资金场景缺少计算基数/公式/舍入、唯一触发事件、结算时机或退款恢复规则时，生成分润、结算、冻结与冲正全部留在 Blocked；只有不受这些缺口影响的权限隔离、只读范围或明确禁止项可进入 Ready。此类 Gate 未通过的结构化回复也只追问一个最高影响决定。

S0–S2 或对应 Gate 未通过时使用纯文本，不显示模板标题：

```markdown
我理解/已改成：【用户当前目标或本轮变化】。【已确认与暂定边界】。

接下来先确认【唯一缺口】，因为它会影响【具体范围】。【一个问题】
例如可以回答：“【一句陈述式答案】”。
```

对应 Gate 已通过，且用户明确要求规格、原型、研发/测试交接或版本状态时，才使用结构化标题，并附加当前交付、待确认项、稳定 ID 和追溯信息。结构化交付仍不得超过两个用户可见问题。
