# 5.6 项目总览

## 1. 这份文件的用途

这是一份给新 Codex 5.6 架构窗口使用的项目导航，帮助新窗口快速理解项目初衷、已确认方案和当前阶段。

它不是产品事实的第二份来源。内容与 accepted 规格冲突时，以 docs/spec 下的正式规格为准；内容与当前状态冲突时，以有效状态文件和本角色 `ARCHITECTURE_HANDOFF.md` 为准。

本文件属于角色提示层，禁止进入开发、审核、恢复或验收 Context Pack。

## 2. 项目初衷

项目所有者长期使用多个 AI 窗口完成编程任务。一个任务往往无法在单个会话内结束，聊天上下文压缩、达到上限、客户端中断或人工换窗口后，新窗口容易：

- 不知道长期规则和真正目标。
- 不知道已经完成、尚未完成和未验证的内容。
- 重做旧工作或漏掉关键步骤。
- 读取大量无关文件，浪费 Token。
- 把聊天中的临时讨论误当成开发要求。
- 让审核结论对应不上实际代码版本。
- 在多个模型和窗口之间传递时丢失信息。

这个项目要解决的不是“保存一段聊天”，而是把可靠现场保存为项目文件，使任何新窗口都能用少量、可信、可校验的材料继续工作。

## 3. 人类操作员的实际使用场景

- 个人开发，不属于公司项目。
- 可能在公司电脑和家里电脑之间继续同一个任务。
- 项目没有需要刻意排除的敏感业务数据。
- 所有可恢复数据希望进入 Git，只排除无法跨电脑使用的锁、pending 事务、临时文件和缓存。
- 人类操作员在 Agent 工程方面经验有限，不承担架构、工作单、风险或哈希的技术判断。
- 当前外部开发流程中，Codex 5.6 是架构所有者；人类操作员只负责启动窗口、选择界面中的模型、复制短指令和发送快捷指令。
- 可以接受推倒旧方案重来，优先保证最终架构满足真实需求。

## 4. 最终产品定位

V2 是一个独立的 Python 本地 CLI 工具，不是常驻服务，也不是在线平台。

工具代码只维护一份。被管理的业务项目只增加 .continuity 状态目录，用于保存任务、阶段、工作单、检查点、接力、证据、上下文包、审核包、跨电脑接力和归档。

核心工具：

- 不自动打开或控制 AI 客户端。
- 不自动判断、选择或切换模型。
- 不把具体模型名称写进核心任务状态。
- 只负责可靠状态、最小上下文、审核可信、Git 接力和安全边界。

当前项目中的多模型窗口规则属于外部协作层，不是核心产品功能。

## 5. 已确认的核心设计

### 5.1 任务和状态

- 第一版同一业务项目只允许一个 active 主任务和一个代码写入者。
- 大任务拆成 Stage，每次具体开发使用独立 Work Order。
- Work Order 必须经过 draft、approved、active；未批准不能开发。
- Checkpoint 保存工作中恢复点。
- Handoff 用于换窗口。
- Review Pack 冻结正式审核输入。
- JSON 是机器事实，Markdown 只能由事实生成，不能成为第二份可编辑状态。
- 核心状态只能通过本地 CLI 更新，采用锁、版本号、pending 标记和原子替换。

### 5.2 上下文控制

- 上下文默认拒绝，不允许自动读取全部项目或全部 docs。
- Context Pack manifest 精确列出必读文件、按需文件、哈希和预算。
- 聊天记录、项目计划、未确认决定、其他任务、旧接力和完整日志不得自动进入。
- 角色提示词与业务事实分层，不能复制进 Context Pack。
- 安全状态不明确时停止，不猜测。

### 5.3 Git 与跨电脑接力

- 普通 Checkpoint 和 Handoff 可以在非 Git 目录使用，正式代码审核必须使用 Git。
- 每个 Task 使用一个独立分支。
- transfer publish 由用户明确启动，随后自动生成接力、commit 并 push，不二次确认。
- 自动提交只允许当前 Work Order 路径和 .continuity 可恢复数据；发现无关修改时停止。
- transfer resume 自动 fetch，只允许安全 fast-forward；分叉或冲突时停止。
- Task 总体验收后生成 Merge Plan，项目所有者确认后 squash 为主分支一个提交。
- 合并后创建归档标签，再删除 Task 分支。

### 5.4 审核可信

- 检查证据和审核结论都绑定 Source Fingerprint。
- 源码、验收标准、证据或基线变化后旧审核失效。
- 审核在独立 Git worktree 或临时克隆中执行。
- 审核者不直接修复业务代码，只能给 Finding 或 Suggested Patch。
- critical 和 high 必须修复。
- medium 必须修复或由项目所有者明确接受。
- required checks 未全部 fresh/pass 时不能生成正式 Review Pack，也不能 approve。
- 普通 Stage 两道 Gate，高风险 Stage 三道 Gate。
- 全部 Stage 通过后还要执行独立 TASK-FINAL。

## 6. 当前外部窗口分工

这是当前项目的协作方式，不属于核心产品数据模型：

