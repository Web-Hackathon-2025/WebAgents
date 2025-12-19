import { post, get } from "./client";
import { LoginCredentials, RegisterData, CustomerRegisterData, ProviderRegisterData, AuthResponse } from "@/types/auth";

export const authApi = {
  login: async (credentials: LoginCredentials): Promise<AuthResponse> => {
    return post<AuthResponse>("/auth/login", credentials);
  },

  registerCustomer: async (data: CustomerRegisterData): Promise<AuthResponse> => {
    return post<AuthResponse>("/auth/register/customer", data);
  },

  registerProvider: async (data: ProviderRegisterData): Promise<AuthResponse> => {
    return post<AuthResponse>("/auth/register/provider", data);
  },

  logout: async (): Promise<void> => {
    return post<void>("/auth/logout");
  },

  refreshToken: async (): Promise<{ accessToken: string }> => {
    return post<{ accessToken: string }>("/auth/refresh");
  },

  verifyEmail: async (token: string): Promise<void> => {
    return post<void>("/auth/verify-email", { token });
  },

  forgotPassword: async (email: string): Promise<void> => {
    return post<void>("/auth/forgot-password", { email });
  },

  resetPassword: async (token: string, password: string): Promise<void> => {
    return post<void>("/auth/reset-password", { token, password });
  },

  getCurrentUser: async (): Promise<AuthResponse["user"]> => {
    return get<AuthResponse["user"]>("/auth/me");
  },
};
