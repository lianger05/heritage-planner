# 长期记忆

## AI项目：古建文旅经济智能规划助手

### 项目定位
- 方向：古建保护性开发方案AI生成平台
- 核心功能：选择古建→AI生成方案（动线+业态+经济估算）→多轮对话修改→导出报告
- 用户：文旅规划从业者、地方文旅局、学术研究者
- 分工模式：用户主导需求与架构设计，灵犀定技术方向，其他AI填充代码

### 技术栈
- 前端: Next.js 14 + TypeScript + Tailwind + shadcn/ui
- 后端: FastAPI + SQLAlchemy(async) + Pydantic v2
- AI引擎: DeepSeek/Qwen + ChromaDB(RAG) + Neo4j/内存(知识图谱)
- 数据: SQLite(本地开发) / PostgreSQL+PostGIS(生产) + Redis(可选)
- 部署: 本地开发直接运行 / 生产 Docker Compose

### 项目路径
C:\Users\Admin\WorkBuddy\2026-05-16-task-15\

### 本地开发环境（2026-05-17 确立）
- **后端**: `uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload`（8000被C-Lodop占用）
- **前端**: `npm run dev` (localhost:3000)
- **数据库**: SQLite (./data/heritage_planner.db) + ChromaDB持久化 (./data/chroma_db/)
- **知识图谱**: 内存模式（neo4j_enabled=False）
- **LLM缓存**: 内存字典（llm_cache_enabled=False）
- **种子数据**: 10个开封古建 + 5条法规（SQLite）+ 5条法规 + 4条案例（ChromaDB向量）
- **LLM**: DeepSeek API Key已配置（sk-b9134...），方案生成功能可用

### 关键架构决策
- 方案内容用JSON存储（非关系化），方便LLM结构化输出
- AI引擎四模块：LLM生成器 + RAG检索 + 知识图谱推理 + 约束优化
- LLM支持多供应商切换（DeepSeek主/Qwen备/OpenAI兜底），DeepSeek已配Key可用
- **重要**: 修改.env后必须完全杀掉uvicorn进程重启（@lru_cache导致reload不刷新Settings）
- 本地开发全栈降级：SQLite/内存缓存/内存KG/嵌入式ChromaDB
- 生产环境可切换回 PostgreSQL/Redis/Neo4j/HTTP ChromaDB
- 数据起步策略：先做河南省开封市深度数据
- 知识图谱种子：8个朝代 + 5种风格 + 4个保护等级 + 5处开封古建

### 阶段规划
- Phase 1 (4周): MVP - 基础数据+LLM对话+简单报告
- Phase 2 (4周): 核心AI - RAG+知识图谱+约束优化
- Phase 3 (3周): 深度打磨 - 经济指标+动线可视化+PDF导出
- Phase 4 (持续): 上线运营 - 用户系统+部署+学术产出
