# Final-review dispatches

保存发给 Codex 5.6 的不可覆盖调度文件。

仅在以下两种情况创建：

- high 或 critical 风险 Stage 已完成 5.5 的一次验收，需要 5.6 执行唯一一次 Stage 最终审核。
- 整个 Task 的全部 Stage 已完成，需要 5.6 执行一次 TASK-FINAL 跨阶段总体验收。

low/normal Stage 由 5.5 验收并直接收口，不创建 final-review 调度。

Stage final-review 的额外前置条件是：当前 approved Stage 计划队列已经耗尽，且 BPACK 覆盖整个 Stage 的累计实现。单个中间 Work Order 完成时不得创建。
