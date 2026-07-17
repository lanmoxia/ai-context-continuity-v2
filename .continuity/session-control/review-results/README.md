# Bootstrap 审核结果文件

本目录保存产品正式审核能力启用前的外部审核结果。它属于会话控制层，不冒充产品生成的 Review Decision，也禁止进入业务 Context Pack。

## 目录与责任

```text
review-results/
  gate-01/       Gemini 3.5 Flash 写；5.5 在收到 sh 后读取
  gate-02/       5.5 独立中审后写
  gate-03/       5.6 高风险阶段终审后写；5.5 在收到 zs 后读取
  task-final/    5.6 整体终审后写；5.5 在收到 zs 后读取
```

开发窗口默认不读取原始审核结果。需要返工时，5.5 只把已确认的 Finding 和对应结果文件路径、SHA-256 写入新的 development 调度文件。

## 保存与修订

- 结果文件只新增、不覆盖、不删除，并进入 Git。
- 文件名使用 Gate 与顺序号，例如 `BGATE01-0001-r1.md`。
- 纠正结果时创建新修订并写明 `supersedes`；当前结果由 5.5 HANDOFF 指向。
- 如果代码、Pack、指纹或检查证据变化，原结果立即 stale，但文件仍保留。
- 结果作者完成写入和本角色 HANDOFF 后，由 5.5 在处理 `sh` 或 `zs` 时核对并纳入检查点提交；需要中途换电脑时，先回到 5.5 执行安全发布。

## 必需字段

每份结果至少包含：

1. 结果 ID、修订、Gate、执行角色、生成时间和 `supersedes`。
2. 调度文件路径与 SHA-256。
3. BPACK 或正式 Pack ID、Git 提交、Source Fingerprint、diff 哈希和检查证据标识。
4. 审核范围，以及是否确认没有修改业务代码。
5. 每个 Finding 的 ID、严重度、文件/位置、证据、影响和建议。
6. required checks 是否 fresh/pass。
7. 结论：`approve`、`request_changes` 或 `blocked`。

聊天中的“通过”不能替代结果文件。审核文档不保证模型具有某个固定准确率；它保证版本绑定、证据可追溯，并让下一道 Gate 可以独立复查。

L3 正式审核能力启用后，停止创建新的 Bootstrap 结果，改用产品 `.continuity/reviews/` 中的正式记录；旧文件保留为开发历史。
