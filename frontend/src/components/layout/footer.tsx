import Link from "next/link";
import { ROUTES } from "@/lib/constants/routes";

export function Footer() {
  return (
    <footer className="border-t border-border bg-surface">
      <div className="container mx-auto px-4 py-12">
        <div className="grid gap-8 md:grid-cols-4">
          <div>
            <h3 className="mb-4 text-lg font-semibold text-text-primary">Karigar</h3>
            <p className="text-sm text-text-secondary">
              Connecting customers with trusted local service providers.
            </p>
          </div>
          <div>
            <h4 className="mb-4 text-sm font-semibold text-text-primary">For Customers</h4>
            <ul className="space-y-2 text-sm text-text-secondary">
              <li>
                <Link href={ROUTES.SEARCH} className="hover:text-primary">
                  Find Services
                </Link>
              </li>
              <li>
                <Link href={ROUTES.CUSTOMER_DASHBOARD} className="hover:text-primary">
                  Dashboard
                </Link>
              </li>
              <li>
                <Link href={ROUTES.CUSTOMER_BOOKINGS} className="hover:text-primary">
                  My Bookings
                </Link>
              </li>
            </ul>
          </div>
          <div>
            <h4 className="mb-4 text-sm font-semibold text-text-primary">For Providers</h4>
            <ul className="space-y-2 text-sm text-text-secondary">
              <li>
                <Link href={ROUTES.REGISTER_PROVIDER} className="hover:text-primary">
                  Become a Provider
                </Link>
              </li>
              <li>
                <Link href={ROUTES.PROVIDER_DASHBOARD} className="hover:text-primary">
                  Provider Dashboard
                </Link>
              </li>
            </ul>
          </div>
          <div>
            <h4 className="mb-4 text-sm font-semibold text-text-primary">Company</h4>
            <ul className="space-y-2 text-sm text-text-secondary">
              <li>
                <Link href="/about" className="hover:text-primary">
                  About Us
                </Link>
              </li>
              <li>
                <Link href="/contact" className="hover:text-primary">
                  Contact
                </Link>
              </li>
              <li>
                <Link href="/terms" className="hover:text-primary">
                  Terms of Service
                </Link>
              </li>
              <li>
                <Link href="/privacy" className="hover:text-primary">
                  Privacy Policy
                </Link>
              </li>
            </ul>
          </div>
        </div>
        <div className="mt-8 border-t border-border pt-8 text-center text-sm text-text-secondary">
          <p>&copy; {new Date().getFullYear()} Karigar. All rights reserved.</p>
        </div>
      </div>
    </footer>
  );
}
