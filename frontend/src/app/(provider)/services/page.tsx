"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { serviceApi } from "@/lib/api/services";
import { Service } from "@/types/service";
import { LoadingSpinner } from "@/components/shared/loading-spinner";
import { EmptyState } from "@/components/shared/empty-state";
import { RatingDisplay } from "@/components/shared/rating-display";
import { formatCurrency } from "@/lib/utils/format";
import { Plus, Edit, Trash2, Eye } from "lucide-react";
import { toast } from "sonner";

export default function ServicesPage() {
  const [services, setServices] = useState<Service[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetchServices();
  }, []);

  const fetchServices = async () => {
    try {
      const data = await serviceApi.getServices();
      setServices(data);
    } catch (error: any) {
      toast.error("Failed to fetch services");
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Are you sure you want to delete this service?")) return;

    try {
      await serviceApi.deleteService(id);
      toast.success("Service deleted successfully");
      fetchServices();
    } catch (error: any) {
      toast.error("Failed to delete service");
    }
  };

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-text-primary">My Services</h1>
          <p className="mt-2 text-text-secondary">Manage your service offerings</p>
        </div>
        <Button asChild>
          <Link href="/provider/services/new">
            <Plus className="mr-2 h-4 w-4" />
            Add New Service
          </Link>
        </Button>
      </div>

      {services.length === 0 ? (
        <EmptyState
          icon={<Plus className="h-12 w-12 text-text-secondary" />}
          title="No services yet"
          description="Start by adding your first service offering"
          action={{
            label: "Add Service",
            onClick: () => (window.location.href = "/provider/services/new"),
          }}
        />
      ) : (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {services.map((service) => (
            <Card key={service.id} className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <CardTitle className="text-xl">{service.title}</CardTitle>
                    <CardDescription className="mt-1">{service.category}</CardDescription>
                  </div>
                  {service.isActive ? (
                    <Badge variant="success">Active</Badge>
                  ) : (
                    <Badge variant="secondary">Inactive</Badge>
                  )}
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <p className="text-sm text-text-secondary line-clamp-2">
                    {service.description}
                  </p>

                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-lg font-semibold text-text-primary">
                        {formatCurrency(service.pricing.basePrice)}
                        {service.pricing.maxPrice &&
                          ` - ${formatCurrency(service.pricing.maxPrice)}`}
                        {service.pricing.type === "hourly" && "/hr"}
                      </p>
                    </div>
                    {service.averageRating && (
                      <RatingDisplay
                        rating={service.averageRating}
                        count={service.bookingCount}
                        size="sm"
                      />
                    )}
                  </div>

                  <div className="flex gap-2 pt-2">
                    <Button variant="outline" size="sm" className="flex-1" asChild>
                      <Link href={`/provider/services/${service.id}`}>
                        <Eye className="mr-2 h-4 w-4" />
                        View
                      </Link>
                    </Button>
                    <Button variant="outline" size="sm" className="flex-1" asChild>
                      <Link href={`/provider/services/${service.id}/edit`}>
                        <Edit className="mr-2 h-4 w-4" />
                        Edit
                      </Link>
                    </Button>
                    <Button
                      variant="destructive"
                      size="sm"
                      onClick={() => handleDelete(service.id)}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
