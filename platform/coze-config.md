# Coze 配置映射

## Bot 人设/系统指令

将上级目录的 `SKILL.md` 全文粘贴到 Bot 的人设与指令字段。将 `references/meta-prompt.md` 作为维护者测试时使用的独立指令，不作为普通用户默认开场白。

## 建议工作流节点

1. Snapshot 节点：归集项目想法、资料和已有结论，初始化/更新 `ProjectSnapshot`。
2. 需求收拢节点：默认每轮 1 个、最多 2 个高影响自然语言问题，维护 DEC/CHG。
3. 架构与规格节点：输出对象、流程、状态、功能、IA、页面、组件、AC 和测试追溯。
4. Ready for Prototype 网关：高影响歧义进入 Needs Decision；通过后建立独立 `ProjectUIProfile`。
5. 模具适配节点：按用户、任务、页面、层级、区域、设备和状态输出 `TemplateFitDecision`，只使用 `exact / extensible / no_match`。
6. 原型与验证节点：no_match 先生成项目级黑白候选和素材 Slot；随后用受控 Generation Request 生成中保真，并分开记录技术、目标用户和交接证据。
7. Handoff Ready 网关：核对 Must、Owner、依赖、风险和 DEC/F/P/TR/AC/T/ART 追溯。
8. 可选运营节点：研究、竞品、路线图、阶段汇报或指标复盘；结果写回 Snapshot，不另建 PRD。
9. 返回审计节点：核对范围、状态、Mock/真实边界和新增假设；未验证产物不得标记 Completed。

## 范围边界

不启用代码执行或源文件生成作为默认能力；技术架构只输出需求级候选方案。专业交付节点必须显式配置并由用户请求触发，不得把发布、部署、推送或外部写入包含在默认授权内。平台变量必须保留 S0–S7、ProjectSnapshot、DEC/CHG 和 Ready Gate 语义。
