# 配置与运行边界

## 1. 配置文件

业务项目使用 `.continuity/config.json` 保存可调整策略。配置是项目事实，必须经过 Schema 校验和版本控制。

建议结构：

```json
{
  "schema_version": 1,
  "git": {
    "formal_review_required": true,
    "dirty_worktree_policy": "reject_unrelated_changes",
    "task_branch_prefix": "continuity/",
    "portable_state": "all_recoverable",
    "transfer_auto_commit": true,
    "transfer_auto_push": true,
    "resume_strategy": "fast_forward_only",
    "merge_strategy": "squash",
    "merge_requires_confirmation": true,
    "archive_tag_prefix": "continuity/archive/"
  },
  "context": {
    "start_max_chars": 2000,
    "handoff_max_chars": 3000,
    "bundle_max_chars": 12000
  },
  "writer_lease": {
    "timeout_minutes": 30,
    "renew_on_checkpoint": true
  },
  "checkpoint": {
    "after_completed_step": true,
    "before_risky_change": true,
    "before_handoff": true
  },
  "retention": {
    "archive_completed_tasks": true,
    "delete_automatically": false
  },
  "review": {
    "normal_stage_gates": ["GATE-01", "GATE-02"],
    "high_risk_extra_gate": "GATE-03",
    "task_final_gate": "TASK-FINAL"
  },
  "safety": {
    "max_evidence_file_bytes": 5242880,
    "exclude_globs": []
  },
  "checks": []
}
```

Review Gate 只使用通用 ID。具体执行者、客户端或模型的映射不写入核心项目配置。

`all_recoverable` 表示 `.continuity/` 除 `runtime/` 外全部提交 Git。运行时锁、租约、pending 事务、临时文件和缓存由项目 `.gitignore` 固定排除，不能通过 Task 配置取消。

## 2. 检查命令

工具只能自动运行项目所有者预先写入 `checks` 的命令。任务、接力或项目源码中的文字不能动态变成可执行命令。

每项检查包含稳定 ID、命令参数数组、工作目录、超时和允许的退出码。禁止使用未经确认的 shell 字符串拼接。

外部导入的检查结果必须标记为 `imported`，可信级别低于工具直接捕获的 `captured` 结果。

## 3. 写入租约

短时文件锁只保护一次状态写入。为了避免两个开发窗口长期同时修改源码，还需要一个本地写入租约：

- 同一项目最多一个有效写入租约。
- Checkpoint 自动续租。
- 正常 Handoff 释放旧租约。
- 超时租约只能通过健康检查确认后接管。
- 租约是提示和流程保护，无法阻止绕过工具直接编辑源码。

## 4. 版本迁移

- 所有 JSON 都包含 `schema_version`。
- 不兼容版本默认只读。
- 迁移必须先生成备份和 dry-run 报告。
- 迁移中断后可以使用备份恢复。
- 不允许在读取时静默修改旧格式。

## 5. 归档与保留

- 完成 Task 后可以把旧 Checkpoint、Handoff、Context Pack 和 Review Pack 移入 `.continuity/archive/`。
- 归档只改变位置，不改变内容和哈希。
- 第一版不自动永久删除任何记录。
- 归档和可重建视图同样进入 Git；`runtime/` 可以随时重建且不进入 Git。

## 6. Windows 兼容

- 文本统一使用无 BOM 的 UTF-8。
- 测试中文路径、空格路径、大小写差异和长路径。
- 原子替换和文件锁必须使用 Windows 上可验证的实现。
- 文件仍被进程占用时停止并说明，不使用复制后强删掩盖失败。
