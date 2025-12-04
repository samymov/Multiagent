"""
Response Generation Module for Goal Planner Agent.
Translates technical outputs from estimators and rules into clear, actionable client-facing guidance.
"""

from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)


class ResponseGenerator:
    """Generates client-facing responses from estimator outputs and advice rules."""
    
    def generate_response(
        self,
        intent_type: str,
        intent_data: Dict[str, Any],
        estimator_output: Dict[str, Any],
        advice: List[Dict[str, Any]]
    ) -> str:
        """
        Generate a comprehensive response for the client.
        
        Args:
            intent_type: The classified intent type
            intent_data: Intent classification data (confidence, entities, etc.)
            estimator_output: Output from relevant estimator
            advice: List of advice recommendations
            
        Returns:
            Formatted response string
        """
        response_parts = []
        
        # Add personalized greeting
        response_parts.append(self._generate_greeting(intent_type, intent_data))
        
        # Add main analysis/answer
        response_parts.append(self._generate_main_answer(intent_type, estimator_output))
        
        # Add specific recommendations
        if advice:
            response_parts.append(self._format_advice(advice))
        
        # Add next steps
        response_parts.append(self._generate_next_steps(intent_type))
        
        return "\n\n".join(response_parts)
    
    def _generate_greeting(self, intent_type: str, intent_data: Dict[str, Any]) -> str:
        """Generate a personalized greeting based on intent."""
        question = intent_data.get("raw_question", "")
        
        if intent_type == "retirement_tracking":
            return f"Great question! Let me help you understand your retirement readiness. Based on your question: *{question}*"
        elif intent_type == "savings_optimization":
            return f"I'd be happy to help you optimize your savings! Regarding your question: *{question}*"
        elif intent_type == "goal_management":
            return f"Excellent! Let's work on your financial goals. You asked: *{question}*"
        else:
            return f"Thank you for your question. Let me help you with: *{question}*"
    
    def _generate_main_answer(self, intent_type: str, estimator_output: Dict[str, Any]) -> str:
        """Generate the main answer based on intent type and estimator output."""
        if intent_type == "retirement_tracking":
            return self._format_retirement_tracking_answer(estimator_output)
        elif intent_type == "savings_optimization":
            return self._format_savings_optimization_answer(estimator_output)
        elif intent_type == "goal_management":
            return self._format_goal_management_answer(estimator_output)
        else:
            return "I understand your question. Let me provide some general guidance based on your financial situation."
    
    def _format_retirement_tracking_answer(self, output: Dict[str, Any]) -> str:
        """Format retirement tracking answer."""
        lines = ["## Your Retirement Readiness"]
        
        on_track = output.get("on_track", False)
        portfolio_value = output.get("current_portfolio_value", 0)
        expected_value = output.get("expected_value_at_retirement", 0)
        projected_income = output.get("projected_annual_income", 0)
        target_income = output.get("target_annual_income", 0)
        success_prob = output.get("success_probability", 0)
        
        if on_track:
            lines.append(f"✅ **Good news!** You're on track for retirement.")
        else:
            gap = output.get("income_gap", 0)
            lines.append(f"⚠️ **Action needed:** You have a projected income gap of ${gap:,.0f} per year.")
        
        lines.append("")
        lines.append("### Current Situation")
        lines.append(f"- **Current Portfolio Value:** ${portfolio_value:,.0f}")
        lines.append(f"- **Expected Value at Retirement:** ${expected_value:,.0f}")
        lines.append(f"- **Projected Annual Income:** ${projected_income:,.0f}")
        lines.append(f"- **Target Annual Income:** ${target_income:,.0f}")
        lines.append(f"- **Success Probability:** {success_prob:.0f}%")
        
        # 401k specific analysis
        if "401k_analysis" in output:
            analysis = output["401k_analysis"]
            lines.append("")
            lines.append("### 401k Contribution Analysis")
            lines.append(f"- **Current Contribution:** ${analysis.get('current_estimated_contribution', 0):,.0f}")
            lines.append(f"- **Recommended Contribution:** ${analysis.get('recommended_contribution', 0):,.0f}")
            lines.append(f"- **Maximum Contribution Limit:** ${analysis.get('max_contribution_limit', 0):,.0f}")
            
            if not analysis.get("is_contributing_enough", False):
                gap = analysis.get("gap", 0)
                lines.append(f"- **Contribution Gap:** ${gap:,.0f} per year")
        
        return "\n".join(lines)
    
    def _format_savings_optimization_answer(self, output: Dict[str, Any]) -> str:
        """Format savings optimization answer."""
        lines = ["## Savings Optimization Analysis"]
        
        # HSA analysis
        if "hsa_analysis" in output:
            hsa = output["hsa_analysis"]
            lines.append("### Health Savings Account (HSA)")
            lines.append(f"- **Maximum Contribution Limit:** ${hsa.get('max_contribution_limit', 4150):,.0f}")
            lines.append(f"- **Recommended Contribution:** ${hsa.get('recommended_contribution', 4150):,.0f}")
            lines.append(f"- **Reason:** {hsa.get('reason', '')}")
            lines.append("")
        
        # General savings optimization
        if "savings_optimization" in output:
            savings = output["savings_optimization"]
            lines.append("### How to Save More for Retirement")
            lines.append(f"- **Current Annual Contribution:** ${savings.get('current_annual_contribution', 0):,.0f}")
            lines.append(f"- **Required Annual Contribution:** ${savings.get('required_annual_contribution', 0):,.0f}")
            
            gap = savings.get("contribution_gap", 0)
            if gap > 0:
                lines.append(f"- **Recommended Increase:** ${gap:,.0f} per year")
                lines.append("")
                lines.append("### Strategies to Increase Savings:")
                for strategy in savings.get("strategies", []):
                    lines.append(f"- {strategy}")
        
        return "\n".join(lines)
    
    def _format_goal_management_answer(self, output: Dict[str, Any]) -> str:
        """Format goal management answer."""
        lines = ["## Financial Goal Management"]
        lines.append("")
        lines.append("Here's a framework for effectively managing your financial goals:")
        lines.append("")
        lines.append("### Goal Prioritization Framework")
        lines.append("1. **Emergency Fund** (3-6 months expenses) - Build this first")
        lines.append("2. **High-Interest Debt** - Pay off credit cards and high-rate loans")
        lines.append("3. **Employer Match** - Don't leave free money on the table")
        lines.append("4. **Retirement Savings** - Beyond employer match")
        lines.append("5. **Other Goals** - House, education, major purchases")
        lines.append("")
        lines.append("### Tips for Success")
        lines.append("- Focus on 2-3 primary goals at a time")
        lines.append("- Automate contributions to each goal")
        lines.append("- Review and adjust quarterly")
        lines.append("- Celebrate milestones along the way")
        
        return "\n".join(lines)
    
    def _format_advice(self, advice: List[Dict[str, Any]]) -> str:
        """Format advice recommendations."""
        lines = ["## Recommendations"]
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
        
        if intent_type == "retirement_tracking":
            lines.append("1. Review your current contribution rate and consider increasing it")
            lines.append("2. Check if you're maximizing employer match")
            lines.append("3. Review your portfolio allocation for optimization")
            lines.append("4. Consider consulting with a financial advisor for personalized planning")
        elif intent_type == "savings_optimization":
            lines.append("1. Set up automatic contribution increases")
            lines.append("2. Review all available tax-advantaged accounts")
            lines.append("3. Create a budget to identify additional savings opportunities")
            lines.append("4. Track your progress monthly")
        elif intent_type == "goal_management":
            lines.append("1. Write down your top 3 financial goals")
            lines.append("2. Set specific, measurable targets for each goal")
            lines.append("3. Create an action plan with timelines")
            lines.append("4. Set up automated savings for each goal")
        else:
            lines.append("1. Provide more details about your specific financial situation")
            lines.append("2. Review your current financial goals")
            lines.append("3. Consider scheduling a consultation for personalized advice")
        
        return "\n".join(lines)

