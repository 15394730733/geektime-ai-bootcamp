# instructions
## 阅读 codex 代码
仔细阅读 ./venders/codex 的代码，撰写一个详细的架构分析文档，如需图表，使用mermaid chart。文档放在：./sth-specs/w4/codex-arch-by-claude.md

## 事件循环
帮我梳理codex代码处理事件循环的部分，详细解读当用户发起一个任务后，codex是如何分解处理这个任务，并不断自我迭代，最终完成整个任务。这个过程中发生了什么，codex如何决定任务完成还是未完成需要继续迭代。如果需要，可以用mermaid chart来辅助说明。写入./sth-specs/w4/codex-event-loop.md

## 工具调用
帮我梳理codex 代码处理工具调用的部分，详细解读codex 是如何知道有哪些工具可以调用，如何选择工具，如何调用工具，如何处理工具的返回结果，如何决定工具调用是否成功等等。如果需要，可以用 mermaid chart来辅助说明。写入 ./sth-specs/w4/codex-tool-call.md