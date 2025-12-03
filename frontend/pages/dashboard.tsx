import { useUser, useAuth } from "@clerk/nextjs";
import { useEffect, useState, useCallback } from "react";
import { useRouter } from "next/router";
import { API_URL } from "../lib/config";
import Layout from "../components/Layout";
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from "recharts";
import { Skeleton, SkeletonCard } from "../components/Skeleton";
import { showToast } from "../components/Toast";
import Head from "next/head";
import WellnessScore from "../components/WellnessScore";

interface UserData {
  clerk_user_id: string;
  display_name: string;
  years_until_retirement: number;
  target_retirement_income: number;
  asset_class_targets: Record<string, number>;
  region_targets: Record<string, number>;
}

interface Account {
  account_id: string;
  clerk_user_id: string;
  account_name: string;
  account_type: string;
  account_purpose: string;
  cash_balance: number;
  created_at: string;
  updated_at: string;
}

interface Position {
  position_id: string;
  account_id: string;
  symbol: string;
  quantity: number;
  created_at: string;
  updated_at: string;
}

interface Instrument {
  symbol: string;
  name: string;
  instrument_type: string;
  current_price?: number;
  asset_class_allocation?: Record<string, number>;
  region_allocation?: Record<string, number>;
  sector_allocation?: Record<string, number>;
}

