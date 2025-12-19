import { post, get, put, patch, del, upload } from "./client";
import { Service, ServiceCategory } from "@/types/service";

export const serviceApi = {
  getServices: async (providerId?: string): Promise<Service[]> => {
    return get<Service[]>("/services", providerId ? { providerId } : undefined);
  },

  getServiceById: async (id: string): Promise<Service> => {
    return get<Service>(`/services/${id}`);
  },

  createService: async (data: Partial<Service>, images?: File[]): Promise<Service> => {
    if (images && images.length > 0) {
      return upload<Service>("/services", images, data);
    }
    return post<Service>("/services", data);
  },

  updateService: async (id: string, data: Partial<Service>): Promise<Service> => {
    return patch<Service>(`/services/${id}`, data);
  },

  deleteService: async (id: string): Promise<void> => {
    return del<void>(`/services/${id}`);
  },

  getCategories: async (): Promise<ServiceCategory[]> => {
    return get<ServiceCategory[]>("/services/categories");
  },
};
