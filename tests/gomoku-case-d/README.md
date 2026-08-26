# 用例 D：五子棋好友比拼完整交付回归

本用例最初验证 v2.6.0–v2.6.2 的组合行为，v3.4 继续用它检查入口压缩和生命周期重构没有破坏既有交付约束；它不只检查关键词：

1. 已确认业务规则进入稳定 DEC 决策账本；
2. 多人、倒计时、并发和恢复规则自动触发状态机与测试；
3. 需求 Ready 后建立跨 Skill Handoff Manifest；
4. 高保真原型、研发清单、测试/状态机返回后执行功能与决策追溯；
5. 不把只读评审、文件存在或界面完整误报为发布完成。

## 测试资产

- `scenario.json`：权威输入、确认决策、核心对象、功能和页面范围。
- `latest-response.md`：正式 Codex 运行时基于当前 Skill 对真实产物进行审计后的回复。
- `result.json`：静态规则、正式回复和真实产物三层检查及四维评分。
- `artifact-manifest.json`：本次实际验证文件的路径、大小与 SHA-256。
- `../run_gomoku_case_d.py`：可重复执行的回归脚本。

## 运行

```bash
python3 tests/run_gomoku_case_d.py \
  --run-runtime \
  --artifact-dir "/path/to/gomoku-friend-battle"
```

只复核已保存结果：

```bash
python3 tests/run_gomoku_case_d.py \
  --artifact-dir "/path/to/gomoku-friend-battle"
```

通过条件：Skill 运行表现总分不低于 90、任一维度不低于 15、所有关键静态规则存在、正式回复没有实现代码或多余问题，并且三份真实产物完成内容与追溯审计。产物可以被正确判定为 Blocked；不能因为输入产物存在缺陷而反向扣减 Skill 的审计能力分，也不能把测试用例存在误报为测试已经通过。
