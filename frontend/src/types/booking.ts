export type BookingStatus =
  | "requested"
  | "accepted"
  | "scheduled"
  | "in_progress"
  | "completed"
  | "cancelled"
  | "disputed";

export interface Booking {
  id: string;
  customerId: string;
  providerId: string;
  serviceId: string;
  status: BookingStatus;
  scheduledAt: string;
  location: {
    lat: number;
    lng: number;
    address: string;
  };
  description?: string;
  estimatedPrice?: {
    min: number;
    max: number;
  };
  finalPrice?: number;
  createdAt: string;
  updatedAt: string;
  completedAt?: string;
  cancelledAt?: string;
  cancellationReason?: string;
  customer?: {
    id: string;
    fullName: string;
    phone: string;
    avatar?: string;
  };
  provider?: {
    id: string;
    businessName: string;
    phone: string;
    avatar?: string;
  };
  service?: {
    id: string;
    title: string;
    category: string;
  };
  review?: {
    id: string;
    rating: number;
    comment?: string;
  };
}

export interface BookingRequest {
  providerId: string;
  serviceId: string;
  scheduledAt: string;
  location: {
    lat: number;
    lng: number;
    address: string;
  };
  description?: string;
  estimatedBudget?: {
    min: number;
    max: number;
  };
}

export interface BookingFilters {
  status?: BookingStatus[];
  dateFrom?: string;
  dateTo?: string;
  providerId?: string;
  customerId?: string;
}
