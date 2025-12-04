"""
Intent Classification Module for Goal Planner Agent.
Categorizes client questions into appropriate intent types.
"""

from typing import Dict, Any, Optional
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class IntentType(str, Enum):
    """Financial planning intent categories."""
    RETIREMENT_TRACKING = "retirement_tracking"
    SAVINGS_OPTIMIZATION = "savings_optimization"
    GOAL_MANAGEMENT = "goal_management"
    UNKNOWN = "unknown"


class IntentClassifier:
    """Classifies client questions into financial planning intent categories."""
    
    # Keywords for retirement tracking intents
    RETIREMENT_TRACKING_KEYWORDS = [
        "on track", "track for retirement", "retirement track",
        "contributing enough", "401k", "401(k)", "403b", "403(b)",
        "retirement account", "retirement savings", "retirement goal",
        "retirement readiness", "retirement plan", "retirement projection"
    ]
    
    # Keywords for savings optimization intents
    SAVINGS_OPTIMIZATION_KEYWORDS = [
        "save more", "save for retirement", "saving more",
        "how much", "should i put", "contribute", "contribution",
        "hsa", "health savings", "health savings account",
        "maximize", "optimize savings", "increase savings",
        "savings rate", "contribution rate", "contribution limit"
    ]
    
    # Keywords for goal management intents
    GOAL_MANAGEMENT_KEYWORDS = [
        "set a goal", "set goal", "financial goal", "create goal",
        "which goal", "focus on", "prioritize", "goal priority",
        "reach my goal", "achieve goal", "goal faster", "reach goal faster",
        "multiple goals", "goal planning", "goal setting"
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
        
        # Check for retirement tracking intents
        retirement_score = self._score_keywords(
            question_lower, 
            self.RETIREMENT_TRACKING_KEYWORDS
        )
        
        # Check for savings optimization intents
        savings_score = self._score_keywords(
            question_lower,
            self.SAVINGS_OPTIMIZATION_KEYWORDS
        )
        
        # Check for goal management intents
        goal_score = self._score_keywords(
            question_lower,
            self.GOAL_MANAGEMENT_KEYWORDS
        )
        
        # Determine intent with highest score
        scores = {
            IntentType.RETIREMENT_TRACKING: retirement_score,
            IntentType.SAVINGS_OPTIMIZATION: savings_score,
            IntentType.GOAL_MANAGEMENT: goal_score
        }
        
        max_score = max(scores.values())
        intent_type = max(scores, key=scores.get) if max_score > 0 else IntentType.UNKNOWN
        
        # Extract entities
        entities = self._extract_entities(question_lower, intent_type)
        
        return {
            "intent_type": intent_type.value,
            "confidence": min(max_score / 3.0, 1.0),  # Normalize confidence
            "entities": entities,
            "raw_question": question
        }
    
    def _score_keywords(self, text: str, keywords: list) -> float:
        """Score text based on keyword matches."""
        score = 0.0
        for keyword in keywords:
            if keyword in text:
                # Longer keywords get higher weight
                score += len(keyword.split()) * 0.5
        return score
    
    def _extract_entities(self, question: str, intent_type: IntentType) -> Dict[str, Any]:
        """Extract relevant entities from the question."""
        entities = {}
        
        if intent_type == IntentType.RETIREMENT_TRACKING:
            # Extract account types
            if "401k" in question or "401(k)" in question:
                entities["account_type"] = "401k"
            elif "403b" in question or "403(b)" in question:
                entities["account_type"] = "403b"
            elif "ira" in question:
                entities["account_type"] = "ira"
            elif "retirement" in question:
                entities["account_type"] = "retirement_account"
        
        elif intent_type == IntentType.SAVINGS_OPTIMIZATION:
            # Extract account types
            if "hsa" in question or "health savings" in question:
                entities["account_type"] = "hsa"
            elif "401k" in question or "401(k)" in question:
                entities["account_type"] = "401k"
            elif "ira" in question:
                entities["account_type"] = "ira"
            elif "retirement" in question:
                entities["account_type"] = "retirement_account"
        
        elif intent_type == IntentType.GOAL_MANAGEMENT:
            # Extract goal-related terms
            if "first" in question or "prioritize" in question:
                entities["action"] = "prioritize"
            elif "faster" in question or "reach" in question:
                entities["action"] = "accelerate"
            elif "set" in question or "create" in question:
                entities["action"] = "create"
        
        return entities

