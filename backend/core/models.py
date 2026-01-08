# -*- coding: utf-8 -*-
"""
Pydantic 数据模型定义
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict


# ============ 卦象相关模型 ============

class GuaInfo(BaseModel):
    """卦象信息"""
    name: str
    binary: str
    description: str
    image: str
    symbol: Optional[str] = None
    yaoci: Optional[List[str]] = None


class ChangingLine(BaseModel):
    """变爻信息"""
    position: int
    yaoci: str


# ============ 占卜请求/响应模型 ============

class DivinationRequest(BaseModel):
    """占卜请求"""
    numbers: List[int] = Field(..., min_length=6, max_length=6, description="6个数字(6-9)")
    question: Optional[str] = Field(None, description="占卜问题")


class DivinationResponse(BaseModel):
    """占卜结果"""
    ben_gua: GuaInfo
    bian_gua: GuaInfo
    changing_lines: List[ChangingLine]
    question: Optional[str] = None
    numbers: Optional[List[int]] = None


class RandomDivinationRequest(BaseModel):
    """随机占卜请求"""
    question: Optional[str] = Field(None, description="占卜问题")


# ============ 解卦请求/响应模型 ============

class InterpretationRequest(BaseModel):
    """解卦请求"""
    question: str = Field(..., description="占卜问题")
    ben_gua: GuaInfo
    bian_gua: GuaInfo
    changing_lines: List[ChangingLine]


class InterpretationResponse(BaseModel):
    """解卦结果"""
    interpretation: str
    summary: str


# ============ 八字相关模型 ============

class PillarInfo(BaseModel):
    """单柱信息（天干地支）"""
    gan: str = Field(..., description="天干")
    zhi: str = Field(..., description="地支")


class LunarInfo(BaseModel):
    """农历信息"""
    year: int
    month: int
    day: int
    is_leap: bool
    gan_zhi_year: str
    sheng_xiao: str
    formatted: str


class SolarInfo(BaseModel):
    """公历信息"""
    year: int
    month: int
    day: int
    hour: int
    minute: int
    formatted: str


class BaziRequest(BaseModel):
    """八字计算请求"""
    year: int = Field(..., ge=1900, le=2100, description="出生年份")
    month: int = Field(..., ge=1, le=12, description="出生月份")
    day: int = Field(..., ge=1, le=31, description="出生日期")
    hour: int = Field(..., ge=0, le=23, description="出生小时")
    minute: int = Field(0, ge=0, le=59, description="出生分钟")


class ShenshaDetail(BaseModel):
    """神煞详细信息"""
    name: str
    description: str
    type: str  # ji(吉), xiong(凶), zhong(中性)


class ShenshaInfo(BaseModel):
    """神煞信息"""
    all: List[str]
    ji: List[str]
    xiong: List[str]
    details: List[ShenshaDetail]
    count: int


class BaziResponse(BaseModel):
    """八字计算结果"""
    year_pillar: str
    month_pillar: str
    day_pillar: str
    hour_pillar: str
    pillars: Dict[str, PillarInfo]
    wu_xing: Dict[str, str]
    wu_xing_count: Dict[str, int]
    yin_yang: Dict[str, str]
    bazi_string: str
    lunar: LunarInfo
    solar: SolarInfo
    shensha: ShenshaInfo


class LunarConversionRequest(BaseModel):
    """公历转农历请求"""
    year: int = Field(..., ge=1900, le=2100, description="公历年份")
    month: int = Field(..., ge=1, le=12, description="公历月份")
    day: int = Field(..., ge=1, le=31, description="公历日期")


# ============ 奇门遁甲相关模型 ============

class GongInfo(BaseModel):
    """宫位信息"""
    gong_name: str
    ba_gua: str
    di_pan: str
    tian_pan: str
    ba_men: str
    jiu_xing: str
    ba_shen: str
    ji_xiong: str
    ji_score: int
    xiong_score: int
    notes: List[str]


class QimenZongPing(BaseModel):
    """奇门遁甲总评"""
    overall: str
    summary: str
    ji_count: int
    xiong_count: int
    best_gong: int
    best_gong_name: str
    worst_gong: int
    worst_gong_name: str
    advice: str


class QimenRequest(BaseModel):
    """奇门遁甲请求"""
    year: int = Field(..., ge=1900, le=2100, description="年份")
    month: int = Field(..., ge=1, le=12, description="月份")
    day: int = Field(..., ge=1, le=31, description="日期")
    hour: int = Field(..., ge=0, le=23, description="小时")
    minute: int = Field(0, ge=0, le=59, description="分钟")


class QimenResponse(BaseModel):
    """奇门遁甲排盘结果"""
    date_time: str
    term: str
    yuan: str
    dun_type: str
    ju_number: int
    zhi_fu_gong: int
    jiu_gong: Dict[int, GongInfo]
    zong_ping: QimenZongPing


# ============ 通用模型 ============

class ErrorResponse(BaseModel):
    """错误响应"""
    detail: str
    code: Optional[str] = None
