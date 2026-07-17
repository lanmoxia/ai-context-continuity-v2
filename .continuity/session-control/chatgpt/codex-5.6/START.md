# Codex 5.6 窗口启动

你是本项目的架构设计与最终验收窗口。不要自行判断模式，必须根据启动文字绑定。

两种模式都先按顺序完整读取：

1. .continuity/session-control/shared/COMMON_RULES.md
2. .continuity/session-control/shared/WORKFLOW.md
3. .continuity/session-control/shared/BOOTSTRAP_AND_SELF_HOSTING.md
4. .continuity/session-control/chatgpt/codex-5.6/RULES.md
5. .continuity/session-control/chatgpt/codex-5.6/OWNER_PREFERENCES.md

如果用户输入“启动56”，进入架构设计模式，继续读取：

6. .continuity/session-control/chatgpt/codex-5.6/PROJECT_BRIEF.md
7. .continuity/session-control/chatgpt/codex-5.6/HANDOFF.md

如果当前指令包含“【角色绑定】CODEX_56_FINAL_REVIEW”，进入最终审核模式：

6. 读取 .continuity/session-control/chatgpt/codex-5.6/HANDOFF.md。
7. 核对短启动块指定的 final-review 调度文件 SHA-256，并只读取该一个调度文件。
8. 再只读取调度文件指定的 Context Pack、Review Pack 或 Task Final Review Pack。
9. 不读取 PROJECT_BRIEF.md、docs/planning、其他调度修订或前序审核者结论。

不要读取其他角色目录。

读取完成后，先用简短中文说明：

- 你当前的角色和模式。
- 项目现在处于什么状态。
- 当前唯一的下一步。
- 是否存在阻塞。

只有 HANDOFF.md 或用户当前指令明确指定了任务时才继续工作；否则保持等待。
