# Retirement Planning Agent

## Overview

The Retirement Planning Agent provides comprehensive retirement guidance to clients at all stages of their retirement journey. It handles conversational questions about retirement planning while maintaining the ability to perform automated retirement analysis as part of the orchestration flow.

## Architecture

### Components

1. **Intent Classification Module** (`retirement_intent_classifier.py`)
   - Classifies client questions into 10 intent categories:
     - Savings Strategy: "How much should I save?", "Should I use Roth or traditional?"
     - Investment Allocation: "What's the right asset allocation?"
     - Withdrawal Planning: "How much can I withdraw?", "What's the 4% rule?"
     - Tax Optimization: "How can I reduce taxes?", "Should I do a Roth conversion?"
     - Healthcare Costs: "How much will healthcare cost?"
     - Social Security: "When should I claim Social Security?"
     - Estate Planning: "How should I plan my estate?"
     - Lifestyle Adjustments: "How do I adjust my lifestyle in retirement?"
     - Retirement Readiness: "Am I on track for retirement?"
     - Retirement Income: "What will my retirement income be?"

2. **Retirement Calculators** (`retirement_calculators.py`)
   - Portfolio value and asset allocation calculations
   - Monte Carlo simulation for success probability
   - Retirement readiness assessment
   - Social Security benefit calculations
   - Required Minimum Distribution (RMD) calculations
   - Safe withdrawal rate analysis

3. **Advice Rule Engine** (`retirement_advice_engine.py`)
   - Applies retirement planning advice rules based on:
     - Client intent type
     - Calculator outputs
     - User's financial profile and stage of retirement
   - Generates prioritized recommendations with action items

4. **Response Generator** (`retirement_response_generator.py`)
   - Translates technical outputs into clear, actionable client-facing guidance
   - Formats responses with:
     - Personalized greetings
     - Main analysis/answers with specific numbers
     - Prioritized recommendations
     - Next steps

5. **Retirement Planning Agent** (`retirement_planning_agent.py`)
   - Main orchestrator that:
     - Processes client questions
     - Coordinates intent classification, calculations, and advice generation
     - Returns comprehensive responses

## Usage

### Lambda Handler

The retirement planning agent supports two modes:

**1. Orchestration Mode (job-based, existing functionality):**
```json
{
  "job_id": "uuid",
  "portfolio_data": {...}
}
```

**2. Direct Question Mode (conversational):**
```json
{
  "mode": "retirement_planning",
  "clerk_user_id": "user_xxx",
  "question": "Am I on track for retirement?",
  "context": {
    "current_age": 45,
    "years_until_retirement": 20,
    "target_retirement_income": 100000
  }
}
```

### Direct Usage

```python
from retirement_planning_agent import RetirementPlanningAgent

agent = RetirementPlanningAgent(
    portfolio_data=portfolio_data,
    user_data=user_data,
    db=db
)

context = {
    "current_age": 45,
    "years_until_retirement": 20,
    "target_retirement_income": 100000
}

result = agent.process_question("Am I on track for retirement?", context)
print(result["response"])
```

## Intent Categories

### Retirement Readiness
- Questions about being on track for retirement
- Retirement goal assessment
- Success probability analysis

### Savings Strategy
- Contribution limits and maximization
- Roth vs. Traditional decisions
- Catch-up contributions
- Tax-advantaged account optimization

### Social Security
- Claiming age strategies
- Benefit calculations
- Spousal and survivor benefits
- Coordination with other income

### Withdrawal Planning
- Safe withdrawal rates (4% rule)
- Tax-efficient withdrawal sequencing
- Required Minimum Distributions (RMDs)
- Dynamic withdrawal strategies

### Investment Allocation
- Age-appropriate asset allocation
- Diversification strategies
- Rebalancing recommendations

### Tax Optimization
- Roth conversions
- Tax bracket management
- Capital gains strategies

### Healthcare Costs
- Medicare planning
- Long-term care
- Health Savings Accounts (HSAs)

### Estate Planning
- Beneficiary designations
- Trust strategies
- Legacy planning

## Key Features

- **Intent Classification**: Automatically categorizes questions into appropriate intent types
- **Comprehensive Calculations**: Monte Carlo simulations, Social Security analysis, RMD calculations
- **Personalized Recommendations**: Provides advice based on client's specific situation and stage
- **Actionable Steps**: Includes specific numbers, timelines, and action items
- **Dual Mode Support**: Works in both orchestration (automated) and conversational (interactive) modes
- **Error Handling**: Fallback mechanisms for missing data or unrecognized intents
- **Extensible**: Easy to add new intent types and advice rules

## Retirement Planning Topics Covered

### Early Career (20s-30s)
- Starting retirement savings
- Maximizing employer matches
- Roth vs. Traditional decisions
- Setting retirement goals

### Mid Career (40s-50s)
- Catch-up contributions
- Asset allocation adjustments
- Retirement readiness assessment
- Social Security planning

### Pre-Retirement (55-65)
- Retirement timeline planning
- Social Security claiming strategies
- Withdrawal planning
- Healthcare preparation

### Retirement (65+)
- Withdrawal strategies
- RMD planning
- Tax optimization
- Estate planning
- Lifestyle adjustments

## Error Handling

The agent includes fallback mechanisms for:
- Unrecognized intents → Returns general retirement planning advice
- Missing data → Asks targeted clarifying questions
- Technical errors → Returns helpful error messages with next steps

## Extensibility

To add new intent types:
1. Add keywords to `RetirementIntentClassifier`
2. Create calculator method in `RetirementCalculator`
3. Add advice rules in `RetirementAdviceEngine`
4. Update response formatting in `RetirementResponseGenerator`

## Backward Compatibility

The original orchestration mode functionality is preserved:
- `agent.py` - Original retirement analysis functions (Monte Carlo, projections)
- `lambda_handler.py` - Supports both orchestration and conversational modes
- Existing job-based analysis continues to work as before

