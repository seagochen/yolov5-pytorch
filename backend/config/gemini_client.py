# -*- coding: utf-8 -*-
import google.generativeai as genai
from typing import Optional

from .settings import settings


_model_instance = None


def get_gemini_model(model_name: Optional[str] = None):
    """
    获取 Gemini 模型实例
    :param model_name: 模型名称，默认使用配置中的模型
    :return: GenerativeModel 实例
    """
    global _model_instance

    api_key = settings.api_key
    if not api_key:
        raise ValueError("Gemini API Key 未配置，请在项目根目录创建 gemini.json 文件")

    genai.configure(api_key=api_key)

    target_model = model_name or settings.model_name

    # 如果请求的是默认模型且已有缓存实例，直接返回
    if model_name is None and _model_instance is not None:
        return _model_instance

    model = genai.GenerativeModel(target_model)

    # 缓存默认模型实例
    if model_name is None:
        _model_instance = model

    return model
