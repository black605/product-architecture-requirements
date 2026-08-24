# 原型模具生命周期与登记治理

用于项目级候选模具完成原型验证后，判断是否可以登记到共享模板目录。它管理需求级模板资产的版本、作用域和证据，不执行未授权的 Catalog、Registry、代码仓库或远程发布写入。

## 1. 生命周期

```text
project-candidate
  → in-validation
  → validated
  → registration-requested
  → registered
  → deprecated / superseded
```

| 状态 | 最低证据 | 不能声称 |
|---|---|---|
| `project-candidate` | PTC 存在且绑定当前项目 | 可跨项目复用 |
| `in-validation` | 验证任务、视口、状态和重置方式已建立 | 验证通过 |
| `validated` | 当前项目结构、技术和任务证据通过，隔离扫描通过 | 已进入共享目录 |
| `registration-requested` | Owner、适用范围、版本和 Manifest 完整 | 已登记或已发布 |
| `registered` | 真实目录记录、版本和返回审计存在 | 生产组件/Registry 已可用 |
| `deprecated` | 停用原因、替代版本和历史引用保留 | 可供新项目选择 |

生产组件、A2UI Registry、代码包和部署状态分别记录，不能由 `registered` 推导。

## 2. 验证门槛

候选进入 `validated` 前必须具备：

1. 结构：P0、唯一主操作、入口出口、状态和扩展点通过审计；
2. 隔离：旧文案、用户数据、视觉资产、品牌 Token 和未确认业务规则扫描为空；
3. 技术：声明视口和关键状态能够真实渲染、打开、操作和恢复；
4. 任务：本轮用户任务和成功标准完成验证，明确证据类型与样本边界；
5. 追溯：PUI、UIP、TFD、PTC、ASC、页面、功能、AC、测试和 ART 可互查；
6. 来源：外部设计证据、许可、Owner 和允许复用范围明确。

内部走查只能支持结构/技术证据；没有目标用户或授权 Owner 证据时，只能保持项目级 validated 或 registration-requested，不能自动成为 shared。

## 3. 登记规则

- 登记必须使用 [`../schemas/template-manifest.yaml`](../schemas/template-manifest.yaml)；
- Owner 明确确认 `scope`、适用用户、任务、页面、设备、状态和排除项；
- 新登记模具不携带项目内容和视觉资产；
- 实际目录写入、Registry 注册、Bit export、Git push 或部署需要对应授权和下游能力；`registration.authorized` 默认为 `false`；
- 返回后核对真实模板 ID、版本、目录位置、校验结果和消费状态；
- 缺少返回证据时保持 `registration-requested`，不得手工改为 `registered`。

## 4. 版本策略

- 仅修改说明、示例或不影响结构的元数据：补丁版本；
- 增加可选 Slot、状态或兼容扩展点：次版本，并重跑受影响适配用例；
- 改变主任务、P0、必需区域、主操作、设备兼容或删除状态：主版本，旧版保留并标记兼容性；
- 任一验证后变化都生成新版本，不能覆盖原验证证据；
- 停用保留历史引用和迁移建议，不删除正在被项目引用的版本。

## 5. 新项目使用

共享目录中的 `registered` 模具只能进入候选集合，仍须创建新项目 UIP 并执行完整 TFD。历史命中率、验证次数或同类项目只能提供排序证据，不能跳过适配。

## 6. 验收

- 生命周期状态与证据一一对应，不跨级升级；
- 项目候选不会自动进入共享目录；
- Manifest 明确适用范围、排除项、来源、版本和 Owner；
- 模具变化产生新版本并重新验证；
- deprecated 模具不进入新项目候选；
- 目录登记、Runtime Registry、工程消费和生产部署状态分开。
