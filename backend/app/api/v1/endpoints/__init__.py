"""健康检查端点"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/health", summary="健康检查")
async def health_check():
    return {"status": "ok", "service": "heritage-planner-backend"}
