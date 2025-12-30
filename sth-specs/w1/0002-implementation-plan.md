# Ticket 标签管理工具实现计划

## 1. 项目概述

本实现计划基于 `0001-spec.md` 中的需求和设计文档，详细描述了 Ticket 标签管理工具的开发步骤、技术实现和交付标准。项目采用前后端分离架构，后端基于 FastAPI 0.115.0 和 PostgreSQL 17.0，前端使用 Vue3 3.5.26 + TypeScript 5.9.3、Vite 8.0.0、UnoCSS 0.60.2 和 Element Plus 2.13.0。

## 2. 项目结构

### 2.1 整体目录结构

```
ticket-manager/
├── backend/                    # 后端项目
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py            # 应用入口
│   │   ├── config.py          # 配置管理
│   │   ├── database.py        # 数据库连接
│   │   ├── models/            # 数据模型
│   │   │   ├── __init__.py
│   │   │   ├── ticket.py
│   │   │   └── tag.py
│   │   ├── schemas/           # Pydantic 模型
│   │   │   ├── __init__.py
│   │   │   ├── ticket.py
│   │   │   └── tag.py
│   │   ├── api/               # API 路由
│   │   │   ├── __init__.py
│   │   │   ├── tickets.py
│   │   │   └── tags.py
│   │   ├── crud/              # 数据库操作
│   │   │   ├── __init__.py
│   │   │   ├── ticket.py
│   │   │   └── tag.py
│   │   ├── core/              # 核心功能
│   │   │   ├── __init__.py
│   │   │   ├── security.py
│   │   │   └── deps.py
│   │   └── utils/             # 工具函数
│   │       ├── __init__.py
│   │       └── response.py
│   ├── tests/                 # 测试文件
│   ├── alembic/               # 数据库迁移
│   ├── requirements.txt       # Python 依赖
│   ├── Dockerfile
│   └── .env.example
├── frontend/                   # 前端项目
│   ├── src/
│   │   ├── main.ts
│   │   ├── App.vue
│   │   ├── components/        # Vue 组件
│   │   │   ├── TicketList.vue
│   │   │   ├── TicketDetail.vue
│   │   │   ├── TicketForm.vue
│   │   │   ├── TagCloud.vue
│   │   │   ├── SearchBar.vue
│   │   │   └── FilterPanel.vue
│   │   ├── views/             # 页面视图
│   │   │   ├── Home.vue
│   │   │   └── TicketDetail.vue
│   │   ├── api/               # API 封装
│   │   │   ├── tickets.ts
│   │   │   └── tags.ts
│   │   ├── stores/            # 状态管理
│   │   │   ├── ticket.ts
│   │   │   └── tag.ts
│   │   ├── types/             # TypeScript 类型
│   │   │   ├── ticket.ts
│   │   │   └── tag.ts
│   │   ├── utils/             # 工具函数
│   │   │   └── request.ts
│   │   └── assets/            # 静态资源
│   ├── tests/                 # 测试文件
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   ├── unocss.config.ts
│   └── Dockerfile
├── docker-compose.yml         # Docker Compose 配置
├── .gitignore
└── README.md
```

## 3. 后端实现计划

### 3.1 环境准备

#### 3.1.1 开发环境搭建

**任务描述**：搭建后端开发环境，安装必要的依赖和工具

**具体步骤**：
1. 创建 Python 虚拟环境
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

2. 安装核心依赖
   ```bash
   pip install fastapi==0.115.0
   pip install uvicorn[standard]==0.32.0
   pip install sqlalchemy==2.0.36
   pip install asyncpg==0.29.0
   pip install pydantic==2.9.2
   pip install pydantic-settings==2.6.1
   pip install alembic==1.14.0
   pip install python-jose[cryptography]==3.3.0
   pip install passlib[bcrypt]==1.7.4
   ```

3. 安装开发依赖
   ```bash
   pip install pytest==8.3.3
   pip install pytest-asyncio==0.24.0
   pip install httpx==0.27.2
   pip install black==24.10.0
   pip install flake8==7.1.1
   pip install mypy==1.13.0
   ```

**交付标准**：
- 虚拟环境创建成功
- 所有依赖安装完成
- requirements.txt 文件生成

**预计时间**：0.5 天

---

### 3.2 数据库设计与实现

#### 3.2.1 数据库模型定义

**任务描述**：使用 SQLAlchemy 定义数据库模型

**具体步骤**：
1. 创建数据库配置文件 `app/config.py`
   ```python
   from pydantic_settings import BaseSettings
   
   class Settings(BaseSettings):
       DATABASE_URL: str = "postgresql+asyncpg://user:pass@localhost/db"
       SECRET_KEY: str = "your-secret-key"
       ALGORITHM: str = "HS256"
       ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
   ```

2. 创建数据库连接文件 `app/database.py`
   ```python
   from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
   from sqlalchemy.ext.declarative import declarative_base
   from sqlalchemy.orm import sessionmaker
   
   engine = create_async_engine(settings.DATABASE_URL, echo=True)
   AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
   Base = declarative_base()
   ```

3. 定义 Ticket 模型 `app/models/ticket.py`
   ```python
   from sqlalchemy import Column, String, Boolean, DateTime
   from sqlalchemy.dialects.postgresql import UUID
   import uuid
   
   class Ticket(Base):
       __tablename__ = "tickets"
       
       id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
       title = Column(String(255), nullable=False)
       description = Column(String)
       is_completed = Column(Boolean, default=False)
       created_at = Column(DateTime, default=datetime.utcnow)
       updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
   ```

4. 定义 Tag 模型 `app/models/tag.py`
   ```python
   from sqlalchemy import Column, String, DateTime
   from sqlalchemy.dialects.postgresql import UUID
   import uuid
   
   class Tag(Base):
       __tablename__ = "tags"
       
       id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
       name = Column(String(50), nullable=False, unique=True)
       color = Column(String(7), default="#0070f3")
       created_at = Column(DateTime, default=datetime.utcnow)
   ```

5. 定义 TicketTag 关联模型 `app/models/ticket.py`
   ```python
   class TicketTag(Base):
       __tablename__ = "ticket_tags"
       
       id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
       ticket_id = Column(UUID(as_uuid=True), ForeignKey("tickets.id", ondelete="CASCADE"))
       tag_id = Column(UUID(as_uuid=True), ForeignKey("tags.id", ondelete="CASCADE"))
       created_at = Column(DateTime, default=datetime.utcnow)
       
       ticket = relationship("Ticket", back_populates="tags")
       tag = relationship("Tag", back_populates="tickets")
   ```

**交付标准**：
- 所有数据库模型定义完成
- 模型之间的关系正确建立
- 通过 mypy 类型检查

**预计时间**：1 天

---

#### 3.2.2 数据库迁移配置

**任务描述**：使用 Alembic 配置数据库迁移

**具体步骤**：
1. 初始化 Alembic
   ```bash
   alembic init alembic
   ```

2. 配置 `alembic.ini`
   ```ini
   sqlalchemy.url = postgresql+asyncpg://user:pass@localhost/db
   ```

3. 配置 `alembic/env.py`
   ```python
   from app.database import Base
   target_metadata = Base.metadata
   ```

4. 创建初始迁移
   ```bash
   alembic revision --autogenerate -m "Initial migration"
   ```

5. 执行迁移
   ```bash
   alembic upgrade head
   ```

**交付标准**：
- Alembic 配置完成
- 初始迁移脚本生成
- 数据库表创建成功

**预计时间**：0.5 天

---

### 3.3 Pydantic 模型定义

#### 3.3.1 Ticket Schemas

**任务描述**：定义 Ticket 相关的 Pydantic 模型

**具体步骤**：
1. 创建 `app/schemas/ticket.py`
   ```python
   from pydantic import BaseModel, Field
   from datetime import datetime
   from typing import List, Optional
   from uuid import UUID
   
   class TagBase(BaseModel):
       id: UUID
       name: str
       color: str
   
   class TicketBase(BaseModel):
       title: str = Field(..., min_length=1, max_length=255)
       description: Optional[str] = None
   
   class TicketCreate(TicketBase):
       tags: Optional[List[str]] = None
   
   class TicketUpdate(TicketBase):
       is_completed: Optional[bool] = None
   
   class TicketResponse(TicketBase):
       id: UUID
       is_completed: bool
       created_at: datetime
       updated_at: datetime
       tags: List[TagBase]
       
       class Config:
           from_attributes = True
   ```

**交付标准**：
- 所有 Pydantic 模型定义完成
- 数据验证规则正确设置
- 通过类型检查

**预计时间**：0.5 天

---

#### 3.3.2 Tag Schemas

**任务描述**：定义 Tag 相关的 Pydantic 模型

**具体步骤**：
1. 创建 `app/schemas/tag.py`
   ```python
   from pydantic import BaseModel, Field
   from datetime import datetime
   from uuid import UUID
   
   class TagBase(BaseModel):
       name: str = Field(..., min_length=1, max_length=50)
       color: str = Field(default="#0070f3", pattern=r"^#[0-9a-fA-F]{6}$")
   
   class TagCreate(TagBase):
       pass
   
   class TagResponse(TagBase):
       id: UUID
       created_at: datetime
       
       class Config:
           from_attributes = True
   ```

**交付标准**：
- 所有 Pydantic 模型定义完成
- 数据验证规则正确设置
- 通过类型检查

**预计时间**：0.5 天

---

### 3.4 CRUD 操作实现

#### 3.4.1 Ticket CRUD

**任务描述**：实现 Ticket 的数据库操作

**具体步骤**：
1. 创建 `app/crud/ticket.py`
   ```python
   from sqlalchemy.ext.asyncio import AsyncSession
   from sqlalchemy import select, and_, or_
   from app.models.ticket import Ticket, TicketTag
   from app.schemas.ticket import TicketCreate, TicketUpdate
   
   async def get_ticket(db: AsyncSession, ticket_id: UUID) -> Optional[Ticket]:
       result = await db.execute(select(Ticket).where(Ticket.id == ticket_id))
       return result.scalar_one_or_none()
   
   async def get_tickets(
       db: AsyncSession,
       skip: int = 0,
       limit: int = 100,
       tag: Optional[str] = None,
       search: Optional[str] = None
   ) -> tuple[List[Ticket], int]:
       query = select(Ticket)
       
       if tag:
           query = query.join(TicketTag).join(Tag).where(Tag.name == tag)
       
       if search:
           query = query.where(Ticket.title.ilike(f"%{search}%"))
       
       total_query = select(func.count()).select_from(query.subquery())
       total_result = await db.execute(total_query)
       total = total_result.scalar()
       
       query = query.offset(skip).limit(limit)
       result = await db.execute(query)
       tickets = result.scalars().all()
       
       return list(tickets), total
   
   async def create_ticket(db: AsyncSession, ticket: TicketCreate) -> Ticket:
       db_ticket = Ticket(**ticket.model_dump(exclude={"tags"}))
       db.add(db_ticket)
       await db.flush()
       
       if ticket.tags:
           for tag_name in ticket.tags:
               tag = await get_or_create_tag_by_name(db, tag_name)
               ticket_tag = TicketTag(ticket_id=db_ticket.id, tag_id=tag.id)
               db.add(ticket_tag)
       
       await db.commit()
       await db.refresh(db_ticket)
       return db_ticket
   
   async def update_ticket(
       db: AsyncSession,
       ticket_id: UUID,
       ticket: TicketUpdate
   ) -> Optional[Ticket]:
       db_ticket = await get_ticket(db, ticket_id)
       if db_ticket:
           update_data = ticket.model_dump(exclude_unset=True)
           for field, value in update_data.items():
               setattr(db_ticket, field, value)
           await db.commit()
           await db.refresh(db_ticket)
       return db_ticket
   
   async def delete_ticket(db: AsyncSession, ticket_id: UUID) -> bool:
       db_ticket = await get_ticket(db, ticket_id)
       if db_ticket:
           await db.delete(db_ticket)
           await db.commit()
           return True
       return False
   ```

**交付标准**：
- 所有 CRUD 操作实现完成
- 支持按标签筛选和标题搜索
- 通过单元测试

**预计时间**：1 天

---

#### 3.4.2 Tag CRUD

**任务描述**：实现 Tag 的数据库操作

**具体步骤**：
1. 创建 `app/crud/tag.py`
   ```python
   from sqlalchemy.ext.asyncio import AsyncSession
   from sqlalchemy import select
   from app.models.tag import Tag
   from app.schemas.tag import TagCreate
   
   async def get_tag(db: AsyncSession, tag_id: UUID) -> Optional[Tag]:
       result = await db.execute(select(Tag).where(Tag.id == tag_id))
       return result.scalar_one_or_none()
   
   async def get_tags(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Tag]:
       result = await db.execute(select(Tag).offset(skip).limit(limit))
       return list(result.scalars().all())
   
   async def get_tag_by_name(db: AsyncSession, name: str) -> Optional[Tag]:
       result = await db.execute(select(Tag).where(Tag.name == name))
       return result.scalar_one_or_none()
   
   async def create_tag(db: AsyncSession, tag: TagCreate) -> Tag:
       db_tag = Tag(**tag.model_dump())
       db.add(db_tag)
       await db.commit()
       await db.refresh(db_tag)
       return db_tag
   
   async def delete_tag(db: AsyncSession, tag_id: UUID) -> bool:
       db_tag = await get_tag(db, tag_id)
       if db_tag:
           await db.delete(db_tag)
           await db.commit()
           return True
       return False
   ```

**交付标准**：
- 所有 CRUD 操作实现完成
- 支持标签名称唯一性检查
- 通过单元测试

**预计时间**：0.5 天

---

### 3.5 API 路由实现

#### 3.5.1 Ticket API

**任务描述**：实现 Ticket 相关的 API 端点

**具体步骤**：
1. 创建 `app/api/tickets.py`
   ```python
   from fastapi import APIRouter, Depends, HTTPException, Query
   from sqlalchemy.ext.asyncio import AsyncSession
   from typing import Optional
   from uuid import UUID
   
   from app.database import get_db
   from app.schemas.ticket import TicketCreate, TicketUpdate, TicketResponse
   from app.crud.ticket import get_ticket, get_tickets, create_ticket, update_ticket, delete_ticket
   from app.utils.response import success_response, error_response
   
   router = APIRouter(prefix="/api/v1", tags=["tickets"])
   
   @router.post("/addTickets", response_model=dict)
   async def create_ticket_endpoint(
       ticket: TicketCreate,
       db: AsyncSession = Depends(get_db)
   ):
       db_ticket = await create_ticket(db, ticket)
       return success_response(data=str(db_ticket.id), message="Ticket 创建成功", code=200)
   
   @router.get("/listTickets", response_model=dict)
   async def get_tickets_endpoint(
       tag: Optional[str] = Query(None),
       search: Optional[str] = Query(None),
       skip: int = Query(0, ge=0),
       limit: int = Query(100, ge=1, le=100),
       db: AsyncSession = Depends(get_db)
   ):
       tickets, total = await get_tickets(db, skip=skip, limit=limit, tag=tag, search=search)
       return success_response(data={
           "tickets": tickets,
           "total": total
       })
   
   @router.get("/tickets/{ticket_id}", response_model=dict)
   async def get_ticket_endpoint(
       ticket_id: UUID,
       db: AsyncSession = Depends(get_db)
   ):
       ticket = await get_ticket(db, ticket_id)
       if not ticket:
           raise HTTPException(status_code=404, detail="Ticket 不存在")
       return success_response(data=ticket)
   
   @router.put("/updateTickets/{ticket_id}", response_model=dict)
   async def update_ticket_endpoint(
       ticket_id: UUID,
       ticket: TicketUpdate,
       db: AsyncSession = Depends(get_db)
   ):
       db_ticket = await update_ticket(db, ticket_id, ticket)
       if not db_ticket:
           raise HTTPException(status_code=404, detail="Ticket 不存在")
       return success_response(message="Ticket 更新成功")
   
   @router.delete("/tickets/{ticket_id}", response_model=dict)
   async def delete_ticket_endpoint(
       ticket_id: UUID,
       db: AsyncSession = Depends(get_db)
   ):
       success = await delete_ticket(db, ticket_id)
       if not success:
           raise HTTPException(status_code=404, detail="Ticket 不存在")
       return success_response(message="Ticket 删除成功", code=200)
   ```

