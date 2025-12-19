"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { mockDataService, DEMO_CREDENTIALS } from "@/lib/mock-data";
import { useAuthStore } from "@/stores/auth-store";
import { Eye, EyeOff, User, Settings, Shield, Copy, Check } from "lucide-react";

export function DemoModeToggle() {
  const [isMockMode, setIsMockMode] = useState(false);
  const [copiedCredential, setCopiedCredential] = useState<string | null>(null);
  const { login, logout, isAuthenticated } = useAuthStore();

  useEffect(() => {
    setIsMockMode(mockDataService.isMockModeEnabled());
  }, []);

  const toggleMockMode = () => {
    if (isMockMode) {
      mockDataService.disableMockMode();
      setIsMockMode(false);
      if (isAuthenticated) {
        logout();
      }
    } else {
      mockDataService.enableMockMode();
      setIsMockMode(true);
    }
  };

  const copyToClipboard = async (text: string, type: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedCredential(type);
      setTimeout(() => setCopiedCredential(null), 2000);
    } catch (err) {
      console.error('Failed to copy text: ', err);
    }
  };

  const handleDemoLogin = async (role: 'customer' | 'provider' | 'admin') => {
    try {
      if (!isMockMode) {
        mockDataService.enableMockMode();
        setIsMockMode(true);
      }
      const credentials = DEMO_CREDENTIALS[role];
      await login(credentials);
    } catch (error) {
      console.error("Demo login failed:", error);
    }
  };

  return (
    <Card className="w-full max-w-2xl mx-auto">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              {isMockMode ? <Eye className="h-5 w-5" /> : <EyeOff className="h-5 w-5" />}
              Demo Mode
              {isMockMode && <Badge variant="secondary" className="bg-green-100 text-green-700">Active</Badge>}
            </CardTitle>
            <CardDescription>
              {isMockMode 
                ? "Using sample data for demonstration. Perfect for testing features!" 
                : "Enable demo mode to test the application with sample data."
              }
            </CardDescription>
          </div>
          <Button
            onClick={toggleMockMode}
            variant={isMockMode ? "destructive" : "default"}
            size="sm"
          >
            {isMockMode ? "Disable" : "Enable"} Demo
          </Button>
        </div>
      </CardHeader>

      {isMockMode && (
        <CardContent className="space-y-4">
          <div>
            <h4 className="font-semibold mb-3">Quick Demo Login</h4>
            <div className="grid gap-3 sm:grid-cols-3">
              <Button
                onClick={() => handleDemoLogin('customer')}
                variant="outline"
                className="flex items-center gap-2 h-auto p-3"
              >
                <User className="h-4 w-4" />
                <div className="text-left">
                  <div className="font-medium">Customer</div>
                  <div className="text-xs text-gray-500">John Smith</div>
                </div>
              </Button>
              
              <Button
                onClick={() => handleDemoLogin('provider')}
                variant="outline"
                className="flex items-center gap-2 h-auto p-3"
              >
                <Settings className="h-4 w-4" />
                <div className="text-left">
                  <div className="font-medium">Provider</div>
                  <div className="text-xs text-gray-500">Mike Johnson</div>
                </div>
              </Button>
              
              <Button
                onClick={() => handleDemoLogin('admin')}
                variant="outline"
                className="flex items-center gap-2 h-auto p-3"
              >
                <Shield className="h-4 w-4" />
                <div className="text-left">
                  <div className="font-medium">Admin</div>
                  <div className="text-xs text-gray-500">Admin User</div>
                </div>
              </Button>
            </div>
          </div>

          <div>
            <h4 className="font-semibold mb-3">Demo Credentials</h4>
            <div className="space-y-2 text-sm">
              {Object.entries(DEMO_CREDENTIALS).map(([role, credentials]) => (
                <div key={role} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                  <div>
                    <span className="font-medium capitalize">{role}:</span>
                    <span className="ml-2 text-gray-600">{credentials.email}</span>
                    <span className="ml-2 text-gray-500">/ {credentials.password}</span>
                  </div>
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => copyToClipboard(`${credentials.email} / ${credentials.password}`, role)}
                    className="h-6 w-6 p-0"
                  >
                    {copiedCredential === role ? (
                      <Check className="h-3 w-3 text-green-600" />
                    ) : (
                      <Copy className="h-3 w-3" />
                    )}
                  </Button>
                </div>
              ))}
            </div>
          </div>

          <div className="text-xs text-gray-500 bg-blue-50 p-3 rounded">
            <strong>Note:</strong> Demo mode uses mock data stored locally. No real API calls are made. 
            Perfect for testing features, UI components, and user flows without affecting real data.
          </div>
        </CardContent>
      )}
    </Card>
  );
}