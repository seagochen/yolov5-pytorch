# 投掷结果转换为爻
def toss_to_yao(toss):
    """
    将三枚硬币投掷结果转换为爻值
    :param toss: list[str] 投掷结果（正或反）
    :return: str 爻值
    """
    yao_value = sum([3 if coin == '正' else 2 for coin in toss])
    if yao_value == 6:
        return '6'  # 老阴
    elif yao_value == 7:
        return '7'  # 少阳
    elif yao_value == 8:
        return '8'  # 少阴
    elif yao_value == 9:
        return '9'  # 老阳


# 交互式获取投掷结果
def get_toss_results():
    toss_results = []
    print("请依次输入六次投掷结果，每次输入三个硬币的结果（正或反），用空格分隔。")
    for i in range(6):
        toss = input(f"第{i+1}次投掷结果（例如：正 反 正）：").split()

        # 输入检查, 三个硬币的结果必须为正或反
        while len(toss) != 3 or not all(coin in ['正', '反'] for coin in toss):  #
            toss = input("输入有误，请重新输入（正或反，用空格分隔）：").split()

        # 将投掷结果转换为爻值
        toss_results.append(toss_to_yao(toss))

    return toss_results


# 爻值转换为二进制表示
def yao_to_binary(yao_list, changing=False):
    """
    把爻转换成二进制字符串
    :param yao_list: 6个数字（6,7,8,9）
    :param changing: 是否计算变卦（6变阳, 9变阴）
    :return: 6位二进制字符串（低位在前）
    """
    binary_str = ""
    for yao in yao_list:
        if changing:  # 计算变卦
            if yao == 6:
                binary_str += "1"  # 6 变 阳（⚊）
            elif yao == 9:
                binary_str += "0"  # 9 变 阴（⚋）
            elif yao == 7:
                binary_str += "1"  # 7 保持 阳（⚊）
            elif yao == 8:
                binary_str += "0"  # 8 保持 阴（⚋）
        else:  # 计算本卦
            if yao in [6, 8]:
                binary_str += "0"  # 6、8 是阴（⚋）
            elif yao in [7, 9]:
                binary_str += "1"  # 7、9 是阳（⚊）

    return binary_str[::-1]  # 易经卦象低位在前，高位在后，需反转

