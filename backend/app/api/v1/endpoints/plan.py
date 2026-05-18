"""规划方案端点"""

import json
import time

from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.rate_limit import limiter
from app.models.heritage import Heritage, Plan
from app.schemas.heritage import PlanCreate, PlanResponse
from app.services.plan_service import PlanGeneratorService

router = APIRouter()


@router.post("/generate", response_model=PlanResponse, summary="AI生成规划方案")
@limiter.limit("5/minute")
async def generate_plan(
    request: Request,
    data: PlanCreate,
    db: AsyncSession = Depends(get_db),
):
    """根据古建信息和用户需求，AI自动生成保护性开发方案"""
    # 获取古建信息
    result = await db.execute(select(Heritage).where(Heritage.id == data.heritage_id))
    heritage = result.scalar_one_or_none()
    if not heritage:
        raise HTTPException(status_code=404, detail="古建信息未找到")

    heritage_info = {
        "id": heritage.id,
        "name": heritage.name,
        "dynasty": heritage.dynasty,
        "building_type": heritage.building_type,
        "protection_level": heritage.protection_level,
        "style": heritage.style,
        "province": heritage.province,
        "city": heritage.city,
        "district": heritage.district,
        "address": heritage.address,
        "description": heritage.description,
        "current_status": heritage.current_status,
        "area_size": heritage.area_size,
        "is_open": heritage.is_open,
        "ticket_price": heritage.ticket_price,
        "annual_visitors": heritage.annual_visitors,
    }

    # 调用AI生成方案
    generator = PlanGeneratorService()
    plan_data = await generator.generate_plan(heritage_info, data.requirements)

    # 存储方案
    meta = plan_data.pop("_meta", {})
    plan = Plan(
        heritage_id=data.heritage_id,
        title=data.title,
        description=data.description,
        protection_measures=plan_data.get("protection_measures"),
        tourism_routes=plan_data.get("tourism_routes"),
        business_layout=plan_data.get("business_layout"),
        economic_estimation=plan_data.get("economic_estimation"),
        constraints_check=plan_data.get("constraints_check"),
        llm_model=meta.get("llm_model"),
        generation_time=meta.get("generation_time"),
    )
    db.add(plan)
    await db.flush()
    await db.refresh(plan)

    return plan


@router.get("/{plan_id}", response_model=PlanResponse, summary="获取方案详情")
async def get_plan(plan_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Plan).where(Plan.id == plan_id))
    plan = result.scalar_one_or_none()
    if not plan:
        raise HTTPException(status_code=404, detail="方案未找到")
    return plan


@router.get("/heritage/{heritage_id}", response_model=list[PlanResponse], summary="获取古建的所有方案")
async def list_plans_by_heritage(
    heritage_id: int,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Plan)
        .where(Plan.heritage_id == heritage_id, Plan.is_active == True)
        .order_by(Plan.version.desc())
    )
    return result.scalars().all()


class RefineRequest(BaseModel):
    """方案修改请求"""
    feedback: str = Field(..., min_length=1, max_length=2000, description="用户反馈")


@router.post("/{plan_id}/refine", response_model=PlanResponse, summary="AI修改方案")
@limiter.limit("10/minute")
async def refine_plan(
    request: Request,
    plan_id: int,
    data: RefineRequest,
    db: AsyncSession = Depends(get_db),
):
    """根据用户反馈修改方案"""
    feedback = data.feedback
    result = await db.execute(select(Plan).where(Plan.id == plan_id))
    plan = result.scalar_one_or_none()
    if not plan:
        raise HTTPException(status_code=404, detail="方案未找到")

    # 获取古建信息
    heritage_result = await db.execute(select(Heritage).where(Heritage.id == plan.heritage_id))
    heritage = heritage_result.scalar_one_or_none()
    heritage_info = {"name": heritage.name, "protection_level": heritage.protection_level} if heritage else {}

    current_plan = {
        "protection_measures": plan.protection_measures,
        "tourism_routes": plan.tourism_routes,
        "business_layout": plan.business_layout,
        "economic_estimation": plan.economic_estimation,
    }

    generator = PlanGeneratorService()
    updated_data = await generator.refine_plan(current_plan, feedback, heritage_info)

    # 创建新版本
    new_plan = Plan(
        heritage_id=plan.heritage_id,
        title=plan.title,
        description=f"基于用户反馈修改: {feedback[:100]}",
        protection_measures=updated_data.get("protection_measures"),
        tourism_routes=updated_data.get("tourism_routes"),
        business_layout=updated_data.get("business_layout"),
        economic_estimation=updated_data.get("economic_estimation"),
        constraints_check=updated_data.get("constraints_check"),
        version=plan.version + 1,
        llm_model=generator.llm.model,
    )

    # 旧版本设为非活跃
    plan.is_active = False

    db.add(new_plan)
    await db.flush()
    await db.refresh(new_plan)

    return new_plan
