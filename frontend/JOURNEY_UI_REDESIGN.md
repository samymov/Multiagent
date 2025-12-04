# Four-Stage Journey UI Redesign

## Overview

The platform has been redesigned to explicitly support and visualize a four-stage client journey: **Assess**, **Explore**, **Act**, and **Track**. This redesign provides clear navigation, progress visualization, and stage-specific guidance to help users understand where they are in their financial journey and what actions they need to take.

## Journey Stages

### 1. Assess 📊
**Purpose**: Initial evaluation and diagnostic phase where clients understand their current financial state.

**Routes**: 
- `/wellness-chat` - Conversational financial wellness assessment
- `/wellness-questionnaire` - Traditional questionnaire format

**Key Features**:
- Stage indicator showing "Assess Stage" with red (Vanguard) color scheme
- Progress bar for questionnaire completion
- Automatic progression to Explore stage upon completion

**Completion Trigger**: When wellness assessment is successfully submitted

### 2. Explore 🔍
**Purpose**: Discovery phase where clients investigate options, solutions, and possibilities.

**Routes**:
- `/advisor-team` - Browse available AI agents and advisors
- `/analysis` - View analysis results and recommendations

**Key Features**:
- Stage indicator with purple color scheme
- Agent cards showing available advisors
- Analysis results with recommendations
- Automatic progression to Act stage when analysis is initiated

**Completion Trigger**: When user starts an analysis from advisor team

### 3. Act ⚡
**Purpose**: Implementation phase where clients take concrete steps or make decisions.

**Routes**:
- `/analysis` - View and act on analysis recommendations
- `/agents/*` - Interact with specific agents (goal-solver, retirement-planning, etc.)
- `/accounts` - Manage financial accounts

**Key Features**:
- Stage indicator with green color scheme
- Action buttons to implement recommendations
- Agent interaction interfaces
- Account management tools

**Completion Trigger**: When user completes actions based on recommendations

### 4. Track 📈
**Purpose**: Monitoring phase where clients measure progress and outcomes.

**Routes**:
- `/dashboard` - Main dashboard with portfolio overview
- `/accounts` - Account tracking and management

**Key Features**:
- Stage indicator with blue color scheme
- Portfolio summary cards
- Wellness score display
- Progress tracking over time

## UI Components

### JourneyProgress Component
**Location**: `frontend/components/JourneyProgress.tsx`

**Features**:
- Visual representation of all four stages
- Progress indicators showing completed stages
- Clickable navigation between accessible stages
- Compact and full display modes
- Color-coded stages with icons

**Props**:
- `currentStage`: Current stage in the journey
- `completedStages`: Array of completed stages
- `showLabels`: Whether to show stage labels
- `compact`: Compact horizontal layout vs full vertical layout

### JourneyStageIndicator Component
**Location**: `frontend/components/JourneyStageIndicator.tsx`

**Features**:
- Large, prominent indicator for current stage
- Progress percentage display
- Stage-specific color scheme
- Step counter (e.g., "Step 1 of 4")
- Description of current stage purpose

**Props**:
- `currentStage`: Current stage to display
- `showProgress`: Whether to show progress bar

### Journey State Management
**Location**: `frontend/lib/journey.ts`

**Functions**:
- `getJourneyState()`: Retrieve current journey state from localStorage
- `saveJourneyState()`: Save journey state to localStorage
- `completeStage()`: Mark a stage as completed
- `setCurrentStage()`: Set the current active stage
- `initializeJourney()`: Initialize journey state (typically after assessment)
- `getNextStage()`: Get the next stage in sequence
- `isStageAccessible()`: Check if a stage can be accessed

## Navigation Structure

### Header Navigation
The main navigation header includes:
- **Journey Progress Bar** (compact mode) - Shows all four stages with current position
- **Traditional Navigation Links** - Dashboard, Advisor Team, Analysis
- **User Profile** - Clerk user button

### Page-Level Navigation
Each page displays:
- **Journey Stage Indicator** - Large banner showing current stage
- **Journey Progress Overview** (on dashboard) - Full journey visualization
- **Stage-specific content** - Content relevant to current stage

## Visual Design

### Color Scheme
Each stage has a distinct color identity:

