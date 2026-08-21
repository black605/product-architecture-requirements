# 五角色 50 轮对话回归

本测试覆盖教师/业务专家、产品经理、UI/UX 设计师、运营、研发/技术负责人五类角色，各 10 轮；由 10 条会话路径组成，每条路径包含 5 个带“此前已确认用户信息”的独立真实运行时会话。

## 执行方式

```bash
python3 tests/run_formal_platform_50.py \
  --cases-json tests/role-dialogue-50-v2.json \
  --project-context '' \
  --workers 4 \
  --rounds 1-50 \
  --expect-count 50 \
  --output tests/role-dialogue-50/<version>
```

`--project-context ''` 是必要条件：角色化测试不得向口语课程、内容运营、分销或研发案例注入无关的“高考备考专区”固定背景。

## 基线与回归口径

- `v3.4.4-baseline/`：运行器诊断记录，因错误注入固定项目背景，不用于体验结论。
- `v3.4.4-role-baseline/`：无污染有效基线，50/50 通过基础运行约束；其体验审查见同目录 `review.md`。
- `v3.4.5-low-friction/`：同一矩阵的修复后正式回归，50/50 通过；量化对比与人工审查见同目录 `review.md`。
- `v3.4.7-dialogue-quality-final/`：增强矩阵，覆盖五角色各 10 轮、40 个探索场景与 10 个交付场景；增加 250 字、单决策、纯文本、上下文隔离、Ready/Blocked 互斥和高影响资金 Gate 检查，50/50 通过。
- 低摩擦回归除基础运行约束外，还要检查：角色化人话开场、探索阶段单问题推进、不重复已确认事实、5W2H 不问卷化、内部术语仅在规格/交接时外露。
