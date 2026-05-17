"""法规检索端点"""

from fastapi import APIRouter

from app.schemas.heritage import RegulationSearchRequest, RegulationResponse
from app.services.rag_service import RAGService

router = APIRouter()


@router.post("/search", response_model=list[RegulationResponse], summary="检索相关法规")
async def search_regulations(data: RegulationSearchRequest):
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
async def check_plan_constraints(heritage_info: dict, plan_content: dict):
    """校验规划方案是否违反法规约束"""
    rag = RAGService()
    result = await rag.check_constraints(heritage_info, plan_content)
    return result
