"""
Response Generation Module for Retirement Planning Agent.
Translates calculator outputs and advice rules into clear, actionable client-facing guidance.
"""

from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)


class RetirementResponseGenerator:
    """Generates client-facing responses from calculator outputs and advice rules."""
    
    def generate_response(
        self,
        intent_type: str,
        intent_data: Dict[str, Any],
        calculator_output: Optional[Dict[str, Any]],
        advice: List[Dict[str, Any]]
    ) -> str:
        """
        Generate a comprehensive response for the client.
        
        Args:
            intent_type: The classified intent type
            intent_data: Intent classification data
            calculator_output: Output from retirement calculators
            advice: List of advice recommendations
            
        Returns:
            Formatted response string
        """
        response_parts = []
        
        # Add personalized greeting
        response_parts.append(self._generate_greeting(intent_type, intent_data))
        
        # Add main analysis/answer
        response_parts.append(self._generate_main_answer(intent_type, calculator_output))
        
        # Add specific recommendations
        if advice:
            response_parts.append(self._format_advice(advice))
        
        # Add next steps
        response_parts.append(self._generate_next_steps(intent_type))
        
        return "\n\n".join(response_parts)
    
    def _generate_greeting(self, intent_type: str, intent_data: Dict[str, Any]) -> str:
        """Generate a personalized greeting based on intent."""
        question = intent_data.get("raw_question", "")
        
        if intent_type == "retirement_readiness":
            return f"Great question! Let me help you understand your retirement readiness. You asked: *{question}*"
        elif intent_type == "savings_strategy":
            return f"I'd be happy to help you optimize your retirement savings strategy. Your question: *{question}*"
        elif intent_type == "social_security":
            return f"Social Security is a crucial part of retirement planning. Let me help you understand your options. You asked: *{question}*"
        elif intent_type == "withdrawal_planning":
            return f"Withdrawal planning is essential for a secure retirement. Let me help you create a strategy. Your question: *{question}*"
        else:
            return f"Thank you for your retirement planning question. Let me help you with: *{question}*"
    
    def _generate_main_answer(self, intent_type: str, calculator_output: Optional[Dict[str, Any]]) -> str:
        """Generate the main answer based on intent type and calculator output."""
        if intent_type == "retirement_readiness":
            return self._format_retirement_readiness_answer(calculator_output)
        elif intent_type == "savings_strategy":
            return self._format_savings_strategy_answer(calculator_output)
        elif intent_type == "social_security":
            return self._format_social_security_answer(calculator_output)
        elif intent_type == "withdrawal_planning":
            return self._format_withdrawal_planning_answer(calculator_output)
        else:
            return "I understand your question. Let me provide guidance based on your retirement planning needs."
    
    def _format_retirement_readiness_answer(self, output: Optional[Dict[str, Any]]) -> str:
        """Format retirement readiness answer."""
        if not output:
            return "## Retirement Readiness Analysis\n\nTo provide a comprehensive assessment, I need information about your current savings, retirement timeline, and income goals."
        
        lines = ["## Your Retirement Readiness Assessment"]
        lines.append("")
        
        on_track = output.get("on_track", False)
        portfolio_value = output.get("current_portfolio_value", 0)
        expected_value = output.get("expected_value_at_retirement", 0)
        total_income = output.get("total_retirement_income", 0)
        target_income = output.get("target_annual_income", 0)
        success_prob = output.get("success_probability", 0)
        
        if on_track:
            lines.append(f"✅ **Good news!** You're on track for retirement.")
        else:
            gap = output.get("income_gap", 0)
            lines.append(f"⚠️ **Action needed:** You have a projected income gap of ${abs(gap):,.0f} per year.")
        
        lines.append("")
        lines.append("### Current Situation")
        lines.append(f"- **Current Portfolio Value:** ${portfolio_value:,.0f}")
        lines.append(f"- **Expected Value at Retirement:** ${expected_value:,.0f}")
        lines.append(f"- **Projected Total Retirement Income:** ${total_income:,.0f}/year")
        lines.append(f"- **Target Annual Income:** ${target_income:,.0f}/year")
        lines.append(f"- **Success Probability:** {success_prob:.0f}%")
        
        # Income breakdown
        portfolio_income = output.get("portfolio_income", 0)
        social_security = output.get("social_security_benefit", 0)
        pension = output.get("pension_income", 0)
        
        if portfolio_income > 0 or social_security > 0 or pension > 0:
            lines.append("")
            lines.append("### Income Sources Breakdown")
            if portfolio_income > 0:
                lines.append(f"- **Portfolio Income (4% rule):** ${portfolio_income:,.0f}/year")
            if social_security > 0:
                lines.append(f"- **Social Security:** ${social_security:,.0f}/year")
            if pension > 0:
                lines.append(f"- **Pension:** ${pension:,.0f}/year")
        
        return "\n".join(lines)
    
    def _format_savings_strategy_answer(self, output: Optional[Dict[str, Any]]) -> str:
        """Format savings strategy answer."""
        lines = ["## Retirement Savings Strategy"]
        lines.append("")
        lines.append("Here's a comprehensive approach to maximizing your retirement savings:")
        lines.append("")
        lines.append("### Contribution Limits (2024)")
        lines.append("- **401(k)/403(b):** $23,000 ($30,500 if 50+)")
        lines.append("- **IRA:** $7,000 ($8,000 if 50+)")
        lines.append("- **Catch-up contributions:** Additional $7,500 for 401(k), $1,000 for IRA if 50+")
        lines.append("")
        lines.append("### Key Strategies")
        lines.append("1. **Maximize employer match** - Don't leave free money on the table")
        lines.append("2. **Automate contributions** - Set it and forget it")
        lines.append("3. **Increase with raises** - Boost contributions when income increases")
        lines.append("4. **Tax diversification** - Balance traditional and Roth accounts")
        lines.append("")
        lines.append("### Account Priority")
        lines.append("1. 401(k) up to employer match (free money)")
        lines.append("2. Max out IRA (more investment options)")
        lines.append("3. Max out 401(k) (higher limits)")
        lines.append("4. Consider taxable accounts for additional savings")
        
        return "\n".join(lines)
    
    def _format_social_security_answer(self, output: Optional[Dict[str, Any]]) -> str:
        """Format Social Security answer."""
        lines = ["## Social Security Claiming Strategy"]
        lines.append("")
        
        if output:
            claiming_age = output.get("claiming_age", 67)
            fra = output.get("full_retirement_age", 67)
            benefit = output.get("benefit_at_claiming_age", 0)
            benefit_at_fra = output.get("benefit_at_fra", 0)
            
            lines.append("### Your Benefit Analysis")
            lines.append(f"- **Full Retirement Age:** {fra}")
            lines.append(f"- **Claiming Age:** {claiming_age}")
            lines.append(f"- **Benefit at FRA:** ${benefit_at_fra:,.0f}/year")
            lines.append(f"- **Benefit at Claiming Age:** ${benefit:,.0f}/year")
            lines.append("")
        
        lines.append("### Key Considerations")
        lines.append("")
        lines.append("**Early Claiming (Before FRA):**")
        lines.append("- Benefits reduced by ~6.67% per year (up to 36 months early)")
        lines.append("- Then ~5% per year for additional months")
        lines.append("- Reduction is permanent")
        lines.append("- May make sense if you need income or have health concerns")
        lines.append("")
        lines.append("**Delayed Claiming (After FRA):**")
        lines.append("- Benefits increase by ~8% per year")
        lines.append("- Maximum benefit reached at age 70")
        lines.append("- Increases are permanent")
        lines.append("- Best strategy for longer life expectancies")
        lines.append("")
        lines.append("**Spousal Benefits:**")
        lines.append("- Spouse can claim up to 50% of your benefit")
        lines.append("- Timing of both spouses' claims matters")
        lines.append("- Consider survivor benefits for the lower-earning spouse")
        
        return "\n".join(lines)
    
    def _format_withdrawal_planning_answer(self, output: Optional[Dict[str, Any]]) -> str:
        """Format withdrawal planning answer."""
        lines = ["## Retirement Withdrawal Planning"]
        lines.append("")
        
        if output:
            portfolio_value = output.get("portfolio_value", 0)
            withdrawal_rate = output.get("withdrawal_rate", 0.04)
            initial_withdrawal = output.get("initial_annual_withdrawal", 0)
            
            lines.append("### Your Withdrawal Analysis")
            lines.append(f"- **Portfolio Value:** ${portfolio_value:,.0f}")
            lines.append(f"- **Withdrawal Rate:** {withdrawal_rate*100:.1f}%")
            lines.append(f"- **Initial Annual Withdrawal:** ${initial_withdrawal:,.0f}")
            lines.append(f"- **Initial Monthly Withdrawal:** ${initial_withdrawal/12:,.0f}")
            lines.append("")
        
        lines.append("### The 4% Rule")
        lines.append("The 4% rule suggests withdrawing 4% of your portfolio in the first year of retirement, then adjusting for inflation each subsequent year.")
        lines.append("")
        lines.append("- **Success Rate:** Historically ~95% for 30-year retirements")
        lines.append("- **Assumptions:** 50/50 stock/bond allocation, 3% inflation")
        lines.append("- **Adjustments:** Use 3-3.5% for longer retirements (35+ years)")
        lines.append("")
        lines.append("### Tax-Efficient Withdrawal Order")
        lines.append("1. **Taxable accounts first** - Capital gains rates, basis step-up")
        lines.append("2. **Traditional IRAs/401(k)s** - Ordinary income rates, RMDs at 72")
        lines.append("3. **Roth accounts last** - Tax-free, no RMDs")
        lines.append("")
        lines.append("### Required Minimum Distributions (RMDs)")
        lines.append("- Start at age 72 (73 for those reaching 72 after 2022)")
        lines.append("- Based on account balance and life expectancy")
        lines.append("- Failure to take RMD results in 25% penalty")
        lines.append("- Consider Roth conversions before RMD age")
        
        return "\n".join(lines)
    
    def _format_advice(self, advice: List[Dict[str, Any]]) -> str:
        """Format advice recommendations."""
        lines = ["## Personalized Recommendations"]
        lines.append("")
        
        # Sort by priority
        priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        sorted_advice = sorted(advice, key=lambda x: priority_order.get(x.get("priority", "low"), 3))
        
        for i, rec in enumerate(sorted_advice, 1):
            priority = rec.get("priority", "medium").upper()
            title = rec.get("title", "Recommendation")
            message = rec.get("message", "")
            action_items = rec.get("action_items", [])
            
            lines.append(f"### {i}. {title} ({priority} Priority)")
            lines.append("")
            lines.append(message)
            
            if action_items:
                lines.append("")
                lines.append("**Action Items:**")
                for item in action_items:
                    lines.append(f"- {item}")
            
            lines.append("")
        
        return "\n".join(lines)
    
    def _generate_next_steps(self, intent_type: str) -> str:
        """Generate next steps section."""
        lines = ["## Next Steps"]
        lines.append("")
        
        if intent_type == "retirement_readiness":
            lines.append("1. Review your current contribution rate and consider increasing it")
            lines.append("2. Check if you're maximizing employer match")
            lines.append("3. Review your portfolio allocation for optimization")
            lines.append("4. Consider consulting with a financial advisor for personalized planning")
        elif intent_type == "savings_strategy":
            lines.append("1. Set up automatic contributions to retirement accounts")
            lines.append("2. Increase contributions with each raise or bonus")
            lines.append("3. Review and maximize all available tax-advantaged accounts")
            lines.append("4. Track your progress annually")
        elif intent_type == "social_security":
            lines.append("1. Create an account at ssa.gov to view your estimated benefits")
            lines.append("2. Consider your health and life expectancy when deciding when to claim")
            lines.append("3. Coordinate claiming strategy with your spouse")
            lines.append("4. Consider working with a financial advisor on claiming strategy")
        elif intent_type == "withdrawal_planning":
            lines.append("1. Create a withdrawal plan before retirement")
            lines.append("2. Understand RMD requirements for your accounts")
            lines.append("3. Plan for tax-efficient withdrawal sequencing")
            lines.append("4. Review and adjust your plan annually")
        else:
            lines.append("1. Provide more details about your specific retirement situation")
            lines.append("2. Review your current retirement savings and goals")
            lines.append("3. Consider consulting with a financial advisor")
            lines.append("4. Create an action plan with timelines")
        
        return "\n".join(lines)

