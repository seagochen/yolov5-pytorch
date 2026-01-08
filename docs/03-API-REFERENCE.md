# API 参考文档

## 基础信息

- **Base URL**: `http://localhost:8000`
- **Content-Type**: `application/json`

## 占卜接口

### 计算卦象

根据六个数字计算本卦和变卦。

**请求**

```
POST /api/divination/calculate
```

```json
{
  "numbers": [7, 8, 9, 6, 7, 8],
  "question": "我的事业发展如何？"
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| numbers | number[] | 是 | 6个数字，范围 6-9 |
| question | string | 是 | 占卜问题 |

**响应**

```json
{
  "numbers": [7, 8, 9, 6, 7, 8],
  "ben_gua": {
    "index": 11,
    "name": "泰",
    "symbol": "䷊",
    "description": "地天泰",
    "judgement": "小往大来，吉，亨"
  },
  "bian_gua": {
    "index": 19,
    "name": "临",
    "symbol": "䷒",
    "description": "地泽临",
    "judgement": "元亨利贞"
  },
  "changing_lines": [
    {
      "position": 3,
      "yaoci": "九三：无平不陂，无往不复"
    },
    {
      "position": 4,
      "yaoci": "六四：翩翩不富，以其邻"
    }
  ]
}
```

### 随机占卜

模拟三枚硬币投掷，生成随机卦象。

**请求**

```
POST /api/divination/random
```

```json
{
  "question": "最近的感情运势如何？"
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| question | string | 是 | 占卜问题 |

**响应**

与计算卦象接口相同。

### 获取卦象信息

根据卦序号获取完整卦象数据。

**请求**

```
GET /api/divination/gua/{index}
```

| 参数 | 类型 | 说明 |
|------|------|------|
| index | number | 卦序号 (1-64) |

**响应**

```json
{
  "index": 1,
  "name": "乾",
  "symbol": "䷀",
  "description": "乾为天",
  "judgement": "元亨利贞",
  "image": "天行健，君子以自强不息",
  "lines": [
    {
      "position": 1,
      "yaoci": "初九：潜龙勿用"
    },
    {
      "position": 2,
      "yaoci": "九二：见龙在田，利见大人"
    }
  ]
}
```

## AI 解卦接口

### 分析卦象

调用 Gemini AI 对卦象进行解读。

**请求**

```
POST /api/interpretation/analyze
```

```json
{
  "question": "我的事业发展如何？",
  "ben_gua": {
    "index": 11,
    "name": "泰",
    "symbol": "䷊",
    "description": "地天泰"
  },
  "bian_gua": {
    "index": 19,
    "name": "临",
    "symbol": "䷒",
    "description": "地泽临"
  },
  "changing_lines": [
    {
      "position": 3,
      "yaoci": "九三：无平不陂，无往不复"
    }
  ]
}
```

**响应**

```json
{
  "summary": "泰卦主通达顺利，变临卦示机遇将至...",
  "interpretation": "此卦显示您的事业正处于上升期..."
}
```

## 八字排盘接口

### 计算八字

根据出生时间计算四柱八字。

**请求**

```
POST /api/bazi/calculate
```

```json
{
  "name": "张三",
  "calendar": "solar",
  "year": 1990,
  "month": 5,
  "day": 15,
  "hour": 10,
  "minute": 30
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| name | string | 是 | 姓名 |
| calendar | string | 是 | 历法类型："solar"（公历）或 "lunar"（农历） |
| year | number | 是 | 年份 |
| month | number | 是 | 月份 (1-12) |
| day | number | 是 | 日期 (1-31) |
| hour | number | 是 | 小时 (0-23) |
| minute | number | 是 | 分钟 (0-59) |

**响应**

```json
{
  "name": "张三",
  "solar_date": "1990-05-15",
  "lunar_date": "农历四月廿一",
  "pillars": {
    "year": {"gan": "庚", "zhi": "午"},
    "month": {"gan": "辛", "zhi": "巳"},
    "day": {"gan": "甲", "zhi": "子"},
    "hour": {"gan": "己", "zhi": "巳"}
  },
  "wuxing": {
    "wood": 1,
    "fire": 3,
    "earth": 2,
    "metal": 2,
    "water": 1
  },
  "shensha": {
    "auspicious": ["天乙贵人", "文昌星"],
    "inauspicious": ["羊刃"]
  }
}
```

## 奇门遁甲接口

### 排盘计算

根据时间进行奇门遁甲排盘。

**请求**

```
POST /api/qimen/calculate
```

```json
{
  "year": 2025,
  "month": 1,
  "day": 8,
  "hour": 14,
  "minute": 30
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| year | number | 是 | 年份 |
| month | number | 是 | 月份 (1-12) |
| day | number | 是 | 日期 (1-31) |
| hour | number | 是 | 小时 (0-23) |
| minute | number | 是 | 分钟 (0-59) |

**响应**

```json
{
  "time": "2025-01-08 14:30",
  "solar_term": "小寒",
  "ju": "阳遁一局",
  "zhifu_palace": 6,
  "palaces": {
    "1": {
      "bagua": "坎",
      "dipan": "戊",
      "tianpan": "己",
      "door": "休门",
      "star": "天蓬",
      "god": "值符",
      "fortune": 3
    },
    "2": {...},
    ...
  },
  "analysis": {
    "best_direction": "乾宫（西北）",
    "worst_direction": "坤宫（西南）",
    "suggestion": "整体吉利，宜主动出击"
  }
}
```

## 指南数据接口

### 获取奇门遁甲指南

获取奇门遁甲的完整使用指南和定义数据。

**请求**

```
GET /api/guide/qimen
```

**响应**

```json
{
  "introduction": {
    "title": "奇门遁甲简介",
    "content": "奇门遁甲是中国古代三式之一..."
  },
  "elements": {
    "dipan": {...},
    "tianpan": {...},
    "doors": {...},
    "stars": {...},
    "gods": {...}
  },
  "four_pillars": {
    "pillars": [...],
    "examples": [...]
  },
  "bagua_palaces": [...],
  "yongshen_meanings": {...},
  "fortune_judgment": {...},
  "interpretation_steps": [...]
}
```

### 获取八字指南

获取八字排盘的完整使用指南和定义数据。

**请求**

```
GET /api/guide/bazi
```

**响应**

```json
{
  "introduction": {...},
  "pillars": [...],
  "tiangan": {
    "items": [
      {
        "name": "甲",
        "element": "阳木",
        "characteristics": ["生发", "向上", "刚健"]
      },
      ...
    ]
  },
  "dizhi": {...},
  "wuxing": {...},
  "shensha": {...},
  "calendar_systems": {...},
  "usage_tips": [...]
}
```

### 获取所有指南

获取所有模块的指南数据。

**请求**

```
GET /api/guide/
```

**响应**

```json
{
  "qimen": {...},
  "bazi": {...}
}
```

## 错误响应

所有接口在出错时返回统一格式：

```json
{
  "detail": "错误描述信息"
}
```

常见状态码：

| 状态码 | 说明 |
|--------|------|
| 400 | 请求参数错误 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

## 数据模型

### GuaInfo

卦象基本信息。

```typescript
interface GuaInfo {
  index: number;      // 卦序号 (1-64)
  name: string;       // 卦名
  symbol?: string;    // Unicode 卦符
  description: string; // 卦象描述
  judgement?: string; // 卦辞
  image?: string;     // 象辞
  lines?: Line[];     // 爻辞
}
```

### ChangingLine

变爻信息。

```typescript
interface ChangingLine {
  position: number;  // 爻位 (1-6)
  yaoci: string;     // 爻辞
}
```

### DivinationResponse

占卜响应。

```typescript
interface DivinationResponse {
  numbers?: number[];        // 占卜数字
  ben_gua: GuaInfo;          // 本卦
  bian_gua: GuaInfo;         // 变卦
  changing_lines: ChangingLine[]; // 变爻列表
}
```

### InterpretationResponse

AI 解读响应。

```typescript
interface InterpretationResponse {
  summary: string;        // 简要总结
  interpretation: string; // 详细解读
}
```
