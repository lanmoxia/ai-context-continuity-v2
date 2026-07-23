# Development dispatches

保存发给 Antigravity 开发窗口的不可覆盖调度文件。新调度不绑定具体模型，用户在同一开发会话中手动选择当前有额度的模型。

每份新调度必须绑定当前 approved Stage 计划及其中一张 approved Work Order。5.5 按计划顺序一次只创建一条；当前 Work Order 验收后，如队列仍有下一张则直接继续调度，不回 5.6 索要。
