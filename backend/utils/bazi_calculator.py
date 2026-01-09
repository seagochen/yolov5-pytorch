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

    # 藏干
    CANG_GAN = {
        '子': ['癸'],
        '丑': ['己', '癸', '辛'],
        '寅': ['甲', '丙', '戊'],
        '卯': ['乙'],
        '辰': ['戊', '乙', '癸'],
        '巳': ['丙', '戊', '庚'],
        '午': ['丁', '己'],
        '未': ['己', '丁', '乙'],
        '申': ['庚', '壬', '戊'],
        '酉': ['辛'],
        '戌': ['戊', '辛', '丁'],
        '亥': ['壬', '甲']
    }

    # 六十甲子纳音
    NAYIN = {
        '甲子': '海中金', '乙丑': '海中金',
        '丙寅': '炉中火', '丁卯': '炉中火',
        '戊辰': '大林木', '己巳': '大林木',
        '庚午': '路旁土', '辛未': '路旁土',
        '壬申': '剑锋金', '癸酉': '剑锋金',
        '甲戌': '山头火', '乙亥': '山头火',
        '丙子': '涧下水', '丁丑': '涧下水',
        '戊寅': '城头土', '己卯': '城头土',
        '庚辰': '白蜡金', '辛巳': '白蜡金',
        '壬午': '杨柳木', '癸未': '杨柳木',
        '甲申': '泉中水', '乙酉': '泉中水',
        '丙戌': '屋上土', '丁亥': '屋上土',
        '戊子': '霹雳火', '己丑': '霹雳火',
        '庚寅': '松柏木', '辛卯': '松柏木',
        '壬辰': '长流水', '癸巳': '长流水',
        '甲午': '砂石金', '乙未': '砂石金',
        '丙申': '山下火', '丁酉': '山下火',
        '戊戌': '平地木', '己亥': '平地木',
        '庚子': '壁上土', '辛丑': '壁上土',
        '壬寅': '金箔金', '癸卯': '金箔金',
        '甲辰': '覆灯火', '乙巳': '覆灯火',
        '丙午': '天河水', '丁未': '天河水',
        '戊申': '大驿土', '己酉': '大驿土',
        '庚戌': '钗钏金', '辛亥': '钗钏金',
        '壬子': '桑柘木', '癸丑': '桑柘木',
        '甲寅': '大溪水', '乙卯': '大溪水',
        '丙辰': '砂中土', '丁巳': '砂中土',
        '戊午': '天上火', '己未': '天上火',
        '庚申': '石榴木', '辛酉': '石榴木',
        '壬戌': '大海水', '癸亥': '大海水'
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
    def get_nayin(cls, ganzhi: str) -> str:
        """获取纳音五行"""
        return cls.NAYIN.get(ganzhi, '')

    @classmethod
    def get_canggan(cls, zhi: str) -> list:
        """获取地支藏干"""
        return cls.CANG_GAN.get(zhi, [])

    @classmethod
    def get_shishen(cls, day_gan: str, target_gan: str) -> str:
        """
        计算十神关系
        以日干为我，看目标干与日干的关系

        Args:
            day_gan: 日干（我）
            target_gan: 目标天干

        Returns:
            十神名称
        """
        if day_gan == target_gan:
            return '比肩'

        day_wuxing = cls.WU_XING[day_gan]
        target_wuxing = cls.WU_XING[target_gan]
        day_yinyang = cls.YIN_YANG[day_gan]
        target_yinyang = cls.YIN_YANG[target_gan]
        same_yinyang = day_yinyang == target_yinyang

        # 五行生克关系
        sheng = {'木': '火', '火': '土', '土': '金', '金': '水', '水': '木'}
        ke = {'木': '土', '火': '金', '土': '水', '金': '木', '水': '火'}

        # 同我（比劫）
        if day_wuxing == target_wuxing:
            return '比肩' if same_yinyang else '劫财'
        # 我生（食伤）
        elif sheng[day_wuxing] == target_wuxing:
            return '食神' if same_yinyang else '伤官'
        # 我克（财）
        elif ke[day_wuxing] == target_wuxing:
            return '偏财' if same_yinyang else '正财'
        # 克我（官杀）
        elif ke[target_wuxing] == day_wuxing:
            return '七杀' if same_yinyang else '正官'
        # 生我（印）
        elif sheng[target_wuxing] == day_wuxing:
            return '偏印' if same_yinyang else '正印'

        return ''

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

        # 计算藏干
        cang_gan = {
            'year': cls.get_canggan(year_zhi),
            'month': cls.get_canggan(month_zhi),
            'day': cls.get_canggan(day_zhi),
            'hour': cls.get_canggan(hour_zhi),
        }

        # 计算纳音
        nayin = {
            'year': cls.get_nayin(year_pillar),
            'month': cls.get_nayin(month_pillar),
            'day': cls.get_nayin(day_pillar),
            'hour': cls.get_nayin(hour_pillar),
        }

        # 计算十神（以日干为主）
        shishen = {
            'year_gan': cls.get_shishen(day_gan, year_gan),
            'month_gan': cls.get_shishen(day_gan, month_gan),
            'day_gan': '日主',  # 日干是自己
            'hour_gan': cls.get_shishen(day_gan, hour_gan),
        }

        # 计算藏干的十神
        canggan_shishen = {
            'year': [cls.get_shishen(day_gan, g) for g in cang_gan['year']],
            'month': [cls.get_shishen(day_gan, g) for g in cang_gan['month']],
            'day': [cls.get_shishen(day_gan, g) for g in cang_gan['day']],
            'hour': [cls.get_shishen(day_gan, g) for g in cang_gan['hour']],
        }

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
            'cang_gan': cang_gan,
            'nayin': nayin,
            'shishen': shishen,
            'canggan_shishen': canggan_shishen,
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
