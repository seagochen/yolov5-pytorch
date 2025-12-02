import axios from 'axios';
import type {
  DivinationResult,
  InterpretationResult,
  DivinationRequest,
  RandomDivinationRequest,
  InterpretationRequest,
  GuaListItem
} from '../types';

// 创建 axios 实例
const api = axios.create({
  baseURL: '/api',
  timeout: 60000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 响应拦截器处理错误
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const message = error.response?.data?.detail || error.message || '请求失败';
    return Promise.reject(new Error(message));
  }
);

// 占卜相关 API
export const divinationApi = {
  // 根据数字计算卦象
  calculate: async (request: DivinationRequest): Promise<DivinationResult> => {
    const response = await api.post<DivinationResult>('/divination/calculate', request);
    return response.data;
  },

  // 随机摇卦
  random: async (request: RandomDivinationRequest): Promise<DivinationResult> => {
    const response = await api.post<DivinationResult>('/divination/random', request);
    return response.data;
  },

  // 获取所有64卦列表
  getAllGua: async (): Promise<GuaListItem[]> => {
    const response = await api.get<GuaListItem[]>('/divination/gua');
    return response.data;
  },

  // 根据二进制获取卦象信息
  getGuaByBinary: async (binary: string): Promise<GuaListItem> => {
    const response = await api.get<GuaListItem>(`/divination/gua/${binary}`);
    return response.data;
  },
};

// 解卦相关 API
export const interpretationApi = {
  // AI 解卦
  analyze: async (request: InterpretationRequest): Promise<InterpretationResult> => {
    const response = await api.post<InterpretationResult>('/interpretation/analyze', request);
    return response.data;
  },
};

export default api;
