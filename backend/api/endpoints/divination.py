# -*- coding: utf-8 -*-
"""
占卜相关 API 端点
"""
from fastapi import APIRouter, HTTPException

from core.models import (
    DivinationRequest,
    DivinationResponse,
    RandomDivinationRequest,
    GuaInfo,
    ChangingLine
)
from services import gua_service

router = APIRouter()


@router.post("/calculate", response_model=DivinationResponse)
async def calculate_gua(request: DivinationRequest):
    """
    根据输入的6个数字（6-9）计算卦象
    """
    # 验证数字范围
    if not all(num in [6, 7, 8, 9] for num in request.numbers):
        raise HTTPException(
            status_code=400,
            detail="每个数字必须在 6-9 范围内"
        )

    try:
        result = gua_service.calculate_divination(request.numbers)

        return DivinationResponse(
            ben_gua=GuaInfo(
                name=result['ben_gua']['name'],
                binary=result['ben_gua']['binary'],
                description=result['ben_gua']['description'],
                image=result['ben_gua']['image'],
                symbol=result['ben_gua'].get('symbol'),
                yaoci=result['ben_gua'].get('yaoci')
            ),
            bian_gua=GuaInfo(
                name=result['bian_gua']['name'],
                binary=result['bian_gua']['binary'],
                description=result['bian_gua']['description'],
                image=result['bian_gua']['image'],
                symbol=result['bian_gua'].get('symbol'),
                yaoci=result['bian_gua'].get('yaoci')
            ),
            changing_lines=[
                ChangingLine(position=cl['position'], yaoci=cl['yaoci'])
                for cl in result['changing_lines']
            ],
            question=request.question,
            numbers=result['numbers']
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/random", response_model=DivinationResponse)
async def random_divination(request: RandomDivinationRequest):
    """
    随机摇卦（模拟三枚硬币投掷）
    """
    try:
        numbers = gua_service.generate_random_numbers()
        result = gua_service.calculate_divination(numbers)

        return DivinationResponse(
            ben_gua=GuaInfo(
                name=result['ben_gua']['name'],
                binary=result['ben_gua']['binary'],
                description=result['ben_gua']['description'],
                image=result['ben_gua']['image'],
                symbol=result['ben_gua'].get('symbol'),
                yaoci=result['ben_gua'].get('yaoci')
            ),
            bian_gua=GuaInfo(
                name=result['bian_gua']['name'],
                binary=result['bian_gua']['binary'],
                description=result['bian_gua']['description'],
                image=result['bian_gua']['image'],
                symbol=result['bian_gua'].get('symbol'),
                yaoci=result['bian_gua'].get('yaoci')
            ),
            changing_lines=[
                ChangingLine(position=cl['position'], yaoci=cl['yaoci'])
                for cl in result['changing_lines']
            ],
            question=request.question,
            numbers=result['numbers']
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/gua/{binary}")
async def get_gua_by_binary(binary: str):
    """
    根据二进制编码获取卦象信息
    """
    if len(binary) != 6 or not all(c in '01' for c in binary):
        raise HTTPException(
            status_code=400,
            detail="二进制编码必须是6位0/1字符串"
        )

    result = gua_service.get_gua_by_binary(binary)
    if result is None:
        raise HTTPException(status_code=404, detail="未找到该卦象")

    return result


@router.get("/gua")
async def list_all_gua():
    """
    获取所有64卦列表
    """
    return gua_service.get_all_gua_list()
