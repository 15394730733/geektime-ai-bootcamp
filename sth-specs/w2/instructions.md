# Instructions

## constitution 

这是针对 ./w2/sth-db-query 项目的:

- 使用 Ergonomic Python 风格来编写代码，前端使用typeScript
- 前后端都要有严格的类型标注
- 使用pydantic来定义数据模型
- 所有后端生成的json数据，使用 camelCase 格式。
- 不需要 authentication，任何用户都可以使用。

## 基本思路
这是一个数据库查询工具，用户可以添加一个db url，系统会连接到数据库，获取数据库的metadata，然后将数据库中的table和view的信息展示出来，然后用户可以自己输入sql查询，也可以通过自然语言来生成sql查询。

基本想法：
- 数据库连接字符串和数据库的metadata都会存储到sqlite数据库中。我们可以根据postgres 的功能来查询系统中的表和视图的信息，然后用llm来将这些信息转换成json格式，然后存储到sqlite数据库中，这个信息以后可以复用。
- 当用户使用llm来生成sql查询时，我们可以把系统中的表和视图的信息作为context传递给llm，然后llm会根据这些信息来生成sql查询
- 任何输入的sql语句，都需要经过sqlparser解析，确保语法正确，并且仅包含select 语句。如果语法不正确，需要给出错误信息。
- 如果查询不包含limit子句，则默认添加limit 1000 子句。
- 输出格式是json，前端将其组织成表格，并展示出来.


后端使用python（uv） / FastAPI / sqlglot / openai sdk 来实现。
前端使用 React /refine5 /tailwind / ant design 来实现。 Sql editor 使用 monaco editor 来实现。

GLM-api-key在编码后预留出来环境变量文件方便我补充，数据库连接和metadata存储在sqlite数据库中，放在./w2/sth-db-query/.db_query、db_query.db中。

后端API 需要支持cors, 允许所有origin。
大致API 如下：
```bash
# 获取所有已存储的数据库
GET /api/v1/dbs
# 添加一个数据库
PUT /api/v1/dbs/{name}

{
  "url": "postgresql://user:pass@localhost:5432/mydb",
  "description": "My local database"
}

# 获取一个数据库的metadata
GET /api/v1/dbs/{name}

# 查询某个数据库的信息
POST /api/v1/dbs/{name}/query
{
  "sql": "SELECT * FROM users"
}

# 通过自然语言生成sql查询
POST /api/v1/dbs/{name}/query/natural
{
  "prompt": "查询用户表的所有信息"
}
```

## 测试
运行后端和前端，根据test.rest 用curl 测试后端已实现的路由；然后用playwright代开前端进行测试，任何测试问题，都请深度思考后再修复

## ui ux界面优化 

![alt text](image.png) query界面使用这样的页面布局

其他可参考
按照 apple website 的设计风格,think ultra hard,优化 UI 和 UX。  


## code review
/speckit.analyze 仔细 review w2/sth-db_query 代码，删除不用的代码，添加更多 unit test,以及寻找opportunity

# 其他
根据 @specs/001-db-query-tool/spec.md 和@specs/001-db-query-tool/plan.md 撰写详细介绍。