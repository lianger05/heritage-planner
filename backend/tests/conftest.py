"""测试配置 - pytest fixtures 和 TestClient"""

import os
import sys
import asyncio
from pathlib import Path
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

# 确保 backend 在 sys.path 中
sys.path.insert(0, str(Path(__file__).parent.parent))

# 测试环境变量 - 必须在导入 app 前设置
os.environ["APP_ENV"] = "testing"
os.environ["APP_DEBUG"] = "false"
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./data/test_heritage_planner.db"
os.environ["DATABASE_URL_SYNC"] = "sqlite:///./data/test_heritage_planner.db"
os.environ["API_KEY"] = ""  # 测试环境不启用 API Key 认证
os.environ["CORS_ORIGINS"] = "http://localhost:3000"


@pytest.fixture(scope="session")
def event_loop():
    """创建 session 级事件循环"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """创建异步 HTTP 测试客户端"""
    from app.main import app  # noqa: E402

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture
def sample_heritage_data() -> dict:
    """示例古建数据"""
    return {
        "name": "测试古建",
        "dynasty": "明",
        "building_type": "寺庙",
        "protection_level": "全国重点文物保护单位",
        "style": "宗教建筑",
        "province": "河南",
        "city": "洛阳",
        "district": "老城区",
        "address": "测试地址1号",
        "longitude": 112.45,
        "latitude": 34.62,
        "description": "用于单元测试的示例古建",
        "current_status": "保存完好",
        "area_size": 10000,
        "is_open": True,
        "ticket_price": 50.0,
        "annual_visitors": 100000,
    }


@pytest.fixture
def sample_plan_data() -> dict:
    """示例规划请求数据"""
    return {
        "heritage_id": 1,
        "title": "测试规划方案",
        "description": "用于单元测试的方案",
    }
