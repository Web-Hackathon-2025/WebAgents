import { User } from "@/types/auth";
import { Customer, Provider } from "@/types/user";

// Mock Users
export const mockUsers: User[] = [
  {
    id: "1",
    email: "john.customer@example.com",
    fullName: "John Smith",
    phone: "+1-555-0101",
    role: "customer",
    avatar: "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150&h=150&fit=crop&crop=face",
    isVerified: true,
    createdAt: "2024-01-15T10:00:00Z",
    updatedAt: "2024-01-15T10:00:00Z",
  },
  {
    id: "2",
    email: "mike.plumber@example.com",
    fullName: "Mike Johnson",
    phone: "+1-555-0102",
    role: "provider",
    avatar: "https://images.unsplash.com/photo-1560250097-0b93528c311a?w=150&h=150&fit=crop&crop=face",
    isVerified: true,
    createdAt: "2024-01-10T10:00:00Z",
    updatedAt: "2024-01-10T10:00:00Z",
  },
  {
    id: "3",
    email: "sarah.electrician@example.com",
    fullName: "Sarah Davis",
    phone: "+1-555-0103",
    role: "provider",
    avatar: "https://images.unsplash.com/photo-1494790108755-2616b612b786?w=150&h=150&fit=crop&crop=face",
    isVerified: true,
    createdAt: "2024-01-12T10:00:00Z",
    updatedAt: "2024-01-12T10:00:00Z",
  },
  {
    id: "4",
    email: "admin@karigar.com",
    fullName: "Admin User",
    phone: "+1-555-0100",
    role: "admin",
    avatar: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&h=150&fit=crop&crop=face",
    isVerified: true,
    createdAt: "2024-01-01T10:00:00Z",
    updatedAt: "2024-01-01T10:00:00Z",
  },
];

// Mock Customers
export const mockCustomers: Customer[] = [
  {
    ...mockUsers[0],
    role: "customer",
    location: {
      lat: 40.7128,
      lng: -74.0060,
      address: "123 Main St, New York, NY 10001",
    },
    totalBookings: 15,
    totalSpent: 2450.00,
  },
];

// Mock Providers
export const mockProviders: Provider[] = [
  {
    ...mockUsers[1],
    role: "provider",
    businessName: "Mike's Plumbing Services",
    businessAddress: {
      lat: 40.7589,
      lng: -73.9851,
      address: "456 Broadway, New York, NY 10013",
    },
    serviceCategories: ["plumbing", "emergency-repair"],
    serviceRadius: 25,
    rating: 4.8,
    reviewCount: 127,
    isVerified: true,
    isActive: true,
    portfolio: [
      "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400&h=300&fit=crop",
      "https://images.unsplash.com/photo-1581244277943-fe4a9c777189?w=400&h=300&fit=crop",
      "https://images.unsplash.com/photo-1562259949-e8e7689d7828?w=400&h=300&fit=crop",
    ],
  },
  {
    ...mockUsers[2],
    role: "provider",
    businessName: "Davis Electrical Solutions",
    businessAddress: {
      lat: 40.7505,
      lng: -73.9934,
      address: "789 5th Ave, New York, NY 10022",
    },
    serviceCategories: ["electrical", "installation"],
    serviceRadius: 30,
    rating: 4.9,
    reviewCount: 89,
    isVerified: true,
    isActive: true,
    portfolio: [
      "https://images.unsplash.com/photo-1621905251189-08b45d6a269e?w=400&h=300&fit=crop",
      "https://images.unsplash.com/photo-1558618047-3c8c76ca7d13?w=400&h=300&fit=crop",
    ],
  },
  {
    id: "5",
    email: "carlos.carpenter@example.com",
    fullName: "Carlos Rodriguez",
    phone: "+1-555-0104",
    role: "provider",
    avatar: "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=150&h=150&fit=crop&crop=face",
    isVerified: true,
    createdAt: "2024-01-08T10:00:00Z",
    updatedAt: "2024-01-08T10:00:00Z",
    businessName: "Rodriguez Carpentry & Woodwork",
    businessAddress: {
      lat: 40.7282,
      lng: -73.7949,
      address: "321 Queens Blvd, Queens, NY 11415",
    },
    serviceCategories: ["carpentry", "furniture-repair", "custom-work"],
    serviceRadius: 20,
    rating: 4.7,
    reviewCount: 156,
    isActive: true,
    portfolio: [
      "https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=400&h=300&fit=crop",
      "https://images.unsplash.com/photo-1558618047-3c8c76ca7d13?w=400&h=300&fit=crop",
      "https://images.unsplash.com/photo-1581244277943-fe4a9c777189?w=400&h=300&fit=crop",
    ],
  },
  {
    id: "6",
    email: "lisa.cleaner@example.com",
    fullName: "Lisa Thompson",
    phone: "+1-555-0105",
    role: "provider",
    avatar: "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=150&h=150&fit=crop&crop=face",
    isVerified: true,
    createdAt: "2024-01-05T10:00:00Z",
    updatedAt: "2024-01-05T10:00:00Z",
    businessName: "Thompson Cleaning Services",
    businessAddress: {
      lat: 40.6782,
      lng: -73.9442,
      address: "567 Atlantic Ave, Brooklyn, NY 11217",
    },
    serviceCategories: ["cleaning", "deep-cleaning", "move-in-out"],
    serviceRadius: 15,
    rating: 4.9,
    reviewCount: 203,
    isActive: true,
    portfolio: [
      "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400&h=300&fit=crop",
      "https://images.unsplash.com/photo-1562259949-e8e7689d7828?w=400&h=300&fit=crop",
    ],
  },
];

