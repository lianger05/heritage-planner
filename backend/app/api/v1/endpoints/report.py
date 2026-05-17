"""报告导出端点"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.heritage import Heritage, Plan
from app.schemas.heritage import ReportRequest, ReportResponse

router = APIRouter()


@router.post("/generate", response_model=ReportResponse, summary="导出规划方案报告")
async def generate_report(
    data: ReportRequest,
    db: AsyncSession = Depends(get_db),
):
    """将规划方案导出为PDF/DOCX/Markdown报告"""
    # 获取方案
    result = await db.execute(select(Plan).where(Plan.id == data.plan_id))
    plan = result.scalar_one_or_none()
    if not plan:
        raise HTTPException(status_code=404, detail="方案未找到")

    # 获取古建信息
    heritage_result = await db.execute(select(Heritage).where(Heritage.id == plan.heritage_id))
    heritage = heritage_result.scalar_one_or_none()

    # TODO: 实际报告生成逻辑（Jinja2模板 + WeasyPrint / python-docx）
    # 当前返回占位响应
    filename = f"plan_{plan.id}_{heritage.name if heritage else 'unknown'}"

    if data.format == "markdown":
        content = _generate_markdown(plan, heritage)
        # TODO: 存储到MinIO
        return ReportResponse(
            download_url=f"/api/v1/report/download/{filename}.md",
            filename=f"{filename}.md",
            format="markdown",
        )
    elif data.format == "docx":
        return ReportResponse(
            download_url=f"/api/v1/report/download/{filename}.docx",
            filename=f"{filename}.docx",
            format="docx",
        )
    else:
        return ReportResponse(
            download_url=f"/api/v1/report/download/{filename}.pdf",
            filename=f"{filename}.pdf",
            format="pdf",
        )


def _generate_markdown(plan: Plan, heritage: Heritage | None) -> str:
    """生成Markdown格式报告"""
    h = heritage
    lines = [
        f"# {h.name if h else '古建'}保护性开发方案",
        "",
        f"## 基本信息",
        f"- 名称：{h.name if h else '-'}",
        f"- 朝代：{h.dynasty if h else '-'}",
        f"- 保护等级：{h.protection_level if h else '-'}",
        f"- 建筑类型：{h.building_type if h else '-'}",
        f"- 所在地：{h.province if h else ''}{h.city if h else ''}{h.district if h else ''}",
        "",
        f"## 保护措施",
        str(plan.protection_measures or "暂无"),
        "",
        f"## 旅游动线规划",
        str(plan.tourism_routes or "暂无"),
        "",
        f"## 业态布局建议",
        str(plan.business_layout or "暂无"),
        "",
        f"## 经济估算",
        str(plan.economic_estimation or "暂无"),
        "",
        f"## 约束校验",
        str(plan.constraints_check or "暂无"),
        "",
        f"---",
        f"*本方案由AI生成，仅供参考。请务必经过专业规划师审核。*",
    ]
    return "\n".join(lines)
