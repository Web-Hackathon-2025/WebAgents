import { User } from "./auth";

export interface Customer extends User {
  role: "customer";
  location?: {
    lat: number;
    lng: number;
    address: string;
  };
  totalBookings?: number;
  totalSpent?: number;
}

export interface Provider extends User {
  role: "provider";
  businessName: string;
  businessAddress: {
    lat: number;
    lng: number;
    address: string;
  };
  serviceCategories: string[];
  serviceRadius: number;
  rating?: number;
  reviewCount?: number;
  isVerified: boolean;
  isActive: boolean;
  portfolio?: string[];
  documents?: string[];
}

export interface Admin extends User {
  role: "admin";
}
