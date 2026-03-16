# -*- coding: utf-8 -*-
from openai import OpenAI

from .settings import settings


_client_instance = None


def get_ai_client() -> OpenAI:
    """
    获取 AI 客户端实例（连接 kimi-code 代理）
    :return: OpenAI 兼容客户端
    """
    global _client_instance

    if _client_instance is not None:
        return _client_instance

    _client_instance = OpenAI(
        base_url=settings.ai_base_url,
        api_key=settings.ai_api_key,
    )

    return _client_instance
