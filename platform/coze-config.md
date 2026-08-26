# Coze 配置映射

## Bot 人设/系统指令

将上级目录的 `SKILL.md` 全文粘贴到 Bot 的人设与指令字段。将 `references/meta-prompt.md` 作为维护者测试时使用的独立指令，不作为普通用户默认开场白。

## 建议工作流节点

1. Project Identity 节点：输出 `resume / fork / new / needs_confirmation`，确定项目隔离和继承边界。
2. Snapshot 节点：初始化/增量更新 `ProjectSnapshot`，使用 revision 和事件日志防止覆盖。
3. 需求收拢节点：探索阶段每轮只问 1 个高影响自然语言问题，维护 DEC/CHG。
4. 架构与规格节点：输出对象、流程、状态、功能、IA、页面、组件、AC 和测试追溯。
5. Ready for Prototype 网关：高影响歧义进入 Needs Decision；通过后建立独立 `ProjectUIProfile`。
6. 模具适配节点：按七维输出 `exact / extensible / no_match`；no_match 创建 project-local 候选和素材 Slot。
7. Contract 编译节点：生成 PUI、Frame、Flow 与受控 Generation Request；失败时不进入渲染。
8. Harness 节点：在已配置执行环境时运行 `lint → render → test → report`，分开记录浏览器、视觉、目标用户和交接证据。
9. Handoff Ready 网关：核对 Must、Owner、依赖、风险、HPKG 与 DEC/F/P/TR/AC/T/ART 追溯。
10. 运营与返回审计：研究/指标写回 Snapshot；未验证产物不得标记 Completed。

## 范围边界

没有代码执行和真实浏览器能力时只输出 Frame/Flow、Generation Request 与 Handoff，不伪造 Harness 通过。专业交付节点必须显式配置并由用户请求触发；发布、部署、推送或外部写入不包含在默认授权内。平台变量必须保留 S0–S7、ProjectSnapshot、DEC/CHG 和 Ready Gate 语义。
