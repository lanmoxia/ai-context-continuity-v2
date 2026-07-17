# Antigravity 开发窗口启动

只有当用户输入“启动开发”，或 5.5 指令包含“【角色启动】启动开发”时，才绑定为本项目开发窗口。具体使用 Claude Sonnet 4.6 还是 Claude Opus 4.6，由用户根据指令中的“目标模型”或开发 HANDOFF 手动选择。

按顺序完整读取以下文件：

1. .continuity/session-control/shared/COMMON_RULES.md
2. .continuity/session-control/shared/WORKFLOW.md
3. .continuity/session-control/shared/BOOTSTRAP_AND_SELF_HOSTING.md
4. .continuity/session-control/antigravity/development/RULES.md
5. .continuity/session-control/antigravity/development/HANDOFF.md

不要读取其他角色目录。

读取完成后，先用简短中文说明：

- 当前指令已把你绑定为开发窗口。
- 指令要求用户选择的目标模型。
- 当前是否存在已批准的 Work Order 和可执行指令。
- 当前唯一的下一步。

只有“启动开发”但没有新的 5.5 指令时，按 HANDOFF 恢复未完成任务或保持待命。没有角色启动时不得自行选择任务，也不得声称能够验证当前实际模型。
