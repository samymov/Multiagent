import React from 'react';
import { useRouter } from 'next/router';

interface PillarScore {
  name: string;
  score: number;
  rating: string;
  description: string;
  improvementTip: string;
  color: string;
  bgColor?: string;
}

interface NBARecommendation {
  nba_code: string;
  agent_route: string;
  agent_name: string;
  icon: string;
  description: string;
}

export interface WellnessScoreProps {
  overallScore: number;
  pillars: PillarScore[];
  lastUpdated: string;
  nbaRecommendations?: NBARecommendation[];
}

const getOverallRating = (score: number): string => {
  // Match Streamlit rating logic: Excellent (80+), Good (60-79), Fair (40-59), Poor (<40)
  if (score >= 80) return 'Excellent';
  if (score >= 60) return 'Good';
  if (score >= 40) return 'Fair';
  return 'Poor';
};

const getOverallRatingColor = (score: number): string => {
  if (score >= 80) return '#2E7D32';  // Green
  if (score >= 60) return '#1976D2';  // Blue
  if (score >= 40) return '#F9A825';  // Yellow
  return '#D32F2F';  // Red
};

// Gauge chart component using SVG
const GaugeChart: React.FC<{ score: number }> = ({ score }) => {
  const radius = 80;
  const circumference = 2 * Math.PI * radius;
  const strokeDasharray = circumference;
  const strokeDashoffset = circumference - (score / 100) * circumference;
  const color = getOverallRatingColor(score);
  const rating = getOverallRating(score);

  return (
    <div className="relative w-64 h-64 mx-auto">
      <svg className="transform -rotate-90" width="256" height="256">
        {/* Background circle */}
        <circle
          cx="128"
          cy="128"
          r={radius}
          fill="none"
          stroke="#E5E7EB"
          strokeWidth="18"
        />
        {/* Progress circle */}
        <circle
          cx="128"
          cy="128"
          r={radius}
          fill="none"
          stroke={color}
          strokeWidth="18"
          strokeDasharray={strokeDasharray}
          strokeDashoffset={strokeDashoffset}
          strokeLinecap="round"
          className="transition-all duration-1000"
        />
      </svg>
      {/* Score text in center */}
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <div className="text-4xl font-bold" style={{ color }}>{score}</div>
        <div className="text-sm text-gray-500">/ 100</div>
        <div className="text-xl font-semibold mt-2" style={{ color: color }}>
          {rating}
        </div>
      </div>
    </div>
  );
};

export default function WellnessScore({ overallScore, pillars, lastUpdated, nbaRecommendations = [] }: WellnessScoreProps) {
  const router = useRouter();
  
  const formatDate = (dateString: string) => {
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString('en-US', { 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric' 
      });
    } catch {
      return dateString;
    }
  };

  const handleAgentClick = (route: string) => {
    router.push(route);
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold mb-2" style={{ color: '#062147' }}>
            Your Financial Wellness Score
          </h1>
          <p className="text-gray-600">
            Track your progress across the four pillars of financial wellness and see how you&apos;re doing overall.
          </p>
        </div>

        {/* Main Score Section - Two Columns */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-8">
          {/* Left Column - Gauge Chart */}
          <div className="md:col-span-1 flex flex-col items-center">
            <GaugeChart score={overallScore} />
            <p className="text-center text-gray-500 mt-4">
              Last updated: {formatDate(lastUpdated)}
            </p>
          </div>

          {/* Right Column - Pillar Breakdown */}
          <div className="md:col-span-2">
            <h2 className="text-xl font-semibold mb-4" style={{ color: '#062147' }}>
              Pillar Breakdown
            </h2>
            <div className="space-y-4">
              {pillars.map((pillar, index) => (
                <div key={index}>
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex-1 font-medium" style={{ color: '#062147' }}>
                      {pillar.name}
                    </div>
                    <div className="w-20 text-right font-bold" style={{ color: '#062147' }}>
                      {pillar.score}/100
                    </div>
                    <div 
                      className="w-24 text-right font-bold"
                      style={{ color: pillar.color }}
                    >
                      {pillar.rating}
                    </div>
                  </div>
                  {/* Progress bar */}
                  <div className="w-full h-2 bg-gray-200 rounded-full overflow-hidden">
                    <div
                      className="h-2 rounded-full transition-all duration-1000"
                      style={{
                        width: `${pillar.score}%`,
                        backgroundColor: pillar.color
                      }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        <hr className="my-8" />

        {/* Pillar Cards - 4 Columns */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {pillars.map((pillar, index) => (
            <div
              key={index}
              className="rounded-2xl p-4 shadow-sm"
              style={{
                backgroundColor: pillar.bgColor || '#F5F5F5',
                minHeight: '220px'
              }}
            >
              {/* Score and Rating */}
              <div className="mb-3">
                <span className="text-3xl font-bold" style={{ color: pillar.color }}>
                  {pillar.score}
                </span>
                <span className="text-lg ml-2" style={{ color: pillar.color }}>
                  {pillar.rating}
                </span>
              </div>

              {/* Pillar Name */}
              <h3 className="text-base font-bold mb-2" style={{ color: '#062147' }}>
                {pillar.name}
              </h3>

              {/* Description */}
              <p className="text-sm mb-3 text-gray-700">
                {pillar.description}
              </p>

              {/* Improvement Tip */}
              <div className="text-xs" style={{ color: '#2E7D32' }}>
                <span className="font-bold">Improvement tip:</span> {pillar.improvementTip}
              </div>
            </div>
          ))}
        </div>

        {/* Next Best Actions Section */}
        {nbaRecommendations && nbaRecommendations.length > 0 && (
          <>
            <hr className="my-8" />
            <div className="mt-8">
              <h2 className="text-2xl font-bold mb-4" style={{ color: '#062147' }}>
                📌 Recommended Next Best Actions
              </h2>
              <p className="text-gray-600 mb-6">
                Based on your assessment, we recommend working with these specialized agents to improve your financial wellness:
              </p>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                {nbaRecommendations.map((nba, index) => (
                  <div
                    key={index}
                    className="card cursor-pointer hover:shadow-lg transition-shadow"
                    onClick={() => handleAgentClick(nba.agent_route)}
                    style={{
                      border: '2px solid transparent',
                      borderColor: '#E5E7EB'
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.borderColor = '#BA0C2F';
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.borderColor = '#E5E7EB';
                    }}
                  >
                    <div className="text-4xl mb-3">{nba.icon}</div>
                    <h3 className="text-lg font-semibold mb-2" style={{ color: '#BA0C2F' }}>
                      {nba.agent_name}
                    </h3>
                    <p className="text-sm text-gray-600 mb-4">
                      {nba.description}
                    </p>
                    <button
                      className="btn btn-primary btn-sm w-full"
                      style={{
                        backgroundColor: '#BA0C2F',
                        color: 'white',
                        border: 'none',
                        padding: '0.5rem 1rem',
                        borderRadius: '4px',
                        cursor: 'pointer',
                        fontSize: '0.875rem',
                        fontWeight: 500
                      }}
                      onClick={(e) => {
                        e.stopPropagation();
                        handleAgentClick(nba.agent_route);
                      }}
                    >
                      Get Started →
                    </button>
                  </div>
                ))}
              </div>
            </div>
          </>
        )}
    </div>
  );
}
