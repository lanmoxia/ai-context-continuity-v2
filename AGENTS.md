# 会话角色总路由

本文件是 Codex 与 Antigravity 兼容代理都可读取的根路由。不要尝试判断当前使用的平台或模型名称；只根据用户明确提供的启动文字绑定角色。

## 启动55

当用户发送“启动55”时：

1. 绑定角色 codex-5.5。
2. 完整读取 .continuity/session-control/chatgpt/codex-5.5/START.md。
3. 按 START.md 的顺序读取共享规则、本角色规则、命令协议和本角色接力摘要。
4. 简短汇报当前状态和唯一下一步。
5. 不读取 codex-5.6 或 Antigravity 的角色目录。

## 启动56

当用户发送“启动56”时：

1. 绑定角色 codex-5.6，默认进入架构所有者模式。
2. 完整读取 .continuity/session-control/chatgpt/codex-5.6/START.md。
3. 按 START.md 的顺序读取共享规则、本角色规则和本角色接力摘要。
4. 由 5.6 自行完成技术判断、工作单拆分和批准；用户不是技术审批者。
5. 简短汇报结论，并给出用户下一步只需复制的短指令。
6. 不读取 codex-5.5 或 Antigravity 的角色目录。

## 5.6 终审指令

当用户粘贴的指令明确包含“【角色绑定】CODEX_56_FINAL_REVIEW”时：

1. 绑定角色 codex-5.6，并进入最终审核模式。
2. 完整读取 .continuity/session-control/chatgpt/codex-5.6/START.md。
3. 核对并读取短启动块指定的一个 final-review 调度文件，再读取该文件指定的 Review Pack 或 Task Final Review Pack。
4. 不要求用户先输入“启动56”。

## 启动开发

当用户消息的完整内容是“启动开发”，或短启动块包含“【角色启动】启动开发”时：

1. 绑定角色 antigravity-development。
2. 完整读取 .agents/rules/session-router.md，并只执行其中“启动开发”部分。
3. 再完整读取 .continuity/session-control/antigravity/development/START.md。
4. 按 START.md 顺序读取共享规则、本角色规则和本角色接力摘要。
5. 不读取已停用的 initial-review、codex-5.5 或 codex-5.6 的角色目录；当前模型由用户在 Antigravity 中手动选择，不作为角色绑定条件。

## 启动审核（已停用）

当用户消息的完整内容是“启动审核”，或短启动块包含“【角色启动】启动审核”时：

1. 不绑定审核角色，也不开始审核。
2. 不读取 initial-review 的 HANDOFF、历史调度或历史审核结果。
3. 简短说明独立 Antigravity 初审已经停用；low/normal Stage 由 Codex 5.5 一次验收后收口，high/critical Stage 才由 Codex 5.6 终审一次。
4. 要求用户回到 Codex 5.5 窗口继续当前流程。

## 未绑定状态

如果同一条用户消息同时触发两个或更多角色，停止并要求用户只保留一个启动文字，不得自行选择。

如果新任务没有“启动55”“启动56”“启动开发”或明确的 5.6 终审角色绑定：

- 不自行猜测角色。
- 不读取任何角色私有目录。
- 如果用户要求开展本项目的角色工作，只询问应使用哪个启动文字，不自行选择角色。

角色绑定只对当前 Codex 任务有效。更换新任务后必须重新启动。上下文压缩后如果无法确认当前角色，停止工作并请用户重新发送对应启动文字。
