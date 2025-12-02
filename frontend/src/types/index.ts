// ============ 卦象相关类型 ============

export interface GuaInfo {
  name: string;
  binary: string;
  description: string;
  image: string;
  yaoci?: string[];
}

export interface ChangingLine {
  position: number;
  yaoci: string;
}

export interface GuaListItem {
  binary: string;
  name: string;
  alternate_name?: string;
  description: string;
  yaoci?: string[];
  image?: string;
}

// ============ 占卜请求/响应类型 ============

export interface DivinationRequest {
  numbers: number[];
  question?: string;
}

export interface RandomDivinationRequest {
  question?: string;
}

export interface DivinationResult {
  ben_gua: GuaInfo;
  bian_gua: GuaInfo;
  changing_lines: ChangingLine[];
  question?: string;
  numbers?: number[];
}

// ============ 解卦请求/响应类型 ============

export interface InterpretationRequest {
  question: string;
  ben_gua: GuaInfo;
  bian_gua: GuaInfo;
  changing_lines: ChangingLine[];
}

export interface InterpretationResult {
  interpretation: string;
  summary: string;
}

// ============ 通用类型 ============

export interface ErrorResponse {
  detail: string;
  code?: string;
}
