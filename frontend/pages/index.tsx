import { SignInButton, SignUpButton, SignedIn, SignedOut, UserButton } from "@clerk/nextjs";
import Link from "next/link";
import Head from "next/head";

export default function Home() {
  return (
    <>
      <Head>
        <title>Samy AI Financial Advisor - Intelligent Portfolio Management</title>
      </Head>
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-gray-50">
      {/* Navigation */}
      <nav className="px-8 py-6 bg-white shadow-sm" style={{ borderBottom: '1px solid #E5E7EB' }}>
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <div className="flex items-center gap-3">
            <img 
              src="/vanguard-logo.svg" 
              alt="Vanguard" 
              className="h-8 w-auto"
              style={{ maxHeight: '32px' }}
            />
            <span className="text-lg font-semibold" style={{ color: '#BA0C2F' }}>
              AI Financial Wellbeing
            </span>
          </div>
          <div className="flex gap-4">
            <SignedOut>
              <SignInButton mode="modal">
                <button 
                  className="px-6 py-2 border rounded-lg transition-colors"
                  style={{ 
                    borderColor: '#BA0C2F', 
                    color: '#BA0C2F',
                    backgroundColor: 'transparent'
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.backgroundColor = '#BA0C2F';
                    e.currentTarget.style.color = 'white';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.backgroundColor = 'transparent';
                    e.currentTarget.style.color = '#BA0C2F';
                  }}
                >
                  Sign In
                </button>
              </SignInButton>
              <SignUpButton mode="modal">
                <button 
                  className="px-6 py-2 rounded-lg transition-colors"
                  style={{ 
                    backgroundColor: '#BA0C2F', 
                    color: 'white'
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.backgroundColor = '#D91E47';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.backgroundColor = '#BA0C2F';
                  }}
                >
                  Get Started
                </button>
              </SignUpButton>
            </SignedOut>
            <SignedIn>
              <div className="flex items-center gap-4">
                <Link href="/dashboard">
                  <button 
                    className="px-6 py-2 text-white rounded-lg transition-colors"
                    style={{ backgroundColor: '#BA0C2F' }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.backgroundColor = '#D91E47';
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.backgroundColor = '#BA0C2F';
                    }}
                  >
                    Go to Dashboard
                  </button>
                </Link>
                <UserButton afterSignOutUrl="/" />
              </div>
            </SignedIn>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="px-8 py-20">
        <div className="max-w-7xl mx-auto text-center">
          <h1 className="text-5xl font-bold mb-6" style={{ color: '#8B0A23', letterSpacing: '-0.01em' }}>
            Your AI-Powered Financial Future
          </h1>
          <p className="text-xl mb-8 max-w-3xl mx-auto" style={{ color: '#4a4a4a' }}>
            Experience the power of autonomous AI agents working together to analyze your portfolio, 
            plan your retirement, and optimize your investments.
          </p>
          <div className="flex gap-6 justify-center">
            <SignedOut>
              <SignUpButton mode="modal">
                <button 
                  className="px-8 py-4 text-lg rounded-lg transition-colors shadow-lg"
                  style={{ backgroundColor: '#BA0C2F', color: 'white' }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.backgroundColor = '#D91E47';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.backgroundColor = '#BA0C2F';
                  }}
                >
                  Start Your Analysis
                </button>
              </SignUpButton>
            </SignedOut>
            <SignedIn>
              <Link href="/dashboard">
                <button 
                  className="px-8 py-4 text-lg rounded-lg transition-colors shadow-lg"
                  style={{ backgroundColor: '#BA0C2F', color: 'white' }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.backgroundColor = '#D91E47';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.backgroundColor = '#BA0C2F';
                  }}
                >
                  Open Dashboard
                </button>
              </Link>
            </SignedIn>
            <button 
              className="px-8 py-4 border-2 text-lg rounded-lg transition-colors"
              style={{ 
                borderColor: '#BA0C2F', 
                color: '#BA0C2F',
                backgroundColor: 'transparent'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor = '#BA0C2F';
                e.currentTarget.style.color = 'white';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = 'transparent';
                e.currentTarget.style.color = '#BA0C2F';
              }}
            >
              Watch Demo
            </button>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="px-8 py-20 bg-white">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-12" style={{ color: '#BA0C2F', letterSpacing: '-0.01em' }}>
            Meet Your AI Advisory Team
          </h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            <div className="text-center p-6 rounded-xl hover:shadow-lg transition-shadow">
              <div className="text-4xl mb-4">🎯</div>
              <h3 className="text-xl font-semibold text-ai-accent mb-2">Financial Planner</h3>
              <p className="text-gray-600">Coordinates your complete financial analysis with intelligent orchestration</p>
            </div>
            <div className="text-center p-6 rounded-xl hover:shadow-lg transition-shadow">
              <div className="text-4xl mb-4">📊</div>
              <h3 className="text-xl font-semibold text-primary mb-2">Portfolio Analyst</h3>
              <p className="text-gray-600">Deep analysis of holdings, performance metrics, and risk assessment</p>
            </div>
            <div className="text-center p-6 rounded-xl hover:shadow-lg transition-shadow">
              <div className="text-4xl mb-4">📈</div>
              <h3 className="text-xl font-semibold text-success mb-2">Chart Specialist</h3>
              <p className="text-gray-600">Visualizes your portfolio composition with interactive charts</p>
            </div>
            <div className="text-center p-6 rounded-xl hover:shadow-lg transition-shadow">
              <div className="text-4xl mb-4">🎯</div>
              <h3 className="text-xl font-semibold text-accent mb-2">Retirement Planner</h3>
              <p className="text-gray-600">Projects your retirement readiness with Monte Carlo simulations</p>
            </div>
          </div>
        </div>
      </section>

      {/* Benefits Section */}
      <section className="px-8 py-20 bg-gradient-to-r from-primary/10 to-ai-accent/10">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-12" style={{ color: '#BA0C2F', letterSpacing: '-0.01em' }}>
            Enterprise-Grade AI Advisory
          </h2>
          <div className="grid md:grid-cols-3 gap-8">
            <div className="bg-white p-8 rounded-xl shadow-md">
              <div className="text-accent text-2xl mb-4">⚡</div>
              <h3 className="text-xl font-semibold mb-3">Real-Time Analysis</h3>
              <p className="text-gray-600">Watch AI agents collaborate in parallel to analyze your complete financial picture</p>
            </div>
            <div className="bg-white p-8 rounded-xl shadow-md">
              <div className="text-accent text-2xl mb-4">🔒</div>
              <h3 className="text-xl font-semibold mb-3">Bank-Level Security</h3>
              <p className="text-gray-600">Your data is protected with enterprise security and row-level access controls</p>
            </div>
            <div className="bg-white p-8 rounded-xl shadow-md">
              <div className="text-accent text-2xl mb-4">📊</div>
              <h3 className="text-xl font-semibold mb-3">Comprehensive Reports</h3>
              <p className="text-gray-600">Detailed markdown reports with interactive charts and retirement projections</p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="px-8 py-20 text-white" style={{ backgroundColor: '#BA0C2F' }}>
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl font-bold mb-6" style={{ letterSpacing: '-0.01em' }}>
            Ready to Transform Your Financial Future?
          </h2>
          <p className="text-xl mb-8" style={{ opacity: 0.9 }}>
            Join thousands of investors using AI to optimize their portfolios
          </p>
          <SignUpButton mode="modal">
            <button 
              className="px-8 py-4 font-semibold text-lg rounded-lg transition-colors shadow-lg"
              style={{ backgroundColor: '#EDBA75', color: '#BA0C2F' }}
              onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor = '#f5c98a';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = '#EDBA75';
              }}
            >
              Get Started Free
            </button>
          </SignUpButton>
        </div>
      </section>

      {/* Footer */}
      <footer className="px-8 py-6 text-center text-sm" style={{ backgroundColor: '#1F2937', color: '#9CA3AF' }}>
        <p>© 2025 The Vanguard Group, Inc. All rights reserved. Vanguard Marketing Corporation, Distributor.</p>
        <p className="mt-2">
          This AI-generated advice has not been vetted by a qualified financial advisor and should not be used for trading decisions. 
          For informational purposes only.
        </p>
      </footer>
    </div>
    </>
  );
}