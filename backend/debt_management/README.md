# Debt Management Agent

## Overview

The Debt Management Agent provides personalized debt management and budgeting advice to clients. It helps clients eliminate debt, create budgets, manage student loans, and reduce spending through actionable, data-driven recommendations.

## Architecture

### Components

1. **Intent Classification Module** (`debt_intent_classifier.py`)
   - Classifies client questions into intent categories:
     - Debt Payoff Strategy: "Which debt should I pay off first?", "Avalanche vs. Snowball"
     - Student Loan Management: "Should I refinance?", "Am I eligible for PSLF?"
     - Budget Creation: "Help me create a budget", "What's the 50/30/20 rule?"
     - Spending Reduction: "How can I reduce my spending?"
     - Debt Consolidation: "Should I consolidate my debts?"

2. **Debt Calculators** (`debt_calculators.py`)
   - Calculates debt payoff strategies:
     - Debt Avalanche (highest interest first)
     - Debt Snowball (smallest balance first)
     - Strategy comparison with interest savings
   - Student loan calculations:
     - Standard amortization payments
     - Income-Driven Repayment (IDR) calculations
   - Budget calculations:
     - 50/30/20 budget allocation
     - Zero-based budgeting

3. **Advice Rule Engine** (`debt_advice_engine.py`)
   - Applies financial advice rules based on:
     - Client intent type
     - Calculator outputs
     - User's financial profile
   - Generates prioritized recommendations with action items

4. **Response Generator** (`debt_response_generator.py`)
   - Translates technical outputs into clear, actionable client-facing guidance
   - Formats responses with:
     - Personalized greetings
     - Main analysis/answers with specific numbers
     - Prioritized recommendations
     - Next steps

5. **Debt Management Agent** (`agent.py`)
   - Main orchestrator that:
     - Processes client questions
     - Coordinates intent classification, calculations, and advice generation
     - Returns comprehensive responses

## Usage

### Lambda Handler

The debt management agent can be invoked via Lambda with:

```json
{
  "mode": "debt_management",
  "clerk_user_id": "user_xxx",
  "question": "Which debt should I pay off first?",
  "context": {
    "debts": [
      {
        "name": "Credit Card",
        "balance": 5000,
        "interest_rate": 18.5,
        "minimum_payment": 150
      },
      {
        "name": "Car Loan",
        "balance": 15000,
        "interest_rate": 5.5,
        "minimum_payment": 300
      }
    ],
    "monthly_payment": 500,
    "income": 5000,
    "expenses": {
      "needs": 2500,
      "wants": 1500,
      "savings_debt": 1000
    }
  }
}
```

### Direct Usage

```python
from debt_management.agent import DebtManagementAgent

agent = DebtManagementAgent(
    user_data=user_data,
    db=db
)

context = {
    "debts": [
        {"name": "Credit Card", "balance": 5000, "interest_rate": 18.5, "minimum_payment": 150}
    ],
    "monthly_payment": 500
}

result = agent.process_question("Which debt should I pay off first?", context)
print(result["response"])
```

## Intent Categories

### Debt Payoff Strategy
- Questions about which debt to pay off first
- Avalanche vs. Snowball method comparison
- Debt prioritization strategies

### Student Loan Management
- Income-Driven Repayment (IDR) plan recommendations
- Public Service Loan Forgiveness (PSLF) eligibility
- Employer student loan assistance programs
- Refinancing considerations

### Budget Creation
- 50/30/20 budget framework
- Zero-based budgeting
- Envelope system
- Pay yourself first principle

### Spending Reduction
- Fixed expense negotiation strategies
- Variable expense tracking and reduction
- Lifestyle adjustments
- Needs vs. wants analysis

### Debt Consolidation
- Personal loan options
- Balance transfer cards
- Consolidation cost analysis

## Key Features

- **Intent Classification**: Automatically categorizes questions into appropriate intent types
- **Strategy Comparison**: Calculates and compares Avalanche vs. Snowball methods with interest savings
- **Personalized Recommendations**: Provides advice based on client's specific financial situation
- **Actionable Steps**: Includes specific numbers, timelines, and action items
- **Error Handling**: Fallback mechanisms for missing data or unrecognized intents
- **Extensible**: Easy to add new intent types and advice rules

## Debt Payoff Methods

### Debt Avalanche
- Prioritizes debts with highest interest rates first
- Saves the most money in interest
- Best for: Clients focused on mathematical optimization

### Debt Snowball
- Prioritizes smallest debts first for psychological wins
- Builds momentum and motivation
- Best for: Clients who need quick wins to stay motivated

### Strategy Selection
The agent automatically compares both methods and recommends based on:
- Interest rate spread (if >3%, favor Avalanche)
- Client's stated psychological preferences
- Calculated interest savings

## Student Loan Strategies

### Income-Driven Repayment (IDR) Plans
- **SAVE Plan**: Most generous for low-income borrowers (10% of discretionary income)
- **PAYE Plan**: 10% of discretionary income, capped at standard payment
- **IBR Plan**: 10-15% of discretionary income depending on loan origination date

### Public Service Loan Forgiveness (PSLF)
- Forgiveness after 120 qualifying payments (10 years)
- Must work for qualifying employer (government, nonprofit, education)
- Requires annual employment certification

### Employer Student Loan Assistance
- Up to $5,250 annually tax-free through 2025
- Check with HR department for availability
- Can significantly accelerate payoff

## Budgeting Frameworks

### 50/30/20 Rule
- 50% needs (housing, food, transportation, insurance, minimum debt payments)
- 30% wants (dining out, entertainment, hobbies, subscriptions)
- 20% savings/debt (emergency fund, extra debt payments, retirement)

### Zero-Based Budgeting
- Every dollar assigned a specific purpose
- Income - Expenses = $0
- Requires detailed expense tracking

### Envelope System
- Cash allocated to spending categories
- Prevents overspending in each category
- Good for variable expenses

## Error Handling

The agent includes fallback mechanisms for:
- Unrecognized intents → Returns general debt management advice
- Missing data → Asks targeted clarifying questions
- Technical errors → Returns helpful error messages with next steps

## Extensibility

To add new intent types:
1. Add keywords to `DebtIntentClassifier`
2. Create calculator method in `DebtCalculator`
3. Add advice rules in `DebtAdviceEngine`
4. Update response formatting in `DebtResponseGenerator`

