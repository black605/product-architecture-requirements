# Dify 配置映射

## System Prompt

将上级目录的 `SKILL.md` 全文作为 Dify Chatflow/Agent 的 System Prompt。将本文件中的变量作为可选输入变量，不改变核心规则。

## 建议变量

```yaml
project_context: ""
target_audience: ""
delivery_stage: "探索"
requested_output: "需求分析与产品架构方案"
benchmark_required: false
```

## 运行约束

- 每轮最多提出 2 个高影响问题。
- 自然语言确认优先：不配置 Checkbox、Choice Chips 或 Radio Chips 作为默认输入；用短问题和示例引导用户自由回答。保存决策摘要与影响范围，并接受“不要小班，改为录播”等自然语言回改。
- 需要对标时才调用联网检索，并在输出中附来源。
- 输出阶段、假设、待确认问题和下一步。
- 不连接代码生成节点；如用户要求实现，转为需求级接口/数据说明并说明范围边界。
