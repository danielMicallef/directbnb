import { apiClient, setTokens, clearTokens } from '../api-client';
import type {
  User,
  LoginRequest,
  LoginResponse,
  RegisterRequest,
  RegisterResponse,
  ChangePasswordRequest,
  TokenRefreshRequest,
  TokenRefreshResponse,
  ResendVerificationRequest,
} from '@/types/api';

export const authApi = {
  // Authentication
  async login(credentials: LoginRequest): Promise<LoginResponse> {
    const response = await apiClient.post<LoginResponse>('/auth/login/', credentials);
    // Store tokens after successful login
    if (response.access && response.refresh) {
      setTokens(response.access, response.refresh);
    }
    return response;
  },

  async register(data: RegisterRequest): Promise<RegisterResponse> {
    return apiClient.post<RegisterResponse>('/auth/register/', data);
  },

  async logout(): Promise<void> {
    try {
      await apiClient.post<void>('/auth/logout/');
    } finally {
      // Clear tokens regardless of API response
      clearTokens();
    }
  },

  async refreshToken(refreshToken: string): Promise<TokenRefreshResponse> {
    const response = await apiClient.post<TokenRefreshResponse>(
      '/auth/token/refresh/',
      { refresh: refreshToken } as TokenRefreshRequest
    );
    // Update tokens after successful refresh
    if (response.access && response.refresh) {
      setTokens(response.access, response.refresh);
    }
    return response;
  },

  async resendVerification(data: ResendVerificationRequest): Promise<void> {
    return apiClient.post<void>('/auth/resend-verification/', data);
  },

  // User Profile
  async getCurrentUser(): Promise<User> {
    return apiClient.get<User>('/auth/me/');
  },

  async updateCurrentUser(data: Partial<Omit<User, 'id' | 'is_email_confirmed' | 'registered_at'>>): Promise<User> {
    return apiClient.patch<User>('/auth/me/', data);
  },

  async changePassword(data: ChangePasswordRequest): Promise<void> {
    return apiClient.post<void>('/auth/change-password/', data);
  },
};
