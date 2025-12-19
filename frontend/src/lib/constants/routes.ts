export const ROUTES = {
  // Public routes
  HOME: "/",
  SEARCH: "/search",
  LOGIN: "/login",
  REGISTER: "/register",
  REGISTER_CUSTOMER: "/register/customer",
  REGISTER_PROVIDER: "/register/provider",
  FORGOT_PASSWORD: "/forgot-password",
  VERIFY_EMAIL: "/verify-email",

  // Customer routes
  CUSTOMER_DASHBOARD: "/dashboard",
  CUSTOMER_BOOKINGS: "/bookings",
  CUSTOMER_BOOKING_DETAIL: (id: string) => `/bookings/${id}`,
  CUSTOMER_PROFILE: "/profile",
  CUSTOMER_FAVORITES: "/favorites",

  // Provider routes
  PROVIDER_DASHBOARD: "/provider/dashboard",
  PROVIDER_SERVICES: "/provider/services",
  PROVIDER_SERVICE_NEW: "/provider/services/new",
  PROVIDER_SERVICE_EDIT: (id: string) => `/provider/services/${id}/edit`,
  PROVIDER_BOOKINGS: "/provider/bookings",
  PROVIDER_AVAILABILITY: "/provider/availability",
  PROVIDER_REVIEWS: "/provider/reviews",
  PROVIDER_ANALYTICS: "/provider/analytics",

  // Admin routes
  ADMIN_DASHBOARD: "/admin/dashboard",
  ADMIN_USERS: "/admin/users",
  ADMIN_PROVIDERS: "/admin/providers",
  ADMIN_PROVIDERS_PENDING: "/admin/providers/pending",
  ADMIN_BOOKINGS: "/admin/bookings",
  ADMIN_REVIEWS: "/admin/reviews",
  ADMIN_DISPUTES: "/admin/disputes",
  ADMIN_ANALYTICS: "/admin/analytics",

  // Shared routes
  PROVIDER_PROFILE: (id: string) => `/providers/${id}`,
} as const;
