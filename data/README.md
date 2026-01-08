# 数据文件说明

本目录包含易学系统的各种数据文件，采用 JSON 格式存储，便于维护、扩展和国际化。

## 目录结构

```
data/
├── gua/                    # 卦象数据
│   ├── 000000_001001.json # 坤卦系列
│   ├── 001010_001111.json # 其他卦象...
│   └── ...
├── qimen_guide.json        # 奇门遁甲指南数据
├── bazi_guide.json         # 八字排盘指南数据
└── README.md               # 本文件
```

## 文件说明

### 1. gua/ - 卦象数据

存储64卦的详细信息，每个文件包含多个卦象。

**数据结构**：
```json
{
  "二进制编码": {
    "name": "卦名",
    "alternate_name": "别名",
    "symbol": "卦象符号",
    "description": "卦辞",
    "yaoci": ["爻辞数组"]
  }
}
```

### 2. qimen_guide.json - 奇门遁甲指南

包含奇门遁甲的完整说明和定义数据。

**主要内容**：
- `introduction`: 基本介绍
- `elements`: 九宫格元素说明（地盘、天盘、八门、九星、八神）
- `four_pillars`: 四柱用神定义
  - `pillars`: 年干、月干、日干、时干的含义
  - `examples`: 实际应用举例
- `bagua_palaces`: 八卦宫位含义（方位、五行、象征）
- `yongshen_meanings`: 用神宫位映射（1-9宫的用神含义）
- `fortune_judgment`: 吉凶判断标准
  - 吉门、凶门、平门
  - 吉星、凶星、中性星
  - 吉神、凶神、中性神
  - 三奇（日奇、月奇、星奇）
- `interpretation_steps`: 解读步骤

**使用场景**：
- 前端通过 `/api/guide/qimen` 获取
- 用于奇门遁甲使用指南弹窗
- 用于九宫格的用神含义显示

### 3. bazi_guide.json - 八字排盘指南

包含八字排盘的完整说明和定义数据。

**主要内容**：
- `introduction`: 基本介绍
- `pillars`: 四柱说明（年柱、月柱、日柱、时柱）
- `tiangan`: 十天干详解
  - 天干名称、五行属性、阴阳性质
  - 特征描述
- `dizhi`: 十二地支详解
  - 地支名称、对应生肖、五行属性
  - 时辰范围、季节归属
- `wuxing`: 五行分析
  - 五行属性（木、火、土、金、水）
  - 颜色、特征、对应身体部位
  - 相生相克关系
  - 五行平衡说明
- `shensha`: 神煞说明
  - 吉神列表和含义
  - 凶神列表和含义
  - 使用注意事项
- `calendar_systems`: 历法系统说明
  - 公历、农历、节气的区别
  - 八字排盘中的历法应用
- `usage_tips`: 使用建议

**使用场景**：
- 前端通过 `/api/guide/bazi` 获取
- 可用于八字排盘的帮助系统
- 可用于天干地支、五行、神煞的解释说明

## API 访问

### 获取奇门遁甲指南
```
GET /api/guide/qimen
```

### 获取八字排盘指南
```
GET /api/guide/bazi
```

### 获取所有指南
```
GET /api/guide/
```

## 数据维护

### 添加新内容
1. 直接编辑对应的 JSON 文件
2. 保持 JSON 格式正确（建议使用 JSON 验证工具）
3. 重启后端服务即可生效（无需重新构建）

### 数据验证
```bash
# 验证 JSON 格式
python -m json.tool qimen_guide.json
python -m json.tool bazi_guide.json
```

### 国际化支持
未来可以扩展为多语言支持：
```
data/
├── qimen_guide.zh-CN.json
├── qimen_guide.en.json
├── bazi_guide.zh-CN.json
└── bazi_guide.en.json
```

## 设计原则

1. **数据与逻辑分离**：所有说明性文字存储在数据文件中，代码只负责展示
2. **易于维护**：JSON 格式便于编辑和版本控制
3. **可扩展性**：结构化设计便于添加新内容
4. **国际化友好**：支持多语言扩展
5. **API 驱动**：前端通过 API 动态加载，便于缓存和更新

## 注意事项

1. 修改数据文件后需要重启后端服务
2. 确保 JSON 格式正确，否则会导致 API 报错
3. 文件编码必须为 UTF-8
4. 避免在数据中使用特殊字符，或正确转义
5. 大型数据更新建议先在测试环境验证

## 扩展建议

未来可以考虑添加的数据文件：
- `divination_guide.json` - 周易占卜指南
- `terms_glossary.json` - 术语词汇表
- `examples.json` - 案例库
- `faq.json` - 常见问题
