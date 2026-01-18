# Quick Start: Database Query Tool

**Date**: 2025-12-30
**Target**: Developers setting up the database query tool for development

## Prerequisites

- **Python 3.12+** with uv package manager
- **Node.js 22+** with npm
- **PostgreSQL** (for testing target databases)
- **Git** for version control

## Environment Setup

### 1. Clone and Setup Project

```bash
# Navigate to w2 directory
cd w2

# Create project structure
mkdir -p sth-db-query/.db_query

# Initialize backend
cd sth-db-query/backend
uv init
```

### 2. Backend Dependencies

Create `pyproject.toml`:

```toml
[project]
name = "sth-db-query-backend"
version = "0.1.0"
description = "Database query tool backend"
requires-python = ">=3.12"
dependencies = [
    "fastapi>=0.104.0",
    "uvicorn[standard]>=0.24.0",
    "sqlalchemy>=2.0.0",
    "alembic>=1.12.0",
    "psycopg2-binary>=2.9.0",
    "sqlglot>=20.0.0",
    "openai>=1.0.0",
    "pydantic>=2.5.0",
    "python-dotenv>=1.0.0",
    "aiosqlite>=0.19.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

Install dependencies:

```bash
uv sync
```

### 3. Environment Variables

Create `.env` file in backend directory:

```bash
# GLM API Configuration
GLM_API_KEY=your_glm_api_key_here
GLM_BASE_URL=https://open.bigmodel.cn/api/paas/v4/

# Database Configuration (SQLite for local storage)
DATABASE_URL=sqlite:///./.db_query/db_query.db

# Server Configuration
HOST=0.0.0.0
PORT=8000

# Development Settings
DEBUG=true
LOG_LEVEL=INFO
```

### 4. Frontend Setup

```bash
# From project root
cd w2/sth-db-query/frontend

# Initialize React + TypeScript project
npm create vite@latest . -- --template react-ts

# Install dependencies
npm install @refinedev/core @refinedev/react-router-v6 @refinedev/simple-rest
npm install @refinedev/ui @refinedev/antd
npm install @monaco-editor/react monaco-editor
npm install tailwindcss @tailwindcss/forms autoprefixer postcss
npm install axios lucide-react

# Install dev dependencies
npm install -D @types/node vitest @testing-library/react @testing-library/jest-dom
```

### 5. Frontend Configuration

Update `vite.config.ts`:

```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
```

Update `tailwind.config.js`:

```javascript
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
```

## Database Initialization

### 1. Create SQLite Database

```bash
# From backend directory
python -c "
import sqlite3
import os

os.makedirs('../.db_query', exist_ok=True)
conn = sqlite3.connect('../.db_query/db_query.db')
conn.execute('''
CREATE TABLE database_connections (
    id TEXT PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    url TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT 1
)
''')
conn.execute('''
CREATE TABLE database_metadata (
    id TEXT PRIMARY KEY,
    connection_id TEXT NOT NULL,
    object_type TEXT NOT NULL,
    schema_name TEXT DEFAULT 'public',
    object_name TEXT NOT NULL,
    columns TEXT NOT NULL,  -- JSON string
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (connection_id) REFERENCES database_connections(id)
)
''')
conn.commit()
conn.close()
print('Database initialized successfully')
"
```

### 2. Test Database Connection

Create a test PostgreSQL database:

```sql
-- In PostgreSQL
CREATE DATABASE test_db;
\c test_db;

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    amount DECIMAL(10,2) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO users (name, email) VALUES
('Alice Johnson', 'alice@example.com'),
('Bob Smith', 'bob@example.com'),
('Carol Williams', 'carol@example.com');

INSERT INTO orders (user_id, amount, status) VALUES
(1, 99.99, 'completed'),
(2, 149.50, 'pending'),
(1, 75.00, 'completed');
```

## Running the Application

### 1. Start Backend

```bash
# From backend directory
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API will be available at: http://localhost:8000
API documentation at: http://localhost:8000/docs

### 2. Start Frontend

```bash
# From frontend directory (new terminal)
npm run dev
```

Frontend will be available at: http://localhost:5173

## Testing the Application

### 1. Add Database Connection

```bash
curl -X PUT http://localhost:8000/api/v1/dbs/test-db \
  -H "Content-Type: application/json" \
  -d '{
    "url": "postgresql://user:password@localhost:5432/test_db",
    "description": "Test database for development"
  }'
```

### 2. Get Database Metadata

```bash
curl http://localhost:8000/api/v1/dbs/test-db
```

### 3. Execute SQL Query

```bash
curl -X POST http://localhost:8000/api/v1/dbs/test-db/query \
  -H "Content-Type: application/json" \
  -d '{
    "sql": "SELECT * FROM users LIMIT 5"
  }'
```

### 4. Natural Language Query

```bash
curl -X POST http://localhost:8000/api/v1/dbs/test-db/query/natural \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "显示所有用户及其订单总金额"
  }'
```

## Development Workflow

### Backend Development

```bash
# Run tests
uv run pytest

# Format code
uv run black .
uv run isort .

# Type checking
uv run mypy .
```

### Frontend Development

```bash
# Run tests
npm test

# Format code
npm run format

# Type checking
npm run type-check
```

## Troubleshooting

### Common Issues

1. **CORS Errors**: Ensure backend has CORS middleware enabled for all origins
2. **Database Connection**: Verify PostgreSQL is running and credentials are correct
3. **GLM API**: Check API key and base URL in environment variables
4. **Port Conflicts**: Ensure ports 8000 (backend) and 5173 (frontend) are available

### Debug Mode

Enable debug logging:

```bash
# Backend
export LOG_LEVEL=DEBUG
uv run uvicorn app.main:app --reload

# Frontend
npm run dev -- --mode development
```

## Next Steps

1. **Add Database Connection**: Use the frontend to add your first database
2. **Explore Metadata**: View table structures and relationships
3. **Run Queries**: Test both manual SQL and natural language queries
4. **Customize UI**: Modify components to match your preferences

For detailed implementation, see the specification and implementation plan in the `specs/001-db-query-tool/` directory.
