"use client";

import { useEffect } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useBookingStore } from "@/stores/booking-store";
import { LoadingSpinner } from "@/components/shared/loading-spinner";
import { EmptyState } from "@/components/shared/empty-state";
import { StatusBadge } from "@/components/shared/status-badge";
import { formatCurrency, formatRelativeDate } from "@/lib/utils/format";
import { formatDateTime } from "@/lib/utils/date";
import { CheckCircle, XCircle, Clock, MapPin } from "lucide-react";
import { toast } from "sonner";

export default function ProviderBookingsPage() {
  const { bookings, isLoading, fetchBookings, acceptBooking, rejectBooking } =
    useBookingStore();

  useEffect(() => {
    fetchBookings();
  }, [fetchBookings]);

  const handleAccept = async (id: string) => {
    try {
      await acceptBooking(id, new Date().toISOString());
      toast.success("Booking accepted");
    } catch (error: any) {
      toast.error(error.message || "Failed to accept booking");
    }
  };

  const handleReject = async (id: string) => {
    if (!confirm("Are you sure you want to reject this booking?")) return;

    try {
      await rejectBooking(id, "Provider rejected");
      toast.success("Booking rejected");
    } catch (error: any) {
      toast.error(error.message || "Failed to reject booking");
    }
  };

  const pendingBookings = bookings.filter((b) => b.status === "requested");
  const acceptedBookings = bookings.filter((b) => b.status === "accepted");
  const scheduledBookings = bookings.filter((b) => b.status === "scheduled");
  const inProgressBookings = bookings.filter((b) => b.status === "in_progress");
  const completedBookings = bookings.filter((b) => b.status === "completed");

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-text-primary">Booking Management</h1>
        <p className="mt-2 text-text-secondary">Manage your booking requests and schedule</p>
      </div>

      <Tabs defaultValue="pending" className="w-full">
        <TabsList>
          <TabsTrigger value="pending">
            Pending ({pendingBookings.length})
          </TabsTrigger>
          <TabsTrigger value="accepted">
            Accepted ({acceptedBookings.length})
          </TabsTrigger>
          <TabsTrigger value="scheduled">
            Scheduled ({scheduledBookings.length})
          </TabsTrigger>
          <TabsTrigger value="in-progress">
            In Progress ({inProgressBookings.length})
          </TabsTrigger>
          <TabsTrigger value="completed">
            Completed ({completedBookings.length})
          </TabsTrigger>
        </TabsList>

        <TabsContent value="pending" className="mt-6">
          {isLoading ? (
            <div className="flex justify-center py-12">
              <LoadingSpinner size="lg" />
            </div>
          ) : pendingBookings.length === 0 ? (
            <EmptyState
              title="No pending bookings"
              description="You don't have any pending booking requests at the moment."
            />
          ) : (
            <div className="space-y-4">
              {pendingBookings.map((booking) => (
                <Card key={booking.id} className="hover:shadow-md transition-shadow">
                  <CardContent className="pt-6">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <h3 className="text-lg font-semibold text-text-primary">
                            {booking.service?.title || "Service Request"}
                          </h3>
                          <StatusBadge status={booking.status} />
                        </div>
                        <div className="space-y-1 text-sm text-text-secondary">
                          <p>
                            <strong>Customer:</strong> {booking.customer?.fullName || "N/A"}
                          </p>
                          <div className="flex items-center gap-2">
                            <Clock className="h-4 w-4" />
                            <span>Requested: {formatDateTime(booking.scheduledAt)}</span>
                          </div>
                          <div className="flex items-center gap-2">
                            <MapPin className="h-4 w-4" />
                            <span>{booking.location.address}</span>
                          </div>
                          {booking.description && (
                            <p className="mt-2">{booking.description}</p>
                          )}
                          {booking.estimatedPrice && (
                            <p className="font-medium text-text-primary">
                              Estimated: {formatCurrency(booking.estimatedPrice.min)} -{" "}
                              {formatCurrency(booking.estimatedPrice.max)}
                            </p>
                          )}
                        </div>
                      </div>
                      <div className="flex gap-2 ml-4">
                        <Button
                          size="sm"
                          variant="default"
                          onClick={() => handleAccept(booking.id)}
                        >
                          <CheckCircle className="mr-2 h-4 w-4" />
                          Accept
                        </Button>
                        <Button
                          size="sm"
                          variant="destructive"
                          onClick={() => handleReject(booking.id)}
                        >
                          <XCircle className="mr-2 h-4 w-4" />
                          Reject
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </TabsContent>

        <TabsContent value="accepted" className="mt-6">
          <BookingList bookings={acceptedBookings} isLoading={isLoading} />
        </TabsContent>

        <TabsContent value="scheduled" className="mt-6">
          <BookingList bookings={scheduledBookings} isLoading={isLoading} />
        </TabsContent>

        <TabsContent value="in-progress" className="mt-6">
          <BookingList bookings={inProgressBookings} isLoading={isLoading} />
        </TabsContent>

        <TabsContent value="completed" className="mt-6">
          <BookingList bookings={completedBookings} isLoading={isLoading} />
        </TabsContent>
      </Tabs>
    </div>
  );
}

function BookingList({
  bookings,
  isLoading,
}: {
  bookings: any[];
  isLoading: boolean;
}) {
  if (isLoading) {
    return (
      <div className="flex justify-center py-12">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (bookings.length === 0) {
    return <EmptyState title="No bookings" description="No bookings in this category." />;
  }

  return (
    <div className="space-y-4">
      {bookings.map((booking) => (
        <Card key={booking.id} className="hover:shadow-md transition-shadow">
          <CardContent className="pt-6">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-2">
                  <h3 className="text-lg font-semibold text-text-primary">
                    {booking.service?.title || "Service"}
                  </h3>
                  <StatusBadge status={booking.status} />
                </div>
                <div className="space-y-1 text-sm text-text-secondary">
                  <p>
                    <strong>Customer:</strong> {booking.customer?.fullName || "N/A"}
                  </p>
                  <div className="flex items-center gap-2">
                    <Clock className="h-4 w-4" />
                    <span>{formatDateTime(booking.scheduledAt)}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <MapPin className="h-4 w-4" />
                    <span>{booking.location.address}</span>
                  </div>
                  {booking.finalPrice && (
                    <p className="font-medium text-text-primary">
                      {formatCurrency(booking.finalPrice)}
                    </p>
                  )}
                </div>
              </div>
              <Button variant="outline" asChild>
                <a href={`/provider/bookings/${booking.id}`}>View Details</a>
              </Button>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
