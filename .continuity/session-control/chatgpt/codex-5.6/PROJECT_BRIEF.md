# 5.6 项目总览

## 1. 这份文件的用途

这是一份给新 Codex 5.6 架构窗口使用的项目导航，帮助新窗口快速理解项目初衷、已确认方案和当前阶段。

它不是产品事实的第二份来源。内容与 accepted 规格冲突时，以 docs/spec 下的正式规格为准；内容与当前状态冲突时，以有效状态文件和本角色 HANDOFF.md 为准。

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

## 3. 项目所有者的实际使用场景

- 个人开发，不属于公司项目。
- 可能在公司电脑和家里电脑之间继续同一个任务。
- 项目没有需要刻意排除的敏感业务数据。
- 所有可恢复数据希望进入 Git，只排除无法跨电脑使用的锁、pending 事务、临时文件和缓存。
- 项目所有者在 Agent 工程方面经验有限，需要架构窗口使用简单、具体的中文解释。
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

- Codex 5.6：需求、架构、任务拆分、详细开发文档、高风险 Stage 的 GATE-03、整个 Task 的 TASK-FINAL。
- Codex 5.5：协调器、一次一条开发指令、开发结果预检、模型目标提示、普通 Stage 的 GATE-02、返工和下一步调度。
- Antigravity 开发窗口：按 5.5 提示，由用户手动选择 Sonnet 4.6 或 Opus 4.6 执行开发。
- Antigravity 初审窗口：由用户手动选择 Gemini 3.5 Flash，执行 GATE-01。

窗口不能验证自己实际运行的模型，模型选择始终由用户负责。

启动方式：

- 新 Codex 5.5 窗口：启动55。
- 新 Codex 5.6 架构窗口：启动56。
- Antigravity 开发新 Conversation：启动开发。
- Antigravity 初审新 Conversation：启动审核。
- 5.6 终审窗口直接使用 5.5 生成的 CODEX_56_FINAL_REVIEW 指令。

## 7. Prompt 污染边界

项目所有者特别担心把开发前置讨论一股脑写入其他模型需要阅读的文件。

必须长期遵守：

- 产品规格只保存长期有效、已经确认的产品事实。
- planning 只供项目所有者和架构设计，不进入开发或审核上下文。
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
- 下一计划项 DEV-002 对应 WORK-0002，内容是“实现 Schema 与纯领域校验”，当前为 draft，尚未获得项目所有者批准。
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

## 10. 5.6 架构窗口的判断原则

- 先理解真实需求，再决定是否修改架构。
- 不因旧文档已经存在就维护错误设计。
- 不重复询问已经 accepted 的决定，除非发现明确冲突或新需求改变了前提。
- 讨论方案时先讨论，不提前实现。
- 用户明确批准后再落地，并做一致性检查。
- 每次只把当前角色需要的信息送给当前角色。
- 新窗口接力依赖本角色 HANDOFF.md，不依赖旧聊天。
