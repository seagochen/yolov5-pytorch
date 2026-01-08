# -*- coding: utf-8 -*-
"""
阴历（农历）转换工具
使用寿星万年历算法实现公历到农历的转换
"""
from datetime import datetime, timedelta
from typing import Tuple, Optional


class LunarCalendar:
    """农历转换类"""

    # 农历数据（1900-2100年）
    # 每个数字的前12位表示12个月是大月(30天)还是小月(29天)，最后4位表示闰月月份
    LUNAR_INFO = [
        0x04bd8, 0x04ae0, 0x0a570, 0x054d5, 0x0d260, 0x0d950, 0x16554, 0x056a0, 0x09ad0, 0x055d2,
        0x04ae0, 0x0a5b6, 0x0a4d0, 0x0d250, 0x1d255, 0x0b540, 0x0d6a0, 0x0ada2, 0x095b0, 0x14977,
        0x04970, 0x0a4b0, 0x0b4b5, 0x06a50, 0x06d40, 0x1ab54, 0x02b60, 0x09570, 0x052f2, 0x04970,
        0x06566, 0x0d4a0, 0x0ea50, 0x06e95, 0x05ad0, 0x02b60, 0x186e3, 0x092e0, 0x1c8d7, 0x0c950,
        0x0d4a0, 0x1d8a6, 0x0b550, 0x056a0, 0x1a5b4, 0x025d0, 0x092d0, 0x0d2b2, 0x0a950, 0x0b557,
        0x06ca0, 0x0b550, 0x15355, 0x04da0, 0x0a5b0, 0x14573, 0x052b0, 0x0a9a8, 0x0e950, 0x06aa0,
        0x0aea6, 0x0ab50, 0x04b60, 0x0aae4, 0x0a570, 0x05260, 0x0f263, 0x0d950, 0x05b57, 0x056a0,
        0x096d0, 0x04dd5, 0x04ad0, 0x0a4d0, 0x0d4d4, 0x0d250, 0x0d558, 0x0b540, 0x0b6a0, 0x195a6,
        0x095b0, 0x049b0, 0x0a974, 0x0a4b0, 0x0b27a, 0x06a50, 0x06d40, 0x0af46, 0x0ab60, 0x09570,
        0x04af5, 0x04970, 0x064b0, 0x074a3, 0x0ea50, 0x06b58, 0x055c0, 0x0ab60, 0x096d5, 0x092e0,
        0x0c960, 0x0d954, 0x0d4a0, 0x0da50, 0x07552, 0x056a0, 0x0abb7, 0x025d0, 0x092d0, 0x0cab5,
        0x0a950, 0x0b4a0, 0x0baa4, 0x0ad50, 0x055d9, 0x04ba0, 0x0a5b0, 0x15176, 0x052b0, 0x0a930,
        0x07954, 0x06aa0, 0x0ad50, 0x05b52, 0x04b60, 0x0a6e6, 0x0a4e0, 0x0d260, 0x0ea65, 0x0d530,
        0x05aa0, 0x076a3, 0x096d0, 0x04afb, 0x04ad0, 0x0a4d0, 0x1d0b6, 0x0d250, 0x0d520, 0x0dd45,
        0x0b5a0, 0x056d0, 0x055b2, 0x049b0, 0x0a577, 0x0a4b0, 0x0aa50, 0x1b255, 0x06d20, 0x0ada0,
        0x14b63, 0x09370, 0x049f8, 0x04970, 0x064b0, 0x168a6, 0x0ea50, 0x06b20, 0x1a6c4, 0x0aae0,
        0x0a2e0, 0x0d2e3, 0x0c960, 0x0d557, 0x0d4a0, 0x0da50, 0x05d55, 0x056a0, 0x0a6d0, 0x055d4,
        0x052d0, 0x0a9b8, 0x0a950, 0x0b4a0, 0x0b6a6, 0x0ad50, 0x055a0, 0x0aba4, 0x0a5b0, 0x052b0,
        0x0b273, 0x06930, 0x07337, 0x06aa0, 0x0ad50, 0x14b55, 0x04b60, 0x0a570, 0x054e4, 0x0d160,
        0x0e968, 0x0d520, 0x0daa0, 0x16aa6, 0x056d0, 0x04ae0, 0x0a9d4, 0x0a2d0, 0x0d150, 0x0f252,
        0x0d520,
    ]

    # 天干
    TIAN_GAN = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']

    # 地支
    DI_ZHI = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']

    # 生肖
    SHENG_XIAO = ['鼠', '牛', '虎', '兔', '龙', '蛇', '马', '羊', '猴', '鸡', '狗', '猪']

    # 农历月份
    LUNAR_MONTHS = ['正', '二', '三', '四', '五', '六', '七', '八', '九', '十', '冬', '腊']

    # 农历日期
    LUNAR_DAYS1 = ['初', '十', '廿', '卅']
    LUNAR_DAYS2 = ['一', '二', '三', '四', '五', '六', '七', '八', '九', '十']

    # 1900年1月31日，农历1900年正月初一
    BASE_DATE = datetime(1900, 1, 31)
    MIN_YEAR = 1900
    MAX_YEAR = 2100

    @classmethod
    def _get_leap_month(cls, year: int) -> int:
        """获取闰月月份（0表示无闰月）"""
        if year < cls.MIN_YEAR or year >= cls.MIN_YEAR + len(cls.LUNAR_INFO):
            return 0
        return cls.LUNAR_INFO[year - cls.MIN_YEAR] & 0xf

    @classmethod
    def _get_lunar_month_days(cls, year: int, month: int) -> int:
        """获取农历某月的天数"""
        if year < cls.MIN_YEAR or year >= cls.MIN_YEAR + len(cls.LUNAR_INFO):
            return 30

        # 获取该年的农历信息
        info = cls.LUNAR_INFO[year - cls.MIN_YEAR]

        # 检查是否为大月（30天）还是小月（29天）
        if info & (0x10000 >> month):
            return 30
        else:
            return 29

    @classmethod
    def _get_lunar_year_days(cls, year: int) -> int:
        """获取农历年的总天数"""
        sum_days = 0
        for i in range(1, 13):
            sum_days += cls._get_lunar_month_days(year, i)

        # 加上闰月的天数
        leap_month = cls._get_leap_month(year)
        if leap_month:
            sum_days += cls._get_lunar_month_days(year, leap_month)

        return sum_days

    @classmethod
    def _get_leap_month_days(cls, year: int) -> int:
        """获取闰月的天数"""
        leap_month = cls._get_leap_month(year)
        if leap_month:
            if cls.LUNAR_INFO[year - cls.MIN_YEAR] & 0x10000:
                return 30
            else:
                return 29
        return 0

    @classmethod
    def solar_to_lunar(cls, solar_date: datetime) -> Tuple[int, int, int, bool]:
        """
        公历转农历

        Args:
            solar_date: 公历日期

        Returns:
            (农历年, 农历月, 农历日, 是否闰月)
        """
        if solar_date < cls.BASE_DATE:
            raise ValueError(f"日期不能早于{cls.BASE_DATE.strftime('%Y-%m-%d')}")

        # 计算与基准日期的差距
        offset = (solar_date - cls.BASE_DATE).days

        # 从1900年开始逐年累加
        lunar_year = cls.MIN_YEAR
        while lunar_year < cls.MAX_YEAR:
            year_days = cls._get_lunar_year_days(lunar_year)
            if offset < year_days:
                break
            offset -= year_days
            lunar_year += 1

        # 计算月份
        leap_month = cls._get_leap_month(lunar_year)
        is_leap = False

        lunar_month = 1
        while lunar_month <= 12:
            # 闰月
            if leap_month > 0 and lunar_month == leap_month + 1 and not is_leap:
                lunar_month -= 1
                is_leap = True
                month_days = cls._get_leap_month_days(lunar_year)
            else:
                month_days = cls._get_lunar_month_days(lunar_year, lunar_month)

            if offset < month_days:
                break

            offset -= month_days
            lunar_month += 1

            if is_leap and lunar_month == leap_month + 1:
                is_leap = False

        lunar_day = offset + 1

        return lunar_year, lunar_month, int(lunar_day), is_leap

    @classmethod
    def get_gan_zhi_year(cls, year: int) -> str:
        """获取年份的干支"""
        # 甲子年是1984年（以立春为界，这里简化处理）
        gan_index = (year - 4) % 10
        zhi_index = (year - 4) % 12
        return cls.TIAN_GAN[gan_index] + cls.DI_ZHI[zhi_index]

    @classmethod
    def get_sheng_xiao(cls, year: int) -> str:
        """获取生肖"""
        return cls.SHENG_XIAO[(year - 4) % 12]

    @classmethod
    def format_lunar_date(cls, year: int, month: int, day: int, is_leap: bool = False) -> str:
        """
        格式化农历日期

        Args:
            year: 农历年
            month: 农历月
            day: 农历日
            is_leap: 是否闰月

        Returns:
            格式化的农历日期字符串
        """
        # 年份
        year_str = cls.get_gan_zhi_year(year) + '年'

        # 月份
        if is_leap:
            month_str = '闰' + cls.LUNAR_MONTHS[month - 1] + '月'
        else:
            month_str = cls.LUNAR_MONTHS[month - 1] + '月'

        # 日期
        if day == 10:
            day_str = '初十'
        elif day == 20:
            day_str = '二十'
        elif day == 30:
            day_str = '三十'
        else:
            day_str = cls.LUNAR_DAYS1[day // 10] + cls.LUNAR_DAYS2[day % 10 - 1]

        return f"{year_str}{month_str}{day_str}"


def solar_to_lunar(year: int, month: int, day: int) -> dict:
    """
    公历转农历的便捷函数

    Args:
        year: 公历年
        month: 公历月
        day: 公历日

    Returns:
        包含农历信息的字典
    """
    solar_date = datetime(year, month, day)
    lunar_year, lunar_month, lunar_day, is_leap = LunarCalendar.solar_to_lunar(solar_date)

    return {
        'year': lunar_year,
        'month': lunar_month,
        'day': lunar_day,
        'is_leap': is_leap,
        'gan_zhi_year': LunarCalendar.get_gan_zhi_year(lunar_year),
        'sheng_xiao': LunarCalendar.get_sheng_xiao(lunar_year),
        'formatted': LunarCalendar.format_lunar_date(lunar_year, lunar_month, lunar_day, is_leap)
    }
