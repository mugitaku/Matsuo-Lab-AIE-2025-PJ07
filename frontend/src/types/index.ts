export interface User {
  id: number;
  username: string;
  email: string;
  role: 'user' | 'admin';
  created_at: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

export interface GPUServer {
  id: number;
  name: string;
  description?: string;
  gpu_type?: string;
  gpu_count: number;
  is_active: boolean;
  created_at: string;
}

export interface Reservation {
  id: number;
  user_id: number;
  server_id: number;
  natural_language_request: string;
  purpose?: string;
  start_time: string;
  end_time: string;
  priority_score: number;
  status: 'pending' | 'confirmed' | 'rejected' | 'cancelled' | 'pending_rejection';
  ai_judgment_reason?: string;
  rejection_reason?: string;
  created_at: string;
  updated_at: string;
  user: User;
  server: GPUServer;
}

export interface ReservationCreate {
  natural_language_request: string;
}

export interface ReservationConfirmRejection {
  confirm: boolean;
  reason?: string;
}