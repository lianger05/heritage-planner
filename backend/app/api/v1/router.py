"""API v1 路由汇总"""

from fastapi import APIRouter

from app.api.v1.endpoints import heritage, plan, regulation, report, chat, map as map_endpoint
from app.api.v1.endpoints import health as health_endpoint

api_router = APIRouter()

api_router.include_router(health_endpoint.router, tags=["系统"])
api_router.include_router(heritage.router, prefix="/heritage", tags=["古建信息"])
api_router.include_router(plan.router, prefix="/plan", tags=["规划方案"])
api_router.include_router(regulation.router, prefix="/regulation", tags=["法规检索"])
api_router.include_router(report.router, prefix="/report", tags=["报告导出"])
api_router.include_router(chat.router, prefix="/chat", tags=["AI对话"])
api_router.include_router(map_endpoint.router, prefix="/map", tags=["地图服务"])
