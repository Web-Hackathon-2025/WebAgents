import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Toaster } from "@/components/ui/sonner";
import { Header } from "@/components/layout/header";
import { ErrorBoundary } from "@/components/shared/error-boundary";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
});

export const metadata: Metadata = {
  title: {
    default: "Karigar - Find Local Service Providers",
    template: "%s | Karigar",
  },
  description: "Connect with trusted local service providers in your area. Find plumbers, electricians, carpenters, and more.",
  keywords: ["plumber", "electrician", "services", "local", "handyman", "home services"],
  authors: [{ name: "Karigar Team" }],
  creator: "Karigar",
  openGraph: {
    type: "website",
    locale: "en_US",
    url: "https://karigar.com",
    title: "Karigar - Find Local Service Providers",
    description: "Connect with trusted local service providers in your area.",
    siteName: "Karigar",
  },
  twitter: {
    card: "summary_large_image",
    title: "Karigar - Find Local Service Providers",
    description: "Connect with trusted local service providers in your area.",
  },
  robots: {
    index: true,
    follow: true,
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={inter.variable}>
      <body className="antialiased">
        <ErrorBoundary>
          <Header />
          {children}
          <Toaster position="top-right" richColors />
        </ErrorBoundary>
      </body>
    </html>
  );
}
