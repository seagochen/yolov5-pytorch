def get_gua_info(binary, gua_dict):
    if binary in gua_dict:
        return gua_dict[binary]
    else:
        return {'name': '未知卦象', 'description': f'二进制表示 {binary} 未找到对应卦象信息。'}


def generate_gua_image(binary):
    image = []
    for bit in binary:
        if bit == '1':  # 阳爻
            image.append('———')
        else:  # 阴爻
            image.append('— —')
    return '\n'.join(image)


if __name__ == '__main__':
    # 根据二进制查询卦象信息
    from toss_gua import yao_to_binary

    # 示例用法
    yao_list = ['8', '6', '8', '7', '7', '7']
    binary = yao_to_binary(yao_list)
    gua_image = generate_gua_image(binary)
    print(gua_image)