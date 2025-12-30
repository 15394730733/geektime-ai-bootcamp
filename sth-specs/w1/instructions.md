# instructions 

## project 需求和设计文档

构建一个简单的，使用标签分类和管理ticket的工具
它基于 postgresql 数据库, 使用Fast API 作为后端，使用
Typescript/vite/Unocss/Shadcn 作为前端。无需用户系统，当前用户可以：
- 创建/编辑/删除/完成/取消完成 ticket
- 添加/删除 ticket 的标签
- 按照不同的标签查看 ticket 列表
- 按 title 搜索ticket

按照这个想法，帮我生成详细的需求和设计文档，放在./sth-specs/w1/0001-spec.md 文件中。输出为中文

构建一个简单的，使用标签分类和管理ticket的工具
它基于 postgresql 数据库, 使用Fast API 作为后端，使用
Typescript/vite/Unocss/Shadcn 作为前端。无需用户系统，当前用户可以：
- 创建/编辑/删除/完成/取消完成 ticket
- 添加/删除 ticket 的标签
- 按照不同的标签查看 ticket 列表
- 按 title 搜索ticket

按照这个想法，帮我生成详细的需求和设计文档，放在./sth-specs/w1/0001-spec-by-claude.md 文件中。输出为中文。不要参考其他文档

## implementation plan

按照 ./sth-specs/w1/0001-spec.md 文件中的需求和设计文档，生成一个详细的实现计划，放在./sth-specs/w1/0002-implementation-plan.md 文件中。输出为中文

按照 ./sth-specs/w1/0001-spec-by-claude.md 文件中的需求和设计文档，生成一个详细的实现计划，放在./sth-specs/w1/0002-implementation-plan-by-claude.md 文件中。输出为中文。不要参考其他文档

## phased implementation

按照 ./sth-specs/w1/0002-implementation-plan.md，完整实现这个项目的代码。输出目录为./w1/sth-project/

## test.rest
帮我根据 rest client 撰写一个test.rest 文件，里面包含对所有支持api的测试

## seed.sql
添加一个 seed.sql, 里面放50个meaningful的ticket和 几十个tag （包含platform tag, 如ios， project tag 如 viking， 功能性tag 如 autocomplete，等等）。要求seed文件正确可以通过psql执行

## 优化ui
安装 apple website 的设计风格，深度思考，优化ui和ux。

## pre-commit & git-action

use pre-commit to init the config and set pre-commit for python and typescript for this project, also setup github action properly