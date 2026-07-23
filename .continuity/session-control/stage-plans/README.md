# Bootstrap Stage plans

本目录保存 BOOTSTRAP 阶段由 Codex 5.6 架构模式生成的不可覆盖 Stage 计划。

每份计划必须：

- 绑定一个 Task 和 Stage。
- 列出该 Stage 全部 approved Work Order 的顺序、精确路径、SHA-256、依赖条件和队列末项。
- 记录 Stage 累计目标、验收标准、风险和 required Gate。
- 使用新修订纠错，不覆盖、不改名、不删除旧计划。

5.5 只能读取架构接力或 Stage 启动指令精确指定且 SHA-256 匹配的一份计划。计划内仍有 ready Work Order 时，5.5 必须连续调度，不能返回 5.6 临时索要下一张单。

Stage 计划属于外部会话控制层，不是产品正式 Stage 状态，也禁止进入业务 Context Pack。产品 Stage 与 Work Order 状态能力启用后停止创建新的 Bootstrap Stage 计划。
