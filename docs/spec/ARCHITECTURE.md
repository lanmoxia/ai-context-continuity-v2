# 建议架构

## 1. 系统边界

V2 分成两部分：

```text
Continuity 工具仓库                 被管理的业务项目
命令、校验、模板、测试       →      .continuity/ 状态目录
```

工具代码只维护一份。业务项目中只保存与该项目有关的配置、任务、接力、上下文包和审核数据。

外部客户端通过本地命令或生成文件使用工具，但不属于核心工具进程。

## 2. 核心组件

```text
CLI 命令入口
  ├─ 任务与阶段服务
  ├─ 检查点与接力服务
  ├─ 上下文包与恢复材料生成器
  ├─ 源码指纹与检查证据服务
  ├─ 审核包生成与失效检查
  ├─ Git 分支、跨电脑 transfer 与合并计划
  ├─ 健康检查与恢复
  └─ 安全边界
         ↓
统一状态仓库（唯一写入入口）
```

- CLI：接收明确命令，不决定外部客户端或执行者。
- 状态仓库：统一分配编号、校验状态转换、原子写入。
- 生成器：把 JSON 事实生成为 Markdown 阅读页。
- 上下文选择器：按文档注册表和用途生成最小 Context Pack。
- 安全边界：限制路径、写入租约、敏感信息、命令和审核包范围。

## 3. 工具仓库结构

```text
ai-context-continuity-v2/
  pyproject.toml
  src/continuity/
    cli.py
    domain/                 数据模型和状态转换
    storage/                原子写入、锁、编号和读取
    services/               接力、上下文、证据、审核包、健康检查
    git/                    指纹、分支、transfer、审核副本和合并
    renderers/              JSON → Markdown
    security/               路径和敏感信息检查
    schemas/                JSON Schema
    templates/              阅读页模板
  tests/
    unit/
    integration/
    e2e/
  docs/
    spec/                   产品和技术规格
    planning/               不进入运行时上下文的项目管理材料
```

业务逻辑不能直接散落在 CLI 中，所有入口复用同一套领域和安全校验。

## 4. 业务项目状态目录

```text
.continuity/
  project.json
  config.json
  document-registry.json
  current.json

  tasks/
    TASK-0001/
      task.json
      task.md
      stages/
        STAGE-01/
          stage.json
          stage.md

  work-orders/
    WORK-0001/
      work-order.json
      work-order.md

  checkpoints/
    CHECKPOINT-0001.json

  handoffs/
    HANDOFF-0001/
      handoff.json
      handoff.md

  evidence/
    EVIDENCE-0001/
      evidence.json
      output.txt

  reviews/
    PACK-0001/
      manifest.json
      review-request.md
      code.patch
      changed-files.txt
      test-summary.md
      findings/
      decisions/
      suggested-patches/

  contexts/
    CTX-0001/
      manifest.json
      START.md

  transfers/
    TRANSFER-0001.json

  merge-plans/
    MERGE-0001.json

  views/
    START_HERE.md
    CURRENT_TASK.md
    LATEST_HANDOFF.md

  recovery/
    current.prev.json

  archive/

  runtime/
    write.lock
    writer-lease.json
    pending/
    temp/
    cache/
```

除 `runtime/` 外，`.continuity/` 中所有可恢复数据都进入 Git，包括 Checkpoint、Context Pack、完整审核材料和归档。`views/` 虽然可以重建，也随其他恢复数据提交。

`document-registry.json` 只登记项目所有者明确允许的规则和规格文件，不扫描项目后自动扩充。

## 5. 单一事实来源

- `current.json` 只保存当前指针和状态版本，不复制任务全文。
- `task.json`、`stage.json` 保存任务事实。
- `work-order.json` 保存一次具体开发尝试的精确输入和输出约束。
- 检查点、接力和审核包创建后不覆盖，只新增新版本。
- Context Pack 和检查证据创建后不覆盖。
- 同名 Markdown 是自动生成的阅读版本，禁止作为独立状态手工维护。
- `START_HERE.md` 等视图可以随时重新生成。

