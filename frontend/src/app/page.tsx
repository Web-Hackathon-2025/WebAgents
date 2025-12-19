"use client";

import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { Search, Shield, Clock, Star, Wrench, Zap, Home, Hammer, CheckCircle2, Sparkles, MapPin, Phone } from "lucide-react";
import { mockProviders, mockServices, mockReviews } from "@/lib/mock-data";
import { useEffect, useState } from "react";

export default function HomePage() {
  const [featuredProviders, setFeaturedProviders] = useState(mockProviders.slice(0, 3));
  const [recentReviews, setRecentReviews] = useState(mockReviews.slice(0, 3));
  return (
    <div className="flex min-h-screen flex-col">
      {/* Hero Section - Modern Design */}
      <section className="relative overflow-hidden bg-gradient-to-br from-blue-50 via-white to-indigo-50 py-24 sm:py-32">
        {/* Decorative background elements */}
        <div className="absolute inset-0 -z-10 overflow-hidden">
          <div className="absolute left-[20%] top-0 h-[500px] w-[500px] rounded-full bg-blue-200/20 blur-3xl" />
          <div className="absolute right-[20%] bottom-0 h-[500px] w-[500px] rounded-full bg-indigo-200/20 blur-3xl" />
        </div>

        <div className="container mx-auto px-4">
          <div className="mx-auto max-w-5xl text-center">
            {/* Badge */}
            <div className="mb-6 inline-flex items-center gap-2 rounded-full bg-blue-100 px-4 py-2 text-sm font-medium text-blue-700">
              <Sparkles className="h-4 w-4" />
              <span>Trusted by 10,000+ customers</span>
            </div>

            <h1 className="mb-6 text-5xl font-extrabold tracking-tight text-gray-900 sm:text-6xl lg:text-7xl">
              Find Trusted{" "}
              <span className="bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
                Local Service
              </span>{" "}
              Providers
            </h1>
            <p className="mb-10 text-xl text-gray-600 sm:text-2xl">
              Connect with verified professionals in your area. From plumbing to electrical work,
              <br className="hidden sm:block" />
              we've got you covered.
            </p>
            <div className="flex flex-col gap-4 sm:flex-row sm:justify-center">
              <Button asChild size="lg" className="h-14 text-lg shadow-lg shadow-blue-500/25 transition-all hover:shadow-xl hover:shadow-blue-500/30">
                <Link href="/search">
                  <Search className="mr-2 h-5 w-5" />
                  Find Services
                </Link>
              </Button>
              <Button asChild size="lg" variant="outline" className="h-14 border-2 text-lg font-semibold">
                <Link href="/register/provider">Become a Provider</Link>
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section - Enhanced Design */}
      <section className="relative py-24">
        <div className="container mx-auto px-4">
          <div className="mb-16 text-center">
            <h2 className="mb-4 text-4xl font-bold text-gray-900 sm:text-5xl">
              Why Choose Karigar?
            </h2>
            <p className="mx-auto max-w-2xl text-lg text-gray-600">
              Experience the difference with our trusted platform
            </p>
          </div>
          <div className="grid gap-8 md:grid-cols-3">
            <Card className="group relative h-full border-2 border-transparent transition-all duration-300 hover:border-blue-200 hover:shadow-xl">
              <div className="absolute inset-0 rounded-lg bg-gradient-to-br from-blue-50 to-transparent opacity-0 transition-opacity group-hover:opacity-100" />
              <CardHeader className="relative">
                <div className="mb-4 inline-flex h-14 w-14 items-center justify-center rounded-xl bg-blue-100 text-blue-600 transition-transform group-hover:scale-110">
                  <Shield className="h-7 w-7" />
                </div>
                <CardTitle className="text-2xl">Verified Providers</CardTitle>
                <CardDescription className="text-base">
                  All service providers are verified and background-checked for your peace of mind.
                </CardDescription>
              </CardHeader>
            </Card>
            <Card className="group relative h-full border-2 border-transparent transition-all duration-300 hover:border-indigo-200 hover:shadow-xl">
              <div className="absolute inset-0 rounded-lg bg-gradient-to-br from-indigo-50 to-transparent opacity-0 transition-opacity group-hover:opacity-100" />
              <CardHeader className="relative">
                <div className="mb-4 inline-flex h-14 w-14 items-center justify-center rounded-xl bg-indigo-100 text-indigo-600 transition-transform group-hover:scale-110">
                  <Clock className="h-7 w-7" />
                </div>
                <CardTitle className="text-2xl">Quick Response</CardTitle>
                <CardDescription className="text-base">
                  Get matched with available providers in your area within minutes.
                </CardDescription>
              </CardHeader>
            </Card>
            <Card className="group relative h-full border-2 border-transparent transition-all duration-300 hover:border-amber-200 hover:shadow-xl">
              <div className="absolute inset-0 rounded-lg bg-gradient-to-br from-amber-50 to-transparent opacity-0 transition-opacity group-hover:opacity-100" />
              <CardHeader className="relative">
                <div className="mb-4 inline-flex h-14 w-14 items-center justify-center rounded-xl bg-amber-100 text-amber-600 transition-transform group-hover:scale-110">
                  <Star className="h-7 w-7" />
                </div>
                <CardTitle className="text-2xl">Quality Guaranteed</CardTitle>
                <CardDescription className="text-base">
                  Rate and review providers to help maintain high service standards.
                </CardDescription>
              </CardHeader>
            </Card>
          </div>
        </div>
      </section>

      {/* Categories Section - Modern Grid */}
      <section className="bg-gradient-to-b from-gray-50 to-white py-24">
        <div className="container mx-auto px-4">
          <div className="mb-16 text-center">
            <h2 className="mb-4 text-4xl font-bold text-gray-900 sm:text-5xl">
              Popular Service Categories
            </h2>
            <p className="mx-auto max-w-2xl text-lg text-gray-600">
              Browse our most requested services
            </p>
          </div>
          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
            {[
              { icon: Wrench, name: "Plumbing", description: "Leaks, repairs, installations", color: "blue" },
              { icon: Zap, name: "Electrical", description: "Wiring, repairs, installations", color: "amber" },
              { icon: Home, name: "Carpentry", description: "Furniture, repairs, custom work", color: "orange" },
              { icon: Hammer, name: "General Repair", description: "Home maintenance & fixes", color: "indigo" },
            ].map((category) => {
              const colorClasses = {
                blue: "bg-blue-100 text-blue-600 group-hover:bg-blue-600 group-hover:text-white",
                amber: "bg-amber-100 text-amber-600 group-hover:bg-amber-600 group-hover:text-white",
                orange: "bg-orange-100 text-orange-600 group-hover:bg-orange-600 group-hover:text-white",
                indigo: "bg-indigo-100 text-indigo-600 group-hover:bg-indigo-600 group-hover:text-white",
              };
              return (
                <Card
                  key={category.name}
                  className="group h-full cursor-pointer border-2 border-transparent transition-all duration-300 hover:scale-105 hover:border-gray-200 hover:shadow-xl"
                >
                  <CardHeader>
                    <div className={`mb-4 inline-flex h-16 w-16 items-center justify-center rounded-2xl transition-all duration-300 ${colorClasses[category.color as keyof typeof colorClasses]}`}>
                      <category.icon className="h-8 w-8" />
                    </div>
                    <CardTitle className="text-xl">{category.name}</CardTitle>
                    <CardDescription className="text-base">{category.description}</CardDescription>
                  </CardHeader>
                </Card>
              );
            })}
          </div>
        </div>
      </section>

      {/* Featured Providers Section */}
      <section className="py-24 bg-white">
        <div className="container mx-auto px-4">
          <div className="mb-16 text-center">
            <h2 className="mb-4 text-4xl font-bold text-gray-900 sm:text-5xl">
              Featured Service Providers
            </h2>
            <p className="mx-auto max-w-2xl text-lg text-gray-600">
              Meet some of our top-rated professionals ready to help you
            </p>
          </div>
          <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-3">
            {featuredProviders.map((provider) => (
              <Card key={provider.id} className="group h-full border-2 border-transparent transition-all duration-300 hover:border-blue-200 hover:shadow-xl">
                <CardHeader className="text-center">
                  <div className="mx-auto mb-4">
                    <Avatar className="h-20 w-20">
                      <AvatarImage src={provider.avatar} alt={provider.fullName} />
                      <AvatarFallback className="text-lg">
                        {provider.fullName.charAt(0)}
                      </AvatarFallback>
                    </Avatar>
                  </div>
                  <CardTitle className="text-xl">{provider.businessName}</CardTitle>
                  <CardDescription className="text-base font-medium text-gray-700">
                    {provider.fullName}
                  </CardDescription>
                  <div className="flex items-center justify-center gap-2 mt-2">
                    <div className="flex items-center gap-1">
                      <Star className="h-4 w-4 fill-yellow-400 text-yellow-400" />
                      <span className="font-semibold">{provider.rating}</span>
                      <span className="text-gray-500">({provider.reviewCount} reviews)</span>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="flex items-center gap-2 text-sm text-gray-600">
                      <MapPin className="h-4 w-4" />
                      <span>{provider.businessAddress.address}</span>
                    </div>
                    <div className="flex items-center gap-2 text-sm text-gray-600">
                      <Phone className="h-4 w-4" />
                      <span>{provider.phone}</span>
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {provider.serviceCategories.slice(0, 2).map((category) => (
                        <Badge key={category} variant="secondary" className="text-xs">
                          {category.replace('-', ' ')}
                        </Badge>
                      ))}
                      {provider.serviceCategories.length > 2 && (
                        <Badge variant="outline" className="text-xs">
                          +{provider.serviceCategories.length - 2} more
                        </Badge>
                      )}
                    </div>
                    {provider.isVerified && (
                      <div className="flex items-center gap-2 text-sm text-green-600">
                        <CheckCircle2 className="h-4 w-4" />
                        <span>Verified Provider</span>
                      </div>
                    )}
                  </div>
                  <Button asChild className="w-full mt-4" variant="outline">
                    <Link href={`/providers/${provider.id}`}>
                      View Profile
                    </Link>
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
          <div className="text-center mt-12">
            <Button asChild size="lg" variant="outline" className="border-2">
              <Link href="/search">
                View All Providers
              </Link>
            </Button>
          </div>
        </div>
      </section>

      {/* Recent Reviews Section */}
      <section className="py-24 bg-gray-50">
        <div className="container mx-auto px-4">
          <div className="mb-16 text-center">
            <h2 className="mb-4 text-4xl font-bold text-gray-900 sm:text-5xl">
              What Our Customers Say
            </h2>
            <p className="mx-auto max-w-2xl text-lg text-gray-600">
              Real reviews from real customers
            </p>
          </div>
          <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-3">
            {recentReviews.map((review) => (
              <Card key={review.id} className="h-full">
                <CardHeader>
                  <div className="flex items-center gap-3">
                    <Avatar>
                      <AvatarImage src={review.customerAvatar} alt={review.customerName} />
                      <AvatarFallback>
                        {review.customerName.charAt(0)}
                      </AvatarFallback>
                    </Avatar>
                    <div>
                      <p className="font-semibold">{review.customerName}</p>
                      <div className="flex items-center gap-1">
                        {Array.from({ length: 5 }).map((_, i) => (
                          <Star
                            key={i}
                            className={`h-4 w-4 ${
                              i < review.rating
                                ? "fill-yellow-400 text-yellow-400"
                                : "text-gray-300"
                            }`}
                          />
                        ))}
                      </div>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <p className="text-gray-700 leading-relaxed">{review.comment}</p>
                  <p className="text-sm text-gray-500 mt-3">
                    {new Date(review.createdAt).toLocaleDateString()}
                  </p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-16 bg-white">
        <div className="container mx-auto px-4">
          <div className="grid gap-8 sm:grid-cols-2 lg:grid-cols-4">
            {[
              { number: "10,000+", label: "Happy Customers" },
              { number: "500+", label: "Verified Providers" },
              { number: "50,000+", label: "Services Completed" },
              { number: "4.9/5", label: "Average Rating" },
            ].map((stat) => (
              <div key={stat.label} className="text-center">
                <div className="mb-2 text-4xl font-bold text-gray-900 sm:text-5xl">
                  {stat.number}
                </div>
                <div className="text-lg text-gray-600">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section - Fixed and Enhanced */}
      <section className="relative overflow-hidden bg-gradient-to-r from-blue-600 via-indigo-600 to-blue-700 py-20">
        {/* Decorative pattern */}
        <div className="absolute inset-0 opacity-10">
          <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PGRlZnM+PHBhdHRlcm4gaWQ9ImdyaWQiIHdpZHRoPSI2MCIgaGVpZ2h0PSI2MCIgcGF0dGVyblVuaXRzPSJ1c2VyU3BhY2VPblVzZSI+PHBhdGggZD0iTSAxMCAwIEwgMCAwIDAgMTAiIGZpbGw9Im5vbmUiIHN0cm9rZT0id2hpdGUiIHN0cm9rZS13aWR0aD0iMSIvPjwvcGF0dGVybj48L2RlZnM+PHJlY3Qgd2lkdGg9IjEwMCUiIGhlaWdodD0iMTAwJSIgZmlsbD0idXJsKCNncmlkKSIvPjwvc3ZnPg==')]"></div>
        </div>

        <div className="container relative mx-auto px-4">
          <div className="mx-auto max-w-4xl text-center">
            <h2 className="mb-4 text-4xl font-bold text-white sm:text-5xl">
              Ready to Get Started?
            </h2>
            <p className="mb-10 text-xl text-blue-100 sm:text-2xl">
              Join thousands of satisfied customers and service providers.
            </p>
            <div className="flex flex-col gap-4 sm:flex-row sm:justify-center">
              <Button
                asChild
                size="lg"
                variant="secondary"
                className="h-14 bg-white text-lg font-semibold text-blue-600 shadow-xl transition-all hover:scale-105 hover:shadow-2xl"
              >
                <Link href="/register/customer">
                  <CheckCircle2 className="mr-2 h-5 w-5" />
                  Sign Up as Customer
                </Link>
              </Button>
              <Button
                asChild
                size="lg"
                variant="outline"
                className="h-14 border-2 border-white bg-transparent text-lg font-semibold text-white transition-all hover:scale-105 hover:bg-white/10"
              >
                <Link href="/register/provider">
                  Sign Up as Provider
                </Link>
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-gray-200 bg-white py-12">
        <div className="container mx-auto px-4 text-center text-sm text-gray-600">
          <p>&copy; {new Date().getFullYear()} Karigar. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
}
