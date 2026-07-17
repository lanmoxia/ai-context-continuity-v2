# 会话控制入口

本目录只管理当前项目的多窗口协作，不属于产品需求、开发工作单或审核证据。

## 新窗口怎么启动

Codex 新窗口使用根目录 AGENTS.md 自动路由：

- Codex 5.6 架构窗口：输入“启动56”。
- Codex 5.5 协调窗口：输入“启动55”。
- Codex 5.6 终审窗口：直接粘贴 5.5 生成的完整终审指令。

Antigravity 使用简单中文启动文字：

- 新开发任务：直接粘贴 5.5 生成的完整开发或返工指令，指令自带“启动开发”。
- 开发窗口中途换新 Conversation：输入“启动开发”。
- 新初审任务：直接粘贴 5.5 生成的完整 GATE-01 指令，指令自带“启动审核”。
- 初审窗口中途换新 Conversation：输入“启动审核”。

根目录 `AGENTS.md` 同时包含 Antigravity 的后备路由。即使 Workspace Rule 没有在 Antigravity 界面启用，只要代理读取根规则，也能把“启动开发”和“启动审核”转到正确角色。`.agents/rules/session-router.md` 仍应作为 Workspace Rule 启用，形成双入口但执行同一套规则。

不要让任何窗口读取整个 session-control 目录。

首次开始开发前，按 `SMOKE_TEST.md` 分别用新窗口演练四个启动词。

## 文件分工

- shared：所有窗口共同遵守的边界和流程。
- BOOTSTRAP_AND_SELF_HOSTING.md：产品开发自身时使用的临时引导和分阶段自托管边界。
- RULES.md：当前角色的固定职责。
- COMMANDS.md：Codex 5.5 使用的快捷指令协议。
- PROJECT_BRIEF.md：只供5.6架构模式使用的项目初衷、已确认架构和文档地图。
- OWNER_PREFERENCES.md：项目所有者长期稳定的沟通与协作偏好。
- HANDOFF.md：当前角色最新的可恢复现场，只能由该角色或项目所有者更新。
- ROLE_REGISTRY.json：角色文件白名单；全部文件禁止进入业务 Context Pack。

## 重要边界

角色规则是提示词输入层，业务 Context Pack 是事实输入层。两者必须分别读取，不能互相复制。
