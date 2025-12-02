# -*- coding: utf-8 -*-
"""
解卦相关 API 端点
"""
from fastapi import APIRouter, HTTPException

from ...core.models import InterpretationRequest, InterpretationResponse
from ...services import gemini_service

router = APIRouter()


@router.post("/analyze", response_model=InterpretationResponse)
async def analyze_gua(request: InterpretationRequest):
    """
    使用 AI 解读卦象
    """
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="问题不能为空")

    try:
        result = await gemini_service.interpret_gua(
            question=request.question,
            ben_gua={
                'name': request.ben_gua.name,
                'description': request.ben_gua.description,
                'image': request.ben_gua.image
            },
            bian_gua={
                'name': request.bian_gua.name,
                'description': request.bian_gua.description,
                'image': request.bian_gua.image
            },
            changing_lines=[
                {'position': cl.position, 'yaoci': cl.yaoci}
                for cl in request.changing_lines
            ]
        )

        return InterpretationResponse(
            interpretation=result['interpretation'],
            summary=result['summary']
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI 解卦失败: {str(e)}")
