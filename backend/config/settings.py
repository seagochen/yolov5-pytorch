# -*- coding: utf-8 -*-
import os
import json
from pathlib import Path
from typing import Optional


class Settings:
    """全局配置管理"""

    # 目录配置
    BASE_DIR = Path(__file__).resolve().parent.parent.parent  # IChing 根目录
    BACKEND_DIR = BASE_DIR / "backend"
    DATA_DIR = BASE_DIR / "data"
    GUA_DATA_DIR = DATA_DIR / "gua"

    # 配置文件
    API_KEY_FILE = BASE_DIR / "gemini.json"

    # 默认模型配置
    DEFAULT_MODEL = "gemini-2.0-flash"
    DEFAULT_GENERATION_CONFIG = {
        "temperature": 0.7,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 2000
    }

    # CORS 配置
    CORS_ORIGINS = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]

    @property
    def api_key(self) -> Optional[str]:
        """从 gemini.json 加载 API Key"""
        if self.API_KEY_FILE.exists():
            try:
                with open(self.API_KEY_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('api_key')
            except (json.JSONDecodeError, IOError):
                return None
        return None

    @property
    def model_name(self) -> str:
        """获取模型名称"""
        return self.DEFAULT_MODEL

    @property
    def generation_config(self) -> dict:
        """获取生成配置"""
        return self.DEFAULT_GENERATION_CONFIG.copy()


# 全局单例
settings = Settings()