export default function Dashboard() {
  const { user, isLoaded: userLoaded } = useUser();
  const { getToken } = useAuth();
  const router = useRouter();
  const [userData, setUserData] = useState<UserData | null>(null);
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [positions, setPositions] = useState<Record<string, Position[]>>({});
  const [instruments, setInstruments] = useState<Record<string, Instrument>>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastAnalysisDate, setLastAnalysisDate] = useState<string | null>(null);
  const [wellnessData, setWellnessData] = useState<{
    overallScore: number;
    pillars: Array<{
      name: string;
      score: number;
      rating: string;
      description: string;
      improvementTip: string;
      color: string;
      bgColor?: string;
    }>;
    lastUpdated: string;
    nbaRecommendations?: Array<{
      nba_code: string;
      agent_route: string;
      agent_name: string;
      icon: string;
      description: string;
    }>;
  } | null>(null);
  const [wellnessLoading, setWellnessLoading] = useState(true);

  // Calculate portfolio summary
  const calculatePortfolioSummary = useCallback(() => {
    let totalValue = 0;
    const assetClassBreakdown: Record<string, number> = {
      equity: 0,
      fixed_income: 0,
      alternatives: 0,
      cash: 0
    };

    // Add cash balances
    accounts.forEach(account => {
      const cashBalance = Number(account.cash_balance);
      totalValue += cashBalance;
      assetClassBreakdown.cash += cashBalance;
    });

    // Add position values
    Object.entries(positions).forEach(([, accountPositions]) => {
      accountPositions.forEach(position => {
        const instrument = instruments[position.symbol];
        if (instrument?.current_price) {
          const positionValue = Number(position.quantity) * Number(instrument.current_price);
          totalValue += positionValue;

          // Add to asset class breakdown
          if (instrument.asset_class_allocation) {
            Object.entries(instrument.asset_class_allocation).forEach(([assetClass, percentage]) => {
              assetClassBreakdown[assetClass] = (assetClassBreakdown[assetClass] || 0) + (positionValue * percentage / 100);
            });
          }
        }
      });
    });

    return { totalValue, assetClassBreakdown };
  }, [accounts, positions, instruments]);

  // Load wellness score
  useEffect(() => {
    async function loadWellnessScore() {
      if (!userLoaded || !user) return;

      try {
        const token = await getToken();
        if (!token) {
          setWellnessLoading(false);
          return;
        }

        const apiUrl = API_URL || 'http://localhost:8000';
        const response = await fetch(`${apiUrl}/api/wellness/score`, {
          headers: {
            "Authorization": `Bearer ${token}`,
          },
        });

        // If no wellness score, don't show it (user can complete questionnaire separately)
        if (response.status === 404) {
          setWellnessLoading(false);
          return;
        }

        if (!response.ok) {
          setWellnessLoading(false);
          return;
        }

        const data = await response.json();
        setWellnessData({
          overallScore: data.overallScore,
          pillars: data.pillars,
          lastUpdated: data.lastUpdated,
          nbaRecommendations: data.nbaRecommendations || [],
        });
      } catch (err) {
        // Ignore errors, just don't show wellness score
        console.log('Wellness score load error:', err);
      } finally {
        setWellnessLoading(false);
      }
    }

    loadWellnessScore();
  }, [userLoaded, user, getToken]);

  // Load user data and accounts
  useEffect(() => {
    async function loadData() {
      if (!userLoaded || !user) return;

      try {
        const token = await getToken();
        if (!token) {
          setError("Not authenticated");
          setLoading(false);
          return;
        }

        // Get/create user
        const userResponse = await fetch(`${API_URL}/api/user`, {
          headers: {
            "Authorization": `Bearer ${token}`,
          },
        });

        if (!userResponse.ok) {
          const errorText = await userResponse.text();
          console.error('API error response:', errorText);
          throw new Error(`Failed to sync user: ${userResponse.status} - ${errorText}`);
        }

        const response = await userResponse.json();
        const userData = response.user; // Extract user from response
        setUserData(userData);

        // Get accounts
        const accountsResponse = await fetch(`${API_URL}/api/accounts`, {
          headers: {
            "Authorization": `Bearer ${token}`,
          },
        });

        if (accountsResponse.ok) {
          const accountsData = await accountsResponse.json();
          setAccounts(accountsData);

          // Get positions for each account
          const positionsMap: Record<string, Position[]> = {};
          const instrumentsMap: Record<string, Instrument> = {};

          for (const account of accountsData) {
            // Skip if account has no ID
            if (!account.id) {
              console.warn('Account missing ID in dashboard:', account);
              continue;
            }

            const positionsResponse = await fetch(`${API_URL}/api/accounts/${account.id}/positions`, {
              headers: {
                "Authorization": `Bearer ${token}`,
              },
            });

            if (positionsResponse.ok) {
              const positionsData = await positionsResponse.json();
              // API returns positions in a positions key
              positionsMap[account.id] = positionsData.positions || [];

              // Store instrument data from each position
              for (const position of positionsData.positions || []) {
                if (position.instrument) {
                  instrumentsMap[position.symbol] = position.instrument as Instrument;
                }
              }
            }
          }

          setPositions(positionsMap);
          setInstruments(instrumentsMap);
        }

        // Get last analysis date
        // This would come from the jobs endpoint in a real implementation
        setLastAnalysisDate(null);

      } catch (err) {
        console.error("Error loading data:", err);
        setError(err instanceof Error ? err.message : "Failed to load data");
      } finally {
        setLoading(false);
      }
    }

    loadData();
  }, [userLoaded, user, getToken]);

  // Listen for analysis completion events to refresh data
  useEffect(() => {
    if (!userLoaded || !user) return;

    const handleAnalysisCompleted = async () => {
      try {
        const token = await getToken();
        if (!token) return;

        console.log('Analysis completed - refreshing dashboard data...');

        // Refresh accounts to get latest prices
        const accountsResponse = await fetch(`${API_URL}/api/accounts`, {
          headers: {
            "Authorization": `Bearer ${token}`,
          },
        });

        if (accountsResponse.ok) {
          const accountsData = await accountsResponse.json();
          setAccounts(accountsData.accounts || []);

          // Load positions for each account
          const positionsData: Record<string, Position[]> = {};
          const instrumentsData: Record<string, Instrument> = {};

          for (const account of accountsData.accounts || []) {
            const positionsResponse = await fetch(
              `${API_URL}/api/accounts/${account.id}/positions`,
              {
                headers: {
                  "Authorization": `Bearer ${token}`,
                },
              }
            );

            if (positionsResponse.ok) {
              const data = await positionsResponse.json();
              positionsData[account.id] = data.positions || [];

              // Extract instruments from positions
              for (const position of data.positions || []) {
                if (position.instrument) {
                  instrumentsData[position.symbol] = position.instrument;
                }
              }
            }
          }

          setPositions(positionsData);
          setInstruments(instrumentsData);

          // Portfolio will be recalculated on render
        }
      } catch (err) {
        console.error("Error refreshing dashboard data:", err);
      }
    };

    // Listen for the completion event
    window.addEventListener('analysis:completed', handleAnalysisCompleted);

    return () => {
      window.removeEventListener('analysis:completed', handleAnalysisCompleted);
    };
  }, [userLoaded, user, getToken, calculatePortfolioSummary]);


  const { totalValue, assetClassBreakdown } = calculatePortfolioSummary();

  // Prepare data for pie chart
  const pieChartData = Object.entries(assetClassBreakdown)
    .filter(([, value]) => value > 0)
    .map(([key, value]) => ({
      name: key.charAt(0).toUpperCase() + key.slice(1).replace('_', ' '),
      value: Math.round(value),
      percentage: totalValue > 0 ? Math.round(value / totalValue * 100) : 0
    }));

  const COLORS = ['#209DD7', '#753991', '#FFB707', '#062147', '#10B981'];

  return (
    <>
      <Head>
        <title>Dashboard - Samy AI Financial Advisor</title>
      </Head>
      <Layout>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <h1 className="text-3xl font-bold text-dark mb-8">Dashboard</h1>

        {loading ? (
          // Loading skeleton
          <div className="space-y-8">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              {Array.from({ length: 4 }).map((_, i) => (
                <div key={i} className="bg-white rounded-lg shadow p-6">
                  <Skeleton className="h-4 w-3/4 mx-auto mb-3" />
                  <Skeleton className="h-8 w-1/2 mx-auto" />
                </div>
              ))}
            </div>
            <SkeletonCard />
            <SkeletonCard />
          </div>
        ) : (
          <>
            {/* Portfolio Summary Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6 text-center">
            <h3 className="text-sm font-medium text-gray-500 mb-3">Total Portfolio Value</h3>
            <p className="text-3xl font-bold text-primary">
              ${totalValue % 1 === 0
                ? totalValue.toLocaleString('en-US')
                : totalValue.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
            </p>
          </div>

          <div className="bg-white rounded-lg shadow p-6 text-center">
            <h3 className="text-sm font-medium text-gray-500 mb-3">Number of Accounts</h3>
            <p className="text-3xl font-bold text-dark">{accounts.length}</p>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-sm font-medium text-gray-500 mb-2 text-center">Asset Allocation</h3>
            {pieChartData.length > 0 ? (
              <div className="h-24">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={pieChartData}
                      cx="50%"
                      cy="50%"
                      innerRadius={20}
                      outerRadius={40}
                      paddingAngle={2}
                      dataKey="value"
                    >
                      {pieChartData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(value: number) => `$${value.toLocaleString()}`} />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            ) : (
              <p className="text-sm text-gray-500">No positions yet</p>
            )}
          </div>

          <div className="bg-white rounded-lg shadow p-6 text-center">
            <h3 className="text-sm font-medium text-gray-500 mb-3">Last Analysis</h3>
            <p className="text-3xl font-bold text-dark">
              {lastAnalysisDate ? new Date(lastAnalysisDate).toLocaleDateString() : "Never"}
            </p>
          </div>
        </div>

        {/* Wellness Score Section */}
        {!wellnessLoading && wellnessData ? (
          <div className="mb-8">
            <WellnessScore
              overallScore={wellnessData.overallScore}
              pillars={wellnessData.pillars}
              lastUpdated={wellnessData.lastUpdated}
              nbaRecommendations={wellnessData.nbaRecommendations}
            />
          </div>
        ) : !wellnessLoading && (
          <div className="bg-white rounded-lg shadow p-6 mb-8">
            <div className="text-center">
              <h2 className="text-2xl font-bold mb-4" style={{ color: '#062147' }}>
                Complete Your Financial Wellness Assessment
              </h2>
              <p className="text-gray-600 mb-6">
                Chat with our Financial Wellness Coach to get personalized insights about your financial health.
                The assessment takes about 3 minutes and will help you understand your financial wellness across four key pillars.
              </p>
              <button
                onClick={() => router.push('/wellness-chat')}
                className="px-8 py-3 bg-primary text-white rounded-lg font-medium hover:bg-blue-600 transition-colors text-lg"
              >
                Start Assessment
              </button>
            </div>
          </div>
        )}
          </>
        )}
      </div>
      </Layout>
    </>
  );
}