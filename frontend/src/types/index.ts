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
