# 开发任务拆分

本文件是项目所有者使用的内部排期，不进入实现或审核 Context Pack。任务必须按依赖顺序完成，每项单独测试和审核。

## 第一组：可靠状态底座

### DEV-001 工程骨架

- 建立 Python 包、CLI 入口、架构规定的包边界和三层测试目录。
- 验收：空项目可以安装并运行 `continuity --help`。

### DEV-002 Schema 与领域模型

- 分成两张 Work Order，避免单个开发窗口一次读取和修改过多内容。
- WORK-0002：只定义 Project、Config、Current、Task、Stage、Work Order、Checkpoint、Handoff、Evidence、Context Pack、Review Pack 和 Review Decision Schema，并实现离线 Schema registry。
- WORK-0003：在 WORK-0002 审核通过后，再实现合法状态转换和跨实体约束。
- 依赖：DEV-001。
- 验收：WORK-0002 的合法/非法结构 fixture 全部通过；WORK-0003 的合法转换和跨实体约束逐项通过。

### DEV-003 状态仓库

- 实现统一读取、编号、状态版本、原子替换和上一版本保留。
- 实现 pending 事务、短时独占文件锁和异常恢复入口。
- 依赖：DEV-002。
- 验收：并发和分步骤异常退出测试通过。

### DEV-004 路径安全

- 解析真实路径，阻止绝对越界、`..` 和符号链接逃逸。
- 依赖：DEV-001。
- 验收：路径安全 P0 场景通过。

## 第二组：任务和接力

### DEV-005 初始化与视图生成

- 实现基础结构化日志，禁止记录源码正文、完整密钥或大段检查输出。
- 实现 `init`、配置校验、Schema 版本检查、`render` 和基础目录模板。
- 所有 Markdown 只从 JSON 生成。
- 依赖：DEV-003、DEV-004。

### DEV-006 Task 与 Stage

- 实现 Task、Stage、Work Order 的创建、激活、阻塞、完成和单 active 约束。
- 实现 Work Order 的 draft、approved、active、superseded 状态转换和确认哈希。
- 实现 Writer Lease 的领取、续租、释放和受控接管。
- 记录 Git 基线或非 Git 降级状态。
- 依赖：DEV-005。

### DEV-007 Checkpoint

- 实现结构化进度保存、文件清单、Source Fingerprint 和租约续期。
- 依赖：DEV-006。

### DEV-008 Handoff 与 Restore

- 实现两类 Handoff、Context Pack、文档默认拒绝、恢复页和异常中断提示。
- 依赖：DEV-007。
- 验收：两个窗口接力、异常中断恢复场景通过。

## 第三组：审核可信度

### DEV-009 Git 证据采集

- 统一生成包含 HEAD、暂存、未暂存和未跟踪文件的 Source Fingerprint。
- 记录基线提交、脏工作区、变更文件和 diff。
- 禁止把无法归属的旧变化静默算入当前任务。
- 依赖：DEV-006。

### DEV-010 Review Pack

- 生成冻结目录、manifest、文件哈希、大小限制和排除规则。
- 实现已批准检查的安全执行、captured/imported Evidence 和新鲜度校验。
- 依赖：DEV-008、DEV-009。

### DEV-011 审核结论与失效

- 校验 Pack ID、manifest 哈希和 Review Gate。
- 任一受监控输入变化后把旧结论标记为 stale。
- 只有所有 required Gate 对同一 fresh Pack 通过后才允许批准 Stage。
- 依赖：DEV-010。
- 验收：审核失效 P0 场景通过。

## 第四组：安全恢复和交付

### DEV-012 敏感信息检查

- 检查常见密钥、私钥和 Token 格式，输出脱敏位置。
- 依赖：DEV-010。

### DEV-013 Doctor 与 Recover

- 检查 Schema、指针、哈希、孤立记录、pending 事务、过期租约和 Context Pack 污染。
- 先给恢复方案，再经明确命令应用。
- 依赖：DEV-003、DEV-008、DEV-011。

### DEV-014 端到端验收夹具

- 建立可重复使用的隔离项目、Git 仓库和异常注入测试框架。
- 覆盖配置迁移、Context Pack 准入、Evidence 失效、原子写入和恢复基础场景。
- 依赖：DEV-012、DEV-013。

### DEV-015 Windows 交付

- 提供基础安装、升级和卸载方式。
- 验证路径包含中文和空格的情况。
- 依赖：DEV-014。

## 第五组：跨电脑与最终集成

### DEV-016 Task 分支与 Transfer

- 自动创建 Task 分支。
- 实现限定 Work Order 范围的 `transfer publish`。
- 实现只允许 fast-forward 的 `transfer resume`。
- 保存可提交的 Transfer Record，排除全部 runtime 文件。
- 依赖：DEV-009、DEV-013、DEV-015。
- 验收：两份隔离克隆可以完整 publish/resume；无关修改和分叉均安全停止。

### DEV-017 隔离审核工作区

- 从精确提交创建 Git worktree，必要时使用临时克隆。
- 限制审核副本不能 push 或修改正式 Task 分支。
- 把审核修改导出为 Suggested Patch。
- 依赖：DEV-010、DEV-015。
- 验收：审核修改和检查不改变正式开发目录。

### DEV-018 Task Final Review 与 Merge Plan

- 聚合全部 Stage Pack、Task 验收标准、集成 Evidence 和 Finding。
- 实现 TASK-FINAL Gate、`approved_for_merge` 和失效规则。
- 实现需项目所有者确认的 squash Merge Plan。
- 合并后创建归档标签，再删除 Task 分支。
- 依赖：DEV-011、DEV-016、DEV-017。

### DEV-019 全流程验收与归档

- 覆盖跨电脑接力、两道/三道 Stage Gate、Suggested Patch 和总体验收。
- 验证 `.continuity/` 除 `runtime/` 外全部进入 Git。
- 实现只移动不永久删除的完成任务归档。
- 依赖：DEV-012、DEV-013、DEV-018。

### DEV-020 Windows 最终交付

- 在中文、空格和长路径下验证完整流程。
- 完成安装、升级、迁移、卸载和故障恢复说明。
- 依赖：DEV-019。

## 开发门槛

- DEV-001 开始前，`planning/DECISIONS.md` 的待确认选择必须确认。
- 每项任务必须先有测试，再进入下一项。
- 不允许为了赶进度绕过 Schema、状态仓库或路径安全层直接写文件。
- 每个实现 Work Order 只引用 `document-registry.json` 允许的 accepted 规格，不引用本文件全文。
