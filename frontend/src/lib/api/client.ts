import { ApiError, ApiResponse } from "@/types/api";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

/**
 * Get authentication headers
 */
function getAuthHeaders(): HeadersInit {
  const token = typeof window !== "undefined" 
    ? localStorage.getItem("accessToken") 
    : null;
  
  return {
    "Content-Type": "application/json",
    ...(token && { Authorization: `Bearer ${token}` }),
  };
}

/**
 * Custom API Error class
 */
export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public data?: any
  ) {
    super(message);
    this.name = "ApiError";
  }
}

/**
 * Handle API errors
 */
function handleApiError(error: unknown): never {
  if (error instanceof ApiError) {
    // Handle 401 Unauthorized - redirect to login
    if (error.status === 401) {
      if (typeof window !== "undefined") {
        localStorage.removeItem("accessToken");
        window.location.href = "/login";
      }
    }
    throw error;
  }
  
  if (error instanceof Error) {
    throw new ApiError(error.message, 500);
  }
  
  throw new ApiError("An unexpected error occurred", 500);
}

/**
 * Build query string from object
 */
function buildQueryString(params: Record<string, any>): string {
  const searchParams = new URLSearchParams();
  
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null) {
      if (Array.isArray(value)) {
        value.forEach((item) => searchParams.append(key, String(item)));
      } else {
        searchParams.append(key, String(value));
      }
    }
  });
  
  return searchParams.toString();
}

/**
 * Base API request function
 */
export async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  
  const config: RequestInit = {
    headers: getAuthHeaders(),
    ...options,
  };
  
  // Add timeout
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 30000);
  config.signal = controller.signal;
  
  try {
    const response = await fetch(url, config);
    clearTimeout(timeout);
    
    if (!response.ok) {
      let errorData;
      try {
        errorData = await response.json();
      } catch {
        errorData = { message: response.statusText };
      }
      
      throw new ApiError(
        errorData.message || "Request failed",
        response.status,
        errorData
      );
    }
    
    // Handle empty responses
    const contentType = response.headers.get("content-type");
    if (!contentType || !contentType.includes("application/json")) {
      return {} as T;
    }
    
    const data = await response.json();
    return data;
  } catch (error) {
    clearTimeout(timeout);
    
    if (error instanceof ApiError) {
      handleApiError(error);
    }
    
    if (error instanceof Error && error.name === "AbortError") {
      throw new ApiError("Request timeout", 408);
    }
    
    handleApiError(error);
    throw error;
  }
}

/**
 * GET request
 */
export function get<T>(endpoint: string, params?: Record<string, any>): Promise<T> {
  const queryString = params ? `?${buildQueryString(params)}` : "";
  return apiRequest<T>(`${endpoint}${queryString}`, { method: "GET" });
}

/**
 * POST request
 */
export function post<T>(endpoint: string, data?: any): Promise<T> {
  return apiRequest<T>(endpoint, {
    method: "POST",
    body: data ? JSON.stringify(data) : undefined,
  });
}

/**
 * PUT request
 */
export function put<T>(endpoint: string, data?: any): Promise<T> {
  return apiRequest<T>(endpoint, {
    method: "PUT",
    body: data ? JSON.stringify(data) : undefined,
  });
}

/**
 * PATCH request
 */
export function patch<T>(endpoint: string, data?: any): Promise<T> {
  return apiRequest<T>(endpoint, {
    method: "PATCH",
    body: data ? JSON.stringify(data) : undefined,
  });
}

/**
 * DELETE request
 */
export function del<T>(endpoint: string): Promise<T> {
  return apiRequest<T>(endpoint, { method: "DELETE" });
}

/**
 * Upload file(s)
 */
export async function upload<T>(
  endpoint: string,
  files: File[],
  additionalData?: Record<string, any>
): Promise<T> {
  const formData = new FormData();
  
  files.forEach((file, index) => {
    formData.append(`file${index}`, file);
  });
  
  if (additionalData) {
    Object.entries(additionalData).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        formData.append(key, typeof value === "string" ? value : JSON.stringify(value));
      }
    });
  }
  
  const token = typeof window !== "undefined" 
    ? localStorage.getItem("accessToken") 
    : null;
  
  const headers: HeadersInit = {
    ...(token && { Authorization: `Bearer ${token}` }),
  };
  
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 60000); // 60s for uploads
  
  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: "POST",
      headers,
      body: formData,
      signal: controller.signal,
    });
    
    clearTimeout(timeout);
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new ApiError(
        errorData.message || "Upload failed",
        response.status,
        errorData
      );
    }
    
    return response.json();
  } catch (error) {
    clearTimeout(timeout);
    handleApiError(error);
    throw error;
  }
}
