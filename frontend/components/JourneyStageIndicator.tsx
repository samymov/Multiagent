/**
 * Journey Stage Indicator Component
 * Shows current stage with visual indicator and navigation
 */

import { useRouter } from "next/router";
import { JourneyStage, STAGES } from "./JourneyProgress";

interface JourneyStageIndicatorProps {
  currentStage: JourneyStage;
  showProgress?: boolean;
}

export default function JourneyStageIndicator({
  currentStage,
  showProgress = true
}: JourneyStageIndicatorProps) {
  const router = useRouter();
  const stage = STAGES.find(s => s.id === currentStage);
  
  if (!stage) return null;

  const currentIndex = STAGES.findIndex(s => s.id === currentStage);
  const progress = ((currentIndex + 1) / STAGES.length) * 100;

  return (
    <div 
      className="w-full py-4 px-6 rounded-lg mb-6"
      style={{ 
        backgroundColor: stage.bgColor,
        borderLeft: `4px solid ${stage.color}`
      }}
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div 
            className="w-12 h-12 rounded-full flex items-center justify-center text-2xl"
            style={{ backgroundColor: stage.color, color: 'white' }}
          >
            {stage.icon}
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 
                className="text-xl font-bold"
                style={{ color: stage.color }}
              >
                {stage.label} Stage
              </h2>
              <span className="text-xs px-2 py-1 rounded-full bg-white text-gray-600">
                Step {currentIndex + 1} of {STAGES.length}
              </span>
            </div>
            <p className="text-sm text-gray-600 mt-1">{stage.description}</p>
          </div>
        </div>
        
        {showProgress && (
          <div className="flex items-center gap-4">
            <div className="w-32">
              <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                <div
                  className="h-full transition-all duration-500"
                  style={{
                    width: `${progress}%`,
                    backgroundColor: stage.color
                  }}
                />
              </div>
            </div>
            <span className="text-sm font-medium text-gray-600">
              {Math.round(progress)}%
            </span>
          </div>
        )}
      </div>
    </div>
  );
}