**交付标准**：
- 所有 API 端点实现完成
- 支持请求参数验证
- 返回统一的响应格式
- 通过集成测试

**预计时间**：1 天

---

#### 3.5.2 Tag API

**任务描述**：实现 Tag 相关的 API 端点

**具体步骤**：
1. 创建 `app/api/tags.py`
   ```python
   from fastapi import APIRouter, Depends, HTTPException, Query
   from sqlalchemy.ext.asyncio import AsyncSession
   from uuid import UUID
   
   from app.database import get_db
   from app.schemas.tag import TagCreate, TagResponse
   from app.crud.tag import get_tag, get_tags, get_tag_by_name, create_tag, delete_tag
   from app.utils.response import success_response, error_response
   
   router = APIRouter(prefix="/api/v1", tags=["tags"])
   
   @router.get("/listTags", response_model=dict)
   async def get_tags_endpoint(
       skip: int = Query(0, ge=0),
       limit: int = Query(100, ge=1, le=100),
       db: AsyncSession = Depends(get_db)
   ):
       tags = await get_tags(db, skip=skip, limit=limit)
       return success_response(data={"tags": tags})
   
   @router.post("/addTags", response_model=dict)
   async def create_tag_endpoint(
       tag: TagCreate,
       db: AsyncSession = Depends(get_db)
   ):
       existing_tag = await get_tag_by_name(db, tag.name)
       if existing_tag:
           raise HTTPException(status_code=409, detail="标签已存在")
       db_tag = await create_tag(db, tag)
       return success_response(data=str(db_tag.id), message="标签创建成功", code=200)
   
   @router.post("/addTicketTags/{ticket_id}", response_model=dict)
   async def add_ticket_tags_endpoint(
       ticket_id: UUID,
       tag_ids: list[UUID],
       db: AsyncSession = Depends(get_db)
   ):
       ticket = await get_ticket(db, ticket_id)
       if not ticket:
           raise HTTPException(status_code=404, detail="Ticket 不存在")
       
       for tag_id in tag_ids:
           tag = await get_tag(db, tag_id)
           if not tag:
               raise HTTPException(status_code=404, detail=f"标签 {tag_id} 不存在")
           
           existing_relation = await db.execute(
               select(TicketTag).where(
                   and_(TicketTag.ticket_id == ticket_id, TicketTag.tag_id == tag_id)
               )
           )
           if not existing_relation.scalar_one_or_none():
               ticket_tag = TicketTag(ticket_id=ticket_id, tag_id=tag_id)
               db.add(ticket_tag)
       
       await db.commit()
       return success_response(message="标签添加成功")
   
   @router.delete("/deleteTicketTags/{ticket_id}/{tag_id}", response_model=dict)
   async def delete_ticket_tag_endpoint(
       ticket_id: UUID,
       tag_id: UUID,
       db: AsyncSession = Depends(get_db)
   ):
       ticket_tag = await db.execute(
           select(TicketTag).where(
               and_(TicketTag.ticket_id == ticket_id, TicketTag.tag_id == tag_id)
           )
       )
       ticket_tag = ticket_tag.scalar_one_or_none()
       if not ticket_tag:
           raise HTTPException(status_code=404, detail="标签关联不存在")
       
       await db.delete(ticket_tag)
       await db.commit()
       return success_response(message="标签移除成功")
   ```

**交付标准**：
- 所有 API 端点实现完成
- 支持请求参数验证
- 返回统一的响应格式
- 通过集成测试

**预计时间**：1 天

---

### 3.6 工具函数和中间件

#### 3.6.1 统一响应格式

**任务描述**：实现统一的 API 响应格式

**具体步骤**：
1. 创建 `app/utils/response.py`
   ```python
   from typing import Any, Optional
   from fastapi import status
   import time
   
   def success_response(
       data: Any = None,
       message: str = "success",
       code: int = status.HTTP_200_OK
   ) -> dict:
       return {
           "code": code,
           "message": message,
           "data": data,
           "timestamp": int(time.time() * 1000)
       }
   
   def error_response(
       message: str = "Internal Server Error",
       code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
       data: Any = None
   ) -> dict:
       return {
           "code": code,
           "message": message,
           "data": data,
           "timestamp": int(time.time() * 1000)
       }
   ```

**交付标准**：
- 统一响应格式实现完成
- 所有 API 使用统一响应格式

**预计时间**：0.5 天

---

#### 3.6.2 异常处理中间件

**任务描述**：实现全局异常处理

**具体步骤**：
1. 在 `app/main.py` 中添加异常处理
   ```python
   from fastapi import FastAPI, Request, status
   from fastapi.responses import JSONResponse
   from fastapi.exceptions import RequestValidationError
   from app.utils.response import error_response
   
   app = FastAPI(title="Ticket Manager API", version="1.0.0")
   
   @app.exception_handler(RequestValidationError)
   async def validation_exception_handler(request: Request, exc: RequestValidationError):
       return JSONResponse(
           status_code=status.HTTP_400_BAD_REQUEST,
           content=error_response(message="请求参数错误", data=exc.errors())
       )
   
   @app.exception_handler(Exception)
   async def general_exception_handler(request: Request, exc: Exception):
       return JSONResponse(
           status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
           content=error_response(message=str(exc))
       )
   ```

**交付标准**：
- 全局异常处理实现完成
- 所有异常返回统一格式

**预计时间**：0.5 天

---

### 3.7 应用入口和配置

**任务描述**：完成应用入口配置和路由注册

**具体步骤**：
1. 创建 `app/main.py`
   ```python
   from fastapi import FastAPI
   from fastapi.middleware.cors import CORSMiddleware
   from app.api import tickets, tags
   
   app = FastAPI(
       title="Ticket Manager API",
       description="Ticket 标签管理工具后端 API",
       version="1.0.0"
   )
   
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["http://localhost:3000"],
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   
   app.include_router(tickets.router)
   app.include_router(tags.router)
   
   @app.get("/")
   async def root():
       return {"message": "Ticket Manager API"}
   
   @app.get("/health")
   async def health_check():
       return {"status": "healthy"}
   ```

2. 创建 `.env.example`
   ```env
   DATABASE_URL=postgresql+asyncpg://ticketadmin:ticketpass@localhost:5432/ticketdb
   SECRET_KEY=your-secret-key-here
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ```

**交付标准**：
- 应用启动成功
- 所有路由正确注册
- CORS 配置正确
- 健康检查接口可用

**预计时间**：0.5 天

---

## 4. 前端实现计划

### 4.1 环境准备

#### 4.1.1 项目初始化

**任务描述**：使用 Vite 初始化 Vue3 + TypeScript 项目

**具体步骤**：
1. 创建项目
   ```bash
   npm create vite@latest frontend -- --template vue-ts
   cd frontend
   ```

2. 安装依赖
   ```bash
   pnpm install
   pnpm install vue-router@4.4.5
   pnpm install pinia@2.2.6
   pnpm install axios@1.7.7
   pnpm install element-plus@2.13.0
   pnpm install @element-plus/icons-vue@2.3.1
   pnpm install unocss@0.60.2
   pnpm install -D @types/node
   ```

3. 配置 TypeScript
   ```json
   {
     "compilerOptions": {
       "target": "ES2020",
       "useDefineForClassFields": true,
       "module": "ESNext",
       "lib": ["ES2020", "DOM", "DOM.Iterable"],
       "skipLibCheck": true,
       "moduleResolution": "bundler",
       "allowImportingTsExtensions": true,
       "resolveJsonModule": true,
       "isolatedModules": true,
       "noEmit": true,
       "jsx": "preserve",
       "strict": true,
       "noUnusedLocals": true,
       "noUnusedParameters": true,
       "noFallthroughCasesInSwitch": true,
       "baseUrl": ".",
       "paths": {
         "@/*": ["src/*"]
       }
     },
     "include": ["src/**/*.ts", "src/**/*.d.ts", "src/**/*.tsx", "src/**/*.vue"],
     "references": [{ "path": "./tsconfig.node.json" }]
   }
   ```

**交付标准**：
- 项目创建成功
- 所有依赖安装完成
- TypeScript 配置正确

**预计时间**：0.5 天

---

#### 4.1.2 UnoCSS 配置

**任务描述**：配置 UnoCSS 原子化 CSS 框架

**具体步骤**：
1. 创建 `unocss.config.ts`
   ```typescript
   import { defineConfig, presetUno, presetAttributify, presetIcons } from 'unocss'
   
   export default defineConfig({
     presets: [
       presetUno(),
       presetAttributify(),
       presetIcons({
         scale: 1.2,
       }),
     ],
     theme: {
       colors: {
         primary: '#0070f3',
         success: '#2ecc71',
         warning: '#f1c40f',
         danger: '#e74c3c',
       },
     },
   })
   ```

2. 在 `main.ts` 中引入
   ```typescript
   import { createApp } from 'vue'
   import App from './App.vue'
   import router from './router'
   import { createPinia } from 'pinia'
   import ElementPlus from 'element-plus'
   import 'element-plus/dist/index.css'
   import 'virtual:uno.css'
   
   const app = createApp(App)
   app.use(createPinia())
   app.use(router)
   app.use(ElementPlus)
   app.mount('#app')
   ```

**交付标准**：
- UnoCSS 配置完成
- 样式正常工作

**预计时间**：0.5 天

---

### 4.2 类型定义

#### 4.2.1 Ticket 类型

**任务描述**：定义 Ticket 相关的 TypeScript 类型

**具体步骤**：
1. 创建 `src/types/ticket.ts`
   ```typescript
   export interface Tag {
     id: string
     name: string
     color: string
   }
   
   export interface Ticket {
     id: string
     title: string
     description: string | null
     is_completed: boolean
     created_at: string
     updated_at: string
     tags: Tag[]
   }
   
   export interface TicketCreate {
     title: string
     description?: string
     tags?: string[]
   }
   
   export interface TicketUpdate {
     title?: string
     description?: string
     is_completed?: boolean
   }
   
   export interface TicketListResponse {
     tickets: Ticket[]
     total: number
   }
   
   export interface ApiResponse<T = any> {
     code: number
     message: string
     data: T
     timestamp: number
   }
   ```

**交付标准**：
- 所有类型定义完成
- 通过类型检查

**预计时间**：0.5 天

---

#### 4.2.2 Tag 类型

**任务描述**：定义 Tag 相关的 TypeScript 类型

**具体步骤**：
1. 创建 `src/types/tag.ts`
   ```typescript
   export interface Tag {
     id: string
     name: string
     color: string
   }
   
   export interface TagCreate {
     name: string
     color?: string
   }
   
   export interface TagListResponse {
     tags: Tag[]
   }
   
   export interface ApiResponse<T = any> {
     code: number
     message: string
     data: T
     timestamp: number
   }
   ```

**交付标准**：
- 所有类型定义完成
- 通过类型检查

**预计时间**：0.5 天

---

### 4.3 API 封装

#### 4.3.1 Axios 配置

**任务描述**：配置 Axios 实例和拦截器

**具体步骤**：
1. 创建 `src/utils/request.ts`
   ```typescript
   import axios, { AxiosInstance, AxiosError, InternalAxiosRequestConfig, AxiosResponse } from 'axios'
   import { ElMessage } from 'element-plus'
   
   const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
   
   const instance: AxiosInstance = axios.create({
     baseURL,
     timeout: 10000,
     headers: {
       'Content-Type': 'application/json',
     },
   })
   
   // 请求拦截器
   instance.interceptors.request.use(
     (config: InternalAxiosRequestConfig) => {
       const token = localStorage.getItem('token')
       if (token) {
         config.headers.Authorization = `Bearer ${token}`
       }
       return config
     },
     (error: AxiosError) => {
       return Promise.reject(error)
     }
   )
   
   // 响应拦截器
   instance.interceptors.response.use(
     (response: AxiosResponse) => {
       return response.data
     },
     (error: AxiosError) => {
       const message = error.response?.data?.message || error.message || '请求失败'
       ElMessage.error(message)
       return Promise.reject(error)
     }
   )
   
   export default instance
   ```

**交付标准**：
- Axios 配置完成
- 拦截器正常工作
- 错误处理正确

**预计时间**：0.5 天

---

#### 4.3.2 Ticket API

**任务描述**：封装 Ticket 相关的 API 请求

**具体步骤**：
1. 创建 `src/api/tickets.ts`
   ```typescript
   import request from '@/utils/request'
   import type { TicketCreate, TicketUpdate, TicketListResponse, ApiResponse } from '@/types/ticket'
   
   // 创建 Ticket
   export const createTicket = (data: TicketCreate) => {
     return request.post<ApiResponse<string>>('/api/v1/addTickets', data)
   }
   
   // 获取 Ticket 列表
   export const getTickets = (params: {
     tag?: string
     search?: string
     skip?: number
     limit?: number
   }) => {
     return request.get<ApiResponse<TicketListResponse>>('/api/v1/listTickets', { params })
   }
   
   // 获取单个 Ticket
   export const getTicket = (id: string) => {
     return request.get<ApiResponse<any>>(`/api/v1/tickets/${id}`)
   }
   
   // 更新 Ticket
   export const updateTicket = (id: string, data: TicketUpdate) => {
     return request.put<ApiResponse<void>>(`/api/v1/updateTickets/${id}`, data)
   }
   
   // 删除 Ticket
   export const deleteTicket = (id: string) => {
     return request.delete<ApiResponse<void>>(`/api/v1/tickets/${id}`)
   }
   ```

**交付标准**：
- 所有 API 方法封装完成
- 类型定义正确

**预计时间**：0.5 天

---

#### 4.3.3 Tag API

**任务描述**：封装 Tag 相关的 API 请求

**具体步骤**：
1. 创建 `src/api/tags.ts`
   ```typescript
   import request from '@/utils/request'
   import type { TagCreate, TagListResponse, ApiResponse } from '@/types/tag'
   
   // 获取所有标签
   export const getTags = (params?: { skip?: number; limit?: number }) => {
     return request.get<ApiResponse<TagListResponse>>('/api/v1/listTags', { params })
   }
   
   // 创建标签
   export const createTag = (data: TagCreate) => {
     return request.post<ApiResponse<string>>('/api/v1/addTags', data)
   }
   
   // 为 Ticket 添加标签
   export const addTicketTags = (ticketId: string, tagIds: string[]) => {
     return request.post<ApiResponse<void>>(`/api/v1/addTicketTags/${ticketId}`, { tag_ids: tagIds })
   }
   
   // 为 Ticket 移除标签
   export const deleteTicketTag = (ticketId: string, tagId: string) => {
     return request.delete<ApiResponse<void>>(`/api/v1/deleteTicketTags/${ticketId}/${tagId}`)
   }
   ```

**交付标准**：
- 所有 API 方法封装完成
- 类型定义正确

**预计时间**：0.5 天

---

### 4.4 状态管理

#### 4.4.1 Ticket Store

**任务描述**：使用 Pinia 管理 Ticket 状态

