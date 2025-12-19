import { get, post, patch, del } from "./client";
import { User, Customer, Provider } from "@/types/user";
import { Booking } from "@/types/booking";
import { Review } from "@/types/service";
import { PaginatedResponse } from "@/types/api";

export const adminApi = {
  // User Management
  getUsers: async (filters?: {
    role?: string;
    status?: string;
    page?: number;
    pageSize?: number;
  }): Promise<PaginatedResponse<User>> => {
    return get<PaginatedResponse<User>>("/admin/users", filters);
  },

  getUserById: async (id: string): Promise<User> => {
    return get<User>(`/admin/users/${id}`);
  },

  suspendUser: async (id: string): Promise<void> => {
    return post<void>(`/admin/users/${id}/suspend`);
  },

  deleteUser: async (id: string): Promise<void> => {
    return del<void>(`/admin/users/${id}`);
  },

  // Provider Approval
  getPendingProviders: async (): Promise<Provider[]> => {
    return get<Provider[]>("/admin/providers/pending");
  },

  approveProvider: async (id: string, notes?: string): Promise<void> => {
    return post<void>(`/admin/providers/${id}/approve`, { notes });
  },

  rejectProvider: async (id: string, reason: string): Promise<void> => {
    return post<void>(`/admin/providers/${id}/reject`, { reason });
  },

  // Bookings
  getAllBookings: async (filters?: {
    status?: string;
    dateFrom?: string;
    dateTo?: string;
    page?: number;
    pageSize?: number;
  }): Promise<PaginatedResponse<Booking>> => {
    return get<PaginatedResponse<Booking>>("/admin/bookings", filters);
  },

  // Reviews
  getFlaggedReviews: async (): Promise<Review[]> => {
    return get<Review[]>("/admin/reviews/flagged");
  },

  removeReview: async (id: string): Promise<void> => {
    return del<void>(`/admin/reviews/${id}`);
  },

  // Disputes
  getDisputes: async (filters?: {
    status?: string;
    page?: number;
    pageSize?: number;
  }): Promise<PaginatedResponse<any>> => {
    return get<PaginatedResponse<any>>("/admin/disputes", filters);
  },

  resolveDispute: async (id: string, resolution: {
    favor: "customer" | "provider" | "partial";
    refundAmount?: number;
    notes: string;
  }): Promise<void> => {
    return post<void>(`/admin/disputes/${id}/resolve`, resolution);
  },

  // Analytics
  getAnalytics: async (dateFrom?: string, dateTo?: string): Promise<any> => {
    return get<any>("/admin/analytics", { dateFrom, dateTo });
  },
};
