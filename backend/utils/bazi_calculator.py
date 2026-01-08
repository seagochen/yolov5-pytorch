# -*- coding: utf-8 -*-
"""
八字计算工具
实现四柱（年柱、月柱、日柱、时柱）的计算
"""
from datetime import datetime, timedelta
from typing import Tuple, Dict
from .lunar_calendar import LunarCalendar
from .shensha import ShenshaCalculator


class BaziCalculator:
    """八字计算类"""

    # 天干
    TIAN_GAN = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']

    # 地支
    DI_ZHI = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']

    # 五行
    WU_XING = {
        '甲': '木', '乙': '木',
        '丙': '火', '丁': '火',
        '戊': '土', '己': '土',
        '庚': '金', '辛': '金',
        '壬': '水', '癸': '水',
        '子': '水', '丑': '土', '寅': '木', '卯': '木',
        '辰': '土', '巳': '火', '午': '火', '未': '土',
        '申': '金', '酉': '金', '戌': '土', '亥': '水'
    }

    # 阴阳
    YIN_YANG = {
        '甲': '阳', '乙': '阴',
        '丙': '阳', '丁': '阴',
        '戊': '阳', '己': '阴',
        '庚': '阳', '辛': '阴',
        '壬': '阳', '癸': '阴',
        '子': '阳', '丑': '阴', '寅': '阳', '卯': '阴',
        '辰': '阳', '巳': '阴', '午': '阳', '未': '阴',
        '申': '阳', '酉': '阴', '戌': '阳', '亥': '阴'
    }

    # 节气信息（简化版本，用于月柱计算）
    # 每年的节气大致时间（实际应根据精确天文计算）
    SOLAR_TERMS_BASE = [
        (2, 4),   # 立春
        (3, 6),   # 惊蛰
        (4, 5),   # 清明
        (5, 6),   # 立夏
        (6, 6),   # 芒种
        (7, 7),   # 小暑
        (8, 8),   # 立秋
        (9, 8),   # 白露
        (10, 8),  # 寒露
        (11, 7),  # 立冬
        (12, 7),  # 大雪
        (1, 6),   # 小寒
    ]

    # 月柱地支（从寅月开始，立春为界）
    MONTH_DI_ZHI = ['寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥', '子', '丑']

    # 时辰地支
    HOUR_DI_ZHI = {
        (23, 1): '子', (1, 3): '丑', (3, 5): '寅', (5, 7): '卯',
        (7, 9): '辰', (9, 11): '巳', (11, 13): '午', (13, 15): '未',
        (15, 17): '申', (17, 19): '酉', (19, 21): '戌', (21, 23): '亥'
    }

    @classmethod
    def _get_gan_index(cls, gan: str) -> int:
        """获取天干索引"""
        return cls.TIAN_GAN.index(gan)

    @classmethod
    def _get_zhi_index(cls, zhi: str) -> int:
        """获取地支索引"""
        return cls.DI_ZHI.index(zhi)

    @classmethod
    def calculate_year_pillar(cls, birth_date: datetime) -> Tuple[str, str]:
        """
        计算年柱（以立春为界）

        Args:
            birth_date: 出生日期时间

        Returns:
            (天干, 地支)
        """
        year = birth_date.year

        # 简化处理：如果在立春之前（2月4日之前），使用上一年
        # 实际应该精确计算立春时刻
        if birth_date.month < 2 or (birth_date.month == 2 and birth_date.day < 4):
            year -= 1

        # 计算干支
        # 1984年为甲子年
        gan_index = (year - 4) % 10
        zhi_index = (year - 4) % 12

        return cls.TIAN_GAN[gan_index], cls.DI_ZHI[zhi_index]

    @classmethod
    def calculate_month_pillar(cls, birth_date: datetime, year_gan: str) -> Tuple[str, str]:
        """
        计算月柱（以节气为界）

        Args:
            birth_date: 出生日期时间
            year_gan: 年干

        Returns:
            (天干, 地支)
        """
        # 简化处理：根据月份确定地支
        # 实际应该根据节气精确计算
        month = birth_date.month
        day = birth_date.day

        # 确定月柱地支（从立春开始算寅月）
        if month == 1:
            month_index = 10 if day < 6 else 11  # 小寒之前是子月，之后是丑月
        elif month == 2:
            month_index = 11 if day < 4 else 0  # 立春之前是丑月，之后是寅月
        else:
            # 其他月份简化处理
            month_index = month - 2

        month_zhi = cls.MONTH_DI_ZHI[month_index]

        # 月干计算：年干配月干
        # 甲己之年丙作首，乙庚之岁戊为头
        # 丙辛必定寻庚起，丁壬壬位顺行流
        # 若问戊癸何方发，甲寅之上好追求
        year_gan_index = cls._get_gan_index(year_gan)

        # 起始天干
        if year_gan in ['甲', '己']:
            start_gan_index = 2  # 丙
        elif year_gan in ['乙', '庚']:
            start_gan_index = 4  # 戊
        elif year_gan in ['丙', '辛']:
            start_gan_index = 6  # 庚
        elif year_gan in ['丁', '壬']:
            start_gan_index = 8  # 壬
        else:  # 戊、癸
            start_gan_index = 0  # 甲

        month_gan_index = (start_gan_index + month_index) % 10
        month_gan = cls.TIAN_GAN[month_gan_index]

        return month_gan, month_zhi

    @classmethod
    def calculate_day_pillar(cls, birth_date: datetime) -> Tuple[str, str]:
        """
        计算日柱

        Args:
            birth_date: 出生日期时间

        Returns:
            (天干, 地支)
        """
        # 使用蔡勒公式的变种来计算日柱
        # 以1900年1月1日（庚戌日）为基准
        base_date = datetime(1900, 1, 1)
        days_diff = (birth_date.date() - base_date.date()).days

        # 1900年1月1日是庚戌日
        # 庚是第6个天干（索引6），戌是第10个地支（索引10）
        base_gan_index = 6
        base_zhi_index = 10

        gan_index = (base_gan_index + days_diff) % 10
        zhi_index = (base_zhi_index + days_diff) % 12

        return cls.TIAN_GAN[gan_index], cls.DI_ZHI[zhi_index]

    @classmethod
    def calculate_hour_pillar(cls, birth_date: datetime, day_gan: str) -> Tuple[str, str]:
        """
        计算时柱

        Args:
            birth_date: 出生日期时间
            day_gan: 日干

        Returns:
            (天干, 地支)
        """
        hour = birth_date.hour

        # 确定时辰地支
        if hour == 23 or hour < 1:
            hour_zhi = '子'
            hour_index = 0
        else:
            for (start, end), zhi in cls.HOUR_DI_ZHI.items():
                if start <= hour < end:
                    hour_zhi = zhi
                    hour_index = cls._get_zhi_index(zhi)
                    break

        # 时干计算：日干配时干
        # 甲己还加甲，乙庚丙作初
        # 丙辛从戊起，丁壬庚子居
        # 戊癸何方发，壬子是真途
        if day_gan in ['甲', '己']:
            start_gan_index = 0  # 甲
        elif day_gan in ['乙', '庚']:
            start_gan_index = 2  # 丙
        elif day_gan in ['丙', '辛']:
            start_gan_index = 4  # 戊
        elif day_gan in ['丁', '壬']:
            start_gan_index = 6  # 庚
        else:  # 戊、癸
            start_gan_index = 8  # 壬

        hour_gan_index = (start_gan_index + hour_index) % 10
        hour_gan = cls.TIAN_GAN[hour_gan_index]

        return hour_gan, hour_zhi

    @classmethod
    def calculate_bazi(cls, birth_date: datetime) -> Dict:
        """
        计算完整的八字四柱

        Args:
            birth_date: 出生日期时间

        Returns:
            包含四柱信息的字典
        """
        # 计算年柱
        year_gan, year_zhi = cls.calculate_year_pillar(birth_date)
        year_pillar = year_gan + year_zhi

        # 计算月柱
        month_gan, month_zhi = cls.calculate_month_pillar(birth_date, year_gan)
        month_pillar = month_gan + month_zhi

        # 计算日柱
        day_gan, day_zhi = cls.calculate_day_pillar(birth_date)
        day_pillar = day_gan + day_zhi

        # 计算时柱
        hour_gan, hour_zhi = cls.calculate_hour_pillar(birth_date, day_gan)
        hour_pillar = hour_gan + hour_zhi

        # 计算五行
        wu_xing = {
            'year_gan': cls.WU_XING[year_gan],
            'year_zhi': cls.WU_XING[year_zhi],
            'month_gan': cls.WU_XING[month_gan],
            'month_zhi': cls.WU_XING[month_zhi],
            'day_gan': cls.WU_XING[day_gan],
            'day_zhi': cls.WU_XING[day_zhi],
            'hour_gan': cls.WU_XING[hour_gan],
            'hour_zhi': cls.WU_XING[hour_zhi],
        }

        # 计算阴阳
        yin_yang = {
            'year_gan': cls.YIN_YANG[year_gan],
            'year_zhi': cls.YIN_YANG[year_zhi],
            'month_gan': cls.YIN_YANG[month_gan],
            'month_zhi': cls.YIN_YANG[month_zhi],
            'day_gan': cls.YIN_YANG[day_gan],
            'day_zhi': cls.YIN_YANG[day_zhi],
            'hour_gan': cls.YIN_YANG[hour_gan],
            'hour_zhi': cls.YIN_YANG[hour_zhi],
        }

        # 统计五行数量
        wu_xing_count = {'木': 0, '火': 0, '土': 0, '金': 0, '水': 0}
        for element in wu_xing.values():
            wu_xing_count[element] += 1

        return {
            'year_pillar': year_pillar,
            'month_pillar': month_pillar,
            'day_pillar': day_pillar,
            'hour_pillar': hour_pillar,
            'pillars': {
                'year': {'gan': year_gan, 'zhi': year_zhi},
                'month': {'gan': month_gan, 'zhi': month_zhi},
                'day': {'gan': day_gan, 'zhi': day_zhi},
                'hour': {'gan': hour_gan, 'zhi': hour_zhi},
            },
            'wu_xing': wu_xing,
            'wu_xing_count': wu_xing_count,
            'yin_yang': yin_yang,
            'bazi_string': f"{year_pillar} {month_pillar} {day_pillar} {hour_pillar}"
        }


