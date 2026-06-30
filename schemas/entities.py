"""结构化实体定义 - 用于旅行攻略信息提取"""

from typing import List, Optional
from pydantic import BaseModel, Field


class OpeningHours(BaseModel):
    """营业/开放时间"""
    weekdays: Optional[str] = Field(None, description="工作日时间，如：09:00-21:00")
    weekends: Optional[str] = Field(None, description="周末时间，如：10:00-22:00")
    holidays: Optional[str] = Field(None, description="节假日时间")
    note: Optional[str] = Field(None, description="时间说明")


class Pricing(BaseModel):
    """价格信息"""
    adult: Optional[str] = Field(None, description="成人价")
    child: Optional[str] = Field(None, description="儿童价")
    student: Optional[str] = Field(None, description="学生价")
    senior: Optional[str] = Field(None, description="老人价")
    note: Optional[str] = Field(None, description="价格说明")


class Location(BaseModel):
    """位置信息"""
    address: Optional[str] = Field(None, description="详细地址")
    address_local: Optional[str] = Field(None, description="当地语言地址")
    district: Optional[str] = Field(None, description="区域")
    landmark: Optional[str] = Field(None, description="地标")
    coordinates: Optional[str] = Field(None, description="坐标")


class Contact(BaseModel):
    """联系方式"""
    phone: Optional[str] = Field(None, description="电话")
    website: Optional[str] = Field(None, description="网站")
    email: Optional[str] = Field(None, description="邮箱")


class Attraction(BaseModel):
    """景点实体"""
    name: str = Field(description="景点名称")
    name_local: Optional[str] = Field(None, description="当地语言名称")
    category: Optional[str] = Field(None, description="类别：自然景观/历史古迹/娱乐设施/博物馆等")
    location: Optional[Location] = Field(None, description="位置")
    ticket: Optional[Pricing] = Field(None, description="门票价格")
    hours: Optional[OpeningHours] = Field(None, description="开放时间")
    duration: Optional[str] = Field(None, description="建议游览时长")
    highlights: List[str] = Field(default_factory=list, description="亮点/必看点")
    tips: List[str] = Field(default_factory=list, description="游览贴士")
    photos: List[str] = Field(default_factory=list, description="图片URL")
    source_urls: List[str] = Field(default_factory=list, description="来源URL")
    source_ids: List[int] = Field(default_factory=list, description="来源编号")
    confidence: float = Field(0.5, ge=0.0, le=1.0, description="置信度0-1")


class Restaurant(BaseModel):
    """餐厅实体"""
    name: str = Field(description="餐厅名称")
    name_local: Optional[str] = Field(None, description="当地语言名称")
    cuisine: Optional[str] = Field(None, description="菜系：韩餐/中餐/日料/西餐等")
    location: Optional[Location] = Field(None, description="位置")
    price_range: Optional[str] = Field(None, description="价格区间，如：人均100-150元")
    signature_dishes: List[str] = Field(default_factory=list, description="招牌菜")
    hours: Optional[OpeningHours] = Field(None, description="营业时间")
    rating: Optional[float] = Field(None, description="评分0-5")
    reservation: Optional[str] = Field(None, description="预约信息")
    tips: List[str] = Field(default_factory=list, description="用餐贴士")
    photos: List[str] = Field(default_factory=list, description="图片URL")
    source_urls: List[str] = Field(default_factory=list, description="来源URL")
    source_ids: List[int] = Field(default_factory=list, description="来源编号")
    confidence: float = Field(0.5, ge=0.0, le=1.0, description="置信度0-1")


class Hotel(BaseModel):
    """酒店实体"""
    name: str = Field(description="酒店名称")
    hotel_type: Optional[str] = Field(None, description="类型：酒店/民宿/青旅等")
    location: Optional[Location] = Field(None, description="位置")
    price_range: Optional[str] = Field(None, description="价格区间")
    rating: Optional[float] = Field(None, description="评分0-5")
    amenities: List[str] = Field(default_factory=list, description="设施")
    rooms: List[str] = Field(default_factory=list, description="房型")
    breakfast: Optional[str] = Field(None, description="早餐信息")
    check_in: Optional[str] = Field(None, description="入住时间")
    check_out: Optional[str] = Field(None, description="退房时间")
    tips: List[str] = Field(default_factory=list, description="住宿贴士")
    photos: List[str] = Field(default_factory=list, description="图片URL")
    source_urls: List[str] = Field(default_factory=list, description="来源URL")
    source_ids: List[int] = Field(default_factory=list, description="来源编号")
    confidence: float = Field(0.5, ge=0.0, le=1.0, description="置信度0-1")


class Transportation(BaseModel):
    """交通信息"""
    type: str = Field(description="类型：机场交通/市内交通/城际交通")
    from_location: Optional[str] = Field(None, description="出发地")
    to_location: Optional[str] = Field(None, description="目的地")
    methods: List[dict] = Field(default_factory=list, description="交通方式列表")
    cost: Optional[str] = Field(None, description="费用")
    duration: Optional[str] = Field(None, description="时长")
    tips: List[str] = Field(default_factory=list, description="交通贴士")
    source_urls: List[str] = Field(default_factory=list, description="来源URL")
    source_ids: List[int] = Field(default_factory=list, description="来源编号")
    confidence: float = Field(0.5, ge=0.0, le=1.0, description="置信度0-1")


class TravelTip(BaseModel):
    """旅行贴士"""
    category: str = Field(description="类别：天气/支付/语言/安全/避坑等")
    content: str = Field(description="具体内容")
    importance: Optional[str] = Field(None, description="重要性：高/中/低")
    source_urls: List[str] = Field(default_factory=list, description="来源URL")
    source_ids: List[int] = Field(default_factory=list, description="来源编号")
    confidence: float = Field(0.5, ge=0.0, le=1.0, description="置信度0-1")


class ExtractedEntities(BaseModel):
    """提取的实体集合"""
    attractions: List[Attraction] = Field(default_factory=list, description="景点列表")
    restaurants: List[Restaurant] = Field(default_factory=list, description="餐厅列表")
    hotels: List[Hotel] = Field(default_factory=list, description="酒店列表")
    transportations: List[Transportation] = Field(default_factory=list, description="交通信息")
    tips: List[TravelTip] = Field(default_factory=list, description="旅行贴士")
    weather: Optional[str] = Field(None, description="天气信息")
    budget_estimate: Optional[str] = Field(None, description="预算预估")
    best_time: Optional[str] = Field(None, description="最佳旅行时间")
    extraction_metadata: dict = Field(default_factory=dict, description="提取元数据")