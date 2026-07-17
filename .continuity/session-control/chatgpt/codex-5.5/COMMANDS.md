# Codex 5.5 指令协议

## 1. 快捷指令

- kf：开发或返工完成声明。
- sh：Gemini GATE-01 初审完成声明。
- zs：Codex 5.6 GATE-03 或 TASK-FINAL 完成声明。

快捷指令可以附带简短说明，但 5.5 必须以项目文件为准。

## 2. 第一行格式

开发给 Sonnet：

**请切换到 Antigravity 开发窗口｜模型：Claude Sonnet 4.6｜任务：WORK-ORDER-ID**

【角色启动】启动开发

【目标模型】Claude Sonnet 4.6（由用户手动确认）

开发给 Opus：

**请切换到 Antigravity 开发窗口｜模型：Claude Opus 4.6｜任务：WORK-ORDER-ID**

【角色启动】启动开发

【目标模型】Claude Opus 4.6（由用户手动确认）

Gemini 初审：

**请切换到 Antigravity 初审窗口｜模型：Gemini 3.5 Flash｜审核：REVIEW-PACK-ID / GATE-01**

【角色启动】启动审核

【目标模型】Gemini 3.5 Flash（由用户手动确认）

5.6 高风险阶段终审：

**请切换到 Codex 5.6 终审窗口｜范围：高风险阶段 GATE-03｜审核：REVIEW-PACK-ID**

【角色绑定】CODEX_56_FINAL_REVIEW

5.6 整体终审：

**请切换到 Codex 5.6 终审窗口｜范围：TASK-FINAL｜审核：TASK-FINAL-PACK-ID**

【角色绑定】CODEX_56_FINAL_REVIEW

第一行之前不得添加解释，避免用户复制错窗口或忘记切换模型。

## 3. 可复制指令必须包含

每条指令只描述当前一步，并明确：

1. 当前角色和唯一目标。
2. 明确的角色启动标记。
3. 需要人工选择时，醒目标注目标模型。
4. Task、Stage、Work Order、Context Pack 或 Review Pack ID。
5. 第一步需要读取的角色 START.md。
6. 按顺序读取的精确任务文件路径。
7. 允许修改的路径。
8. 禁止修改的路径。
9. required checks。
10. 完成结果必须写入的精确文件。
11. 遇到越界、基线变化或缺少文件时立即停止。
12. 完成后更新当前窗口自己的 HANDOFF.md。
13. 用户完成后回到 5.5 应输入 kf、sh 或 zs。

禁止使用“阅读整个项目”“自行查看相关文件”或“按之前讨论继续”等模糊表述。

当前处于 BOOTSTRAP-L0 时，开发指令还必须包含：

- 【执行模式】BOOTSTRAP-L0。
- 当前approved Work Order JSON的SHA-256。
- Git基线提交和当前Task分支。
- 明确说明这不是正式implementation Context Pack。
- 不使用CTX编号。

正式Review Pack能力尚未启用时，审核指令必须使用BPACK前缀，并绑定精确Git提交、diff哈希和检查结果。

## 4. 回复尾部

可复制指令之后，只保留一句用户操作说明：

- 开发或返工：完成后回到本窗口输入 kf。
- Gemini 初审：完成后回到本窗口输入 sh。
- Codex 5.6 终审：完成后回到本窗口输入 zs。

不得提前附带下一阶段指令。
