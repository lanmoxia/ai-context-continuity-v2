# 核心数据模型

## 1. 关系

```text
Project
  └─ Task（第一版最多一个 active）
       └─ Stage（同一任务最多一个 active）
            ├─ Work Order（一次具体开发尝试）
            ├─ Checkpoint（工作中，可多次创建）
            ├─ Handoff（换窗口时创建）
            ├─ Evidence（检查结果）
            └─ Review Pack（Stage 审核）
                  └─ Review Finding / Decision

Context Pack 按用途引用上述实体，但不复制或改写它们。

Task 另有 Task Final Review Pack、Transfer Record 和 Merge Plan。
```

检查点解决意外中断，接力解决有计划的换窗口，审核包解决“审核结论对应哪一版代码”。三者不能混成一种文件。

## 2. 当前状态

`current.json` 只保存指针，不保存任务全文。

```json
{
  "schema_version": 1,
  "state_revision": 12,
  "active_task_id": "TASK-0001",
  "active_stage_id": "STAGE-02",
  "active_work_order_id": "WORK-0003",
  "latest_checkpoint_id": "CHECKPOINT-0008",
  "latest_handoff_id": "HANDOFF-0003",
  "latest_context_id": "CTX-0004",
  "active_review_pack_id": null,
  "latest_transfer_id": "TRANSFER-0002",
  "task_final_review_pack_id": null,
  "active_task_branch": "continuity/TASK-0001-short-title",
  "updated_at": "2026-07-17T15:00:00+08:00"
}
```

每次更新必须携带调用者读到的 `state_revision`。版本不一致时拒绝覆盖，要求重新读取。

### 2.1 Project 与 Config

`project.json` 保存不可随意变化的项目身份：项目 ID、规范化根路径、创建时间和数据格式版本。

`config.json` 保存可调整策略：Git 模式、上下文预算、写入租约、保留策略、安全限制和已批准检查。配置变更也会递增状态版本并记录文件哈希。

### 2.2 Source Fingerprint

需要证明材料对应同一版源码时，统一使用 Source Fingerprint：

- Git HEAD。
- 暂存区 diff 的 SHA-256。
- 未暂存 diff 的 SHA-256。
- 任务允许路径内未跟踪文件的路径、大小和内容哈希。
- 生成时间。

Checkpoint、Handoff、Evidence 和 Review Pack 使用同一算法。只比较 `git status` 文本不足以判断源码是否一致。

## 3. Task

Task 表示用户的一项完整需求。

必填字段：

- `id`：稳定编号。
- `title`：简短名称。
- `goal`：最终要得到什么结果。
- `scope_in` / `scope_out`：允许和不允许做什么。
- `acceptance_criteria`：可验证的完成条件。
- `status`：任务状态。
- `created_at` / `updated_at`。

状态：

```text
draft → ready → active → ready_for_final_review → approved_for_merge → completed
                  ├─ blocked
                  └─ cancelled
blocked → active
```

第一版一个项目最多一个 `active` Task。审核中的仍是同一个主任务，不算第二个开发任务。

## 4. Stage

Stage 是大任务中可以独立开发、测试和审核的一段。

必填字段：

- `id`、`task_id`、`title`。
- `goal` 和 `acceptance_criteria`。
- `dependencies`。
- `allowed_paths`：本阶段计划修改的范围。
- `required_checks`：完成前应执行的验证。
- `review_gates`：必须针对同一 Review Pack 通过的通用审核关卡。
- `risk_level`：`low`、`normal`、`high` 或 `critical`。
- `risk_reasons`：人工声明和工具自动提高的原因。
- `status`。

状态：

```text
planned → active → ready_for_review → approved → completed
             ↑            ↓
             └─ changes_requested
active → blocked → active
```

`ready_for_review` 后如果代码变化，审核包会失效，Stage 回到 `active` 或 `changes_requested`。

## 5. Work Order

Work Order 是当前开发执行者唯一需要遵循的任务指令源，采用版本化、只新增设计。

必填字段：

- `id`、`task_id`、`stage_id` 和修订号。
- `goal`。
- `allowed_paths` 和 `forbidden_paths`。
- `required_inputs`：精确文件引用。
- `required_outputs`：代码、文档或证据交付要求。
- `required_checks`。
- `acceptance_criteria`。
- `known_constraints`。
- `risk_level` 和 `required_review_gates`。
- `supersedes_work_order_id`。
- `status`：`draft`、`approved`、`active`、`superseded` 或 `completed`。

Work Order 只写当前任务事实，不包含讨论历史、未来计划、角色人格或其他任务材料。

只有项目所有者确认过的 `approved` Work Order 才能激活并进入 implementation Context Pack。新修订批准后，旧版本变为 `superseded`。

## 6. Checkpoint

Checkpoint 是工作中的轻量保存点，采用只新增、不覆盖。

记录：

- 当前任务、阶段和状态版本。
- 已完成的步骤。
- 正在进行的步骤。
- 已修改文件路径。
- 已运行检查及结果摘要。
- 已知风险。
- 保存时的 Source Fingerprint（如果可用）。
- 当前写入租约 ID。

Checkpoint 不声称窗口已经完成交接。异常恢复时，系统必须提示检查点之后的内容未知。

保存 Checkpoint 的触发点是完成一个明确步骤、重大修改前或换窗口前，不按固定时间自动生成半完成记录。

## 7. Handoff

Handoff 是给下一个窗口的正式接力记录。

必填字段：

