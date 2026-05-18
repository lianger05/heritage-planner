"""报告导出端点"""

import json
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import PlainTextResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.rate_limit import limiter
from app.models.heritage import Heritage, Plan
from app.schemas.heritage import ReportRequest, ReportResponse

router = APIRouter()


@router.post("/generate", response_model=ReportResponse, summary="导出规划方案报告")
@limiter.limit("5/minute")
async def generate_report(
    request: Request,
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

    safe_name = heritage.name if heritage else "unknown"
    filename = f"plan_{plan.id}_{safe_name}"

    if data.format == "markdown":
        # Markdown 格式直接生成并返回下载 URL
        return ReportResponse(
            download_url=f"/api/v1/report/download/{plan.id}?format=markdown",
            filename=f"{filename}.md",
            format="markdown",
        )
    elif data.format == "docx":
        # DOCX 格式暂未实现，返回提示
        return ReportResponse(
            download_url=f"/api/v1/report/download/{plan.id}?format=markdown",
            filename=f"{filename}.md",
            format="markdown",  # fallback to markdown
        )
    else:
        # PDF 格式暂未实现，返回 Markdown fallback
        return ReportResponse(
            download_url=f"/api/v1/report/download/{plan.id}?format=markdown",
            filename=f"{filename}.md",
            format="markdown",  # fallback to markdown
        )


@router.get("/download/{plan_id}", summary="下载报告文件")
async def download_report(
    plan_id: int,
    format: str = "markdown",
    db: AsyncSession = Depends(get_db),
):
    """下载已生成的报告文件"""
    # 获取方案
    result = await db.execute(select(Plan).where(Plan.id == plan_id))
    plan = result.scalar_one_or_none()
    if not plan:
        raise HTTPException(status_code=404, detail="方案未找到")

    # 获取古建信息
    heritage_result = await db.execute(select(Heritage).where(Heritage.id == plan.heritage_id))
    heritage = heritage_result.scalar_one_or_none()

    if format == "markdown":
        content = _generate_markdown(plan, heritage)
        safe_name = heritage.name if heritage else "unknown"
        filename = f"plan_{plan.id}_{safe_name}.md"
        return PlainTextResponse(
            content=content,
            media_type="text/markdown; charset=utf-8",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
            },
        )
    else:
        raise HTTPException(
            status_code=400,
            detail=f"暂不支持 {format} 格式导出，请使用 markdown 格式",
        )


def _format_json_section(data: dict | list | None, indent: int = 0) -> str:
    """将 JSON 数据格式化为可读的 Markdown 文本"""
    if data is None:
        return "暂无"
    if isinstance(data, str):
        return data
    # 递归格式化字典
    if isinstance(data, dict):
        lines = []
        prefix = "  " * indent
        for key, value in data.items():
            key_display = key.replace("_", " ").title()
            if isinstance(value, (dict, list)) and value:
                lines.append(f"{prefix}- **{key_display}**:")
                lines.append(_format_json_section(value, indent + 1))
            elif isinstance(value, list) and value:
                lines.append(f"{prefix}- **{key_display}**:")
                for item in value:
                    if isinstance(item, dict):
                        lines.append(_format_json_section(item, indent + 1))
                    else:
                        lines.append(f"{prefix}  - {item}")
            else:
                lines.append(f"{prefix}- **{key_display}**: {value}")
        return "\n".join(lines)
    if isinstance(data, list):
        lines = []
        prefix = "  " * indent
        for item in data:
            if isinstance(item, dict):
                lines.append(_format_json_section(item, indent))
            else:
                lines.append(f"{prefix}- {item}")
        return "\n".join(lines)
    return str(data)


def _generate_markdown(plan: Plan, heritage: Heritage | None) -> str:
    """生成Markdown格式报告"""
    h = heritage
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    lines = [
        f"# {h.name if h else '古建'}保护性开发方案",
        "",
        f"> 生成时间：{now}  ",
        f"> AI 模型：{plan.llm_model or 'N/A'}  ",
        f"> 版本：v{plan.version}",
        "",
        "---",
        "",
        "## 一、基本信息",
        "",
        f"| 字段 | 值 |",
        f"|------|-----|",
        f"| 名称 | {h.name if h else '-'} |",
        f"| 朝代 | {h.dynasty if h else '-'} |",
        f"| 保护等级 | {h.protection_level if h else '-'} |",
        f"| 建筑类型 | {h.building_type if h else '-'} |",
        f"| 所在地 | {h.province if h else ''}{h.city if h else ''}{h.district if h else ''} |",
        f"| 地址 | {h.address if h else '-'} |",
        f"| 面积 | {h.area_size if h else '-'} m² |",
        f"| 现状 | {h.current_status if h else '-'} |",
        "",
        "---",
        "",
        "## 二、保护措施",
        "",
        _format_json_section(plan.protection_measures),
        "",
        "---",
        "",
        "## 三、旅游动线规划",
        "",
        _format_json_section(plan.tourism_routes),
        "",
        "---",
        "",
        "## 四、业态布局建议",
        "",
        _format_json_section(plan.business_layout),
        "",
        "---",
        "",
        "## 五、经济估算",
        "",
        _format_json_section(plan.economic_estimation),
        "",
        "---",
        "",
        "## 六、约束校验",
        "",
        _format_json_section(plan.constraints_check),
        "",
        "---",
        "",
        f"*本方案由 AI ({plan.llm_model or 'N/A'}) 生成，仅供参考。请务必经过专业规划师审核。*",
    ]
    return "\n".join(lines)
