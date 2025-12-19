"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useBookingStore } from "@/stores/booking-store";
import { LoadingSpinner } from "@/components/shared/loading-spinner";
import { EmptyState } from "@/components/shared/empty-state";
import { StatusBadge } from "@/components/shared/status-badge";
import { formatCurrency } from "@/lib/utils/format";
import { formatDateTime } from "@/lib/utils/date";
import { Calendar, Clock, MapPin, Wrench } from "lucide-react";

export default function CustomerBookingsPage() {
  const router = useRouter();
  const { bookings, isLoading, fetchBookings } = useBookingStore();

  useEffect(() => {
    fetchBookings();
  }, [fetchBookings]);

  const activeBookings = bookings.filter(
    (b) => !["completed", "cancelled"].includes(b.status)
  );
  const completedBookings = bookings.filter((b) => b.status === "completed");
  const cancelledBookings = bookings.filter((b) => b.status === "cancelled");

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-text-primary">My Bookings</h1>
        <p className="mt-2 text-text-secondary">View and manage your service bookings</p>
      </div>

      <Tabs defaultValue="active" className="w-full">
        <TabsList>
          <TabsTrigger value="active">Active ({activeBookings.length})</TabsTrigger>
          <TabsTrigger value="completed">Completed ({completedBookings.length})</TabsTrigger>
          <TabsTrigger value="cancelled">Cancelled ({cancelledBookings.length})</TabsTrigger>
        </TabsList>

        <TabsContent value="active" className="mt-6">
          {isLoading ? (
            <div className="flex justify-center py-12">
              <LoadingSpinner size="lg" />
            </div>
          ) : activeBookings.length === 0 ? (
            <EmptyState
              icon={<Calendar className="h-12 w-12 text-text-secondary" />}
              title="No active bookings"
              description="You don't have any active bookings at the moment."
              action={{
                label: "Find Services",
                onClick: () => router.push("/search"),
              }}
            />
          ) : (
            <div className="space-y-4">
              {activeBookings.map((booking) => (
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
                          <div className="flex items-center gap-2">
                            <Wrench className="h-4 w-4" />
                            <span>{booking.provider?.businessName || "Provider"}</span>
                          </div>
                          <div className="flex items-center gap-2">
                            <Clock className="h-4 w-4" />
                            <span>{formatDateTime(booking.scheduledAt)}</span>
                          </div>
                          <div className="flex items-center gap-2">
                            <MapPin className="h-4 w-4" />
                            <span>{booking.location.address}</span>
                          </div>
                          {booking.finalPrice && (
                            <div className="font-medium text-text-primary">
                              {formatCurrency(booking.finalPrice)}
                            </div>
                          )}
                        </div>
                      </div>
                      <Button variant="outline" asChild>
                        <Link href={`/bookings/${booking.id}`}>View Details</Link>
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </TabsContent>

        <TabsContent value="completed" className="mt-6">
          <BookingList bookings={completedBookings} isLoading={isLoading} />
        </TabsContent>

        <TabsContent value="cancelled" className="mt-6">
          <BookingList bookings={cancelledBookings} isLoading={isLoading} />
        </TabsContent>
      </Tabs>
    </div>
  );
}

function BookingList({ bookings, isLoading }: { bookings: any[]; isLoading: boolean }) {
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
                  <div className="flex items-center gap-2">
                    <Wrench className="h-4 w-4" />
                    <span>{booking.provider?.businessName || "Provider"}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Clock className="h-4 w-4" />
                    <span>{formatDateTime(booking.scheduledAt)}</span>
                  </div>
                  {booking.finalPrice && (
                    <div className="font-medium text-text-primary">
                      {formatCurrency(booking.finalPrice)}
                    </div>
                  )}
                </div>
              </div>
              <Button variant="outline" asChild>
                <Link href={`/bookings/${booking.id}`}>View Details</Link>
              </Button>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
