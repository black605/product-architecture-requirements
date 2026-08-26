# 原型模具目录

用于维护可被原型阶段检索的页面骨架与插槽结构。目录只保存可复用的结构、语义和状态能力，不保存项目文案、用户数据、品牌资产或业务规则。

## 1. 模具定义

每个模具使用稳定 `TPL-` ID，并至少声明：

| 维度 | 要求 |
|---|---|
| 身份 | `template_id`、名称、版本、状态、作用域、来源 |
| 适用对象 | 目标用户、核心任务、页面类型 |
| 页面结构 | P0/P1/P2 能力、必需区域、可选区域、主操作位置 |
| 设备约束 | 设备类型、视口范围、方向、输入方式、密度 |
| 插槽与变体 | 必需/可选插槽、区域扩展点、允许变体和组合限制 |
| 状态能力 | loading、empty、error、no_permission、disabled、partial_data、extreme_content 与领域状态 |
| 继承边界 | 允许复用的结构和明确禁止携带的内容 |
| 证据状态 | `project-candidate / validated / registered / deprecated` |

详细结构使用 [`../schemas/template-definition.yaml`](../schemas/template-definition.yaml)。模板描述的是能力，不以某张截图、相似颜色或组件名称代替适用条件。

## 2. 作用域

- `project-local`：只允许当前 `project_id` 使用；新生成候选默认处于此作用域。
- `shared`：通过验证和登记后可被其他项目检索，但仍须重新执行适配检查。
- `restricted`：只允许声明的产品线、设备、角色或安全范围使用。

模板被登记为 `shared` 不等于任何新项目可以直接套用，也不等于组件、Registry 或生产代码已经发布。

## 3. 目录索引

目录检索键至少包含：

```text
target_users + primary_tasks + page_types + device_profiles
+ required_regions + supported_states + template_version + scope
```

命中缓存只能缩小候选集合，不能跳过 Profile 比对。候选排序可以参考历史验证结果，但不能只以视觉相似度、业务名称相似度或最近使用时间决定。

本仓库的可执行索引位于 [`../assets/prototype-harness/templates/registry.json`](../assets/prototype-harness/templates/registry.json)。该索引只保存已登记的中性结构和组件白名单；Golden Case、项目生成页和 `PTC-` 不会自动进入索引。

## 4. 内容与资产隔离

模板允许保存语义化占位定义，例如 `course-cover-slot`、`primary-action-label-slot`；禁止保存可直接流入新项目的真实文案、用户数据、旧项目图片、插画、音视频和品牌 Token。示例内容必须标记 `example-only`，生成项目实例时清空。

## 5. 目录质量门槛

- 每个模具都有适用用户、任务、页面、设备、区域和状态声明；
- 每个必需插槽有缺失行为，每个可选区域有坍缩规则；
- 版本升级说明兼容性；破坏 P0、主任务或关键状态时创建新主版本；
- 候选、已验证、已登记和生产组件状态分开；
- 停用模具不进入新项目候选，但历史项目仍保留版本引用。

候选的验证、登记、版本升级和停用按 [原型模具生命周期与登记治理](prototype-template-lifecycle.md) 执行。只有真实目录返回证据存在时，状态才可为 `registered`。
