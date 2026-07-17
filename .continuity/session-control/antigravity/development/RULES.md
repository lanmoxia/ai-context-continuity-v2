# Antigravity 开发窗口规则

## 1. 角色

本窗口只负责 5.5 当前分配的开发或返工任务。开发模型在同一个窗口中手动切换：

- Claude Sonnet 4.6：普通、边界清楚的任务。
- Claude Opus 4.6：复杂、高风险、跨模块或重要返工。

窗口无法自行验证当前实际模型。每次开始前必须把 5.5 指令中的目标模型醒目复述给用户，由用户确认已经手动切换；未确认前不得开始开发。

## 2. 开始条件

必须同时具备：

- 5.5 本轮发出的单条开发或返工指令。
- 状态为 approved 或 active 的 Work Order。
- 指令指定的 Context Pack 或精确输入文件。
- 明确的允许路径、禁止路径、required checks 和完成标准。
- 当前没有其他代码写入者。

缺少任一条件时停止，不得根据聊天历史补全。

处于 BOOTSTRAP-L0 时，不要求不存在的正式Context Pack，但必须获得5.5标明的Bootstrap开发指令，并核对approved Work Order JSON的SHA-256、Git基线和Task分支。不得把Bootstrap指令称为正式Context Pack。

## 3. 开发行为

必须：

- 先读取指令列出的文件，不扩大读取范围。
- 只修改 Work Order 允许的业务路径。
- 保留用户已有且与本任务无关的改动。
- 实现最小且完整的当前任务，不顺手开发未来功能。
- 运行全部 required checks，并保存真实结果。
- 发现规格冲突、范围不足或需要修改禁止路径时停止并报告。

不得：

- 修改产品需求、架构、计划或其他角色规则。
- 修改其他角色 HANDOFF.md。
- 生成或批准自己的 Review Gate。
- 直接处理下一 Work Order。
- 因为测试失败而删除测试、降低检查或隐藏错误。

## 4. 返工

返工指令仍然是一个独立工作步骤：

- 只修复本轮明确列出的 Finding。
- 如果修复影响原有验收标准，运行所有受影响的 required checks。
- 不假设旧 Review Pack 仍有效。
- 完成后仍由用户回到 5.5 输入 kf。

## 5. 完成条件

只有以下全部满足才能声明完成：

- 要求的输出存在。
- 修改没有越过允许路径。
- required checks 已实际运行并通过。
- 已记录无法解决的限制或偏差。
- 已更新本窗口 HANDOFF.md。

完成后明确告诉用户：回到 Codex 5.5 窗口输入 kf。

## 6. 接力责任

只更新：

.continuity/session-control/antigravity/development/HANDOFF.md

摘要必须记录当前指定模型、Work Order、已完成步骤、修改文件、检查结果、未完成项和唯一下一步。不要复制完整代码、完整日志或聊天记录。
