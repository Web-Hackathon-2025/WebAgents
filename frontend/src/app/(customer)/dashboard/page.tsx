"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useAuthStore } from "@/stores/auth-store";
import { useBookingStore } from "@/stores/booking-store";
import { LoadingSpinner } from "@/components/shared/loading-spinner";
import { EmptyState } from "@/components/shared/empty-state";
import { StatusBadge } from "@/components/shared/status-badge";
import { formatCurrency, formatRelativeDate } from "@/lib/utils/format";
import { Calendar, Clock, MapPin, Search, Heart, Wrench } from "lucide-react";
import { formatDateTime } from "@/lib/utils/date";

export default function CustomerDashboard() {
  const router = useRouter();
  const { user, isAuthenticated, checkAuth } = useAuthStore();
  const { bookings, isLoading, fetchBookings } = useBookingStore();

  useEffect(() => {
    if (!isAuthenticated) {
      checkAuth();
    }
  }, [isAuthenticated, checkAuth]);

  useEffect(() => {
    if (isAuthenticated && user?.role === "customer") {
      fetchBookings({ status: ["requested", "accepted", "scheduled", "in_progress"] });
    }
  }, [isAuthenticated, user, fetchBookings]);

  if (!isAuthenticated || user?.role !== "customer") {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  const activeBookings = bookings.filter(
    (b) => !["completed", "cancelled"].includes(b.status)
  );
  const recentBookings = bookings.slice(0, 5);

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-text-primary">
          Welcome back, {user.fullName}! 👋
        </h1>
        <p className="mt-2 text-text-secondary">Here's what's happening with your bookings</p>
      </div>

      {/* Stats Cards */}
      <div className="mb-8 grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Bookings</CardTitle>
            <Calendar className="h-4 w-4 text-text-secondary" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{activeBookings.length}</div>
            <p className="text-xs text-text-secondary">Currently in progress</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Bookings</CardTitle>
            <Wrench className="h-4 w-4 text-text-secondary" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{bookings.length}</div>
            <p className="text-xs text-text-secondary">All time</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Quick Actions</CardTitle>
            <Search className="h-4 w-4 text-text-secondary" />
          </CardHeader>
          <CardContent>
            <Button asChild className="w-full">
              <Link href="/search">Find Services</Link>
            </Button>
          </CardContent>
        </Card>
      </div>

      {/* Recent Bookings */}
      <div className="mb-8">
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-2xl font-semibold text-text-primary">Recent Bookings</h2>
          <Button asChild variant="outline">
            <Link href="/bookings">View All</Link>
          </Button>
        </div>

        {isLoading ? (
          <div className="flex justify-center py-12">
            <LoadingSpinner size="lg" />
          </div>
        ) : recentBookings.length === 0 ? (
          <EmptyState
            icon={<Calendar className="h-12 w-12 text-text-secondary" />}
            title="No bookings yet"
            description="Start by searching for service providers in your area"
            action={{
              label: "Find Services",
              onClick: () => router.push("/search"),
            }}
          />
        ) : (
          <div className="space-y-4">
            {recentBookings.map((booking) => (
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
                    <Button asChild variant="outline">
                      <Link href={`/bookings/${booking.id}`}>View Details</Link>
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
