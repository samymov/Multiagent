"""
Goal Planner Agent - Intelligent interface for financial planning queries.
Refactored from tagger agent to handle client financial intents.
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

from agents import Agent, Runner, trace, function_tool, RunContextWrapper
from agents.extensions.models.litellm_model import LitellmModel

from .intent_classifier import IntentClassifier, IntentType
from .estimators import EstimatorIntegration
from .advice_rules import AdviceRuleEngine
from .response_generator import ResponseGenerator

logger = logging.getLogger(__name__)

# Get configuration
BEDROCK_MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "amazon.nova-pro-v1:0")
BEDROCK_REGION = os.getenv("BEDROCK_REGION", "us-east-1")


@dataclass
class GoalPlannerContext:
    """Context for goal planner agent."""
    clerk_user_id: Optional[str] = None
    portfolio_data: Optional[Dict[str, Any]] = None
    user_data: Optional[Dict[str, Any]] = None
    db: Optional[Any] = None


class GoalPlannerAgent:
    """Main goal planner agent that orchestrates intent classification, estimation, and advice."""
    
    def __init__(self, portfolio_data: Optional[Dict[str, Any]] = None,
                 user_data: Optional[Dict[str, Any]] = None,
                 db: Optional[Any] = None):
        """
        Initialize goal planner agent.
        
        Args:
            portfolio_data: User's portfolio data
            user_data: User profile data
            db: Database connection
        """
        self.intent_classifier = IntentClassifier()
        self.estimator = EstimatorIntegration(portfolio_data, user_data)
        self.advice_engine = AdviceRuleEngine(user_data)
        self.response_generator = ResponseGenerator()
        self.portfolio_data = portfolio_data or {}
        self.user_data = user_data or {}
        self.db = db
    
    def process_question(self, question: str) -> Dict[str, Any]:
        """
        Process a client question and return comprehensive response.
        
        Args:
            question: Client's financial planning question
            
        Returns:
            Dictionary with response, intent, and metadata
        """
        try:
            # Step 1: Classify intent
            intent_data = self.intent_classifier.classify(question)
            intent_type = intent_data["intent_type"]
            entities = intent_data.get("entities", {})
            
            logger.info(f"Classified intent: {intent_type} with confidence {intent_data.get('confidence', 0):.2f}")
            
            # Step 2: Get estimator output
            estimator_output = self._get_estimator_output(intent_type, entities)
            
            # Step 3: Apply advice rules
            advice = self.advice_engine.generate_advice(intent_type, estimator_output, entities)
            
            # Step 4: Generate response
            response = self.response_generator.generate_response(
                intent_type,
                intent_data,
                estimator_output,
                advice
            )
            
            return {
                "success": True,
                "response": response,
                "intent": intent_data,
                "estimator_output": estimator_output,
                "advice": advice
            }
            
        except Exception as e:
            logger.error(f"Error processing question: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "response": self._generate_error_response(question)
            }
    
    def _get_estimator_output(self, intent_type: str, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Get output from relevant estimator based on intent type."""
        output = {}
        
        if intent_type == "retirement_tracking":
            output["retirement_readiness"] = self.estimator.estimate_retirement_readiness()
            
            # Add 401k analysis if relevant
            if entities.get("account_type") in ["401k", "401(k)", "403b", "403(b)"]:
                output["401k_analysis"] = self.estimator.estimate_401k_contribution_adequacy()
        
        elif intent_type == "savings_optimization":
            output["savings_optimization"] = self.estimator.estimate_savings_optimization()
            
            # Add HSA analysis if relevant
            if entities.get("account_type") == "hsa":
                output["hsa_analysis"] = self.estimator.estimate_hsa_contribution()
        
        elif intent_type == "goal_management":
            # For goal management, we still need retirement context
            output["retirement_readiness"] = self.estimator.estimate_retirement_readiness()
            output["savings_optimization"] = self.estimator.estimate_savings_optimization()
        
        return output
    
    def _generate_error_response(self, question: str) -> str:
        """Generate fallback error response."""
        return f"""I apologize, but I encountered an issue processing your question: *{question}*

This could be due to:
- Missing financial data needed for analysis
- Unclear intent in your question
- Technical issues

**What you can do:**
1. Try rephrasing your question with more specific details
2. Ensure your portfolio and profile data are up to date
3. Contact support if the issue persists

I'm here to help with:
- Retirement tracking and planning
- Savings optimization strategies
- Financial goal setting and management

Please try asking your question again with more context."""


@function_tool
async def answer_financial_question(
    wrapper: RunContextWrapper[GoalPlannerContext],
    question: str
) -> str:
    """
    Answer a client's financial planning question using intent classification,
    estimators, and advice rules.
    
    Args:
        question: The client's financial planning question
        
    Returns:
        Comprehensive answer with analysis and recommendations
    """
    if not wrapper.context.portfolio_data or not wrapper.context.user_data:
        return "Error: Portfolio and user data required to answer financial questions. Please ensure your profile is complete."
    
    agent = GoalPlannerAgent(
        portfolio_data=wrapper.context.portfolio_data,
        user_data=wrapper.context.user_data,
        db=wrapper.context.db
    )
    
    result = agent.process_question(question)
    
    if result.get("success"):
        return result.get("response", "I couldn't generate a response. Please try rephrasing your question.")
    else:
        return result.get("response", "I encountered an error processing your question. Please try again.")


def create_goal_planner_agent(
    clerk_user_id: str,
    portfolio_data: Dict[str, Any],
    user_data: Dict[str, Any],
    db: Optional[Any] = None
) -> tuple:
    """
    Create the goal planner agent with tools and context.
    
    Args:
        clerk_user_id: User's Clerk ID
        portfolio_data: User's portfolio data
        user_data: User profile data
        db: Database connection
        
    Returns:
        Tuple of (model, tools, task, context)
    """
    # Set up model
    model_id = BEDROCK_MODEL_ID
    if model_id.startswith("us."):
        model_id = model_id[3:]
        logger.info(f"Goal Planner: Removed us. prefix from model ID, now: {model_id}")
    
    bedrock_region = BEDROCK_REGION
    os.environ["AWS_REGION_NAME"] = bedrock_region
    os.environ["AWS_REGION"] = bedrock_region
    os.environ["AWS_DEFAULT_REGION"] = bedrock_region
    
    model = LitellmModel(model=f"bedrock/{model_id}")
    
    # Create context
    context = GoalPlannerContext(
        clerk_user_id=clerk_user_id,
        portfolio_data=portfolio_data,
        user_data=user_data,
        db=db
    )
    
    # Tools
    tools = [answer_financial_question]
    
    # Task
    task = """You are a Goal Planning Agent that helps clients with their financial planning questions.

You can help with:
1. Retirement Tracking: "Am I on track for retirement?", "Am I contributing enough to my 401k?"
2. Savings Optimization: "How can I save more for retirement?", "How much should I put in my HSA?"
3. Goal Management: "Help me set a financial goal", "Which goal should I focus on first?", "How can I reach my goal faster?"

When a client asks a question:
1. Use the answer_financial_question tool to get a comprehensive analysis
2. Present the information clearly and actionably
3. Be specific with numbers and timelines
4. Provide personalized recommendations based on their situation

Be warm, professional, and focused on helping the client achieve their financial goals."""

    return model, tools, task, context