**具体步骤**：
1. 创建 `src/stores/ticket.ts`
   ```typescript
   import { defineStore } from 'pinia'
   import { ref, computed } from 'vue'
   import type { Ticket, TicketCreate, TicketUpdate, TicketListResponse } from '@/types/ticket'
   import * as ticketApi from '@/api/tickets'
   
   export const useTicketStore = defineStore('ticket', () => {
     const tickets = ref<Ticket[]>([])
     const total = ref(0)
     const loading = ref(false)
     const currentTicket = ref<Ticket | null>(null)
     
     const completedTickets = computed(() => 
       tickets.value.filter(t => t.is_completed)
     )
     
     const pendingTickets = computed(() => 
       tickets.value.filter(t => !t.is_completed)
     )
     
     // 获取 Ticket 列表
     const fetchTickets = async (params?: {
       tag?: string
       search?: string
       skip?: number
       limit?: number
     }) => {
       loading.value = true
       try {
         const response = await ticketApi.getTickets(params)
         tickets.value = response.data.tickets
         total.value = response.data.total
       } catch (error) {
         console.error('获取 Ticket 列表失败:', error)
       } finally {
         loading.value = false
       }
     }
     
     // 创建 Ticket
     const createTicket = async (data: TicketCreate) => {
       loading.value = true
       try {
         const response = await ticketApi.createTicket(data)
         await fetchTickets()
         return response.data
       } catch (error) {
         console.error('创建 Ticket 失败:', error)
         throw error
       } finally {
         loading.value = false
       }
     }
     
     // 更新 Ticket
     const updateTicket = async (id: string, data: TicketUpdate) => {
       loading.value = true
       try {
         await ticketApi.updateTicket(id, data)
         await fetchTickets()
       } catch (error) {
         console.error('更新 Ticket 失败:', error)
         throw error
       } finally {
         loading.value = false
       }
     }
     
     // 删除 Ticket
     const deleteTicket = async (id: string) => {
       loading.value = true
       try {
         await ticketApi.deleteTicket(id)
         await fetchTickets()
       } catch (error) {
         console.error('删除 Ticket 失败:', error)
         throw error
       } finally {
         loading.value = false
       }
     }
     
     // 切换完成状态
     const toggleComplete = async (id: string) => {
       const ticket = tickets.value.find(t => t.id === id)
       if (ticket) {
         await updateTicket(id, { is_completed: !ticket.is_completed })
       }
     }
     
     return {
       tickets,
       total,
       loading,
       currentTicket,
       completedTickets,
       pendingTickets,
       fetchTickets,
       createTicket,
       updateTicket,
       deleteTicket,
       toggleComplete,
     }
   })
   ```

**交付标准**：
- Ticket Store 实现完成
- 所有状态和方法正确
- 通过类型检查

**预计时间**：1 天

---

#### 4.4.2 Tag Store

**任务描述**：使用 Pinia 管理 Tag 状态

**具体步骤**：
1. 创建 `src/stores/tag.ts`
   ```typescript
   import { defineStore } from 'pinia'
   import { ref } from 'vue'
   import type { Tag, TagCreate, TagListResponse } from '@/types/tag'
   import * as tagApi from '@/api/tags'
   
   export const useTagStore = defineStore('tag', () => {
     const tags = ref<Tag[]>([])
     const loading = ref(false)
     
     // 获取所有标签
     const fetchTags = async () => {
       loading.value = true
       try {
         const response = await tagApi.getTags()
         tags.value = response.data.tags
       } catch (error) {
         console.error('获取标签列表失败:', error)
       } finally {
         loading.value = false
       }
     }
     
     // 创建标签
     const createTag = async (data: TagCreate) => {
       loading.value = true
       try {
         const response = await tagApi.createTag(data)
         await fetchTags()
         return response.data
       } catch (error) {
         console.error('创建标签失败:', error)
         throw error
       } finally {
         loading.value = false
       }
     }
     
     // 为 Ticket 添加标签
     const addTicketTags = async (ticketId: string, tagIds: string[]) => {
       loading.value = true
       try {
         await tagApi.addTicketTags(ticketId, tagIds)
       } catch (error) {
         console.error('添加标签失败:', error)
         throw error
       } finally {
         loading.value = false
       }
     }
     
     // 为 Ticket 移除标签
     const deleteTicketTag = async (ticketId: string, tagId: string) => {
       loading.value = true
       try {
         await tagApi.deleteTicketTag(ticketId, tagId)
       } catch (error) {
         console.error('移除标签失败:', error)
         throw error
       } finally {
         loading.value = false
       }
     }
     
     return {
       tags,
       loading,
       fetchTags,
       createTag,
       addTicketTags,
       deleteTicketTag,
     }
   })
   ```

**交付标准**：
- Tag Store 实现完成
- 所有状态和方法正确
- 通过类型检查

**预计时间**：0.5 天

---

### 4.5 路由配置

**任务描述**：配置 Vue Router 路由

**具体步骤**：
1. 创建 `src/router/index.ts`
   ```typescript
   import { createRouter, createWebHistory } from 'vue-router'
   import type { RouteRecordRaw } from 'vue-router'
   
   const routes: RouteRecordRaw[] = [
     {
       path: '/',
       name: 'Home',
       component: () => import('@/views/Home.vue'),
     },
     {
       path: '/tickets/:id',
       name: 'TicketDetail',
       component: () => import('@/views/TicketDetail.vue'),
       props: true,
     },
   ]
   
   const router = createRouter({
     history: createWebHistory(),
     routes,
   })
   
   export default router
   ```

**交付标准**：
- 路由配置完成
- 路由跳转正常

**预计时间**：0.5 天

---

### 4.6 组件开发

#### 4.6.1 TicketList 组件

**任务描述**：开发 Ticket 列表展示组件

**具体步骤**：
1. 创建 `src/components/TicketList.vue`
   ```vue
   <template>
     <div class="ticket-list">
       <el-card v-for="ticket in tickets" :key="ticket.id" class="ticket-card">
         <template #header>
           <div class="ticket-header">
             <el-checkbox
               :model-value="ticket.is_completed"
               @change="toggleComplete(ticket.id)"
             />
             <h3 class="ticket-title">{{ ticket.title }}</h3>
             <el-tag
               v-for="tag in ticket.tags"
               :key="tag.id"
               :color="tag.color"
               size="small"
               class="ml-2"
             >
               {{ tag.name }}
             </el-tag>
           </div>
         </template>
         
         <div class="ticket-content">
           <p>{{ ticket.description || '暂无描述' }}</p>
           <div class="ticket-footer">
             <span class="text-sm text-gray-500">
               {{ formatDate(ticket.created_at) }}
             </span>
             <div class="ticket-actions">
               <el-button size="small" @click="editTicket(ticket)">
                 编辑
               </el-button>
               <el-button size="small" type="danger" @click="confirmDelete(ticket)">
                 删除
               </el-button>
             </div>
           </div>
         </div>
       </el-card>
       
       <el-empty v-if="tickets.length === 0" description="暂无 Ticket" />
     </div>
   </template>
   
   <script setup lang="ts">
   import { computed } from 'vue'
   import { useRouter } from 'vue-router'
   import { useTicketStore } from '@/stores/ticket'
   import { ElMessageBox } from 'element-plus'
   import type { Ticket } from '@/types/ticket'
   
   const router = useRouter()
   const ticketStore = useTicketStore()
   
   const tickets = computed(() => ticketStore.tickets)
   
   const formatDate = (dateString: string) => {
     return new Date(dateString).toLocaleString('zh-CN')
   }
   
   const toggleComplete = async (id: string) => {
     await ticketStore.toggleComplete(id)
   }
   
   const editTicket = (ticket: Ticket) => {
     router.push(`/tickets/${ticket.id}`)
   }
   
   const confirmDelete = async (ticket: Ticket) => {
     try {
       await ElMessageBox.confirm(
         `确定要删除 Ticket "${ticket.title}" 吗？`,
         '确认删除',
         {
           confirmButtonText: '删除',
           cancelButtonText: '取消',
           type: 'warning',
         }
       )
       await ticketStore.deleteTicket(ticket.id)
     } catch (error) {
       // 用户取消删除
     }
   }
   </script>
   
   <style scoped>
   .ticket-list {
     display: flex;
     flex-direction: column;
     gap: 16px;
   }
   
   .ticket-card {
     transition: all 0.3s ease;
   }
   
   .ticket-card:hover {
     box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
   }
   
   .ticket-header {
     display: flex;
     align-items: center;
     gap: 12px;
   }
   
   .ticket-title {
     margin: 0;
     font-size: 16px;
     font-weight: 500;
   }
   
   .ticket-content {
     padding: 12px 0;
   }
   
   .ticket-footer {
     display: flex;
     justify-content: space-between;
     align-items: center;
     margin-top: 12px;
   }
   
   .ticket-actions {
     display: flex;
     gap: 8px;
   }
   </style>
   ```

**交付标准**：
- 组件功能完整
- 样式美观
- 交互流畅

**预计时间**：1 天

---

#### 4.6.2 TicketForm 组件

**任务描述**：开发 Ticket 创建/编辑表单组件

**具体步骤**：
1. 创建 `src/components/TicketForm.vue`
   ```vue
   <template>
     <el-dialog
       v-model="visible"
       :title="isEdit ? '编辑 Ticket' : '创建 Ticket'"
       width="600px"
       @close="handleClose"
     >
       <el-form
         ref="formRef"
         :model="form"
         :rules="rules"
         label-width="100px"
       >
         <el-form-item label="标题" prop="title">
           <el-input v-model="form.title" placeholder="请输入标题" />
         </el-form-item>
         
         <el-form-item label="描述" prop="description">
           <el-input
             v-model="form.description"
             type="textarea"
             :rows="4"
             placeholder="请输入描述"
           />
         </el-form-item>
         
         <el-form-item label="标签" prop="tags">
           <el-select
             v-model="form.tags"
             multiple
             filterable
             allow-create
             placeholder="请选择或创建标签"
             style="width: 100%"
           >
             <el-option
               v-for="tag in availableTags"
               :key="tag.id"
               :label="tag.name"
               :value="tag.name"
             />
           </el-select>
         </el-form-item>
         
         <el-form-item v-if="isEdit" label="完成状态" prop="is_completed">
           <el-switch v-model="form.is_completed" />
         </el-form-item>
       </el-form>
       
       <template #footer>
         <el-button @click="handleClose">取消</el-button>
         <el-button type="primary" :loading="loading" @click="handleSubmit">
           {{ isEdit ? '更新' : '创建' }}
         </el-button>
       </template>
     </el-dialog>
   </template>
   
   <script setup lang="ts">
   import { ref, computed, watch } from 'vue'
   import type { FormInstance, FormRules } from 'element-plus'
   import { useTicketStore } from '@/stores/ticket'
   import { useTagStore } from '@/stores/tag'
   import type { Ticket, TicketCreate, TicketUpdate } from '@/types/ticket'
   
   interface Props {
     modelValue: boolean
     ticket?: Ticket
   }
   
   interface Emits {
     (e: 'update:modelValue', value: boolean): void
     (e: 'success'): void
   }
   
   const props = defineProps<Props>()
   const emit = defineEmits<Emits>()
   
   const ticketStore = useTicketStore()
   const tagStore = useTagStore()
   
   const formRef = ref<FormInstance>()
   const loading = ref(false)
   
   const visible = computed({
     get: () => props.modelValue,
     set: (value) => emit('update:modelValue', value),
   })
   
   const isEdit = computed(() => !!props.ticket)
   
   const form = ref<TicketCreate & { is_completed?: boolean }>({
     title: '',
     description: '',
     tags: [],
     is_completed: false,
   })
   
   const rules: FormRules = {
     title: [
       { required: true, message: '请输入标题', trigger: 'blur' },
       { min: 1, max: 255, message: '标题长度在 1 到 255 个字符', trigger: 'blur' },
     ],
   }
   
   const availableTags = computed(() => tagStore.tags)
   
   watch(
     () => props.ticket,
     (ticket) => {
       if (ticket) {
         form.value = {
           title: ticket.title,
           description: ticket.description || '',
           tags: ticket.tags.map(t => t.name),
           is_completed: ticket.is_completed,
         }
       } else {
         form.value = {
           title: '',
           description: '',
           tags: [],
           is_completed: false,
         }
       }
     },
     { immediate: true }
   )
   
   const handleSubmit = async () => {
     if (!formRef.value) return
     
     await formRef.value.validate(async (valid) => {
       if (valid) {
         loading.value = true
         try {
           if (isEdit.value && props.ticket) {
             const updateData: TicketUpdate = {
               title: form.value.title,
               description: form.value.description,
               is_completed: form.value.is_completed,
             }
             await ticketStore.updateTicket(props.ticket.id, updateData)
           } else {
             await ticketStore.createTicket(form.value)
           }
           emit('success')
           handleClose()
         } catch (error) {
           console.error('提交失败:', error)
         } finally {
           loading.value = false
         }
       }
     })
   }
   
   const handleClose = () => {
     visible.value = false
     formRef.value?.resetFields()
   }
   </script>
   ```

**交付标准**：
- 表单验证正确
- 创建和编辑功能正常
- 标签选择支持多选和创建

**预计时间**：1 天

---

#### 4.6.3 TagCloud 组件

**任务描述**：开发标签云展示组件

**具体步骤**：
1. 创建 `src/components/TagCloud.vue`
   ```vue
   <template>
     <div class="tag-cloud">
       <h3 class="tag-cloud-title">标签</h3>
       <div class="tag-list">
         <el-tag
           v-for="tag in tags"
           :key="tag.id"
           :color="tag.color"
           :class="{ 'tag-active': selectedTag === tag.name }"
           class="tag-item"
           @click="selectTag(tag.name)"
         >
           {{ tag.name }}
         </el-tag>
         <el-tag
           v-if="selectedTag"
           class="tag-item"
           @click="selectTag(null)"
         >
           全部
         </el-tag>
       </div>
     </div>
   </template>
   
   <script setup lang="ts">
   import { computed } from 'vue'
   import { useTagStore } from '@/stores/tag'
   
   interface Props {
     selectedTag?: string | null
   }
   
   interface Emits {
     (e: 'select', tag: string | null): void
   }
   
   const props = defineProps<Props>()
   const emit = defineEmits<Emits>()
   
   const tagStore = useTagStore()
   
   const tags = computed(() => tagStore.tags)
   
   const selectTag = (tag: string | null) => {
     emit('select', tag)
   }
   </script>
   
   <style scoped>
   .tag-cloud {
     padding: 16px;
     background: #fff;
     border-radius: 8px;
   }
   
   .tag-cloud-title {
     margin: 0 0 12px 0;
     font-size: 16px;
     font-weight: 500;
   }
   
   .tag-list {
     display: flex;
     flex-wrap: wrap;
     gap: 8px;
   }
   
   .tag-item {
     cursor: pointer;
     transition: all 0.3s ease;
   }
   
   .tag-item:hover {
     opacity: 0.8;
   }
   
   .tag-active {
     border: 2px solid #0070f3;
   }
   </style>
   ```

**交付标准**：
- 标签展示美观
- 点击筛选功能正常
- 支持取消筛选

**预计时间**：0.5 天

---

#### 4.6.4 SearchBar 组件

**任务描述**：开发搜索框组件

**具体步骤**：
1. 创建 `src/components/SearchBar.vue`
   ```vue
   <template>
     <div class="search-bar">
       <el-input
         v-model="searchKeyword"
         placeholder="搜索 Ticket 标题..."
         clearable
         @input="handleSearch"
       >
         <template #prefix>
           <el-icon><Search /></el-icon>
         </template>
       </el-input>
     </div>
   </template>
   
   <script setup lang="ts">
   import { ref } from 'vue'
   import { Search } from '@element-plus/icons-vue'
   
   interface Emits {
     (e: 'search', keyword: string): void
   }
   
   const emit = defineEmits<Emits>()
   
   const searchKeyword = ref('')
   
   const handleSearch = () => {
     emit('search', searchKeyword.value)
   }
   </script>
   
   <style scoped>
   .search-bar {
     width: 100%;
     max-width: 400px;
   }
   </style>
   ```

