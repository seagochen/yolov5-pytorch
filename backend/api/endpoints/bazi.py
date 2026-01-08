# -*- coding: utf-8 -*-
"""
八字相关 API 端点
"""
from fastapi import APIRouter, HTTPException
from core.models import (
    BaziRequest,
    BaziResponse,
    LunarConversionRequest,
    LunarInfo,
    ErrorResponse
)
from utils.bazi_calculator import calculate_bazi
from utils.lunar_calendar import solar_to_lunar
from datetime import datetime

router = APIRouter(prefix="/bazi", tags=["八字"])


@router.post("/calculate", response_model=BaziResponse, summary="计算八字")
async def calculate_bazi_endpoint(request: BaziRequest):
    """
    根据出生日期时间计算八字四柱

    Args:
        request: 包含出生年月日时分的请求

    Returns:
        八字计算结果，包含四柱、五行、阴阳等信息
    """
    try:
        # 验证日期有效性
        try:
            datetime(request.year, request.month, request.day, request.hour, request.minute)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"无效的日期时间: {str(e)}")

        # 计算八字
        result = calculate_bazi(
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
        raise HTTPException(status_code=500, detail=f"计算八字时发生错误: {str(e)}")


@router.post("/lunar-conversion", response_model=LunarInfo, summary="公历转农历")
async def lunar_conversion_endpoint(request: LunarConversionRequest):
    """
    将公历日期转换为农历日期

    Args:
        request: 包含公历年月日的请求

    Returns:
        农历日期信息
    """
    try:
        # 验证日期有效性
        try:
            datetime(request.year, request.month, request.day)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"无效的日期: {str(e)}")

        # 转换为农历
        result = solar_to_lunar(request.year, request.month, request.day)

        return result

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"转换农历时发生错误: {str(e)}")


@router.get("/", summary="八字系统信息")
async def bazi_info():
    """
    获取八字系统的基本信息
    """
    return {
        "name": "八字计算系统",
        "version": "1.0.0",
        "description": "提供公历转农历、八字四柱计算等功能",
        "features": [
            "公历转农历",
            "计算年柱（以立春为界）",
            "计算月柱（以节气为界）",
            "计算日柱",
            "计算时柱",
            "五行统计",
            "阴阳属性"
        ],
        "endpoints": {
            "calculate": "/api/bazi/calculate - 计算八字四柱",
            "lunar_conversion": "/api/bazi/lunar-conversion - 公历转农历"
        }
    }
