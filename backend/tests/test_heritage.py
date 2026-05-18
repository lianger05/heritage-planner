"""古建遗产 CRUD 端点测试"""

import pytest
from httpx import AsyncClient


class TestHeritageList:
    """GET /api/v1/heritage/ - 获取古建列表"""

    @pytest.mark.asyncio
    async def test_list_default(self, async_client: AsyncClient):
        """默认分页获取古建列表"""
        response = await async_client.get("/api/v1/heritage/")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "page_size" in data
        assert isinstance(data["items"], list)
        assert data["page"] == 1
        assert data["page_size"] == 20

    @pytest.mark.asyncio
    async def test_list_with_pagination(self, async_client: AsyncClient):
        """带分页参数获取列表"""
        response = await async_client.get("/api/v1/heritage/?page=1&page_size=5")
        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 1
        assert data["page_size"] == 5

    @pytest.mark.asyncio
    async def test_list_filter_by_province(self, async_client: AsyncClient):
        """按省份筛选"""
        response = await async_client.get("/api/v1/heritage/?province=河南")
        assert response.status_code == 200
        data = response.json()
        for item in data["items"]:
            assert item["province"] == "河南"

    @pytest.mark.asyncio
    async def test_list_filter_by_protection_level(self, async_client: AsyncClient):
        """按保护等级筛选"""
        response = await async_client.get(
            "/api/v1/heritage/?protection_level=全国重点文物保护单位"
        )
        assert response.status_code == 200
        data = response.json()
        for item in data["items"]:
            assert item["protection_level"] == "全国重点文物保护单位"

    @pytest.mark.asyncio
    async def test_list_keyword_search(self, async_client: AsyncClient):
        """关键词搜索"""
        response = await async_client.get("/api/v1/heritage/?keyword=铁塔")
        assert response.status_code == 200
        data = response.json()
        # 应该至少找到"铁塔"
        names = [item["name"] for item in data["items"]]
        assert any("铁塔" in name for name in names)


class TestHeritageDetail:
    """GET /api/v1/heritage/{id} - 获取古建详情"""

    @pytest.mark.asyncio
    async def test_get_existing(self, async_client: AsyncClient):
        """获取存在的古建详情"""
        response = await async_client.get("/api/v1/heritage/1")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert "name" in data
        assert "dynasty" in data
        assert "protection_level" in data

    @pytest.mark.asyncio
    async def test_get_nonexistent(self, async_client: AsyncClient):
        """获取不存在的古建应返回 404"""
        response = await async_client.get("/api/v1/heritage/99999")
        assert response.status_code == 404


class TestHeritageCreate:
    """POST /api/v1/heritage/ - 创建古建"""

    @pytest.mark.asyncio
    async def test_create_valid(self, async_client: AsyncClient, sample_heritage_data):
        """创建合法的古建"""
        response = await async_client.post(
            "/api/v1/heritage/",
            json=sample_heritage_data,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == sample_heritage_data["name"]
        assert data["dynasty"] == sample_heritage_data["dynasty"]
        assert "id" in data

    @pytest.mark.asyncio
    async def test_create_missing_required(self, async_client: AsyncClient):
        """缺少必填字段应返回 422"""
        response = await async_client.post(
            "/api/v1/heritage/",
            json={"name": "缺少字段"},
        )
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data


class TestHeritageEdgeCases:
    """边界条件测试"""

    @pytest.mark.asyncio
    async def test_empty_keyword(self, async_client: AsyncClient):
        """空关键词搜索"""
        response = await async_client.get("/api/v1/heritage/?keyword=")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_large_page_number(self, async_client: AsyncClient):
        """大页码请求"""
        response = await async_client.get("/api/v1/heritage/?page=1000&page_size=20")
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []  # 无数据

    @pytest.mark.asyncio
    async def test_invalid_page_params(self, async_client: AsyncClient):
        """无效分页参数"""
        response = await async_client.get("/api/v1/heritage/?page=-1&page_size=0")
        # 应该返回 422（Pydantic 验证失败）或 200（默认值降级）
        assert response.status_code in (200, 422)