**交付标准**：
- 搜索功能正常
- 支持清空搜索

**预计时间**：0.5 天

---

### 4.7 页面开发

#### 4.7.1 Home 页面

**任务描述**：开发主页，整合所有组件

**具体步骤**：
1. 创建 `src/views/Home.vue`
   ```vue
   <template>
     <div class="home">
       <el-container>
         <el-header class="header">
           <h1 class="title">Ticket 管理工具</h1>
           <el-button type="primary" @click="showCreateDialog">
             <el-icon><Plus /></el-icon>
             创建 Ticket
           </el-button>
         </el-header>
         
         <el-container>
           <el-aside width="250px">
             <TagCloud :selected-tag="selectedTag" @select="handleTagSelect" />
           </el-aside>
           
           <el-main>
             <div class="main-content">
               <div class="toolbar">
                 <SearchBar @search="handleSearch" />
                 <el-tag v-if="selectedTag" closable @close="handleTagSelect(null)">
                   标签: {{ selectedTag }}
                 </el-tag>
               </div>
               
               <el-divider />
               
               <div v-loading="loading" class="ticket-container">
                 <TicketList />
               </div>
             </div>
           </el-main>
         </el-container>
       </el-container>
       
       <TicketForm
         v-model="showDialog"
         @success="handleFormSuccess"
       />
     </div>
   </template>
   
   <script setup lang="ts">
   import { ref, onMounted } from 'vue'
   import { Plus } from '@element-plus/icons-vue'
   import { useTicketStore } from '@/stores/ticket'
   import { useTagStore } from '@/stores/tag'
   import TicketList from '@/components/TicketList.vue'
   import TicketForm from '@/components/TicketForm.vue'
   import TagCloud from '@/components/TagCloud.vue'
   import SearchBar from '@/components/SearchBar.vue'
   
   const ticketStore = useTicketStore()
   const tagStore = useTagStore()
   
   const showDialog = ref(false)
   const selectedTag = ref<string | null>(null)
   const searchKeyword = ref('')
   
   const loading = computed(() => ticketStore.loading)
   
   onMounted(async () => {
     await Promise.all([
       ticketStore.fetchTickets(),
       tagStore.fetchTags(),
     ])
   })
   
   const showCreateDialog = () => {
     showDialog.value = true
   }
   
   const handleFormSuccess = async () => {
     await Promise.all([
       ticketStore.fetchTickets({ tag: selectedTag.value || undefined, search: searchKeyword.value || undefined }),
       tagStore.fetchTags(),
     ])
   }
   
   const handleTagSelect = async (tag: string | null) => {
     selectedTag.value = tag
     await ticketStore.fetchTickets({
       tag: tag || undefined,
       search: searchKeyword.value || undefined,
     })
   }
   
   const handleSearch = async (keyword: string) => {
     searchKeyword.value = keyword
     await ticketStore.fetchTickets({
       tag: selectedTag.value || undefined,
       search: keyword || undefined,
     })
   }
   </script>
   
   <style scoped>
   .home {
     min-height: 100vh;
     background: #f5f5f5;
   }
   
   .header {
     display: flex;
     justify-content: space-between;
     align-items: center;
     padding: 0 24px;
     background: #fff;
     box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
   }
   
   .title {
     margin: 0;
     font-size: 24px;
     font-weight: 500;
   }
   
   .main-content {
     padding: 24px;
   }
   
   .toolbar {
     display: flex;
     gap: 16px;
     align-items: center;
   }
   
   .ticket-container {
     min-height: 400px;
   }
   </style>
   ```

**交付标准**：
- 页面布局合理
- 所有组件正常工作
- 交互流畅

**预计时间**：1 天

---

## 5. 测试计划

### 5.1 后端测试

#### 5.1.1 单元测试

**任务描述**：编写后端单元测试

**具体步骤**：
1. 安装测试依赖
   ```bash
   pip install pytest pytest-asyncio httpx pytest-cov pytest-mock factory-boy faker
   ```

2. 创建测试配置文件 `tests/conftest.py`
   ```python
   import pytest
   from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
   from httpx import AsyncClient
   from app.main import app
   from app.database import get_db, Base
   from app.models.ticket import Ticket, Tag, TicketTag
   
   TEST_DATABASE_URL = "postgresql+asyncpg://test:test@localhost/test_db"
   
   test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
   TestSessionLocal = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)
   
   @pytest.fixture
   async def db_session():
       async with test_engine.begin() as conn:
           await conn.run_sync(Base.metadata.create_all)
       async with TestSessionLocal() as session:
           yield session
       async with test_engine.begin() as conn:
           await conn.run_sync(Base.metadata.drop_all)
   
   @pytest.fixture
   async def client(db_session):
       async def override_get_db():
           yield db_session
       app.dependency_overrides[get_db] = override_get_db
       async with AsyncClient(app=app, base_url="http://test") as ac:
           yield ac
       app.dependency_overrides.clear()
   
   @pytest.fixture
   def sample_ticket_data():
       return {
           "title": "测试 Ticket",
           "description": "这是一个测试 Ticket",
           "tags": ["测试"]
       }
   
   @pytest.fixture
   def sample_tag_data():
       return {
           "name": "测试标签",
           "color": "#0070f3"
       }
   ```

3. 创建 Ticket CRUD 测试文件 `tests/test_crud_ticket.py`
   ```python
   import pytest
   from uuid import uuid4
   from app.crud.ticket import (
       get_ticket, get_tickets, create_ticket, 
       update_ticket, delete_ticket
   )
   from app.schemas.ticket import TicketCreate, TicketUpdate
   
   @pytest.mark.asyncio
   async def test_create_ticket_success(db_session):
       ticket_data = TicketCreate(
           title="测试 Ticket",
           description="这是一个测试 Ticket"
       )
       ticket = await create_ticket(db_session, ticket_data)
       assert ticket.id is not None
       assert ticket.title == "测试 Ticket"
       assert ticket.is_completed is False
   
   @pytest.mark.asyncio
   async def test_create_ticket_with_tags(db_session):
       ticket_data = TicketCreate(
           title="带标签的 Ticket",
           description="测试标签关联",
           tags=["标签1", "标签2"]
       )
       ticket = await create_ticket(db_session, ticket_data)
       assert len(ticket.tags) == 2
   
   @pytest.mark.asyncio
   async def test_get_ticket_by_id(db_session, sample_ticket_data):
       created_ticket = await create_ticket(db_session, TicketCreate(**sample_ticket_data))
       fetched_ticket = await get_ticket(db_session, created_ticket.id)
       assert fetched_ticket is not None
       assert fetched_ticket.id == created_ticket.id
   
   @pytest.mark.asyncio
   async def test_get_ticket_not_found(db_session):
       ticket = await get_ticket(db_session, uuid4())
       assert ticket is None
   
   @pytest.mark.asyncio
   async def test_get_tickets_with_pagination(db_session):
       for i in range(5):
           await create_ticket(db_session, TicketCreate(title=f"Ticket {i}"))
       tickets, total = await get_tickets(db_session, skip=0, limit=3)
       assert len(tickets) == 3
       assert total == 5
   
   @pytest.mark.asyncio
   async def test_get_tickets_with_search(db_session):
       await create_ticket(db_session, TicketCreate(title="Python 学习"))
       await create_ticket(db_session, TicketCreate(title="Vue 开发"))
       tickets, total = await get_tickets(db_session, search="Python")
       assert len(tickets) == 1
       assert tickets[0].title == "Python 学习"
   
   @pytest.mark.asyncio
   async def test_update_ticket(db_session):
       created_ticket = await create_ticket(
           db_session, 
           TicketCreate(title="原标题")
       )
       updated_ticket = await update_ticket(
           db_session, 
           created_ticket.id, 
           TicketUpdate(title="更新后的标题", is_completed=True)
       )
       assert updated_ticket.title == "更新后的标题"
       assert updated_ticket.is_completed is True
   
   @pytest.mark.asyncio
   async def test_delete_ticket(db_session):
       created_ticket = await create_ticket(
           db_session, 
           TicketCreate(title="待删除的 Ticket")
       )
       success = await delete_ticket(db_session, created_ticket.id)
       assert success is True
       ticket = await get_ticket(db_session, created_ticket.id)
       assert ticket is None
   ```

4. 创建 Tag CRUD 测试文件 `tests/test_crud_tag.py`
   ```python
   import pytest
   from uuid import uuid4
   from app.crud.tag import get_tag, get_tags, get_tag_by_name, create_tag, delete_tag
   from app.schemas.tag import TagCreate
   
   @pytest.mark.asyncio
   async def test_create_tag_success(db_session):
       tag_data = TagCreate(name="测试标签", color="#0070f3")
       tag = await create_tag(db_session, tag_data)
       assert tag.id is not None
       assert tag.name == "测试标签"
       assert tag.color == "#0070f3"
   
   @pytest.mark.asyncio
   async def test_create_tag_default_color(db_session):
       tag_data = TagCreate(name="默认颜色标签")
       tag = await create_tag(db_session, tag_data)
       assert tag.color == "#0070f3"
   
   @pytest.mark.asyncio
   async def test_get_tag_by_name(db_session):
       tag_data = TagCreate(name="唯一标签")
       await create_tag(db_session, tag_data)
       tag = await get_tag_by_name(db_session, "唯一标签")
       assert tag is not None
       assert tag.name == "唯一标签"
   
   @pytest.mark.asyncio
   async def test_get_tag_by_name_not_found(db_session):
       tag = await get_tag_by_name(db_session, "不存在的标签")
       assert tag is None
   
   @pytest.mark.asyncio
   async def test_get_tags_pagination(db_session):
       for i in range(5):
           await create_tag(db_session, TagCreate(name=f"标签{i}"))
       tags = await get_tags(db_session, skip=0, limit=3)
       assert len(tags) == 3
   
   @pytest.mark.asyncio
   async def test_delete_tag(db_session):
       created_tag = await create_tag(db_session, TagCreate(name="待删除标签"))
       success = await delete_tag(db_session, created_tag.id)
       assert success is True
       tag = await get_tag(db_session, created_tag.id)
       assert tag is None
   ```

5. 创建 Pydantic Schema 测试文件 `tests/test_schemas.py`
   ```python
   import pytest
   from pydantic import ValidationError
   from app.schemas.ticket import TicketCreate, TicketUpdate
   from app.schemas.tag import TagCreate
   
   def test_ticket_create_valid():
       ticket = TicketCreate(
           title="有效标题",
           description="有效描述",
           tags=["标签1", "标签2"]
       )
       assert ticket.title == "有效标题"
   
   def test_ticket_create_title_too_short():
       with pytest.raises(ValidationError):
           TicketCreate(title="")
   
   def test_ticket_create_title_too_long():
       with pytest.raises(ValidationError):
           TicketCreate(title="a" * 256)
   
   def test_ticket_update_partial():
       ticket = TicketUpdate(title="仅更新标题")
       assert ticket.title == "仅更新标题"
       assert ticket.is_completed is None
   
   def test_tag_create_valid():
       tag = TagCreate(name="有效标签", color="#ff0000")
       assert tag.name == "有效标签"
       assert tag.color == "#ff0000"
   
   def test_tag_create_invalid_color():
       with pytest.raises(ValidationError):
           TagCreate(name="标签", color="invalid")
   
   def test_tag_create_name_too_long():
       with pytest.raises(ValidationError):
           TagCreate(name="a" * 51)
   ```

6. 创建工具函数测试文件 `tests/test_utils.py`
   ```python
   import pytest
   from app.utils.response import success_response, error_response
   
   def test_success_response_with_data():
       response = success_response(data={"id": "123"}, message="成功")
       assert response["code"] == 200
       assert response["message"] == "成功"
       assert response["data"]["id"] == "123"
   
   def test_success_response_default():
       response = success_response()
       assert response["code"] == 200
       assert response["message"] == "success"
   
   def test_error_response():
       response = error_response(message="错误信息", code=400)
       assert response["code"] == 400
       assert response["message"] == "错误信息"
   ```

**交付标准**：
- 核心业务逻辑测试覆盖率 ≥ 95%
- 所有测试通过
- 测试覆盖率报告生成

**预计时间**：2 天

---

#### 5.1.2 集成测试

**任务描述**：编写后端集成测试，测试 API 端点的完整流程

**具体步骤**：

1. 创建测试数据库配置 `tests/conftest.py`
   ```python
   import pytest
   from httpx import AsyncClient, ASGITransport
   from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
   from sqlalchemy.pool import StaticPool
   from app.main import app
   from app.database import get_db, Base
   from app.models.ticket import Ticket, TicketTag
   from app.models.tag import Tag
   
   # 使用内存 SQLite 数据库进行集成测试
   TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
   
   test_engine = create_async_engine(
       TEST_DATABASE_URL,
       connect_args={"check_same_thread": False},
       poolclass=StaticPool,
   )
   
   TestSessionLocal = async_sessionmaker(
       test_engine, class_=AsyncSession, expire_on_commit=False
   )
   
   @pytest.fixture(scope="function")
   async def db_session():
       async with test_engine.begin() as conn:
           await conn.run_sync(Base.metadata.create_all)
       
       async with TestSessionLocal() as session:
           yield session
           await session.rollback()
   
   @pytest.fixture(scope="function")
   async def client(db_session: AsyncSession):
       async def override_get_db():
           yield db_session
       
       app.dependency_overrides[get_db] = override_get_db
       
       async with AsyncClient(
           transport=ASGITransport(app=app),
           base_url="http://test"
       ) as ac:
           yield ac
       
       app.dependency_overrides.clear()
   
   @pytest.fixture
   async def sample_ticket(db_session: AsyncSession):
       ticket = Ticket(
           title="测试 Ticket",
           description="测试描述",
           is_completed=False
       )
       db_session.add(ticket)
       await db_session.commit()
       await db_session.refresh(ticket)
       return ticket
   
   @pytest.fixture
   async def sample_tag(db_session: AsyncSession):
       tag = Tag(name="测试标签", color="#0070f3")
       db_session.add(tag)
       await db_session.commit()
       await db_session.refresh(tag)
       return tag
   ```

