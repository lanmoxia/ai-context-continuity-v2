# WORK-0002：实现 Schema 与纯领域校验

状态：draft

- Task：TASK-0001
- Stage：STAGE-02
- 计划项：DEV-002

## 目标

为 Continuity 的首批持久化实体建立可打包、可离线校验的 JSON Schema，并实现不依赖文件系统的领域模型、状态转换和跨实体不变量校验。

## 风险与审核

- 风险等级：high
- 必需审核：GATE-01、GATE-02、GATE-03
- 原因：本工作单新增运行时依赖，定义公共持久化格式，并建立后续状态写入所依赖的状态机与跨实体约束。

## 必读输入

- `docs/spec/DATA_MODEL.md`：首批实体、状态转换、Source Fingerprint 和不可破坏约束。
- `docs/spec/ARCHITECTURE.md`：domain/schemas 包边界、状态目录和单一事实来源。
- `docs/spec/REQUIREMENTS.md`：状态一致、审核可信、并发边界、安全和 fail-closed 要求。
- `docs/spec/CONFIGURATION.md`：Config、检查参数数组、版本和 Windows 文本边界。
- `docs/spec/CORE_WORKFLOW.md`：Task、Stage、Context Pack、Handoff 和审核的流程前置条件。
- `docs/spec/REVIEW_POLICY.md`：Review Pack、Gate、Finding、风险与 TASK-FINAL 约束。

精确章节以 `work-order.json` 的 `required_inputs` 为准。

## 允许修改的业务路径

- `pyproject.toml`
- `src/continuity/domain/**`
- `src/continuity/schemas/**`
- `tests/fixtures/schemas/**`
- `tests/unit/test_domain.py`
- `tests/unit/test_schemas.py`

## 主要交付

- 12 类 Draft 2020-12 JSON Schema，以及共享定义。
- 固定白名单、仅从包资源离线加载的 Schema registry。
- 状态枚举、结构化错误、只封装已校验数据的轻量领域记录，以及状态转换和跨实体不变量校验。
- 每类实体的合法与非法 fixture。
- Schema、状态转换和不变量的单元测试。
- `jsonschema>=4.26,<5` 作为唯一新增的直接运行时依赖，并正确打包 JSON Schema 文件。

完整文件清单以 `work-order.json` 的 `required_outputs` 为准。

## 核心约束

- JSON Schema 是结构事实来源；领域对象不能静默补默认值或维护冲突规则。
- Python 领域记录不得重复定义每类实体的字段形状、必填项或默认值。
- 所有 `$ref` 只允许指向内置 Schema，运行时不得读取网络或任意项目文件。
- 状态机与不变量校验必须是纯函数，不读写文件、不执行命令、不获取锁。
- Evidence 与 Review Pack 的 freshness 只能按当前指纹重新计算并从 fresh 降为 stale，不能原地改写不可变记录。
- 非法输入必须 fail-closed，并返回带错误代码和数据路径的稳定结构化错误。
- 不实现状态仓库、编号、Context Pack 生成、Review Pack 冻结、Writer Lease、Transfer 或 Merge Plan。
- approval 哈希计算、状态持久化和路径越界检查分别留给后续状态服务与 DEV-004；本工作单只实现纯校验前置条件。
- 不修改 CLI、其他包、集成测试、端到端测试、文档或产品核心状态。
- accepted 规格未明确的持久字段、必填性或状态边不得自行发明；遇到会改变公共格式的歧义必须停止并报告。

## 必须验证

- Python 版本、editable install 和依赖一致性。
- 编译全部 `src` 与 `tests`。
- 运行全部 unittest，不允许跳过本工作单测试。
- 所有 Schema 通过 Draft 2020-12 元 Schema 自检。
- 安装后的包可以加载全部 12 类 Schema 资源。
- 构建 wheel 并检查其中实际包含 common 与 12 类实体 Schema，共 13 个 JSON 文件。
- 现有模块入口和控制台入口的 help/version 行为无回归。

机器执行时以 `work-order.json` 中的 `required_checks` 参数数组为准。

## 完成标准

- 每类合法 fixture 通过，每类关键非法状态逐项拒绝。
- Task、Stage 和 Work Order 转换矩阵测试完整；旧 draft 也可以在更高 approved 修订存在时进入 superseded；Evidence 与 Review Pack freshness 只能降级且不覆盖原记录。
- current 指针、唯一 active、实体归属、指纹一致和 Gate 前置条件被强制执行。
- 所有错误稳定、结构化、无 traceback，且不发生隐式修正或网络访问。
- 全部 required checks 通过，没有范围外业务修改。

## 批准门槛

本文件当前只是 draft。项目所有者明确批准后，才可把 JSON 状态改为 `approved`、记录批准前 draft SHA-256，并交给 5.5 调度开发。
