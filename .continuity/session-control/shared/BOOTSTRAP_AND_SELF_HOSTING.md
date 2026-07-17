# 渐进式自托管规则

## 1. 为什么需要这份规则

当前正在开发的产品就是 Continuity。产品尚未具备 Task、Context Pack、Handoff、Review Pack、Transfer 等能力时，不能要求它先用这些能力管理自己的开发。

因此本项目采用渐进式自托管：未实现的能力由外部会话控制层和 Git 临时承担；对应能力通过验收后，立即切换到产品自身执行。

临时流程不得伪装成正式产品状态，也不得创建看起来像由产品生成的 current.json、正式 Context Pack 或正式 Review Pack。

## 2. 当前等级：BOOTSTRAP-L0

当前处于 BOOTSTRAP-L0：

- 产品业务代码尚未开始。
- 产品 CLI 还不能创建正式 Task、Stage、Work Order、Writer Lease 或 Context Pack。
- Task、Stage 和 Work Order 的逻辑身份由已确认文档与角色 HANDOFF 共同记录。
- 5.6维护工作单 JSON 源文件和 Markdown 阅读页。
- 5.5根据已批准工作单生成一次一条的精确开发指令。
- 各窗口使用自己的角色 HANDOFF 接力。
- Git提交负责保存可恢复代码基线。

BOOTSTRAP-L0 不创建假的产品核心状态文件。

## 3. BOOTSTRAP-L0 开发前条件

5.5发出第一条开发指令前必须全部满足：

1. 项目所有者明确批准当前 Work Order。
2. Work Order JSON 状态为 approved，并包含 `approval` 对象：`approved_at` 使用带时区的 RFC 3339 时间，`approved_by` 固定为 `project_owner`，`draft_sha256` 记录批准前完整 draft JSON 文件的小写 SHA-256；不得让哈希字段循环包含自身。
3. Markdown 阅读页与 JSON 内容一致，但 JSON 是唯一权威来源。
4. Git仓库、固定 .gitignore、初始基线提交和当前 Task 分支已经存在。
5. 当前开发环境满足 Work Order 的 Python 版本。
6. 5.5指令列出精确输入文件、当前approved Work Order文件的 SHA-256、允许业务路径、禁止业务路径和检查。
7. 只有一个开发窗口被指定为代码写入者。
8. 已配置名为 `origin` 的远端仓库，并已把主分支和当前 Task 分支安全推送到远端，确保公司与家里电脑都能恢复。

缺少任一条件时不得开发。

## 4. BOOTSTRAP-L0 指令和接力

- 5.5的开发指令必须明确标记为“Bootstrap开发指令”，不能冒充正式 implementation Context Pack。
- 不生成 CTX 编号；指令直接引用精确文件路径和 Work Order SHA-256。
- 开发窗口开始前核对 Work Order 文件哈希。
- 开发窗口只修改允许的业务路径，并按角色规则更新自己的 HANDOFF。
- own HANDOFF 是外部角色状态，不是 Work Order 业务交付，也不是产品核心状态。
- 5.5收到 kf 后检查真实 diff、检查结果和范围，再决定返工或下一步。
- 5.5检查通过后创建或要求创建限定范围的 Bootstrap检查点提交，并把提交ID记录在自己的 HANDOFF。

## 5. 路径解释

Work Order 中的 allowed_paths 和 forbidden_paths约束业务实现与产品核心状态。

角色规则单独授权窗口更新自己的 session-control HANDOFF.md。这个更新：

- 不算 Work Order 的业务输出。
- 不允许扩大到其他 session-control 文件。
- 不允许修改其他角色 HANDOFF。
- 不允许修改 .continuity 中的产品核心状态。
- 必须与业务变更一起保留在Git中。

因此，“禁止修改 .continuity”与“更新自己的角色 HANDOFF”不冲突：前者保护产品核心状态，后者是唯一、明确的外部角色状态例外。

## 6. Bootstrap 跨电脑接力

在 L4 的正式 `transfer publish` 和 `transfer resume` 通过验收前，使用 Git 执行临时接力，但不得创建假的 Transfer 记录。

离开当前电脑前：

1. 当前开发窗口先更新自己的 HANDOFF，并停止继续写代码。
2. 5.5核对允许范围、检查结果和工作区状态。
3. 用户明确要求本次跨电脑发布后，才提交当前 Task 分支。
4. fetch `origin`；发现分叉、冲突或远端异常时停止。
5. 只在能够安全快进时 push 当前 Task 分支；禁止 force push、自动 rebase、自动 merge、stash 或 reset。

在另一台电脑恢复时：

1. 首次使用时 clone 远端仓库；已有仓库时先确认工作区没有未处理修改。
2. fetch `origin`，切换到同名 Task 分支，只允许 fast-forward 更新。
3. 核对最新提交和角色 HANDOFF。
4. 重新创建本机 `.venv`，运行当前 Work Order 要求的环境检查。
5. 新开发窗口按启动规则接力，旧电脑上的窗口不再写代码。

这套临时流程只保存真实 Git 提交和角色接力，不冒充产品已经实现 Transfer。L4 通过后立即停用。

## 7. Bootstrap审核

正式 Review Pack 功能尚未通过验收前，Stage审核使用外部 Bootstrap审核材料：

- 使用前缀 BPACK，不使用正式 PACK ID。
- 绑定精确 Git提交、变更文件清单、diff哈希和检查结果。
- 5.5只给 Gemini 一条当前 GATE-01 指令。
- 5.5的 GATE-02 和高风险时5.6的 GATE-03必须审核同一份 BPACK。
- 代码变化后旧 BPACK 立即失效，并从 GATE-01重新开始。
- Bootstrap审核结果只证明开发过程受控，不冒充产品自身已经实现并强制了审核状态机。

产品 Review Pack 和 Gate能力完成后，必须使用产品重新演练相应流程。

## 8. 自托管切换点

### L1：Task状态自托管

DEV-006通过后：

- 使用正式 init、Task、Stage、Work Order和Writer Lease。
- 停止用角色 HANDOFF代替核心任务状态。
- Bootstrap记录保留为历史，不反向导入未经校验的状态。

### L2：接力自托管

DEV-008通过后：

- 使用正式 Checkpoint、Handoff、Restore和Context Pack。
- 角色 HANDOFF只保留窗口角色恢复，不再重复业务进度事实。

### L3：审核自托管

DEV-011通过后：

- 使用正式 Evidence、Review Pack、Finding和Review Decision。
- 停止创建新的 BPACK。

### L4：跨电脑自托管

DEV-016通过后：

- 使用 transfer publish和transfer resume。
- 停止人工模拟跨电脑发布记录。

### L5：完整自托管

DEV-018和DEV-019通过后：

- 使用 TASK-FINAL、Merge Plan、squash、归档标签和完整归档流程。
- 对整个项目执行一次真实全流程验收。

## 9. 维护边界

本文件属于外部会话控制层，不属于产品规格，不进入业务 Context Pack。

只有5.6架构模式或项目所有者可以修改自托管等级。能力只有在对应Work Order通过检查和审核后才能升级，不能因为“代码看起来已经有了”提前切换。
