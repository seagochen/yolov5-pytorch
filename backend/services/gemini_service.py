# -*- coding: utf-8 -*-
"""
Gemini AI 服务 - 处理 AI 解卦
"""
import google.generativeai as genai
from typing import Dict, List, Optional

from config import settings, get_gemini_model
from prompts import SYSTEM_PROMPT, get_interpretation_prompt, get_summary_prompt


class GeminiService:
    """Gemini AI 服务类"""

    async def interpret_gua(
        self,
        question: str,
        ben_gua: Dict,
        bian_gua: Dict,
        changing_lines: List[Dict]
    ) -> Dict[str, str]:
        """
        使用 Gemini AI 解读卦象
        """
        model = get_gemini_model()
        generation_config = settings.generation_config

        # 生成解卦提示词
        user_prompt = get_interpretation_prompt(question, ben_gua, bian_gua, changing_lines)

        try:
            # 调用 Gemini API
            response = model.generate_content(
                [SYSTEM_PROMPT, user_prompt],
                generation_config=genai.types.GenerationConfig(
                    temperature=generation_config['temperature'],
                    max_output_tokens=generation_config['max_output_tokens'],
                )
            )

            interpretation = response.text

            # 生成简短总结
            summary_prompt = get_summary_prompt(interpretation)
            summary_response = model.generate_content(
                summary_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3,
                    max_output_tokens=200,
                )
            )
            summary = summary_response.text

            return {
                'interpretation': interpretation,
                'summary': summary
            }

        except Exception as e:
            raise Exception(f"Gemini API 调用失败: {str(e)}")

    def generate_response(
        self,
        prompt: str,
        system_instruction: Optional[str] = None
    ) -> str:
        """
        通用生成响应
        """
        model = get_gemini_model()
        generation_config = settings.generation_config

        try:
            if system_instruction:
                response = model.generate_content(
                    [system_instruction, prompt],
                    generation_config=genai.types.GenerationConfig(
                        temperature=generation_config['temperature'],
                        max_output_tokens=generation_config['max_output_tokens'],
                    )
                )
            else:
                response = model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=generation_config['temperature'],
                        max_output_tokens=generation_config['max_output_tokens'],
                    )
                )

            return response.text

        except Exception as e:
            raise Exception(f"Gemini API 调用失败: {str(e)}")


# 全局单例
gemini_service = GeminiService()
