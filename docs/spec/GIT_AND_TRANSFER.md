# Git 与跨电脑接力规格

## 1. 版本控制范围

所有可用于恢复、追溯或审核的数据都提交 Git：

- Project、Config、Document Registry 和 Current。
- Task、Stage 和 Work Order。
- Checkpoint、Handoff 和 Context Pack。
- Evidence、Review Pack、Review Decision 和 Suggested Patch。
- 可重建视图、上一有效状态和完成任务归档。

只排除无法跨电脑使用的运行时机械文件：

```text
.continuity/runtime/write.lock
.continuity/runtime/writer-lease.json
.continuity/runtime/pending/
.continuity/runtime/temp/
.continuity/runtime/cache/
```

持久文件只保存项目相对路径。设备名、进程 ID 和本机绝对路径只能出现在 `runtime/`。

大日志仍受配置的单文件大小限制。超过限制时停止发布，要求调整配置或生成合规归档；不得静默漏交恢复数据。

## 2. Task 分支

每个 active Task 使用独立分支，建议命名：

```text
continuity/TASK-0001-short-title
```

工具创建分支前必须：

- fetch 远端。
- 确认起始分支可以安全 fast-forward。
- 确认没有另一个 active Task。
- 记录任务基线提交。

Stage 不单独建分支。所有 Stage 在同一个 Task 分支依次完成。

## 3. 自动跨电脑发布

显式执行以下命令即代表授权本次自动 commit 和 push，不再二次询问：

```text
continuity transfer publish
```

固定流程：

1. 验证当前分支、active Task、Stage、approved Work Order 和 Writer Lease。
2. 保存最新 Checkpoint，并根据用途生成 Handoff 和 recovery Context Pack。
3. 运行健康检查和配置中的 transfer checks。
4. 扫描路径越界、敏感信息、超大文件和不完整事务。
5. fetch 远端并确认没有分叉。
6. 只暂存当前 Work Order 允许路径和 `.continuity` 可恢复数据。
7. 发现任何其他修改时停止，不使用 `git add -A`。
8. 生成固定格式提交信息并 commit。
9. push 当前 Task 分支。
10. 记录远端、分支和提交哈希，释放本机 Writer Lease。

任一步失败都停止后续动作。禁止自动 force push、rebase、merge、stash、reset 或清理无关文件。

## 4. 跨电脑恢复

```text
continuity transfer resume
```

固定流程：

1. 确认本机目标项目没有未处理修改。
2. fetch 远端。
3. 仅允许把本地 Task 分支安全 fast-forward 到远端状态。
4. 校验最新 transfer commit、状态文件和 Context Pack 哈希。
5. 运行 `doctor`。
6. 领取新的本机 Writer Lease。
7. 生成或验证 implementation Context Pack 后继续。

发现分叉、冲突、缺失对象或状态不一致时停止。工具不自动决定保留哪一边。

## 5. 审核隔离副本

Stage Review Pack 冻结后，工具从精确 Git 提交或源码指纹创建隔离 worktree；无法安全使用 worktree 时使用临时克隆。

审核副本必须：

- 位于正式开发目录之外。
- 绑定 Review Pack ID、manifest 哈希和 Source Fingerprint。
- 允许读取、编辑和运行已批准检查。
- 不能 push、合并或修改正式 Task 分支。

审核中的代码修改导出为 Suggested Patch，记录文件哈希、适用 Pack 和检查证据。Suggested Patch 只作为建议输入，不能自动合并。

## 6. 主分支合并

全部 Stage 和 Task 总体验收通过后，工具生成 Merge Plan。计划至少包含：

- 主分支当前提交和 Task 分支最终提交。
- Task Final Review Pack 与最终结论。
- squash 后文件变化摘要。
- 未解决或已豁免 Finding。
- 计划创建的归档标签和删除的分支。

只有项目所有者确认 Merge Plan 后才能执行：

1. fetch 并安全 fast-forward 主分支。
2. 确认 Task Final Review Pack 仍为 fresh。
3. squash Task 分支为主分支上的一个提交。
4. push 主分支。
5. 在 Task 分支最终提交创建并 push 归档标签，例如 `continuity/archive/TASK-0001`。
6. 标签验证成功后删除本地和远端 Task 分支。

出现冲突或主分支变化时，原 Merge Plan 失效，必须重新生成并确认。
