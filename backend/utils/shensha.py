# -*- coding: utf-8 -*-
"""
神煞计算工具
计算八字中的各种神煞
"""
from typing import List, Dict, Set, Tuple


class ShenshaCalculator:
    """神煞计算类"""

    # 天干
    TIAN_GAN = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']

    # 地支
    DI_ZHI = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']

    # ============ 天乙贵人 ============
    # 甲戊庚牛羊，乙己鼠猴乡，丙丁猪鸡位，壬癸蛇兔藏，六辛逢虎马，此是贵人方
    TIANYI_GUIREN = {
        '甲': ['丑', '未'], '戊': ['丑', '未'],
        '庚': ['丑', '未'],
        '乙': ['子', '申'], '己': ['子', '申'],
        '丙': ['亥', '酉'], '丁': ['亥', '酉'],
        '壬': ['巳', '卯'], '癸': ['巳', '卯'],
        '辛': ['寅', '午']
    }

    # ============ 太极贵人 ============
    # 甲乙生人子午中，丙丁鸡兔定亨通，戊己两干临四季，庚辛寅亥禄丰隆，壬癸巳申偏喜美，值此应当福气钟
    TAIJI_GUIREN = {
        '甲': ['子', '午'], '乙': ['子', '午'],
        '丙': ['卯', '酉'], '丁': ['卯', '酉'],
        '戊': ['辰', '戌', '丑', '未'], '己': ['辰', '戌', '丑', '未'],
        '庚': ['寅', '亥'], '辛': ['寅', '亥'],
        '壬': ['巳', '申'], '癸': ['巳', '申']
    }

    # ============ 文昌贵人 ============
    # 甲乙巳午报君知，丙戊申宫丁己鸡，庚猪辛鼠壬逢虎，癸人见兔入云梯
    WENCHANG_GUIREN = {
        '甲': '巳', '乙': '午',
        '丙': '申', '戊': '申',
        '丁': '酉', '己': '酉',
        '庚': '亥',
        '辛': '子',
        '壬': '寅',
        '癸': '卯'
    }

    # ============ 天德贵人 ============
    # 正丁二申宫，三壬四辛同，五亥六甲上，七癸八寅逢，九丙十居乙，子巳丑庚中
    TIANDE_GUIREN = {
        1: '丁', 2: '申', 3: '壬', 4: '辛',
        5: '亥', 6: '甲', 7: '癸', 8: '寅',
        9: '丙', 10: '乙', 11: '巳', 12: '庚'
    }

    # ============ 月德贵人 ============
    # 寅午戌月在丙，申子辰月在壬，亥卯未月在甲，巳酉丑月在庚
    YUEDE_GUIREN = {
        '寅': '丙', '午': '丙', '戌': '丙',
        '申': '壬', '子': '壬', '辰': '壬',
        '亥': '甲', '卯': '甲', '未': '甲',
        '巳': '庚', '酉': '庚', '丑': '庚'
    }

    # ============ 驿马 ============
    # 申子辰马在寅，寅午戌马在申，巳酉丑马在亥，亥卯未马在巳
    YIMA = {
        '申': '寅', '子': '寅', '辰': '寅',
        '寅': '申', '午': '申', '戌': '申',
        '巳': '亥', '酉': '亥', '丑': '亥',
        '亥': '巳', '卯': '巳', '未': '巳'
    }

    # ============ 华盖 ============
    # 寅午戌见戌，亥卯未见未，申子辰见辰，巳酉丑见丑
    HUAGAI = {
        '寅': '戌', '午': '戌', '戌': '戌',
        '亥': '未', '卯': '未', '未': '未',
        '申': '辰', '子': '辰', '辰': '辰',
        '巳': '丑', '酉': '丑', '丑': '丑'
    }

    # ============ 将星 ============
    # 寅午戌见午，巳酉丑见酉，申子辰见子，亥卯未见卯
    JIANGXING = {
        '寅': '午', '午': '午', '戌': '午',
        '巳': '酉', '酉': '酉', '丑': '酉',
        '申': '子', '子': '子', '辰': '子',
        '亥': '卯', '卯': '卯', '未': '卯'
    }

    # ============ 桃花（咸池）============
    # 申子辰在酉，寅午戌在卯，巳酉丑在午，亥卯未在子
    TAOHUA = {
        '申': '酉', '子': '酉', '辰': '酉',
        '寅': '卯', '午': '卯', '戌': '卯',
        '巳': '午', '酉': '午', '丑': '午',
        '亥': '子', '卯': '子', '未': '子'
    }

    # ============ 红艳 ============
    # 多情多欲少人知，六丙逢寅辛见鸡，癸临申上丁见未，眉开眼笑乐嘻嘻
    # 甲乙午申庚见戌，世间只是众人妻，戊己怕辰壬怕子，禄马相逢作路妓
    HONGYAN = {
        '甲': '午', '乙': '申',
        '丙': '寅',
        '丁': '未',
        '戊': '辰', '己': '辰',
        '庚': '戌',
        '辛': '酉',
        '壬': '子',
        '癸': '申'
    }

    # ============ 孤辰寡宿 ============
    # 亥子丑人，见寅为孤，见戌为寡
    # 寅卯辰人，见巳为孤，见丑为寡
    # 巳午未人，见申为孤，见辰为寡
    # 申酉戌人，见亥为孤，见未为寡
    GUCHEN_GUASU = {
        '亥': ('寅', '戌'), '子': ('寅', '戌'), '丑': ('寅', '戌'),
        '寅': ('巳', '丑'), '卯': ('巳', '丑'), '辰': ('巳', '丑'),
        '巳': ('申', '辰'), '午': ('申', '辰'), '未': ('申', '辰'),
        '申': ('亥', '未'), '酉': ('亥', '未'), '戌': ('亥', '未')
    }

    # ============ 羊刃 ============
    # 甲羊刃在卯，乙羊刃在寅，丙戊羊刃在午，丁己羊刃在巳，庚羊刃在酉，辛羊刃在申，壬羊刃在子，癸羊刃在亥
    YANGREN = {
        '甲': '卯', '乙': '寅',
        '丙': '午', '戊': '午',
        '丁': '巳', '己': '巳',
        '庚': '酉', '辛': '申',
        '壬': '子', '癸': '亥'
    }

    # ============ 禄神 ============
    # 甲禄在寅，乙禄在卯，丙戊禄在巳，丁己禄在午，庚禄在申，辛禄在酉，壬禄在亥，癸禄在子
    LUSHEN = {
        '甲': '寅', '乙': '卯',
        '丙': '巳', '戊': '巳',
        '丁': '午', '己': '午',
        '庚': '申', '辛': '酉',
        '壬': '亥', '癸': '子'
    }

    # ============ 劫煞 ============
    # 申子辰见巳，亥卯未见申，寅午戌见亥，巳酉丑见寅
    JIESHA = {
        '申': '巳', '子': '巳', '辰': '巳',
        '亥': '申', '卯': '申', '未': '申',
        '寅': '亥', '午': '亥', '戌': '亥',
        '巳': '寅', '酉': '寅', '丑': '寅'
    }

    # ============ 亡神 ============
    # 申子辰见亥，寅午戌见巳，巳酉丑见申，亥卯未见寅
    WANGSHEN = {
        '申': '亥', '子': '亥', '辰': '亥',
        '寅': '巳', '午': '巳', '戌': '巳',
        '巳': '申', '酉': '申', '丑': '申',
        '亥': '寅', '卯': '寅', '未': '寅'
    }

    # ============ 天罗地网 ============
    # 辰为天罗，戌为地网，火命人以戌为天罗、辰为地网
    TIANLUO_DIWANG = ['辰', '戌']

    # ============ 金舆 ============
    # 甲龙乙蛇丙戊羊，丁己猴歌庚犬方，辛猪壬鼠癸见牛，凡人遇此福气昌
    JINYU = {
        '甲': '辰', '乙': '巳',
        '丙': '未', '戊': '未',
        '丁': '申', '己': '申',
        '庚': '戌',
        '辛': '亥',
        '壬': '子',
        '癸': '丑'
    }

    # ============ 国印贵人 ============
    # 甲见戌，乙见亥，丙见丑，丁见寅，戊见丑，己见寅，庚见辰，辛见巳，壬见未，癸见申
    GUOYIN = {
        '甲': '戌', '乙': '亥',
        '丙': '丑', '戊': '丑',
        '丁': '寅', '己': '寅',
        '庚': '辰', '辛': '巳',
        '壬': '未', '癸': '申'
    }

    # ============ 学堂 ============
    # 甲见巳，乙见午，丙见申，丁见酉，戊见申，己见酉，庚见亥，辛见子，壬见寅，癸见卯
    XUETANG = {
        '甲': '巳', '乙': '午',
        '丙': '申', '戊': '申',
        '丁': '酉', '己': '酉',
        '庚': '亥', '辛': '子',
        '壬': '寅', '癸': '卯'
    }

    # ============ 词馆 ============
    # 甲干见庚寅，乙干见辛卯，丙干见乙巳，丁干见戊午，戊干见丁巳，己干见庚午，庚干见壬申，辛干见癸酉，壬干见甲子，癸干见乙亥
    CIGUAN = {
        '甲': ('庚', '寅'), '乙': ('辛', '卯'),
        '丙': ('乙', '巳'), '丁': ('戊', '午'),
        '戊': ('丁', '巳'), '己': ('庚', '午'),
        '庚': ('壬', '申'), '辛': ('癸', '酉'),
        '壬': ('甲', '子'), '癸': ('乙', '亥')
    }

    # 神煞说明
    SHENSHA_DESC = {
        '天乙贵人': '最吉之神，逢凶化吉，遇难呈祥',
        '太极贵人': '聪明好学，有钻研精神，喜欢哲学玄学',
        '文昌贵人': '聪明过人，文才出众，利于功名',
        '天德贵人': '福德深厚，逢凶化吉，一生少病',
        '月德贵人': '福德深厚，化险为夷，性情温良',
        '驿马': '奔波走动，利于远行，职业多变',
        '华盖': '聪明好学，喜欢艺术宗教，性格孤独',
        '将星': '有领导才能，处事果断，权威性强',
        '桃花': '聪明漂亮，异性缘好，容易有桃花运',
        '红艳': '异性缘佳，容易有感情纠葛',
        '孤辰': '孤独之星，六亲缘薄，性格孤僻',
        '寡宿': '孤独之星，婚姻不利，容易孤独',
        '羊刃': '刚强好斗，性格刚烈，易有刑伤',
        '禄神': '衣食丰足，财运亨通，福禄双全',
        '劫煞': '小人多，易遭劫夺，需防破财',
        '亡神': '易有官司诉讼，需防小人',
        '天罗': '做事阻滞，易受牵制困扰',
        '地网': '做事阻滞，易受牵制困扰',
        '金舆': '财运亨通，有贵人扶持',
        '国印': '有权威，能掌实权，受人尊敬',
        '学堂': '聪明好学，利于读书考试',
        '词馆': '文笔出众，善于表达，口才好'
    }

    @classmethod
    def _check_in_pillars(cls, target: str, pillars: List[str]) -> bool:
        """检查某个字是否在四柱中"""
        return target in pillars

    @classmethod
    def calculate_tianyi_guiren(cls, day_gan: str, pillars: List[str]) -> List[str]:
        """计算天乙贵人（以日干查四柱地支）"""
        result = []
        if day_gan in cls.TIANYI_GUIREN:
            for zhi in cls.TIANYI_GUIREN[day_gan]:
                if zhi in pillars:
                    result.append('天乙贵人')
                    break
        return result

    @classmethod
    def calculate_taiji_guiren(cls, day_gan: str, pillars: List[str]) -> List[str]:
        """计算太极贵人（以日干查四柱地支）"""
        result = []
        if day_gan in cls.TAIJI_GUIREN:
            for zhi in cls.TAIJI_GUIREN[day_gan]:
                if zhi in pillars:
                    result.append('太极贵人')
                    break
        return result

    @classmethod
    def calculate_wenchang_guiren(cls, day_gan: str, pillars: List[str]) -> List[str]:
        """计算文昌贵人（以日干或年干查四柱地支）"""
        result = []
        if day_gan in cls.WENCHANG_GUIREN:
            if cls.WENCHANG_GUIREN[day_gan] in pillars:
                result.append('文昌贵人')
        return result

    @classmethod
    def calculate_tiande_guiren(cls, month: int, gan_zhi_list: List[Tuple[str, str]]) -> List[str]:
        """计算天德贵人（以月支查四柱天干地支）"""
        result = []
        if month in cls.TIANDE_GUIREN:
            tiande = cls.TIANDE_GUIREN[month]
            # 检查四柱天干和地支
            for gan, zhi in gan_zhi_list:
                if gan == tiande or zhi == tiande:
                    result.append('天德贵人')
                    break
        return result

    @classmethod
    def calculate_yuede_guiren(cls, month_zhi: str, gan_zhi_list: List[Tuple[str, str]]) -> List[str]:
        """计算月德贵人（以月支查四柱天干）"""
        result = []
        if month_zhi in cls.YUEDE_GUIREN:
            yuede = cls.YUEDE_GUIREN[month_zhi]
            for gan, _ in gan_zhi_list:
                if gan == yuede:
                    result.append('月德贵人')
                    break
        return result

    @classmethod
    def calculate_yima(cls, year_zhi: str, day_zhi: str, pillars: List[str]) -> List[str]:
        """计算驿马（以年支或日支查四柱地支）"""
        result = []
        # 以年支查
        if year_zhi in cls.YIMA and cls.YIMA[year_zhi] in pillars:
            result.append('驿马')
        # 以日支查（如果还没有找到）
        elif day_zhi in cls.YIMA and cls.YIMA[day_zhi] in pillars:
            result.append('驿马')
        return result

    @classmethod
    def calculate_huagai(cls, year_zhi: str, day_zhi: str, pillars: List[str]) -> List[str]:
        """计算华盖（以年支或日支查四柱地支）"""
        result = []
        if year_zhi in cls.HUAGAI and cls.HUAGAI[year_zhi] in pillars:
            result.append('华盖')
        elif day_zhi in cls.HUAGAI and cls.HUAGAI[day_zhi] in pillars:
            result.append('华盖')
        return result

    @classmethod
    def calculate_jiangxing(cls, year_zhi: str, day_zhi: str, pillars: List[str]) -> List[str]:
        """计算将星（以年支或日支查四柱地支）"""
        result = []
        if year_zhi in cls.JIANGXING and cls.JIANGXING[year_zhi] in pillars:
            result.append('将星')
        elif day_zhi in cls.JIANGXING and cls.JIANGXING[day_zhi] in pillars:
            result.append('将星')
        return result

    @classmethod
    def calculate_taohua(cls, year_zhi: str, day_zhi: str, pillars: List[str]) -> List[str]:
        """计算桃花（以年支或日支查四柱地支）"""
        result = []
        if year_zhi in cls.TAOHUA and cls.TAOHUA[year_zhi] in pillars:
            result.append('桃花')
        elif day_zhi in cls.TAOHUA and cls.TAOHUA[day_zhi] in pillars:
            result.append('桃花')
        return result

    @classmethod
    def calculate_hongyan(cls, day_gan: str, pillars: List[str]) -> List[str]:
        """计算红艳（以日干查四柱地支）"""
        result = []
        if day_gan in cls.HONGYAN and cls.HONGYAN[day_gan] in pillars:
            result.append('红艳')
        return result

    @classmethod
    def calculate_guchen_guasu(cls, year_zhi: str, pillars: List[str]) -> List[str]:
        """计算孤辰寡宿（以年支查四柱地支）"""
        result = []
        if year_zhi in cls.GUCHEN_GUASU:
            guchen, guasu = cls.GUCHEN_GUASU[year_zhi]
            if guchen in pillars:
                result.append('孤辰')
            if guasu in pillars:
                result.append('寡宿')
        return result

    @classmethod
    def calculate_yangren(cls, day_gan: str, pillars: List[str]) -> List[str]:
        """计算羊刃（以日干查四柱地支）"""
        result = []
        if day_gan in cls.YANGREN and cls.YANGREN[day_gan] in pillars:
            result.append('羊刃')
        return result

    @classmethod
    def calculate_lushen(cls, day_gan: str, pillars: List[str]) -> List[str]:
        """计算禄神（以日干查四柱地支）"""
        result = []
        if day_gan in cls.LUSHEN and cls.LUSHEN[day_gan] in pillars:
            result.append('禄神')
        return result

    @classmethod
    def calculate_jiesha(cls, year_zhi: str, day_zhi: str, pillars: List[str]) -> List[str]:
        """计算劫煞（以年支或日支查四柱地支）"""
        result = []
        if year_zhi in cls.JIESHA and cls.JIESHA[year_zhi] in pillars:
            result.append('劫煞')
        elif day_zhi in cls.JIESHA and cls.JIESHA[day_zhi] in pillars:
            result.append('劫煞')
        return result

    @classmethod
    def calculate_wangshen(cls, year_zhi: str, day_zhi: str, pillars: List[str]) -> List[str]:
        """计算亡神（以年支或日支查四柱地支）"""
        result = []
        if year_zhi in cls.WANGSHEN and cls.WANGSHEN[year_zhi] in pillars:
            result.append('亡神')
        elif day_zhi in cls.WANGSHEN and cls.WANGSHEN[day_zhi] in pillars:
            result.append('亡神')
        return result

    @classmethod
    def calculate_tianluo_diwang(cls, pillars: List[str]) -> List[str]:
        """计算天罗地网（查四柱地支中是否有辰戌）"""
        result = []
        if '辰' in pillars:
            result.append('天罗')
        if '戌' in pillars:
            result.append('地网')
        return result

    @classmethod
    def calculate_jinyu(cls, day_gan: str, pillars: List[str]) -> List[str]:
        """计算金舆（以日干查四柱地支）"""
        result = []
        if day_gan in cls.JINYU and cls.JINYU[day_gan] in pillars:
            result.append('金舆')
        return result

    @classmethod
    def calculate_guoyin(cls, day_gan: str, pillars: List[str]) -> List[str]:
        """计算国印贵人（以日干查四柱地支）"""
        result = []
        if day_gan in cls.GUOYIN and cls.GUOYIN[day_gan] in pillars:
            result.append('国印')
        return result

    @classmethod
    def calculate_xuetang(cls, day_gan: str, pillars: List[str]) -> List[str]:
        """计算学堂（以日干查四柱地支）"""
        result = []
        if day_gan in cls.XUETANG and cls.XUETANG[day_gan] in pillars:
            result.append('学堂')
        return result

    @classmethod
    def calculate_ciguan(cls, day_gan: str, gan_zhi_list: List[Tuple[str, str]]) -> List[str]:
        """计算词馆（以日干查四柱干支组合）"""
        result = []
        if day_gan in cls.CIGUAN:
            target_gan, target_zhi = cls.CIGUAN[day_gan]
            for gan, zhi in gan_zhi_list:
                if gan == target_gan and zhi == target_zhi:
                    result.append('词馆')
                    break
        return result

    @classmethod
    def calculate_all_shensha(cls, bazi_info: Dict) -> Dict[str, any]:
        """
        计算所有神煞

        Args:
            bazi_info: 八字信息字典

        Returns:
            神煞信息字典
        """
        pillars = bazi_info['pillars']
        year_gan = pillars['year']['gan']
        year_zhi = pillars['year']['zhi']
        month_gan = pillars['month']['gan']
        month_zhi = pillars['month']['zhi']
        day_gan = pillars['day']['gan']
        day_zhi = pillars['day']['zhi']
        hour_gan = pillars['hour']['gan']
        hour_zhi = pillars['hour']['zhi']

        # 四柱地支列表
        zhi_list = [year_zhi, month_zhi, day_zhi, hour_zhi]

        # 四柱干支组合列表
        gan_zhi_list = [
            (year_gan, year_zhi),
            (month_gan, month_zhi),
            (day_gan, day_zhi),
            (hour_gan, hour_zhi)
        ]

        # 月份（从农历信息获取）
        month = bazi_info['lunar']['month']

        # 收集所有神煞
        all_shensha = []

        # 计算各种神煞
        all_shensha.extend(cls.calculate_tianyi_guiren(day_gan, zhi_list))
        all_shensha.extend(cls.calculate_taiji_guiren(day_gan, zhi_list))
        all_shensha.extend(cls.calculate_wenchang_guiren(day_gan, zhi_list))
        all_shensha.extend(cls.calculate_tiande_guiren(month, gan_zhi_list))
        all_shensha.extend(cls.calculate_yuede_guiren(month_zhi, gan_zhi_list))
        all_shensha.extend(cls.calculate_yima(year_zhi, day_zhi, zhi_list))
        all_shensha.extend(cls.calculate_huagai(year_zhi, day_zhi, zhi_list))
        all_shensha.extend(cls.calculate_jiangxing(year_zhi, day_zhi, zhi_list))
        all_shensha.extend(cls.calculate_taohua(year_zhi, day_zhi, zhi_list))
        all_shensha.extend(cls.calculate_hongyan(day_gan, zhi_list))
        all_shensha.extend(cls.calculate_guchen_guasu(year_zhi, zhi_list))
        all_shensha.extend(cls.calculate_yangren(day_gan, zhi_list))
        all_shensha.extend(cls.calculate_lushen(day_gan, zhi_list))
        all_shensha.extend(cls.calculate_jiesha(year_zhi, day_zhi, zhi_list))
        all_shensha.extend(cls.calculate_wangshen(year_zhi, day_zhi, zhi_list))
        all_shensha.extend(cls.calculate_tianluo_diwang(zhi_list))
        all_shensha.extend(cls.calculate_jinyu(day_gan, zhi_list))
        all_shensha.extend(cls.calculate_guoyin(day_gan, zhi_list))
        all_shensha.extend(cls.calculate_xuetang(day_gan, zhi_list))
        all_shensha.extend(cls.calculate_ciguan(day_gan, gan_zhi_list))

        # 去重
        unique_shensha = list(set(all_shensha))

        # 分类神煞
        ji_shensha = []  # 吉神
        xiong_shensha = []  # 凶神

        ji_list = ['天乙贵人', '太极贵人', '文昌贵人', '天德贵人', '月德贵人',
                   '金舆', '国印', '学堂', '词馆', '禄神', '将星']
        xiong_list = ['羊刃', '劫煞', '亡神', '天罗', '地网', '孤辰', '寡宿']
        zhong_list = ['驿马', '华盖', '桃花', '红艳']  # 中性神煞

        for shensha in unique_shensha:
            if shensha in ji_list:
                ji_shensha.append(shensha)
            elif shensha in xiong_list:
                xiong_shensha.append(shensha)

        # 构建神煞详细信息
        shensha_details = []
        for shensha in unique_shensha:
            shensha_details.append({
                'name': shensha,
                'description': cls.SHENSHA_DESC.get(shensha, ''),
                'type': 'ji' if shensha in ji_list else ('xiong' if shensha in xiong_list else 'zhong')
            })

        return {
            'all': unique_shensha,
            'ji': ji_shensha,
            'xiong': xiong_shensha,
            'details': shensha_details,
            'count': len(unique_shensha)
        }
