import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Search, Shield, Clock, Star, Wrench, Zap, Home, Hammer } from "lucide-react";

export default function HomePage() {
  return (
    <div className="flex min-h-screen flex-col">
      {/* Hero Section */}
      <section className="relative overflow-hidden bg-gradient-to-b from-primary-light to-background py-20">
        <div className="container mx-auto px-4">
          <div className="mx-auto max-w-4xl text-center">
            <h1 className="mb-6 text-5xl font-bold tracking-tight text-text-primary sm:text-6xl">
              Find Trusted Local Service Providers
            </h1>
            <p className="mb-8 text-xl text-text-secondary">
              Connect with verified professionals in your area. From plumbing to electrical work,
              we've got you covered.
            </p>
            <div className="flex flex-col gap-4 sm:flex-row sm:justify-center">
              <Button asChild size="lg" className="text-lg">
                <Link href="/search">Find Services</Link>
              </Button>
              <Button asChild size="lg" variant="outline" className="text-lg">
                <Link href="/register/provider">Become a Provider</Link>
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20">
        <div className="container mx-auto px-4">
          <h2 className="mb-12 text-center text-3xl font-bold text-text-primary">
            Why Choose Karigar?
          </h2>
          <div className="grid gap-6 md:grid-cols-3">
            <Card>
              <CardHeader>
                <Shield className="mb-2 h-10 w-10 text-primary" />
                <CardTitle>Verified Providers</CardTitle>
                <CardDescription>
                  All service providers are verified and background-checked for your peace of mind.
                </CardDescription>
              </CardHeader>
            </Card>
            <Card>
              <CardHeader>
                <Clock className="mb-2 h-10 w-10 text-primary" />
                <CardTitle>Quick Response</CardTitle>
                <CardDescription>
                  Get matched with available providers in your area within minutes.
                </CardDescription>
              </CardHeader>
            </Card>
            <Card>
              <CardHeader>
                <Star className="mb-2 h-10 w-10 text-primary" />
                <CardTitle>Quality Guaranteed</CardTitle>
                <CardDescription>
                  Rate and review providers to help maintain high service standards.
                </CardDescription>
              </CardHeader>
            </Card>
          </div>
        </div>
      </section>

      {/* Categories Section */}
      <section className="bg-surface py-20">
        <div className="container mx-auto px-4">
          <h2 className="mb-12 text-center text-3xl font-bold text-text-primary">
            Popular Service Categories
          </h2>
          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
            {[
              { icon: Wrench, name: "Plumbing", description: "Leaks, repairs, installations" },
              { icon: Zap, name: "Electrical", description: "Wiring, repairs, installations" },
              { icon: Home, name: "Carpentry", description: "Furniture, repairs, custom work" },
              { icon: Hammer, name: "General Repair", description: "Home maintenance & fixes" },
            ].map((category) => (
              <Card key={category.name} className="cursor-pointer transition-shadow hover:shadow-lg">
                <CardHeader>
                  <category.icon className="mb-2 h-8 w-8 text-primary" />
                  <CardTitle className="text-xl">{category.name}</CardTitle>
                  <CardDescription>{category.description}</CardDescription>
                </CardHeader>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="bg-primary py-20 text-white">
        <div className="container mx-auto px-4 text-center">
          <h2 className="mb-4 text-3xl font-bold">Ready to Get Started?</h2>
          <p className="mb-8 text-xl opacity-90">
            Join thousands of satisfied customers and service providers.
          </p>
          <div className="flex flex-col gap-4 sm:flex-row sm:justify-center">
            <Button asChild size="lg" variant="secondary" className="text-lg">
              <Link href="/register/customer">Sign Up as Customer</Link>
            </Button>
            <Button asChild size="lg" variant="outline" className="text-lg border-white text-white hover:bg-white/10">
              <Link href="/register/provider">Sign Up as Provider</Link>
            </Button>
          </div>
        </div>
      </section>
    </div>
  );
}
