# Bootstrap Review Packs

本目录保存产品正式 Review Pack 能力启用前的外部审核输入。BPACK 属于会话控制层，不是产品正式 Review Pack，也禁止进入业务 Context Pack。

## 保存规则

- 文件名使用 `BPACK-NNNN.json`；文件一经写入调度并发出，只读、保留、进入 Git，不覆盖、不删除。
- 代码、检查证据或 Pack 内容变化时创建下一 BPACK；旧文件保持历史状态。
- 当前有效 BPACK 只由审核调度中的精确路径与完整文件 SHA-256 确定。

## 可复算规则

- BPACK 文件、Work Order 和规格文件：对原始完整文件字节计算小写 SHA-256。
- implementation diff：执行 JSON 中保存的完整 `argv`，直接对进程原始 stdout 字节计算 SHA-256；不得经过 PowerShell 字符串、换行转换或临时文本文件。
- 源文件条目：对 `git cat-file blob <checkpoint>:<path>` 的原始 stdout 字节计算 SHA-256。
- Source Fingerprint：按 UTF-8 路径字节升序排列条目；每行写成 `<path>\t<lowercase sha256>\n`，整体使用无 BOM UTF-8 与 LF，再计算 SHA-256。
- required input 的行范围只控制读取量；其 SHA-256 仍绑定完整文件，防止范围外变化被悄悄忽略。

## 检查证据

- required check 的 `argv` 与 `env` 以 Pack 绑定的 Work Order JSON 为准，BPACK 只保存实际执行顺序与结果。
- 失败、未运行或未经 Work Order 明确允许的 skipped 都不能冻结 BPACK。
- 因安装依赖关系需要调整执行顺序时，只能调整顺序，不能修改 check 的 `argv`、`env` 或通过标准，并必须在 BPACK 中写明原因。
