# 架构设计文档

## 1. 系统架构

四层架构，自上而下：

### 1.1 前端交互层 (Next.js)
- **地图交互页** (`/map`): 高德地图展示古建分布，支持空间筛选
- **方案生成页** (`/plan`): 选择古建 → 填写需求 → AI生成 → 查看结果 → 多轮对话修改
- **报告查看页** (`/report`): 预览方案报告，导出PDF/DOCX/Markdown
- **项目管理页** (`/project`): 管理古建信息、方案列表

### 1.2 AI引擎层 (Python Services)
核心是 `PlanGeneratorService`，编排四个子模块：

```
用户输入 → [知识图谱查询] → [RAG法规检索] → [RAG案例检索] → [LLM方案生成] → [约束校验] → 结构化方案
```

- **LLM规划生成器** (`llm_service.py`): 封装OpenAI兼容API，支持多供应商切换、缓存、流式输出、JSON结构化输出
- **RAG政策检索** (`rag_service.py`): ChromaDB向量检索 + 混合检索（向量+BM25），法规入库/检索/校验
- **知识图谱推理** (`kg_service.py`): Neo4j图数据库，保护等级约束传播、相似古建发现
- **约束优化引擎** (`plan_service.py`): 法规红线硬约束 + 专家经验软约束，多目标平衡

### 1.3 数据层
- **PostgreSQL + PostGIS**: 关系数据 + 空间数据（古建坐标、范围查询）
- **Neo4j**: 知识图谱（古建-朝代-风格-保护等级的关系网络）
- **ChromaDB**: 向量数据库（法规/案例的语义检索）
- **Redis**: LLM响应缓存、会话管理
- **MinIO**: 报告文件存储

### 1.4 外部服务层
- **LLM API**: DeepSeek/Qwen/OpenAI
- **高德地图 API**: POI检索、地理编码、地图渲染
- **开放数据**: 文物局名录、统计年鉴

## 2. 数据模型

### 2.1 核心实体关系

```
Heritage 1──N Plan 1──N ChatSession
                │
                └── 保护措施 / 旅游动线 / 业态布局 / 经济估算 / 约束校验 (JSONB)

Regulation (独立表 + ChromaDB向量)
```

### 2.2 方案数据结构

方案内容以JSONB存储在Plan表中，结构由LLM的结构化输出保证：

```json
{
  "protection_measures": { "core_zone": "...", "buffer_zone": "...", ... },
  "tourism_routes": { "main_route": {...}, "alternative_routes": [...], ... },
  "business_layout": { "cultural_creative": {...}, "prohibited": [...] },
  "economic_estimation": { "investment": {...}, "revenue": {...}, "roi": {...} },
  "constraints_check": { "violations": [...], "warnings": [...], "passed": bool }
}
```

### 2.3 知识图谱Schema

节点类型：Heritage, Dynasty, Style, ProtectionLevel, BuildingType, Region
关系类型：BUILT_IN, HAS_STYLE, HAS_PROTECTION, HAS_TYPE, LOCATED_IN, CONSTRAINS

## 3. AI引擎详细设计

### 3.1 规划生成流程

```
1. 用户选择古建 → 获取heritage_info
2. 知识图谱查询:
   - 获取保护等级约束 (Heritage → ProtectionLevel → constraints)
   - 查找相似古建 (同风格/同时代/同类型的其他古建)
3. RAG法规检索:
   - 查询 "古建名 保护等级 保护开发规划约束" → top-8相关法规
4. RAG案例检索:
   - 查询 "建筑类型 保护等级 文旅开发成功案例" → top-3相似案例
5. LLM方案生成:
   - System Prompt: 规划专家角色 + 严格JSON输出格式
   - User Prompt: 古建信息 + 图谱约束 + 法规条文 + 案例参考 + 用户需求
   - 参数: temperature=0.7, max_tokens=4096, response_format=json
6. 约束校验:
   - 用LLM对比生成方案与检索法规，检查违规
   - 输出: violations/warnings/passed
7. 存储方案 → 返回前端
```