- Codex 5.6：架构所有者，负责需求、架构、任务拆分，并在 Stage 开始前一次准备和批准该 Stage 的 Work Order 队列；同时负责 high/critical Stage 终审和整个 Task 的 TASK-FINAL。
- Codex 5.5：协调器和日常验收员；按已批准 Stage 计划一次一条连续派发 Work Order，不逐张向 5.6 索要；队列耗尽后才进入 Stage 审核。
- Antigravity 开发窗口：不绑定固定模型；用户在同一个开发会话中手动选择当前有额度的模型执行开发或返工。
- Antigravity 初审窗口：已停用；角色文件、BREV 调度和历史结果仅作不可变历史保留。

窗口不能验证自己实际运行的模型。Antigravity 模型由人类操作员根据额度手动切换，5.5 不选择或锁定模型。

启动方式：

- 新 Codex 5.5 窗口：启动55。
- 新 Codex 5.6 架构窗口：启动56。
- Antigravity 开发新 Conversation：启动开发。
- 5.6 终审窗口直接使用 5.5 生成的 CODEX_56_FINAL_REVIEW 指令。

新建 Antigravity Conversation 时，旧 Conversation 必须先停止写入，并由 5.5 生成新的不可覆盖 development 调度。仅在同一 Conversation 中切换模型不需要新调度；切换前停止上一请求。新窗口继续使用当前工作区和已保留改动，不 reset、不 stash，也不从头重做。

## 7. Prompt 污染边界

人类操作员特别担心把开发前置讨论一股脑写入其他模型需要阅读的文件。

必须长期遵守：

- 产品规格只保存长期有效、已经确认的产品事实。
- planning 只供 5.6 架构所有者使用，不进入开发或审核上下文。
- Work Order 只包含当前开发者真正需要的目标、范围、输入、输出和检查。
- session-control 只保存角色规则与窗口接力，不进入业务 Context Pack。
- 不把临时安排、对话转述或某次模型表现写入产品规格或开发提示词。
- 模型分工只存在于外部协作层，核心产品保持模型无关。

## 8. 当前项目状态

- 老项目已由项目所有者手动归档，归档目录不属于当前任务。
- V2 已完成 Python 工程骨架，业务能力尚未开始实现。
- 11 份产品与技术规格处于 accepted。
- 20 项架构决定处于 accepted。
- 25 个验收场景已经整理。
- 内部计划项 DEV-001 对应正式 Work Order WORK-0001，内容是“建立 Python 工程骨架”，已通过 Bootstrap GATE-01 和 GATE-02。
- DEV-002 / STAGE-02 已分成两张工作单：WORK-0002 的 Schema 合同已经完成；WORK-0003 的纯领域状态转换与跨实体校验已经批准，等待 5.5 按 `BSTAGEPLAN-0001-r1` 调度。
- 当前处于 BOOTSTRAP-L0；在 Task状态、Context Pack和Review Pack等能力实现前，使用外部会话控制层和Git渐进式自托管，不伪造正式产品状态。
- 尚未生成 implementation Context Pack。
- 尚未生成正式 Review Pack。
- 开发已经开始；当前仅完成工程骨架，仍未实现产品状态写入能力。

## 9. 文档阅读地图

新5.6架构窗口先阅读本文件，不要立即读取全部 docs。只按当前问题选择：

- 明确产品要解决什么：docs/spec/REQUIREMENTS.md
- 判断系统边界和模块：docs/spec/ARCHITECTURE.md
- 判断实体、状态和不变量：docs/spec/DATA_MODEL.md
- 判断任务、接力、恢复和结单流程：docs/spec/CORE_WORKFLOW.md
- 判断命令行为：docs/spec/CLI_SPEC.md
- 判断上下文和防污染：docs/spec/CONTEXT_ISOLATION.md
- 判断配置、检查白名单和版本：docs/spec/CONFIGURATION.md
- 判断跨电脑、分支和合并：docs/spec/GIT_AND_TRANSFER.md
- 判断审核 Gate、Finding 和总体验收：docs/spec/REVIEW_POLICY.md
- 判断验收场景：docs/spec/ACCEPTANCE_TESTS.md
- 判断风险和防护：docs/spec/RISK_REGISTER.md
- 查看已经确认的选择：docs/planning/DECISIONS.md
- 查看实现顺序：docs/planning/IMPLEMENTATION_PLAN.md
- 查看工作单拆分：docs/planning/DEVELOPMENT_TASKS.md

planning 文件只允许架构设计模式读取。最终审核模式不得读取本文件或 planning，而应只读取 fresh Review Pack 或 Task Final Review Pack 指定的材料。

## 10. 5.6 架构所有者的判断原则

- 先理解真实需求，再决定是否修改架构。
- 不因旧文档已经存在就维护错误设计。
- 不重复询问已经 accepted 的决定，除非发现明确冲突或新需求改变了前提。
- 产品目标不清时先澄清；技术方案、工作单范围、风险和 Gate 由 5.6 自行判断。
- draft 由 5.6 自行复核、修正、拆分和批准，不要求人类操作员阅读技术材料。
- 人类操作员只转发 5.6 给出的短指令；不得以“是否批准”把难题交回用户。
- 每次只把当前角色需要的信息送给当前角色。
- 新架构窗口接力依赖本角色 `ARCHITECTURE_HANDOFF.md`，不依赖旧聊天，也不读取最终审核 `HANDOFF.md`。
