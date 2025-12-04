/**
 * Journey Progress Component
 * Visualizes the four-stage client journey: Assess, Explore, Act, Track
 */

import { useRouter } from "next/router";
import { useEffect, useState } from "react";

export type JourneyStage = "assess" | "explore" | "act" | "track";

interface JourneyStageConfig {
  id: JourneyStage;
  label: string;
  icon: string;
  description: string;
  color: string;
  bgColor: string;
  route: string;
}

const STAGES: JourneyStageConfig[] = [
  {
    id: "assess",
    label: "Assess",
    icon: "📊",
    description: "Understand your current financial state",
    color: "#BA0C2F", // Vanguard Red
    bgColor: "#FFF5F7",
    route: "/wellness-chat"
  },
  {
    id: "explore",
    label: "Explore",
    icon: "🔍",
    description: "Discover options and solutions",
    color: "#753991", // Purple
    bgColor: "#F5F0F8",
    route: "/advisor-team"
  },
  {
    id: "act",
    label: "Act",
    icon: "⚡",
    description: "Take concrete steps and decisions",
    color: "#10B981", // Green
    bgColor: "#F0FDF4",
    route: "/analysis"
  },
  {
    id: "track",
    label: "Track",
    icon: "📈",
    description: "Monitor progress and outcomes",
    color: "#209DD7", // Blue
    bgColor: "#F0F9FF",
    route: "/dashboard"
  }
];

interface JourneyProgressProps {
  currentStage?: JourneyStage;
  completedStages?: JourneyStage[];
  showLabels?: boolean;
  compact?: boolean;
}

export default function JourneyProgress({
  currentStage,
  completedStages = [],
  showLabels = true,
  compact = false
}: JourneyProgressProps) {
  const router = useRouter();
  const [userStage, setUserStage] = useState<JourneyStage | null>(currentStage || null);

  // Determine current stage from route
  useEffect(() => {
    const path = router.pathname;
    
    // Map routes to stages
    if (path.includes("wellness-chat") || path.includes("wellness-questionnaire")) {
      setUserStage("assess");
    } else if (path.includes("advisor-team") || path.includes("analysis")) {
      setUserStage("explore");
    } else if (path.includes("agents/") || path.includes("accounts")) {
      setUserStage("act");
    } else if (path === "/dashboard" || path === "/accounts") {
      setUserStage("track");
    } else {
      // Default to assess if on dashboard without assessment
      if (path === "/dashboard") {
        setUserStage("assess");
      }
    }
  }, [router.pathname]);

  const currentStageIndex = userStage ? STAGES.findIndex(s => s.id === userStage) : -1;
  const effectiveCompletedStages = completedStages.length > 0 
    ? completedStages 
    : (currentStageIndex >= 0 ? STAGES.slice(0, currentStageIndex).map(s => s.id) : []);

  const handleStageClick = (stage: JourneyStageConfig) => {
    router.push(stage.route);
  };

  if (compact) {
    return (
      <div className="flex items-center justify-between bg-white rounded-lg shadow-sm p-4">
        {STAGES.map((stage, index) => {
          const isCompleted = effectiveCompletedStages.includes(stage.id);
          const isCurrent = userStage === stage.id;
          const isAccessible = isCompleted || isCurrent || index === 0;

          return (
            <div
              key={stage.id}
              className={`flex items-center ${index < STAGES.length - 1 ? 'flex-1' : ''}`}
            >
              <button
                onClick={() => isAccessible && handleStageClick(stage)}
                disabled={!isAccessible}
                className={`
                  flex items-center gap-2 px-3 py-2 rounded-lg transition-all
                  ${isCurrent 
                    ? 'font-semibold' 
                    : isCompleted
                    ? 'bg-gray-50 text-gray-700 hover:bg-gray-100'
                    : 'bg-gray-50 text-gray-400 cursor-not-allowed'
                  }
                  ${isAccessible && !isCurrent ? 'hover:bg-gray-100' : ''}
                `}
                style={{
                  backgroundColor: isCurrent ? stage.bgColor : undefined,
                  color: isCurrent ? stage.color : undefined,
                }}
              >
                <span className="text-lg">{stage.icon}</span>
                {showLabels && (
                  <span className="text-sm font-medium">{stage.label}</span>
                )}
              </button>
              {index < STAGES.length - 1 && (
                <div className={`
                  flex-1 h-0.5 mx-2 transition-all
                  ${isCompleted ? 'bg-green-500' : 'bg-gray-200'}
                `} />
              )}
            </div>
          );
        })}
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-sm p-6">
      <h3 className="text-lg font-semibold mb-4" style={{ color: '#062147' }}>
        Your Financial Journey
      </h3>
      <div className="space-y-4">
        {STAGES.map((stage, index) => {
          const isCompleted = effectiveCompletedStages.includes(stage.id);
          const isCurrent = userStage === stage.id;
          const isAccessible = isCompleted || isCurrent || index === 0;

          return (
            <div key={stage.id} className="relative">
              <button
                onClick={() => isAccessible && handleStageClick(stage)}
                disabled={!isAccessible}
                className={`
                  w-full flex items-center gap-4 p-4 rounded-lg border-2 transition-all
                  ${isCurrent 
                    ? '' 
                    : isCompleted
                    ? 'border-green-200 bg-green-50'
                    : 'border-gray-200 bg-gray-50 opacity-60'
                  }
                  ${isAccessible && !isCurrent ? 'hover:border-gray-300 hover:bg-gray-100' : ''}
                  ${!isAccessible ? 'cursor-not-allowed' : 'cursor-pointer'}
                `}
                style={{
                  borderColor: isCurrent ? stage.color : undefined,
                  backgroundColor: isCurrent ? stage.bgColor : undefined,
                }}
              >
                <div className={`
                  w-12 h-12 rounded-full flex items-center justify-center text-2xl
                  ${isCurrent ? 'bg-white' : isCompleted ? 'bg-green-500' : 'bg-gray-300'}
                `}>
                  {isCompleted && !isCurrent ? '✓' : stage.icon}
                </div>
                <div className="flex-1 text-left">
                  <div className="flex items-center gap-2">
                    <h4 
                      className="font-semibold"
                      style={{ 
                        color: isCurrent ? stage.color : isCompleted ? '#15803d' : '#6b7280'
                      }}
                    >
                      {stage.label}
                    </h4>
                    {isCurrent && (
                      <span className="text-xs px-2 py-1 rounded-full bg-white text-gray-600">
                        Current
                      </span>
                    )}
                    {isCompleted && !isCurrent && (
                      <span className="text-xs px-2 py-1 rounded-full bg-green-100 text-green-700">
                        Completed
                      </span>
                    )}
                  </div>
                  <p className="text-sm text-gray-600 mt-1">{stage.description}</p>
                </div>
                {isAccessible && (
                  <svg
                    className="w-5 h-5 text-gray-400"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M9 5l7 7-7 7"
                    />
                  </svg>
                )}
              </button>
              {index < STAGES.length - 1 && (
                <div className={`
                  absolute left-6 top-full w-0.5 h-4 transition-all
                  ${isCompleted ? 'bg-green-500' : 'bg-gray-200'}
                `} style={{ marginTop: '4px' }} />
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

export { STAGES, type JourneyStageConfig };

