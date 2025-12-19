"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { User, Wrench } from "lucide-react";

export default function RegisterPage() {
  const router = useRouter();

  return (
    <div className="flex min-h-screen items-center justify-center bg-surface px-4 py-12">
      <div className="w-full max-w-4xl">
        <div className="mb-8 text-center">
          <h1 className="mb-2 text-4xl font-bold text-text-primary">Join Karigar</h1>
          <p className="text-lg text-text-secondary">Choose your account type to get started</p>
        </div>

        <div className="grid gap-6 md:grid-cols-2">
          <Card className="cursor-pointer transition-all hover:shadow-lg">
            <CardHeader className="text-center">
              <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-customer-accent/10">
                <User className="h-8 w-8 text-customer-accent" />
              </div>
              <CardTitle className="text-2xl">Customer</CardTitle>
              <CardDescription className="mt-2">
                Find and book trusted service providers in your area
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ul className="mb-6 space-y-2 text-sm text-text-secondary">
                <li className="flex items-center">
                  <span className="mr-2">✓</span>
                  Search for local service providers
                </li>
                <li className="flex items-center">
                  <span className="mr-2">✓</span>
                  Book services easily
                </li>
                <li className="flex items-center">
                  <span className="mr-2">✓</span>
                  Rate and review providers
                </li>
              </ul>
              <Button
                className="w-full"
                onClick={() => router.push("/register/customer")}
              >
                Sign Up as Customer
              </Button>
            </CardContent>
          </Card>

          <Card className="cursor-pointer transition-all hover:shadow-lg">
            <CardHeader className="text-center">
              <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-provider-accent/10">
                <Wrench className="h-8 w-8 text-provider-accent" />
              </div>
              <CardTitle className="text-2xl">Provider</CardTitle>
              <CardDescription className="mt-2">
                Offer your services and grow your business
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ul className="mb-6 space-y-2 text-sm text-text-secondary">
                <li className="flex items-center">
                  <span className="mr-2">✓</span>
                  Create and manage services
                </li>
                <li className="flex items-center">
                  <span className="mr-2">✓</span>
                  Accept booking requests
                </li>
                <li className="flex items-center">
                  <span className="mr-2">✓</span>
                  Build your reputation
                </li>
              </ul>
              <Button
                className="w-full"
                variant="outline"
                onClick={() => router.push("/register/provider")}
              >
                Sign Up as Provider
              </Button>
            </CardContent>
          </Card>
        </div>

        <p className="mt-8 text-center text-sm text-text-secondary">
          Already have an account?{" "}
          <Link href="/login" className="text-primary hover:underline">
            Sign in
          </Link>
        </p>
      </div>
    </div>
  );
}
