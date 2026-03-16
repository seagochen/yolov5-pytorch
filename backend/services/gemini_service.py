# -*- coding: utf-8 -*-
"""
AI 服务 - 通过 kimi-code 代理处理 AI 解卦
"""
from typing import Dict, List, Optional

from config import settings, get_ai_client
from prompts import SYSTEM_PROMPT, get_interpretation_prompt, get_summary_prompt


class GeminiService:
    """AI 服务类（通过 kimi-code 代理）"""

    async def interpret_gua(
        self,
        question: str,
        ben_gua: Dict,
        bian_gua: Dict,
        changing_lines: List[Dict]
    ) -> Dict[str, str]:
        """
        使用 AI 解读卦象
        """
        client = get_ai_client()
        generation_config = settings.generation_config

        # 生成解卦提示词
        user_prompt = get_interpretation_prompt(question, ben_gua, bian_gua, changing_lines)

        try:
            # 调用 AI API
            response = client.chat.completions.create(
                model=settings.model_name,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=generation_config['temperature'],
                max_tokens=generation_config['max_tokens'],
            )

            interpretation = response.choices[0].message.content

            # 生成简短总结
            summary_prompt = get_summary_prompt(interpretation)
            summary_response = client.chat.completions.create(
                model=settings.model_name,
                messages=[
                    {"role": "user", "content": summary_prompt},
                ],
                temperature=0.3,
                max_tokens=200,
            )
            summary = summary_response.choices[0].message.content

            return {
                'interpretation': interpretation,
                'summary': summary
            }

        except Exception as e:
            raise Exception(f"AI API 调用失败: {str(e)}")

    def generate_response(
        self,
        prompt: str,
        system_instruction: Optional[str] = None
    ) -> str:
        """
        通用生成响应
        """
        client = get_ai_client()
        generation_config = settings.generation_config

        try:
            messages = []
            if system_instruction:
                messages.append({"role": "system", "content": system_instruction})
            messages.append({"role": "user", "content": prompt})

            response = client.chat.completions.create(
                model=settings.model_name,
                messages=messages,
                temperature=generation_config['temperature'],
                max_tokens=generation_config['max_tokens'],
            )

            return response.choices[0].message.content

        except Exception as e:
            raise Exception(f"AI API 调用失败: {str(e)}")


# 全局单例
gemini_service = GeminiService()
