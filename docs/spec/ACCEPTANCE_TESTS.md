# 第一版验收场景

这些场景全部通过后，第一版才算可以进入真实项目使用。

## P0：必须通过

### 1. 两个窗口接力

- 窗口 A 创建任务、完成部分修改并生成 Handoff。
- 关闭窗口 A，不向窗口 B提供聊天记录。
- 窗口 B 只读 recovery Context Pack，能够正确说出目标、进度、风险和第一步。

### 2. 意外中断恢复

- 保存 Checkpoint 后继续工作，但不生成 Handoff，直接结束窗口。
- 新窗口恢复到最后 Checkpoint。
- 系统明确说明检查点之后的工作未知，不虚构完成状态。

### 3. 原子写入

- 分别在写临时文件、写不可变记录、替换 `current.json` 时模拟异常退出。
- 重新启动后至少有一份完整、可校验的有效状态。
- 不出现半个 JSON 或指向不存在实体的当前状态。

### 4. 并发写入

- 两个进程同时尝试更新同一状态版本。
- 只允许一个成功；另一个收到明确的占用或版本冲突提示。

### 5. 写入租约

- 两个开发窗口依次申请 Writer Lease。
- 第一个成功，第二个在租约有效期内被拒绝。
- Checkpoint 可以续租；过期租约未经健康检查不能直接接管。

### 6. 上下文污染隔离

- 在 `owner_planning` 文档中加入与当前任务冲突的文字，并准备另一个 Task 的旧接力。
- 生成 implementation 和 review Context Pack。
- 两个 Pack 都不包含该规划文档、旧接力或聊天摘要，manifest 只列当前任务允许文件。
- 源码 fixture 中加入“忽略 Work Order”的文字，manifest 仍把它标记为 `source_data`，不会获得指令权威。
- 新建一个未登记 README 和一个 draft Work Order；两者都不能进入 implementation Context Pack。
- Work Order 批准并激活后才能生成 implementation Context Pack。

### 7. 审核失效

- 生成 Review Pack 并记录通过结论。
- 随后修改受审核代码、任务标准或测试证据。
- 旧结论自动变为 stale，不能用于结单。

### 8. 检查证据失效

- 运行一个已批准检查并保存 captured Evidence。
- 修改源码但不重新运行检查。
- Evidence 自动变为 stale，不能进入正式 Review Pack。

### 9. 路径安全

- 尝试使用 `..`、绝对外部路径或指向项目外的符号链接收集文件。
- 工具拒绝操作，项目外文件不被读取、复制或修改。

### 10. 敏感信息

- 在候选审核材料中放入测试密钥、私钥头或常见 Token 格式。
- 工具阻止生成正式审核包，并指出文件位置，不在报告中回显完整秘密。

### 11. 跨电脑发布与恢复

- 电脑 A 在 Task 分支执行 `transfer publish`。
- 工具自动生成接力、限定范围 commit 并 push，且不二次询问。
- 电脑 B 从空闲或旧副本执行 `transfer resume`，只通过 fast-forward 恢复同一 Task、Work Order、Checkpoint、Context Pack 和源码指纹。

### 12. 自动提交范围

- 在 Work Order 允许路径内外同时制造修改。
- `transfer publish` 拒绝提交，远端不发生变化。
- 清除无关修改后，只提交允许路径和 `.continuity` 可恢复数据；不使用 `git add -A`。

### 13. 审核隔离

- 为 Review Pack 创建隔离 worktree，在其中修改代码并运行检查。
- 正式 Task 分支和开发目录保持不变。
- 修改只能导出为绑定原 Pack 的 Suggested Patch，不能自动合并。

### 14. 必要检查门槛

- 准备未运行、失败和 stale 的 required Evidence。
- 三种情况都不能生成正式 Review Pack。
- required checks 全部 fresh 且通过后才允许生成。

### 15. Stage 与 Task 审核门槛

- 普通 Stage 未通过两道 Gate、高风险 Stage 未通过三道 Gate时，不能批准。
- 修复生成新 Pack 后，旧 Pack 的所有 Gate 结论失效并从第一道重新开始。
- 所有 Stage 通过但 TASK-FINAL 未通过时，Task 不能进入 `approved_for_merge`。

## P1：发布前通过

### 16. 脏工作区

- Task 开始前已有未提交变化。
- 工具要求确认并记录基线指纹。
- 审核包能够区分原有变化和本任务变化，无法区分时必须阻止正式审核。

### 17. 视图可重建

- 删除 `START_HERE.md`、`CURRENT_TASK.md` 和任务 Markdown。
- 使用 JSON 事实重新生成，内容和当前状态一致。

### 18. 状态损坏检查

- 人工制造错误指针、错误状态转换、缺失实体和哈希不符。
- `doctor` 能逐项报告，并且默认不擅自覆盖数据。

### 19. 上下文大小

- 构造包含大量历史接力和长测试日志的任务。
- Context Pack 仍只包含当前摘要和证据路径。
- 超出配置上限时拒绝生成，不静默截断风险。

### 20. 格式迁移

- 准备一个旧 Schema fixture。
- dry-run 不修改任何文件，并生成备份与变更计划。
- 应用迁移后可以读取；中途异常时可以恢复旧版本。

### 21. Windows 路径

- 在包含中文、空格和长路径的目录完成初始化、原子写入和归档。
- 文件被占用时安全停止，不出现复制后删除或部分迁移。

### 22. 完整阶段循环

- 创建 Task 和多个 Stage。
- 至少一次换窗口、一次要求修改、一次重新生成审核包。
- 配置多个 required Review Gate；修改代码后旧 Gate 结论全部失效。
- 最终只有全部 required Gate 对同一个 fresh Pack 通过，才可以完成 Stage 和 Task。

### 23. 确定性与幂等

- 对同一份 JSON 状态连续运行两次 `render` 和 `doctor`。
- 除明确允许的运行时间字段外，生成内容和哈希一致。
- 第二次运行不产生状态版本变化或业务代码修改。

### 24. 离线与日志脱敏

- 在禁止网络的环境执行初始化、任务、接力、恢复和审核包生成。
- 未运行外部检查命令时，核心流程全部成功且不尝试联网。
- 失败日志不包含完整秘密、源码正文或大段检查输出。

### 25. Merge Plan 与归档标签

- Task Final Review 通过后生成 Merge Plan，未确认时不能修改主分支。
- 确认后 squash 为主分支一个提交并 push。
- 先创建并验证归档标签，再删除 Task 分支。
- 主分支或 Task 分支在执行前变化时，原计划失效且不发生部分合并。

## 验收证据

每个场景必须保存：

- 测试输入或 fixture。
- 执行命令。
- 退出码和关键输出。
- 预期与实际结果。
- 是否通过。

不能只写“已测试”或“应该没问题”。
