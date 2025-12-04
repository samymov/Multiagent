"""
Goal Planner Lambda Handler
Handles financial planning questions using intent classification, estimators, and advice rules.
"""

import os
import json
import asyncio
import logging
from typing import Dict, Any, Optional

from agents import Agent, Runner, trace
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from litellm.exceptions import RateLimitError

from src import Database
from .goal_planner_agent import create_goal_planner_agent, GoalPlannerContext
from .templates import GOAL_PLANNER_INSTRUCTIONS
from observability import observe

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize database
db = Database()


def load_user_portfolio_data(clerk_user_id: str) -> Dict[str, Any]:
    """Load user's portfolio data from database."""
    try:
        user = db.users.find_by_clerk_id(clerk_user_id)
        if not user:
            raise ValueError(f"User {clerk_user_id} not found")
        
        accounts = db.accounts.find_by_user(clerk_user_id)
        
        # Build portfolio data structure
        portfolio_data = {
            "accounts": []
        }
        
        for account in accounts:
            account_id = account["id"]
            positions = db.positions.find_by_account(account_id)
            
            account_positions = []
            for position in positions:
                symbol = position.get("symbol")
                if symbol:
                    instrument = db.instruments.find_by_symbol(symbol)
                    if instrument:
                        account_positions.append({
                            "symbol": symbol,
                            "quantity": float(position.get("quantity", 0)),
                            "instrument": {
                                "name": instrument.get("name", ""),
                                "current_price": float(instrument.get("current_price", 0)),
                                "allocation_asset_class": instrument.get("allocation_asset_class", {}),
                                "allocation_regions": instrument.get("allocation_regions", {}),
                                "allocation_sectors": instrument.get("allocation_sectors", {})
                            }
                        })
            
            portfolio_data["accounts"].append({
                "id": str(account_id),
                "name": account.get("account_name", ""),
                "cash_balance": float(account.get("cash_balance", 0)),
                "positions": account_positions
            })
        
        return portfolio_data
    
    except Exception as e:
        logger.error(f"Error loading portfolio data: {e}")
        return {"accounts": []}


def load_user_data(clerk_user_id: str) -> Dict[str, Any]:
    """Load user profile data from database."""
    try:
        user = db.users.find_by_clerk_id(clerk_user_id)
        if not user:
            raise ValueError(f"User {clerk_user_id} not found")
        
        # Get wellness questionnaire for age if available
        age = None
        try:
            questionnaire = db.client.query_one(
                "SELECT age FROM wellness_questionnaire WHERE clerk_user_id = :user_id",
                db.client._build_parameters({'user_id': clerk_user_id})
            )
            if questionnaire:
                age = questionnaire.get("age")
        except Exception:
            pass  # Age not available
        
        return {
            "clerk_user_id": clerk_user_id,
            "display_name": user.get("display_name", ""),
            "years_until_retirement": user.get("years_until_retirement", 30),
            "target_retirement_income": float(user.get("target_retirement_income", 80000) or 80000),
            "current_age": age or 40,  # Default to 40 if not available
            "asset_class_targets": user.get("asset_class_targets", {}),
            "region_targets": user.get("region_targets", {})
        }
    
    except Exception as e:
        logger.error(f"Error loading user data: {e}")
        return {
            "clerk_user_id": clerk_user_id,
            "years_until_retirement": 30,
            "target_retirement_income": 80000,
            "current_age": 40
        }


@retry(
    retry=retry_if_exception_type(RateLimitError),
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=4, max=60),
    before_sleep=lambda retry_state: logger.info(f"Goal Planner: Rate limit hit, retrying in {retry_state.next_action.sleep} seconds...")
)
async def process_goal_planning_question(
    clerk_user_id: str,
    question: str
) -> Dict[str, Any]:
    """Process a goal planning question."""
    try:
        # Load user data
        portfolio_data = load_user_portfolio_data(clerk_user_id)
        user_data = load_user_data(clerk_user_id)
        
        # Create agent
        model, tools, task, context = create_goal_planner_agent(
            clerk_user_id=clerk_user_id,
            portfolio_data=portfolio_data,
            user_data=user_data,
            db=db
        )
        
        # Run agent
        with trace("Goal Planner Agent"):
            agent = Agent[GoalPlannerContext](
                name="Goal Planning Agent",
                instructions=GOAL_PLANNER_INSTRUCTIONS,
                model=model,
                tools=tools
            )
            
            # Format the question as input
            input_text = f"Client question: {question}\n\nPlease provide a comprehensive answer using the answer_financial_question tool."
            
            result = await Runner.run(
                agent,
                input=input_text,
                context=context,
                max_turns=10
            )
            
            return {
                "success": True,
                "response": result.final_output,
                "question": question
            }
    
    except Exception as e:
        logger.error(f"Error processing goal planning question: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "question": question
        }


def lambda_handler(event, context):
    """
    Lambda handler for goal planning questions.
    
    Expected event format:
    {
        "mode": "goal_planning",
        "clerk_user_id": "user_xxx",
        "question": "Am I on track for retirement?"
    }
    """
    with observe():
        try:
            logger.info(f"Goal Planner Lambda invoked with event: {json.dumps(event)[:500]}")
            
            # Check mode
            mode = event.get("mode", "goal_planning")
            
            if mode != "goal_planning":
                return {
                    'statusCode': 400,
                    'body': json.dumps({'error': f'Invalid mode: {mode}. Expected "goal_planning"'})
                }
            
            # Extract parameters
            clerk_user_id = event.get("clerk_user_id")
            question = event.get("question")
            
            if not clerk_user_id:
                return {
                    'statusCode': 400,
                    'body': json.dumps({'error': 'clerk_user_id is required'})
                }
            
            if not question:
                return {
                    'statusCode': 400,
                    'body': json.dumps({'error': 'question is required'})
                }
            
            logger.info(f"Processing goal planning question for user {clerk_user_id}: {question}")
            
            # Process question
            result = asyncio.run(process_goal_planning_question(clerk_user_id, question))
            
            if result.get("success"):
                return {
                    'statusCode': 200,
                    'body': json.dumps(result)
                }
            else:
                return {
                    'statusCode': 500,
                    'body': json.dumps(result)
                }
        
        except Exception as e:
            logger.error(f"Goal Planner Lambda handler error: {e}", exc_info=True)
            return {
                'statusCode': 500,
                'body': json.dumps({
                    'success': False,
                    'error': str(e)
                })
            }

