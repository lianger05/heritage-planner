"""古建信息 CRUD 端点"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.heritage import Heritage
from app.schemas.heritage import (
    HeritageCreate,
    HeritageUpdate,
    HeritageResponse,
    HeritageListResponse,
)

router = APIRouter()


@router.get("/", response_model=HeritageListResponse, summary="获取古建列表")
async def list_heritage(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    province: str | None = None,
    city: str | None = None,
    protection_level: str | None = None,
    building_type: str | None = None,
    keyword: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    query = select(Heritage)
    count_query = select(func.count(Heritage.id))

    if province:
        query = query.where(Heritage.province == province)
        count_query = count_query.where(Heritage.province == province)
    if city:
        query = query.where(Heritage.city == city)
        count_query = count_query.where(Heritage.city == city)
    if protection_level:
        query = query.where(Heritage.protection_level == protection_level)
        count_query = count_query.where(Heritage.protection_level == protection_level)
    if building_type:
        query = query.where(Heritage.building_type == building_type)
        count_query = count_query.where(Heritage.building_type == building_type)
    if keyword:
        query = query.where(Heritage.name.ilike(f"%{keyword}%"))
        count_query = count_query.where(Heritage.name.ilike(f"%{keyword}%"))

    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    query = query.offset((page - 1) * page_size).limit(page_size).order_by(Heritage.id)
    result = await db.execute(query)
    items = result.scalars().all()

    return HeritageListResponse(items=items, total=total, page=page, page_size=page_size)


@router.get("/{heritage_id}", response_model=HeritageResponse, summary="获取古建详情")
async def get_heritage(heritage_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Heritage).where(Heritage.id == heritage_id))
    heritage = result.scalar_one_or_none()
    if not heritage:
        raise HTTPException(status_code=404, detail="古建信息未找到")
    return heritage


@router.post("/", response_model=HeritageResponse, summary="创建古建信息")
async def create_heritage(
    data: HeritageCreate,
    db: AsyncSession = Depends(get_db),
):
    heritage_data = data.model_dump()
    heritage = Heritage(**heritage_data)
    db.add(heritage)
    await db.flush()
    await db.refresh(heritage)
    return heritage


@router.put("/{heritage_id}", response_model=HeritageResponse, summary="更新古建信息")
async def update_heritage(
    heritage_id: int,
    data: HeritageUpdate,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Heritage).where(Heritage.id == heritage_id))
    heritage = result.scalar_one_or_none()
    if not heritage:
        raise HTTPException(status_code=404, detail="古建信息未找到")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(heritage, key, value)

    await db.flush()
    await db.refresh(heritage)
    return heritage


@router.delete("/{heritage_id}", summary="删除古建信息")
async def delete_heritage(heritage_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Heritage).where(Heritage.id == heritage_id))
    heritage = result.scalar_one_or_none()
    if not heritage:
        raise HTTPException(status_code=404, detail="古建信息未找到")
    await db.delete(heritage)
    return {"message": "删除成功"}
