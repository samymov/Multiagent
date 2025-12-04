/**
 * Journey State Management
 * Tracks user progress through the four-stage journey
 */

import { JourneyStage } from "../components/JourneyProgress";

export interface JourneyState {
  currentStage: JourneyStage;
  completedStages: JourneyStage[];
  lastUpdated: string;
}

const JOURNEY_STORAGE_KEY = "financial_journey_state";

/**
 * Get journey state from localStorage
 */
export function getJourneyState(): JourneyState | null {
  if (typeof window === "undefined") return null;
  
  try {
    const stored = localStorage.getItem(JOURNEY_STORAGE_KEY);
    if (stored) {
      return JSON.parse(stored);
    }
  } catch (e) {
    console.error("Error reading journey state:", e);
  }
  
  return null;
}

/**
 * Save journey state to localStorage
 */
export function saveJourneyState(state: JourneyState): void {
  if (typeof window === "undefined") return;
  
  try {
    localStorage.setItem(JOURNEY_STORAGE_KEY, JSON.stringify({
      ...state,
      lastUpdated: new Date().toISOString()
    }));
  } catch (e) {
    console.error("Error saving journey state:", e);
  }
}

/**
 * Mark a stage as completed
 */
export function completeStage(stage: JourneyStage): void {
  const current = getJourneyState();
  const completedStages = current?.completedStages || [];
  
  if (!completedStages.includes(stage)) {
    completedStages.push(stage);
    saveJourneyState({
      currentStage: stage,
      completedStages,
      lastUpdated: new Date().toISOString()
    });
  }
}

/**
 * Set current stage
 */
export function setCurrentStage(stage: JourneyStage): void {
  const current = getJourneyState();
  saveJourneyState({
    currentStage: stage,
    completedStages: current?.completedStages || [],
    lastUpdated: new Date().toISOString()
  });
}

/**
 * Initialize journey state (typically called after assessment)
 */
export function initializeJourney(): JourneyState {
  const state: JourneyState = {
    currentStage: "assess",
    completedStages: [],
    lastUpdated: new Date().toISOString()
  };
  saveJourneyState(state);
  return state;
}

/**
 * Get next stage in the journey
 */
export function getNextStage(currentStage: JourneyStage): JourneyStage | null {
  const stages: JourneyStage[] = ["assess", "explore", "act", "track"];
  const currentIndex = stages.indexOf(currentStage);
  
  if (currentIndex < stages.length - 1) {
    return stages[currentIndex + 1];
  }
  
  return null;
}

/**
 * Check if a stage is accessible (previous stages completed)
 */
export function isStageAccessible(stage: JourneyStage): boolean {
  const stages: JourneyStage[] = ["assess", "explore", "act", "track"];
  const stageIndex = stages.indexOf(stage);
  const state = getJourneyState();
  
  // First stage is always accessible
  if (stageIndex === 0) return true;
  
  // Check if previous stage is completed
  if (state) {
    const previousStage = stages[stageIndex - 1];
    return state.completedStages.includes(previousStage);
  }
  
  return false;
}

