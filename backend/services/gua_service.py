# -*- coding: utf-8 -*-
"""
卦象服务 - 处理卦象数据加载和计算
"""
import json
import random
from typing import Dict, List, Optional
from functools import lru_cache

from config import settings


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
            # 如果数据中没有symbol字段，生成Unicode符号
            if 'symbol' not in info:
                info['symbol'] = self.generate_gua_image(binary)
            return info
        else:
            return {
                'name': '未知卦象',
                'binary': binary,
                'description': f'二进制表示 {binary} 未找到对应卦象信息。',
                'yaoci': [],
                'symbol': '?'
            }

    def generate_gua_image(self, binary: str) -> str:
        """生成卦象 Unicode 符号

        使用64卦的Unicode符号（U+4DC0 到 U+4DFF）
        二进制从下到上对应爻的顺序，0=阴爻，1=阳爻
        """
        # 64卦映射表：binary -> Unicode字符
        # 卦序按照二进制值从000000到111111
        gua_unicode_map = {
            '000000': '䷁',  # 坤
            '000001': '䷗',  # 剥
            '000010': '䷆',  # 比
            '000011': '䷓',  # 观
            '000100': '䷏',  # 豫
            '000101': '䷂',  # 晋
            '000110': '䷇',  # 萃
            '000111': '䷒',  # 否
            '001000': '䷖',  # 谦
            '001001': '䷎',  # 艮
            '001010': '䷳',  # 蹇
            '001011': '䷴',  # 渐
            '001100': '䷢',  # 小过
            '001101': '䷸',  # 旅
            '001110': '䷻',  # 咸
            '001111': '䷋',  # 遁
            '010000': '䷭',  # 师
            '010001': '䷦',  # 蒙
            '010010': '䷜',  # 坎
            '010011': '䷮',  # 涣
            '010100': '䷟',  # 解
            '010101': '䷿',  # 未济
            '010110': '䷬',  # 困
            '010111': '䷤',  # 讼
            '011000': '䷨',  # 升
            '011001': '䷳',  # 蹇
            '011010': '䷵',  # 坎
            '011011': '䷯',  # 井
            '011100': '䷹',  # 巽
            '011101': '䷰',  # 鼎
            '011110': '䷱',  # 恒
            '011111': '䷡',  # 大过
            '100000': '䷗',  # 复
            '100001': '䷐',  # 颐
            '100010': '䷫',  # 屯
            '100011': '䷾',  # 益
            '100100': '䷲',  # 震
            '100101': '䷴',  # 噬嗑
            '100110': '䷧',  # 随
            '100111': '䷙',  # 无妄
            '101000': '䷤',  # 明夷
            '101001': '䷷',  # 贲
            '101010': '䷕',  # 既济
            '101011': '䷣',  # 家人
            '101100': '䷶',  # 丰
            '101101': '䷰',  # 离
            '101110': '䷩',  # 革
            '101111': '䷚',  # 同人
            '110000': '䷗',  # 临
            '110001': '䷙',  # 损
            '110010': '䷺',  # 节
            '110011': '䷼',  # 中孚
            '110100': '䷳',  # 归妹
            '110101': '䷥',  # 睽
            '110110': '䷾',  # 兑
            '110111': '䷪',  # 履
            '111000': '䷋',  # 泰
            '111001': '䷓',  # 大畜
            '111010': '䷿',  # 需
            '111011': '䷄',  # 小畜
            '111100': '䷐',  # 大壮
            '111101': '䷡',  # 大有
            '111110': '䷬',  # 夬
            '111111': '䷀',  # 乾
        }

        return gua_unicode_map.get(binary, '?')

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

        # 获取卦象 Unicode 符号（优先使用数据中的symbol字段）
        ben_gua_image = ben_gua_info.get('symbol', self.generate_gua_image(ben_gua_binary))
        bian_gua_image = bian_gua_info.get('symbol', self.generate_gua_image(bian_gua_binary))

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
                'image': info.get('symbol', self.generate_gua_image(binary))
            }
        return None


# 全局单例
gua_service = GuaService()
