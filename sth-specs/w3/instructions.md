# Instructions

## code review command

帮我参照 .claude/commands/speckit.specify.md 的结构，非常努力的深度思考，构建一个对Python和 TypeScript 代码进行深度代码审查的命令，放在 .claude/commands/下。主要考虑几个方面

- 架构和设计：是否考虑python 和TypeScript 的架构和设计最佳实践？是否有清晰的接口设计？是否考虑一定程度的可扩展性
- KISS 原则
- 代码质量：DRY, YAGNI, SOLID, etc. 函数原则上不超过150行，参数原则上不超过7个。
- 使用builder 模式