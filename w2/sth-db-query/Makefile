# Database Query Tool - Makefile
# 用于管理项目的构建、运行、测试和维护任务

.PHONY: help build up down restart logs clean test lint format db-init db-reset api-test frontend-dev backend-dev setup

# 默认目标
help: ## 显示帮助信息
	@echo "Database Query Tool - 可用命令:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

# === 环境管理 ===

setup: ## 初始设置项目环境
	@echo "🚀 设置项目环境..."
	cd backend && uv sync
	cd frontend && npm install
	@echo "✅ 项目环境设置完成"

backend-setup: ## 设置后端环境
	@echo "🔧 设置后端环境..."
	cd backend && uv sync
	@echo "✅ 后端环境设置完成"

frontend-setup: ## 设置前端环境
	@echo "🎨 设置前端环境..."
	cd frontend && npm install
	@echo "✅ 前端环境设置完成"

# === 开发服务器 ===

dev: ## 启动所有开发服务器 (Docker Compose)
	@echo "🚀 启动所有开发服务器..."
	docker-compose up --build -d
	@echo "✅ 开发服务器已启动"
	@echo "📊 后端API: http://localhost:8000"
	@echo "🎨 前端应用: http://localhost:5173"
	@echo "📝 API文档: http://localhost:8000/docs"

dev-down: ## 停止所有开发服务器
	@echo "🛑 停止开发服务器..."
	docker-compose down
	@echo "✅ 开发服务器已停止"

backend-dev: ## 仅启动后端开发服务器
	@echo "🔧 启动后端开发服务器..."
	cd backend && uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
	@echo "✅ 后端服务器已启动: http://localhost:8000"

frontend-dev: ## 仅启动前端开发服务器
	@echo "🎨 启动前端开发服务器..."
	cd frontend && npm run dev
	@echo "✅ 前端服务器已启动: http://localhost:5173"

# === 数据库管理 ===

db-init: ## 初始化数据库
	@echo "🗄️ 初始化数据库..."
	cd backend && python init_db.py
	@echo "✅ 数据库初始化完成"

db-reset: ## 重置数据库 (删除并重新创建)
	@echo "🔄 重置数据库..."
	rm -rf .db_query/
	mkdir -p .db_query
	cd backend && python init_db.py
	@echo "✅ 数据库重置完成"

# === 构建和部署 ===

build: ## 构建所有服务
	@echo "🔨 构建所有服务..."
	docker-compose build
	@echo "✅ 构建完成"

backend-build: ## 构建后端
	@echo "🔨 构建后端..."
	cd backend && uv build --wheel
	@echo "✅ 后端构建完成"

frontend-build: ## 构建前端
	@echo "🔨 构建前端..."
	cd frontend && npm run build
	@echo "✅ 前端构建完成"

# === 测试 ===

test: ## 运行所有测试
	@echo "🧪 运行所有测试..."
	cd backend && uv run pytest
	cd frontend && npm test
	@echo "✅ 所有测试完成"

test-backend: ## 运行后端测试
	@echo "🧪 运行后端测试..."
	cd backend && uv run pytest -v --cov=app --cov-report=term-missing
	@echo "✅ 后端测试完成"

test-frontend: ## 运行前端测试
	@echo "🧪 运行前端测试..."
	cd frontend && npm test -- --coverage
	@echo "✅ 前端测试完成"

test-api: ## 使用REST Client测试API
	@echo "🔗 测试API端点..."
	@echo "请在VSCode中打开 fixtures/test.rest 文件"
	@echo "然后使用REST Client扩展执行测试"
	code fixtures/test.rest

# === 代码质量 ===

lint: ## 运行代码检查
	@echo "🔍 运行代码检查..."
	cd backend && uv run ruff check .
	cd frontend && npm run lint
	@echo "✅ 代码检查完成"

format: ## 格式化代码
	@echo "✨ 格式化代码..."
	cd backend && uv run ruff format .
	cd frontend && npm run format
	@echo "✅ 代码格式化完成"

type-check: ## 类型检查
	@echo "🔍 运行类型检查..."
	cd backend && uv run mypy app/
	cd frontend && npm run type-check
	@echo "✅ 类型检查完成"

# === 日志和监控 ===

logs: ## 查看所有服务日志
	@echo "📋 查看服务日志..."
	docker-compose logs -f

logs-backend: ## 查看后端日志
	@echo "📋 查看后端日志..."
	docker-compose logs -f backend

logs-frontend: ## 查看前端日志
	@echo "📋 查看前端日志..."
	docker-compose logs -f frontend

# === 清理 ===

clean: ## 清理构建产物和缓存
	@echo "🧹 清理项目..."
	# 停止容器
	docker-compose down -v 2>/dev/null || true
	# 清理Python缓存
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.pyc" -delete 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	# 清理Node缓存
	rm -rf frontend/node_modules/.cache 2>/dev/null || true
	rm -rf frontend/dist 2>/dev/null || true
	# 清理构建产物
	rm -rf backend/dist 2>/dev/null || true
	rm -rf backend/build 2>/dev/null || true
	@echo "✅ 项目清理完成"

clean-all: clean ## 深度清理 (包括依赖)
	@echo "🧹 深度清理项目..."
	# 清理Python虚拟环境
	rm -rf backend/.venv 2>/dev/null || true
	rm -rf backend/uv.lock 2>/dev/null || true
	# 清理Node依赖
	rm -rf frontend/node_modules 2>/dev/null || true
	rm -rf frontend/package-lock.json 2>/dev/null || true
	# 清理数据库
	rm -rf .db_query 2>/dev/null || true
	@echo "✅ 深度清理完成"

# === 快捷命令 ===

install: setup ## 安装所有依赖 (setup的别名)

run: dev ## 运行项目 (dev的别名)

stop: dev-down ## 停止项目 (dev-down的别名)

restart: ## 重启所有服务
	@echo "🔄 重启所有服务..."
	docker-compose restart
	@echo "✅ 服务重启完成"

status: ## 查看服务状态
	@echo "📊 服务状态:"
	docker-compose ps

# === 帮助信息 ===

info: ## 显示项目信息
	@echo "📋 Database Query Tool - 项目信息"
	@echo "=================================="
	@echo "后端技术栈: FastAPI, SQLAlchemy, Pydantic, SQLite"
	@echo "前端技术栈: React, Refine5, TypeScript, Tailwind CSS"
	@echo "数据库: SQLite (本地), PostgreSQL (测试)"
	@echo "API文档: http://localhost:8000/docs"
	@echo "前端应用: http://localhost:5173"
	@echo ""
	@echo "主要文件:"
	@echo "  - backend/pyproject.toml    - 后端依赖配置"
	@echo "  - frontend/package.json     - 前端依赖配置"
	@echo "  - docker-compose.yml        - 开发环境配置"
	@echo "  - fixtures/test.rest        - API测试用例"
	@echo "  - specs/                    - 项目规格文档"