2. 创建 Ticket API 集成测试 `tests/test_api_tickets.py`
   ```python
   import pytest
   from httpx import AsyncClient
   
   
   @pytest.mark.asyncio
   async def test_create_ticket_success(client: AsyncClient):
       response = await client.post(
           "/api/v1/addTickets",
           json={
               "title": "新 Ticket",
               "description": "新 Ticket 描述"
           }
       )
       assert response.status_code == 200
       data = response.json()
       assert data["code"] == 200
       assert "data" in data
       assert data["message"] == "Ticket 创建成功"
   
   
   @pytest.mark.asyncio
   async def test_create_ticket_with_tags(client: AsyncClient, sample_tag):
       response = await client.post(
           "/api/v1/addTickets",
           json={
               "title": "带标签的 Ticket",
               "tags": [sample_tag.name]
           }
       )
       assert response.status_code == 200
       data = response.json()
       assert data["code"] == 200
   
   
   @pytest.mark.asyncio
   async def test_create_ticket_empty_title(client: AsyncClient):
       response = await client.post(
           "/api/v1/addTickets",
           json={"title": ""}
       )
       assert response.status_code == 422
   
   
   @pytest.mark.asyncio
   async def test_get_tickets_list(client: AsyncClient, sample_ticket):
       response = await client.get("/api/v1/listTickets")
       assert response.status_code == 200
       data = response.json()
       assert data["code"] == 200
       assert "tickets" in data["data"]
       assert len(data["data"]["tickets"]) >= 1
   
   
   @pytest.mark.asyncio
   async def test_get_tickets_with_pagination(client: AsyncClient, db_session):
       from app.crud.ticket import create_ticket
       from app.schemas.ticket import TicketCreate
       
       for i in range(5):
           await create_ticket(db_session, TicketCreate(title=f"Ticket {i}"))
       
       response = await client.get("/api/v1/listTickets?skip=0&limit=3")
       assert response.status_code == 200
       data = response.json()
       assert len(data["data"]["tickets"]) == 3
       assert data["data"]["total"] >= 5
   
   
   @pytest.mark.asyncio
   async def test_get_tickets_with_search(client: AsyncClient, db_session):
       from app.crud.ticket import create_ticket
       from app.schemas.ticket import TicketCreate
       
       await create_ticket(db_session, TicketCreate(title="Python 学习"))
       await create_ticket(db_session, TicketCreate(title="Vue 开发"))
       
       response = await client.get("/api/v1/listTickets?search=Python")
       assert response.status_code == 200
       data = response.json()
       assert len(data["data"]["tickets"]) == 1
       assert data["data"]["tickets"][0]["title"] == "Python 学习"
   
   
   @pytest.mark.asyncio
   async def test_get_ticket_by_id(client: AsyncClient, sample_ticket):
       response = await client.get(f"/api/v1/tickets/{sample_ticket.id}")
       assert response.status_code == 200
       data = response.json()
       assert data["code"] == 200
       assert data["data"]["id"] == str(sample_ticket.id)
       assert data["data"]["title"] == sample_ticket.title
   
   
   @pytest.mark.asyncio
   async def test_get_ticket_not_found(client: AsyncClient):
       from uuid import uuid4
       response = await client.get(f"/api/v1/tickets/{uuid4()}")
       assert response.status_code == 404
   
   
   @pytest.mark.asyncio
   async def test_update_ticket(client: AsyncClient, sample_ticket):
       response = await client.put(
           f"/api/v1/updateTickets/{sample_ticket.id}",
           json={
               "title": "更新后的标题",
               "description": "更新后的描述",
               "is_completed": True
           }
       )
       assert response.status_code == 200
       data = response.json()
       assert data["code"] == 200
       assert data["message"] == "Ticket 更新成功"
   
   
   @pytest.mark.asyncio
   async def test_update_ticket_not_found(client: AsyncClient):
       from uuid import uuid4
       response = await client.put(
           f"/api/v1/updateTickets/{uuid4()}",
           json={"title": "更新标题"}
       )
       assert response.status_code == 404
   
   
   @pytest.mark.asyncio
   async def test_delete_ticket(client: AsyncClient, sample_ticket):
       response = await client.delete(f"/api/v1/tickets/{sample_ticket.id}")
       assert response.status_code == 200
       data = response.json()
       assert data["code"] == 200
       assert data["message"] == "Ticket 删除成功"
   
   
   @pytest.mark.asyncio
   async def test_delete_ticket_not_found(client: AsyncClient):
       from uuid import uuid4
       response = await client.delete(f"/api/v1/tickets/{uuid4()}")
       assert response.status_code == 404
   ```

3. 创建 Tag API 集成测试 `tests/test_api_tags.py`
   ```python
   import pytest
   from httpx import AsyncClient
   
   
   @pytest.mark.asyncio
   async def test_create_tag_success(client: AsyncClient):
       response = await client.post(
           "/api/v1/addTags",
           json={"name": "新标签", "color": "#ff0000"}
       )
       assert response.status_code == 200
       data = response.json()
       assert data["code"] == 200
       assert "data" in data
       assert data["message"] == "标签创建成功"
   
   
   @pytest.mark.asyncio
   async def test_create_tag_duplicate(client: AsyncClient, sample_tag):
       response = await client.post(
           "/api/v1/addTags",
           json={"name": sample_tag.name, "color": "#ff0000"}
       )
       assert response.status_code == 409
   
   
   @pytest.mark.asyncio
   async def test_create_tag_invalid_color(client: AsyncClient):
       response = await client.post(
           "/api/v1/addTags",
           json={"name": "测试标签", "color": "invalid"}
       )
       assert response.status_code == 422
   
   
   @pytest.mark.asyncio
   async def test_get_tags_list(client: AsyncClient, sample_tag):
       response = await client.get("/api/v1/listTags")
       assert response.status_code == 200
       data = response.json()
       assert data["code"] == 200
       assert "tags" in data["data"]
       assert len(data["data"]["tags"]) >= 1
   
   
   @pytest.mark.asyncio
   async def test_add_ticket_tags(client: AsyncClient, sample_ticket, sample_tag):
       response = await client.post(
           f"/api/v1/addTicketTags/{sample_ticket.id}",
           json=[str(sample_tag.id)]
       )
       assert response.status_code == 200
       data = response.json()
       assert data["code"] == 200
       assert data["message"] == "标签添加成功"
   
   
   @pytest.mark.asyncio
   async def test_add_ticket_tags_ticket_not_found(client: AsyncClient, sample_tag):
       from uuid import uuid4
       response = await client.post(
           f"/api/v1/addTicketTags/{uuid4()}",
           json=[str(sample_tag.id)]
       )
       assert response.status_code == 404
   
   
   @pytest.mark.asyncio
   async def test_add_ticket_tags_tag_not_found(client: AsyncClient, sample_ticket):
       from uuid import uuid4
       response = await client.post(
           f"/api/v1/addTicketTags/{sample_ticket.id}",
           json=[str(uuid4())]
       )
       assert response.status_code == 404
   
   
   @pytest.mark.asyncio
   async def test_delete_ticket_tag(client: AsyncClient, db_session, sample_ticket, sample_tag):
       from app.models.ticket import TicketTag
       
       ticket_tag = TicketTag(ticket_id=sample_ticket.id, tag_id=sample_tag.id)
       db_session.add(ticket_tag)
       await db_session.commit()
       
       response = await client.delete(
           f"/api/v1/deleteTicketTags/{sample_ticket.id}/{sample_tag.id}"
       )
       assert response.status_code == 200
       data = response.json()
       assert data["code"] == 200
       assert data["message"] == "标签移除成功"
   
   
   @pytest.mark.asyncio
   async def test_delete_ticket_tag_not_found(client: AsyncClient, sample_ticket, sample_tag):
       response = await client.delete(
           f"/api/v1/deleteTicketTags/{sample_ticket.id}/{sample_tag.id}"
       )
       assert response.status_code == 404
   ```

4. 创建数据库事务测试 `tests/test_transactions.py`
   ```python
   import pytest
   from sqlalchemy.ext.asyncio import AsyncSession
   from app.crud.ticket import create_ticket, get_ticket
   from app.schemas.ticket import TicketCreate
   from app.models.ticket import Ticket
   
   
   @pytest.mark.asyncio
   async def test_transaction_rollback_on_error(db_session: AsyncSession):
       """测试事务在错误时回滚"""
       initial_count = await db_session.execute(
           "SELECT COUNT(*) FROM tickets"
       )
       initial_count = initial_count.scalar()
       
       try:
           await create_ticket(
               db_session,
               TicketCreate(title="测试 Ticket")
           )
           await db_session.commit()
           
           # 模拟错误
           await db_session.rollback()
       except Exception:
           pass
       
       final_count = await db_session.execute(
           "SELECT COUNT(*) FROM tickets"
       )
       final_count = final_count.scalar()
       
       # 验证回滚后数据未增加
       assert final_count == initial_count + 1
   
   
   @pytest.mark.asyncio
   async def test_transaction_commit_success(db_session: AsyncSession):
       """测试事务成功提交"""
       ticket = await create_ticket(
           db_session,
           TicketCreate(title="提交测试 Ticket")
       )
       await db_session.commit()
       await db_session.refresh(ticket)
       
       retrieved_ticket = await get_ticket(db_session, ticket.id)
       assert retrieved_ticket is not None
       assert retrieved_ticket.title == "提交测试 Ticket"
   
   
   @pytest.mark.asyncio
   async def test_cascade_delete(db_session: AsyncSession):
       """测试级联删除"""
       from app.crud.tag import create_tag
       from app.schemas.tag import TagCreate
       from app.models.ticket import TicketTag
       
       tag = await create_tag(db_session, TagCreate(name="级联测试标签"))
       ticket = await create_ticket(
           db_session,
           TicketCreate(title="级联测试 Ticket")
       )
       
       ticket_tag = TicketTag(ticket_id=ticket.id, tag_id=tag.id)
       db_session.add(ticket_tag)
       await db_session.commit()
       
       # 删除 ticket
       await db_session.delete(ticket)
       await db_session.commit()
       
       # 验证关联也被删除
       result = await db_session.execute(
           "SELECT COUNT(*) FROM ticket_tags WHERE ticket_id = :ticket_id",
           {"ticket_id": ticket.id}
       )
       count = result.scalar()
       assert count == 0
   ```

5. 创建性能测试 `tests/test_performance.py`
   ```python
   import pytest
   import time
   from httpx import AsyncClient
   from app.crud.ticket import create_ticket
   from app.schemas.ticket import TicketCreate
   
   
   @pytest.mark.asyncio
   async def test_list_tickets_performance(client: AsyncClient, db_session):
       """测试大量数据查询性能"""
       # 创建 100 条测试数据
       for i in range(100):
           await create_ticket(
               db_session,
               TicketCreate(title=f"性能测试 Ticket {i}")
           )
       await db_session.commit()
       
       # 测试查询性能
       start_time = time.time()
       response = await client.get("/api/v1/listTickets?limit=100")
       end_time = time.time()
       
       assert response.status_code == 200
       # 响应时间应小于 500ms
       assert (end_time - start_time) < 0.5
   
   
   @pytest.mark.asyncio
   async def test_search_performance(client: AsyncClient, db_session):
       """测试搜索性能"""
       # 创建包含搜索关键词的数据
       for i in range(50):
           await create_ticket(
               db_session,
               TicketCreate(title=f"Python 学习 {i}")
           )
       await db_session.commit()
       
       start_time = time.time()
       response = await client.get("/api/v1/listTickets?search=Python")
       end_time = time.time()
       
       assert response.status_code == 200
       # 搜索响应时间应小于 300ms
       assert (end_time - start_time) < 0.3
   ```

**交付标准**：
- 所有 API 集成测试通过
- 数据库事务测试覆盖正常和异常场景
- 性能测试满足响应时间要求
- 测试覆盖率 ≥ 90%

**预计时间**：2 天

---

### 5.2 前端测试

#### 5.2.1 组件测试

**任务描述**：编写前端组件测试

**具体步骤**：
1. 安装测试依赖
   ```bash
   pnpm install -D vitest @vue/test-utils jsdom @vitest/coverage-v8 happy-dom
   ```

2. 创建测试配置文件 `vitest.config.ts`
   ```typescript
   import { defineConfig } from 'vitest/config'
   import vue from '@vitejs/plugin-vue'
   import { fileURLToPath } from 'node:url'
   
   export default defineConfig({
     plugins: [vue()],
     test: {
       globals: true,
       environment: 'happy-dom',
       coverage: {
         provider: 'v8',
         reporter: ['text', 'json', 'html'],
         exclude: ['node_modules/', 'tests/']
       }
     },
     resolve: {
       alias: {
         '@': fileURLToPath(new URL('./src', import.meta.url))
       }
     }
   })
   ```

3. 创建测试工具文件 `tests/setup.ts`
   ```typescript
   import { vi } from 'vitest'
   
   vi.mock('@/api/tickets', () => ({
     getTickets: vi.fn(),
     createTicket: vi.fn(),
     updateTicket: vi.fn(),
     deleteTicket: vi.fn()
   }))
   
   vi.mock('@/api/tags', () => ({
     getTags: vi.fn(),
     createTag: vi.fn(),
     addTicketTags: vi.fn(),
     deleteTicketTag: vi.fn()
   }))
   ```

4. 创建 TicketList 组件测试文件 `tests/components/TicketList.spec.ts`
   ```typescript
   import { describe, it, expect, vi } from 'vitest'
   import { mount } from '@vue/test-utils'
   import TicketList from '@/components/TicketList.vue'
   import type { Ticket } from '@/types/ticket'
   
   const mockTickets: Ticket[] = [
     {
       id: '1',
       title: '测试 Ticket',
       description: '测试描述',
       is_completed: false,
       created_at: '2025-01-01T00:00:00Z',
       updated_at: '2025-01-01T00:00:00Z',
       tags: [{ id: 'tag1', name: '测试标签', color: '#0070f3', created_at: '2025-01-01T00:00:00Z' }]
     },
     {
       id: '2',
       title: '已完成 Ticket',
       description: '已完成描述',
       is_completed: true,
       created_at: '2025-01-01T00:00:00Z',
       updated_at: '2025-01-01T00:00:00Z',
       tags: []
     }
   ]
   
   describe('TicketList', () => {
     it('正确渲染 tickets 列表', () => {
       const wrapper = mount(TicketList, {
         props: { tickets: mockTickets }
       })
       expect(wrapper.text()).toContain('测试 Ticket')
       expect(wrapper.text()).toContain('已完成 Ticket')
     })
     
     it('渲染空列表时显示提示信息', () => {
       const wrapper = mount(TicketList, {
         props: { tickets: [] }
       })
       expect(wrapper.text()).toContain('暂无')
     })
     
     it('点击 ticket 触发 select 事件', async () => {
       const wrapper = mount(TicketList, {
         props: { tickets: mockTickets }
       })
       await wrapper.find('[data-test="ticket-item"]').trigger('click')
       expect(wrapper.emitted('select')).toBeTruthy()
       expect(wrapper.emitted('select')?.[0]).toEqual([mockTickets[0]])
     })
     
     it('正确显示完成状态', () => {
       const wrapper = mount(TicketList, {
         props: { tickets: mockTickets }
       })
       const completedItems = wrapper.findAll('[data-test="completed"]')
       expect(completedItems.length).toBe(1)
     })
     
     it('正确显示标签', () => {
       const wrapper = mount(TicketList, {
         props: { tickets: mockTickets }
       })
       expect(wrapper.text()).toContain('测试标签')
     })
   })
   ```

5. 创建 TicketForm 组件测试文件 `tests/components/TicketForm.spec.ts`
   ```typescript
   import { describe, it, expect, vi } from 'vitest'
   import { mount } from '@vue/test-utils'
   import TicketForm from '@/components/TicketForm.vue'
   import ElementPlus from 'element-plus'
   
   describe('TicketForm', () => {
     it('正确渲染表单字段', () => {
       const wrapper = mount(TicketForm, {
         global: { plugins: [ElementPlus] }
       })
       expect(wrapper.find('input[type="text"]').exists()).toBe(true)
       expect(wrapper.find('textarea').exists()).toBe(true)
     })
     
     it('表单验证 - 标题必填', async () => {
       const wrapper = mount(TicketForm, {
         global: { plugins: [ElementPlus] }
       })
       await wrapper.find('form').trigger('submit')
       expect(wrapper.vm.hasError).toBe(true)
     })
     
     it('提交表单时触发 submit 事件', async () => {
       const wrapper = mount(TicketForm, {
         global: { plugins: [ElementPlus] }
       })
       const titleInput = wrapper.find('input[type="text"]')
       await titleInput.setValue('测试标题')
       await wrapper.find('form').trigger('submit')
       expect(wrapper.emitted('submit')).toBeTruthy()
     })
     
     it('重置表单时触发 reset 事件', async () => {
       const wrapper = mount(TicketForm, {
         global: { plugins: [ElementPlus] }
       })
       await wrapper.find('[data-test="reset-btn"]').trigger('click')
       expect(wrapper.emitted('reset')).toBeTruthy()
     })
     
     it('编辑模式正确填充数据', () => {
       const ticket = {
         id: '1',
         title: '编辑标题',
         description: '编辑描述',
         is_completed: false,
         created_at: '2025-01-01T00:00:00Z',
         updated_at: '2025-01-01T00:00:00Z',
         tags: []
       }
       const wrapper = mount(TicketForm, {
         props: { ticket, isEdit: true },
         global: { plugins: [ElementPlus] }
       })
       expect(wrapper.find('input[type="text"]').element.value).toBe('编辑标题')
     })
   })
   ```

