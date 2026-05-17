"""古建遗产 Pydantic Schema"""

from datetime import datetime

from pydantic import BaseModel, Field


# ========== Heritage ==========

class HeritageBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200, description="古建名称")
    alias: str | None = Field(None, max_length=200, description="别名")
    dynasty: str | None = Field(None, max_length=50, description="朝代/年代")
    year_start: int | None = Field(None, description="始建年份")
    year_end: int | None = Field(None, description="终止/重修年份")
    building_type: str = Field(..., description="建筑类型")
    style: str | None = Field(None, max_length=100, description="建筑风格/流派")
    protection_level: str = Field(..., description="保护等级")
    province: str = Field(..., max_length=50, description="省份")
    city: str = Field(..., max_length=50, description="城市")
    district: str | None = Field(None, max_length=50, description="区县")
    address: str | None = Field(None, max_length=300, description="详细地址")
    longitude: float | None = Field(None, description="经度")
    latitude: float | None = Field(None, description="纬度")
    description: str | None = Field(None, description="现状描述")
    current_status: str | None = Field(None, description="保存状态")
    area_size: float | None = Field(None, description="占地面积(平方米)")
    is_open: bool | None = Field(None, description="是否对外开放")
    ticket_price: float | None = Field(None, description="门票价格(元)")
    annual_visitors: int | None = Field(None, description="年游客量")


class HeritageCreate(HeritageBase):
    pass


class HeritageUpdate(BaseModel):
    name: str | None = None
    alias: str | None = None
    dynasty: str | None = None
    building_type: str | None = None
    protection_level: str | None = None
    description: str | None = None
    current_status: str | None = None
    area_size: float | None = None
    is_open: bool | None = None
    ticket_price: float | None = None
    annual_visitors: int | None = None


class HeritageResponse(HeritageBase):
    id: int
    listed_date: datetime | None = None
    nearby_poi_count: int | None = None
    nearby_hotel_count: int | None = None
    extra_data: dict | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class HeritageListResponse(BaseModel):
    items: list[HeritageResponse]
    total: int
    page: int
    page_size: int


# ========== Plan ==========

class PlanCreate(BaseModel):
    heritage_id: int = Field(..., description="关联古建ID")
    title: str = Field(..., min_length=1, max_length=200, description="方案标题")
    description: str | None = Field(None, description="方案需求描述")
    requirements: dict | None = Field(None, description="额外需求参数")


class PlanResponse(BaseModel):
    id: int
    heritage_id: int
    title: str
    description: str | None = None
    protection_measures: dict | None = None
    tourism_routes: dict | None = None
    business_layout: dict | None = None
    economic_estimation: dict | None = None
    constraints_check: dict | None = None
    llm_model: str | None = None
    generation_time: float | None = None
    version: int = 1
    quality_score: float | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ========== Chat ==========

class ChatMessage(BaseModel):
    role: str = Field(..., description="角色: user / assistant / system")
    content: str = Field(..., description="消息内容")
    timestamp: datetime | None = None


class ChatRequest(BaseModel):
    plan_id: int = Field(..., description="关联方案ID")
    message: str = Field(..., min_length=1, description="用户消息")
    session_id: str | None = Field(None, description="会话ID，首次对话可不传")


class ChatResponse(BaseModel):
    session_id: str
    reply: str = Field(..., description="AI回复")
    updated_plan: dict | None = Field(None, description="更新后的方案片段")
    references: list[dict] | None = Field(None, description="引用的法规/案例")


# ========== Report ==========

class ReportRequest(BaseModel):
    plan_id: int = Field(..., description="方案ID")
    format: str = Field("pdf", description="导出格式: pdf / docx / markdown")
    template: str | None = Field(None, description="报告模板名称")


class ReportResponse(BaseModel):
    download_url: str = Field(..., description="下载链接")
    filename: str = Field(..., description="文件名")
    format: str = Field(..., description="文件格式")


# ========== Map ==========

class MapMarker(BaseModel):
    id: int
    name: str
    longitude: float
    latitude: float
    protection_level: str
    building_type: str
    is_open: bool | None = None


class MapBounds(BaseModel):
    southwest_lng: float
    southwest_lat: float
    northeast_lng: float
    northeast_lat: float


class MapSearchRequest(BaseModel):
    bounds: MapBounds | None = None
    province: str | None = None
    city: str | None = None
    protection_level: str | None = None
    building_type: str | None = None
    keyword: str | None = None


# ========== Regulation ==========

class RegulationSearchRequest(BaseModel):
    query: str = Field(..., min_length=1, description="检索查询")
    protection_level: str | None = Field(None, description="按保护等级过滤")
    top_k: int = Field(5, ge=1, le=20, description="返回数量")


class RegulationResponse(BaseModel):
    id: int
    title: str
    source: str | None = None
    level: str | None = None
    content: str
    summary: str | None = None
    relevance_score: float | None = None

    model_config = {"from_attributes": True}
