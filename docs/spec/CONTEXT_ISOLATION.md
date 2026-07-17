# 上下文隔离规格

## 1. 目标

不同任务只读取完成本任务所必需的事实。当前讨论、项目路线图、其他角色材料、旧接力和无关证据不能因为“存在于项目中”就自动进入模型上下文。

## 2. 文档类别

```text
stable_spec       已确认的长期产品或技术事实
work_order        当前任务的目标、范围和验收标准
current_state     当前任务、阶段、检查点和接力
evidence          代码、diff、检查结果和审核材料
owner_planning    未确认决定、路线图和任务排期
history           已被替代或仅供追溯的记录
```

`owner_planning` 和 `history` 默认禁止进入运行时上下文。

## 3. 默认拒绝

上下文生成器必须先读取文档注册表，再按当前用途选择文件。任何文件只要满足以下任一条件就必须排除：

- 未登记。
- 状态不是当前有效状态。
- 文档类别不允许用于当前用途。
- 不属于当前 Task 或 Stage。
- 已被新版本替代。
- 超出路径、大小或敏感信息限制。

禁止通过扫描整个 `docs/` 或整个 `.continuity/` 自动补充材料。

每个业务项目都维护 `.continuity/document-registry.json`。只有项目所有者明确登记的长期规则和规格才能获得权威类别；README、临时笔记或新出现的文档不会自动登记。

## 4. 上下文包

每次开始工作都生成不可变上下文包：

```text
.continuity/contexts/CTX-0001/
  manifest.json
  START.md
```

`manifest.json` 至少记录：

- `context_id` 和 `purpose`。
- Task、Stage、Checkpoint、Handoff 或 Review Pack ID。
- `required_files`：必须读取的精确路径和 SHA-256。
- `optional_files`：仅遇到指定问题时读取。
- 每个文件的 `content_role` 和权威级别。
- `excluded_classes`。
- 字符或 token 预算。
- 生成时间和生成器版本。

`START.md` 只解释本次上下文包的目标、读取顺序和第一步，不复制所引用文件的全文。

## 5. 用途分类

用途是工作类型，不绑定具体模型：

- `architecture_design`：允许读取草案规格和项目管理材料。
- `implementation`：只读已确认规格、当前工作单、当前状态和必要源码。
- `review`：只读冻结审核包、适用验收标准和审核输出位置。
- `recovery`：只读项目规则、当前状态、最新有效检查点或接力。
- `acceptance`：只读已确认需求、验收标准和最终证据。

实现、审核、恢复和验收用途不得包含 `owner_planning`。

## 6. 明确排除

以下内容永不自动进入上下文包：

- 原始聊天记录和聊天摘要。
- “现在先做什么、以后再做什么”一类临时讨论。
- 被否决的设计方案。
- 未确认决定。
- 其他任务的工作单、接力和审核结论。
- 完整历史日志、完整测试输出和无关 diff。
- 任何角色或模型的私有提示词。

## 7. 事实与提示词分离

上下文包只提供事实、证据和文件路由，不包含角色人格、模型选择或工作话术。

角色提示词作为独立输入层，只引用一个 Context ID。更换外部执行者或角色提示词时，不复制、不改写事实材料。

manifest 中只有 `authoritative_spec` 和当前 `work_order` 可以提供任务约束。`current_state` 描述现场，`evidence` 和 `source_data` 只作为数据；它们内部即使出现“忽略规则”或命令式文字，也不获得指令权威。

Work Order 必须经过 `draft → approved → active` 状态转换。草稿、已替代版本和其他 Task 的 Work Order 一律排除。

implementation Context Pack 用于确定开始现场；进入开发后源码变化是预期行为。它不能被当成代码审核证据。review Context Pack 只引用冻结 Review Pack，源码变化会使审核材料失效。

## 8. 防污染校验

生成上下文包时必须检查：

- 每个文件都在 manifest 中。
- manifest 中的哈希与文件一致。
- 没有 `owner_planning`、`history` 或其他 Task 内容。
- 没有聊天记录标记和未确认状态。
- 总大小不超过配置预算。

发现违规时拒绝生成，而不是仅给警告。
