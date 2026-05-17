# 古建文旅经济智能规划助手

> AI驱动的古建保护性开发方案生成平台

## 项目概述

选择一个古建遗产片区，AI自动生成平衡文物保护红线与经济效益的保护性开发方案——旅游动线规划、业态布局建议、投资回报预估，一站完成。

## 技术栈

| 层 | 技术 |
|---|---|
| 前端 | Next.js 14 + TypeScript + Tailwind CSS + shadcn/ui |
| 后端 | FastAPI (Python 3.12+) |
| 数据库 | PostgreSQL 16 + PostGIS 3.4 |
| 知识图谱 | Neo4j 5.20 Community |
| 向量库 | ChromaDB |
| 缓存 | Redis 7 |
| 文件存储 | MinIO |
| LLM | DeepSeek / Qwen / OpenAI (兼容接口) |
| 地图 | 高德地图 JS API 2.0 |

## 项目结构

```
heritage-planner/
├── backend/                    # FastAPI 后端
│   ├── app/
│   │   ├── api/v1/            # API路由
│   │   │   ├── endpoints/     # 各功能端点
│   │   │   └── router.py      # 路由汇总
│   │   ├── core/              # 核心配置
│   │   │   ├── config.py      # Pydantic Settings
│   │   │   └── database.py    # SQLAlchemy异步引擎
│   │   ├── models/            # ORM模型
│   │   ├── schemas/           # Pydantic Schema
│   │   ├── services/          # 业务逻辑层
│   │   │   ├── llm_service.py # LLM封装（多供应商）
│   │   │   ├── rag_service.py # RAG检索
│   │   │   ├── kg_service.py  # 知识图谱
│   │   │   └── plan_service.py# 规划生成（核心引擎）
│   │   └── main.py            # 应用入口
│   ├── Dockerfile
│   └── pyproject.toml
├── frontend/                   # Next.js 前端
│   ├── src/
│   │   ├── app/               # 页面路由
│   │   │   ├── map/           # 地图浏览页
│   │   │   ├── plan/          # 方案生成页
│   │   │   ├── report/        # 报告查看页
│   │   │   └── project/       # 项目管理页
│   │   ├── components/        # UI组件
│   │   ├── lib/               # 工具函数
│   │   │   ├── api.ts         # API客户端
│   │   │   ├── store.ts       # Zustand状态管理
│   │   │   └── utils.ts       # 通用工具
│   │   └── types/             # TypeScript类型
│   ├── Dockerfile
│   └── package.json
├── data/
│   └── seed/                  # 种子数据
│       ├── init_db.sql        # 数据库建表
│       ├── kaifeng_heritage.sql # 开封古建数据
│       ├── regulations.sql    # 法规数据
│       └── seed_rag.py        # RAG向量入库
├── docs/                      # 文档
├── docker-compose.yml         # 容器编排
├── .env.example               # 环境变量模板
└── .gitignore
```

## 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone <repo-url>
cd heritage-planner

# 复制环境变量
cp .env.example .env
# 编辑 .env 填入API Key
```

### 2. 启动服务（Docker Compose）

```bash
# 启动所有服务
docker compose up -d

# 查看日志
docker compose logs -f backend
```

### 3. 初始化数据

```bash
# 数据库表和种子数据已通过docker-entrypoint自动初始化

# 导入RAG向量数据（需要ChromaDB启动后）
cd data/seed
pip install chromadb
python seed_rag.py

# 初始化知识图谱（需要Neo4j启动后）
# 在后端容器内执行
docker compose exec backend python -c "
from app.services.kg_service import KnowledgeGraphService
import asyncio
kg = KnowledgeGraphService()
asyncio.run(kg.connect())
asyncio.run(kg.init_seed_data())
asyncio.run(kg.close())
"
```

### 4. 访问服务

- 前端：http://localhost:3000
- 后端API文档：http://localhost:8000/api/docs
- Neo4j控制台：http://localhost:7474
- MinIO控制台：http://localhost:9001

## API概览

| 端点 | 方法 | 描述 |
|---|---|---|
| `/api/v1/heritage/` | GET | 获取古建列表（分页/筛选） |
| `/api/v1/heritage/{id}` | GET | 获取古建详情 |
| `/api/v1/heritage/` | POST | 创建古建信息 |
| `/api/v1/plan/generate` | POST | AI生成规划方案 |
| `/api/v1/plan/{id}` | GET | 获取方案详情 |
| `/api/v1/plan/{id}/refine` | POST | AI修改方案 |
| `/api/v1/chat/message` | POST | AI多轮对话 |
| `/api/v1/regulation/search` | POST | 法规语义检索 |
| `/api/v1/regulation/check` | POST | 方案合规校验 |
| `/api/v1/map/markers` | POST | 获取地图标记 |
| `/api/v1/report/generate` | POST | 导出方案报告 |

## 开发指南

详见 [ARCHITECTURE.md](./docs/ARCHITECTURE.md)

## 许可

MIT
