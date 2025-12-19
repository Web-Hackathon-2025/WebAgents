import { get } from "./client";
import { SearchFilters, PaginatedResponse } from "@/types/api";
import { Provider } from "@/types/user";
import { ServiceCategory } from "@/types/service";

export const searchApi = {
  searchProviders: async (filters: SearchFilters): Promise<PaginatedResponse<Provider>> => {
    return get<PaginatedResponse<Provider>>("/search/providers", filters);
  },

  getRecommendations: async (): Promise<Provider[]> => {
    return get<Provider[]>("/search/recommendations");
  },

  getCategories: async (): Promise<ServiceCategory[]> => {
    return get<ServiceCategory[]>("/search/categories");
  },

  getProviderById: async (id: string): Promise<Provider> => {
    return get<Provider>(`/providers/${id}`);
  },
};
