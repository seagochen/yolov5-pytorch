# -*- coding: utf-8 -*-
"""
解卦相关的提示词
"""
from typing import List, Dict

SYSTEM_PROMPT = """你是一位精通周易的解卦大师，拥有深厚的易经知识和丰富的解卦经验。
请根据用户的问题和所得卦象，给出详细、有洞察力的解读。

解卦时请遵循以下结构：
1. 【卦象概述】简要介绍本卦的基本含义
2. 【针对问题的解读】结合用户的具体问题分析本卦的启示
3. 【变爻分析】如有变爻，解释变爻的特殊意义
4. 【变卦趋势】分析变卦代表的发展趋势
5. 【综合建议】给出实际可行的建议

注意事项：
- 用通俗易懂的现代语言解释古文
- 解读要贴合用户的实际问题
- 避免过于绝对的断言，保持谦逊的态度
- 适当引用原文增加权威性"""


def format_changing_lines(changing_lines: List[Dict]) -> str:
    """格式化变爻信息"""
    if not changing_lines:
        return "无变爻"

    lines = []
    position_names = ['初', '二', '三', '四', '五', '上']
    for cl in changing_lines:
        pos = cl['position']
        pos_name = position_names[pos - 1] if pos <= 6 else f"第{pos}"
        lines.append(f"{pos_name}爻：{cl['yaoci']}")

    return '\n'.join(lines)


def get_interpretation_prompt(
    question: str,
    ben_gua: Dict,
    bian_gua: Dict,
    changing_lines: List[Dict]
) -> str:
    """生成解卦提示词"""
    return f"""请为我解读以下卦象：

【求问】{question}

【本卦】{ben_gua['name']}
卦辞：{ben_gua['description']}
卦象：
{ben_gua['image']}

【变卦】{bian_gua['name']}
卦辞：{bian_gua['description']}
卦象：
{bian_gua['image']}

【变爻】
{format_changing_lines(changing_lines)}

请根据以上信息，结合我的问题进行详细解读。"""


def get_summary_prompt(interpretation: str) -> str:
    """生成总结提示词"""
    return f"请用一两句话总结以下解卦内容的核心建议：\n\n{interpretation}"
