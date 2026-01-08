# -*- coding: utf-8 -*-
"""
节气计算工具
用于奇门遁甲的节气判断
"""
from datetime import datetime, timedelta
from typing import Tuple


class SolarTerms:
    """节气计算类"""

    # 24节气名称
    SOLAR_TERMS = [
        '立春', '雨水', '惊蛰', '春分', '清明', '谷雨',
        '立夏', '小满', '芒种', '夏至', '小暑', '大暑',
        '立秋', '处暑', '白露', '秋分', '寒露', '霜降',
        '立冬', '小雪', '大雪', '冬至', '小寒', '大寒'
    ]

    # 节气基准数据（简化版本，实际应使用精确天文算法）
    # 以2000年为基准，每个节气的大致日期
    SOLAR_TERMS_BASE_2000 = [
        (2, 4),   # 立春
        (2, 19),  # 雨水
        (3, 6),   # 惊蛰
        (3, 21),  # 春分
        (4, 5),   # 清明
        (4, 20),  # 谷雨
        (5, 6),   # 立夏
        (5, 21),  # 小满
        (6, 6),   # 芒种
        (6, 21),  # 夏至
        (7, 7),   # 小暑
        (7, 23),  # 大暑
        (8, 8),   # 立秋
        (8, 23),  # 处暑
        (9, 8),   # 白露
        (9, 23),  # 秋分
        (10, 8),  # 寒露
        (10, 23), # 霜降
        (11, 7),  # 立冬
        (11, 22), # 小雪
        (12, 7),  # 大雪
        (12, 22), # 冬至
        (1, 6),   # 小寒
        (1, 20),  # 大寒
    ]

    @classmethod
    def get_solar_term(cls, date: datetime) -> Tuple[str, int]:
        """
        获取当前日期所在的节气

        Args:
            date: 日期时间

        Returns:
            (节气名称, 节气索引)
        """
        year = date.year
        month = date.month
        day = date.day

        # 简化处理：根据月日判断节气
        # 实际应该使用精确的天文算法计算
        for i, (m, d) in enumerate(cls.SOLAR_TERMS_BASE_2000):
            term_date = datetime(year, m, d)

            # 获取下一个节气
            next_i = (i + 1) % 24
            next_m, next_d = cls.SOLAR_TERMS_BASE_2000[next_i]

            # 处理跨年情况
            if next_i == 0:  # 小寒（下一年）
                next_term_date = datetime(year + 1, next_m, next_d)
            elif i == 23:  # 大寒到立春
                next_term_date = datetime(year, next_m, next_d)
                if date < term_date:
                    # 如果当前日期在大寒之前，说明是上一年的节气
                    prev_year = year - 1
                    prev_term_date = datetime(prev_year, 12, 22)  # 上一年冬至
                    if date >= prev_term_date:
                        return cls.SOLAR_TERMS[23], 23  # 大寒
            else:
                next_term_date = datetime(year, next_m, next_d)

            # 判断日期是否在当前节气范围内
            if term_date <= date < next_term_date:
                return cls.SOLAR_TERMS[i], i

        # 默认返回冬至
        return cls.SOLAR_TERMS[21], 21

    @classmethod
    def get_yuan(cls, term_index: int, day_in_term: int) -> str:
        """
        获取元（上元、中元、下元）

        Args:
            term_index: 节气索引
            day_in_term: 节气后第几天

        Returns:
            上元/中元/下元
        """
        if day_in_term <= 5:
            return '上元'
        elif day_in_term <= 10:
            return '中元'
        else:
            return '下元'

    @classmethod
    def is_yang_dun(cls, term_index: int) -> bool:
        """
        判断是阳遁还是阴遁
        冬至到夏至前为阳遁，夏至到冬至前为阴遁

        Args:
            term_index: 节气索引

        Returns:
            True为阳遁，False为阴遁
        """
        # 冬至(21)到芒种(8)为阳遁
        # 夏至(9)到大雪(20)为阴遁
        if term_index >= 21 or term_index <= 8:
            return True  # 阳遁
        else:
            return False  # 阴遁

    @classmethod
    def get_ju_number(cls, term_index: int, yuan: str) -> int:
        """
        获取局数（1-9局）

        Args:
            term_index: 节气索引
            yuan: 上元/中元/下元

        Returns:
            局数(1-9)
        """
        # 阳遁九局配置
        yang_dun_ju = {
            '立春': {'上元': 8, '中元': 9, '下元': 1},
            '雨水': {'上元': 8, '中元': 9, '下元': 1},
            '惊蛰': {'上元': 2, '中元': 3, '下元': 4},
            '春分': {'上元': 2, '中元': 3, '下元': 4},
            '清明': {'上元': 5, '中元': 6, '下元': 7},
            '谷雨': {'上元': 5, '中元': 6, '下元': 7},
            '立夏': {'上元': 8, '中元': 9, '下元': 1},
            '小满': {'上元': 8, '中元': 9, '下元': 1},
            '芒种': {'上元': 2, '中元': 3, '下元': 4},
            '夏至': {'上元': 2, '中元': 3, '下元': 4},
        }

        # 阴遁九局配置
        yin_dun_ju = {
            '夏至': {'上元': 9, '中元': 8, '下元': 7},
            '小暑': {'上元': 9, '中元': 8, '下元': 7},
            '大暑': {'上元': 6, '中元': 5, '下元': 4},
            '立秋': {'上元': 6, '中元': 5, '下元': 4},
            '处暑': {'上元': 3, '中元': 2, '下元': 1},
            '白露': {'上元': 3, '中元': 2, '下元': 1},
            '秋分': {'上元': 9, '中元': 8, '下元': 7},
            '寒露': {'上元': 9, '中元': 8, '下元': 7},
            '霜降': {'上元': 6, '中元': 5, '下元': 4},
            '立冬': {'上元': 6, '中元': 5, '下元': 4},
            '小雪': {'上元': 3, '中元': 2, '下元': 1},
            '大雪': {'上元': 3, '中元': 2, '下元': 1},
            '冬至': {'上元': 9, '中元': 8, '下元': 7},
            '小寒': {'上元': 9, '中元': 8, '下元': 7},
            '大寒': {'上元': 6, '中元': 5, '下元': 4},
        }

        term_name = cls.SOLAR_TERMS[term_index]
        is_yang = cls.is_yang_dun(term_index)

        if is_yang and term_name in yang_dun_ju:
            return yang_dun_ju[term_name].get(yuan, 1)
        elif not is_yang and term_name in yin_dun_ju:
            return yin_dun_ju[term_name].get(yuan, 9)
        else:
            return 1  # 默认值

    @classmethod
    def get_day_in_term(cls, date: datetime, term_index: int) -> int:
        """
        获取日期在节气中的天数

        Args:
            date: 日期
            term_index: 节气索引

        Returns:
            节气后第几天
        """
        year = date.year
        month, day = cls.SOLAR_TERMS_BASE_2000[term_index]
        term_date = datetime(year, month, day)

        if date < term_date:
            # 如果日期在节气之前，使用上一年的对应节气
            year -= 1
            term_date = datetime(year, month, day)

        days_diff = (date - term_date).days + 1
        return days_diff if days_diff <= 15 else 15  # 每个节气最多15天
