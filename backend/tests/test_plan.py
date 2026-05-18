"""规划方案端点测试"""

import pytest
from httpx import AsyncClient


class TestPlanGenerate:
    """POST /api/v1/plan/generate - AI 生成规划方案"""

    @pytest.mark.asyncio
    async def test_generate_requires_heritage(self, async_client: AsyncClient):
        """不存在的古建 ID 应返回 404"""
        response = await async_client.post(
            "/api/v1/plan/generate",
            json={
                "heritage_id": 99999,
                "title": "不存在的古建方案",
            },
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_generate_missing_title(self, async_client: AsyncClient):
        """缺少 title 字段应返回 422"""
        response = await async_client.post(
            "/api/v1/plan/generate",
            json={"heritage_id": 1},
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_generate_fallback_when_no_llm(self, async_client: AsyncClient):
        """LLM 不可用时应返回模板方案（fallback）"""
        response = await async_client.post(
            "/api/v1/plan/generate",
            json={
                "heritage_id": 1,
                "title": "铁塔保护性开发方案",
                "description": "测试 fallback 模式",
            },
        )
        # 测试环境未配置 LLM API Key，应返回 200 + fallback 方案
        assert response.status_code == 200
        data = response.json()
        # fallback 方案应有 protection_measures 字段
        assert "protection_measures" in data or "fallback" in data


class TestPlanDetail:
    """GET /api/v1/plan/{id} - 获取方案详情"""

    @pytest.mark.asyncio
    async def test_get_nonexistent_plan(self, async_client: AsyncClient):
        """获取不存在的方案应返回 404"""
        response = await async_client.get("/api/v1/plan/99999")
        assert response.status_code == 404


class TestPlanByHeritage:
    """GET /api/v1/plan/heritage/{heritage_id} - 获取古建的所有方案"""

    @pytest.mark.asyncio
    async def test_list_empty(self, async_client: AsyncClient):
        """没有方案的 heritage_id 返回空列表"""
        response = await async_client.get("/api/v1/plan/heritage/99999")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert data == []


class TestPlanRefine:
    """POST /api/v1/plan/{id}/refine - 修改方案"""

    @pytest.mark.asyncio
    async def test_refine_nonexistent_plan(self, async_client: AsyncClient):
        """修改不存在的方案应返回 404"""
        response = await async_client.post(
            "/api/v1/plan/99999/refine",
            json={"feedback": "调整旅游路线"},
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_refine_empty_feedback(self, async_client: AsyncClient):
        """空反馈应返回 422"""
        response = await async_client.post(
            "/api/v1/plan/1/refine",
            json={"feedback": ""},
        )
        assert response.status_code == 422