- **Assess**: Red (#BA0C2F) - Vanguard brand color
- **Explore**: Purple (#753991) - AI/agent accent color
- **Act**: Green (#10B981) - Success/action color
- **Track**: Blue (#209DD7) - Primary blue

### Typography
- Stage labels use bold, semibold font weights
- Descriptions use regular weight with secondary text color
- Progress percentages use medium weight

### Icons
Each stage has a distinctive emoji icon:
- 📊 Assess
- 🔍 Explore
- ⚡ Act
- 📈 Track

## User Flow

### Initial User Journey
1. **User lands on Dashboard** → Sees "Assess" stage indicator
2. **Clicks "Start Assessment"** → Navigates to `/wellness-chat`
3. **Completes assessment** → Stage marked as complete, moves to Explore
4. **Views Advisor Team** → Sees available agents, can start analysis
5. **Starts analysis** → Moves to Act stage
6. **Views analysis results** → Can take actions based on recommendations
7. **Returns to Dashboard** → Sees Track stage with progress overview

### Stage Progression Logic
- Stages are unlocked sequentially
- Users can revisit completed stages
- Current stage is always accessible
- Future stages are locked until previous stages are completed

## Responsive Design

### Desktop (lg breakpoint and above)
- Journey progress bar in header (compact mode)
- Full journey progress widget on dashboard
- Side-by-side layouts for stage indicators

### Tablet (md breakpoint)
- Compact journey progress in header
- Stacked layouts for stage content
- Full journey progress on dashboard

### Mobile (sm breakpoint and below)
- Compact journey progress in mobile navigation
- Full-width stage indicators
- Stacked journey progress cards

## Integration Points

### Assessment Completion
When wellness assessment is completed:
```typescript
completeStage("assess");
const nextStage = getNextStage("assess");
if (nextStage) {
  setCurrentStage(nextStage);
}
```

### Analysis Initiation
When analysis is started from advisor team:
```typescript
completeStage("explore");
setCurrentStage("act");
```

### Action Completion
When user completes actions:
```typescript
completeStage("act");
setCurrentStage("track");
```

## Accessibility

### Keyboard Navigation
- All stage buttons are keyboard accessible
- Tab order follows visual flow
- Enter/Space activates stage navigation

### Screen Readers
- Stage labels include descriptive text
- Progress indicators announce completion status
- Current stage is clearly announced

### Visual Indicators
- Color is not the only indicator (icons and text labels)
- High contrast ratios for text
- Clear focus states for interactive elements

## Future Enhancements

### Potential Additions
1. **Journey Analytics**: Track time spent in each stage
2. **Stage-specific Onboarding**: Contextual help for each stage
3. **Milestone Celebrations**: Celebrate stage completions
4. **Journey Recommendations**: Suggest next actions based on progress
5. **Multi-journey Support**: Support for different journey types
6. **Journey Templates**: Pre-defined journey paths for different goals

## Technical Implementation

### State Persistence
Journey state is persisted in `localStorage` with key `financial_journey_state`:
```typescript
{
  currentStage: "assess" | "explore" | "act" | "track",
  completedStages: JourneyStage[],
  lastUpdated: string
}
```

### Route Mapping
Routes are automatically mapped to stages:
- `/wellness-chat`, `/wellness-questionnaire` → `assess`
- `/advisor-team`, `/analysis` → `explore`
- `/agents/*`, `/accounts` → `act`
- `/dashboard` → `track`

### Component Reusability
All journey components are designed to be reusable across different pages and contexts, with props for customization.

## Testing Considerations

### Unit Tests
- Journey state management functions
- Stage accessibility logic
- Progress calculation

### Integration Tests
- Stage progression flow
- Navigation between stages
- State persistence

### E2E Tests
- Complete user journey from Assess to Track
- Stage completion triggers
- Navigation accessibility

## Summary

The four-stage journey UI redesign provides:
- ✅ Clear stage identification
- ✅ Visual progress tracking
- ✅ Intuitive navigation
- ✅ Stage-specific guidance
- ✅ Responsive design
- ✅ Accessibility support
- ✅ State persistence
- ✅ Smooth transitions

This redesign significantly improves user understanding of their financial journey and provides clear guidance on what actions to take at each stage.