这不是“所有事实放进一个大文件”，而是“每类事实只有一个权威来源”。

## 6. 写入和恢复

每次状态变化采用同一顺序：

1. 获取操作系统级独占锁。
2. 读取并校验当前版本号。
3. 创建恢复用 pending 事务标记。
4. 写入新的不可变记录。
5. 在临时目录生成新状态和阅读页。
6. 校验完成后原子替换正式文件。
7. 标记事务完成并释放锁。

`write.lock` 只记录占用者信息，真正防并发依靠文件锁，而不是依靠一个可伪造的 `locked: true`。

写入中断时保留 `current.prev.json` 和 pending 标记。健康检查负责判断应继续使用旧状态，还是把已完成写入的新记录重新挂接到当前状态。不建立一份与状态重复的通用事件日志。

短时文件锁只保护一次 CLI 写入。跨窗口开发使用带超时的 `writer-lease.json`；同一项目最多一个有效写入租约。该租约是流程保护，不能阻止绕过工具的外部编辑。

## 7. 审核可信度

审核包必须记录：

- 任务和阶段版本。
- Git 基线提交。
- 创建审核包时的工作区状态。
- 统一源码指纹：HEAD、暂存 diff、未暂存 diff 和任务范围内未跟踪文件内容哈希。
- 变更文件、diff 和检查证据的哈希。
- 审核包自身编号和生成时间。

审核结论绑定 `PACK-ID + manifest hash + gate ID`。任一受监控内容改变，旧审核立即标记为 `stale`，不能继续用于结单。

普通 Stage 使用两道 Review Gate，高风险 Stage 增加第三道。所有必需 Gate 必须针对同一个 fresh Pack 通过；外部流程再把具体执行者映射到 Gate，核心引擎不保存特定模型名称。

所有 Stage 通过后生成 Task Final Review Pack。它聚合完整任务验收标准、所有 Stage Pack、最终源码指纹、Task 级检查和 Finding。Task Final Gate 通过后才能生成主分支 Merge Plan。

普通接力可以在没有 Git 的目录使用；正式代码审核第一版要求 Git，否则无法可靠证明审核对应哪一版代码。

检查证据同样绑定源码指纹。源码变化后，旧检查结果可以保留作历史，但不能作为当前审核已验证的依据。

## 8. 上下文控制

每项工作先生成 Context Pack。manifest 按用途精确列出必读和按需文件及其哈希。未登记文件、项目管理材料、未确认决定、历史记录和其他 Task 内容默认排除。

Context Pack 只提供事实、证据路由和下一步，不包含角色提示词。源码、完整 diff 和完整检查日志按需读取，不复制进启动页。

审核用途优先使用物理隔离的 Review Pack，避免审核者扫描整个业务项目。

审核需要运行代码时，从精确提交创建隔离 worktree 或临时克隆。审核修改只能导出 Suggested Patch，不能写入正式 Task 分支。

## 9. 配置和版本

`config.json` 管理上下文预算、Git 策略、写入租约、文件限制、保留策略和已批准检查命令。

所有持久 JSON 带 `schema_version`。不兼容版本默认只读；迁移必须先备份、生成 dry-run 报告，再明确应用。

完成任务的不可变记录可以归档。第一版只移动不自动永久删除。

## 10. Git 与跨电脑边界

- 每个 Task 使用一个独立分支。
- `transfer publish` 自动保存接力，只提交 Work Order 范围和可恢复状态，再 push Task 分支。
- `transfer resume` 自动 fetch，但只允许 fast-forward。
- 自动流程禁止 force push、rebase、冲突合并、stash、reset 和清理无关修改。
- Task Final Review 通过后先生成 Merge Plan；项目所有者确认后才 squash 合并主分支。
- 合并后创建归档标签，再删除 Task 分支。

详细行为见 `GIT_AND_TRANSFER.md`。

## 11. 核心工具边界

- 不做常驻服务和数据库。
- 不做多项目管理后台。
- 不自动打开、切换或控制 AI 客户端。
- 不同时运行两个写代码的主任务。
- 角色提示词和客户端适配不属于核心状态与恢复引擎。
