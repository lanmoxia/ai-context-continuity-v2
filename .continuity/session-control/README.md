# 会话控制入口

本目录只管理当前项目的多窗口协作，不属于产品需求、开发工作单或审核证据。

## 新窗口怎么启动

Codex 新窗口使用根目录 AGENTS.md 自动路由：

- Codex 5.6 架构所有者窗口：输入“启动56”。
- Codex 5.5 协调窗口：输入“启动55”。
- Codex 5.6 终审窗口：粘贴 5.5 生成的短启动块，按其中路径读取当前 final-review 调度文件。

Antigravity 只保留开发角色：

- 新开发或返工：先由 5.5 生成短启动块；用户按标题选择 `Gemini 3.5 Flash (Medium)` 或 `Gemini 3.5 Flash (High)`，再把包含“启动开发”、调度路径和 SHA-256 的整块粘贴到新 Conversation。
- 更换账号、模型或 Conversation：旧 Conversation 先停止写入，回到 5.5 生成新的不可覆盖 development 调度；新 Conversation 保留当前工作区改动继续，不 reset、不 stash、不清理、不从头重做。
- 单独输入“启动开发”只用于恢复 HANDOFF 中目标模型仍为当前两个 Gemini 之一的有效调度；旧 Claude 调度不得恢复。
- 独立 Antigravity 初审已经停用；“启动审核”和 `sh` 不能推动当前流程。

根目录 `AGENTS.md` 同时包含 Antigravity 的后备路由。即使 Workspace Rule 没有在 Antigravity 界面启用，只要代理读取根规则，也能把“启动开发”转到正确角色，并拒绝已停用的“启动审核”。`.agents/rules/session-router.md` 仍应作为 Workspace Rule 启用，形成双入口但执行同一套规则。

不要让任何窗口读取整个 session-control 目录。

首次开始开发或协作规则迁移后，按 `SMOKE_TEST.md` 用新窗口演练当前启动路由。

## 文件分工

- shared：所有窗口共同遵守的边界和流程。
- BOOTSTRAP_AND_SELF_HOSTING.md：产品开发自身时使用的临时引导和分阶段自托管边界。
- RULES.md：当前角色的固定职责。
- COMMANDS.md：Codex 5.5 使用的快捷指令协议。
- PROJECT_BRIEF.md：只供 5.6 架构模式使用的项目初衷、已确认架构和文档地图。
- OPERATOR_PROTOCOL.md：规定 5.6 负责技术决策，人类用户只负责窗口切换和指令转发。
- HANDOFF.md：当前角色最新的可恢复现场，只能由该角色更新；人类操作员不手工维护。
- ROLE_REGISTRY.json：活动角色文件白名单和历史角色禁用状态；全部文件禁止进入业务 Context Pack。
- dispatches/development/：保存不可覆盖的开发与返工调度。
- dispatches/pre-final-review/：保存 5.5 自己执行的终审前 Gate 调度。
- dispatches/final-review/：保存 5.6 Stage 最终 Gate 与 TASK-FINAL 调度。
- dispatches/initial-review/：只读历史，不再新增 BREV。
- bootstrap-packs/：保存不可覆盖、可独立复算的 BPACK 审核输入与检查证据。
- review-results/：按 GATE-01、GATE-02、GATE-03、TASK-FINAL 保存不可覆盖的 Bootstrap 审核结果。

## 重要边界

角色规则是提示词输入层，业务 Context Pack 是事实输入层。两者必须分别读取，不能互相复制。

调度文件只负责路由；BPACK 冻结审核输入与证据；审核结果保存 Gate 结论。三者不得互相复制成多份事实来源。
