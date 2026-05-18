"""法规检索端点"""

from pydantic import BaseModel, Field
from fastapi import APIRouter, Request

from app.core.rate_limit import limiter
from app.schemas.heritage import RegulationSearchRequest, RegulationResponse
from app.services.rag_service import RAGService

router = APIRouter()


class RegulationCheckRequest(BaseModel):
    """合规校验请求体"""
    heritage_info: dict = Field(..., description="古建信息字典")
    plan_content: dict = Field(..., description="方案内容字典")


@router.post("/search", response_model=list[RegulationResponse], summary="检索相关法规")
@limiter.limit("10/minute")
async def search_regulations(request: Request, data: RegulationSearchRequest):
    """基于语义检索相关文物保护法规"""
    rag = RAGService()
    results = await rag.search_regulations(
        query=data.query,
        protection_level=data.protection_level,
        top_k=data.top_k,
    )
    return [
        RegulationResponse(
            id=0,
            title=r["title"],
            source=r.get("source"),
            level=r.get("level"),
            content=r["content"],
            summary=r.get("content", "")[:200],
            relevance_score=r.get("relevance_score"),
        )
        for r in results
    ]


@router.post("/check", summary="校验方案合规性")
@limiter.limit("10/minute")
async def check_plan_constraints(request: Request, data: RegulationCheckRequest):
    """校验规划方案是否违反法规约束"""
    rag = RAGService()
    result = await rag.check_constraints(data.heritage_info, data.plan_content)
    return result
