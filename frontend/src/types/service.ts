export interface Service {
  id: string;
  providerId: string;
  category: string;
  title: string;
  description: string;
  pricing: {
    type: "fixed" | "hourly" | "daily";
    basePrice: number;
    maxPrice?: number;
  };
  duration?: number; // in minutes
  images?: string[];
  tags?: string[];
  isActive: boolean;
  bookingCount?: number;
  averageRating?: number;
  createdAt: string;
  updatedAt: string;
}

export interface ServiceCategory {
  id: string;
  name: string;
  icon?: string;
  description?: string;
}

export interface Review {
  id: string;
  bookingId: string;
  customerId: string;
  providerId: string;
  rating: number;
  criteriaRatings?: {
    serviceQuality: number;
    punctuality: number;
    professionalism: number;
    valueForMoney: number;
  };
  comment?: string;
  images?: string[];
  createdAt: string;
  customer?: {
    id: string;
    fullName: string;
    avatar?: string;
  };
  providerResponse?: {
    comment: string;
    createdAt: string;
  };
}
