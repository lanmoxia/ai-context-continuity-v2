# WORK-0003：实现纯领域状态转换与跨实体约束

状态：draft

- Task：TASK-0001
- Stage：STAGE-02
- 计划项：DEV-002

## 目标

为 WORK-0002 已定义的首批持久化结构补上纯领域规则：明确哪些状态可以转换，以及多条记录组合后必须满足哪些不变量。

## 范围

只允许修改：

- `src/continuity/domain/**`
- `tests/unit/test_domain.py`

不实现存储、锁、编号、CLI、Git、路径安全、Context Pack、Review Pack 冻结或文件写入，也不修改现有 Schema。

## 主要交付

- 不可变、稳定排序的 `DomainViolation`。
- 明确、fail-closed 的状态转换表和纯函数 API。
- 当前指针、父子归属、单 active、Handoff、Evidence、Review Pack、Gate 与 TASK-FINAL 前置条件校验。
- 覆盖全部合法/非法状态边和跨实体约束的单元测试。

## 核心边界

- JSON Schema 继续是单记录结构事实来源；domain 不复制字段定义、默认值、ID 或日期格式规则。
- domain 只做纯计算，不读取或修改外部状态。
- 未在 accepted 规格声明的状态边一律拒绝。
- 单个 Work Order 完成不等于 STAGE-02 完成；本单是 STAGE-02 队列末项，完成后才进入累计 Stage 审核。

## 必须验证

- Python、安装、依赖、编译和全部 unittest。
- 领域 API 导入与基本 fail-closed 行为。
- Schema 自检与 CLI help/version 无回归。
- 新增测试不跳过，错误顺序稳定，输入不被修改。

详细输入、输出、检查和验收标准以同目录 `work-order.json` 为唯一权威来源。

## 批准状态

当前为 draft，等待 Codex 5.6 架构所有者完成就绪复核并记录批准前 SHA-256。
