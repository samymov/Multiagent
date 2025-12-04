"""
Debt Management Agent - Provides personalized debt management and budgeting advice.
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

from agents import Agent, Runner, trace, function_tool, RunContextWrapper
from agents.extensions.models.litellm_model import LitellmModel

from .debt_intent_classifier import DebtIntentClassifier, DebtIntentType
from .debt_calculators import DebtCalculator
from .debt_advice_engine import DebtAdviceEngine
from .debt_response_generator import DebtResponseGenerator

logger = logging.getLogger(__name__)

# Get configuration
BEDROCK_MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "amazon.nova-pro-v1:0")
BEDROCK_REGION = os.getenv("BEDROCK_REGION", "us-east-1")


@dataclass
class DebtManagementContext:
    """Context for debt management agent."""
    clerk_user_id: Optional[str] = None
    user_data: Optional[Dict[str, Any]] = None
    db: Optional[Any] = None


class DebtManagementAgent:
    """Main debt management agent that orchestrates intent classification, calculations, and advice."""
    
    def __init__(self, user_data: Optional[Dict[str, Any]] = None, db: Optional[Any] = None):
        """
        Initialize debt management agent.
        
        Args:
            user_data: User profile data
            db: Database connection
        """
        self.intent_classifier = DebtIntentClassifier()
        self.calculator = DebtCalculator()
        self.advice_engine = DebtAdviceEngine(user_data)
        self.response_generator = DebtResponseGenerator()
        self.user_data = user_data or {}
        self.db = db
    
    def process_question(self, question: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process a client question and return comprehensive response.
        
        Args:
            question: Client's debt management question
            context: Additional context (debts, income, expenses, etc.)
            
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
        
        if intent_type == "debt_payoff_strategy":
            debts = context.get("debts", [])
            monthly_payment = context.get("monthly_payment", 0)
            
            if debts and monthly_payment > 0:
                comparison = self.calculator.compare_strategies(debts, monthly_payment)
                output["comparison"] = comparison
        
        elif intent_type == "student_loan_management":
            loan_info = context.get("loan_info", {})
            if loan_info:
                balance = loan_info.get("balance", 0)
                rate = loan_info.get("interest_rate", 0)
                years = loan_info.get("years", 10)
                
                if balance > 0 and rate > 0:
                    monthly_payment = self.calculator.calculate_student_loan_payment(balance, rate, years)
                    output["loan_analysis"] = {
                        **loan_info,
                        "monthly_payment": monthly_payment
                    }
        
        elif intent_type == "budget_creation":
            income = context.get("income", 0)
            framework = context.get("framework", "50/30/20")
            
            if income > 0:
                if framework == "50/30/20":
                    budget = self.calculator.calculate_budget_50_30_20(income)
                    output["budget"] = {
                        "framework": framework,
                        **budget
                    }
                elif framework == "zero-based":
                    expenses = context.get("expenses", {})
                    budget = self.calculator.calculate_zero_based_budget(income, expenses)
                    output["budget"] = {
                        "framework": framework,
                        **budget
                    }
        
        return output if output else None
    
    def _generate_error_response(self, question: str) -> str:
        """Generate fallback error response."""
        return f"""I apologize, but I encountered an issue processing your question: *{question}*

This could be due to:
- Missing financial data needed for analysis
- Unclear intent in your question
- Technical issues

**What you can do:**
1. Try rephrasing your question with more specific details
2. Provide information about your debts, income, or expenses
3. Contact support if the issue persists

I'm here to help with:
- Debt payoff strategies (Avalanche vs. Snowball)
- Student loan management and repayment plans
- Budget creation and frameworks
- Spending reduction strategies
- Debt consolidation options

Please try asking your question again with more context."""


@function_tool
async def answer_debt_question(
    wrapper: RunContextWrapper[DebtManagementContext],
    question: str,
    debts: Optional[List[Dict[str, Any]]] = None,
    monthly_payment: Optional[float] = None,
    income: Optional[float] = None,
    expenses: Optional[Dict[str, Any]] = None,
    loan_info: Optional[Dict[str, Any]] = None,
    employment_info: Optional[Dict[str, Any]] = None
) -> str:
    """
    Answer a client's debt management or budgeting question.
    
    Args:
        question: The client's question
        debts: Optional list of debts with keys: name, balance, interest_rate, minimum_payment
        monthly_payment: Optional total monthly amount available for debt repayment
        income: Optional monthly income for budget calculations
        expenses: Optional dictionary of expenses
        loan_info: Optional student loan information
        employment_info: Optional employment information
        
    Returns:
        Comprehensive answer with analysis and recommendations
    """
    context = {
        "debts": debts or [],
        "monthly_payment": monthly_payment or 0,
        "income": income or 0,
        "expenses": expenses or {},
        "loan_info": loan_info or {},
        "employment_info": employment_info or {}
    }
    
    agent = DebtManagementAgent(
        user_data=wrapper.context.user_data,
        db=wrapper.context.db
    )
    
    result = agent.process_question(question, context)
    
    if result.get("success"):
        return result.get("response", "I couldn't generate a response. Please try rephrasing your question.")
    else:
        return result.get("response", "I encountered an error processing your question. Please try again.")


def create_debt_management_agent(
    clerk_user_id: str,
    user_data: Optional[Dict[str, Any]] = None,
    db: Optional[Any] = None
) -> tuple:
    """
    Create the debt management agent with tools and context.
    
    Args:
        clerk_user_id: User's Clerk ID
        user_data: User profile data
        db: Database connection
        
    Returns:
        Tuple of (model, tools, task, context)
    """
    # Set up model
    model_id = BEDROCK_MODEL_ID
    if model_id.startswith("us."):
        model_id = model_id[3:]
        logger.info(f"Debt Management: Removed us. prefix from model ID, now: {model_id}")
    
    bedrock_region = BEDROCK_REGION
    os.environ["AWS_REGION_NAME"] = bedrock_region
    os.environ["AWS_REGION"] = bedrock_region
    os.environ["AWS_DEFAULT_REGION"] = bedrock_region
    
    model = LitellmModel(model=f"bedrock/{model_id}")
    
    # Create context
    context = DebtManagementContext(
        clerk_user_id=clerk_user_id,
        user_data=user_data or {},
        db=db
    )
    
    # Tools
    tools = [answer_debt_question]
    
    # Task
    task = """You are a Debt Management Agent that helps clients manage debt and create budgets.

You can help with:
1. Debt Payoff Strategies: "Which debt should I pay off first?", "Avalanche vs. Snowball method"
2. Student Loan Management: "Should I refinance my student loans?", "Am I eligible for PSLF?", "How much should I put toward student loans?"
3. Budget Creation: "Help me create a budget", "What's the 50/30/20 rule?"
4. Spending Reduction: "How can I reduce my spending?", "Where am I overspending?"
5. Debt Consolidation: "Should I consolidate my debts?", "Is a balance transfer right for me?"

When a client asks a question:
1. Use the answer_debt_question tool with any available context (debts, income, expenses)
2. If information is missing, ask targeted clarifying questions before making recommendations
3. Provide specific numbers, timelines, and action steps
4. Be encouraging and non-judgmental
5. Explain the reasoning behind recommendations

Always provide actionable, personalized advice based on the client's specific situation."""

    return model, tools, task, context

