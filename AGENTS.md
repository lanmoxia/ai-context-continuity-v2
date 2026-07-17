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

1. 绑定角色 codex-5.6，默认进入架构设计模式。
2. 完整读取 .continuity/session-control/chatgpt/codex-5.6/START.md。
3. 按 START.md 的顺序读取共享规则、本角色规则和本角色接力摘要。
4. 简短汇报当前状态和唯一下一步。
5. 不读取 codex-5.5 或 Antigravity 的角色目录。

## 5.6 终审指令

当用户粘贴的指令明确包含“【角色绑定】CODEX_56_FINAL_REVIEW”时：

1. 绑定角色 codex-5.6，并进入最终审核模式。
2. 完整读取 .continuity/session-control/chatgpt/codex-5.6/START.md。
3. 再读取该指令指定的 Review Pack 或 Task Final Review Pack。
4. 不要求用户先输入“启动56”。

## 启动开发

当用户消息的完整内容是“启动开发”，或完整开发指令包含“【角色启动】启动开发”时：

1. 绑定角色 antigravity-development。
2. 完整读取 .agents/rules/session-router.md，并只执行其中“启动开发”部分。
3. 再完整读取 .continuity/session-control/antigravity/development/START.md。
4. 按 START.md 顺序读取共享规则、本角色规则和本角色接力摘要。
5. 不读取 initial-review、codex-5.5 或 codex-5.6 的角色目录。

## 启动审核

当用户消息的完整内容是“启动审核”，或完整初审指令包含“【角色启动】启动审核”时：

1. 绑定角色 antigravity-initial-review。
2. 完整读取 .agents/rules/session-router.md，并只执行其中“启动审核”部分。
3. 再完整读取 .continuity/session-control/antigravity/initial-review/START.md。
4. 按 START.md 顺序读取共享规则、本角色规则和本角色接力摘要。
5. 不读取 development、codex-5.5 或 codex-5.6 的角色目录。

## 未绑定状态

如果同一条用户消息同时触发两个或更多角色，停止并要求用户只保留一个启动文字，不得自行选择。

如果新任务没有“启动55”“启动56”“启动开发”“启动审核”或明确的角色绑定：

- 不自行猜测角色。
- 不读取任何角色私有目录。
- 如果用户要求开展本项目的角色工作，只询问应使用哪个启动文字，不自行选择角色。

角色绑定只对当前 Codex 任务有效。更换新任务后必须重新启动。上下文压缩后如果无法确认当前角色，停止工作并请用户重新发送对应启动文字。
