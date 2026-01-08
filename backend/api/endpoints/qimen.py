# -*- coding: utf-8 -*-
"""
奇门遁甲相关 API 端点
"""
from fastapi import APIRouter, HTTPException
from core.models import (
    QimenRequest,
    QimenResponse,
    ErrorResponse
)
from utils.qimen import qimen_paipan
from datetime import datetime

router = APIRouter(prefix="/qimen", tags=["奇门遁甲"])


@router.post("/paipan", response_model=QimenResponse, summary="奇门遁甲排盘")
async def qimen_paipan_endpoint(request: QimenRequest):
    """
    根据时间进行奇门遁甲排盘

    Args:
        request: 包含年月日时分的请求

    Returns:
        奇门遁甲排盘结果，包含九宫信息、吉凶判断等
    """
    try:
        # 验证日期有效性
        try:
            datetime(request.year, request.month, request.day, request.hour, request.minute)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"无效的日期时间: {str(e)}")

        # 进行排盘
        result = qimen_paipan(
            request.year,
            request.month,
            request.day,
            request.hour,
            request.minute
        )

        return result

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"排盘时发生错误: {str(e)}")


@router.get("/", summary="奇门遁甲系统信息")
async def qimen_info():
    """
    获取奇门遁甲系统的基本信息
    """
    return {
        "name": "奇门遁甲排盘系统",
        "version": "1.0.0",
        "description": "提供奇门遁甲时家奇门排盘及吉凶判断功能",
        "features": [
            "自动计算节气和局数",
            "阴阳遁自动判断",
            "九宫排盘（天盘、地盘、人盘、神盘）",
            "三奇六仪配置",
            "八门分析",
            "九星判断",
            "八神配置",
            "吉凶格局自动判断",
            "整体形势分析"
        ],
        "elements": {
            "三奇": ["乙（日奇）", "丙（月奇）", "丁（星奇）"],
            "六仪": ["戊", "己", "庚", "辛", "壬", "癸"],
            "八门": ["休门", "生门", "伤门", "杜门", "景门", "死门", "惊门", "开门"],
            "九星": ["天蓬星", "天芮星", "天冲星", "天辅星", "天禽星", "天心星", "天柱星", "天任星", "天英星"],
            "八神": ["值符", "腾蛇", "太阴", "六合", "白虎", "玄武", "九地", "九天"]
        },
        "endpoints": {
            "paipan": "/api/qimen/paipan - 进行奇门遁甲排盘"
        }
    }
