"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { RatingDisplay } from "@/components/shared/rating-display";
import { LoadingSpinner } from "@/components/shared/loading-spinner";
import { EmptyState } from "@/components/shared/empty-state";
import { searchApi } from "@/lib/api/search";
import { reviewApi } from "@/lib/api/reviews";
import { Provider } from "@/types/user";
import { Review } from "@/types/service";
import { ArrowLeft, MapPin, CheckCircle, Calendar, MessageSquare } from "lucide-react";
import { formatDistance } from "@/lib/utils/distance";

export default function ProviderProfilePage() {
  const params = useParams();
  const providerId = params.id as string;
  const [provider, setProvider] = useState<Provider | null>(null);
  const [reviews, setReviews] = useState<Review[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchProvider = async () => {
      try {
        const data = await searchApi.getProviderById(providerId);
        setProvider(data);
      } catch (error) {
        console.error("Failed to fetch provider:", error);
      } finally {
        setIsLoading(false);
      }
    };

    if (providerId) {
      fetchProvider();
    }
  }, [providerId]);

  useEffect(() => {
    const fetchReviews = async () => {
      if (!providerId) return;
      try {
        const response = await reviewApi.getReviews(providerId);
        setReviews(response.items || []);
      } catch (error) {
        console.error("Failed to fetch reviews:", error);
      }
    };

    fetchReviews();
  }, [providerId]);

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (!provider) {
    return (
      <EmptyState
        title="Provider not found"
        description="The provider you're looking for doesn't exist or has been removed."
      />
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <Button variant="ghost" asChild className="mb-6">
        <Link href="/search">
          <ArrowLeft className="mr-2 h-4 w-4" />
          Back to Search
        </Link>
      </Button>

      <div className="mb-8">
        <div className="flex items-start justify-between">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <h1 className="text-3xl font-bold text-text-primary">{provider.businessName}</h1>
              {provider.isVerified && (
                <Badge variant="success" className="flex items-center gap-1">
                  <CheckCircle className="h-3 w-3" />
                  Verified
                </Badge>
              )}
            </div>
            {provider.rating && (
              <RatingDisplay
                rating={provider.rating}
                count={provider.reviewCount}
                size="md"
                className="mb-2"
              />
            )}
            <div className="flex items-center gap-2 text-text-secondary">
              <MapPin className="h-4 w-4" />
              <span>{provider.businessAddress.address}</span>
              <span>•</span>
              <span>Service Radius: {provider.serviceRadius} km</span>
            </div>
          </div>
          <Button asChild size="lg">
            <Link href={`/bookings/new?providerId=${provider.id}`}>Book Now</Link>
          </Button>
        </div>
      </div>

      <Tabs defaultValue="about" className="w-full">
        <TabsList>
          <TabsTrigger value="about">About</TabsTrigger>
          <TabsTrigger value="services">Services</TabsTrigger>
          <TabsTrigger value="reviews">
            Reviews ({reviews.length})
          </TabsTrigger>
        </TabsList>

        <TabsContent value="about" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle>About</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div>
                  <h3 className="font-semibold mb-2">Service Categories</h3>
                  <div className="flex flex-wrap gap-2">
                    {provider.serviceCategories.map((category) => (
                      <Badge key={category} variant="secondary">
                        {category}
                      </Badge>
                    ))}
                  </div>
                </div>
                <div>
                  <h3 className="font-semibold mb-2">Service Area</h3>
                  <p className="text-text-secondary">
                    Serving customers within {provider.serviceRadius} km of{" "}
                    {provider.businessAddress.address}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="services" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle>Services Offered</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-text-secondary">Services will be listed here</p>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="reviews" className="mt-6">
          <div className="space-y-4">
            {reviews.length === 0 ? (
              <EmptyState
                icon={<MessageSquare className="h-12 w-12 text-text-secondary" />}
                title="No reviews yet"
                description="This provider hasn't received any reviews yet."
              />
            ) : (
              reviews.map((review) => (
                <Card key={review.id}>
                  <CardContent className="pt-6">
                    <div className="flex items-start justify-between mb-2">
                      <div>
                        <h4 className="font-semibold">
                          {review.customer?.fullName || "Anonymous"}
                        </h4>
                        <RatingDisplay rating={review.rating} size="sm" className="mt-1" />
                      </div>
                      <span className="text-sm text-text-secondary">
                        {new Date(review.createdAt).toLocaleDateString()}
                      </span>
                    </div>
                    {review.comment && (
                      <p className="text-text-secondary mt-2">{review.comment}</p>
                    )}
                  </CardContent>
                </Card>
              ))
            )}
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}
