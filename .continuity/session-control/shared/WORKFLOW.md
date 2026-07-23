# 多窗口协作流程

## 1. 固定角色

- Codex 5.6：架构所有者和高风险最终裁判；负责 Work Order 技术批准、high/critical Stage 终审，以及整个 Task 的 TASK-FINAL。
- Codex 5.5：协调器、日常验收员和 low/normal Stage 的最终验收者；负责一次一条调度、一次验收、冻结 BPACK、普通任务收口、返工和下一步路由。
- Antigravity 开发窗口：不绑定固定模型；用户在同一个开发会话中手动选择当前有额度的模型执行开发或返工。
- Antigravity 初审窗口：停用。任何可用模型都只用于同一个开发角色，不再单独承担初审。

人类用户只负责切换窗口、手动选择当前有额度的 Antigravity 模型、复制短启动块和输入 `kf`、`zs`。技术判断不交给用户。

## 2. 唯一裁判与 Gate 分工

5.5 对每个开发结果只验收一次，不得把同一代码包反复包装成多轮“独立代码审核”。

- low/normal Stage：5.5 在一次验收中核对代码、范围、测试和全部 required Gate 证据；通过后直接作出最终结论并收口，不调用 5.6。
- 高风险或 critical Stage：5.5 在同一次验收中完成最后一道 Gate 之前的语义与证据核对；5.6 只执行最后一道 Gate，作出一次最终裁决。
- TASK-FINAL：始终由 5.6 执行，只检查跨 Stage 整合、最终 E2E、未解决 Finding 和合并准备度，不重新逐文件审核已绑定且未失效的 Stage。

审核唯一键为 `Task + Stage + BPACK + Gate`。同一键已有有效结果时禁止重复调度或新增第二份结论。

5.6 APPROVED 后，5.5 只能核对绑定并收口，不得推翻、重复审核或再次为同一 Stage/BPACK 生成 final-review。

## 3. 一次只发一条指令

5.5 每次只发布当前步骤的一个不可覆盖调度。聊天只显示窗口和任务标题、一个可复制的最小启动块，以及代码块外的一句用户下一步。

复制块内只保留角色启动、调度路径、调度 SHA-256 和哈希失败停止条件。标题也不指定模型；`kf`、`zs` 只放代码块外。

## 4. 开发与初验

1. 5.5 核对 5.6 已批准的 Work Order、Git 基线和单一写入者。
2. 5.5 生成不绑定具体模型的 development 调度。
3. 用户把最小启动块粘贴到 Antigravity 开发 Conversation。
4. 开发窗口完成业务代码、required checks 和自己的 HANDOFF。
5. 用户回到 5.5 输入 `kf`。
6. 5.5 在一个连续动作中核对真实 diff、路径、交付物、验收标准和 fresh checks。
7. 不合格：只生成一条返工 development 调度。
8. 合格：low/normal Stage 记录验收和 required Gate 证据后直接收口；high/critical Stage 冻结 fresh BPACK、记录最后一道之前的 Gate 证据，然后生成一次 5.6 最终调度。

5.5 不要求用户为内部 GATE 切换窗口，也不要求额外快捷指令。

## 5. 5.6 最终裁决

1. 只有高风险或 critical Stage 才进入本节。5.5 生成一个 final-review 调度，只绑定当前 fresh BPACK 和 Stage 最后一道 Gate。
2. 用户把短启动块粘贴到独立 5.6 终审窗口。
3. 5.6 独立裁决，不读取 5.5 原始推理，只核对 Pack、规格、源码和证据。
4. 用户回 5.5 输入 `zs`。
5. 5.5 只核对结果绑定。CHANGES_REQUESTED 时生成返工；APPROVED 时关闭 Stage或请求 5.6 架构窗口准备下一 Work Order。

任何业务代码变化都会使当前 BPACK 和其 Gate 结果 stale；返工后重新冻结，再走一次 5.5 初验和一次 5.6 终审。

## 6. TASK-FINAL

只有所有计划 Stage 都已正式收口，且存在专用 Task Final Review Pack 时，5.5 才能生成 TASK-FINAL。“当前没有下一份 approved Work Order”不等于所有 Stage 已完成。

TASK-FINAL Pack 只提供跨 Stage 接口、最终 E2E、未解决 Finding、Stage 结果索引和合并准备证据。已通过且源码未变化的 Stage 不重复完整代码审核。

## 7. 更换 Conversation

- 开发 Conversation 更换前，旧窗口先停止写入；5.5 生成新的 development 接续调度并列出允许保留的脏文件，不 reset、不 stash、不重做。
- 新 Conversation 不继承聊天，只依赖角色 START、HANDOFF 和短启动块指定的一个调度文件。
- 在同一 Antigravity 开发会话中仅切换模型不需要新调度；模型切换前确认前一个请求已经停止，不允许两个模型同时写文件。

## 8. 快捷指令

- `kf`：开发或返工完成；low/normal 任务由 5.5 一次验收后收口，high/critical 任务再路由一次 5.6 终审。
- `zs`：5.6 Stage 最终 Gate 或 TASK-FINAL 完成，交给 5.5 只做绑定核对和收口。
- `sh`：停用，不推动当前流程。

没有对应项目文件时，快捷指令不能推动流程。

## 9. 在途审核迁移

规则更新前已经生成、且绑定仍 fresh 的 5.6 最终结果继续有效。5.5 处理其 `zs` 时只核对并收口，不得因为规则迁移重新生成 Gate 或要求 5.6 再审一次。
