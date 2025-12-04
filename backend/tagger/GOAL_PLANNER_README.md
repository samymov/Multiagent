# Goal Planner Agent - Refactored from Tagger Agent

## Overview

The Goal Planner Agent has been refactored from the InstrumentTagger Agent to serve as an intelligent interface for financial planning queries. It interprets client financial intents, leverages existing estimators and advice rules, and provides actionable guidance.

## Architecture

### Components

1. **Intent Classification Module** (`intent_classifier.py`)
   - Classifies client questions into intent categories:
     - Retirement Tracking: "Am I on track for retirement?", "Am I contributing enough to my 401k?"
     - Savings Optimization: "How can I save more for retirement?", "How much should I put in my HSA?"
     - Goal Management: "Help me set a financial goal", "Which goal should I focus on first?"

2. **Estimator Integration Layer** (`estimators.py`)
   - Connects intents to existing estimators from the retirement agent:
     - `calculate_portfolio_value()` - Current portfolio value
     - `calculate_asset_allocation()` - Asset allocation percentages
     - `estimate_retirement_readiness()` - Retirement readiness analysis
     - `estimate_401k_contribution_adequacy()` - 401k contribution analysis
     - `estimate_hsa_contribution()` - HSA contribution recommendations
     - `estimate_savings_optimization()` - Savings optimization strategies

3. **Advice Rule Engine** (`advice_rules.py`)
   - Applies financial advice rules based on:
     - Client intent type
     - Estimator outputs
     - User's financial profile
   - Generates prioritized recommendations with action items

4. **Response Generator** (`response_generator.py`)
   - Translates technical outputs into clear, actionable client-facing guidance
   - Formats responses with:
     - Personalized greetings
     - Main analysis/answers
     - Specific recommendations
     - Next steps

5. **Goal Planner Agent** (`goal_planner_agent.py`)
   - Main orchestrator that:
     - Processes client questions
     - Coordinates intent classification, estimation, and advice generation
     - Returns comprehensive responses

## Usage

### Lambda Handler

The goal planner can be invoked via Lambda with:

```json
{
  "mode": "goal_planning",
  "clerk_user_id": "user_xxx",
  "question": "Am I on track for retirement?"
}
```

### Direct Usage

```python
from goal_planner_agent import GoalPlannerAgent

agent = GoalPlannerAgent(
    portfolio_data=portfolio_data,
    user_data=user_data,
    db=db
)

result = agent.process_question("Am I on track for retirement?")
print(result["response"])
```

## Intent Categories

### Retirement Tracking
- Questions about retirement readiness
- 401k contribution adequacy
- Retirement planning status

### Savings Optimization
- How to save more for retirement
- HSA contribution recommendations
- Savings rate optimization

### Goal Management
- Setting financial goals
- Prioritizing multiple goals
- Accelerating goal achievement

## Error Handling

The agent includes fallback mechanisms for:
- Unrecognized intents → Returns general financial advice
- Missing data → Provides guidance on what data is needed
- Technical errors → Returns helpful error messages with next steps

## Extensibility

To add new intent types:
1. Add keywords to `IntentClassifier`
2. Create estimator method in `EstimatorIntegration`
3. Add advice rules in `AdviceRuleEngine`
4. Update response formatting in `ResponseGenerator`

## Backward Compatibility

The original instrument tagging functionality is preserved in:
- `agent.py` - Original tagger agent
- `lambda_handler.py` - Original tagger lambda handler

Both systems can coexist, with the goal planner being the new primary interface for client questions.

