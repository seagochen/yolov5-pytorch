# -*- coding: utf-8 -*-
"""
API 路由聚合
"""
from fastapi import APIRouter

from .endpoints import divination, interpretation

# 创建主路由
api_router = APIRouter(prefix="/api")

# 注册子路由
api_router.include_router(divination.router, prefix="/divination", tags=["divination"])
api_router.include_router(interpretation.router, prefix="/interpretation", tags=["interpretation"])
