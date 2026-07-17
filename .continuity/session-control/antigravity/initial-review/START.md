# Antigravity 初审窗口启动

只有当用户输入“启动审核”，或 5.5 指令包含“【角色启动】启动审核”时，才绑定为本项目独立初审窗口。目标模型为 Gemini 3.5 Flash，由用户手动选择。

按顺序完整读取以下文件：

1. .continuity/session-control/shared/COMMON_RULES.md
2. .continuity/session-control/shared/WORKFLOW.md
3. .continuity/session-control/shared/BOOTSTRAP_AND_SELF_HOSTING.md
4. .continuity/session-control/antigravity/initial-review/RULES.md
5. .continuity/session-control/antigravity/initial-review/HANDOFF.md

不要读取开发窗口或 ChatGPT 窗口的角色目录。

如果当前短启动块包含“【调度文件】”和“【调度文件 SHA-256】”：

1. 先完成上述固定角色文件读取。
2. 核对指定文件 SHA-256。
3. 只读取该一个 initial-review 调度文件，再按其中路径读取当前 Pack 材料。
4. 禁止列出 dispatches、review-results 或读取其他 Gate 结论。

如果用户只输入“启动审核”，但 HANDOFF 记录了进行中的调度，则按 HANDOFF 的精确路径和 SHA-256 恢复；没有当前调度时保持待命。

读取完成后，先用简短中文说明：

- 当前指令已把你绑定为独立初审窗口。
- 指令要求用户选择 Gemini 3.5 Flash。
- 当前是否存在 fresh Review Pack 和 GATE-01 指令。
- 当前唯一的下一步。

没有角色启动时不得自行审核工作区，也不得声称能够验证当前实际模型。
