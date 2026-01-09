// 类型定义
export interface GuaInfo {
  name: string;
  binary: string;
  description: string;
  image: string;
  symbol?: string;
  yaoci?: string[];
}

export interface ChangingLine {
  position: number;
  yaoci: string;
}

export interface DivinationResponse {
  ben_gua: GuaInfo;
  bian_gua: GuaInfo;
  changing_lines: ChangingLine[];
  question?: string;
  numbers?: number[];
}

export interface InterpretationResponse {
  interpretation: string;
  summary: string;
}

export interface RandomDivinationRequest {
  question?: string;
}

export interface InterpretationRequest {
  question: string;
  ben_gua: GuaInfo;
  bian_gua: GuaInfo;
  changing_lines: ChangingLine[];
}

// 八字相关类型
export interface PillarInfo {
  gan: string;
  zhi: string;
}

export interface LunarInfo {
  year: number;
  month: number;
  day: number;
  is_leap: boolean;
  gan_zhi_year: string;
  sheng_xiao: string;
  formatted: string;
}

export interface SolarInfo {
  year: number;
  month: number;
  day: number;
  hour: number;
  minute: number;
  formatted: string;
}

export interface BaziRequest {
  year: number;
  month: number;
  day: number;
  hour: number;
  minute?: number;
}

export interface ShenshaDetail {
  name: string;
  description: string;
  type: string;
}

export interface ShenshaPillar {
  year: ShenshaDetail[];
  month: ShenshaDetail[];
  day: ShenshaDetail[];
  hour: ShenshaDetail[];
}

export interface ShenshaInfo {
  all: string[];
  ji: string[];
  xiong: string[];
  details: ShenshaDetail[];
  count: number;
  by_pillar: ShenshaPillar;
}

export interface CangGan {
  year: string[];
  month: string[];
  day: string[];
  hour: string[];
}

export interface Nayin {
  year: string;
  month: string;
  day: string;
  hour: string;
}

export interface Shishen {
  year_gan: string;
  month_gan: string;
  day_gan: string;
  hour_gan: string;
}

export interface CangganShishen {
  year: string[];
  month: string[];
  day: string[];
  hour: string[];
}

export interface BaziResponse {
  year_pillar: string;
  month_pillar: string;
  day_pillar: string;
  hour_pillar: string;
  pillars: {
    year: PillarInfo;
    month: PillarInfo;
    day: PillarInfo;
    hour: PillarInfo;
  };
  cang_gan: CangGan;
  nayin: Nayin;
  shishen: Shishen;
  canggan_shishen: CangganShishen;
  wu_xing: Record<string, string>;
  wu_xing_count: Record<string, number>;
  yin_yang: Record<string, string>;
  bazi_string: string;
  lunar: LunarInfo;
  solar: SolarInfo;
  shensha: ShenshaInfo;
}

export interface LunarConversionRequest {
  year: number;
  month: number;
  day: number;
}

// 城市和时区相关类型
export interface CityInfo {
  name: string;
  name_en: string;
  country: string;
  longitude: number;
  latitude: number;
  timezone: number;
  timezone_abbr: string;
}

export interface TimezoneInfo {
  value: number;
  label: string;
}

export interface CitiesData {
  cities: CityInfo[];
  timezones: TimezoneInfo[];
}

// 奇门遁甲相关类型
export interface GongInfo {
  gong_name: string;
  ba_gua: string;
  direction: string;  // 方位
  di_pan: string;
  tian_pan: string;
  ba_men: string;
  jiu_xing: string;
  ba_shen: string;
  ji_xiong: string;
  ji_score: number;
  xiong_score: number;
  notes: string[];
}

export interface QimenZongPing {
  overall: string;
  summary: string;
  ji_count: number;
  xiong_count: number;
  best_gong: number;
  best_gong_name: string;
  worst_gong: number;
  worst_gong_name: string;
  advice: string;
}

export interface QimenRequest {
  year: number;
  month: number;
  day: number;
  hour: number;
  minute?: number;
}

export interface QimenResponse {
  date_time: string;
  term: string;
  yuan: string;
  dun_type: string;
  ju_number: number;
  zhi_fu_gong: number;
  jiu_gong: Record<number, GongInfo>;
  zong_ping: QimenZongPing;
}

// 指南相关类型
export interface QimenGuideData {
  introduction: {
    title: string;
    description: string;
  };
  elements: {
    title: string;
    items: Array<{
      name: string;
      description: string;
    }>;
  };
  four_pillars: {
    title: string;
    description: string;
    pillars: Array<{
      name: string;
      gong: string;
      meaning: string;
    }>;
    examples: Array<{
      scenario: string;
      pillar: string;
      explanation: string;
    }>;
  };
  bagua_palaces: {
    title: string;
    palaces: Array<{
      number: number;
      name: string;
      direction: string;
      element: string;
      meanings: string[];
    }>;
  };
  yongshen_meanings: {
    title: string;
    meanings: Record<string, Array<{
      name: string;
      meaning: string;
    }>>;
  };
  fortune_judgment: {
    title: string;
    categories: Array<{
      type: string;
      items: any[];
    }>;
  };
  interpretation_steps: {
    title: string;
    steps: string[];
  };
}

export interface BaziGuideData {
  introduction: {
    title: string;
    description: string;
  };
  pillars: {
    title: string;
    description: string;
    items: Array<{
      name: string;
      description: string;
      composition: string;
    }>;
  };
  tiangan: {
    title: string;
    items: Array<{
      name: string;
      element: string;
      characteristics: string[];
    }>;
  };
  dizhi: {
    title: string;
    items: Array<{
      name: string;
      zodiac: string;
      element: string;
      time: string;
      season: string;
    }>;
  };
  wuxing: any;
  shensha: any;
  calendar_systems: any;
  usage_tips: any;
}
