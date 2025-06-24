import axios from 'axios';
import { LoginResponse, User, Reservation, ReservationCreate, ReservationConfirmRejection, GPUServer } from '../types';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const authAPI = {
  login: async (username: string, password: string): Promise<LoginResponse> => {
    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);
    const response = await api.post<LoginResponse>('/api/auth/login', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  register: async (username: string, email: string, password: string): Promise<User> => {
    const response = await api.post<User>('/api/auth/register', {
      username,
      email,
      password,
    });
    return response.data;
  },

  getMe: async (): Promise<User> => {
    const response = await api.get<User>('/api/auth/me');
    return response.data;
  },
};

export const reservationAPI = {
  getReservations: async (pendingRejection?: boolean): Promise<Reservation[]> => {
    const params = pendingRejection ? { pending_rejection: true } : {};
    const response = await api.get<Reservation[]>('/api/reservations', { params });
    return response.data;
  },

  createReservation: async (data: ReservationCreate): Promise<Reservation> => {
    const response = await api.post<Reservation>('/api/reservations', data);
    return response.data;
  },

  cancelReservation: async (id: number): Promise<void> => {
    await api.delete(`/api/reservations/${id}`);
  },

  confirmRejection: async (id: number, data: ReservationConfirmRejection): Promise<Reservation> => {
    const response = await api.post<Reservation>(`/api/reservations/${id}/confirm-rejection`, data);
    return response.data;
  },
};

export const serverAPI = {
  getServers: async (): Promise<GPUServer[]> => {
    const response = await api.get<GPUServer[]>('/api/servers');
    return response.data;
  },
};