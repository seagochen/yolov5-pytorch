# -*- coding: utf-8 -*-
import sys
from utils.load_gua import load_gua
from utils.query_gua import get_gua_info, generate_gua_image
from utils.toss_gua import yao_to_binary

def get_gua_from_numbers(numbers):
    """
    根据用户输入的六个数字（6-9），计算对应的本卦和变卦，并仅包含变爻的爻辞
    :param numbers: List[int] 长度为6的列表，包含6-9
    :return: dict 包含本卦、变卦的信息，及变爻爻辞
    """
    if len(numbers) != 6 or not all(num in [6, 7, 8, 9] for num in numbers):
        raise ValueError("输入的数字必须是6个，并且范围只能是 6, 7, 8, 9")
    
    # 读取卦象数据
    gua_dict = load_gua("data/gua")

    # 转换为二进制卦象
    ben_gua_binary = yao_to_binary(numbers)
    bian_gua_binary = yao_to_binary(numbers, changing=True)

    # 获取卦象信息
    ben_gua_info = get_gua_info(ben_gua_binary, gua_dict)
    bian_gua_info = get_gua_info(bian_gua_binary, gua_dict)

    # 生成卦象图
    ben_gua_image = generate_gua_image(ben_gua_binary)
    bian_gua_image = generate_gua_image(bian_gua_binary)

    # 确保爻辞存在，否则给默认值
    ben_yaoci = ben_gua_info.get("yaoci", ["无爻辞"] * 6)

    # 记录变爻（6、9 变）
    changing_lines = [(idx + 1, ben_yaoci[idx]) for idx, num in enumerate(numbers) if num in [6, 9]]

    # 返回结果
    return {
        "ben_gua": {
            "name": ben_gua_info["name"],
            "binary": ben_gua_binary,
            "description": ben_gua_info["description"],
            "image": ben_gua_image,
        },
        "bian_gua": {
            "name": bian_gua_info["name"],
            "binary": bian_gua_binary,
            "description": bian_gua_info["description"],
            "image": bian_gua_image,
        },
        "changing_lines": changing_lines  # 仅包含变爻的爻辞
    }

if __name__ == "__main__":
    # 获取命令行参数
    if len(sys.argv) != 2:
        print("用法: python3 quest_numbers.py <6个数字，例如 698696>")
        sys.exit(1)

    # 解析输入的数字字符串
    input_str = sys.argv[1]
    
    if len(input_str) != 6 or not all(c in "6789" for c in input_str):
        print("错误：输入的数字必须是6位，并且范围只能是 6, 7, 8, 9")
        sys.exit(1)

    # 转换为数字列表
    numbers = [int(c) for c in input_str]

    try:
        gua_result = get_gua_from_numbers(numbers)
        
        # 输出本卦信息
        print("\n=== 本卦 ===")
        print(f"名称：{gua_result['ben_gua']['name']}（{gua_result['ben_gua']['binary']}）")
        print(f"卦辞：{gua_result['ben_gua']['description']}")
        print(f"卦象：\n{gua_result['ben_gua']['image']}")

        # 输出变卦信息
        print("\n=== 变卦 ===")
        print(f"名称：{gua_result['bian_gua']['name']}（{gua_result['bian_gua']['binary']}）")
        print(f"卦辞：{gua_result['bian_gua']['description']}")
        print(f"卦象：\n{gua_result['bian_gua']['image']}")

        # 输出变爻信息（仅变动爻的爻辞）
        if gua_result["changing_lines"]:
            print("\n=== 变爻爻辞 ===")
            for line, yaoci in gua_result["changing_lines"]:
                print(f"第 {line} 爻：{yaoci}")

    except ValueError as e:
        print(f"输入错误：{e}")
