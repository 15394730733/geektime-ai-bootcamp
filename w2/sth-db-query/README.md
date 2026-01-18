# Database Query Tool

A web-based database query tool that allows users to connect to databases, explore metadata, and execute SQL queries through both direct SQL input and natural language processing.

## Project Structure

```
w2/sth-db-query/
├── .db_query/
│   └── db_query.db          # SQLite database for connections and metadata
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py          # FastAPI application
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   └── v1/
│   │   │       ├── __init__.py
│   │   │       ├── api.py   # API router configuration
│   │   │       └── endpoints/
│   │   │           ├── __init__.py
│   │   │           ├── databases.py  # Database management endpoints
│   │   │           └── queries.py    # Query execution endpoints
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py    # Application configuration
│   │   │   ├── database.py  # Database connection setup
│   │   │   └── security.py  # SQL validation logic
│   │   ├── crud/
│   │   │   ├── __init__.py
│   │   │   └── database.py  # Database CRUD operations
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── database.py  # Database connection models
│   │   │   ├── metadata.py  # Metadata models
│   │   │   └── query.py     # Query models
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── database.py  # Pydantic schemas
│   │   │   └── query.py     # Query schemas
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── database.py  # Database connection service
│   │   │   └── llm.py       # LLM integration service
│   │   └── utils/
│   │       ├── __init__.py
│   │       └── response.py  # Response utilities
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── conftest.py
│   │   └── test_*.py        # Test files
│   ├── pyproject.toml       # Python dependencies (uv)
│   ├── .env                 # Environment variables
│   └── .env.example         # Environment variables template
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── DatabaseList.tsx
│   │   │   ├── DatabaseForm.tsx
│   │   │   ├── MetadataViewer.tsx
│   │   │   ├── QueryEditor.tsx
│   │   │   ├── QueryResults.tsx
│   │   │   ├── NaturalLanguageInput.tsx
│   │   │   └── index.ts
│   │   ├── pages/
│   │   │   ├── databases.tsx
│   │   │   └── Query.tsx
│   │   ├── services/
│   │   │   ├── api.ts
│   │   │   ├── dataProvider.ts
│   │   │   └── types.ts
│   │   ├── contexts/
│   │   │   └── color-mode.tsx
│   │   ├── styles/
│   │   │   ├── globals.css
│   │   │   └── tailwind.css
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── tests/
│   ├── package.json         # Node.js dependencies
│   ├── tsconfig.json        # TypeScript configuration
│   ├── tailwind.config.js   # Tailwind CSS configuration
│   └── vite.config.ts       # Vite configuration
├── docker-compose.yml       # Development environment
└── README.md
```

## Technologies

### Backend
- **Python 3.12+** with uv package manager
- **FastAPI** - Modern web framework for building APIs
- **SQLAlchemy** - SQL toolkit and ORM
- **sqlglot** - SQL parser and transpiler for validation
- **OpenAI SDK** - Natural language to SQL conversion
- **Pydantic** - Data validation using Python type annotations
- **SQLite** - Local metadata storage
- **PostgreSQL** - Target database for querying

### Frontend
- **React 19+** with TypeScript
- **Refine** - React framework for building admin panels
- **Ant Design** - UI component library
- **Monaco Editor** - Code editor for SQL input
- **Tailwind CSS** - Utility-first CSS framework
- **Vite** - Build tool and development server

## Getting Started

### Backend Setup
1. Navigate to the backend directory: `cd backend`
2. Install dependencies: `uv sync`
3. Copy environment template: `cp .env.example .env`
4. Update `.env` with your OpenAI API key
5. Start the server: `uv run python -m app.main`

### Frontend Setup
1. Navigate to the frontend directory: `cd frontend`
2. Install dependencies: `npm install`
3. Start the development server: `npm run dev`

### Development Environment
Use Docker Compose for a complete development environment:
```bash
docker-compose up -d
```

## API Endpoints

- `GET /api/v1/dbs` - List all databases
- `PUT /api/v1/dbs/{name}` - Add a database connection
- `GET /api/v1/dbs/{name}` - Get database metadata
- `POST /api/v1/dbs/{name}/query` - Execute SQL query
- `POST /api/v1/dbs/{name}/query/natural` - Natural language query

## Features

- **Database Management**: Connect to and manage multiple PostgreSQL databases
- **Metadata Exploration**: Browse database schemas, tables, and columns
- **SQL Query Execution**: Execute SQL queries with syntax validation and safety checks
- **Natural Language Processing**: Convert natural language to SQL using OpenAI
- **Query Results Export**: Export results to CSV and JSON formats
- **Error Handling**: Comprehensive error messages and validation