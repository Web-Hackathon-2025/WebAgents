import { post, get, patch, del } from "./client";
import { Booking, BookingRequest, BookingFilters, PaginatedResponse } from "@/types/booking";

export const bookingApi = {
  createBooking: async (data: BookingRequest): Promise<Booking> => {
    return post<Booking>("/bookings/request", data);
  },

  getBookings: async (filters?: BookingFilters): Promise<PaginatedResponse<Booking>> => {
    return get<PaginatedResponse<Booking>>("/customers/bookings", filters);
  },

  getBookingById: async (id: string): Promise<Booking> => {
    return get<Booking>(`/customers/bookings/${id}`);
  },

  cancelBooking: async (id: string, reason: string): Promise<Booking> => {
    return post<Booking>(`/bookings/${id}/cancel`, { reason });
  },

  acceptBooking: async (id: string, scheduledAt: string, price?: number): Promise<Booking> => {
    return post<Booking>(`/bookings/${id}/accept`, { scheduledAt, price });
  },

  rejectBooking: async (id: string, reason?: string): Promise<void> => {
    return post<void>(`/bookings/${id}/reject`, { reason });
  },

  updateBookingStatus: async (id: string, status: Booking["status"]): Promise<Booking> => {
    return patch<Booking>(`/bookings/${id}/status`, { status });
  },

  // Provider-specific
  getProviderBookings: async (filters?: BookingFilters): Promise<PaginatedResponse<Booking>> => {
    return get<PaginatedResponse<Booking>>("/providers/bookings", filters);
  },
};
