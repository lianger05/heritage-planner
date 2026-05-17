"""地图服务端点 - SQLite兼容版（去掉PostGIS依赖）"""

from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.heritage import Heritage
from app.schemas.heritage import MapMarker, MapSearchRequest

router = APIRouter()


@router.post("/markers", response_model=list[MapMarker], summary="获取地图标记点")
async def get_map_markers(
    data: MapSearchRequest,
    db: AsyncSession = Depends(get_db),
):
    """根据筛选条件获取古建地图标记"""
    query = select(Heritage).where(Heritage.longitude.isnot(None), Heritage.latitude.isnot(None))

    # 属性过滤
    if data.province:
        query = query.where(Heritage.province == data.province)
    if data.city:
        query = query.where(Heritage.city == data.city)
    if data.protection_level:
        query = query.where(Heritage.protection_level == data.protection_level)
    if data.building_type:
        query = query.where(Heritage.building_type == data.building_type)
    if data.keyword:
        query = query.where(Heritage.name.ilike(f"%{data.keyword}%"))

    # 空间范围过滤（纯Python计算，替代PostGIS）
    result = await db.execute(query.limit(500))
    heritages = result.scalars().all()

    markers = []
    for h in heritages:
        # 空间范围过滤
        if data.bounds and h.longitude is not None and h.latitude is not None:
            if not (
                data.bounds.southwest_lng <= h.longitude <= data.bounds.northeast_lng
                and data.bounds.southwest_lat <= h.latitude <= data.bounds.northeast_lat
            ):
                continue

        markers.append(MapMarker(
            id=h.id,
            name=h.name,
            longitude=h.longitude,
            latitude=h.latitude,
            protection_level=h.protection_level,
            building_type=h.building_type,
            is_open=h.is_open,
        ))

    return markers


@router.get("/stats", summary="获取地图统计信息")
async def get_map_stats(db: AsyncSession = Depends(get_db)):
    """获取古建分布统计"""
    # 按省份统计
    province_stats = await db.execute(
        select(Heritage.province, func.count(Heritage.id))
        .group_by(Heritage.province)
        .order_by(func.count(Heritage.id).desc())
    )

    # 按保护等级统计
    level_stats = await db.execute(
        select(Heritage.protection_level, func.count(Heritage.id))
        .group_by(Heritage.protection_level)
    )

    # 按建筑类型统计
    type_stats = await db.execute(
        select(Heritage.building_type, func.count(Heritage.id))
        .group_by(Heritage.building_type)
    )

    return {
        "by_province": [{"province": r[0], "count": r[1]} for r in province_stats],
        "by_protection_level": [{"level": r[0], "count": r[1]} for r in level_stats],
        "by_building_type": [{"type": r[0], "count": r[1]} for r in type_stats],
        "total": await db.scalar(select(func.count(Heritage.id))),
    }
