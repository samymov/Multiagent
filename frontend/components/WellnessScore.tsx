import React from 'react';
import Head from 'next/head';

interface PillarScore {
  name: string;
  score: number;
  rating: string;
  description: string;
  improvementTip: string;
  color: string;
}

export interface WellnessScoreProps {
  overallScore: number;
  pillars: PillarScore[];
  lastUpdated: string;
}

const getRating = (score: number): string => {
  if (score >= 80) return 'Excellent';
  if (score >= 70) return 'Very Good';
  if (score >= 60) return 'Good';
  if (score >= 50) return 'Fair';
  return 'Needs Improvement';
};

const getRatingColor = (score: number): string => {
  if (score >= 80) return 'text-green-600';
  if (score >= 70) return 'text-blue-600';
  if (score >= 60) return 'text-yellow-600';
  if (score >= 50) return 'text-orange-600';
  return 'text-red-600';
};

const CircularProgress: React.FC<{ score: number; pillars: PillarScore[] }> = ({ score, pillars }) => {
  const radius = 80;
  const circumference = 2 * Math.PI * radius;
  const strokeDasharray = circumference;
  const strokeDashoffset = circumference - (score / 100) * circumference;

  // Calculate angles for each pillar segment
  const totalScore = pillars.reduce((sum, p) => sum + p.score, 0);
  let currentAngle = -90; // Start at top
  const segments = pillars.map((pillar, index) => {
    const segmentAngle = (pillar.score / totalScore) * 360;
    const startAngle = currentAngle;
    currentAngle += segmentAngle;
    return {
      ...pillar,
      startAngle,
      endAngle: currentAngle,
      segmentAngle,
    };
  });

  return (
    <div className="relative w-64 h-64 mx-auto">
      <svg className="transform -rotate-90" width="256" height="256">
        {/* Background circle */}
        <circle
          cx="128"
          cy="128"
          r={radius}
          fill="none"
          stroke="#e5e7eb"
          strokeWidth="20"
        />
        {/* Pillar segments */}
        {segments.map((segment, index) => {
          const startAngleRad = (segment.startAngle * Math.PI) / 180;
          const endAngleRad = (segment.endAngle * Math.PI) / 180;
          const x1 = 128 + radius * Math.cos(startAngleRad);
          const y1 = 128 + radius * Math.sin(startAngleRad);
          const x2 = 128 + radius * Math.cos(endAngleRad);
          const y2 = 128 + radius * Math.sin(endAngleRad);
          const largeArcFlag = segment.segmentAngle > 180 ? 1 : 0;

          return (
            <path
              key={index}
              d={`M 128 128 L ${x1} ${y1} A ${radius} ${radius} 0 ${largeArcFlag} 1 ${x2} ${y2} Z`}
              fill={segment.color}
              opacity="0.3"
            />
          );
        })}
        {/* Overall progress circle */}
        <circle
          cx="128"
          cy="128"
          r={radius}
          fill="none"
          stroke="#209DD7"
          strokeWidth="20"
          strokeDasharray={strokeDasharray}
          strokeDashoffset={strokeDashoffset}
          strokeLinecap="round"
          className="transition-all duration-500"
        />
      </svg>
      {/* Score text in center */}
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <div className="text-5xl font-bold text-dark">{score}</div>
        <div className="text-sm text-gray-500">out of 100</div>
        <div className={`text-sm font-semibold mt-1 ${getRatingColor(score)}`}>
          {getRating(score)}
        </div>
      </div>
    </div>
  );
};

export default function WellnessScore({ overallScore, pillars, lastUpdated }: WellnessScoreProps) {
  return (
    <>
      <Head>
        <title>Financial Wellness Score - Samy AI Financial Advisor</title>
      </Head>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-dark mb-2">Your Financial Wellness Score</h1>
          <p className="text-gray-500">Last updated: {new Date(lastUpdated).toLocaleDateString()}</p>
        </div>

        {/* Overall Score Section */}
        <div className="bg-white rounded-lg shadow-lg p-8 mb-8">
          <div className="text-center mb-6">
            <h2 className="text-2xl font-semibold text-dark mb-4">Overall Financial Wellness</h2>
            <CircularProgress score={overallScore} pillars={pillars} />
          </div>
        </div>

        {/* Pillar Breakdown */}
        <div className="mb-6">
          <h2 className="text-2xl font-semibold text-dark mb-4">Pillar Breakdown</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {pillars.map((pillar, index) => (
              <div
                key={index}
                className="bg-white rounded-lg shadow p-6 border-l-4"
                style={{ borderLeftColor: pillar.color }}
              >
                <div className="flex justify-between items-start mb-4">
                  <h3 className="text-xl font-semibold text-dark">{pillar.name}</h3>
                  <div className="text-right">
                    <div className={`text-3xl font-bold ${getRatingColor(pillar.score)}`}>
                      {pillar.score}
                    </div>
                    <div className={`text-sm font-medium ${getRatingColor(pillar.score)}`}>
                      {pillar.rating}
                    </div>
                  </div>
                </div>
                <p className="text-gray-600 mb-4">{pillar.description}</p>
                <div className="bg-blue-50 border-l-4 border-blue-400 p-3 rounded">
                  <p className="text-sm text-gray-700">
                    <span className="font-semibold">💡 Improvement tip:</span> {pillar.improvementTip}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </>
  );
}

