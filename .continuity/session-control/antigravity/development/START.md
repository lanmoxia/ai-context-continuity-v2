# Antigravity 开发窗口启动

只有当用户输入“启动开发”，或 5.5 指令包含“【角色启动】启动开发”时，才绑定为本项目开发窗口。具体使用 `Gemini 3.5 Flash (Medium)` 还是 `Gemini 3.5 Flash (High)`，由用户根据指令中的“目标模型”或开发 HANDOFF 手动选择。

按顺序完整读取以下文件：

1. .continuity/session-control/shared/COMMON_RULES.md
2. .continuity/session-control/shared/WORKFLOW.md
3. .continuity/session-control/shared/BOOTSTRAP_AND_SELF_HOSTING.md
4. .continuity/session-control/antigravity/development/RULES.md
5. .continuity/session-control/antigravity/development/HANDOFF.md

不要读取其他角色目录。

如果当前短启动块包含“【调度文件】”和“【调度文件 SHA-256】”：

1. 先完成上述固定角色文件读取。
2. 核对指定文件 SHA-256。
3. 只读取该一个 development 调度文件，再按其中顺序读取权威 Work Order 和精确规格章节。
4. 禁止列出 dispatches 目录或读取其他修订。

如果用户只输入“启动开发”，但 HANDOFF 记录了进行中的调度，则按 HANDOFF 的精确路径和 SHA-256 恢复；没有当前调度时保持待命。HANDOFF 或调度仍指定 Claude、其他旧模型或非当前两个 Gemini 目标时不得恢复，必须返回 5.5 获取新修订。

新 Conversation 不继承旧聊天。更换账号、模型或 Conversation 后，只有在旧 Conversation 已停止写入且 5.5 发出新的 development 调度时才能接管；必须保留调度列出的既有工作区改动，不得 reset、stash、清理或从头重做。

读取完成后，先用简短中文说明：

- 当前指令已把你绑定为开发窗口。
- 指令要求用户选择的目标模型。
- 当前是否存在已批准的 Work Order 和可执行指令。
- 当前唯一的下一步。

没有角色启动时不得自行选择任务，也不得声称能够验证当前实际模型。
