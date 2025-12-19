export interface ApiResponse<T> {
  data: T;
  message?: string;
  success: boolean;
}

export interface ApiError {
  message: string;
  status: number;
  errors?: Record<string, string[]>;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
}

export interface SearchFilters {
  query?: string;
  category?: string;
  location?: {
    lat: number;
    lng: number;
    radius?: number; // in km
  };
  priceRange?: {
    min: number;
    max: number;
  };
  rating?: number;
  availability?: string; // ISO date string
  sortBy?: "distance" | "rating" | "price" | "reviews";
  page?: number;
  pageSize?: number;
}
