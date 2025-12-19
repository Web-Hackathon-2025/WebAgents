"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { useAuthStore } from "@/stores/auth-store";
import { User, LogOut, Settings, Menu, UserPlus, LogIn } from "lucide-react";
import { cn } from "@/lib/utils/cn";
import { mockDataService, DEMO_CREDENTIALS } from "@/lib/mock-data";

export function Header() {
  const pathname = usePathname();
  const { user, isAuthenticated, logout, login } = useAuthStore();

  const handleLogout = async () => {
    await logout();
    window.location.href = "/";
  };

  const handleDemoLogin = async (role: 'customer' | 'provider' | 'admin') => {
    try {
      mockDataService.enableMockMode();
      const credentials = DEMO_CREDENTIALS[role];
      await login(credentials);
    } catch (error) {
      console.error("Demo login failed:", error);
    }
  };

  return (
    <header className="sticky top-0 z-50 w-full border-b border-border bg-background">
      <div className="container mx-auto flex h-16 items-center justify-between px-4">
        <Link href="/" className="flex items-center space-x-2">
          <span className="text-2xl font-bold text-primary">Karigar</span>
        </Link>

        <nav className="hidden items-center space-x-6 md:flex">
          <Link
            href="/search"
            className={cn(
              "text-sm font-medium transition-colors hover:text-primary",
              pathname === "/search" ? "text-primary" : "text-text-secondary"
            )}
          >
            Find Services
          </Link>
          {isAuthenticated && user?.role === "customer" && (
            <Link
              href="/dashboard"
              className={cn(
                "text-sm font-medium transition-colors hover:text-primary",
                pathname?.startsWith("/dashboard") ? "text-primary" : "text-text-secondary"
              )}
            >
              Dashboard
            </Link>
          )}
          {isAuthenticated && user?.role === "provider" && (
            <Link
              href="/provider/dashboard"
              className={cn(
                "text-sm font-medium transition-colors hover:text-primary",
                pathname?.startsWith("/provider") ? "text-primary" : "text-text-secondary"
              )}
            >
              Provider Dashboard
            </Link>
          )}
        </nav>

        <div className="flex items-center space-x-4">
          {isAuthenticated ? (
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" className="relative h-10 w-10 rounded-full">
                  <Avatar>
                    <AvatarImage src={user?.avatar} alt={user?.fullName} />
                    <AvatarFallback>
                      {user?.fullName?.charAt(0).toUpperCase() || "U"}
                    </AvatarFallback>
                  </Avatar>
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent className="w-56" align="end">
                <DropdownMenuLabel>
                  <div className="flex flex-col space-y-1">
                    <p className="text-sm font-medium">{user?.fullName}</p>
                    <p className="text-xs text-gray-500">{user?.email}</p>
                    <p className="text-xs font-medium text-blue-600 capitalize">{user?.role}</p>
                  </div>
                </DropdownMenuLabel>
                <DropdownMenuSeparator />
                <DropdownMenuItem asChild>
                  <Link href="/profile" className="flex items-center">
                    <User className="mr-2 h-4 w-4" />
                    Profile
                  </Link>
                </DropdownMenuItem>
                <DropdownMenuItem asChild>
                  <Link href="/settings" className="flex items-center">
                    <Settings className="mr-2 h-4 w-4" />
                    Settings
                  </Link>
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem onClick={handleLogout} className="text-red-600">
                  <LogOut className="mr-2 h-4 w-4" />
                  Log out
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          ) : (
            <div className="flex items-center space-x-3">
              {/* Demo Login Dropdown */}
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="outline" size="sm" className="hidden sm:flex border-blue-200 text-blue-600 hover:bg-blue-50">
                    <UserPlus className="mr-2 h-4 w-4" />
                    Demo Login
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent className="w-48" align="end">
                  <DropdownMenuLabel>Try Demo Account</DropdownMenuLabel>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem onClick={() => handleDemoLogin('customer')}>
                    <User className="mr-2 h-4 w-4" />
                    Customer Demo
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={() => handleDemoLogin('provider')}>
                    <Settings className="mr-2 h-4 w-4" />
                    Provider Demo
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={() => handleDemoLogin('admin')}>
                    <LogOut className="mr-2 h-4 w-4" />
                    Admin Demo
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>

              {/* Regular Auth Buttons */}
              <Button asChild variant="ghost" size="sm" className="text-gray-600 hover:text-gray-900">
                <Link href="/login" className="flex items-center">
                  <LogIn className="mr-2 h-4 w-4" />
                  <span className="hidden sm:inline">Log in</span>
                  <span className="sm:hidden">Login</span>
                </Link>
              </Button>
              <Button asChild size="sm" className="bg-blue-600 hover:bg-blue-700 text-white shadow-md">
                <Link href="/register/customer" className="flex items-center">
                  <UserPlus className="mr-2 h-4 w-4" />
                  <span className="hidden sm:inline">Sign up</span>
                  <span className="sm:hidden">Join</span>
                </Link>
              </Button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
