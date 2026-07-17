# WORK-0001：建立 Python 工程骨架

状态：draft

## 目标

建立结构规范、可以安装、可以运行、可以测试的 Continuity Python 包骨架。

## 风险与审核

- 风险等级：normal
- 必需审核：GATE-01、GATE-02

## 必读输入

- docs/spec/ARCHITECTURE.md 的“工具仓库结构”
- docs/spec/CLI_SPEC.md 的“项目”

## 允许修改的业务路径

- pyproject.toml
- src/continuity/**
- tests/**

## 禁止修改的业务与核心路径

- docs/**
- .continuity/**
- .agents/**
- AGENTS.md
- .git/**

## 必须交付

- Python 3.11+、src布局、可安装的 pyproject.toml。
- continuity 包、模块入口和控制台入口。
- 只支持 --help 和 --version 的标准库 CLI 空入口。
- domain、storage、services、git、renderers、security、schemas、templates 包边界。
- tests/unit、tests/integration、tests/e2e 三层目录。
- tests/unit/test_cli.py。

## 明确不做

- 不实现 Task、Stage、Checkpoint、Handoff、Review、Transfer 或状态写入。
- 不实现配置、日志、Schema内容或模板内容。
- 不引入运行时第三方依赖。
- 不修改允许范围之外的业务文件。

## 必须验证

所有命令都在已激活的 Python 3.11+ 项目虚拟环境中运行：

- Python版本检查。
- 编译 src 和 tests。
- 运行全部 unittest。
- editable install 当前项目。
- 从已安装包导入 continuity 并读取版本。
- python -m continuity --help。
- python -m continuity --version。
- continuity --help。
- continuity --version。
- 未知参数返回非零退出码和简短错误，不打印 traceback。

机器执行时以 work-order.json 中的 required_checks 参数数组为准。

## 完成标准

- 全部required checks通过。
- 两种CLI入口都正常。
- 包边界和三层测试目录完整。
- 没有超范围业务修改。
- 没有提前实现业务逻辑。
