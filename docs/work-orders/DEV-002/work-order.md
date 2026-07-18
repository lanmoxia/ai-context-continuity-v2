# WORK-0002：实现首批持久化 Schema 合同

状态：approved

- Task：TASK-0001
- Stage：STAGE-02
- 计划项：DEV-002

## 目标

为 Continuity 的首批持久化实体建立可打包、可离线、默认拒绝未知输入的 JSON Schema 合同和固定白名单加载器。

## 风险与审核

- 风险等级：high
- 必需审核：GATE-01、GATE-02、GATE-03
- 原因：本工作单新增运行时依赖并首次定义公共持久化格式；领域状态机已拆到后续 WORK-0003。

## 必读输入

- `docs/spec/DATA_MODEL.md`：首批实体字段、状态枚举、Source Fingerprint 和不可破坏约束。
- `docs/spec/ARCHITECTURE.md`：domain/schemas 包边界、状态目录和单一事实来源。
- `docs/spec/REQUIREMENTS.md`：状态一致、审核可信、并发边界、安全和 fail-closed 要求。
- `docs/spec/CONFIGURATION.md`：Config、检查参数数组、版本和 Windows 文本边界。
- `docs/spec/CORE_WORKFLOW.md`：Task、Stage、Context Pack、Handoff 和审核的流程前置条件。
- `docs/spec/REVIEW_POLICY.md`：Review Pack、Gate、Finding、风险与 TASK-FINAL 约束。

精确章节以 `work-order.json` 的 `required_inputs` 为准。

## 允许修改的业务路径

- `pyproject.toml`
- `src/continuity/schemas/**`
- `tests/fixtures/schemas/**`
- `tests/unit/test_schemas.py`

## 主要交付

- 12 类 Draft 2020-12 JSON Schema，以及共享定义。
- 固定白名单、仅从包资源离线加载的 Schema registry。
- 稳定排序的结构化 Schema 校验错误。
- 每类实体的合法与非法 fixture。
- Schema 自检、合法/非法 fixture、离线引用和包资源的单元测试。
- `jsonschema>=4.26,<5` 作为唯一新增的直接运行时依赖，并正确打包 JSON Schema 文件。

完整文件清单以 `work-order.json` 的 `required_outputs` 为准。

## 核心约束

- JSON Schema 是结构事实来源；领域对象不能静默补默认值或维护冲突规则。
- Python 领域记录不得重复定义每类实体的字段形状、必填项或默认值。
- 所有 `$ref` 只允许指向内置 Schema，运行时不得读取网络或任意项目文件。
- 非法输入必须 fail-closed，并返回带错误代码和数据路径的稳定结构化错误。
- 不实现领域状态转换、跨实体不变量、状态仓库、编号、Context Pack 生成、Review Pack 冻结、Writer Lease、Transfer 或 Merge Plan。
- approval 哈希计算、状态前置条件、状态持久化和路径越界检查留给后续工作单。
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
- 12 类实体的合法 fixture 通过，关键非法结构逐项拒绝。
- 所有 Schema 错误稳定、结构化、无 traceback，且不发生隐式修正或网络访问。
- 全部 required checks 通过，没有范围外业务修改。

## 批准门槛

Codex 5.6 架构所有者已完成就绪检查并批准。批准前 draft SHA-256 为 `b2ba3d17531d76f3c776e7c061970b0a815a779b59b6ad0acc83a63568eca1db`，draft 已保存在提交 `6788a16`。人类操作员无需审阅技术内容，下一步由 5.5 核对 approved JSON 后生成开发调度。
