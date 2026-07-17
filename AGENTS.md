# Codex 会话角色路由

本文件由 Codex 在新任务开始时自动读取。不要尝试判断当前使用的模型名称；只根据用户明确提供的启动文字绑定角色。

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

## 未绑定状态

如果新任务没有“启动55”“启动56”或明确的 CODEX_56_FINAL_REVIEW 角色绑定：

- 不自行猜测角色。
- 不读取任何角色私有目录。
- 如果用户要求开展本项目的角色工作，只询问应启动55还是启动56。

角色绑定只对当前 Codex 任务有效。更换新任务后必须重新启动。上下文压缩后如果无法确认当前角色，停止工作并请用户重新发送对应启动文字。

