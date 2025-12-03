import { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import { useUser, useAuth } from '@clerk/nextjs';
import Layout from '../components/Layout';
import WellnessScore from '../components/WellnessScore';
import { API_URL } from '../lib/config';
import { SkeletonCard } from '../components/Skeleton';
import { showToast } from '../components/Toast';

interface PillarScore {
  name: string;
  score: number;
  rating: string;
  description: string;
  improvementTip: string;
  color: string;
  bgColor?: string;
}

interface WellnessScoreData {
  overallScore: number;
  pillars: PillarScore[];
  lastUpdated: string;
}

export default function WellnessScorePage() {
  const { user, isLoaded: userLoaded } = useUser();
  const { getToken } = useAuth();
  const router = useRouter();
  const [wellnessData, setWellnessData] = useState<WellnessScoreData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadWellnessScore() {
      if (!userLoaded || !user) {
        if (userLoaded && !user) {
          router.push('/');
        }
        return;
      }

      try {
        const token = await getToken();
        if (!token) {
          setError('Not authenticated');
          setLoading(false);
          return;
        }

        const response = await fetch(`${API_URL}/api/wellness/score`, {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        });

        if (response.status === 404) {
          // No wellness score yet, redirect to questionnaire
          router.push('/wellness-questionnaire');
          return;
        }

        if (!response.ok) {
          const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
          throw new Error(errorData.detail || `Failed to load wellness score (${response.status})`);
        }

        const data = await response.json();
        setWellnessData({
          overallScore: data.overallScore,
          pillars: data.pillars,
          lastUpdated: data.lastUpdated,
        });
      } catch (err) {
        console.error('Error loading wellness score:', err);
        setError(err instanceof Error ? err.message : 'Failed to load wellness score');
        showToast('error', 'Failed to load wellness score');
      } finally {
        setLoading(false);
      }
    }

    loadWellnessScore();
  }, [userLoaded, user, getToken, router]);

  if (!userLoaded || loading) {
    return (
      <Layout>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <SkeletonCard />
        </div>
      </Layout>
    );
  }

  if (error || !wellnessData) {
    return (
      <Layout>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="bg-red-50 border border-red-200 rounded-lg p-6">
            <p className="text-red-600">{error || 'No wellness score data available'}</p>
            <button
              onClick={() => router.push('/wellness-questionnaire')}
              className="mt-4 px-6 py-2 bg-primary text-white rounded-lg hover:bg-blue-600"
            >
              Complete Questionnaire
            </button>
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <WellnessScore
        overallScore={wellnessData.overallScore}
        pillars={wellnessData.pillars}
        lastUpdated={wellnessData.lastUpdated}
      />
    </Layout>
  );
}

