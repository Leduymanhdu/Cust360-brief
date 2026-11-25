export type UserRole = 'ADMIN' | 'SALES' | 'SERVICE';

export interface UserSummary {
  id: string;
  email: string;
  role: UserRole;
  full_name: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: 'Bearer';
  expires_in: number;
  user: UserSummary;
}
