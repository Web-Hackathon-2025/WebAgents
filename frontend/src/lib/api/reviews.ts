import { post, get, patch, upload } from "./client";
import { Review, PaginatedResponse } from "@/types/service";

export const reviewApi = {
  createReview: async (bookingId: string, data: {
    rating: number;
    criteriaRatings?: Review["criteriaRatings"];
    comment?: string;
    images?: File[];
  }): Promise<Review> => {
    if (data.images && data.images.length > 0) {
      return upload<Review>(`/reviews`, data.images, {
        bookingId,
        rating: data.rating,
        criteriaRatings: data.criteriaRatings,
        comment: data.comment,
      });
    }
    return post<Review>("/reviews", { bookingId, ...data });
  },

  getReviews: async (providerId?: string, filters?: {
    page?: number;
    pageSize?: number;
  }): Promise<PaginatedResponse<Review>> => {
    return get<PaginatedResponse<Review>>("/reviews", {
      ...filters,
      ...(providerId && { providerId }),
    });
  },

  respondToReview: async (reviewId: string, comment: string): Promise<Review> => {
    return post<Review>(`/reviews/${reviewId}/respond`, { comment });
  },
};
