"use client";

import { useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { StatusBadge } from "@/components/shared/status-badge";
import { useBookingStore } from "@/stores/booking-store";
import { LoadingSpinner } from "@/components/shared/loading-spinner";
import { formatCurrency } from "@/lib/utils/format";
import { formatDateTime } from "@/lib/utils/date";
import { ArrowLeft, Calendar, Clock, MapPin, Wrench, MessageSquare } from "lucide-react";
import { toast } from "sonner";

export default function BookingDetailPage() {
  const params = useParams();
  const router = useRouter();
  const bookingId = params.id as string;
  const { currentBooking, isLoading, fetchBookingById, cancelBooking } = useBookingStore();

  useEffect(() => {
    if (bookingId) {
      fetchBookingById(bookingId);
    }
  }, [bookingId, fetchBookingById]);

  const handleCancel = async () => {
    if (!confirm("Are you sure you want to cancel this booking?")) return;

    const reason = prompt("Please provide a reason for cancellation:");
    if (!reason) return;

    try {
      await cancelBooking(bookingId, reason);
      toast.success("Booking cancelled successfully");
      router.push("/bookings");
    } catch (error: any) {
      toast.error(error.message || "Failed to cancel booking");
    }
  };

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (!currentBooking) {
    return (
      <div className="container mx-auto px-4 py-8">
        <Card>
          <CardContent className="pt-6">
            <p>Booking not found</p>
          </CardContent>
        </Card>
      </div>
    );
  }

  const canCancel = ["requested", "accepted", "scheduled"].includes(currentBooking.status);

  return (
    <div className="container mx-auto px-4 py-8">
      <Button variant="ghost" asChild className="mb-6">
        <Link href="/bookings">
          <ArrowLeft className="mr-2 h-4 w-4" />
          Back to Bookings
        </Link>
      </Button>

      <div className="mb-6">
        <div className="flex items-center gap-3 mb-2">
          <h1 className="text-3xl font-bold text-text-primary">
            Booking #{currentBooking.id.slice(0, 8)}
          </h1>
          <StatusBadge status={currentBooking.status} size="lg" />
        </div>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Service Details</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <p className="text-sm text-text-secondary">Service</p>
              <p className="font-medium">{currentBooking.service?.title || "N/A"}</p>
            </div>
            <div>
              <p className="text-sm text-text-secondary">Provider</p>
              <p className="font-medium">{currentBooking.provider?.businessName || "N/A"}</p>
            </div>
            <div>
              <p className="text-sm text-text-secondary">Category</p>
              <p className="font-medium">{currentBooking.service?.category || "N/A"}</p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Booking Information</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center gap-2">
              <Calendar className="h-4 w-4 text-text-secondary" />
              <div>
                <p className="text-sm text-text-secondary">Scheduled Date & Time</p>
                <p className="font-medium">{formatDateTime(currentBooking.scheduledAt)}</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <MapPin className="h-4 w-4 text-text-secondary" />
              <div>
                <p className="text-sm text-text-secondary">Location</p>
                <p className="font-medium">{currentBooking.location.address}</p>
              </div>
            </div>
            {currentBooking.finalPrice && (
              <div>
                <p className="text-sm text-text-secondary">Price</p>
                <p className="font-medium text-lg">{formatCurrency(currentBooking.finalPrice)}</p>
              </div>
            )}
            {currentBooking.estimatedPrice && !currentBooking.finalPrice && (
              <div>
                <p className="text-sm text-text-secondary">Estimated Price</p>
                <p className="font-medium">
                  {formatCurrency(currentBooking.estimatedPrice.min)} -{" "}
                  {formatCurrency(currentBooking.estimatedPrice.max)}
                </p>
              </div>
            )}
          </CardContent>
        </Card>

        {currentBooking.description && (
          <Card className="md:col-span-2">
            <CardHeader>
              <CardTitle>Description</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-text-secondary">{currentBooking.description}</p>
            </CardContent>
          </Card>
        )}

        <Card className="md:col-span-2">
          <CardHeader>
            <CardTitle>Timeline</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-start gap-3">
                <div className="h-2 w-2 rounded-full bg-success mt-2" />
                <div>
                  <p className="font-medium">Requested</p>
                  <p className="text-sm text-text-secondary">
                    {formatDateTime(currentBooking.createdAt)}
                  </p>
                </div>
              </div>
              {currentBooking.status !== "requested" && (
                <div className="flex items-start gap-3">
                  <div className="h-2 w-2 rounded-full bg-info mt-2" />
                  <div>
                    <p className="font-medium">Accepted</p>
                    <p className="text-sm text-text-secondary">
                      {formatDateTime(currentBooking.updatedAt)}
                    </p>
                  </div>
                </div>
              )}
              {["in_progress", "completed"].includes(currentBooking.status) && (
                <div className="flex items-start gap-3">
                  <div className="h-2 w-2 rounded-full bg-warning mt-2" />
                  <div>
                    <p className="font-medium">In Progress</p>
                  </div>
                </div>
              )}
              {currentBooking.status === "completed" && currentBooking.completedAt && (
                <div className="flex items-start gap-3">
                  <div className="h-2 w-2 rounded-full bg-success mt-2" />
                  <div>
                    <p className="font-medium">Completed</p>
                    <p className="text-sm text-text-secondary">
                      {formatDateTime(currentBooking.completedAt)}
                    </p>
                  </div>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      {canCancel && (
        <div className="mt-6 flex gap-4">
          <Button variant="destructive" onClick={handleCancel}>
            Cancel Booking
          </Button>
          <Button variant="outline" asChild>
            <Link href={`/providers/${currentBooking.providerId}`}>
              <MessageSquare className="mr-2 h-4 w-4" />
              Contact Provider
            </Link>
          </Button>
        </div>
      )}
    </div>
  );
}
