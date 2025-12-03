import { useState } from 'react';
import { useRouter } from 'next/router';
import Layout from '../../components/Layout';
import Head from 'next/head';

export default function SocialSecurityAgent() {
  const router = useRouter();

  return (
    <>
      <Head>
        <title>Social Security Agent - AI Financial Wellbeing</title>
      </Head>
      <Layout>
        <div className="container mx-auto px-4 py-8">
          <div className="max-w-4xl mx-auto">
            <div className="text-center mb-8">
              <div className="text-6xl mb-4">🧓</div>
              <h1 className="text-4xl font-bold mb-4" style={{ color: '#BA0C2F' }}>
                Social Security Agent
              </h1>
              <p className="text-xl text-gray-600">
                Plan for Social Security benefits and transition to retirement
              </p>
            </div>

            <div className="bg-white rounded-lg shadow-lg p-8 mb-8">
              <h2 className="text-2xl font-semibold mb-4" style={{ color: '#BA0C2F' }}>
                How I Can Help You
              </h2>
              <ul className="space-y-4 text-gray-700">
                <li className="flex items-start">
                  <span className="text-2xl mr-3">📅</span>
                  <div>
                    <strong>Benefit Timing:</strong> Determine the optimal time to claim Social Security benefits
                  </div>
                </li>
                <li className="flex items-start">
                  <span className="text-2xl mr-3">💼</span>
                  <div>
                    <strong>Retirement Transition:</strong> Plan your transition from work to retirement
                  </div>
                </li>
                <li className="flex items-start">
                  <span className="text-2xl mr-3">🏖️</span>
                  <div>
                    <strong>Lifestyle Planning:</strong> Plan for your desired retirement lifestyle
                  </div>
                </li>
                <li className="flex items-start">
                  <span className="text-2xl mr-3">📊</span>
                  <div>
                    <strong>Benefit Optimization:</strong> Maximize your Social Security benefits
                  </div>
                </li>
              </ul>
            </div>

            <div className="bg-white rounded-lg shadow-lg p-8 mb-8">
              <h2 className="text-2xl font-semibold mb-4" style={{ color: '#BA0C2F' }}>
                Get Started
              </h2>
              <p className="text-gray-700 mb-6">
                The Social Security Agent will help you understand your Social Security benefits and create a plan to optimize them for your retirement.
              </p>
              <div className="flex gap-4">
                <button
                  onClick={() => router.push('/advisor-team')}
                  className="btn btn-primary"
                  style={{
                    backgroundColor: '#BA0C2F',
                    color: 'white',
                    padding: '0.75rem 1.5rem',
                    borderRadius: '4px',
                    border: 'none',
                    cursor: 'pointer',
                    fontWeight: 500
                  }}
                >
                  Start Analysis
                </button>
                <button
                  onClick={() => router.push('/dashboard')}
                  className="btn btn-secondary"
                  style={{
                    backgroundColor: 'transparent',
                    color: '#BA0C2F',
                    padding: '0.75rem 1.5rem',
                    borderRadius: '4px',
                    border: '1px solid #BA0C2F',
                    cursor: 'pointer',
                    fontWeight: 500
                  }}
                >
                  Back to Dashboard
                </button>
              </div>
            </div>
          </div>
        </div>
      </Layout>
    </>
  );
}

