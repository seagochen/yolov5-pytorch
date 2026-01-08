import axios from 'axios';
import type {
  DivinationResponse,
  InterpretationResponse,
  RandomDivinationRequest,
  InterpretationRequest,
  BaziRequest,
  BaziResponse,
  LunarConversionRequest,
  LunarInfo,
  QimenRequest,
  QimenResponse
} from '../types';

// 配置API基础URL
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 随机占卜
export const randomDivination = async (request: RandomDivinationRequest): Promise<DivinationResponse> => {
  const response = await apiClient.post<DivinationResponse>('/api/divination/random', request);
  return response.data;
};

// AI解卦
export const interpretGua = async (request: InterpretationRequest): Promise<InterpretationResponse> => {
  const response = await apiClient.post<InterpretationResponse>('/api/interpretation/analyze', request);
  return response.data;
};

// 计算八字
export const calculateBazi = async (request: BaziRequest): Promise<BaziResponse> => {
  const response = await apiClient.post<BaziResponse>('/api/bazi/calculate', request);
  return response.data;
};

// 公历转农历
export const convertToLunar = async (request: LunarConversionRequest): Promise<LunarInfo> => {
  const response = await apiClient.post<LunarInfo>('/api/bazi/lunar-conversion', request);
  return response.data;
};

// 奇门遁甲排盘
export const qimenPaipan = async (request: QimenRequest): Promise<QimenResponse> => {
  const response = await apiClient.post<QimenResponse>('/api/qimen/paipan', request);
  return response.data;
};

// 获取奇门遁甲指南
export const getQimenGuide = async (): Promise<any> => {
  const response = await apiClient.get('/api/guide/qimen');
  return response.data;
};

// 获取八字指南
export const getBaziGuide = async (): Promise<any> => {
  const response = await apiClient.get('/api/guide/bazi');
  return response.data;
};

export default apiClient;