### 3.2 多轮对话设计

- 会话ID关联方案，上下文注入当前方案内容
- 对话历史存入ChatSession.messages (JSONB)
- 保留最近20条消息，避免token溢出
- AI回复中可包含方案修改片段（updated_plan字段）

### 3.3 缓存策略

- LLM响应缓存：相同messages hash → Redis缓存（TTL 1小时）
- 法规检索缓存：ChromaDB查询结果可短期缓存
- 地图标记：Redis缓存省/市级聚合数据

## 4. 前端页面设计

### 4.1 页面路由

| 路径 | 页面 | 核心功能 |
|---|---|---|
| `/` | 首页 | 产品介绍、功能入口 |
| `/map` | 地图浏览 | 高德地图+古建标记+筛选 |
| `/plan` | 方案生成 | 4步流程：选择→配置→生成→对话 |
| `/report` | 报告查看 | 方案预览+导出 |
| `/project` | 项目管理 | 古建列表+方案列表 |

### 4.2 状态管理

使用Zustand管理全局状态：
- selectedHeritage: 当前选中古建ID
- currentPlan: 当前方案ID
- chatSessionId: 对话会话ID
- mapCenter/mapZoom: 地图视图

## 5. 部署架构

### 开发环境
- Docker Compose一键启动所有服务
- 后端热重载 (uvicorn --reload)
- 前端热重载 (next dev)

### 生产环境（建议）
- 前端: Vercel / 自建Nginx
- 后端: GCE / 阿里云ECS
- 数据库: RDS PostgreSQL + PostGIS
- Neo4j: 云服务或自建
- ChromaDB: 自建
- Redis: 云服务
- MinIO: OSS替代

## 6. 其他AI模型填充指南

### 6.1 项目约定

1. **后端代码规范**: Black格式化 + Ruff检查，类型注解必须
2. **前端代码规范**: ESLint + Prettier，组件使用函数式 + hooks
3. **API设计**: RESTful，严格JSON Schema，所有端点有Pydantic Schema
4. **组件库**: 前端使用shadcn/ui，不要自造UI组件
5. **环境变量**: 所有密钥走.env，不入版本库
6. **包管理**: 后端uv/pip，前端pnpm

### 6.2 待填充功能清单

以下功能需要其他AI模型逐步实现：

**后端：**
- [ ] WeasyPrint PDF报告生成（Jinja2模板）
- [ ] python-docx DOCX报告生成
- [ ] 高德地图API封装（地理编码、POI检索、路径规划）
- [ ] 用户认证系统（JWT）
- [ ] 方案对比接口
- [ ] 经济指标估算参数化模型
- [ ] LLM流式输出端点（SSE）
- [ ] 单元测试

**前端：**
- [ ] 高德地图集成（@amap/amap-jsapi-loader）
- [ ] shadcn/ui组件安装与配置
- [ ] 方案详情页面美化（卡片化展示代替JSON预览）
- [ ] 旅游动线可视化（地图上绘制路线）
- [ ] 报告预览（Markdown渲染）
- [ ] 响应式布局
- [ ] 错误处理与Loading状态
- [ ] ECharts经济数据可视化

**数据：**
- [ ] 扩充更多省份古建数据
- [ ] 法规PDF解析入库
- [ ] 案例库扩充（学术论文摘要）
- [ ] POI数据自动化采集

### 6.3 关键文件说明

| 文件 | 作用 | 修改注意 |
|---|---|---|
| `backend/app/core/config.py` | 全局配置 | 新增配置项需同步更新.env.example |
| `backend/app/services/plan_service.py` | AI核心引擎 | Prompt修改需测试输出格式 |
| `backend/app/services/llm_service.py` | LLM调用 | 切换供应商需测试兼容性 |
| `backend/app/schemas/heritage.py` | API数据契约 | 修改需同步前端types |
| `frontend/src/lib/api.ts` | 前端API客户端 | 需与后端Schema保持同步 |
| `frontend/src/types/heritage.ts` | 前端类型定义 | 需与后端Schema保持同步 |
