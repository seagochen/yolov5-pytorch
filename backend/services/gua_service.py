# -*- coding: utf-8 -*-
"""
卦象服务 - 处理卦象数据加载和计算
"""
import json
import random
from typing import Dict, List, Optional
from functools import lru_cache

from ..config import settings


class GuaService:
    """卦象服务类"""

    def __init__(self):
        self._gua_dict: Optional[Dict] = None

    @property
    def gua_dict(self) -> Dict:
        """懒加载卦象数据"""
        if self._gua_dict is None:
            self._gua_dict = self._load_gua_data()
        return self._gua_dict

    def _load_gua_data(self) -> Dict:
        """加载所有卦象数据"""
        gua_dict = {}
        gua_folder = settings.GUA_DATA_DIR

        if not gua_folder.exists():
            raise FileNotFoundError(f"卦象数据目录不存在: {gua_folder}")

        for file in gua_folder.iterdir():
            if file.suffix == '.json':
                with open(file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    gua_dict.update(data)

        return gua_dict

    def yao_to_binary(self, yao_list: List[int], changing: bool = False) -> str:
        """
        把爻转换成二进制字符串
        :param yao_list: 6个数字（6,7,8,9）
        :param changing: 是否计算变卦（6变阳, 9变阴）
        :return: 6位二进制字符串
        """
        binary_str = ""
        for yao in yao_list:
            if changing:
                if yao == 6:
                    binary_str += "1"
                elif yao == 9:
                    binary_str += "0"
                elif yao == 7:
                    binary_str += "1"
                elif yao == 8:
                    binary_str += "0"
            else:
                if yao in [6, 8]:
                    binary_str += "0"
                elif yao in [7, 9]:
                    binary_str += "1"

        return binary_str[::-1]

    def get_gua_info(self, binary: str) -> Dict:
        """获取卦象信息"""
        if binary in self.gua_dict:
            info = self.gua_dict[binary].copy()
            info['binary'] = binary
            return info
        else:
            return {
                'name': '未知卦象',
                'binary': binary,
                'description': f'二进制表示 {binary} 未找到对应卦象信息。',
                'yaoci': []
            }

    def generate_gua_image(self, binary: str) -> str:
        """生成卦象图案"""
        lines = []
        for bit in binary:
            if bit == '1':
                lines.append('———————')
            else:
                lines.append('——   ——')
        return '\n'.join(lines)

    def calculate_divination(self, numbers: List[int]) -> Dict:
        """
        计算占卜结果
        :param numbers: 6个数字（6-9）
        :return: 包含本卦、变卦和变爻的字典
        """
        # 计算本卦和变卦的二进制
        ben_gua_binary = self.yao_to_binary(numbers)
        bian_gua_binary = self.yao_to_binary(numbers, changing=True)

        # 获取卦象信息
        ben_gua_info = self.get_gua_info(ben_gua_binary)
        bian_gua_info = self.get_gua_info(bian_gua_binary)

        # 生成卦象图
        ben_gua_image = self.generate_gua_image(ben_gua_binary)
        bian_gua_image = self.generate_gua_image(bian_gua_binary)

        # 获取变爻
        ben_yaoci = ben_gua_info.get('yaoci', ['无爻辞'] * 6)
        changing_lines = []
        for idx, num in enumerate(numbers):
            if num in [6, 9]:
                changing_lines.append({
                    'position': idx + 1,
                    'yaoci': ben_yaoci[idx] if idx < len(ben_yaoci) else '无爻辞'
                })

        return {
            'ben_gua': {
                'name': ben_gua_info.get('name', '未知'),
                'binary': ben_gua_binary,
                'description': ben_gua_info.get('description', ''),
                'image': ben_gua_image,
                'yaoci': ben_yaoci
            },
            'bian_gua': {
                'name': bian_gua_info.get('name', '未知'),
                'binary': bian_gua_binary,
                'description': bian_gua_info.get('description', ''),
                'image': bian_gua_image,
                'yaoci': bian_gua_info.get('yaoci', [])
            },
            'changing_lines': changing_lines,
            'numbers': numbers
        }

    def generate_random_numbers(self) -> List[int]:
        """
        随机生成6个数字（模拟摇卦）
        每个数字为 6, 7, 8, 9
        概率分布模拟三枚硬币投掷：
        - 6 (老阴): 1/8
        - 7 (少阳): 3/8
        - 8 (少阴): 3/8
        - 9 (老阳): 1/8
        """
        numbers = []
        for _ in range(6):
            # 模拟三枚硬币投掷
            coins = [random.choice([2, 3]) for _ in range(3)]  # 2=反, 3=正
            total = sum(coins)
            numbers.append(total)
        return numbers

    def get_all_gua_list(self) -> List[Dict]:
        """获取所有64卦列表"""
        result = []
        for binary, info in sorted(self.gua_dict.items()):
            result.append({
                'binary': binary,
                'name': info.get('name', ''),
                'alternate_name': info.get('alternate_name', ''),
                'description': info.get('description', '')
            })
        return result

    def get_gua_by_binary(self, binary: str) -> Optional[Dict]:
        """根据二进制获取卦象"""
        if binary in self.gua_dict:
            info = self.gua_dict[binary]
            return {
                'binary': binary,
                'name': info.get('name', ''),
                'alternate_name': info.get('alternate_name', ''),
                'description': info.get('description', ''),
                'yaoci': info.get('yaoci', []),
                'image': self.generate_gua_image(binary)
            }
        return None


# 全局单例
gua_service = GuaService()
