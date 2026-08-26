# AGENTS.md

## 项目定位

本仓库是 `product-architecture-requirements` Codex Skill 的源项目。它同时维护需求分析规则、ProjectSnapshot 与 Contract、可执行原型 Harness、回归测试和交接协议。

项目地图见 [ARCHITECTURE.md](ARCHITECTURE.md)，质量门槛见 [docs/quality.md](docs/quality.md)。

## Harness Engineering 协作规则

在设计或实现任务期间，Agent 应主动：

- 检查目标、范围、约束和验收标准是否明确；
- 识别缺失的文档、工具、测试、可观测性和安全边界；
- 对非关键缺口采用明确假设并继续；
- 对高风险或不可逆决策请求人工确认；
- 将反复出现的问题转化为可执行约束；
- 在完成任务前运行项目验证，并提供结果证据；
- 提醒代码、架构、需求和文档之间的漂移。

## 持续状态规则

- 不把聊天记忆当作项目唯一事实源；涉及产品状态、Contract、验证或交接的变化必须写入对应项目文件。
- `ProjectSnapshot` 是需求、架构、原型、测试和交接状态的权威来源；更新时保留 revision、事件日志和来源。
- 新项目必须先完成身份判断，使用独立 ProjectUIProfile；默认禁止继承旧项目文案、视觉资产、用户数据、品牌 Token 和业务规则。
- 新规则应优先落在 Schema、Harness、测试或质量门槛中，不只增加自然语言提醒。
- 发现规则、实现、测试、文档之间不一致时，先记录缺口和影响，再决定修复或请求确认。

## 工作方式

1. 先查看 [ARCHITECTURE.md](ARCHITECTURE.md)、[docs/quality.md](docs/quality.md) 和相关需求/决策文档。
2. 明确本次只处理一个核心缺陷或一个可验证目标；高风险变更先写计划。
3. 修改最小必要文件，并同步更新受影响的需求、决策、计划或 Changelog。
4. 使用统一入口 `./scripts/verify` 验证；局部原型问题可执行 `./harness lint` 或对应测试脚本。
5. 汇报实际命令、通过/失败结果、未验证边界和后续风险。

## 安全与权限

- 默认只修改本地仓库内文件；外部推送、发布、目录登记、部署和生产写入必须得到明确授权。
- 不用破坏性 Git 命令覆盖用户已有改动。
- 不把本地预览、静态检查或 Mock 结果描述成真实用户验证、生产接入或上线完成。
