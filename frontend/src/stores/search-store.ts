import { create } from "zustand";
import { Provider } from "@/types/user";
import { SearchFilters, PaginatedResponse } from "@/types/api";
import { searchApi } from "@/lib/api/search";

interface SearchState {
  query: string;
  filters: SearchFilters;
  results: Provider[];
  isLoading: boolean;
  hasMore: boolean;
  pagination: {
    total: number;
    page: number;
    pageSize: number;
    totalPages: number;
  } | null;
  
  // Actions
  setQuery: (query: string) => void;
  setFilters: (filters: Partial<SearchFilters>) => void;
  search: () => Promise<void>;
  loadMore: () => Promise<void>;
  clearSearch: () => void;
}

export const useSearchStore = create<SearchState>((set, get) => ({
  query: "",
  filters: {},
  results: [],
  isLoading: false,
  hasMore: false,
  pagination: null,

  setQuery: (query: string) => {
    set({ query });
  },

  setFilters: (filters: Partial<SearchFilters>) => {
    set((state) => ({
      filters: { ...state.filters, ...filters },
    }));
  },

  search: async () => {
    const { query, filters } = get();
    set({ isLoading: true });
    
    try {
      const searchFilters: SearchFilters = {
        ...filters,
        query: query || undefined,
        page: 1,
        pageSize: 20,
      };
      
      const response = await searchApi.searchProviders(searchFilters);
      
      set({
        results: response.items || [],
        hasMore: response.page < response.totalPages,
        pagination: {
          total: response.total,
          page: response.page,
          pageSize: response.pageSize,
          totalPages: response.totalPages,
        },
        isLoading: false,
      });
    } catch (error: any) {
      console.error('Search error:', error);
      set({
        results: [],
        isLoading: false,
        hasMore: false,
        pagination: null,
      });
    }
  },

  loadMore: async () => {
    const { query, filters, pagination, results } = get();
    
    if (!pagination || !get().hasMore || get().isLoading) return;
    
    set({ isLoading: true });
    
    try {
      const searchFilters: SearchFilters = {
        ...filters,
        query: query || undefined,
        page: pagination.page + 1,
        pageSize: pagination.pageSize,
      };
      
      const response = await searchApi.searchProviders(searchFilters);
      
      set({
        results: [...results, ...response.items],
        hasMore: response.page < response.totalPages,
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
        error: error.message || "Failed to load more results",
      });
    }
  },

  clearSearch: () => {
    set({
      query: "",
      filters: {},
      results: [],
      hasMore: false,
      pagination: null,
    });
  },
}));
