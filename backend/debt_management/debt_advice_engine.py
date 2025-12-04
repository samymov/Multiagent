"""
Advice Rule Engine for Debt Management Agent.
Applies debt management and budgeting advice rules based on client situation.
"""

from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)


class DebtAdviceEngine:
    """Applies debt management and budgeting advice rules."""
    
    def __init__(self, user_data: Optional[Dict[str, Any]] = None):
        """
        Initialize advice engine.
        
        Args:
            user_data: User profile data
        """
        self.user_data = user_data or {}
    
    def apply_debt_payoff_advice(
        self,
        calculator_output: Dict[str, Any],
        debts: List[Dict[str, Any]],
        monthly_payment: float,
        psychological_preference: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Apply advice rules for debt payoff strategies.
        
        Args:
            calculator_output: Output from debt calculator comparison
            debts: List of debts
            monthly_payment: Available monthly payment
            psychological_preference: "quick_wins" or "save_money"
            
        Returns:
            List of advice recommendations
        """
        advice = []
        
        comparison = calculator_output.get("comparison", {})
        recommended = comparison.get("recommended_strategy", "avalanche")
        interest_savings = comparison.get("interest_savings", 0)
        
        # Rule 1: Strategy recommendation
        if recommended == "avalanche":
            advice.append({
                "priority": "high",
                "category": "strategy",
                "title": "Recommended: Debt Avalanche Method",
                "message": f"The Avalanche method will save you ${abs(interest_savings):,.2f} in interest compared to Snowball. Focus on paying off your highest interest rate debt first.",
                "action_items": [
                    "List all debts by interest rate (highest first)",
                    f"Pay minimums on all debts, then apply extra ${monthly_payment - sum(d.get('minimum_payment', 0) for d in debts):,.2f} to highest rate debt",
                    "Once highest rate debt is paid, move to next highest",
                    "Track progress monthly to stay motivated"
                ]
            })
        else:
            advice.append({
                "priority": "high",
                "category": "strategy",
                "title": "Recommended: Debt Snowball Method",
                "message": "The Snowball method provides psychological wins by eliminating smaller debts first, building momentum for larger debts.",
                "action_items": [
                    "List all debts by balance (smallest first)",
                    f"Pay minimums on all debts, then apply extra ${monthly_payment - sum(d.get('minimum_payment', 0) for d in debts):,.2f} to smallest debt",
                    "Celebrate each debt paid off to maintain motivation",
                    "Once smallest debt is paid, move to next smallest"
                ]
            })
        
        # Rule 2: Payment adequacy
        total_minimums = sum(d.get("minimum_payment", 0) for d in debts)
        if monthly_payment <= total_minimums:
            advice.append({
                "priority": "critical",
                "category": "payment_adequacy",
                "title": "⚠️ Payment amount too low",
                "message": f"Your monthly payment of ${monthly_payment:,.2f} only covers minimum payments (${total_minimums:,.2f}). You need to increase your payment to make progress.",
                "action_items": [
                    "Review budget to find additional funds for debt repayment",
                    "Consider reducing discretionary spending",
                    "Look for opportunities to increase income",
                    "Consider debt consolidation if interest rates are high"
                ]
            })
        elif monthly_payment < total_minimums * 1.2:
            advice.append({
                "priority": "medium",
                "category": "payment_optimization",
                "title": "Consider increasing payment amount",
                "message": f"You're paying slightly above minimums. Increasing to ${total_minimums * 1.5:,.2f} would accelerate payoff significantly.",
                "action_items": [
                    "Identify $100-200/month in budget cuts",
                    "Apply windfalls (tax refunds, bonuses) to debt",
                    "Consider side income opportunities"
                ]
            })
        
        # Rule 3: High interest rate warning
        high_interest_debts = [d for d in debts if d.get("interest_rate", 0) > 20]
        if high_interest_debts:
            advice.append({
                "priority": "high",
                "category": "high_interest",
                "title": "⚠️ High interest rate debts detected",
                "message": f"You have {len(high_interest_debts)} debt(s) with interest rates above 20%. These should be prioritized immediately.",
                "action_items": [
                    "Focus all extra payments on highest interest debt",
                    "Consider balance transfer to 0% APR card if eligible",
                    "Explore debt consolidation options",
                    "Avoid using these credit lines while paying off"
                ]
            })
        
        # Rule 4: Debt consolidation recommendation
        if len(debts) >= 3 and any(d.get("interest_rate", 0) > 15 for d in debts):
            avg_rate = sum(d.get("interest_rate", 0) for d in debts) / len(debts)
            if avg_rate > 12:
                advice.append({
                    "priority": "medium",
                    "category": "consolidation",
                    "title": "Consider debt consolidation",
                    "message": f"With {len(debts)} debts and average interest rate of {avg_rate:.1f}%, consolidation could simplify payments and potentially lower rates.",
                    "action_items": [
                        "Research personal loan options (rates typically 6-12%)",
                        "Compare consolidation loan rate to current weighted average",
                        "Ensure consolidation saves money after fees",
                        "Maintain discipline to avoid new debt after consolidation"
                    ]
                })
        
        return advice
    
    def apply_student_loan_advice(
        self,
        loan_info: Dict[str, Any],
        employment_info: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Apply advice rules for student loan management.
        
        Args:
            loan_info: Student loan information
            employment_info: Employment and income information
            
        Returns:
            List of advice recommendations
        """
        advice = []
        
        loan_type = loan_info.get("loan_type", "federal")
        current_plan = loan_info.get("repayment_plan", "standard")
        income = employment_info.get("income", 0)
        employment_sector = employment_info.get("sector", "")
        
        # Rule 1: IDR plan recommendation
        if loan_type == "federal" and current_plan == "standard":
            if income < 50000:  # Low income threshold
                advice.append({
                    "priority": "high",
                    "category": "repayment_plan",
                    "title": "Consider Income-Driven Repayment (IDR) Plan",
                    "message": "With your income level, an IDR plan (SAVE, PAYE, or IBR) could significantly reduce your monthly payment.",
                    "action_items": [
                        "Research SAVE plan (most generous for low-income borrowers)",
                        "Calculate payment under IDR vs. standard plan",
                        "Apply for IDR plan through studentaid.gov",
                        "Re-certify income annually to maintain lower payments"
                    ]
                })
        
        # Rule 2: PSLF eligibility
        if loan_type == "federal" and employment_sector.lower() in ["government", "nonprofit", "public service", "education"]:
            advice.append({
                "priority": "high",
                "category": "forgiveness",
                "title": "You may be eligible for Public Service Loan Forgiveness (PSLF)",
                "message": "PSLF forgives remaining balance after 120 qualifying payments (10 years) for public service workers.",
                "action_items": [
                    "Verify employer qualifies for PSLF",
                    "Ensure you're on a qualifying repayment plan (IDR or standard 10-year)",
                    "Submit Employment Certification Form annually",
                    "Track qualifying payments (must be on-time, full payments)"
                ]
            })
        
        # Rule 3: Employer student loan benefit
        if employment_info.get("has_employer_benefit", False):
            benefit_amount = employment_info.get("employer_benefit_amount", 5250)
            advice.append({
                "priority": "high",
                "category": "employer_benefit",
                "title": "Maximize employer student loan assistance",
                "message": f"Your employer offers up to ${benefit_amount:,.0f} annually in tax-free student loan assistance (through 2025).",
                "action_items": [
                    f"Ensure you're enrolled to receive the full ${benefit_amount:,.0f} benefit",
                    "Apply employer payments to highest interest rate loans first",
                    "Track benefit usage to maximize tax savings",
                    "Coordinate with HR to ensure proper tax treatment"
                ]
            })
        else:
            advice.append({
                "priority": "low",
                "category": "employer_benefit",
                "title": "Ask about employer student loan benefits",
                "message": "Many employers now offer student loan assistance. It's worth asking HR if this benefit is available.",
                "action_items": [
                    "Check with HR about student loan assistance programs",
                    "If not available, consider advocating for this benefit",
                    "Up to $5,250 annually is tax-free through 2025"
                ]
            })
        
        # Rule 4: Refinancing consideration
        current_rate = loan_info.get("interest_rate", 0)
        if loan_type == "federal" and current_rate > 6:
            advice.append({
                "priority": "medium",
                "category": "refinancing",
                "title": "Consider refinancing (with caution)",
                "message": f"Your federal loan rate of {current_rate:.2f}% is relatively high. Refinancing to private could lower it, but you'll lose federal protections.",
                "action_items": [
                    "Research current private refinancing rates",
                    "Compare potential savings vs. loss of federal protections (IDR, PSLF, deferment)",
                    "Only refinance if you have stable income and job security",
                    "Consider refinancing only high-rate loans, keep federal benefits on others"
                ]
            })
        
        return advice
    
    def apply_budget_creation_advice(
        self,
        income: float,
        expenses: Dict[str, float],
        framework: str = "50/30/20"
    ) -> List[Dict[str, Any]]:
        """
        Apply advice rules for budget creation.
        
        Args:
            income: Monthly income
            expenses: Dictionary of expenses by category
            framework: Budgeting framework to apply
            
        Returns:
            List of advice recommendations
        """
        advice = []
        
        total_expenses = sum(expenses.values())
        remaining = income - total_expenses
        
        # Rule 1: Budget balance
        if remaining < 0:
            advice.append({
                "priority": "critical",
                "category": "budget_balance",
                "title": "⚠️ Expenses exceed income",
                "message": f"Your expenses (${total_expenses:,.2f}) exceed your income (${income:,.2f}) by ${abs(remaining):,.2f} per month. Immediate action needed.",
                "action_items": [
                    "Identify expenses to reduce or eliminate",
                    "Consider increasing income through side work",
                    "Prioritize essential expenses (housing, food, minimum debt payments)",
                    "Create emergency plan to address deficit"
                ]
            })
        elif remaining < income * 0.10:
            advice.append({
                "priority": "high",
                "category": "budget_tightness",
                "title": "Budget is very tight",
                "message": f"You have only ${remaining:,.2f} remaining ({(remaining/income)*100:.1f}% of income). Consider reducing expenses to build buffer.",
                "action_items": [
                    "Review variable expenses for reduction opportunities",
                    "Negotiate fixed expenses (insurance, subscriptions)",
                    "Build emergency fund to avoid future debt"
                ]
            })
        
        # Rule 2: Framework-specific advice
        if framework == "50/30/20":
            needs = income * 0.50
            wants = income * 0.30
            savings_debt = income * 0.20
            
            current_needs = expenses.get("needs", 0)
            current_wants = expenses.get("wants", 0)
            current_savings_debt = expenses.get("savings_debt", 0)
            
            if current_needs > needs:
                advice.append({
                    "priority": "medium",
                    "category": "needs_allocation",
                    "title": "Needs exceed 50% of income",
                    "message": f"Your needs (${current_needs:,.2f}) exceed the recommended 50% (${needs:,.2f}). This limits flexibility.",
                    "action_items": [
                        "Review needs category - distinguish true needs from wants",
                        "Negotiate fixed expenses where possible",
                        "Consider downsizing housing or transportation if feasible"
                    ]
                })
            
            if current_savings_debt < savings_debt:
                advice.append({
                    "priority": "high",
                    "category": "savings_allocation",
                    "title": "Increase savings/debt allocation",
                    "message": f"You're allocating ${current_savings_debt:,.2f} to savings/debt, but should target ${savings_debt:,.2f} (20% of income).",
                    "action_items": [
                        f"Increase savings/debt allocation by ${savings_debt - current_savings_debt:,.2f}",
                        "Automate savings transfers",
                        "Apply 'pay yourself first' principle"
                    ]
                })
        
        return advice
    
    def apply_spending_reduction_advice(
        self,
        expenses: Dict[str, float],
        income: float
    ) -> List[Dict[str, Any]]:
        """
        Apply advice rules for spending reduction.
        
        Args:
            expenses: Dictionary of expenses
            income: Monthly income
            
        Returns:
            List of spending reduction recommendations
        """
        advice = []
        
        # Categorize expenses
        fixed_expenses = expenses.get("fixed", {})
        variable_expenses = expenses.get("variable", {})
        
        # Rule 1: Subscription audit
        subscriptions = variable_expenses.get("subscriptions", 0)
        if subscriptions > 50:
            advice.append({
                "priority": "medium",
                "category": "subscriptions",
                "title": "Review and cancel unused subscriptions",
                "message": f"You're spending ${subscriptions:,.2f}/month on subscriptions. Many people have unused subscriptions they forget about.",
                "action_items": [
                    "List all subscriptions and their costs",
                    "Cancel any unused or rarely used services",
                    "Consider sharing family plans where possible",
                    "Set calendar reminders to review quarterly"
                ]
            })
        
        # Rule 2: Dining out reduction
        dining_out = variable_expenses.get("dining_out", 0)
        if dining_out > income * 0.10:
            advice.append({
                "priority": "medium",
                "category": "dining",
                "title": "Reduce dining out expenses",
                "message": f"You're spending ${dining_out:,.2f}/month on dining out ({(dining_out/income)*100:.1f}% of income). Reducing this can free up significant funds.",
                "action_items": [
                    "Set dining out budget (e.g., $100/month)",
                    "Meal prep on weekends to reduce weekday dining",
                    "Use cash envelope for dining out to stay within budget",
                    "Find free or low-cost entertainment alternatives"
                ]
            })
        
        # Rule 3: Fixed expense negotiation
        insurance = fixed_expenses.get("insurance", 0)
        utilities = fixed_expenses.get("utilities", 0)
        
        if insurance > 0:
            advice.append({
                "priority": "low",
                "category": "insurance",
                "title": "Shop around for insurance",
                "message": "Insurance rates can vary significantly. Shopping around annually can save hundreds per year.",
                "action_items": [
                    "Get quotes from 3-5 insurance providers",
                    "Bundle policies (auto + home) for discounts",
                    "Review coverage levels - ensure adequate but not excessive",
                    "Ask about discounts (good driver, loyalty, etc.)"
                ]
            })
        
        if utilities > income * 0.05:
            advice.append({
                "priority": "low",
                "category": "utilities",
                "title": "Reduce utility costs",
                "message": f"Your utilities (${utilities:,.2f}) are {(utilities/income)*100:.1f}% of income. Small changes can add up.",
                "action_items": [
                    "Install programmable thermostat",
                    "Switch to LED bulbs",
                    "Unplug unused electronics",
                    "Compare utility providers if in deregulated area"
                ]
            })
        
        # Rule 4: Lifestyle adjustments
        total_variable = sum(variable_expenses.values())
        if total_variable > income * 0.30:
            advice.append({
                "priority": "medium",
                "category": "lifestyle",
                "title": "Review lifestyle spending",
                "message": f"Variable expenses (${total_variable:,.2f}) are {(total_variable/income)*100:.1f}% of income. Focus on high-impact, low-effort reductions.",
                "action_items": [
                    "Track all spending for 30 days to identify patterns",
                    "Use 24-hour rule for non-essential purchases",
                    "Find free alternatives to paid activities",
                    "Set specific spending limits for entertainment categories"
                ]
            })
        
        return advice
    
    def generate_advice(
        self,
        intent_type: str,
        calculator_output: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate advice based on intent type and context.
        
        Args:
            intent_type: The classified intent type
            calculator_output: Output from debt calculators
            context: Additional context (debts, income, expenses, etc.)
            
        Returns:
            List of advice recommendations
        """
        context = context or {}
        
        if intent_type == "debt_payoff_strategy":
            debts = context.get("debts", [])
            monthly_payment = context.get("monthly_payment", 0)
            preference = context.get("psychological_preference")
            return self.apply_debt_payoff_advice(calculator_output or {}, debts, monthly_payment, preference)
        
        elif intent_type == "student_loan_management":
            loan_info = context.get("loan_info", {})
            employment_info = context.get("employment_info", {})
            return self.apply_student_loan_advice(loan_info, employment_info)
        
        elif intent_type == "budget_creation":
            income = context.get("income", 0)
            expenses = context.get("expenses", {})
            framework = context.get("framework", "50/30/20")
            return self.apply_budget_creation_advice(income, expenses, framework)
        
        elif intent_type == "spending_reduction":
            expenses = context.get("expenses", {})
            income = context.get("income", 0)
            return self.apply_spending_reduction_advice(expenses, income)
        
        elif intent_type == "debt_consolidation":
            debts = context.get("debts", [])
            monthly_payment = context.get("monthly_payment", 0)
            return self.apply_debt_payoff_advice(calculator_output or {}, debts, monthly_payment)
        
        else:
            return [{
                "priority": "low",
                "category": "general",
                "title": "General debt management advice",
                "message": "I'd be happy to help with your debt management question. Could you provide more details about your specific situation?",
                "action_items": []
            }]

