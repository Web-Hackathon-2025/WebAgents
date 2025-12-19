import { create } from "zustand";
import { Booking, BookingRequest, BookingFilters } from "@/types/booking";
import { bookingApi } from "@/lib/api/bookings";
import { PaginatedResponse } from "@/types/api";

interface BookingState {
  bookings: Booking[];
  currentBooking: Booking | null;
  isLoading: boolean;
  error: string | null;
  pagination: {
    total: number;
    page: number;
    pageSize: number;
    totalPages: number;
  } | null;
  
  // Actions
  fetchBookings: (filters?: BookingFilters) => Promise<void>;
  fetchBookingById: (id: string) => Promise<void>;
  createBooking: (data: BookingRequest) => Promise<Booking>;
  updateBooking: (id: string, updates: Partial<Booking>) => Promise<void>;
  cancelBooking: (id: string, reason: string) => Promise<void>;
  acceptBooking: (id: string, scheduledAt: string, price?: number) => Promise<void>;
  rejectBooking: (id: string, reason?: string) => Promise<void>;
  clearError: () => void;
  setCurrentBooking: (booking: Booking | null) => void;
}

export const useBookingStore = create<BookingState>((set, get) => ({
  bookings: [],
  currentBooking: null,
  isLoading: false,
  error: null,
  pagination: null,

  fetchBookings: async (filters?: BookingFilters) => {
    set({ isLoading: true, error: null });
    try {
      const response = await bookingApi.getBookings(filters);
      set({
        bookings: response.items,
        pagination: {
          total: response.total,
          page: response.page,
          pageSize: response.pageSize,
          totalPages: response.totalPages,
        },
        isLoading: false,
      });
    } catch (error: any) {
      set({
        isLoading: false,
        error: error.message || "Failed to fetch bookings",
      });
    }
  },

  fetchBookingById: async (id: string) => {
    set({ isLoading: true, error: null });
    try {
      const booking = await bookingApi.getBookingById(id);
      set({
        currentBooking: booking,
        isLoading: false,
      });
      
      // Update in bookings list if exists
      const bookings = get().bookings;
      const index = bookings.findIndex((b) => b.id === id);
      if (index !== -1) {
        bookings[index] = booking;
        set({ bookings });
      }
    } catch (error: any) {
      set({
        isLoading: false,
        error: error.message || "Failed to fetch booking",
      });
    }
  },

  createBooking: async (data: BookingRequest) => {
    set({ isLoading: true, error: null });
    try {
      const booking = await bookingApi.createBooking(data);
      set((state) => ({
        bookings: [booking, ...state.bookings],
        currentBooking: booking,
        isLoading: false,
      }));
      return booking;
    } catch (error: any) {
      set({
        isLoading: false,
        error: error.message || "Failed to create booking",
      });
      throw error;
    }
  },

  updateBooking: async (id: string, updates: Partial<Booking>) => {
    set({ isLoading: true, error: null });
    try {
      // Optimistic update
      const bookings = get().bookings.map((b) =>
        b.id === id ? { ...b, ...updates } : b
      );
      
      if (get().currentBooking?.id === id) {
        set({
          currentBooking: { ...get().currentBooking, ...updates } as Booking,
        });
      }
      
      set({ bookings, isLoading: false });
    } catch (error: any) {
      set({
        isLoading: false,
        error: error.message || "Failed to update booking",
      });
      // Revert optimistic update
      get().fetchBookings();
    }
  },

  cancelBooking: async (id: string, reason: string) => {
    set({ isLoading: true, error: null });
    try {
      const booking = await bookingApi.cancelBooking(id, reason);
      set((state) => ({
        bookings: state.bookings.map((b) => (b.id === id ? booking : b)),
        currentBooking: state.currentBooking?.id === id ? booking : state.currentBooking,
        isLoading: false,
      }));
    } catch (error: any) {
      set({
        isLoading: false,
        error: error.message || "Failed to cancel booking",
      });
      throw error;
    }
  },

  acceptBooking: async (id: string, scheduledAt: string, price?: number) => {
    set({ isLoading: true, error: null });
    try {
      const booking = await bookingApi.acceptBooking(id, scheduledAt, price);
      set((state) => ({
        bookings: state.bookings.map((b) => (b.id === id ? booking : b)),
        currentBooking: state.currentBooking?.id === id ? booking : state.currentBooking,
        isLoading: false,
      }));
    } catch (error: any) {
      set({
        isLoading: false,
        error: error.message || "Failed to accept booking",
      });
      throw error;
    }
  },

  rejectBooking: async (id: string, reason?: string) => {
    set({ isLoading: true, error: null });
    try {
      await bookingApi.rejectBooking(id, reason);
      set((state) => ({
        bookings: state.bookings.filter((b) => b.id !== id),
        currentBooking: state.currentBooking?.id === id ? null : state.currentBooking,
        isLoading: false,
      }));
    } catch (error: any) {
      set({
        isLoading: false,
        error: error.message || "Failed to reject booking",
      });
      throw error;
    }
  },

  clearError: () => {
    set({ error: null });
  },

  setCurrentBooking: (booking: Booking | null) => {
    set({ currentBooking: booking });
  },
}));
