"""
Retirement Planning Agent - Comprehensive retirement planning advisor.
Handles conversational retirement questions and provides personalized guidance.
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

from agents import Agent, Runner, trace, function_tool, RunContextWrapper
from agents.extensions.models.litellm_model import LitellmModel

from .retirement_intent_classifier import RetirementIntentClassifier, RetirementIntentType
from .retirement_calculators import RetirementCalculator
from .retirement_advice_engine import RetirementAdviceEngine
from .retirement_response_generator import RetirementResponseGenerator

logger = logging.getLogger(__name__)

# Get configuration
BEDROCK_MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "amazon.nova-pro-v1:0")
BEDROCK_REGION = os.getenv("BEDROCK_REGION", "us-east-1")


@dataclass
class RetirementPlanningContext:
    """Context for retirement planning agent."""
    clerk_user_id: Optional[str] = None
    job_id: Optional[str] = None
    portfolio_data: Optional[Dict[str, Any]] = None
    user_data: Optional[Dict[str, Any]] = None
    db: Optional[Any] = None


class RetirementPlanningAgent:
    """Main retirement planning agent that orchestrates intent classification, calculations, and advice."""
    
    def __init__(self, portfolio_data: Optional[Dict[str, Any]] = None,
                 user_data: Optional[Dict[str, Any]] = None,
                 db: Optional[Any] = None):
        """
        Initialize retirement planning agent.
        
        Args:
            portfolio_data: User's portfolio data
            user_data: User profile data
            db: Database connection
        """
        self.intent_classifier = RetirementIntentClassifier()
        self.calculator = RetirementCalculator()
        self.advice_engine = RetirementAdviceEngine(user_data)
        self.response_generator = RetirementResponseGenerator()
        self.portfolio_data = portfolio_data or {}
        self.user_data = user_data or {}
        self.db = db
    
    def process_question(self, question: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process a client question and return comprehensive response.
        
        Args:
            question: Client's retirement planning question
            context: Additional context (age, income, portfolio, etc.)
            
        Returns:
            Dictionary with response, intent, and metadata
        """
        try:
            context = context or {}
            
            # Step 1: Classify intent
            intent_data = self.intent_classifier.classify(question)
            intent_type = intent_data["intent_type"]
            entities = intent_data.get("entities", {})
            
            logger.info(f"Classified intent: {intent_type} with confidence {intent_data.get('confidence', 0):.2f}")
            
            # Step 2: Get calculator output
            calculator_output = self._get_calculator_output(intent_type, context, entities)
            
            # Step 3: Apply advice rules
            advice = self.advice_engine.generate_advice(intent_type, calculator_output, context)
            
            # Step 4: Generate response
            response = self.response_generator.generate_response(
                intent_type,
                intent_data,
                calculator_output,
                advice
            )
            
            return {
                "success": True,
                "response": response,
                "intent": intent_data,
                "calculator_output": calculator_output,
                "advice": advice
            }
            
        except Exception as e:
            logger.error(f"Error processing question: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "response": self._generate_error_response(question)
            }
    
    def _get_calculator_output(self, intent_type: str, context: Dict[str, Any], entities: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get output from relevant calculator based on intent type."""
        output = {}
        
        if intent_type == "retirement_readiness":
            # Calculate retirement readiness
            portfolio_value = self.calculator.calculate_portfolio_value(self.portfolio_data)
            allocation = self.calculator.calculate_asset_allocation(self.portfolio_data)
            
            years_until_retirement = context.get("years_until_retirement", self.user_data.get("years_until_retirement", 30))
            target_income = context.get("target_retirement_income", self.user_data.get("target_retirement_income", 80000))
            annual_contribution = context.get("annual_contribution", 10000)
            social_security = context.get("social_security_benefit", 0)
            pension = context.get("pension_income", 0)
            
            readiness = self.calculator.calculate_retirement_readiness(
                portfolio_value,
                years_until_retirement,
                target_income,
                allocation,
                annual_contribution,
                social_security,
                pension
            )
            output["retirement_readiness"] = readiness
        
        elif intent_type == "social_security":
            # Calculate Social Security benefits
            current_age = context.get("current_age", self.user_data.get("current_age", 65))
            claiming_age = context.get("claiming_age", 67)
            estimated_benefit = context.get("estimated_benefit_at_fra", 0)
            
            if estimated_benefit > 0:
                ss_benefit = self.calculator.calculate_social_security_benefit(
                    current_age,
                    67,  # Full retirement age
                    estimated_benefit,
                    claiming_age
                )
                output["social_security"] = ss_benefit
        
        elif intent_type == "withdrawal_planning":
            # Calculate withdrawal planning
            portfolio_value = self.calculator.calculate_portfolio_value(self.portfolio_data)
            withdrawal_rate = context.get("withdrawal_rate", 0.04)
            
            withdrawal = self.calculator.calculate_safe_withdrawal_rate(
                portfolio_value,
                withdrawal_rate
            )
            output["withdrawal_planning"] = withdrawal
        
        return output if output else None
    
    def _generate_error_response(self, question: str) -> str:
        """Generate fallback error response."""
        return f"""I apologize, but I encountered an issue processing your retirement planning question: *{question}*

This could be due to:
- Missing financial data needed for analysis
- Unclear intent in your question
- Technical issues

**What you can do:**
1. Try rephrasing your question with more specific details
2. Provide information about your age, savings, retirement timeline, and goals
3. Contact support if the issue persists

I'm here to help with:
- Retirement readiness assessment
- Savings strategies and contribution planning
- Investment allocation recommendations
- Social Security claiming strategies
- Withdrawal planning and RMDs
- Tax optimization strategies
- Healthcare and estate planning considerations

Please try asking your question again with more context."""


@function_tool
async def answer_retirement_question(
    wrapper: RunContextWrapper[RetirementPlanningContext],
    question: str,
    current_age: Optional[int] = None,
    years_until_retirement: Optional[int] = None,
    target_retirement_income: Optional[float] = None,
    annual_contribution: Optional[float] = None,
    social_security_benefit: Optional[float] = None,
    pension_income: Optional[float] = None,
    claiming_age: Optional[int] = None,
    withdrawal_rate: Optional[float] = None
) -> str:
    """
    Answer a client's retirement planning question.
    
    Args:
        question: The client's question
        current_age: Optional current age
        years_until_retirement: Optional years until retirement
        target_retirement_income: Optional target annual income in retirement
        annual_contribution: Optional annual contribution amount
        social_security_benefit: Optional estimated Social Security benefit at FRA
        pension_income: Optional pension income
        claiming_age: Optional Social Security claiming age
        withdrawal_rate: Optional withdrawal rate for planning
        
    Returns:
        Comprehensive answer with analysis and recommendations
    """
    context = {
        "current_age": current_age,
        "years_until_retirement": years_until_retirement,
        "target_retirement_income": target_retirement_income,
        "annual_contribution": annual_contribution,
        "social_security_benefit": social_security_benefit,
        "pension_income": pension_income,
        "claiming_age": claiming_age,
        "withdrawal_rate": withdrawal_rate
    }
    
    # Remove None values
    context = {k: v for k, v in context.items() if v is not None}
    
    agent = RetirementPlanningAgent(
        portfolio_data=wrapper.context.portfolio_data,
        user_data=wrapper.context.user_data,
        db=wrapper.context.db
    )
    
    result = agent.process_question(question, context)
    
    if result.get("success"):
        return result.get("response", "I couldn't generate a response. Please try rephrasing your question.")
    else:
        return result.get("response", "I encountered an error processing your question. Please try again.")


def create_retirement_planning_agent(
    clerk_user_id: Optional[str] = None,
    job_id: Optional[str] = None,
    portfolio_data: Optional[Dict[str, Any]] = None,
    user_data: Optional[Dict[str, Any]] = None,
    db: Optional[Any] = None
) -> tuple:
    """
    Create the retirement planning agent with tools and context.
    
    Args:
        clerk_user_id: User's Clerk ID
        job_id: Optional job ID for orchestration mode
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
        logger.info(f"Retirement Planning: Removed us. prefix from model ID, now: {model_id}")
    
    bedrock_region = BEDROCK_REGION
    os.environ["AWS_REGION_NAME"] = bedrock_region
    os.environ["AWS_REGION"] = bedrock_region
    os.environ["AWS_DEFAULT_REGION"] = bedrock_region
    
    model = LitellmModel(model=f"bedrock/{model_id}")
    
    # Create context
    context = RetirementPlanningContext(
        clerk_user_id=clerk_user_id,
        job_id=job_id,
        portfolio_data=portfolio_data or {},
        user_data=user_data or {},
        db=db
    )
    
    # Tools
    tools = [answer_retirement_question]
    
    # Task
    task = """You are a Retirement Planning Agent that helps clients with comprehensive retirement guidance.

You can help with:
1. Retirement Readiness: "Am I on track for retirement?", "Can I retire early?"
2. Savings Strategies: "How much should I save?", "Should I use Roth or traditional?"
3. Investment Allocation: "What's the right asset allocation for retirement?"
4. Withdrawal Planning: "How much can I withdraw in retirement?", "What's the 4% rule?"
5. Social Security: "When should I claim Social Security?", "How much will I get?"
6. Tax Optimization: "How can I reduce taxes in retirement?", "Should I do a Roth conversion?"
7. Healthcare Costs: "How much will healthcare cost in retirement?"
8. Estate Planning: "How should I plan my estate for retirement?"

When a client asks a question:
1. Use the answer_retirement_question tool with any available context (age, savings, timeline, etc.)
2. If information is missing, ask targeted clarifying questions before making recommendations
3. Provide specific numbers, timelines, and action steps
4. Explain complex concepts in accessible language
5. Consider multiple factors: savings, Social Security, pensions, healthcare, taxes, life expectancy
6. Be encouraging and help clients understand their options

Always provide actionable, personalized advice based on the client's specific situation and stage of retirement planning."""

    return model, tools, task, context

