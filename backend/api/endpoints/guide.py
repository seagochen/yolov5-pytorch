# -*- coding: utf-8 -*-
"""
指南数据 API 端点
"""
from fastapi import APIRouter, HTTPException
from pathlib import Path
import json

router = APIRouter(prefix="/guide", tags=["指南"])

# 数据文件路径 (项目根目录/data/)
DATA_DIR = Path(__file__).parent.parent.parent.parent / "data"
QIMEN_GUIDE_FILE = DATA_DIR / "qimen_guide.json"
BAZI_GUIDE_FILE = DATA_DIR / "bazi_guide.json"


@router.get("/qimen", summary="获取奇门遁甲使用指南")
async def get_qimen_guide():
    """
    获取奇门遁甲使用指南数据

    Returns:
        奇门遁甲指南的完整内容
    """
    try:
        with open(QIMEN_GUIDE_FILE, 'r', encoding='utf-8') as f:
            guide_data = json.load(f)
        return guide_data
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="奇门遁甲指南文件未找到")
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="奇门遁甲指南文件格式错误")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"读取奇门遁甲指南时发生错误: {str(e)}")


@router.get("/bazi", summary="获取八字排盘使用指南")
async def get_bazi_guide():
    """
    获取八字排盘使用指南数据

    Returns:
        八字排盘指南的完整内容
    """
    try:
        with open(BAZI_GUIDE_FILE, 'r', encoding='utf-8') as f:
            guide_data = json.load(f)
        return guide_data
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="八字指南文件未找到")
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="八字指南文件格式错误")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"读取八字指南时发生错误: {str(e)}")


@router.get("/", summary="获取所有指南")
async def get_all_guides():
    """
    获取所有功能的使用指南

    Returns:
        包含所有指南的字典
    """
    try:
        qimen_guide = await get_qimen_guide()
        bazi_guide = await get_bazi_guide()

        return {
            "qimen": qimen_guide,
            "bazi": bazi_guide
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"读取指南时发生错误: {str(e)}")
