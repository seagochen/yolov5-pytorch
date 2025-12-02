# -*- coding: utf-8 -*-
"""
Pydantic 数据模型定义
"""
from pydantic import BaseModel, Field
from typing import List, Optional


# ============ 卦象相关模型 ============

class GuaInfo(BaseModel):
    """卦象信息"""
    name: str
    binary: str
    description: str
    image: str
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


# ============ 通用模型 ============

class ErrorResponse(BaseModel):
    """错误响应"""
    detail: str
    code: Optional[str] = None