6. 创建 TagCloud 组件测试文件 `tests/components/TagCloud.spec.ts`
   ```typescript
   import { describe, it, expect, vi } from 'vitest'
   import { mount } from '@vue/test-utils'
   import TagCloud from '@/components/TagCloud.vue'
   import type { Tag } from '@/types/tag'
   
   const mockTags: Tag[] = [
     { id: '1', name: 'Python', color: '#0070f3', created_at: '2025-01-01T00:00:00Z' },
     { id: '2', name: 'Vue', color: '#42b883', created_at: '2025-01-01T00:00:00Z' },
     { id: '3', name: 'TypeScript', color: '#3178c6', created_at: '2025-01-01T00:00:00Z' }
   ]
   
   describe('TagCloud', () => {
     it('正确渲染标签列表', () => {
       const wrapper = mount(TagCloud, {
         props: { tags: mockTags }
       })
       expect(wrapper.text()).toContain('Python')
       expect(wrapper.text()).toContain('Vue')
       expect(wrapper.text()).toContain('TypeScript')
     })
     
     it('正确应用标签颜色', () => {
       const wrapper = mount(TagCloud, {
         props: { tags: mockTags }
       })
       const tagElements = wrapper.findAll('[data-test="tag"]')
       expect(tagElements[0].attributes('style')).toContain('#0070f3')
       expect(tagElements[1].attributes('style')).toContain('#42b883')
     })
     
     it('点击标签触发 select 事件', async () => {
       const wrapper = mount(TagCloud, {
         props: { tags: mockTags }
       })
       await wrapper.find('[data-test="tag"]').trigger('click')
       expect(wrapper.emitted('select')).toBeTruthy()
       expect(wrapper.emitted('select')?.[0]).toEqual([mockTags[0]])
     })
     
     it '选中标签高亮显示', () => {
       const wrapper = mount(TagCloud, {
         props: { tags: mockTags, selectedTagId: '1' }
       })
       const selectedTag = wrapper.find('[data-test="tag"][data-selected="true"]')
       expect(selectedTag.exists()).toBe(true)
     })
     
     it('渲染空标签列表', () => {
       const wrapper = mount(TagCloud, {
         props: { tags: [] }
       })
       expect(wrapper.text()).toContain('暂无标签')
     })
   })
   ```

7. 创建 SearchBar 组件测试文件 `tests/components/SearchBar.spec.ts`
   ```typescript
   import { describe, it, expect, vi } from 'vitest'
   import { mount } from '@vue/test-utils'
   import SearchBar from '@/components/SearchBar.vue'
   
   describe('SearchBar', () => {
     it('正确渲染搜索输入框', () => {
       const wrapper = mount(SearchBar)
       expect(wrapper.find('input[type="text"]').exists()).toBe(true)
     })
     
     it('输入内容时触发 search 事件', async () => {
       const wrapper = mount(SearchBar)
       const input = wrapper.find('input[type="text"]')
       await input.setValue('测试搜索')
       await input.trigger('input')
       expect(wrapper.emitted('search')).toBeTruthy()
       expect(wrapper.emitted('search')?.[0]).toEqual(['测试搜索'])
     })
     
     it '防抖功能正常工作', async () => {
       const wrapper = mount(SearchBar, { props: { debounce: 300 } })
       const input = wrapper.find('input[type="text"]')
       await input.setValue('测试')
       await input.trigger('input')
       await new Promise(resolve => setTimeout(resolve, 200))
       expect(wrapper.emitted('search')).toBeFalsy()
       await new Promise(resolve => setTimeout(resolve, 200))
       expect(wrapper.emitted('search')).toBeTruthy()
     })
     
     it('清空按钮清除输入', async () => {
       const wrapper = mount(SearchBar)
       const input = wrapper.find('input[type="text"]')
       await input.setValue('测试内容')
       await wrapper.find('[data-test="clear-btn"]').trigger('click')
       expect(input.element.value).toBe('')
     })
   })
   ```

**交付标准**：
- 核心组件测试覆盖率 ≥ 95%
- 所有测试通过

**预计时间**：2 天

---

#### 5.2.2 工具函数测试

**任务描述**：编写前端工具函数测试

**具体步骤**：
1. 创建日期格式化工具测试 `tests/utils/formatDate.spec.ts`
   ```typescript
   import { describe, it, expect } from 'vitest'
   import { formatDate } from '@/utils/formatDate'
   
   describe('formatDate', () => {
     it('正确格式化日期字符串', () => {
       const result = formatDate('2025-01-01T12:00:00Z')
       expect(result).toMatch(/2025/)
       expect(result).toMatch(/01/)
     })
     
     it('处理空值返回默认字符串', () => {
       const result = formatDate('')
       expect(result).toBe('--')
     })
     
     it('处理无效日期返回默认字符串', () => {
       const result = formatDate('invalid-date')
       expect(result).toBe('--')
     })
   })
   ```

2. 创建请求工具测试 `tests/utils/request.spec.ts`
   ```typescript
   import { describe, it, expect, vi, beforeEach } from 'vitest'
   import { request } from '@/utils/request'
   
   describe('request', () => {
     beforeEach(() => {
       vi.clearAllMocks()
     })
     
     it('成功请求返回数据', async () => {
       const mockData = { id: '1', title: '测试' }
       global.fetch = vi.fn().mockResolvedValue({
         ok: true,
         json: async () => mockData
       })
       const result = await request('/api/test')
       expect(result).toEqual(mockData)
     })
     
     it('请求失败抛出错误', async () => {
       global.fetch = vi.fn().mockResolvedValue({
         ok: false,
         status: 404
       })
       await expect(request('/api/test')).rejects.toThrow()
     })
     
     it('正确添加请求头', async () => {
       global.fetch = vi.fn().mockResolvedValue({
         ok: true,
         json: async () => ({})
       })
       await request('/api/test', { headers: { 'Custom-Header': 'value' } })
       expect(fetch).toHaveBeenCalledWith(
         expect.any(String),
         expect.objectContaining({
           headers: expect.objectContaining({
             'Custom-Header': 'value'
           })
         })
       )
     })
   })
   ```

3. 创建本地存储工具测试 `tests/utils/storage.spec.ts`
   ```typescript
   import { describe, it, expect, beforeEach, afterEach } from 'vitest'
   import { storage } from '@/utils/storage'
   
   describe('storage', () => {
     beforeEach(() => {
       localStorage.clear()
     })
     
     afterEach(() => {
       localStorage.clear()
     })
     
     it('正确设置和获取值', () => {
       storage.set('test-key', 'test-value')
       expect(storage.get('test-key')).toBe('test-value')
     })
     
     it('获取不存在的键返回 null', () => {
       expect(storage.get('non-existent')).toBeNull()
     })
     
     it('正确删除键', () => {
       storage.set('test-key', 'test-value')
       storage.remove('test-key')
       expect(storage.get('test-key')).toBeNull()
     })
     
     it('正确清空所有数据', () => {
       storage.set('key1', 'value1')
       storage.set('key2', 'value2')
       storage.clear()
       expect(storage.get('key1')).toBeNull()
       expect(storage.get('key2')).toBeNull()
     })
     
     it('正确处理对象数据', () => {
       const obj = { name: 'test', count: 123 }
       storage.set('obj-key', obj)
       expect(storage.get('obj-key')).toEqual(obj)
     })
   })
   ```

**交付标准**：
- 工具函数测试覆盖率 ≥ 95%
- 所有测试通过

**预计时间**：1 天

---

#### 5.2.3 状态管理测试

**任务描述**：编写 Pinia 状态管理测试

**具体步骤**：
1. 创建 Ticket Store 测试 `tests/stores/ticket.spec.ts`
   ```typescript
   import { describe, it, expect, beforeEach, vi } from 'vitest'
   import { setActivePinia, createPinia } from 'pinia'
   import { useTicketStore } from '@/stores/ticket'
   import * as ticketApi from '@/api/tickets'
   
   vi.mock('@/api/tickets')
   
   describe('useTicketStore', () => {
     beforeEach(() => {
       setActivePinia(createPinia())
       vi.clearAllMocks()
     })
     
     it('初始化时 tickets 为空数组', () => {
       const store = useTicketStore()
       expect(store.tickets).toEqual([])
       expect(store.loading).toBe(false)
     })
     
     it('成功获取 tickets 列表', async () => {
       const mockTickets = [
         { id: '1', title: '测试1', is_completed: false },
         { id: '2', title: '测试2', is_completed: true }
       ]
       vi.mocked(ticketApi.getTickets).mockResolvedValue(mockTickets)
       
       const store = useTicketStore()
       await store.fetchTickets()
       
       expect(store.tickets).toEqual(mockTickets)
       expect(store.loading).toBe(false)
     })
     
     it '创建 ticket 成功', async () => {
       const newTicket = { title: '新 Ticket', description: '描述' }
       const createdTicket = { id: '1', ...newTicket, is_completed: false }
       vi.mocked(ticketApi.createTicket).mockResolvedValue(createdTicket)
       
       const store = useTicketStore()
       await store.createTicket(newTicket)
       
       expect(store.tickets).toContainEqual(createdTicket)
     })
     
     it('更新 ticket 成功', async () => {
       const mockTicket = { id: '1', title: '原标题', is_completed: false }
       const updatedTicket = { id: '1', title: '新标题', is_completed: true }
       vi.mocked(ticketApi.updateTicket).mockResolvedValue(updatedTicket)
       
       const store = useTicketStore()
       store.tickets = [mockTicket]
       await store.updateTicket('1', { title: '新标题', is_completed: true })
       
       expect(store.tickets[0]).toEqual(updatedTicket)
     })
     
     it('删除 ticket 成功', async () => {
       const mockTickets = [
         { id: '1', title: 'Ticket 1', is_completed: false },
         { id: '2', title: 'Ticket 2', is_completed: false }
       ]
       vi.mocked(ticketApi.deleteTicket).mockResolvedValue(true)
       
       const store = useTicketStore()
       store.tickets = mockTickets
       await store.deleteTicket('1')
       
       expect(store.tickets.length).toBe(1)
       expect(store.tickets[0].id).toBe('2')
     })
   })
   ```

2. 创建 Tag Store 测试 `tests/stores/tag.spec.ts`
   ```typescript
   import { describe, it, expect, beforeEach, vi } from 'vitest'
   import { setActivePinia, createPinia } from 'pinia'
   import { useTagStore } from '@/stores/tag'
   import * as tagApi from '@/api/tags'
   
   vi.mock('@/api/tags')
   
   describe('useTagStore', () => {
     beforeEach(() => {
       setActivePinia(createPinia())
       vi.clearAllMocks()
     })
     
     it('初始化时 tags 为空数组', () => {
       const store = useTagStore()
       expect(store.tags).toEqual([])
       expect(store.selectedTagId).toBe(null)
     })
     
     it('成功获取 tags 列表', async () => {
       const mockTags = [
         { id: '1', name: 'Python', color: '#0070f3' },
         { id: '2', name: 'Vue', color: '#42b883' }
       ]
       vi.mocked(tagApi.getTags).mockResolvedValue(mockTags)
       
       const store = useTagStore()
       await store.fetchTags()
       
       expect(store.tags).toEqual(mockTags)
     })
     
     it('正确设置选中标签', () => {
       const store = useTagStore()
       store.setSelectedTagId('tag-1')
       expect(store.selectedTagId).toBe('tag-1')
     })
     
     it('清除选中标签', () => {
       const store = useTagStore()
       store.setSelectedTagId('tag-1')
       store.clearSelectedTag()
       expect(store.selectedTagId).toBe(null)
     })
     
     it '创建 tag 成功', async () => {
       const newTag = { name: '新标签', color: '#ff0000' }
       const createdTag = { id: '1', ...newTag }
       vi.mocked(tagApi.createTag).mockResolvedValue(createdTag)
       
       const store = useTagStore()
       await store.createTag(newTag)
       
       expect(store.tags).toContainEqual(createdTag)
     })
   })
   ```

**交付标准**：
- 状态管理测试覆盖率 ≥ 95%
- 所有测试通过

**预计时间**：1 天

---

#### 5.2.4 端到端测试

**任务描述**：编写端到端测试，模拟真实用户操作流程

**具体步骤**：

1. 安装 Playwright 依赖
   ```bash
   pnpm install -D @playwright/test
   npx playwright install
   ```

2. 创建 Playwright 配置文件 `playwright.config.ts`
   ```typescript
   import { defineConfig, devices } from '@playwright/test'
   
   export default defineConfig({
     testDir: './e2e',
     fullyParallel: true,
     forbidOnly: !!process.env.CI,
     retries: process.env.CI ? 2 : 0,
     workers: process.env.CI ? 1 : undefined,
     reporter: 'html',
     use: {
       baseURL: 'http://localhost:3000',
       trace: 'on-first-retry',
       screenshot: 'only-on-failure',
     },
     projects: [
       {
         name: 'chromium',
         use: { ...devices['Desktop Chrome'] },
       },
       {
         name: 'firefox',
         use: { ...devices['Desktop Firefox'] },
       },
       {
         name: 'webkit',
         use: { ...devices['Desktop Safari'] },
       },
     ],
     webServer: {
       command: 'npm run dev',
       url: 'http://localhost:3000',
       reuseExistingServer: !process.env.CI,
     },
   })
   ```

3. 创建 Ticket 管理端到端测试 `e2e/ticket-management.spec.ts`
   ```typescript
   import { test, expect } from '@playwright/test'
   
   test.describe('Ticket 管理端到端测试', () => {
     test.beforeEach(async ({ page }) => {
       await page.goto('/')
     })
     
     test('创建新 Ticket', async ({ page }) => {
       // 点击创建按钮
       await page.click('[data-test="create-ticket-btn"]')
       
       // 填写表单
       await page.fill('[data-test="ticket-title-input"]', '测试 Ticket')
       await page.fill('[data-test="ticket-description-input"]', '这是测试描述')
       
       // 选择标签
       await page.click('[data-test="tag-selector"]')
       await page.click('text=Python')
       
       // 提交表单
       await page.click('[data-test="submit-btn"]')
       
       // 验证成功提示
       await expect(page.locator('[data-test="success-message"]')).toBeVisible()
       await expect(page.locator('[data-test="success-message"]')).toContainText('创建成功')
       
       // 验证 Ticket 列表中包含新创建的 Ticket
       await expect(page.locator('text=测试 Ticket')).toBeVisible()
     })
     
     test('查看 Ticket 详情', async ({ page }) => {
       // 点击第一个 Ticket
       await page.click('[data-test="ticket-item"]:first-child')
       
       // 验证详情页面显示
       await expect(page.locator('[data-test="ticket-detail"]')).toBeVisible()
       await expect(page.locator('[data-test="ticket-title"]')).toBeVisible()
       await expect(page.locator('[data-test="ticket-description"]')).toBeVisible()
     })
     
     test('更新 Ticket', async ({ page }) => {
       // 点击第一个 Ticket
       await page.click('[data-test="ticket-item"]:first-child')
       
       // 点击编辑按钮
       await page.click('[data-test="edit-btn"]')
       
       // 修改标题
       await page.fill('[data-test="ticket-title-input"]', '更新后的标题')
       
       // 保存修改
       await page.click('[data-test="save-btn"]')
       
       // 验证成功提示
       await expect(page.locator('[data-test="success-message"]')).toBeVisible()
       
       // 验证标题已更新
       await expect(page.locator('[data-test="ticket-title"]')).toContainText('更新后的标题')
     })
     
     test('标记 Ticket 为完成', async ({ page }) => {
       // 点击第一个 Ticket 的完成复选框
       await page.click('[data-test="ticket-item"]:first-child [data-test="complete-checkbox"]')
       
       // 验证 Ticket 显示为已完成状态
       await expect(page.locator('[data-test="ticket-item"]:first-child [data-test="completed-badge"]')).toBeVisible()
     })
     
     test('删除 Ticket', async ({ page }) => {
       // 点击第一个 Ticket 的删除按钮
       await page.click('[data-test="ticket-item"]:first-child [data-test="delete-btn"]')
       
       // 确认删除
       await page.click('[data-test="confirm-delete-btn"]')
       
       // 验证成功提示
       await expect(page.locator('[data-test="success-message"]')).toBeVisible()
       
       // 验证 Ticket 已从列表中移除
       await expect(page.locator('[data-test="ticket-item"]')).toHaveCount(0)
     })
   })
   ```

