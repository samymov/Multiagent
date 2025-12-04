"""
Advice Rule Engine for Goal Planner Agent.
Applies existing advice rules based on client intent, financial profile, and estimator outputs.
"""

from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)


class AdviceRuleEngine:
    """Applies financial advice rules based on client situation and estimator outputs."""
    
    def __init__(self, user_data: Optional[Dict[str, Any]] = None):
        """
        Initialize advice rule engine.
        
        Args:
            user_data: User profile data
        """
        self.user_data = user_data or {}
    
    def apply_retirement_tracking_rules(
        self, 
        estimator_output: Dict[str, Any],
        entities: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Apply advice rules for retirement tracking intents.
        
        Args:
            estimator_output: Output from retirement readiness estimator
            entities: Extracted entities from intent classification
            
        Returns:
            List of advice recommendations
        """
        advice = []
        
        # Rule 1: On-track assessment
        if estimator_output.get("on_track", False):
            advice.append({
                "priority": "high",
                "category": "status",
                "title": "You're on track for retirement!",
                "message": f"Based on your current savings and projections, you're on track to meet your retirement income goal of ${estimator_output.get('target_annual_income', 0):,.0f}.",
                "action_items": [
                    "Continue your current contribution rate",
                    "Review your portfolio allocation annually",
                    "Consider increasing contributions if you receive a raise"
                ]
            })
        else:
            gap = estimator_output.get("income_gap", 0)
            advice.append({
                "priority": "high",
                "category": "gap_analysis",
                "title": "Action needed to meet retirement goal",
                "message": f"You have a projected income gap of ${gap:,.0f} per year. You'll need to increase your savings to meet your retirement goal.",
                "action_items": [
                    f"Increase annual contributions by ${estimator_output.get('required_annual_contribution', 0) - estimator_output.get('current_annual_contribution', 0):,.0f}",
                    "Consider maximizing employer match if available",
                    "Review and optimize your investment allocation"
                ]
            })
        
        # Rule 2: Success probability assessment
        success_prob = estimator_output.get("success_probability", 0)
        if success_prob < 50:
            advice.append({
                "priority": "critical",
                "category": "risk_mitigation",
                "title": "Low success probability - immediate action needed",
                "message": f"Your current plan has a {success_prob:.0f}% probability of success. Significant adjustments are needed.",
                "action_items": [
                    "Increase savings rate by at least 20%",
                    "Consider working 2-3 years longer",
                    "Review target retirement income for feasibility",
                    "Consult with a financial advisor"
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
                    "Consider catch-up contributions if over 50"
                ]
            })
        
        # Rule 3: Account-specific advice (401k)
        if entities.get("account_type") == "401k":
            contribution_analysis = estimator_output.get("401k_analysis", {})
            if contribution_analysis.get("percentage_of_max", 0) < 80:
                advice.append({
                    "priority": "medium",
                    "category": "contribution_optimization",
                    "title": "Maximize your 401k contributions",
                    "message": f"You're currently contributing {contribution_analysis.get('percentage_of_max', 0):.0f}% of the maximum. Consider increasing to maximize tax benefits.",
                    "action_items": [
                        f"Increase 401k contribution to ${contribution_analysis.get('recommended_contribution', 0):,.0f} annually",
                        "Take advantage of employer match if available",
                        "Consider automatic contribution increases"
                    ]
                })
        
        return advice
    
    def apply_savings_optimization_rules(
        self,
        estimator_output: Dict[str, Any],
        entities: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Apply advice rules for savings optimization intents.
        
        Args:
            estimator_output: Output from savings optimization estimator
            entities: Extracted entities from intent classification
            
        Returns:
            List of advice recommendations
        """
        advice = []
        
        # Rule 1: HSA-specific advice
        if entities.get("account_type") == "hsa":
            hsa_info = estimator_output.get("hsa_analysis", {})
            if not hsa_info.get("has_hsa_account", False):
                advice.append({
                    "priority": "high",
                    "category": "account_setup",
                    "title": "Consider opening an HSA",
                    "message": "Health Savings Accounts offer triple tax advantages and can be a powerful retirement savings tool.",
                    "action_items": [
                        "Check if you're eligible for an HSA (requires high-deductible health plan)",
                        "Open an HSA if eligible",
                        f"Contribute up to ${hsa_info.get('max_contribution_limit', 4150):,.0f} annually"
                    ]
                })
            else:
                advice.append({
                    "priority": "medium",
                    "category": "contribution_optimization",
                    "title": "Maximize your HSA contributions",
                    "message": f"Consider contributing the maximum ${hsa_info.get('max_contribution_limit', 4150):,.0f} to your HSA for maximum tax benefits.",
                    "action_items": [
                        f"Increase HSA contribution to ${hsa_info.get('recommended_contribution', 4150):,.0f}",
                        "Use HSA as a retirement savings vehicle by paying medical expenses out of pocket",
                        "Invest HSA funds for long-term growth"
                    ]
                })
        
        # Rule 2: General savings increase
        savings_analysis = estimator_output.get("savings_optimization", {})
        gap = savings_analysis.get("contribution_gap", 0)
        
        if gap > 0:
            advice.append({
                "priority": "high",
                "category": "savings_increase",
                "title": "Increase your retirement savings",
                "message": f"To meet your retirement goals, you should increase annual savings by ${gap:,.0f}.",
                "action_items": savings_analysis.get("strategies", [])
            })
        else:
            advice.append({
                "priority": "low",
                "category": "maintenance",
                "title": "Your savings rate looks good",
                "message": "You're on track with your savings. Consider these optimization strategies:",
                "action_items": [
                    "Review and maximize all available tax-advantaged accounts",
                    "Consider increasing contributions with each raise",
                    "Automate savings increases"
                ]
            })
        
        return advice
    
    def apply_goal_management_rules(
        self,
        estimator_output: Dict[str, Any],
        entities: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Apply advice rules for goal management intents.
        
        Args:
            estimator_output: Output from goal management estimator
            entities: Extracted entities from intent classification
            
        Returns:
            List of advice recommendations
        """
        advice = []
        
        action = entities.get("action", "")
        
        if action == "prioritize":
            # Rule: Prioritize goals based on urgency and impact
            advice.append({
                "priority": "high",
                "category": "goal_prioritization",
                "title": "Goal prioritization strategy",
                "message": "Prioritize goals based on urgency, impact, and your financial capacity.",
                "action_items": [
                    "1. Emergency fund (3-6 months expenses) - highest priority",
                    "2. High-interest debt payoff - second priority",
                    "3. Employer 401k match - don't leave free money",
                    "4. Retirement savings beyond match",
                    "5. Other financial goals (house, education, etc.)"
                ]
            })
        
        elif action == "accelerate":
            # Rule: Strategies to reach goals faster
            advice.append({
                "priority": "medium",
                "category": "goal_acceleration",
                "title": "Strategies to reach your goals faster",
                "message": "Here are proven strategies to accelerate progress toward your financial goals:",
                "action_items": [
                    "Increase savings rate by 1-2% every 6 months",
                    "Automate savings to pay yourself first",
                    "Reduce expenses and redirect savings to goals",
                    "Consider side income opportunities",
                    "Review and optimize investment fees",
                    "Take advantage of windfalls (bonuses, tax refunds)"
                ]
            })
        
        elif action == "create":
            # Rule: How to set effective financial goals
            advice.append({
                "priority": "high",
                "category": "goal_setting",
                "title": "Setting effective financial goals",
                "message": "Use the SMART framework to set effective financial goals:",
                "action_items": [
                    "Specific: Define exactly what you want to achieve",
                    "Measurable: Set concrete numbers and timelines",
                    "Achievable: Ensure goals are realistic given your income",
                    "Relevant: Align goals with your values and priorities",
                    "Time-bound: Set clear deadlines for each goal"
                ]
            })
        
        else:
            # Default goal management advice
            advice.append({
                "priority": "medium",
                "category": "general_goal_advice",
                "title": "Effective goal management",
                "message": "Here are key principles for managing multiple financial goals:",
                "action_items": [
                    "Focus on 2-3 primary goals at a time",
                    "Automate contributions to each goal",
                    "Review progress quarterly",
                    "Adjust goals as life circumstances change",
                    "Celebrate milestones along the way"
                ]
            })
        
        return advice
    
    def generate_advice(
        self,
        intent_type: str,
        estimator_output: Dict[str, Any],
        entities: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Generate advice based on intent type and estimator output.
        
        Args:
            intent_type: The classified intent type
            estimator_output: Output from relevant estimator
            entities: Extracted entities from intent classification
            
        Returns:
            List of advice recommendations
        """
        if intent_type == "retirement_tracking":
            return self.apply_retirement_tracking_rules(estimator_output, entities)
        elif intent_type == "savings_optimization":
            return self.apply_savings_optimization_rules(estimator_output, entities)
        elif intent_type == "goal_management":
            return self.apply_goal_management_rules(estimator_output, entities)
        else:
            return [{
                "priority": "low",
                "category": "general",
                "title": "General financial advice",
                "message": "I'd be happy to help with your financial planning. Could you provide more details about your specific question?",
                "action_items": []
            }]

