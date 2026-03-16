# -*- coding: utf-8 -*-
import yaml
from pathlib import Path


class Settings:
    """全局配置管理"""

    # 目录配置
    BASE_DIR = Path(__file__).resolve().parent.parent.parent  # IChing 根目录
    BACKEND_DIR = BASE_DIR / "backend"
    DATA_DIR = BASE_DIR / "data"
    GUA_DATA_DIR = DATA_DIR / "gua"
    CONFIG_FILE = BASE_DIR / "config.yaml"

    def __init__(self):
        self._config = self._load_config()

    def _load_config(self) -> dict:
        """从 config.yaml 加载配置"""
        if self.CONFIG_FILE.exists():
            with open(self.CONFIG_FILE, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        return {}

    @property
    def ai_base_url(self) -> str:
        return self._config.get('ai', {}).get('base_url', 'http://127.0.0.1:9000/v1')

    @property
    def ai_api_key(self) -> str:
        return self._config.get('ai', {}).get('api_key', 'not-needed')

    @property
    def model_name(self) -> str:
        return self._config.get('ai', {}).get('model', 'kimi-for-coding')

    @property
    def generation_config(self) -> dict:
        ai = self._config.get('ai', {})
        return {
            'temperature': ai.get('temperature', 0.7),
            'max_tokens': ai.get('max_tokens', 2000),
        }

    @property
    def cors_origins(self) -> list:
        return self._config.get('cors', {}).get('origins', [
            'http://localhost:3000',
            'http://localhost:5173',
            'http://127.0.0.1:3000',
            'http://127.0.0.1:5173',
        ])


# 全局单例
settings = Settings()
