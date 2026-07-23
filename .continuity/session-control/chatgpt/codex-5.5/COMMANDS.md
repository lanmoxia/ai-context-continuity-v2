# Codex 5.5 指令协议

## 1. 快捷指令

- `kf`：开发或返工完成。
- `zs`：5.6 Stage 最终 Gate 或 TASK-FINAL 完成。
- `sh`：停用。

快捷指令只触发核对；没有当前调度和结果文件时不能推进。

## 2. 调度文件

- 开发/返工：`.continuity/session-control/dispatches/development/BDEV-NNNN-rN.md`
- 5.6 最终裁决：`.continuity/session-control/dispatches/final-review/BFINAL-NNNN-rN.md`

`initial-review/` 和 `pre-final-review/` 只保留旧流程历史，不再新增。

每个调度必须包含 ID、修订、目标角色、Task/Stage/Work Order、业务基线、权威文件路径和哈希、唯一目标、精确读取顺序、允许保留的脏文件、停止条件、结果目标与回传快捷指令。development 调度另外记录模型策略 `user_selected_available_model`；final-review 调度不使用这个字段。

开发调度引用 approved Work Order；最终审核调度只引用 fresh BPACK。调度文件不可覆盖，纠错创建新修订。

## 3. 聊天输出格式

标题只告诉用户切换哪个窗口和任务。Antigravity 具体模型由用户现场手动选择，不写进标题或复制块。`kf`、`zs` 提示放在代码块外。

### 开发

**请切换到 Antigravity 开发窗口｜任务：WORK-ORDER-ID**

```text
【角色启动】启动开发
【调度文件】DISPATCH-PATH
【调度文件 SHA-256】DISPATCH-SHA256
核对哈希后只按该调度文件执行；不匹配立即停止。
```

代码块外另写：完成后回到 Codex 5.5 窗口输入 `kf`。

### Codex 5.6 最终裁决

**请切换到 Codex 5.6 终审窗口｜范围：STAGE-FINAL-GATE 或 TASK-FINAL｜审核：PACK-ID**

```text
【角色绑定】CODEX_56_FINAL_REVIEW
【调度文件】DISPATCH-PATH
【调度文件 SHA-256】DISPATCH-SHA256
核对哈希后只按该调度文件审核；不匹配立即停止。
```

代码块外另写：完成后回到 Codex 5.5 窗口输入 `zs`。

标题前不加长篇解释，代码块内不重复模型名或快捷指令。

## 4. 审核结果与返工

- `zs` 只接受当前 BFINAL 指定的 Stage 最终 Gate 或 TASK-FINAL 结果。
- 返工调度只传递 5.5 已确认的 Finding 摘要和来源哈希，不把整份审核聊天交给开发窗口。
- low/normal 任务由 5.5 一次验收后作出最终结论并收口；业务代码变化使当前 BPACK 和相关 Gate 结果 stale，high/critical 任务返工后只再做一次 5.5 验收和一次 5.6 终审。
