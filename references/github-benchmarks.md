# GitHub 开源项目对标参考

> 用途：当用户要求竞品/开源对标，或当前需求缺少成熟业务模式时，读取本文件，再按需打开官方仓库或官方文档核验。本文只提炼可迁移的产品分析模式，不复制代码、页面或未验证的实现。
>
> 核验日期：2026-08-19

## 1. Plane：工作项、周期与路线图

- 官方仓库：[makeplane/plane](https://github.com/makeplane/plane)
- 可借鉴模式：问题/工作项作为核心对象，周期（cycles）、文档、分诊和路线图作为相互关联的能力。
- 对需求分析的启发：先定义核心对象与生命周期，再把列表、看板、周期视图视为同一对象的不同入口；功能矩阵要记录对象状态、入口和跨模块关联。
- 不应直接推断：仓库中的技术栈、部署方式或具体实现不等于用户项目的技术方案。

## 2. OpenProject：工作包、角色与可追踪交付

- 官方仓库：[opf/openproject](https://github.com/opf/openproject)
- 权限/接口示例：[openproject API example](https://github.com/opf/openproject/blob/dev/docs/api/apiv3/example/README.md)
- 可借鉴模式：工作包承接项目计划、任务、缺陷和交付；角色通过项目成员关系获得权限；对象可与其他交付物关联。
- 对需求分析的启发：权限矩阵要同时描述角色、作用域、可执行动作和对象关联；验收条目要能追溯到工作项或业务目标。

## 3. Outline：知识对象、草稿与继承权限

- 官方接口定义：[outline/openapi](https://github.com/outline/openapi/blob/main/spec3.yml)
- 权限设计讨论：[Outline permission improvements](https://github.com/outline/outline/issues/11760)
- 可借鉴模式：文档、集合、模板、评论、版本和草稿形成内容生命周期；集合和文档层级承载权限；权限继承可以被显式切断并影响子树。
- 对需求分析的启发：信息架构不能只画导航，还要说明对象层级、继承规则、草稿/发布/归档状态和权限断点。

## 4. Penpot：设计系统与设计到开发交接

- 官方仓库：[penpot/penpot](https://github.com/penpot/penpot)
- 组件/Variants/Library 参考：[Penpot MCP initial instructions](https://github.com/penpot/penpot/blob/develop/mcp/packages/server/data/initial_instructions.md)
- 可借鉴模式：设计 Token、组件、Variants 和共享 Library 共同形成可复用的设计系统；Inspect 和 API 连接设计与开发。
- 对需求分析的启发：组件规格不仅记录名称，还要记录变体轴、状态、Token、复用范围、来源和交接方式。

## 使用与约束

1. 对标输出必须区分“仓库事实 / 产品分析推断 / 本项目待确认”。
2. 每次只选择与当前测试用例直接相关的一个模式，不把四个项目的能力全部搬入需求。
3. 需要最新版本、行为或许可证信息时，重新打开官方来源核验，不依赖本文件的旧摘要。
4. 对标只用于发现对象、流程、权限、状态或组件模式；不替用户决定商业规则，也不替项目指定技术框架。
