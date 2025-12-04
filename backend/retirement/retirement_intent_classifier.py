"""
Intent Classification for Retirement Planning Agent.
Categorizes client questions into retirement planning intent types.
"""

from typing import Dict, Any
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class RetirementIntentType(str, Enum):
    """Retirement planning intent categories."""
    SAVINGS_STRATEGY = "savings_strategy"
    INVESTMENT_ALLOCATION = "investment_allocation"
    WITHDRAWAL_PLANNING = "withdrawal_planning"
    TAX_OPTIMIZATION = "tax_optimization"
    HEALTHCARE_COSTS = "healthcare_costs"
    SOCIAL_SECURITY = "social_security"
    ESTATE_PLANNING = "estate_planning"
    LIFESTYLE_ADJUSTMENTS = "lifestyle_adjustments"
    RETIREMENT_READINESS = "retirement_readiness"
    RETIREMENT_INCOME = "retirement_income"
    UNKNOWN = "unknown"


class RetirementIntentClassifier:
    """Classifies client questions into retirement planning intent categories."""
    
    # Keywords for savings strategy
    SAVINGS_STRATEGY_KEYWORDS = [
        "save for retirement", "retirement savings", "how much to save",
        "contribution", "401k", "403b", "ira", "roth", "catch-up",
        "maximize savings", "savings rate", "retirement account"
    ]
    
    # Keywords for investment allocation
    INVESTMENT_ALLOCATION_KEYWORDS = [
        "asset allocation", "portfolio allocation", "investment mix",
        "stocks vs bonds", "equity allocation", "bond allocation",
        "diversification", "rebalance", "target date fund"
    ]
    
    # Keywords for withdrawal planning
    WITHDRAWAL_PLANNING_KEYWORDS = [
        "withdrawal", "withdraw from retirement", "4% rule", "safe withdrawal",
        "retirement income", "spending in retirement", "drawdown strategy",
        "rmd", "required minimum distribution"
    ]
    
    # Keywords for tax optimization
    TAX_OPTIMIZATION_KEYWORDS = [
        "tax", "taxable", "tax-free", "tax bracket", "tax efficient",
        "roth conversion", "tax-deferred", "capital gains", "tax planning"
    ]
    
    # Keywords for healthcare costs
    HEALTHCARE_COSTS_KEYWORDS = [
        "healthcare", "medicare", "medicaid", "health insurance",
        "long-term care", "hsa", "health savings", "medical costs"
    ]
    
    # Keywords for Social Security
    SOCIAL_SECURITY_KEYWORDS = [
        "social security", "ssa", "benefits", "claiming strategy",
        "when to claim", "full retirement age", "delayed credits",
        "spousal benefits", "survivor benefits"
    ]
    
    # Keywords for estate planning
    ESTATE_PLANNING_KEYWORDS = [
        "estate", "inheritance", "beneficiary", "will", "trust",
        "estate tax", "gift tax", "legacy", "passing on wealth"
    ]
    
    # Keywords for lifestyle adjustments
    LIFESTYLE_ADJUSTMENTS_KEYWORDS = [
        "lifestyle", "retirement lifestyle", "spending habits",
        "retirement activities", "purpose in retirement", "retirement transition"
    ]
    
    # Keywords for retirement readiness
    RETIREMENT_READINESS_KEYWORDS = [
        "ready to retire", "retirement readiness", "on track",
        "enough to retire", "can i retire", "retirement goal"
    ]
    
    # Keywords for retirement income
    RETIREMENT_INCOME_KEYWORDS = [
        "retirement income", "income in retirement", "pension",
        "annuity", "income sources", "retirement paycheck"
    ]
    
    def classify(self, question: str) -> Dict[str, Any]:
        """
        Classify a client question into an intent category.
        
        Args:
            question: The client's question or statement
            
        Returns:
            Dictionary with intent_type, confidence, and extracted entities
        """
        question_lower = question.lower().strip()
        
        # Score each intent category
        scores = {
            RetirementIntentType.SAVINGS_STRATEGY: self._score_keywords(
                question_lower, self.SAVINGS_STRATEGY_KEYWORDS
            ),
            RetirementIntentType.INVESTMENT_ALLOCATION: self._score_keywords(
                question_lower, self.INVESTMENT_ALLOCATION_KEYWORDS
            ),
            RetirementIntentType.WITHDRAWAL_PLANNING: self._score_keywords(
                question_lower, self.WITHDRAWAL_PLANNING_KEYWORDS
            ),
            RetirementIntentType.TAX_OPTIMIZATION: self._score_keywords(
                question_lower, self.TAX_OPTIMIZATION_KEYWORDS
            ),
            RetirementIntentType.HEALTHCARE_COSTS: self._score_keywords(
                question_lower, self.HEALTHCARE_COSTS_KEYWORDS
            ),
            RetirementIntentType.SOCIAL_SECURITY: self._score_keywords(
                question_lower, self.SOCIAL_SECURITY_KEYWORDS
            ),
            RetirementIntentType.ESTATE_PLANNING: self._score_keywords(
                question_lower, self.ESTATE_PLANNING_KEYWORDS
            ),
            RetirementIntentType.LIFESTYLE_ADJUSTMENTS: self._score_keywords(
                question_lower, self.LIFESTYLE_ADJUSTMENTS_KEYWORDS
            ),
            RetirementIntentType.RETIREMENT_READINESS: self._score_keywords(
                question_lower, self.RETIREMENT_READINESS_KEYWORDS
            ),
            RetirementIntentType.RETIREMENT_INCOME: self._score_keywords(
                question_lower, self.RETIREMENT_INCOME_KEYWORDS
            )
        }
        
        max_score = max(scores.values())
        intent_type = max(scores, key=scores.get) if max_score > 0 else RetirementIntentType.UNKNOWN
        
        # Extract entities
        entities = self._extract_entities(question_lower, intent_type)
        
        return {
            "intent_type": intent_type.value,
            "confidence": min(max_score / 3.0, 1.0),
            "entities": entities,
            "raw_question": question
        }
    
    def _score_keywords(self, text: str, keywords: list) -> float:
        """Score text based on keyword matches."""
        score = 0.0
        for keyword in keywords:
            if keyword in text:
                score += len(keyword.split()) * 0.5
        return score
    
    def _extract_entities(self, question: str, intent_type: RetirementIntentType) -> Dict[str, Any]:
        """Extract relevant entities from the question."""
        entities = {}
        
        if intent_type == RetirementIntentType.SAVINGS_STRATEGY:
            if "401k" in question or "401(k)" in question:
                entities["account_type"] = "401k"
            elif "403b" in question or "403(b)" in question:
                entities["account_type"] = "403b"
            elif "ira" in question:
                if "roth" in question:
                    entities["account_type"] = "roth_ira"
                else:
                    entities["account_type"] = "ira"
            elif "roth" in question:
                entities["account_type"] = "roth"
        
        elif intent_type == RetirementIntentType.SOCIAL_SECURITY:
            if "claim" in question or "claiming" in question:
                entities["action"] = "claiming_strategy"
            if "spousal" in question:
                entities["benefit_type"] = "spousal"
            if "survivor" in question:
                entities["benefit_type"] = "survivor"
        
        elif intent_type == RetirementIntentType.TAX_OPTIMIZATION:
            if "roth conversion" in question or "convert" in question:
                entities["action"] = "roth_conversion"
            if "rmd" in question or "required minimum" in question:
                entities["action"] = "rmd_planning"
        
        elif intent_type == RetirementIntentType.WITHDRAWAL_PLANNING:
            if "4% rule" in question or "four percent" in question:
                entities["rule_mentioned"] = "4_percent_rule"
            if "rmd" in question:
                entities["rmd_mentioned"] = True
        
        return entities

