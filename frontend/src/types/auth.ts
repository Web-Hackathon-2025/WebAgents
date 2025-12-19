export interface LoginCredentials {
  email: string;
  password: string;
  rememberMe?: boolean;
}

export interface RegisterData {
  email: string;
  password: string;
  fullName: string;
  phone: string;
  location?: {
    lat: number;
    lng: number;
    address: string;
  };
}

export interface CustomerRegisterData extends RegisterData {
  role: "customer";
}

export interface ProviderRegisterData extends RegisterData {
  role: "provider";
  businessName: string;
  businessAddress: {
    lat: number;
    lng: number;
    address: string;
  };
  serviceCategories: string[];
  serviceRadius: number;
  documents?: File[];
}

export interface AuthResponse {
  user: User;
  accessToken: string;
}

export interface User {
  id: string;
  email: string;
  fullName: string;
  phone: string;
  role: "customer" | "provider" | "admin";
  avatar?: string;
  isVerified: boolean;
  createdAt: string;
  updatedAt: string;
}