// Mock Services
export interface MockService {
  id: string;
  providerId: string;
  title: string;
  description: string;
  category: string;
  basePrice: number;
  priceUnit: string;
  duration: string;
  availability: string[];
  images: string[];
  tags: string[];
}

export const mockServices: MockService[] = [
  {
    id: "s1",
    providerId: "2",
    title: "Emergency Plumbing Repair",
    description: "24/7 emergency plumbing services for leaks, clogs, and pipe repairs. Licensed and insured.",
    category: "plumbing",
    basePrice: 120,
    priceUnit: "per hour",
    duration: "1-3 hours",
    availability: ["24/7"],
    images: [
      "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400&h=300&fit=crop",
      "https://images.unsplash.com/photo-1581244277943-fe4a9c777189?w=400&h=300&fit=crop",
    ],
    tags: ["emergency", "licensed", "insured", "24/7"],
  },
  {
    id: "s2",
    providerId: "3",
    title: "Electrical Installation & Repair",
    description: "Professional electrical work including outlet installation, lighting, and circuit repairs.",
    category: "electrical",
    basePrice: 95,
    priceUnit: "per hour",
    duration: "2-4 hours",
    availability: ["Mon-Sat 8AM-6PM"],
    images: [
      "https://images.unsplash.com/photo-1621905251189-08b45d6a269e?w=400&h=300&fit=crop",
      "https://images.unsplash.com/photo-1558618047-3c8c76ca7d13?w=400&h=300&fit=crop",
    ],
    tags: ["licensed", "certified", "warranty"],
  },
  {
    id: "s3",
    providerId: "5",
    title: "Custom Furniture & Carpentry",
    description: "Handcrafted furniture, cabinet installation, and custom woodwork for your home.",
    category: "carpentry",
    basePrice: 85,
    priceUnit: "per hour",
    duration: "4-8 hours",
    availability: ["Mon-Fri 9AM-5PM"],
    images: [
      "https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=400&h=300&fit=crop",
      "https://images.unsplash.com/photo-1558618047-3c8c76ca7d13?w=400&h=300&fit=crop",
    ],
    tags: ["custom", "handcrafted", "quality"],
  },
  {
    id: "s4",
    providerId: "6",
    title: "Deep House Cleaning",
    description: "Comprehensive deep cleaning service for your entire home. Eco-friendly products available.",
    category: "cleaning",
    basePrice: 150,
    priceUnit: "per session",
    duration: "3-5 hours",
    availability: ["Mon-Sat 9AM-4PM"],
    images: [
      "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400&h=300&fit=crop",
      "https://images.unsplash.com/photo-1562259949-e8e7689d7828?w=400&h=300&fit=crop",
    ],
    tags: ["eco-friendly", "thorough", "insured"],
  },
];

