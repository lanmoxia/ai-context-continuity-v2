# BFINAL-0001-r1

## 调度元数据

- 类型：Bootstrap final-review dispatch
- 调度 ID：BFINAL-0001
- 修订：r1
- 生成时间：2026-07-20T11:58:22+08:00
- 准备者：Codex 5.5
- 调度责任角色：Codex 5.5
- 目标角色：Codex 5.6 final review
- 执行模式：BOOTSTRAP-L0；本文件不是正式 Review Pack

## 精确绑定

- Task：TASK-0001
- Stage：STAGE-02
- 计划项：DEV-002
- Work Order：WORK-0002
- Task 分支：`continuity/TASK-0001-project-foundation`
- 实现检查点：`bf0cd41aca43f144392c78b221208587df25e494`
- BPACK：`.continuity/session-control/bootstrap-packs/BPACK-0002.json`
- BPACK SHA-256：`8173f72deaa6edaf034ac621345bce23d2a6982935d22cf522cca190fae7b53e`
- BPACK ID：BPACK-0002
- required review gates：GATE-01、GATE-02、GATE-03
- 本调度唯一审核 Gate：GATE-03
- 结果文件：`.continuity/session-control/review-results/gate-03/BGATE03-0001-r1.md`

## 唯一目标

Codex 5.6 对 `BPACK-0002` 独立执行 WORK-0002 的 Stage 最终 Gate：GATE-03。审核必须绑定同一份 fresh BPACK，重新核对实现检查点、Source Fingerprint、diff hash、fresh checks、required inputs、required outputs 和验收标准。

## 审核输入

只读取：

1. 本调度文件全文，并核对短启动块中的 SHA-256。
2. `.continuity/session-control/bootstrap-packs/BPACK-0002.json`，并核对 SHA-256。
3. BPACK 中列出的 required inputs 与 source snapshot entries。
4. BPACK 绑定的实现 diff 和检查证据。

不要读取开发窗口 HANDOFF、5.5 HANDOFF、GATE-01/GATE-02 原始结果、历史审核结果、聊天摘要或 initial-review 材料。GATE-03 必须独立判断，不依赖 5.5 的原始审核结论。

## 结果写入要求

- 写入唯一结果文件：`.continuity/session-control/review-results/gate-03/BGATE03-0001-r1.md`
- 结果必须记录本调度文件路径与 SHA-256、BPACK 路径与 SHA-256、Gate ID、verdict、findings、实现检查点、Source Fingerprint、diff hash 和 required checks 结论。
- 若要求业务代码修改，verdict 必须为 changes requested 或等价不通过结论；5.5 收到 `zs` 后会生成 development 返工调度。
- 若通过，verdict 必须明确 approve / APPROVED。

## 完成回传

完成并写入结果文件后，用户回到 Codex 5.5 窗口输入 `zs`。