4. 创建标签管理端到端测试 `e2e/tag-management.spec.ts`
   ```typescript
   import { test, expect } from '@playwright/test'
   
   test.describe('标签管理端到端测试', () => {
     test.beforeEach(async ({ page }) => {
       await page.goto('/')
     })
     
     test('创建新标签', async ({ page }) => {
       // 打开标签管理面板
       await page.click('[data-test="tag-panel-toggle"]')
       
       // 点击创建标签按钮
       await page.click('[data-test="create-tag-btn"]')
       
       // 填写标签信息
       await page.fill('[data-test="tag-name-input"]', '测试标签')
       await page.fill('[data-test="tag-color-input"]', '#ff0000')
       
       // 提交表单
       await page.click('[data-test="submit-tag-btn"]')
       
       // 验证标签创建成功
       await expect(page.locator('text=测试标签')).toBeVisible()
       await expect(page.locator('[data-test="tag"][data-name="测试标签"]')).toHaveCSS('background-color', 'rgb(255, 0, 0)')
     })
     
     test('使用标签筛选 Ticket', async ({ page }) => {
       // 点击标签云中的某个标签
       await page.click('[data-test="tag"]:first-child')
       
       // 验证只显示包含该标签的 Ticket
       const tickets = await page.locator('[data-test="ticket-item"]').all()
       for (const ticket of tickets) {
         const hasTag = await ticket.locator('[data-test="ticket-tag"]').count()
         expect(hasTag).toBeGreaterThan(0)
       }
     })
     
     test('清除标签筛选', async ({ page }) => {
       // 先选择一个标签
       await page.click('[data-test="tag"]:first-child')
       
       // 点击清除筛选按钮
       await page.click('[data-test="clear-filter-btn"]')
       
       // 验证所有 Ticket 都显示
       const ticketCount = await page.locator('[data-test="ticket-item"]').count()
       expect(ticketCount).toBeGreaterThan(0)
     })
   })
   ```

5. 创建搜索功能端到端测试 `e2e/search.spec.ts`
   ```typescript
   import { test, expect } from '@playwright/test'
   
   test.describe('搜索功能端到端测试', () => {
     test.beforeEach(async ({ page }) => {
       await page.goto('/')
     })
     
     test('搜索 Ticket 标题', async ({ page }) => {
       // 在搜索框中输入关键词
       await page.fill('[data-test="search-input"]', 'Python')
       
       // 等待搜索结果
       await page.waitForTimeout(300)
       
       // 验证搜索结果
       const tickets = await page.locator('[data-test="ticket-item"]').all()
       for (const ticket of tickets) {
         const title = await ticket.locator('[data-test="ticket-title"]').textContent()
         expect(title?.toLowerCase()).toContain('python')
       }
     })
     
     test('清空搜索', async ({ page }) => {
       // 先进行搜索
       await page.fill('[data-test="search-input"]', '测试')
       await page.waitForTimeout(300)
       
       // 点击清空按钮
       await page.click('[data-test="clear-search-btn"]')
       
       // 验证搜索框已清空
       await expect(page.locator('[data-test="search-input"]')).toHaveValue('')
       
       // 验证所有 Ticket 都显示
       const ticketCount = await page.locator('[data-test="ticket-item"]').count()
       expect(ticketCount).toBeGreaterThan(0)
     })
     
     test('搜索无结果时显示提示', async ({ page }) => {
       // 搜索不存在的关键词
       await page.fill('[data-test="search-input"]', '不存在的Ticket标题123456')
       await page.waitForTimeout(300)
       
       // 验证显示无结果提示
       await expect(page.locator('[data-test="no-results-message"]')).toBeVisible()
       await expect(page.locator('[data-test="no-results-message"]')).toContainText('未找到')
     })
   })
   ```

6. 创建完整用户流程端到端测试 `e2e/user-workflow.spec.ts`
   ```typescript
   import { test, expect } from '@playwright/test'
   
   test.describe('完整用户流程端到端测试', () => {
     test('新用户创建和管理 Ticket 的完整流程', async ({ page }) => {
       // 1. 访问首页
       await page.goto('/')
       await expect(page).toHaveTitle(/Ticket 标签管理工具/)
       
       // 2. 创建标签
       await page.click('[data-test="tag-panel-toggle"]')
       await page.click('[data-test="create-tag-btn"]')
       await page.fill('[data-test="tag-name-input"]', '工作')
       await page.fill('[data-test="tag-color-input"]', '#0070f3')
       await page.click('[data-test="submit-tag-btn"]')
       await expect(page.locator('text=工作')).toBeVisible()
       
       // 3. 创建第一个 Ticket
       await page.click('[data-test="create-ticket-btn"]')
       await page.fill('[data-test="ticket-title-input"]', '完成项目文档')
       await page.fill('[data-test="ticket-description-input"]', '编写项目的技术文档和用户手册')
       await page.click('[data-test="tag-selector"]')
       await page.click('text=工作')
       await page.click('[data-test="submit-btn"]')
       await expect(page.locator('text=完成项目文档')).toBeVisible()
       
       // 4. 创建第二个 Ticket
       await page.click('[data-test="create-ticket-btn"]')
       await page.fill('[data-test="ticket-title-input"]', '代码审查')
       await page.fill('[data-test="ticket-description-input"]', '审查团队成员提交的代码')
       await page.click('[data-test="tag-selector"]')
       await page.click('text=工作')
       await page.click('[data-test="submit-btn"]')
       await expect(page.locator('text=代码审查')).toBeVisible()
       
       // 5. 使用标签筛选
       await page.click('[data-test="tag"][data-name="工作"]')
       const filteredTickets = await page.locator('[data-test="ticket-item"]').all()
       expect(filteredTickets.length).toBe(2)
       
       // 6. 搜索 Ticket
       await page.fill('[data-test="search-input"]', '文档')
       await page.waitForTimeout(300)
       await expect(page.locator('text=完成项目文档')).toBeVisible()
       await expect(page.locator('text=代码审查')).not.toBeVisible()
       
       // 7. 查看并更新 Ticket 详情
       await page.click('[data-test="ticket-item"]:first-child')
       await expect(page.locator('[data-test="ticket-detail"]')).toBeVisible()
       await page.click('[data-test="edit-btn"]')
       await page.fill('[data-test="ticket-description-input"]', '编写项目的技术文档和用户手册（已更新）')
       await page.click('[data-test="save-btn"]')
       await expect(page.locator('[data-test="success-message"]')).toBeVisible()
       
       // 8. 标记 Ticket 为完成
       await page.click('[data-test="complete-checkbox"]')
       await expect(page.locator('[data-test="completed-badge"]')).toBeVisible()
       
       // 9. 返回列表
       await page.click('[data-test="back-to-list-btn"]')
       
       // 10. 删除第二个 Ticket
       await page.click('[data-test="ticket-item"]:nth-child(2) [data-test="delete-btn"]')
       await page.click('[data-test="confirm-delete-btn"]')
       await expect(page.locator('[data-test="ticket-item"]')).toHaveCount(1)
     })
     
     test('批量操作流程', async ({ page }) => {
       // 创建多个 Ticket
       for (let i = 0; i < 5; i++) {
         await page.click('[data-test="create-ticket-btn"]')
         await page.fill('[data-test="ticket-title-input"]', `测试 Ticket ${i}`)
         await page.click('[data-test="submit-btn"]')
       }
       
       // 验证创建了 5 个 Ticket
       await expect(page.locator('[data-test="ticket-item"]')).toHaveCount(5)
       
       // 批量选择前 3 个 Ticket
       await page.click('[data-test="ticket-item"]:nth-child(1) [data-test="select-checkbox"]')
       await page.click('[data-test="ticket-item"]:nth-child(2) [data-test="select-checkbox"]')
       await page.click('[data-test="ticket-item"]:nth-child(3) [data-test="select-checkbox"]')
       
       // 批量标记为完成
       await page.click('[data-test="batch-complete-btn"]')
       
       // 验证前 3 个 Ticket 已完成
       for (let i = 1; i <= 3; i++) {
         await expect(page.locator(`[data-test="ticket-item"]:nth-child(${i}) [data-test="completed-badge"]`)).toBeVisible()
       }
       
       // 批量删除
       await page.click('[data-test="ticket-item"]:nth-child(1) [data-test="select-checkbox"]')
       await page.click('[data-test="ticket-item"]:nth-child(2) [data-test="select-checkbox"]')
       await page.click('[data-test="batch-delete-btn"]')
       await page.click('[data-test="confirm-batch-delete-btn"]')
       
       // 验证删除成功
       await expect(page.locator('[data-test="ticket-item"]')).toHaveCount(3)
     })
   })
   ```

7. 创建响应式设计端到端测试 `e2e/responsive.spec.ts`
   ```typescript
   import { test, expect, devices } from '@playwright/test'
   
   test.describe('响应式设计端到端测试', () => {
     test('桌面端布局', async ({ page }) => {
       await page.setViewportSize({ width: 1920, height: 1080 })
       await page.goto('/')
       
       // 验证桌面端布局
       await expect(page.locator('[data-test="sidebar"]')).toBeVisible()
       await expect(page.locator('[data-test="main-content"]')).toBeVisible()
       await expect(page.locator('[data-test="ticket-list"]')).toBeVisible()
     })
     
     test('平板端布局', async ({ page }) => {
       await page.setViewportSize({ width: 768, height: 1024 })
       await page.goto('/')
       
       // 验证平板端布局
       await expect(page.locator('[data-test="sidebar"]')).toBeVisible()
       await expect(page.locator('[data-test="main-content"]')).toBeVisible()
     })
     
     test('移动端布局', async ({ page }) => {
       await page.setViewportSize({ width: 375, height: 667 })
       await page.goto('/')
       
       // 验证移动端布局
       await expect(page.locator('[data-test="mobile-menu-btn"]')).toBeVisible()
       await expect(page.locator('[data-test="sidebar"]')).not.toBeVisible()
       
       // 点击菜单按钮
       await page.click('[data-test="mobile-menu-btn"]')
       await expect(page.locator('[data-test="sidebar"]')).toBeVisible()
     })
     
     test('iPhone 视图', async ({ page }) => {
       await page.setViewportSize(devices['iPhone 13'].viewport)
       await page.goto('/')
       
       // 验证移动端适配
       await expect(page.locator('[data-test="mobile-menu-btn"]')).toBeVisible()
       await page.click('[data-test="mobile-menu-btn"]')
       await expect(page.locator('[data-test="sidebar"]')).toBeVisible()
     })
   })
   ```