def calculate_bazi(year: int, month: int, day: int, hour: int, minute: int = 0) -> dict:
    """
    计算八字的便捷函数

    Args:
        year: 出生年
        month: 出生月
        day: 出生日
        hour: 出生时
        minute: 出生分（可选）

    Returns:
        包含八字信息的字典
    """
    birth_date = datetime(year, month, day, hour, minute)
    bazi_info = BaziCalculator.calculate_bazi(birth_date)

    # 添加农历信息
    lunar_year, lunar_month, lunar_day, is_leap = LunarCalendar.solar_to_lunar(birth_date)
    bazi_info['lunar'] = {
        'year': lunar_year,
        'month': lunar_month,
        'day': lunar_day,
        'is_leap': is_leap,
        'gan_zhi_year': LunarCalendar.get_gan_zhi_year(lunar_year),
        'sheng_xiao': LunarCalendar.get_sheng_xiao(lunar_year),
        'formatted': LunarCalendar.format_lunar_date(lunar_year, lunar_month, lunar_day, is_leap)
    }

    # 添加公历信息
    bazi_info['solar'] = {
        'year': year,
        'month': month,
        'day': day,
        'hour': hour,
        'minute': minute,
        'formatted': birth_date.strftime('%Y年%m月%d日 %H:%M')
    }

    # 计算神煞
    shensha_info = ShenshaCalculator.calculate_all_shensha(bazi_info)
    bazi_info['shensha'] = shensha_info

    return bazi_info