- `id`、`task_id`、`stage_id`、`work_order_id`。
- `kind`：`working` 或 `stage_complete`。
- `based_on_checkpoint_id`。
- `completed`、`remaining`、`unverified`。
- `changed_files`。
- `checks`。
- `risks`。
- `next_action`：下个窗口开始后的第一步。
- `source_fingerprint`。
- `created_at`。

结构化 JSON 是事实，`handoff.md` 是生成的阅读页。历史 Handoff 不覆盖。

恢复时重新计算指纹。如果源码已经变化，Handoff 仍可阅读，但必须标记为 `source_changed_after_handoff`。

## 8. Evidence

Evidence 保存一次检查的证据：

- `id`、`task_id`、`stage_id` 和检查 ID。
- `capture_mode`：`captured` 或 `imported`。
- 参数数组、工作目录和超时。
- 开始时间、结束时间、退出码。
- 输出文件路径、大小和 SHA-256。
- 执行时的 Source Fingerprint。
- `status`：`fresh` 或 `stale`。

只有配置中预先批准的检查可以由工具以 `captured` 模式执行。导入结果必须保留较低可信级别，不能伪装成工具直接执行。

## 9. Review Pack

Review Pack 是冻结的审核输入。

`manifest.json` 至少包含：

- `pack_id`、`task_id`、`stage_id`。
- `scope`：`stage` 或 `task`；Task Pack 的 `stage_id` 为 null。
- 任务和阶段文件哈希。
- Git 基线提交和工作区状态。
- 包内每个文件的路径、大小和 SHA-256。
- 引用的 Evidence ID、可信级别和源码指纹。
- 生成器版本。
- `status`：`fresh` 或 `stale`。

审核结论必须引用 `pack_id` 和 `manifest_sha256`。只有绑定当前 fresh 审核包的通过结论，才能让 Stage 进入 `approved`。

Review Decision 必填：

- `review_id`、`pack_id` 和 `manifest_sha256`。
- `gate_id` 和通用审核轮次编号，不绑定具体客户端。
- `verdict`：`approve`、`changes_requested` 或 `needs_human`。
- 结构化 Findings 列表及证据位置。
- 创建时间。

同一个 Gate 对同一个 Pack 只能有一个当前有效 Decision。所有 required Gate 均为 `approve` 后，Stage 才能进入 `approved`。

Stage Pack 默认需要 GATE-01 和 GATE-02；高风险 Stage 增加 GATE-03。Task Pack 使用 TASK-FINAL Gate。

Suggested Patch 必须绑定原 Pack、Source Fingerprint、patch SHA-256 和 Evidence，只能由新版 Work Order 引用，不能直接改变正式分支。

## 10. Context Pack

Context Pack 是不可变的文件路由，不是提示词：

- `id`、`purpose`、Task 和 Stage ID。
- 引用的 Checkpoint、Handoff 或 Review Pack ID。
- 必读、按需和排除文件清单。
- 每个文件的 SHA-256 和 `content_role`。
- 内容预算和生成器版本。

Context Pack 不允许引用未确认规格、项目管理材料、聊天记录、其他 Task 内容或角色私有提示词。

`content_role` 至少区分：`authoritative_spec`、`work_order`、`current_state`、`evidence` 和 `source_data`。源码和证据属于数据，不能因为其中出现命令式文字就升级为任务指令。

implementation Context Pack 创建时必须存在 active 且已批准的 Work Order。项目长期规则或外部规格只有在项目 `document-registry.json` 中明确登记为 accepted，才能标记为 `authoritative_spec`。

## 11. Writer Lease

Writer Lease 是本地运行时记录：

- `lease_id`、项目 ID 和持有者标签。
- 获取、最后续租和到期时间。
- 关联 Task 和 Stage。

同一项目最多一个未过期租约。Checkpoint 可以续租，Handoff 正常释放。超时租约必须先由健康检查确认，再显式接管。

## 12. Transfer Record

Transfer Record 是可提交、可跨电脑读取的 durable 记录：

- `id`、Task、Stage、Work Order 和 Handoff ID。
- Task 分支、本次 commit 和远端引用。
- 已提交文件清单和哈希。
- transfer checks 与结果。
- `status`：`prepared`、`pushed`、`resumed` 或 `failed`。

Writer Lease、进程 ID 和绝对路径不进入 Transfer Record。

## 13. Merge Plan

Merge Plan 记录：

- 主分支基线、Task 分支最终提交和 Task Final Pack。
- squash 变化摘要和提交信息。
- 归档标签名称。
- 未解决和已豁免 Finding。
- 计划哈希、创建时间和确认状态。

主分支、Task 分支或 Final Pack 变化后，Merge Plan 立即失效。

## 14. 不可破坏的约束

- 不能出现两个 active Task。
- 不能出现两个 active Stage。
- 不能出现两个有效 Writer Lease。
- 当前指针引用的实体必须存在。
- active Work Order 必须属于当前 Task 和 Stage。
- Handoff 必须属于当前 Task 和 Stage。
- Review Pack 创建后不能原地修改。
- Context Pack 和 Evidence 创建后不能原地修改。
- Context Pack 不能包含不允许用于当前 purpose 的文档类别。
- Evidence 与 Review Pack 的 Source Fingerprint 必须一致。
- Stage 只有在全部 required Review Gate 对同一 fresh Pack 通过后才能批准。
- Task 只有在全部 Stage 批准且 TASK-FINAL 对 fresh Task Pack 通过后才能进入 `approved_for_merge`。
- Transfer 自动提交不能包含 Work Order 允许范围之外的业务文件。
- Merge Plan 未确认或已 stale 时不能修改主分支。
- 审核通过后代码变化，原结论必须失效。
- Markdown 删除后可以重建，JSON 事实删除后不能靠 Markdown 反向猜测恢复。
