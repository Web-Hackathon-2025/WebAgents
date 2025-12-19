import { apiClient } from "./client";
import { SearchFilters, PaginatedResponse } from "@/types/api";
import { Provider } from "@/types/user";
import { ServiceCategory } from "@/types/service";
import { mockProviders, mockCategories } from "@/lib/mock-data";

// Use mock data for now until backend is fully connected
const USE_MOCK_DATA = true;

export const searchApi = {
  searchProviders: async (filters: SearchFilters): Promise<PaginatedResponse<Provider>> => {
    if (USE_MOCK_DATA) {
      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 500));
      
      let filteredProviders = [...mockProviders];
      
      // Filter by query
      if (filters.query) {
        const query = filters.query.toLowerCase();
        filteredProviders = filteredProviders.filter(provider =>
          provider.businessName.toLowerCase().includes(query) ||
          provider.serviceCategories.some(cat => cat.toLowerCase().includes(query))
        );
      }
      
      // Pagination
      const page = filters.page || 1;
      const pageSize = filters.pageSize || 20;
      const start = (page - 1) * pageSize;
      const end = start + pageSize;
      const paginatedItems = filteredProviders.slice(start, end);
      
      return {
        items: paginatedItems,
        total: filteredProviders.length,
        page,
        pageSize,
        totalPages: Math.ceil(filteredProviders.length / pageSize)
      };
    }
    
    try {
      const params = new URLSearchParams();
      if (filters.query) params.append('query', filters.query);
      if (filters.category) params.append('category', filters.category);
      if (filters.latitude) params.append('latitude', filters.latitude.toString());
      if (filters.longitude) params.append('longitude', filters.longitude.toString());
      if (filters.radius) params.append('radius', filters.radius.toString());
      if (filters.page) params.append('page', filters.page.toString());
      if (filters.pageSize) params.append('pageSize', filters.pageSize.toString());
      
      const url = `/search/providers${params.toString() ? '?' + params.toString() : ''}`;
      return await apiClient.get<PaginatedResponse<Provider>>(url);
    } catch (error) {
      console.error('Search providers error:', error);
      // Return empty result on error
      return {
        items: [],
        total: 0,
        page: 1,
        pageSize: 20,
        totalPages: 0
      };
    }
  },

  getRecommendations: async (): Promise<Provider[]> => {
    if (USE_MOCK_DATA) {
      await new Promise(resolve => setTimeout(resolve, 300));
      return mockProviders.slice(0, 3);
    }
    
    try {
      return await apiClient.get<Provider[]>("/search/recommendations");
    } catch (error) {
      console.error('Get recommendations error:', error);
      return [];
    }
  },

  getCategories: async (): Promise<ServiceCategory[]> => {
    if (USE_MOCK_DATA) {
      await new Promise(resolve => setTimeout(resolve, 200));
      return mockCategories;
    }
    
    try {
      return await apiClient.get<ServiceCategory[]>("/search/categories");
    } catch (error) {
      console.error('Get categories error:', error);
      return [];
    }
  },

  getProviderById: async (id: string): Promise<Provider> => {
    if (USE_MOCK_DATA) {
      await new Promise(resolve => setTimeout(resolve, 300));
      const provider = mockProviders.find(p => p.id === id);
      if (!provider) {
        throw new Error('Provider not found');
      }
      return provider;
    }
    
    return await apiClient.get<Provider>(`/search/providers/${id}`);
  },
};
