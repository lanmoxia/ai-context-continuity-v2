# 第一版命令设计

命令名暂定为 `continuity`。所有修改状态的命令都必须经过同一状态仓库，不能让每个命令自己改 JSON。

## 1. 项目

```text
continuity init <项目目录>
continuity status
continuity render
continuity doctor
continuity config validate
continuity migrate --dry-run
continuity migrate --apply <迁移方案编号>
```

- `init`：确认根目录并创建 `.continuity/`，遇到冲突不覆盖。
- `status`：输出当前 Task、Stage、检查点、接力和审核包状态。
- `render`：从 JSON 重建全部 Markdown 阅读页。
- `doctor`：只检查，不默认修复。
- `config validate`：校验配置、检查命令和文档准入表。
- `migrate --dry-run`：生成数据格式迁移方案，不直接修改；`--apply` 只接受仍有效的方案。

## 2. Task 和 Stage

```text
continuity task create
continuity task activate <TASK-ID>
continuity task complete <TASK-ID>

continuity stage add <TASK-ID>
continuity stage start <STAGE-ID>
continuity stage block <STAGE-ID>

continuity work-order create <STAGE-ID> --input <文件>
continuity work-order approve <WORK-ID>
continuity work-order activate <WORK-ID>
```

创建命令优先从一个用户可编辑的输入文件读取目标、范围和验收标准，避免在命令行粘贴长文本。

Work Order 创建时必须拒绝项目讨论、其他 Task 引用和未确认规格，只保留当前执行所需事实。

只有 approved Work Order 可以激活。`approve` 必须记录确认时间和内容哈希。

激活前必须校验：

- 当前没有另一个 active Task 或 Stage。
- 依赖已经满足。
- 允许路径位于项目根目录内。
- Git 基线可记录；非 Git 项目明确降级为仅接力模式。

正式开发模式下，`task activate` 自动创建或校验当前 Task 分支。

## 3. 写入租约

```text
continuity work claim --label <标签>
continuity work renew <LEASE-ID>
continuity work release <LEASE-ID>
continuity work take-over <LEASE-ID> --recovery-plan <编号>
```

同一项目只能存在一个有效 Writer Lease。`take-over` 只接受健康检查生成的有效恢复方案。

## 4. 检查点和接力

```text
continuity checkpoint save --input <文件>
continuity handoff create --kind working --input <文件>
continuity handoff create --kind stage-complete --input <文件>
continuity restore
```

- `checkpoint save`：保存工作中的可靠进度。
- `handoff create`：基于最新检查点生成不可变接力。
- `restore`：生成恢复材料，不修改业务代码。

输入文件采用固定字段，至少区分 `completed`、`remaining`、`unverified`、`risks` 和 `next_action`。缺失关键字段时拒绝创建接力。

## 5. Context Pack

```text
continuity context build --purpose <用途>
continuity context check <CTX-ID>
```

- `build`：按照文档注册表、当前 Task 和用途生成最小上下文包。
- `check`：检查文件哈希、准入类别、Task 归属和内容预算。

没有登记的文件默认拒绝。命令不提供“包含全部文档”选项。

## 6. 检查证据

```text
continuity check run <CHECK-ID>
continuity check import <CHECK-ID> --result <文件>
continuity check verify <EVIDENCE-ID>
```

- `run` 只能执行 `config.json` 中预先批准的参数数组。
- `import` 保存为较低可信级别的外部证据。
- `verify` 比较 Evidence 与当前 Source Fingerprint。

任务文本、接力内容和源码中的字符串不能成为自动执行命令。

## 7. 审核包

```text
continuity review pack <STAGE-ID>
continuity review pack --scope task <TASK-ID>
continuity review check <PACK-ID>
continuity review record <PACK-ID> --gate <GATE-ID> --input <审核结论文件>
continuity review workspace create <PACK-ID>
continuity review patch export <PACK-ID>
```

- `pack`：Stage 模式收集阶段材料；Task 模式聚合全部 Stage 和集成证据。
- `check`：重新计算哈希，判断审核包是否仍为 fresh。
- `record`：保存审核结论，要求引用正确的 Pack ID、manifest 哈希和 Gate ID。
- `workspace create`：从精确提交创建隔离审核副本。
- `patch export`：把审核副本修改保存为 Suggested Patch，不修改正式分支。

## 8. 跨电脑接力

```text
continuity transfer publish
continuity transfer resume
continuity transfer status
```

- `publish`：自动 Checkpoint、Handoff、校验、限定范围 commit 和 push；显式执行后不二次询问。
- `resume`：自动 fetch，只允许 fast-forward，校验后领取新 Writer Lease。
- 发现无关修改、远端分叉或任一安全检查失败时停止。

## 9. 主分支合并

```text
continuity merge plan <TASK-ID>
continuity merge approve <PLAN-ID>
continuity merge execute <PLAN-ID>
```

- `plan`：基于 fresh Task Final Review Pack 生成 squash、归档标签和分支删除计划。
- `approve`：记录项目所有者对计划哈希的确认。
- `execute`：只执行仍有效且已确认的计划；出现主分支变化或冲突时停止。

## 10. 恢复和归档

```text
continuity recover --dry-run
continuity recover --apply <恢复方案编号>
continuity archive task <TASK-ID> --dry-run
continuity archive task <TASK-ID> --apply <归档方案编号>
```

- 默认先生成恢复方案，不直接覆盖。
- `--apply` 只能应用 `doctor` 生成且仍然有效的方案。
- 无法确定正确状态时停止并要求人工选择。
- 归档默认只移动不可变记录，不永久删除。

## 11. 通用输出

每个命令必须：

- 人类模式输出简短中文结果和下一步。
- 支持 `--json`，供其他界面或脚本调用。
- 成功时输出创建或更新的实体 ID。
- 失败时区分输入错误、状态冲突、安全拒绝和内部异常。
- 不在输出中回显完整密钥或大段测试日志。

建议退出码：

```text
0  成功
1  未预期内部错误
2  输入或状态校验失败
3  并发锁或状态版本冲突
4  安全边界或审核新鲜度拒绝
5  检测到可恢复的数据异常
```
