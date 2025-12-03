import { useUser, UserButton, Protect } from "@clerk/nextjs";
import Link from "next/link";
import { useRouter } from "next/router";
import { ReactNode } from "react";
import PageTransition from "./PageTransition";

interface LayoutProps {
  children: ReactNode;
}

export default function Layout({ children }: LayoutProps) {
  const { user } = useUser();
  const router = useRouter();

  // Helper to determine if a link is active
  const isActive = (path: string) => router.pathname === path;

  return (
    <Protect fallback={
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <p className="text-gray-600">Redirecting to sign in...</p>
        </div>
      </div>
    }>
      <div className="min-h-screen flex flex-col" style={{ backgroundColor: '#F5F5F5' }}>
        {/* Navigation */}
        <nav className="header sticky">
          <div className="container">
            <div className="flex justify-between items-center" style={{ height: '64px' }}>
              {/* Logo and Brand */}
              <div className="flex items-center gap-4">
                <Link href="/dashboard" className="flex items-center gap-3">
                  <img 
                    src="/vanguard-logo.svg" 
                    alt="Vanguard" 
                    className="logo"
                  />
                  <span className="text-lg font-semibold" style={{ color: 'var(--vanguard-red)', marginLeft: '12px' }}>
                    AI Financial Wellbeing
                  </span>
                </Link>

                {/* Navigation Links */}
                <div className="hidden md:flex items-center gap-6">
                  <Link
                    href="/dashboard"
                    className={`nav-link ${isActive("/dashboard") ? "active" : ""}`}
                  >
                    Dashboard
                  </Link>
                  <Link
                    href="/accounts"
                    className={`nav-link ${isActive("/accounts") ? "active" : ""}`}
                  >
                    Accounts
                  </Link>
                  <Link
                    href="/advisor-team"
                    className={`nav-link ${isActive("/advisor-team") ? "active" : ""}`}
                  >
                    Advisor Team
                  </Link>
                  <Link
                    href="/analysis"
                    className={`nav-link ${isActive("/analysis") ? "active" : ""}`}
                  >
                    Analysis
                  </Link>
                </div>
              </div>

              {/* User Section */}
              <div className="flex items-center gap-4">
                <span className="hidden sm:inline text-sm" style={{ color: 'var(--text-secondary)' }}>
                  {user?.firstName || user?.emailAddresses[0]?.emailAddress}
                </span>
                <UserButton afterSignOutUrl="/" />
              </div>
            </div>

            {/* Mobile Navigation */}
            <div className="md:hidden flex items-center gap-4 pb-3" style={{ paddingTop: '12px' }}>
              <Link
                href="/dashboard"
                className={`nav-link ${isActive("/dashboard") ? "active" : ""}`}
              >
                Dashboard
              </Link>
              <Link
                href="/accounts"
                className={`nav-link ${isActive("/accounts") ? "active" : ""}`}
              >
                Accounts
              </Link>
              <Link
                href="/advisor-team"
                className={`nav-link ${isActive("/advisor-team") ? "active" : ""}`}
              >
                Advisor Team
              </Link>
              <Link
                href="/analysis"
                className={`nav-link ${isActive("/analysis") ? "active" : ""}`}
              >
                Analysis
              </Link>
            </div>
          </div>
        </nav>

        {/* Main Content */}
        <main className="flex-1">
          <PageTransition>
            {children}
          </PageTransition>
        </main>

        {/* Footer */}
        <footer className="mt-auto">
          <div className="container" style={{ paddingTop: 'var(--spacing-lg)', paddingBottom: 'var(--spacing-lg)' }}>
            <div className="disclaimer">
              <p className="text-sm font-medium mb-2" style={{ color: 'var(--text-primary)' }}>
                Important Disclaimer
              </p>
              <p className="text-xs" style={{ color: 'var(--text-secondary)', lineHeight: '1.5' }}>
                This AI-generated advice has not been vetted by a qualified financial advisor and should not be used for trading decisions.
                For informational purposes only. Always consult with a licensed financial professional before making investment decisions.
              </p>
            </div>
            <div className="copyright">
              <p>
                © 2025 The Vanguard Group, Inc. All rights reserved. Vanguard Marketing Corporation, Distributor.
              </p>
            </div>
          </div>
        </footer>
      </div>
    </Protect>
  );
}