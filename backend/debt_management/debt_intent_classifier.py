"""
Intent Classification for Debt Management Agent.
Categorizes client questions into debt management intent types.
"""

from typing import Dict, Any
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class DebtIntentType(str, Enum):
    """Debt management intent categories."""
    DEBT_PAYOFF_STRATEGY = "debt_payoff_strategy"
    STUDENT_LOAN_MANAGEMENT = "student_loan_management"
    BUDGET_CREATION = "budget_creation"
    SPENDING_REDUCTION = "spending_reduction"
    DEBT_CONSOLIDATION = "debt_consolidation"
    UNKNOWN = "unknown"


class DebtIntentClassifier:
    """Classifies client questions into debt management intent categories."""
    
    # Keywords for debt payoff strategy
    DEBT_PAYOFF_KEYWORDS = [
        "pay off debt", "debt payoff", "payoff strategy", "debt strategy",
        "avalanche", "snowball", "which debt", "prioritize debt",
        "debt free", "eliminate debt", "get out of debt"
    ]
    
    # Keywords for student loan management
    STUDENT_LOAN_KEYWORDS = [
        "student loan", "student debt", "federal loan", "private loan",
        "income-driven", "idr", "save plan", "paye", "ibr", "repaye",
        "pslf", "public service", "loan forgiveness", "refinance student",
        "employer student loan", "student loan benefit"
    ]
    
    # Keywords for budget creation
    BUDGET_CREATION_KEYWORDS = [
        "create budget", "make budget", "budget", "budgeting",
        "50/30/20", "zero-based", "envelope system", "budget framework",
        "monthly budget", "budget plan"
    ]
    
    # Keywords for spending reduction
    SPENDING_REDUCTION_KEYWORDS = [
        "reduce spending", "cut expenses", "save money", "spending less",
        "reduce costs", "lower expenses", "spending reduction",
        "spending habits", "overspending"
    ]
    
    # Keywords for debt consolidation
    DEBT_CONSOLIDATION_KEYWORDS = [
        "consolidate debt", "debt consolidation", "combine debt",
        "balance transfer", "debt refinance", "single payment"
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
            DebtIntentType.DEBT_PAYOFF_STRATEGY: self._score_keywords(
                question_lower, self.DEBT_PAYOFF_KEYWORDS
            ),
            DebtIntentType.STUDENT_LOAN_MANAGEMENT: self._score_keywords(
                question_lower, self.STUDENT_LOAN_KEYWORDS
            ),
            DebtIntentType.BUDGET_CREATION: self._score_keywords(
                question_lower, self.BUDGET_CREATION_KEYWORDS
            ),
            DebtIntentType.SPENDING_REDUCTION: self._score_keywords(
                question_lower, self.SPENDING_REDUCTION_KEYWORDS
            ),
            DebtIntentType.DEBT_CONSOLIDATION: self._score_keywords(
                question_lower, self.DEBT_CONSOLIDATION_KEYWORDS
            )
        }
        
        max_score = max(scores.values())
        intent_type = max(scores, key=scores.get) if max_score > 0 else DebtIntentType.UNKNOWN
        
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
    
    def _extract_entities(self, question: str, intent_type: DebtIntentType) -> Dict[str, Any]:
        """Extract relevant entities from the question."""
        entities = {}
        
        if intent_type == DebtIntentType.DEBT_PAYOFF_STRATEGY:
            if "avalanche" in question:
                entities["method_mentioned"] = "avalanche"
            elif "snowball" in question:
                entities["method_mentioned"] = "snowball"
        
        elif intent_type == DebtIntentType.STUDENT_LOAN_MANAGEMENT:
            if "federal" in question:
                entities["loan_type"] = "federal"
            elif "private" in question:
                entities["loan_type"] = "private"
            
            if "save" in question or "save plan" in question:
                entities["plan_mentioned"] = "SAVE"
            elif "paye" in question:
                entities["plan_mentioned"] = "PAYE"
            elif "ibr" in question:
                entities["plan_mentioned"] = "IBR"
            elif "pslf" in question or "public service" in question:
                entities["forgiveness_program"] = "PSLF"
            elif "employer" in question or "benefit" in question:
                entities["benefit_type"] = "employer_assistance"
        
        elif intent_type == DebtIntentType.BUDGET_CREATION:
            if "50/30/20" in question or "50 30 20" in question:
                entities["framework_mentioned"] = "50/30/20"
            elif "zero-based" in question or "zero based" in question:
                entities["framework_mentioned"] = "zero-based"
            elif "envelope" in question:
                entities["framework_mentioned"] = "envelope"
        
        return entities

