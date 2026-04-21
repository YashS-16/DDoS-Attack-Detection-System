import axios from 'axios';

const API_BASE_URL = '/api';

export const api = axios.create({
  baseURL: API_BASE_URL,
});

export interface LogEntry {
  packet_id: number;
  timestamp: string;
  prediction: string;
  risk_score: number;
  severity: string;
  alert: string;
  anomaly: boolean;
  reconstruction_error: number;
  models: {
    rf_prob: number;
    xgb_prob: number;
    lr_prob: number;
  };
  ip: string;
  attack_type: string;
}

export const fetchLogs = async (): Promise<LogEntry[]> => {
  const response = await api.get('/data');
  return [...(response.data.logs || [])];
};

export const startMonitoring = async (): Promise<{status: string, message: string}> => {
  const response = await api.post('/start_monitoring');
  return response.data;
};

export const stopMonitoring = async (): Promise<{status: string, message: string}> => {
  const response = await api.post('/stop_monitoring');
  return response.data;
};

export const getStatus = async (): Promise<{is_running: boolean}> => {
  const response = await api.get('/status');
  return response.data;
};
