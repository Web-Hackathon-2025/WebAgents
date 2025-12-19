import { create } from "zustand";
import { persist } from "zustand/middleware";
import { User, LoginCredentials, RegisterData, CustomerRegisterData, ProviderRegisterData } from "@/types/auth";
import { authApi } from "@/lib/api/auth";
import { storage } from "@/lib/utils/storage";

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  
  // Actions
  login: (credentials: LoginCredentials) => Promise<void>;
  register: (data: CustomerRegisterData | ProviderRegisterData) => Promise<void>;
  logout: () => Promise<void>;
  refreshToken: () => Promise<void>;
  checkAuth: () => Promise<void>;
  clearError: () => void;
  setUser: (user: User | null) => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,

      login: async (credentials: LoginCredentials) => {
        set({ isLoading: true, error: null });
        try {
          const response = await authApi.login(credentials);
          
          // Store access token
          if (typeof window !== "undefined") {
            localStorage.setItem("accessToken", response.accessToken);
          }
          
          set({
            user: response.user,
            isAuthenticated: true,
            isLoading: false,
            error: null,
          });
        } catch (error: any) {
          set({
            isLoading: false,
            error: error.message || "Login failed",
            isAuthenticated: false,
            user: null,
          });
          throw error;
        }
      },

      register: async (data: CustomerRegisterData | ProviderRegisterData) => {
        set({ isLoading: true, error: null });
        try {
          const response = data.role === "customer"
            ? await authApi.registerCustomer(data as CustomerRegisterData)
            : await authApi.registerProvider(data as ProviderRegisterData);
          
          // Store access token
          if (typeof window !== "undefined") {
            localStorage.setItem("accessToken", response.accessToken);
          }
          
          set({
            user: response.user,
            isAuthenticated: true,
            isLoading: false,
            error: null,
          });
        } catch (error: any) {
          set({
            isLoading: false,
            error: error.message || "Registration failed",
            isAuthenticated: false,
            user: null,
          });
          throw error;
        }
      },

      logout: async () => {
        try {
          await authApi.logout();
        } catch (error) {
          // Continue with logout even if API call fails
          console.error("Logout API call failed:", error);
        } finally {
          // Clear local state
          if (typeof window !== "undefined") {
            localStorage.removeItem("accessToken");
          }
          
          set({
            user: null,
            isAuthenticated: false,
            error: null,
          });
        }
      },

      refreshToken: async () => {
        try {
          const response = await authApi.refreshToken();
          
          if (typeof window !== "undefined") {
            localStorage.setItem("accessToken", response.accessToken);
          }
        } catch (error: any) {
          // If refresh fails, logout user
          get().logout();
          throw error;
        }
      },

      checkAuth: async () => {
        const token = typeof window !== "undefined" 
          ? localStorage.getItem("accessToken") 
          : null;
        
        if (!token) {
          set({ isAuthenticated: false, user: null });
          return;
        }

        set({ isLoading: true });
        try {
          const user = await authApi.getCurrentUser();
          set({
            user,
            isAuthenticated: true,
            isLoading: false,
            error: null,
          });
        } catch (error: any) {
          // Token is invalid, clear auth state
          if (typeof window !== "undefined") {
            localStorage.removeItem("accessToken");
          }
          set({
            user: null,
            isAuthenticated: false,
            isLoading: false,
            error: null,
          });
        }
      },

      clearError: () => {
        set({ error: null });
      },

      setUser: (user: User | null) => {
        set({ user, isAuthenticated: !!user });
      },
    }),
    {
      name: "auth-storage",
      partialize: (state) => ({
        user: state.user,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);
