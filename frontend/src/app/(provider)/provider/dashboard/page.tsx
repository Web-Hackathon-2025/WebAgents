"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useAuthStore } from "@/stores/auth-store";
import { useBookingStore } from "@/stores/booking-store";
import { LoadingSpinner } from "@/components/shared/loading-spinner";
import { StatusBadge } from "@/components/shared/status-badge";
import { formatCurrency, formatRelativeDate } from "@/lib/utils/format";
import { Calendar, DollarSign, Star, Clock, CheckCircle, XCircle } from "lucide-react";
import { formatDateTime } from "@/lib/utils/date";

export default function ProviderDashboard() {
  const router = useRouter();
  const { user, isAuthenticated, checkAuth } = useAuthStore();
  const { bookings, isLoading, fetchBookings } = useBookingStore();

  useEffect(() => {
    if (!isAuthenticated) {
      checkAuth();
    }
  }, [isAuthenticated, checkAuth]);

  useEffect(() => {
    if (isAuthenticated && user?.role === "provider") {
      fetchBookings({ status: ["requested", "accepted", "scheduled", "in_progress"] });
    }
  }, [isAuthenticated, user, fetchBookings]);

  if (!isAuthenticated || user?.role !== "provider") {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  const pendingRequests = bookings.filter((b) => b.status === "requested");
  const todayBookings = bookings.filter((b) => {
    const bookingDate = new Date(b.scheduledAt);
    const today = new Date();
    return (
      bookingDate.toDateString() === today.toDateString() &&
      ["accepted", "scheduled", "in_progress"].includes(b.status)
    );
  });

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-text-primary">
          Provider Dashboard
        </h1>
        <p className="mt-2 text-text-secondary">Manage your services and bookings</p>
      </div>

      {/* Stats Cards */}
      <div className="mb-8 grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Pending Requests</CardTitle>
            <Clock className="h-4 w-4 text-text-secondary" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{pendingRequests.length}</div>
            <p className="text-xs text-text-secondary">Awaiting response</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Today's Bookings</CardTitle>
            <Calendar className="h-4 w-4 text-text-secondary" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{todayBookings.length}</div>
            <p className="text-xs text-text-secondary">Scheduled today</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Rating</CardTitle>
            <Star className="h-4 w-4 text-text-secondary" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">4.8</div>
            <p className="text-xs text-text-secondary">From 156 reviews</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">This Month</CardTitle>
            <DollarSign className="h-4 w-4 text-text-secondary" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{formatCurrency(1250)}</div>
            <p className="text-xs text-text-secondary">Revenue</p>
          </CardContent>
        </Card>
      </div>

      {/* Pending Requests */}
      {pendingRequests.length > 0 && (
        <div className="mb-8">
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-2xl font-semibold text-text-primary">
              Pending Requests ({pendingRequests.length})
            </h2>
            <Button asChild variant="outline">
              <Link href="/provider/bookings?status=requested">View All</Link>
            </Button>
          </div>
          <div className="space-y-4">
            {pendingRequests.slice(0, 3).map((booking) => (
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
                        <p>
                          <strong>Requested:</strong> {formatDateTime(booking.scheduledAt)}
                        </p>
                        <p>
                          <strong>Location:</strong> {booking.location.address}
                        </p>
                        {booking.description && (
                          <p className="mt-2">{booking.description}</p>
                        )}
                      </div>
                    </div>
                    <div className="flex gap-2 ml-4">
                      <Button size="sm" variant="default">
                        <CheckCircle className="mr-2 h-4 w-4" />
                        Accept
                      </Button>
                      <Button size="sm" variant="destructive">
                        <XCircle className="mr-2 h-4 w-4" />
                        Reject
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      )}

      {/* Today's Schedule */}
      {todayBookings.length > 0 && (
        <div>
          <h2 className="mb-4 text-2xl font-semibold text-text-primary">Today's Schedule</h2>
          <div className="space-y-4">
            {todayBookings.map((booking) => (
              <Card key={booking.id}>
                <CardContent className="pt-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="font-semibold">{booking.service?.title}</h3>
                      <p className="text-sm text-text-secondary">
                        {booking.customer?.fullName} • {formatDateTime(booking.scheduledAt)}
                      </p>
                    </div>
                    <StatusBadge status={booking.status} />
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
