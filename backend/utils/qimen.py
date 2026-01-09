# -*- coding: utf-8 -*-
"""
奇门遁甲排盘工具
"""
from datetime import datetime
from typing import Dict, List, Tuple
from .solar_terms import SolarTerms


class QimenDunjia:
    """奇门遁甲排盘类"""

    # 天干（三奇六仪）
    TIAN_GAN = ['戊', '己', '庚', '辛', '壬', '癸', '丁', '丙', '乙']
    # 三奇：乙（日奇）、丙（月奇）、丁（星奇）
    SAN_QI = ['乙', '丙', '丁']

    # 地支
    DI_ZHI = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']

    # 八门
    BA_MEN = ['休门', '生门', '伤门', '杜门', '景门', '死门', '惊门', '开门']

    # 九星
    JIU_XING = ['天蓬星', '天芮星', '天冲星', '天辅星', '天禽星', '天心星', '天柱星', '天任星', '天英星']

    # 八神
    BA_SHEN = ['值符', '腾蛇', '太阴', '六合', '白虎', '玄武', '九地', '九天']

    # 九宫方位
    JIU_GONG = {
        1: '坎一宫',
        2: '坤二宫',
        3: '震三宫',
        4: '巽四宫',
        5: '中五宫',
        6: '乾六宫',
        7: '兑七宫',
        8: '艮八宫',
        9: '离九宫'
    }

    # 九宫八卦
    BA_GUA = {
        1: '坎',
        2: '坤',
        3: '震',
        4: '巽',
        5: '中',
        6: '乾',
        7: '兑',
        8: '艮',
        9: '离'
    }

    # 地盘三奇六仪固定排列（阳遁一局）
    DI_PAN_YANG_1 = {
        1: '戊',
        2: '己',
        3: '庚',
        4: '辛',
        5: '壬',  # 中五宫寄坤二宫
        6: '癸',
        7: '丁',
        8: '丙',
        9: '乙'
    }

    # 八门地盘固定位置（永不变）
    BA_MEN_DI_PAN = {
        1: '休门',
        2: '死门',
        3: '伤门',
        4: '杜门',
        5: '开门',  # 中五宫寄坤二宫
        6: '开门',
        7: '惊门',
        8: '生门',
        9: '景门'
    }

    # 九星地盘固定位置
    JIU_XING_DI_PAN = {
        1: '天蓬星',
        2: '天芮星',
        3: '天冲星',
        4: '天辅星',
        5: '天禽星',
        6: '天心星',
        7: '天柱星',
        8: '天任星',
        9: '天英星'
    }

    @classmethod
    def get_zhi_fu_gong(cls, ju_number: int) -> int:
        """
        获取值符宫位（根据局数）

        Args:
            ju_number: 局数(1-9)

        Returns:
            值符所在宫位(1-9)
        """
        # 值符永远在局数对应的宫位
        # 例如：阳遁一局，值符在坎一宫
        return ju_number

    @classmethod
    def get_shi_gan_index(cls, hour: int) -> int:
        """
        获取时干索引（用于确定值使）

        Args:
            hour: 小时(0-23)

        Returns:
            时干索引(0-11)
        """
        # 时辰对应地支
        if hour == 23 or hour < 1:
            return 0  # 子时
        elif hour < 3:
            return 1  # 丑时
        elif hour < 5:
            return 2  # 寅时
        elif hour < 7:
            return 3  # 卯时
        elif hour < 9:
            return 4  # 辰时
        elif hour < 11:
            return 5  # 巳时
        elif hour < 13:
            return 6  # 午时
        elif hour < 15:
            return 7  # 未时
        elif hour < 17:
            return 8  # 申时
        elif hour < 19:
            return 9  # 酉时
        elif hour < 21:
            return 10  # 戌时
        else:
            return 11  # 亥时

    @classmethod
    def arrange_tian_pan(cls, di_pan: Dict[int, str], zhi_fu_gong: int, shi_gan_index: int, is_yang: bool) -> Dict[int, str]:
        """
        排天盘（三奇六仪）

        Args:
            di_pan: 地盘配置
            zhi_fu_gong: 值符宫位
            shi_gan_index: 时干索引
            is_yang: 是否阳遁

        Returns:
            天盘配置
        """
        # 找到地盘中值符（对应局数的天干）的位置
        zhi_fu_gan = di_pan[zhi_fu_gong]

        # 找到时干在地盘的位置
        shi_gan_gong = None
        for gong, gan in di_pan.items():
            if gan == zhi_fu_gan:
                shi_gan_gong = gong
                break

        # 计算偏移量
        if is_yang:
            # 阳遁：顺时针旋转
            offset = shi_gan_index
        else:
            # 阴遁：逆时针旋转
            offset = -shi_gan_index

        # 排天盘
        tian_pan = {}
        for gong in range(1, 10):
            # 跳过中五宫
            if gong == 5:
                continue

            # 计算天盘对应的地盘位置
            new_gong = gong + offset
            if new_gong > 9:
                new_gong -= 8
            elif new_gong < 1:
                new_gong += 8

            # 跳过中五宫
            if new_gong == 5:
                new_gong = 2  # 寄坤二宫

            tian_pan[gong] = di_pan.get(new_gong, '戊')

        tian_pan[5] = di_pan[2]  # 中五宫寄坤二宫
        return tian_pan

    @classmethod
    def arrange_ba_men(cls, zhi_shi_gong: int, shi_gan_index: int, is_yang: bool) -> Dict[int, str]:
        """
        排八门（人盘）

        八门按照九宫飞布顺序排列：1->8->3->4->9->2->7->6
        八门只有8个，中五宫寄坤二宫（即中五宫显示与坤二宫相同的门）

        Args:
            zhi_shi_gong: 值使宫位
            shi_gan_index: 时干索引
            is_yang: 是否阳遁

        Returns:
            八门配置
        """
        ba_men = {}

        # 九宫飞布顺序（不含中五宫）
        gong_order = [1, 8, 3, 4, 9, 2, 7, 6]

        # 八门顺序（与九宫飞布顺序对应的地盘门）
        # 地盘：1-休门, 8-生门, 3-伤门, 4-杜门, 9-景门, 2-死门, 7-惊门, 6-开门
        men_order = ['休门', '生门', '伤门', '杜门', '景门', '死门', '惊门', '开门']

        # 值使门随时辰移动
        offset = shi_gan_index if is_yang else -shi_gan_index

        # 八门按九宫顺序分配到各宫
        for i, gong in enumerate(gong_order):
            # 计算该宫应该放置的门的索引
            men_index = (i - offset) % 8
            ba_men[gong] = men_order[men_index]

        # 中五宫寄坤二宫
        ba_men[5] = ba_men[2]

        return ba_men

    @classmethod
    def arrange_jiu_xing(cls, zhi_fu_gong: int, shi_gan_index: int, is_yang: bool) -> Dict[int, str]:
        """
        排九星

        九星按照九宫飞布顺序排列：1->8->3->4->9->2->7->6
        天禽星寄坤二宫（中五宫显示与坤二宫相同）

        Args:
            zhi_fu_gong: 值符宫位
            shi_gan_index: 时干索引
            is_yang: 是否阳遁

        Returns:
            九星配置
        """
        jiu_xing = {}

        # 九宫飞布顺序（不含中五宫）
        gong_order = [1, 8, 3, 4, 9, 2, 7, 6]

        # 九星顺序（天禽星寄坤二宫，所以只有8个星分配到8宫）
        # 地盘：1-天蓬, 8-天任, 3-天冲, 4-天辅, 9-天英, 2-天芮(禽), 7-天柱, 6-天心
        xing_order = ['天蓬星', '天任星', '天冲星', '天辅星', '天英星', '天芮星', '天柱星', '天心星']

        offset = shi_gan_index if is_yang else -shi_gan_index

        for i, gong in enumerate(gong_order):
            xing_index = (i - offset) % 8
            jiu_xing[gong] = xing_order[xing_index]

        # 中五宫（天禽星）寄坤二宫
        jiu_xing[5] = jiu_xing[2]

        return jiu_xing

    @classmethod
    def arrange_ba_shen(cls, zhi_fu_gong: int, shi_gan_index: int, is_yang: bool) -> Dict[int, str]:
        """
        排八神

        八神以值符宫为起点，按九宫飞布顺序排列：
        - 阳遁顺排：值符→腾蛇→太阴→六合→白虎→玄武→九地→九天
        - 阴遁逆排：值符→九天→九地→玄武→白虎→六合→太阴→腾蛇

        Args:
            zhi_fu_gong: 值符宫位（八神从此宫开始排布）
            shi_gan_index: 时干索引（未使用，八神不随时干移动）
            is_yang: 是否阳遁

        Returns:
            八神配置
        """
        ba_shen = {}

        # 八神顺序
        if is_yang:
            # 阳遁顺排
            shen_order = ['值符', '腾蛇', '太阴', '六合', '白虎', '玄武', '九地', '九天']
        else:
            # 阴遁逆排
            shen_order = ['值符', '九天', '九地', '玄武', '白虎', '六合', '太阴', '腾蛇']

        # 九宫飞布顺序（不含中五宫）
        gong_order = [1, 8, 3, 4, 9, 2, 7, 6]

        # 找到值符宫在九宫顺序中的位置
        if zhi_fu_gong == 5:
            # 中五宫寄坤二宫
            start_gong = 2
        else:
            start_gong = zhi_fu_gong

        # 找到起始宫位在顺序中的索引
        try:
            start_idx = gong_order.index(start_gong)
        except ValueError:
            start_idx = 0

        # 从值符宫开始，按九宫顺序分配八神
        for i, shen in enumerate(shen_order):
            gong_idx = (start_idx + i) % 8
            gong = gong_order[gong_idx]
            ba_shen[gong] = shen

        # 中五宫寄坤二宫
        ba_shen[5] = ba_shen[2]

        return ba_shen

    @classmethod
    def judge_ji_xiong(cls, gong: int, tian_pan: str, men: str, xing: str, shen: str) -> Dict:
        """
        判断宫位吉凶

        Args:
            gong: 宫位
            tian_pan: 天盘天干
            men: 八门
            xing: 九星
            shen: 八神

        Returns:
            吉凶判断结果
        """
        ji_score = 0
        xiong_score = 0
        notes = []

        # 判断门的吉凶
        if men in ['生门', '开门', '休门']:
            ji_score += 2
            notes.append(f'{men}为吉门')
        elif men in ['死门', '惊门', '伤门']:
            xiong_score += 2
            notes.append(f'{men}为凶门')
        else:
            notes.append(f'{men}为平门')

        # 判断星的吉凶
        if xing in ['天辅星', '天心星', '天任星']:
            ji_score += 2
            notes.append(f'{xing}为吉星')
        elif xing in ['天蓬星', '天芮星']:
            xiong_score += 2
            notes.append(f'{xing}为凶星')

        # 判断神的吉凶
        if shen in ['值符', '六合', '太阴', '九天']:
            ji_score += 1
            notes.append(f'{shen}为吉神')
        elif shen in ['白虎', '玄武', '腾蛇']:
            xiong_score += 1
            notes.append(f'{shen}为凶神')

        # 判断三奇
        if tian_pan in cls.SAN_QI:
            ji_score += 2
            if tian_pan == '乙':
                notes.append('乙为日奇，主文书功名')
            elif tian_pan == '丙':
                notes.append('丙为月奇，主权威武勇')
            elif tian_pan == '丁':
                notes.append('丁为星奇，主玄学智慧')

        # 特殊格局
        if men == '生门' and xing == '天任星':
            ji_score += 3
            notes.append('生门天任，大吉格局')

        if men == '开门' and xing == '天心星':
            ji_score += 3
            notes.append('开门天心，利于求财')

        if tian_pan == '乙' and men == '开门':
            ji_score += 2
            notes.append('日奇开门，利于出行')

        # 判断最终吉凶
        if ji_score > xiong_score:
            result = '吉'
        elif xiong_score > ji_score:
            result = '凶'
        else:
            result = '平'

        return {
            'result': result,
            'ji_score': ji_score,
            'xiong_score': xiong_score,
            'notes': notes
        }

    @classmethod
    def paipan(cls, year: int, month: int, day: int, hour: int, minute: int = 0) -> Dict:
        """
        奇门遁甲排盘

        Args:
            year: 年
            month: 月
            day: 日
            hour: 时
            minute: 分

        Returns:
            排盘结果
        """
        date_time = datetime(year, month, day, hour, minute)

        # 1. 获取节气
        term_name, term_index = SolarTerms.get_solar_term(date_time)
        day_in_term = SolarTerms.get_day_in_term(date_time, term_index)
        yuan = SolarTerms.get_yuan(term_index, day_in_term)

        # 2. 判断阴阳遁
        is_yang = SolarTerms.is_yang_dun(term_index)
        dun_type = '阳遁' if is_yang else '阴遁'

        # 3. 获取局数
        ju_number = SolarTerms.get_ju_number(term_index, yuan)

        # 4. 确定值符宫
        zhi_fu_gong = cls.get_zhi_fu_gong(ju_number)

        # 5. 获取时干索引
        shi_gan_index = cls.get_shi_gan_index(hour)

        # 6. 排地盘（固定）
        di_pan = cls.DI_PAN_YANG_1.copy()

        # 7. 排天盘
        tian_pan = cls.arrange_tian_pan(di_pan, zhi_fu_gong, shi_gan_index, is_yang)

        # 8. 排八门
        zhi_shi_gong = zhi_fu_gong  # 值使跟随值符
        ba_men = cls.arrange_ba_men(zhi_shi_gong, shi_gan_index, is_yang)

        # 9. 排九星
        jiu_xing = cls.arrange_jiu_xing(zhi_fu_gong, shi_gan_index, is_yang)

        # 10. 排八神
        ba_shen = cls.arrange_ba_shen(zhi_fu_gong, shi_gan_index, is_yang)

        # 11. 组合九宫信息
        jiu_gong_info = {}
        for gong in range(1, 10):
            di = di_pan.get(gong, '戊')
            tian = tian_pan.get(gong, '戊')
            men = ba_men.get(gong, '休门')
            xing = jiu_xing.get(gong, '天蓬星')
            shen = ba_shen.get(gong, '值符')

            # 判断吉凶
            ji_xiong = cls.judge_ji_xiong(gong, tian, men, xing, shen)

            jiu_gong_info[gong] = {
                'gong_name': cls.JIU_GONG[gong],
                'ba_gua': cls.BA_GUA[gong],
                'di_pan': di,
                'tian_pan': tian,
                'ba_men': men,
                'jiu_xing': xing,
                'ba_shen': shen,
                'ji_xiong': ji_xiong['result'],
                'ji_score': ji_xiong['ji_score'],
                'xiong_score': ji_xiong['xiong_score'],
                'notes': ji_xiong['notes']
            }

        # 12. 整体分析
        zong_ping = cls.analyze_overall(jiu_gong_info)

        return {
            'date_time': date_time.strftime('%Y年%m月%d日 %H:%M'),
            'term': term_name,
            'yuan': yuan,
            'dun_type': dun_type,
            'ju_number': ju_number,
            'zhi_fu_gong': zhi_fu_gong,
            'jiu_gong': jiu_gong_info,
            'zong_ping': zong_ping
        }

    @classmethod
    def analyze_overall(cls, jiu_gong_info: Dict) -> Dict:
        """
        整体分析

        Args:
            jiu_gong_info: 九宫信息

        Returns:
            整体分析结果
        """
        ji_count = 0
        xiong_count = 0
        total_ji_score = 0
        total_xiong_score = 0
        best_gong = None
        worst_gong = None
        max_ji_score = -1
        max_xiong_score = -1

        for gong, info in jiu_gong_info.items():
            if info['ji_xiong'] == '吉':
                ji_count += 1
            elif info['ji_xiong'] == '凶':
                xiong_count += 1

            total_ji_score += info['ji_score']
            total_xiong_score += info['xiong_score']

            # 找出最吉宫位
            if info['ji_score'] > max_ji_score:
                max_ji_score = info['ji_score']
                best_gong = gong

            # 找出最凶宫位
            if info['xiong_score'] > max_xiong_score:
                max_xiong_score = info['xiong_score']
                worst_gong = gong

        # 整体判断
        if total_ji_score > total_xiong_score * 1.5:
            overall = '大吉'
            summary = '此局吉星吉门居多，宜主动出击，大胆行事'
        elif total_ji_score > total_xiong_score:
            overall = '小吉'
            summary = '此局偏吉，可以行事，但需谨慎为上'
        elif total_xiong_score > total_ji_score * 1.5:
            overall = '大凶'
            summary = '此局凶星凶门居多，宜静不宜动，守为上策'
        elif total_xiong_score > total_ji_score:
            overall = '小凶'
            summary = '此局偏凶，不宜大动，小事可为，大事缓行'
        else:
            overall = '平'
            summary = '此局平平，吉凶参半，行事需审时度势'

        return {
            'overall': overall,
            'summary': summary,
            'ji_count': ji_count,
            'xiong_count': xiong_count,
            'best_gong': best_gong,
            'best_gong_name': cls.JIU_GONG[best_gong] if best_gong else '',
            'worst_gong': worst_gong,
            'worst_gong_name': cls.JIU_GONG[worst_gong] if worst_gong else '',
            'advice': f'最宜从{cls.JIU_GONG.get(best_gong, "")}方位行事' if best_gong else '谨慎行事'
        }


def qimen_paipan(year: int, month: int, day: int, hour: int, minute: int = 0) -> dict:
    """
    奇门遁甲排盘的便捷函数

    Args:
        year: 年
        month: 月
        day: 日
        hour: 时
        minute: 分

    Returns:
        排盘结果
    """
    return QimenDunjia.paipan(year, month, day, hour, minute)