8. 创建性能测试 `e2e/performance.spec.ts`
   ```typescript
   import { test, expect } from '@playwright/test'
   
   test.describe('性能端到端测试', () => {
     test('页面加载性能', async ({ page }) => {
       const startTime = Date.now()
       await page.goto('/')
       const loadTime = Date.now() - startTime
      
       // 验证页面加载时间小于 2 秒
       expect(loadTime).toBeLessThan(2000)
     })
     
     test('列表渲染性能', async ({ page }) => {
       await page.goto('/')
      
       // 创建 100 个 Ticket
       for (let i = 0; i < 100; i++) {
         await page.click('[data-test="create-ticket-btn"]')
         await page.fill('[data-test="ticket-title-input"]', `性能测试 Ticket ${i}`)
         await page.click('[data-test="submit-btn"]')
       }
      
       const startTime = Date.now()
       await page.reload()
       await page.waitForSelector('[data-test="ticket-item"]')
       const renderTime = Date.now() - startTime
      
       // 验证渲染时间小于 1 秒
       expect(renderTime).toBeLessThan(1000)
     })
     
     test('搜索响应性能', async ({ page }) => {
       await page.goto('/')
      
       // 创建测试数据
       for (let i = 0; i < 50; i++) {
         await page.click('[data-test="create-ticket-btn"]')
         await page.fill('[data-test="ticket-title-input"]`, `搜索测试 ${i}`)
         await page.click('[data-test="submit-btn"]')
       }
      
      const startTime = Date.now()
      await page.fill('[data-test="search-input"]', '搜索测试')
      await page.waitForTimeout(300)
      const searchTime = Date.now() - startTime
     
      // 验证搜索响应时间小于 500ms
      expect(searchTime).toBeLessThan(500)
    })
  })
   ```

9. 创建可访问性测试 `e2e/accessibility.spec.ts`
   ```typescript
   import { test, expect } from '@playwright/test'
   
   test.describe('可访问性端到端测试', () => {
     test('键盘导航', async ({ page }) => {
       await page.goto('/')
       
       // 使用 Tab 键导航
       await page.keyboard.press('Tab')
       await expect(page.locator(':focus')).toBeVisible()
       
       await page.keyboard.press('Tab')
       await expect(page.locator(':focus')).toBeVisible()
       
       // 使用 Enter 键激活按钮
       await page.keyboard.press('Enter')
       await expect(page.locator('[data-test="ticket-form"]')).toBeVisible()
     })
     
     test('ARIA 标签', async ({ page }) => {
       await page.goto('/')
       
       // 验证按钮有 aria-label
       const createBtn = page.locator('[data-test="create-ticket-btn"]')
       await expect(createBtn).toHaveAttribute('aria-label')
       
       // 验证表单输入有 aria-label
       const titleInput = page.locator('[data-test="ticket-title-input"]')
       await expect(titleInput).toHaveAttribute('aria-label')
     })
     
     test('屏幕阅读器支持', async ({ page }) => {
       await page.goto('/')
       
       // 验证重要元素有适当的角色
       await expect(page.locator('main')).toHaveAttribute('role', 'main')
       await expect(page.locator('nav')).toHaveAttribute('role', 'navigation')
       
       // 验证状态变化有通知
       await page.click('[data-test="create-ticket-btn"]')
       await expect(page.locator('[role="status"]')).toBeVisible()
     })
   })
   ```

**交付标准**：
- 所有端到端测试通过
- 覆盖主要用户流程
- 支持多浏览器测试（Chrome、Firefox、Safari）
- 响应式设计测试通过
- 性能测试满足要求
- 可访问性测试通过

**预计时间**：3 天

---

## 6. 部署计划

### 6.1 Docker 配置

#### 6.1.1 后端 Dockerfile

**任务描述**：创建后端 Docker 镜像

**具体步骤**：
1. 创建 `backend/Dockerfile`
   ```dockerfile
   FROM python:3.12-slim
   
   WORKDIR /app
   
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt
   
   COPY . .
   
   EXPOSE 8000
   
   CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
   ```

**交付标准**：
- Docker 镜像构建成功
- 容器正常运行

**预计时间**：0.5 天

---

#### 6.1.2 前端 Dockerfile

**任务描述**：创建前端 Docker 镜像

**具体步骤**：
1. 创建 `frontend/Dockerfile`
   ```dockerfile
   FROM node:20-alpine as builder
   
   WORKDIR /app
   
   COPY package*.json ./
   RUN npm install
   
   COPY . .
   RUN npm run build
   
   FROM nginx:alpine
   
   COPY --from=builder /app/dist /usr/share/nginx/html
   COPY nginx.conf /etc/nginx/conf.d/default.conf
   
   EXPOSE 80
   
   CMD ["nginx", "-g", "daemon off;"]
   ```

**交付标准**：
- Docker 镜像构建成功
- 容器正常运行

**预计时间**：0.5 天

---

#### 6.1.3 Docker Compose 配置

**任务描述**：创建 Docker Compose 配置文件

**具体步骤**：
1. 创建 `docker-compose.yml`
   ```yaml
   version: '3.8'
   
   services:
     postgres:
       image: postgres:19
       environment:
         POSTGRES_USER: ticketadmin
         POSTGRES_PASSWORD: ticketpass
         POSTGRES_DB: ticketdb
       volumes:
         - postgres_data:/var/lib/postgresql/data
       ports:
         - "5432:5432"
       healthcheck:
         test: ["CMD-SHELL", "pg_isready -U ticketadmin"]
         interval: 10s
         timeout: 5s
         retries: 5
   
     backend:
       build: ./backend
       environment:
         DATABASE_URL: postgresql+asyncpg://ticketadmin:ticketpass@postgres:5432/ticketdb
         SECRET_KEY: ${SECRET_KEY:-your-secret-key}
       ports:
         - "8000:8000"
       depends_on:
         postgres:
           condition: service_healthy
       healthcheck:
         test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
         interval: 30s
         timeout: 10s
         retries: 3
   
     frontend:
       build: ./frontend
       ports:
         - "3000:80"
       depends_on:
         - backend
   
   volumes:
     postgres_data:
   ```

**交付标准**：
- Docker Compose 配置正确
- 所有服务正常启动

**预计时间**：0.5 天

---

### 6.2 生产环境部署

**任务描述**：配置生产环境部署

**具体步骤**：

1. 创建生产环境配置文件 `backend/.env.production`
   ```bash
   # 数据库配置
   DATABASE_URL=postgresql+asyncpg://user:password@host:5432/dbname
   
   # 安全配置
   SECRET_KEY=your-production-secret-key-change-this
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   
   # 应用配置
   ENV=production
   DEBUG=False
   LOG_LEVEL=info
   
   # CORS 配置
   ALLOWED_ORIGINS=https://yourdomain.com
   ```

2. 配置 Nginx 反向代理 `nginx/nginx.conf`
   ```nginx
   server {
       listen 80;
       server_name yourdomain.com;
       
       # 重定向到 HTTPS
       return 301 https://$server_name$request_uri;
   }
   
   server {
       listen 443 ssl http2;
       server_name yourdomain.com;
       
       # SSL 证书配置
       ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
       ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
       ssl_protocols TLSv1.2 TLSv1.3;
       ssl_ciphers HIGH:!aNULL:!MD5;
       
       # 前端静态文件
       location / {
           root /usr/share/nginx/html;
           try_files $uri $uri/ /index.html;
           index index.html;
       }
       
       # 后端 API 代理
       location /api/ {
           proxy_pass http://backend:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
           
           # 超时配置
           proxy_connect_timeout 60s;
           proxy_send_timeout 60s;
           proxy_read_timeout 60s;
       }
       
       # API 文档代理
       location /docs {
           proxy_pass http://backend:8000/docs;
           proxy_set_header Host $host;
       }
       
       # 日志配置
       access_log /var/log/nginx/access.log;
       error_log /var/log/nginx/error.log;
   }
   ```

3. 创建生产环境 Docker Compose 配置 `docker-compose.prod.yml`
   ```yaml
   version: '3.8'
   
   services:
     postgres:
       image: postgres:19
       container_name: ticket-postgres
       environment:
         POSTGRES_USER: ${POSTGRES_USER}
         POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
         POSTGRES_DB: ${POSTGRES_DB}
       volumes:
         - postgres_data:/var/lib/postgresql/data
         - ./postgres/init:/docker-entrypoint-initdb.d
       networks:
         - ticket-network
       restart: unless-stopped
       healthcheck:
         test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
         interval: 10s
         timeout: 5s
         retries: 5
   
     backend:
       build:
         context: ./backend
         dockerfile: Dockerfile.prod
       container_name: ticket-backend
       environment:
         DATABASE_URL: postgresql+asyncpg://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}
         SECRET_KEY: ${SECRET_KEY}
         ENV: production
         DEBUG: "false"
       volumes:
         - ./backend/logs:/app/logs
       networks:
         - ticket-network
       depends_on:
         postgres:
           condition: service_healthy
       restart: unless-stopped
       healthcheck:
         test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
         interval: 30s
         timeout: 10s
         retries: 3
   
     frontend:
       build:
         context: ./frontend
         dockerfile: Dockerfile.prod
       container_name: ticket-frontend
       networks:
         - ticket-network
       depends_on:
         - backend
       restart: unless-stopped
   
     nginx:
       image: nginx:alpine
       container_name: ticket-nginx
       ports:
         - "80:80"
         - "443:443"
       volumes:
         - ./nginx/nginx.conf:/etc/nginx/conf.d/default.conf
         - ./nginx/ssl:/etc/letsencrypt
         - ./nginx/logs:/var/log/nginx
       networks:
         - ticket-network
       depends_on:
         - frontend
         - backend
       restart: unless-stopped
   
   volumes:
     postgres_data:
   
   networks:
     ticket-network:
       driver: bridge
   ```

4. 创建部署脚本 `deploy.sh`
   ```bash
   #!/bin/bash
   
   set -e
   
   echo "开始部署 Ticket 标签管理工具..."
   
   # 检查环境变量文件
   if [ ! -f .env ]; then
       echo "错误：.env 文件不存在"
       exit 1
   fi
   
   # 拉取最新代码
   echo "拉取最新代码..."
   git pull origin main
   
   # 构建并启动服务
   echo "构建并启动服务..."
   docker-compose -f docker-compose.prod.yml up -d --build
   
   # 等待服务启动
   echo "等待服务启动..."
   sleep 30
   
   # 执行数据库迁移
   echo "执行数据库迁移..."
   docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head
   
   # 检查服务状态
   echo "检查服务状态..."
   docker-compose -f docker-compose.prod.yml ps
   
   echo "部署完成！"
   echo "前端访问地址：https://yourdomain.com"
   echo "API 文档地址：https://yourdomain.com/docs"
   ```

5. 配置 SSL 证书（使用 Let's Encrypt）
   ```bash
   # 安装 Certbot
   sudo apt-get update
   sudo apt-get install certbot python3-certbot-nginx
   
   # 获取 SSL 证书
   sudo certbot --nginx -d yourdomain.com
   
   # 设置自动续期
   sudo certbot renew --dry-run
   ```

6. 配置日志收集
   ```bash
   # 创建日志目录
   mkdir -p backend/logs
   mkdir -p nginx/logs
   
   # 配置日志轮转
   sudo cat > /etc/logrotate.d/ticket-manager << EOF
   /var/log/nginx/*.log {
       daily
       missingok
       rotate 14
       compress
       delaycompress
       notifempty
       create 0640 www-data adm
       sharedscripts
       postrotate
           [ -f /var/run/nginx.pid ] && kill -USR1 `cat /var/run/nginx.pid`
       endscript
   }
   
   /app/logs/*.log {
       daily
       missingok
       rotate 14
       compress
       delaycompress
       notifempty
       create 0640 root root
   }
   EOF
   ```

7. 配置监控和告警
   ```bash
   # 安装 Prometheus 和 Grafana（可选）
   # 或使用云监控服务（如 CloudWatch、Datadog）
   
   # 配置健康检查端点
   # 后端已经包含 /health 端点
   # 可以配置 Uptime Monitor 监控服务可用性
   ```

8. 配置备份策略
   ```bash
   # 创建数据库备份脚本
   cat > backup.sh << 'EOF'
   #!/bin/bash
   
   BACKUP_DIR="/backups"
   DATE=$(date +%Y%m%d_%H%M%S)
   BACKUP_FILE="$BACKUP_DIR/ticketdb_$DATE.sql"
   
   mkdir -p $BACKUP_DIR
   
   # 备份数据库
   docker-compose -f docker-compose.prod.yml exec -T postgres pg_dump -U ticketadmin ticketdb > $BACKUP_FILE
   
   # 压缩备份文件
   gzip $BACKUP_FILE
   
   # 删除 7 天前的备份
   find $BACKUP_DIR -name "*.sql.gz" -mtime +7 -delete
   
   echo "备份完成：$BACKUP_FILE.gz"
   EOF
   
   chmod +x backup.sh
   
   # 添加到 crontab（每天凌晨 2 点执行）
   0 2 * * * /path/to/backup.sh >> /var/log/backup.log 2>&1
   ```

9. 安全加固
   ```bash
   # 配置防火墙
   sudo ufw allow 22/tcp
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   sudo ufw enable
   
   # 限制 SSH 访问
   sudo sed -i 's/#PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
   sudo sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
   sudo systemctl restart sshd
   
   # 定期更新系统
   sudo apt-get update && sudo apt-get upgrade -y
   ```

**交付标准**：
- 生产环境部署成功
- 服务稳定运行
- SSL 证书配置正确
- 日志收集正常工作
- 备份策略已实施
- 监控告警已配置

**预计时间**：1 天

---

## 7. 文档编写

### 7.1 API 文档

**任务描述**：编写 API 接口文档

**具体步骤**：
1. 使用 FastAPI 自动生成的 Swagger UI
2. 补充接口说明和示例
3. 导出 OpenAPI 规范

**交付标准**：
- API 文档完整
- 示例代码正确

**预计时间**：0.5 天

---

### 7.2 用户手册

**任务描述**：编写用户使用手册

**具体步骤**：
1. 功能介绍
2. 操作指南
3. 常见问题解答

**交付标准**：
- 文档清晰易懂
- 截图完整

**预计时间**：0.5 天

---
### 7.3 README.md

**任务描述**：编写项目根目录的 README.md 文档

**具体步骤**：
1. 编写项目概述和功能特性介绍
2. 列出技术栈和依赖版本
3. 提供快速开始指南（安装、运行、开发）
4. 说明项目结构
5. 添加贡献指南和许可证信息

**主要内容**：
- 项目标题和简介
- 功能特性列表（Ticket 管理、标签系统、搜索过滤、响应式设计等）
- 技术栈说明（前端：Vue3 + TypeScript + Vite + Element Plus + UnoCSS；后端：FastAPI + PostgreSQL + SQLAlchemy）
- 快速开始（Docker Compose 部署、本地开发环境搭建）
- 项目目录结构
- 开发指南和测试说明
- 常见问题解答

**交付标准**：
- 文档结构清晰，易于阅读
- 包含必要的安装和运行说明
- 提供完整的快速开始示例

**预计时间**：0.5 天

---

### 7.4 部署指南

**任务描述**：编写详细的部署指南文档

**具体步骤**：
1. 编写开发环境部署指南
2. 编写生产环境部署指南
3. 提供 Docker Compose 部署说明
4. 说明环境变量配置
5. 提供故障排查和常见问题解决方案

**主要内容**：
- 环境要求（Node.js、Python、PostgreSQL、Docker 版本）
- 开发环境搭建步骤
- 生产环境配置（环境变量、数据库配置、安全设置）
- Docker Compose 部署流程
- SSL 证书配置（Let's Encrypt）
- Nginx 反向代理配置
- 日志管理和监控配置
- 数据库备份策略
- 安全加固建议
- 故障排查指南

**交付标准**：
- 部署步骤详细准确
- 包含完整的配置示例
- 提供常见问题解决方案

**预计时间**：0.5 天

---

## 8. 项目时间表

| 阶段         | 任务                         | 预计时间 | 优先级 |
|--------------|------------------------------|----------|--------|
| 环境准备     | 开发环境搭建                 | 1 天     | 高     |
| 后端开发     | 数据库设计与实现             | 2 天     | 高     |
| 后端开发     | Pydantic 模型定义            | 1 天     | 高     |
| 后端开发     | CRUD 操作实现                | 1.5 天   | 高     |
| 后端开发     | API 路由实现                 | 2 天     | 高     |
| 后端开发     | 工具函数和中间件             | 1 天     | 中     |
| 前端开发     | 项目初始化和配置             | 1 天     | 高     |
| 前端开发     | 类型定义和 API 封装          | 1 天     | 高     |
| 前端开发     | 状态管理                     | 1.5 天   | 高     |
| 前端开发     | 组件开发                     | 3 天     | 高     |
| 前端开发     | 页面开发                     | 1 天     | 高     |
| 测试         | 后端测试                     | 3 天     | 高     |
| 测试         | 前端测试                     | 4 天     | 高     |
| 部署         | Docker 配置                  | 1.5 天   | 高     |
| 部署         | 生产环境部署                 | 1 天     | 中     |
| 部署         | 部署文档编写                 | 0.5 天   | 中     |
| 文档         | API 文档和用户手册           | 1 天     | 低     |
| 文档         | README.md 文档编写           | 0.5 天   | 低     |
| **总计**     |                              | **28 天** |        |

---

## 9. 风险评估与应对

| 风险项         | 可能性 | 影响程度 | 应对措施                     |
|----------------|--------|----------|------------------------------|
| 需求变更       | 高     | 中       | 建立变更管理流程，及时沟通   |
| 技术难点       | 中     | 高       | 提前进行技术调研，预留缓冲时间 |
| 人员变动       | 低     | 高       | 建立知识共享机制，文档化流程 |
| 性能问题       | 中     | 中       | 提前进行性能测试和优化       |
| 安全漏洞       | 低     | 高       | 定期进行安全审计和漏洞扫描   |

---

## 10. 交付标准

### 10.1 代码质量

- 代码通过 Black、Flake8、MyPy 检查
- 单元测试覆盖率 ≥ 80%
- 无严重安全漏洞

### 10.2 功能完整性

- 所有需求功能实现完成
- API 接口符合设计文档
- 前端界面符合设计稿

### 10.3 性能指标

- 页面响应时间 ≤ 200ms
- 数据库查询响应时间 ≤ 50ms
- 支持同时在线用户数 ≥ 100

### 10.4 文档完整性

- API 文档完整
- 用户手册清晰
- 代码注释充分

---

## 11. 附录

### 11.1 技术栈版本

| 技术选型                  | 版本号       |
|---------------------------|--------------|
| Vue3 + TypeScript        | 3.5.26 + 5.9.3 |
| Vite                      | 8.0.0        |
| Element Plus + UnoCSS     | 2.13.0 + 0.60.2 |
| FastAPI                   | 0.115.0      |
| PostgreSQL                | 17.0         |
| SQLAlchemy                | 2.0.36       |
| Swagger UI                | 6.5.0        |

### 11.2 参考资料

- [FastAPI 官方文档](https://fastapi.tiangolo.com/)
- [Vue3 官方文档](https://vuejs.org/)
- [Element Plus 文档](https://element-plus.org/)
- [UnoCSS 文档](https://unocss.dev/)
- [PostgreSQL 官方文档](https://www.postgresql.org/docs/)

---

**版本历史**

| 版本 | 日期       | 作者       | 变更描述                     |
|------|------------|------------|------------------------------|
| 1.0  | 2025-01-01 | 开发团队   | 初始版本                     |