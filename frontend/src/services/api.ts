import axios from 'axios';
import type {
  RequirementsInput,
  QualificationResponse,
  ValidationResponse,
  GenerateTADInput,
  GenerateTADResponse,
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const qualifyRequirements = async (
  requirements: string
): Promise<QualificationResponse> => {
  const response = await api.post<QualificationResponse>('/api/qualify', {
    requirements,
  });
  return response.data;
};

export const validateQualification = async (
  qualification: any
): Promise<ValidationResponse> => {
  const response = await api.post<ValidationResponse>('/api/validate', {
    qualification,
  });
  return response.data;
};

export const generateTAD = async (
  requirements: Record<string, any>
): Promise<GenerateTADResponse> => {
  const response = await api.post<GenerateTADResponse>('/api/generate-tad', {
    requirements,
  });
  return response.data;
};

export default api;
