# 会话控制入口

本目录只管理当前项目的多窗口协作，不属于产品需求、开发工作单或审核证据。

## 新窗口怎么启动

Codex 新窗口使用根目录 AGENTS.md 自动路由：

- Codex 5.6 架构所有者窗口：输入“启动56”。
- Codex 5.5 协调窗口：输入“启动55”。
- Codex 5.6 终审窗口：粘贴 5.5 生成的短启动块，按其中路径读取当前 final-review 调度文件。

Antigravity 使用简单中文启动文字：

- 新开发任务：粘贴 5.5 生成的短启动块，指令自带“启动开发”、目标模型、调度文件路径和 SHA-256。
- 开发窗口中途换新 Conversation：输入“启动开发”。
- 新初审任务：粘贴 5.5 生成的短启动块，指令自带“启动审核”、目标模型、调度文件路径和 SHA-256。
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
- OPERATOR_PROTOCOL.md：规定 5.6 负责技术决策，人类用户只负责窗口切换和指令转发。
- HANDOFF.md：当前角色最新的可恢复现场，只能由该角色更新；人类操作员不手工维护。
- ROLE_REGISTRY.json：角色文件白名单；全部文件禁止进入业务 Context Pack。
- dispatches/：按 development、initial-review、final-review 保存不可覆盖的调度指令文件。
- bootstrap-packs/：保存不可覆盖、可独立复算的 BPACK 审核输入与检查证据。
- review-results/：按 GATE-01、GATE-02、GATE-03、TASK-FINAL 保存不可覆盖的 Bootstrap 审核结果。

## 重要边界

角色规则是提示词输入层，业务 Context Pack 是事实输入层。两者必须分别读取，不能互相复制。

调度文件只负责路由；BPACK 冻结审核输入与证据；审核结果保存 Gate 结论。三者不得互相复制成多份事实来源。
