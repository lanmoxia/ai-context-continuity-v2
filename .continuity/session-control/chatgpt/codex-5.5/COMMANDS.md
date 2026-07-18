# Codex 5.5 指令协议

## 1. 快捷指令

- `kf`：开发或返工完成声明。
- `sh`：Gemini GATE-01 初审完成声明。
- `zs`：Codex 5.6 GATE-03 或 TASK-FINAL 完成声明。

快捷指令可以附带简短说明，但 5.5 必须以当前调度文件、结果文件和实际仓库为准。

## 2. 先生成事实材料，再生成调度文件

5.5 不在聊天中输出长篇执行要求。每个可执行步骤必须先新增一个调度文件：

- 开发或返工：`.continuity/session-control/dispatches/development/BDEV-NNNN-rN.md`
- Gemini 初审：`.continuity/session-control/dispatches/initial-review/BREV-NNNN-rN.md`
- 5.6 阶段终审或整体终审：`.continuity/session-control/dispatches/final-review/BFINAL-NNNN-rN.md`

开发调度直接引用 Work Order。审核调度必须先新增 `.continuity/session-control/bootstrap-packs/BPACK-NNNN.json`，计算其 SHA-256，再引用它。

生成顺序：

1. 核对当前事实、权威 Work Order、Git 基线和目标角色。
2. 审核步骤先冻结独立 BPACK：保存可复算 diff、逐文件指纹和无跳过的 fresh checks，再计算 BPACK SHA-256。
3. 选择下一个调度 ID；新步骤使用 `r1`。
4. 新增调度文件，不覆盖任何已有文件。
5. 计算调度文件的小写 SHA-256。
6. 把当前 BPACK 与调度 ID、路径、SHA-256、目标模型、基线和等待事件写入 5.5 HANDOFF。
7. 只暂存本次新增的 BPACK、调度文件和 5.5 HANDOFF，创建纯会话控制提交；确认没有夹带业务文件后安全推送当前 Task 分支。
8. 最后才在聊天中输出短启动块。

未发送的错误指令可以纠正：用户明确说明旧指令尚未粘贴给目标窗口时，创建同一 ID 的下一修订并写明 `supersedes`。旧文件保留，5.5 HANDOFF 改指向新修订；这不算并行发出第二个任务。

## 3. 调度文件内容

调度文件必须包含：

1. 类型、ID、修订、生成时间、生成角色、目标角色、目标模型和 `supersedes`。
2. Task、Stage、Work Order、当前分支和精确业务执行基线。
3. 开发时包含权威 Work Order JSON 路径与 SHA-256；审核时只包含 BPACK 路径、BPACK SHA-256 和结果目标。
4. 唯一目标。
5. 开发调度列出精确读取顺序；审核调度只要求读取当前 BPACK，后续输入由 BPACK 清单决定。
6. 调度前已经存在且允许保留的精确脏文件。
7. 本轮允许新增的会话控制文件，例如本角色 HANDOFF 或审核结果文件。
8. 停止条件、完成回传和用户应输入的快捷指令。

开发调度不复制 Work Order 中的 allowed paths、forbidden paths、required outputs、required checks 或 acceptance criteria；目标窗口读取权威 JSON。禁止读取 `work-order.md` 作为实现输入。

审核调度不复制 BPACK 的源码清单、检查表、指纹、审核重点或结果字段，也不得要求审核者读取开发窗口 HANDOFF。BPACK 必须保存 diff 哈希完整 `argv`、逐文件哈希清单、Source Fingerprint 前像规则和 checks 的测试/跳过数量。

调度文件只能路由到权威事实，不能使用“阅读整个项目”“自行查看相关文件”或“按之前讨论继续”等模糊文字。

## 4. 聊天短启动块

聊天回复固定为两部分：醒目标题，以及一个可一键复制的 `text` 代码块。代码块之外不重复任务详情。

### 开发给 Sonnet

**请切换到 Antigravity 开发窗口｜模型：Claude Sonnet 4.6｜任务：WORK-ORDER-ID**

```text
【角色启动】启动开发
【目标模型】Claude Sonnet 4.6（由用户手动确认）
【调度文件】DISPATCH-PATH
【调度文件 SHA-256】DISPATCH-SHA256
请先完成角色启动，再核对哈希并只按该调度文件执行；不匹配立即停止。
完成后回到 Codex 5.5 窗口输入 kf。
```

### 开发给 Opus

标题改为 Claude Opus 4.6，代码块中的目标模型同步改为 Claude Opus 4.6，其余格式不变。

### Gemini GATE-01

**请切换到 Antigravity 初审窗口｜模型：Gemini 3.5 Flash｜审核：PACK-ID / GATE-01**

```text
【角色启动】启动审核
【目标模型】Gemini 3.5 Flash（由用户手动确认）
【调度文件】DISPATCH-PATH
【调度文件 SHA-256】DISPATCH-SHA256
请先完成角色启动，再核对哈希并只按该调度文件审核；不匹配立即停止。
完成并写入结果文件后，回到 Codex 5.5 窗口输入 sh。
```

### Codex 5.6 GATE-03 或 TASK-FINAL

**请切换到 Codex 5.6 终审窗口｜范围：GATE-03 或 TASK-FINAL｜审核：PACK-ID**

```text
【角色绑定】CODEX_56_FINAL_REVIEW
【调度文件】DISPATCH-PATH
【调度文件 SHA-256】DISPATCH-SHA256
请先完成最终审核角色启动，再核对哈希并只按该调度文件审核；不匹配立即停止。
完成并写入结果文件后，回到 Codex 5.5 窗口输入 zs。
```

第一行标题之前不得添加解释。用户只复制代码块；标题负责提醒切换窗口和模型。

## 5. Bootstrap 特殊要求

BOOTSTRAP-L0 调度文件还必须：

- 明确标注 `BOOTSTRAP-L0`，声明不是正式 Context Pack 或 Review Pack。
- 开发调度绑定 approved Work Order JSON 的 SHA-256、Git 基线和 Task 分支，不使用 CTX 编号。
- 审核调度使用 BPACK 前缀，只绑定独立 BPACK 文件路径和 SHA-256；Git 提交、Source Fingerprint、diff 哈希和 fresh checks 只保存在 BPACK。
- 指定唯一审核结果新文件：GATE-01 写入 `review-results/gate-01/`，GATE-03 写入 `gate-03/`，TASK-FINAL 写入 `task-final/`。

required check 出现失败、未运行或未经 Work Order 明确允许的 `skipped` 时不得创建审核调度。若安装后才能完整运行某组测试，必须安装后重跑并记录 `skipped: 0`。

5.5 的 GATE-02 不需要向其他窗口发送短启动块，但必须把独立结论新增到 `review-results/gate-02/`，并在 HANDOFF 中记录路径和 SHA-256。

## 6. 审核结果与返工

- `sh` 只有在 GATE-01 结果文件存在且绑定当前调度和当前 BPACK 路径、SHA-256 时才有效。
- `zs` 只有在 GATE-03 或 TASK-FINAL 结果文件存在且绑定当前调度和当前 Pack 路径、SHA-256 时才有效。
- 5.5 不把 Gemini 原始报告整份交给开发窗口。需要返工时，创建新的 development 调度，列出 5.5 已确认的 Finding ID、最小证据、来源结果路径与 SHA-256。
- 代码变化使当前 BPACK 和所有相关结果 stale；保留文件，重新生成下一份 BPACK，并从新的 GATE-01 调度开始。
