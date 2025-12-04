"""
Response Generation Module for Debt Management Agent.
Translates calculator outputs and advice rules into clear, actionable client-facing guidance.
"""

from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)


class DebtResponseGenerator:
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
            calculator_output: Output from debt calculators
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
        
        if intent_type == "debt_payoff_strategy":
            return f"I understand you're looking for the best way to pay off your debts. Let me help you find the most effective strategy. Your question: *{question}*"
        elif intent_type == "student_loan_management":
            return f"Student loans can be complex. Let me help you navigate your options. You asked: *{question}*"
        elif intent_type == "budget_creation":
            return f"Creating a budget is a great step toward financial control. Let's build one that works for you. Your question: *{question}*"
        elif intent_type == "spending_reduction":
            return f"Reducing spending can free up significant funds for your goals. Let me help identify opportunities. You asked: *{question}*"
        elif intent_type == "debt_consolidation":
            return f"Debt consolidation can simplify payments and potentially save money. Let me analyze if it's right for you. Your question: *{question}*"
        else:
            return f"Thank you for your question. Let me help you with debt management: *{question}*"
    
    def _generate_main_answer(self, intent_type: str, calculator_output: Optional[Dict[str, Any]]) -> str:
        """Generate the main answer based on intent type and calculator output."""
        if intent_type == "debt_payoff_strategy":
            return self._format_debt_payoff_answer(calculator_output)
        elif intent_type == "student_loan_management":
            return self._format_student_loan_answer(calculator_output)
        elif intent_type == "budget_creation":
            return self._format_budget_creation_answer(calculator_output)
        elif intent_type == "spending_reduction":
            return self._format_spending_reduction_answer(calculator_output)
        elif intent_type == "debt_consolidation":
            return self._format_debt_consolidation_answer(calculator_output)
        else:
            return "I understand your question. Let me provide guidance based on your financial situation."
    
    def _format_debt_payoff_answer(self, output: Optional[Dict[str, Any]]) -> str:
        """Format debt payoff strategy answer."""
        if not output or "comparison" not in output:
            return "## Debt Payoff Strategy Analysis\n\nTo provide the best recommendation, I need information about your debts. Please share:\n- Total balance and interest rate for each debt\n- Minimum monthly payment for each\n- Total amount you can pay toward debt each month"
        
        comparison = output["comparison"]
        avalanche = comparison.get("avalanche", {})
        snowball = comparison.get("snowball", {})
        recommended = comparison.get("recommended_strategy", "avalanche")
        interest_savings = comparison.get("interest_savings", 0)
        
        lines = ["## Debt Payoff Strategy Comparison"]
        lines.append("")
        
        # Strategy comparison
        lines.append("### Avalanche Method (Highest Interest First)")
        lines.append(f"- **Total Interest Paid:** ${avalanche.get('total_interest', 0):,.2f}")
        lines.append(f"- **Months to Payoff:** {avalanche.get('months_to_payoff', 0)}")
        lines.append(f"- **Total Paid:** ${avalanche.get('total_paid', 0):,.2f}")
        lines.append("")
        
        lines.append("### Snowball Method (Smallest Balance First)")
        lines.append(f"- **Total Interest Paid:** ${snowball.get('total_interest', 0):,.2f}")
        lines.append(f"- **Months to Payoff:** {snowball.get('months_to_payoff', 0)}")
        lines.append(f"- **Total Paid:** ${snowball.get('total_paid', 0):,.2f}")
        lines.append("")
        
        # Recommendation
        if recommended == "avalanche":
            lines.append(f"### 💡 Recommendation: Avalanche Method")
            lines.append(f"The Avalanche method will save you **${abs(interest_savings):,.2f}** in interest compared to Snowball.")
        else:
            lines.append(f"### 💡 Recommendation: Snowball Method")
            lines.append("The Snowball method provides psychological wins that help maintain motivation.")
        
        return "\n".join(lines)
    
    def _format_student_loan_answer(self, output: Optional[Dict[str, Any]]) -> str:
        """Format student loan management answer."""
        lines = ["## Student Loan Management Analysis"]
        lines.append("")
        
        if output and "loan_analysis" in output:
            analysis = output["loan_analysis"]
            lines.append("### Current Loan Situation")
            lines.append(f"- **Loan Type:** {analysis.get('loan_type', 'Unknown')}")
            lines.append(f"- **Current Balance:** ${analysis.get('balance', 0):,.2f}")
            lines.append(f"- **Interest Rate:** {analysis.get('interest_rate', 0):.2f}%")
            lines.append(f"- **Current Payment:** ${analysis.get('monthly_payment', 0):,.2f}")
            lines.append("")
        
        lines.append("### Available Options")
        lines.append("")
        lines.append("**Income-Driven Repayment (IDR) Plans:**")
        lines.append("- **SAVE Plan:** Most generous for low-income borrowers, 10% of discretionary income")
        lines.append("- **PAYE Plan:** 10% of discretionary income, capped at standard payment")
        lines.append("- **IBR Plan:** 10-15% of discretionary income depending on when loans were taken")
        lines.append("")
        lines.append("**Public Service Loan Forgiveness (PSLF):**")
        lines.append("- Forgiveness after 120 qualifying payments for public service workers")
        lines.append("- Must work for qualifying employer (government, nonprofit, etc.)")
        lines.append("")
        lines.append("**Employer Student Loan Assistance:**")
        lines.append("- Up to $5,250 annually tax-free through 2025")
        lines.append("- Check with your HR department for availability")
        
        return "\n".join(lines)
    
    def _format_budget_creation_answer(self, output: Optional[Dict[str, Any]]) -> str:
        """Format budget creation answer."""
        lines = ["## Budget Creation Guide"]
        lines.append("")
        
        if output and "budget" in output:
            budget = output["budget"]
            framework = budget.get("framework", "50/30/20")
            
            if framework == "50/30/20":
                lines.append("### 50/30/20 Budget Framework")
                lines.append("")
                lines.append("**Allocation:**")
                lines.append(f"- **Needs (50%):** ${budget.get('needs', 0):,.2f}")
                lines.append(f"- **Wants (30%):** ${budget.get('wants', 0):,.2f}")
                lines.append(f"- **Savings/Debt (20%):** ${budget.get('savings_debt', 0):,.2f}")
                lines.append("")
                lines.append("**What counts as Needs:**")
                lines.append("- Housing (rent/mortgage, utilities)")
                lines.append("- Food (groceries, not dining out)")
                lines.append("- Transportation (essential only)")
                lines.append("- Insurance (health, auto, home)")
                lines.append("- Minimum debt payments")
                lines.append("")
                lines.append("**What counts as Wants:**")
                lines.append("- Dining out, entertainment, hobbies")
                lines.append("- Non-essential shopping")
                lines.append("- Subscription services")
                lines.append("")
                lines.append("**Savings/Debt:**")
                lines.append("- Emergency fund contributions")
                lines.append("- Extra debt payments")
                lines.append("- Retirement savings")
        
        return "\n".join(lines)
    
    def _format_spending_reduction_answer(self, output: Optional[Dict[str, Any]]) -> str:
        """Format spending reduction answer."""
        lines = ["## Spending Reduction Strategies"]
        lines.append("")
        lines.append("Here are high-impact, sustainable ways to reduce spending:")
        lines.append("")
        lines.append("### Quick Wins (Easy to Implement)")
        lines.append("1. **Cancel unused subscriptions** - Review all recurring charges")
        lines.append("2. **Reduce dining out** - Set a monthly budget and meal prep")
        lines.append("3. **Shop insurance rates** - Compare quotes annually")
        lines.append("4. **Use cash-back apps** - Earn money back on purchases")
        lines.append("")
        lines.append("### Medium Impact (Requires Some Effort)")
        lines.append("1. **Negotiate bills** - Call providers to lower rates")
        lines.append("2. **Reduce utility costs** - Energy-efficient upgrades")
        lines.append("3. **Find free entertainment** - Libraries, parks, community events")
        lines.append("4. **Buy generic brands** - Often same quality, lower price")
        lines.append("")
        lines.append("### High Impact (Lifestyle Adjustments)")
        lines.append("1. **Downsize housing** - If possible, move to lower-cost area")
        lines.append("2. **Reduce transportation costs** - Use public transit, carpool")
        lines.append("3. **Cook at home more** - Significantly cheaper than dining out")
        lines.append("4. **Delay non-essential purchases** - Use 24-hour rule")
        
        return "\n".join(lines)
    
    def _format_debt_consolidation_answer(self, output: Optional[Dict[str, Any]]) -> str:
        """Format debt consolidation answer."""
        lines = ["## Debt Consolidation Analysis"]
        lines.append("")
        lines.append("Debt consolidation can simplify payments and potentially lower interest rates.")
        lines.append("")
        lines.append("### When Consolidation Makes Sense:")
        lines.append("- You have 3+ debts with varying interest rates")
        lines.append("- You can get a consolidation loan with lower weighted average rate")
        lines.append("- You're disciplined enough to avoid new debt")
        lines.append("")
        lines.append("### Options to Consider:")
        lines.append("1. **Personal Loan:** Typically 6-12% APR, fixed rate, fixed term")
        lines.append("2. **Balance Transfer Card:** 0% APR for 12-18 months (then higher rate)")
        lines.append("3. **Home Equity Loan:** Lower rates but uses home as collateral")
        lines.append("")
        lines.append("### Important Considerations:")
        lines.append("- Calculate total cost including fees")
        lines.append("- Ensure new rate is lower than current weighted average")
        lines.append("- Avoid closing old accounts immediately (can hurt credit)")
        lines.append("- Have a plan to pay off before promotional rate expires")
        
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
        
        if intent_type == "debt_payoff_strategy":
            lines.append("1. List all your debts with balances, interest rates, and minimum payments")
            lines.append("2. Calculate total available for debt repayment each month")
            lines.append("3. Choose your strategy (Avalanche or Snowball) and stick to it")
            lines.append("4. Set up automatic payments to ensure consistency")
            lines.append("5. Track progress monthly and celebrate milestones")
        elif intent_type == "student_loan_management":
            lines.append("1. Verify your loan type (federal vs. private)")
            lines.append("2. Research IDR plans if your income is low relative to debt")
            lines.append("3. Check PSLF eligibility if you work in public service")
            lines.append("4. Ask HR about employer student loan assistance programs")
            lines.append("5. Compare refinancing options if you have high-rate private loans")
        elif intent_type == "budget_creation":
            lines.append("1. Calculate your total monthly income (after taxes)")
            lines.append("2. List all fixed expenses (rent, utilities, insurance)")
            lines.append("3. Track variable expenses for one month")
            lines.append("4. Apply your chosen budgeting framework")
            lines.append("5. Review and adjust monthly")
        elif intent_type == "spending_reduction":
            lines.append("1. Track all spending for 30 days to identify patterns")
            lines.append("2. Categorize expenses as needs vs. wants")
            lines.append("3. Identify top 3-5 reduction opportunities")
            lines.append("4. Set specific spending limits for each category")
            lines.append("5. Review progress weekly and adjust as needed")
        else:
            lines.append("1. Provide more details about your specific financial situation")
            lines.append("2. Review your current debt and spending patterns")
            lines.append("3. Set clear financial goals")
            lines.append("4. Create an action plan with timelines")
        
        return "\n".join(lines)

