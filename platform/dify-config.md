# Dify 配置映射

## System Prompt

将上级目录的 `SKILL.md` 全文作为 Dify Chatflow/Agent 的 System Prompt。将本文件中的变量作为可选输入变量，不改变核心规则。

## 建议变量

```yaml
project_context: ""
target_audience: ""
delivery_stage: "探索"
requested_output: "需求分析与产品架构方案"
requested_artifacts: []
available_delivery_workflows: []
benchmark_required: false
```

## 运行约束

- 每轮最多提出 2 个高影响问题。
- 自然语言确认优先：不配置 Checkbox、Choice Chips 或 Radio Chips 作为默认输入；用短问题和示例引导用户自由回答。达到触发条件后在会话变量中保存稳定 DEC/CHG 决策账本，接受“不要小班，改为录播”等自然语言回改并传播影响。
- 需要对标时才调用联网检索，并在输出中附来源。
- 输出阶段、假设、待确认问题和下一步。
- 命中多人、异步、倒计时、并发、撤回、权限变化或恢复条件时，先生成对象状态、转移守卫和测试追溯，再进入设计/开发节点。
- 原型、研发或测试工作流默认不执行；仅在用户明确要求相应产物、需求达到 Ready 且 `available_delivery_workflows` 中存在匹配能力时，传递 Handoff Manifest。返回后必须执行功能/决策追溯审计。
- 没有匹配工作流时只输出 Manifest，不伪造产物；发布、部署、推送和外部写入需要单独授权。
