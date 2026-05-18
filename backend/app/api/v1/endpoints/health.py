"""健康检查端点"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/health", summary="健康检查")
async def health_check():
    """服务健康状态检查，用于部署探针和监控"""
    return {
        "status": "ok",
        "service": "heritage-planner-backend",
        "version": "0.1.0",
    }
