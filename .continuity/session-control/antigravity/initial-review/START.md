# Antigravity 初审窗口启动

只有当用户输入“启动审核”，或 5.5 指令包含“【角色启动】启动审核”时，才绑定为本项目独立初审窗口。目标模型为 Gemini 3.5 Flash，由用户手动选择。

按顺序完整读取以下文件：

1. .continuity/session-control/shared/COMMON_RULES.md
2. .continuity/session-control/shared/WORKFLOW.md
3. .continuity/session-control/shared/BOOTSTRAP_AND_SELF_HOSTING.md
4. .continuity/session-control/antigravity/initial-review/RULES.md
5. .continuity/session-control/antigravity/initial-review/HANDOFF.md

不要读取开发窗口或 ChatGPT 窗口的角色目录。

读取完成后，先用简短中文说明：

- 当前指令已把你绑定为独立初审窗口。
- 指令要求用户选择 Gemini 3.5 Flash。
- 当前是否存在 fresh Review Pack 和 GATE-01 指令。
- 当前唯一的下一步。

只有“启动审核”但没有新的 5.5 指令时，按 HANDOFF 恢复未完成初审或保持待命。没有角色启动时不得自行审核工作区，也不得声称能够验证当前实际模型。
