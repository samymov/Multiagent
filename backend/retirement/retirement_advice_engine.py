"""
Advice Rule Engine for Retirement Planning Agent.
Applies retirement planning advice rules based on client situation and calculator outputs.
"""

from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)


class RetirementAdviceEngine:
    """Applies retirement planning advice rules."""
    
    def __init__(self, user_data: Optional[Dict[str, Any]] = None):
        """
        Initialize advice engine.
        
        Args:
            user_data: User profile data
        """
        self.user_data = user_data or {}
    
    def apply_retirement_readiness_advice(
        self,
        calculator_output: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Apply advice rules for retirement readiness assessment.
        
        Args:
            calculator_output: Output from retirement readiness calculator
            
        Returns:
            List of advice recommendations
        """
        advice = []
        
        on_track = calculator_output.get("on_track", False)
        success_prob = calculator_output.get("success_probability", 0)
        income_gap = calculator_output.get("income_gap", 0)
        required_contribution = calculator_output.get("required_annual_contribution", 0)
        current_contribution = calculator_output.get("current_annual_contribution", 0)
        
        # Rule 1: On-track assessment
        if on_track:
            advice.append({
                "priority": "high",
                "category": "status",
                "title": "✅ You're on track for retirement!",
                "message": f"Based on your current savings and projections, you're on track to meet your retirement income goal. Your success probability is {success_prob:.0f}%.",
                "action_items": [
                    "Continue your current contribution rate",
                    "Review your portfolio allocation annually",
                    "Consider increasing contributions if you receive a raise",
                    "Stay the course and maintain your savings discipline"
                ]
            })
        else:
            gap = abs(income_gap)
            advice.append({
                "priority": "high",
                "category": "gap_analysis",
                "title": "⚠️ Action needed to meet retirement goal",
                "message": f"You have a projected income gap of ${gap:,.0f} per year. You'll need to increase your savings to meet your retirement goal.",
                "action_items": [
                    f"Increase annual contributions by ${required_contribution - current_contribution:,.0f}",
                    "Consider maximizing employer match if available",
                    "Review and optimize your investment allocation",
                    "Consider working 1-2 years longer if feasible"
                ]
            })
        
        # Rule 2: Success probability assessment
        if success_prob < 50:
            advice.append({
                "priority": "critical",
                "category": "risk_mitigation",
                "title": "⚠️ Low success probability - immediate action needed",
                "message": f"Your current plan has a {success_prob:.0f}% probability of success. Significant adjustments are needed.",
                "action_items": [
                    "Increase savings rate by at least 20%",
                    "Consider working 3-5 years longer",
                    "Review target retirement income for feasibility",
                    "Consult with a financial advisor for personalized planning"
                ]
            })
        elif success_prob < 70:
            advice.append({
                "priority": "medium",
                "category": "improvement",
                "title": "Moderate success probability - improvements recommended",
                "message": f"Your plan has a {success_prob:.0f}% probability of success. Some improvements would increase your confidence.",
                "action_items": [
                    "Increase contributions by 10-15%",
                    "Review asset allocation for optimization",
                    "Consider catch-up contributions if over 50",
                    "Explore additional income sources"
                ]
            })
        
        return advice
    
    def apply_savings_strategy_advice(
        self,
        context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Apply advice rules for retirement savings strategies.
        
        Args:
            context: Context with age, income, account types, etc.
            
        Returns:
            List of advice recommendations
        """
        advice = []
        
        age = context.get("current_age", 40)
        income = context.get("income", 0)
        
        # Rule 1: Contribution limits (2024)
        if age < 50:
            ira_limit = 7000
            k401_limit = 23000
        else:
            ira_limit = 8000  # Catch-up contribution
            k401_limit = 30500  # Catch-up contribution
        
        advice.append({
            "priority": "high",
            "category": "contribution_limits",
            "title": "Maximize tax-advantaged accounts",
            "message": f"For {2024}, contribution limits are: 401(k)/403(b): ${k401_limit:,}, IRA: ${ira_limit:,} (with catch-up if 50+).",
            "action_items": [
                f"Contribute at least enough to get full employer match",
                f"Aim to maximize 401(k) contributions (${k401_limit:,})",
                f"Consider IRA contributions up to ${ira_limit:,}",
                "Automate contributions to ensure consistency"
            ]
        })
        
        # Rule 2: Roth vs Traditional
        if income < 100000:
            advice.append({
                "priority": "medium",
                "category": "account_selection",
                "title": "Consider Roth accounts for tax diversification",
                "message": "With your income level, Roth contributions can provide tax-free growth and withdrawals in retirement.",
                "action_items": [
                    "Consider Roth 401(k) or Roth IRA contributions",
                    "Balance between traditional and Roth for tax diversification",
                    "Roth is especially valuable if you expect higher tax bracket in retirement"
                ]
            })
        else:
            advice.append({
                "priority": "medium",
                "category": "account_selection",
                "title": "Traditional accounts may provide immediate tax benefit",
                "message": "With your income level, traditional 401(k) contributions provide immediate tax deduction.",
                "action_items": [
                    "Maximize traditional 401(k) for current tax savings",
                    "Consider Roth IRA for tax diversification (income limits apply)",
                    "Balance between traditional and Roth based on expected retirement tax bracket"
                ]
            })
        
        # Rule 3: Catch-up contributions
        if age >= 50:
            advice.append({
                "priority": "high",
                "category": "catch_up",
                "title": "Take advantage of catch-up contributions",
                "message": "You're eligible for catch-up contributions: additional $7,500 for 401(k) and $1,000 for IRA.",
                "action_items": [
                    "Increase 401(k) contributions by $7,500 if possible",
                    "Add $1,000 to IRA contributions",
                    "These catch-up contributions are especially valuable in your final working years"
                ]
            })
        
        return advice
    
    def apply_social_security_advice(
        self,
        calculator_output: Dict[str, Any],
        context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Apply advice rules for Social Security claiming strategies.
        
        Args:
            calculator_output: Output from Social Security calculator
            context: Context with age, health, etc.
            
        Returns:
            List of advice recommendations
        """
        advice = []
        
        claiming_age = calculator_output.get("claiming_age", 67)
        full_retirement_age = calculator_output.get("full_retirement_age", 67)
        benefit = calculator_output.get("benefit_at_claiming_age", 0)
        benefit_at_fra = calculator_output.get("benefit_at_fra", 0)
        
        current_age = context.get("current_age", 65)
        health_status = context.get("health_status", "average")
        
        # Rule 1: Early claiming
        if claiming_age < full_retirement_age:
            reduction = ((benefit_at_fra - benefit) / benefit_at_fra) * 100
            advice.append({
                "priority": "high",
                "category": "claiming_strategy",
                "title": "⚠️ Early claiming reduces benefits permanently",
                "message": f"Claiming at age {claiming_age} reduces your benefit by {reduction:.1f}% compared to full retirement age. This reduction is permanent.",
                "action_items": [
                    "Consider delaying if you can afford to wait",
                    "Each year of delay increases benefit by ~8%",
                    "If you need income, consider part-time work instead",
                    "Early claiming may make sense if you have health concerns"
                ]
            })
        
        # Rule 2: Delayed claiming
        elif claiming_age > full_retirement_age:
            increase = ((benefit - benefit_at_fra) / benefit_at_fra) * 100
            advice.append({
                "priority": "high",
                "category": "claiming_strategy",
                "title": "✅ Delayed claiming increases benefits",
                "message": f"Delaying until age {claiming_age} increases your benefit by {increase:.1f}% compared to full retirement age. Benefits max out at age 70.",
                "action_items": [
                    "If you can afford to wait, delaying maximizes lifetime benefits",
                    "Consider using other assets first to delay Social Security",
                    "Delayed credits stop at age 70, so claim by then",
                    "This strategy is especially valuable for longer life expectancies"
                ]
            })
        
        # Rule 3: Health considerations
        if health_status == "poor" or context.get("life_expectancy", 0) < 75:
            advice.append({
                "priority": "medium",
                "category": "health_consideration",
                "title": "Health may influence claiming decision",
                "message": "If you have health concerns or shorter life expectancy, earlier claiming may make sense.",
                "action_items": [
                    "Consider your family health history",
                    "Consult with a financial advisor about your specific situation",
                    "Balance between maximizing benefits and ensuring you receive them"
                ]
            })
        
        return advice
    
    def apply_withdrawal_planning_advice(
        self,
        calculator_output: Dict[str, Any],
        context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Apply advice rules for withdrawal planning.
        
        Args:
            calculator_output: Output from withdrawal calculator
            context: Context with retirement timeline, etc.
            
        Returns:
            List of advice recommendations
        """
        advice = []
        
        withdrawal_rate = calculator_output.get("withdrawal_rate", 0.04)
        initial_withdrawal = calculator_output.get("initial_annual_withdrawal", 0)
        portfolio_value = calculator_output.get("portfolio_value", 0)
        
        # Rule 1: 4% rule explanation
        advice.append({
            "priority": "high",
            "category": "withdrawal_strategy",
            "title": "Understanding the 4% Rule",
            "message": f"The 4% rule suggests withdrawing ${initial_withdrawal:,.0f} initially (4% of ${portfolio_value:,.0f}), adjusted for inflation each year. This historically had a high success rate for 30-year retirements.",
            "action_items": [
                "Start with 4% withdrawal rate for 30-year retirements",
                "Adjust to 3-3.5% for longer retirements (35+ years)",
                "Be flexible - reduce withdrawals in down markets",
                "Consider dynamic withdrawal strategies based on portfolio performance"
            ]
        })
        
        # Rule 2: RMD planning
        age = context.get("current_age", 72)
        if age >= 72:
            advice.append({
                "priority": "high",
                "category": "rmd_planning",
                "title": "Required Minimum Distributions (RMDs)",
                "message": "You must take RMDs from traditional IRAs and 401(k)s starting at age 72 (73 for those who reach 72 after 2022).",
                "action_items": [
                    "Calculate RMD for each account annually",
                    "Plan withdrawals to meet RMD requirements",
                    "Consider Roth conversions before RMD age to reduce future RMDs",
                    "Work with a tax professional to optimize RMD timing"
                ]
            })
        
        # Rule 3: Tax-efficient withdrawal order
        advice.append({
            "priority": "medium",
            "category": "tax_optimization",
            "title": "Tax-efficient withdrawal strategy",
            "message": "The order in which you withdraw from accounts can significantly impact your taxes.",
            "action_items": [
                "Withdraw from taxable accounts first (capital gains rates)",
                "Then traditional IRAs/401(k)s (ordinary income rates)",
                "Save Roth accounts for last (tax-free)",
                "Consider your tax bracket each year when planning withdrawals"
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
            calculator_output: Output from retirement calculators
            context: Additional context (age, income, portfolio, etc.)
            
        Returns:
            List of advice recommendations
        """
        context = context or {}
        calculator_output = calculator_output or {}
        
        if intent_type == "retirement_readiness":
            return self.apply_retirement_readiness_advice(calculator_output)
        elif intent_type == "savings_strategy":
            return self.apply_savings_strategy_advice(context)
        elif intent_type == "social_security":
            return self.apply_social_security_advice(calculator_output, context)
        elif intent_type == "withdrawal_planning":
            return self.apply_withdrawal_planning_advice(calculator_output, context)
        else:
            return [{
                "priority": "low",
                "category": "general",
                "title": "General retirement planning advice",
                "message": "I'd be happy to help with your retirement planning question. Could you provide more details about your specific situation?",
                "action_items": []
            }]

