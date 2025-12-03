import axios from 'axios';
import type { DivinationResponse, InterpretationResponse, RandomDivinationRequest, InterpretationRequest } from '../types';

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

export default apiClient;
