# 审核与总体验收策略

## 1. 两种审核范围

```text
Stage Review    检查一个阶段的实现和必要证据
Task Final Review
                检查所有阶段集成后的完整需求
```

Review Pack 必须包含 `scope: stage` 或 `scope: task`。两种范围不能混用。

## 2. Stage Review Gate

普通 Stage 默认需要两道顺序审核：

```text
GATE-01 → GATE-02
```

高风险 Stage 增加第三道：

```text
GATE-01 → GATE-02 → GATE-03
```

每道 Gate 都审核同一个 fresh Review Pack：

- 当前 Gate 要求修改时，停止后续 Gate。
- 修复后生成新 Review Pack。
- 旧 Pack 的全部 Gate 结论同时失效。
- 新 Pack 从 GATE-01 重新开始。

核心引擎只保存 Gate ID，不保存具体执行者或客户端名称。

## 3. 风险等级

Work Order 创建时必须声明：

```text
low | normal | high | critical
```

工具可以根据确定性规则自动提高等级，但不能自动降低。自动提高的常见触发项：

- 身份认证、权限、安全或敏感信息处理。
- 数据库 Schema、数据迁移或不可逆数据操作。
- 依赖、锁文件、构建、发布或基础设施变化。
- 公共 API、持久化格式、并发和恢复逻辑变化。
- 超出配置阈值的大范围文件修改。
- Work Order 允许范围之外的实际变化。

人工降低工具判定的等级需要项目所有者明确记录原因，并生成新版 Work Order。

## 4. 必要检查

Work Order 的 required checks 必须全部满足：

- Evidence 为 fresh。
- Source Fingerprint 与 Review Pack 一致。
- 退出码在配置允许范围内。
- 输出通过敏感信息和大小检查。

任一 required check 未运行、失败或 stale，都禁止生成正式 Review Pack。非必要检查失败可以进入包，但必须显著展示。

## 5. Finding 分级

```text
critical  严重安全、数据损坏或完全错误，必须修复
high      主要功能、可靠性或审核可信度问题，必须修复
medium    应修复；项目所有者可明确接受并记录理由
low       轻微问题或改进建议，不阻止通过
info      说明信息，不影响结论
```

Reviewer 不能自行降低 Finding 等级。对 medium 的接受必须绑定 Pack ID、Finding ID、接受人、时间和理由，并进入 Task Final Review。

存在未解决的 critical 或 high Finding 时，任何 Gate 都不能 approve。

## 6. Suggested Patch

审核副本中的修改只生成 Suggested Patch：

- 绑定原 Review Pack 和 Source Fingerprint。
- 包含 patch 哈希、修改说明和检查 Evidence。
- 不改变正式代码和审核结论。
- 由新的 Work Order 明确引用后，才能进入开发流程。

应用 Suggested Patch 后必须重新运行 required checks，并生成新的 Review Pack。

## 7. Task Final Review

所有 Stage 通过后生成 Task Final Review Pack，至少包含：

- Task 目标、范围和全部验收标准。
- 所有 Stage、最终状态和已通过 Pack 的 ID 与哈希。
- Task 分支相对初始基线的完整变化摘要。
- 集成后的最终 Source Fingerprint。
- Task 级 required checks 和 fresh Evidence。
- 所有未解决、已修复和已接受的 Finding。
- Merge Plan 草案。

Task Final Review 使用独立的 `TASK-FINAL` Gate。只有该 Gate 对当前 fresh Task Pack 给出 approve，Task 才能进入 `approved_for_merge`。

最终审核后任何代码、任务验收标准、Evidence 或 Merge Plan 基线变化，都会让 Task Final Review 失效。
