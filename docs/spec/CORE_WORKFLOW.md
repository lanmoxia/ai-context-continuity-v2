# 核心工作流程

## 1. 初始化项目

1. 在业务项目根目录运行初始化。
2. 工具确认目标路径并创建 `.continuity/`。
3. 创建并校验项目配置。
4. 记录项目标识、Git 状态和数据格式版本。
5. 生成空闲状态视图。

初始化不得覆盖业务项目已有同名文件。发现冲突时停止并说明。

## 2. 创建大任务

1. 写清目标、范围和验收标准。
2. 把大任务拆成可以独立验收的 Stage。
3. 检查 Stage 依赖和允许修改的路径。
4. 生成只包含当前任务事实的 draft Work Order。
5. 项目所有者确认 Task、Stage 和 Work Order。
6. 工具把 Work Order 标记为 approved，创建 Task 分支，再激活任务现场。

“一个 active Task”指同一时间只推进一个会改代码的主需求，不限制有几个窗口参与开发和审核。

## 3. 申请写入权

开始修改业务代码前申请 Writer Lease：

- 没有有效租约时可以领取。
- 已有租约时拒绝第二个写入者。
- 租约超时后先运行健康检查，再显式接管。
- 只读检查和冻结审核包读取不领取写入租约。

## 4. 生成并读取 Context Pack

工具根据工作用途生成不可变 Context Pack。执行者只读取：

1. `manifest.json`。
2. `START.md`。
3. manifest 中的当前 Work Order 和其他 `required_files`。
4. 触发明确条件后才读取 `optional_files`。

不得扫描全部 `docs/` 或全部历史记录。开始工作前应能说明当前目标、已经完成、尚未完成和第一步。现场不一致时运行健康检查。

没有 active 且 approved 的 Work Order 时，禁止生成 implementation Context Pack。

## 5. 工作中保存检查点

完成一个有意义的小步骤后创建 Checkpoint，例如：

- 完成一组相关文件修改。
- 完成一次可重复验证。
- 即将进行风险较大的重构。
- 当前窗口上下文明显变长。

检查点保存进度摘要、证据位置和 Source Fingerprint，不复制完整源码或日志。保存成功后续租 Writer Lease。

## 6. 正常换窗口

1. 运行配置中已批准的必要检查并保存 Evidence。
2. 创建最新 Checkpoint。
3. 补充未完成、未验证、风险和下一步。
4. 生成 Handoff。
5. 释放旧 Writer Lease。
6. 为恢复用途生成新的 Context Pack。
7. 新窗口领取写入租约后继续。

同一 Stage 内换开发窗口只创建 `working` Handoff，不生成审核包。

## 7. 跨电脑接力

公司或当前电脑执行 `transfer publish`：

1. 自动创建 Checkpoint、Handoff 和 recovery Context Pack。
2. 校验 Work Order 范围、状态、transfer checks 和远端分支。
3. 只提交允许的业务文件和 `.continuity` 可恢复数据。
4. 自动 commit 并 push Task 分支。
5. 成功后释放本机 Writer Lease。

另一台电脑执行 `transfer resume`：

1. 本地无未处理改动时自动 fetch。
2. 仅执行安全 fast-forward。
3. 校验 Transfer Record 和全部状态哈希。
4. 领取新 Writer Lease 并读取 implementation Context Pack。

任一端发现分叉、冲突或无关修改时停止，不自动合并或清理。

## 8. 窗口意外中断

1. 工具检查 pending 事务、租约和最新有效 Checkpoint。
2. 生成 recovery 用途的 Context Pack。
3. 恢复最后可靠状态。
4. 明确显示“最后检查点之后的工作未知”。
5. 重新计算 Source Fingerprint，标记检查点之后的源码变化。
6. 经人工确认后接管过期租约并继续。

系统不能恢复没有写入文件的聊天内容，这是明确边界。

## 9. Stage 完成和审核

1. 对照 Stage 验收标准运行已批准检查并保存 Evidence。
2. 创建 `stage_complete` Handoff。
3. 确认 Handoff、Evidence 和当前源码指纹一致。
4. 冻结 Review Pack，并计算 manifest 哈希。
5. 普通 Stage 顺序执行两道 Gate，高风险 Stage 执行三道；每道只针对该 Pack 给出结论。
6. 任一 Gate 要求修改，Stage 回到开发状态，根据 Findings 创建新版 Work Order；修复后必须生成新 Pack，旧 Gate 结论全部失效。
7. 全部 required Gate 对同一个 fresh Pack 通过后，Stage 进入 `approved`，随后结单或进入下一 Stage。

审核结论不直接绑定“当前目录”，而是绑定一个不可变审核包。

审核在隔离 worktree 或临时克隆中进行。审核修改只导出 Suggested Patch，由新版 Work Order 接回开发流程。

## 10. Task 总体验收与合并

1. 全部 Stage 通过后生成 Task Final Review Pack。
2. 运行 Task 级 required checks。
3. TASK-FINAL Gate 审核完整需求、集成代码、历史 Finding 和最终证据。
4. 通过后 Task 进入 `approved_for_merge`。
5. 工具生成 squash Merge Plan。
6. 项目所有者确认计划后，工具合并并 push 主分支。
7. 创建并 push Task 归档标签，验证成功后删除 Task 分支。

任何代码、证据、主分支基线或计划内容变化都会使 Final Review 或 Merge Plan 失效。

## 11. Git 边界

- 普通 Checkpoint 和 Handoff 可以在非 Git 目录使用。
- 正式 Review Pack 第一版要求 Git。
- Task 开始时记录基线提交和已有未提交变化。
- 如果工作区原本不干净，必须明确记录旧变化，不能把它们算成本任务成果。
- `.continuity/` 除 `runtime/` 外全部进入 Git；持久记录只能保存项目相对路径。
- 自动流程不执行 force push、rebase、冲突合并、stash、reset 或清理。

## 12. 内容控制

默认目标：

- Context Pack 的 `START.md` 不超过约 2,000 个中文字符。
- 单份 Handoff 阅读页不超过约 3,000 个中文字符。
- 启动恢复材料总量不超过约 12,000 个字符，不含按需读取的源码。

超过目标时拒绝生成运行时 Context Pack，要求压缩摘要或把详细证据改为按需引用；不得静默截断关键风险。

## 13. 完成与归档

Task 完成后冻结最终状态和验收证据。旧 Checkpoint、Handoff、Context Pack 和 Review Pack 可以移动到归档区，但内容和哈希不变。第一版不自动永久删除。