// Mock Reviews
export interface MockReview {
  id: string;
  serviceId: string;
  customerId: string;
  customerName: string;
  customerAvatar?: string;
  rating: number;
  comment: string;
  createdAt: string;
  images?: string[];
}

export const mockReviews: MockReview[] = [
  {
    id: "r1",
    serviceId: "s1",
    customerId: "1",
    customerName: "John Smith",
    customerAvatar: "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150&h=150&fit=crop&crop=face",
    rating: 5,
    comment: "Mike was fantastic! Fixed our emergency leak at 2 AM and was very professional. Highly recommend!",
    createdAt: "2024-01-20T02:30:00Z",
  },
  {
    id: "r2",
    serviceId: "s2",
    customerId: "1",
    customerName: "John Smith",
    customerAvatar: "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150&h=150&fit=crop&crop=face",
    rating: 5,
    comment: "Sarah did an excellent job installing new outlets in our kitchen. Clean work and fair pricing.",
    createdAt: "2024-01-18T14:15:00Z",
  },
  {
    id: "r3",
    serviceId: "s3",
    customerId: "c2",
    customerName: "Emily Johnson",
    customerAvatar: "https://images.unsplash.com/photo-1494790108755-2616b612b786?w=150&h=150&fit=crop&crop=face",
    rating: 4,
    comment: "Carlos built us a beautiful custom bookshelf. Great craftsmanship and attention to detail.",
    createdAt: "2024-01-16T11:00:00Z",
  },
  {
    id: "r4",
    serviceId: "s4",
    customerId: "c3",
    customerName: "David Wilson",
    customerAvatar: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&h=150&fit=crop&crop=face",
    rating: 5,
    comment: "Lisa's team did an amazing deep clean of our house. Everything sparkles! Will definitely book again.",
    createdAt: "2024-01-14T16:45:00Z",
  },
];

// Mock Data Service
export class MockDataService {
  private static instance: MockDataService;
  private isEnabled: boolean = false;

  static getInstance(): MockDataService {
    if (!MockDataService.instance) {
      MockDataService.instance = new MockDataService();
    }
    return MockDataService.instance;
  }

  enableMockMode(): void {
    this.isEnabled = true;
    console.log("🎭 Mock mode enabled - Using sample data");
  }

  disableMockMode(): void {
    this.isEnabled = false;
    console.log("🔌 Mock mode disabled - Using real API");
  }

  isMockModeEnabled(): boolean {
    return this.isEnabled;
  }

  // Mock API responses
  async mockLogin(email: string, password: string) {
    await this.delay(800); // Simulate network delay
    
    const user = mockUsers.find(u => u.email === email);
    if (!user || password !== "password123") {
      throw new Error("Invalid credentials");
    }

    return {
      user,
      accessToken: `mock-token-${user.id}`,
    };
  }

  async mockGetCurrentUser(token: string) {
    await this.delay(300);
    
    const userId = token.replace("mock-token-", "");
    const user = mockUsers.find(u => u.id === userId);
    
    if (!user) {
      throw new Error("Invalid token");
    }
    
    return user;
  }

  async mockGetProviders() {
    await this.delay(500);
    return mockProviders;
  }

  async mockGetServices() {
    await this.delay(500);
    return mockServices;
  }

  async mockGetReviews(serviceId?: string) {
    await this.delay(300);
    return serviceId 
      ? mockReviews.filter(r => r.serviceId === serviceId)
      : mockReviews;
  }

  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

// Export singleton instance
export const mockDataService = MockDataService.getInstance();

// Demo credentials for easy testing
export const DEMO_CREDENTIALS = {
  customer: {
    email: "john.customer@example.com",
    password: "password123",
  },
  provider: {
    email: "mike.plumber@example.com",
    password: "password123",
  },
  admin: {
    email: "admin@karigar.com",
    password: "password123",
  },
};