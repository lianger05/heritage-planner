"""古建遗产 ORM 模型 - SQLite兼容版（去掉PostGIS依赖）"""

from datetime import datetime
from enum import StrEnum

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    JSON,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ProtectionLevel(StrEnum):
    """文物保护等级"""
    NATIONAL = "全国重点文物保护单位"
    PROVINCIAL = "省级文物保护单位"
    MUNICIPAL = "市级文物保护单位"
    DISTRICT = "区县级文物保护单位"
    UNLISTED = "未定级"


class BuildingType(StrEnum):
    """建筑类型"""
    PALACE = "宫殿"
    TEMPLE = "寺庙"
    RESIDENCE = "民居"
    GARDEN = "园林"
    TOWER = "楼阁"
    BRIDGE = "桥梁"
    WALL = "城墙"
    TOMB = "陵墓"
    ACADEMY = "书院"
    WORKSHOP = "作坊"
    OTHER = "其他"


class Heritage(Base):
    """古建遗产信息表"""
    __tablename__ = "heritage"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False, comment="古建名称")
    alias: Mapped[str | None] = mapped_column(String(200), comment="别名")

    # 时代与类型
    dynasty: Mapped[str | None] = mapped_column(String(50), comment="朝代/年代")
    year_start: Mapped[int | None] = mapped_column(Integer, comment="始建年份")
    year_end: Mapped[int | None] = mapped_column(Integer, comment="终止/重修年份")
    building_type: Mapped[str] = mapped_column(
        String(20), nullable=False, comment="建筑类型"
    )
    style: Mapped[str | None] = mapped_column(String(100), comment="建筑风格/流派")

    # 保护等级
    protection_level: Mapped[str] = mapped_column(
        String(30), nullable=False, comment="保护等级"
    )
    listed_date: Mapped[datetime | None] = mapped_column(DateTime, comment="公布日期")
    listing_batch: Mapped[str | None] = mapped_column(String(20), comment="批次")

    # 地理位置（用 Float 字段替代 PostGIS Geometry）
    province: Mapped[str] = mapped_column(String(50), nullable=False, comment="省份")
    city: Mapped[str] = mapped_column(String(50), nullable=False, comment="城市")
    district: Mapped[str | None] = mapped_column(String(50), comment="区县")
    address: Mapped[str | None] = mapped_column(String(300), comment="详细地址")
    longitude: Mapped[float | None] = mapped_column(Float, comment="经度")
    latitude: Mapped[float | None] = mapped_column(Float, comment="纬度")

    # 现状描述
    description: Mapped[str | None] = mapped_column(Text, comment="现状描述")
    current_status: Mapped[str | None] = mapped_column(String(200), comment="保存状态")
    area_size: Mapped[float | None] = mapped_column(Float, comment="占地面积(平方米)")
    is_open: Mapped[bool | None] = mapped_column(Boolean, comment="是否对外开放")
    ticket_price: Mapped[float | None] = mapped_column(Float, comment="门票价格(元)")

    # 经济数据
    annual_visitors: Mapped[int | None] = mapped_column(Integer, comment="年游客量")
    nearby_poi_count: Mapped[int | None] = mapped_column(Integer, comment="周边POI数量")
    nearby_hotel_count: Mapped[int | None] = mapped_column(Integer, comment="周边酒店数量")

    # 元数据
    extra_data: Mapped[dict | None] = mapped_column(JSON, comment="扩展数据")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, comment="创建时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间"
    )

    # 关系
    plans: Mapped[list["Plan"]] = relationship(
        back_populates="heritage", cascade="all, delete-orphan"
    )


class Plan(Base):
    """规划方案表"""
    __tablename__ = "plan"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    heritage_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("heritage.id"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False, comment="方案标题")
    description: Mapped[str | None] = mapped_column(Text, comment="方案描述")

    # 方案内容 (JSON存储，方便LLM结构化输出)
    protection_measures: Mapped[dict | None] = mapped_column(JSON, comment="保护措施")
    tourism_routes: Mapped[dict | None] = mapped_column(JSON, comment="旅游动线")
    business_layout: Mapped[dict | None] = mapped_column(JSON, comment="业态布局")
    economic_estimation: Mapped[dict | None] = mapped_column(JSON, comment="经济估算")
    constraints_check: Mapped[dict | None] = mapped_column(JSON, comment="约束校验结果")

    # 方案元数据
    llm_model: Mapped[str | None] = mapped_column(String(50), comment="生成使用的LLM")
    llm_tokens: Mapped[int | None] = mapped_column(Integer, comment="消耗token数")
    generation_time: Mapped[float | None] = mapped_column(Float, comment="生成耗时(秒)")
    version: Mapped[int] = mapped_column(Integer, default=1, comment="版本号")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, comment="是否当前版本")

    # 评价
    quality_score: Mapped[float | None] = mapped_column(Float, comment="质量评分(0-100)")
    feedback: Mapped[str | None] = mapped_column(Text, comment="用户反馈")

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, comment="创建时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间"
    )

    # 关系
    heritage: Mapped["Heritage"] = relationship(back_populates="plans")
    chat_sessions: Mapped[list["ChatSession"]] = relationship(
        back_populates="plan", cascade="all, delete-orphan"
    )


class ChatSession(Base):
    """对话会话表"""
    __tablename__ = "chat_session"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    plan_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("plan.id"), nullable=False
    )
    session_id: Mapped[str] = mapped_column(
        String(36), nullable=False, unique=True, comment="会话UUID"
    )
    messages: Mapped[dict | None] = mapped_column(JSON, comment="对话消息列表")
    context: Mapped[dict | None] = mapped_column(JSON, comment="上下文信息")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, comment="创建时间"
    )

    plan: Mapped["Plan"] = relationship(back_populates="chat_sessions")


class Regulation(Base):
    """法规条例表"""
    __tablename__ = "regulation"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(300), nullable=False, comment="法规标题")
    source: Mapped[str | None] = mapped_column(String(100), comment="来源机关")
    level: Mapped[str | None] = mapped_column(String(20), comment="法规层级(国家/省/市)")
    publish_date: Mapped[datetime | None] = mapped_column(DateTime, comment="发布日期")
    content: Mapped[str] = mapped_column(Text, nullable=False, comment="法规全文")
    summary: Mapped[str | None] = mapped_column(Text, comment="摘要")
    keywords: Mapped[list | None] = mapped_column(JSON, comment="关键词列表")
    protection_levels: Mapped[list | None] = mapped_column(
        JSON, comment="适用的保护等级"
    )
    is_constraint: Mapped[bool] = mapped_column(
        Boolean, default=True, comment="是否为硬约束"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, comment="创建时间"
    )
