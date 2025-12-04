"""
Debt Management Lambda Handler
Handles debt management and budgeting questions.
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
from .agent import create_debt_management_agent, DebtManagementContext
from .templates import DEBT_MANAGEMENT_INSTRUCTIONS
from .observability import observe

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize database
db = Database()


async def run_debt_management_agent(job_id: str, portfolio_data: Dict[str, Any], db=None) -> Dict[str, Any]:
    """Run the debt management agent in orchestration mode to analyze user's debt situation."""
    try:
        # Load job and user data
        job = db.jobs.find_by_id(job_id)
        if not job:
            raise ValueError(f"Job {job_id} not found")
        
        clerk_user_id = job['clerk_user_id']
        user_data = load_user_data(clerk_user_id)
        
        # Extract debt information from portfolio/wellness data
        # Check wellness questionnaire for debt information
        debts = []
        income = 0
        expenses = {}
        
        try:
            questionnaire = db.client.query_one(
                "SELECT questionnaire_responses FROM wellness_questionnaire WHERE clerk_user_id = :user_id",
                db.client._build_parameters({'user_id': clerk_user_id})
            )
            if questionnaire:
                responses = questionnaire.get("questionnaire_responses", {})
                debt_types = responses.get("debts", [])
                monthly_spending = responses.get("typical_month", "")
                
                # Build debt context from questionnaire
                # Note: Actual debt amounts would need to be stored separately
                # For now, we'll provide general debt management guidance
                
        except Exception as e:
            logger.warning(f"Could not load questionnaire data: {e}")
        
        # Create a general debt management analysis question
        question = "Help me understand my debt situation and create a plan to get out of debt. I need guidance on debt payoff strategies and budgeting."
        
        context = {
            "debts": debts,
            "income": income,
            "expenses": expenses,
            "portfolio_data": portfolio_data
        }
        
        # Process the question
        result = await process_debt_question(clerk_user_id, question, context)
        
        # Save analysis to job (similar to how charter saved charts)
        if result.get("success") and db:
            try:
                # Store debt management analysis in job payload
                analysis = {
                    "debt_management_analysis": result.get("response", ""),
                    "advice": result.get("advice", []),
                    "timestamp": str(asyncio.get_event_loop().time())
                }
                # Update job with debt management analysis
                # Note: This would require adding a method to store debt analysis
                # For now, we'll log it
                logger.info(f"Debt management analysis completed for job {job_id}")
            except Exception as e:
                logger.error(f"Error saving debt analysis: {e}")
        
        return {
            'success': result.get("success", False),
            'message': 'Debt management analysis completed' if result.get("success") else 'Failed to complete analysis',
            'analysis': result.get("response", "")
        }
    
    except Exception as e:
        logger.error(f"Error in debt management orchestration: {e}", exc_info=True)
        return {
            'success': False,
            'error': str(e)
        }


def handle_orchestration_mode(job_id: str, event: Dict[str, Any], db) -> Dict[str, Any]:
    """Handle orchestration mode (job-based invocation)."""
    try:
        portfolio_data = event.get('portfolio_data')
        if not portfolio_data:
            # Load portfolio data from database
            logger.info(f"Debt Management: Loading portfolio data for job {job_id}")
            try:
                job = db.jobs.find_by_id(job_id)
                if job:
                    user_id = job['clerk_user_id']
                    user = db.users.find_by_clerk_id(user_id)
                    accounts = db.accounts.find_by_user(user_id)

                    portfolio_data = {
                        'user_id': user_id,
                        'job_id': job_id,
                        'years_until_retirement': user.get('years_until_retirement', 30) if user else 30,
                        'accounts': []
                    }

                    for account in accounts:
                        account_data = {
                            'id': account['id'],
                            'name': account['account_name'],
                            'type': account.get('account_type', 'investment'),
                            'cash_balance': float(account.get('cash_balance', 0)),
                            'positions': []
                        }

                        positions = db.positions.find_by_account(account['id'])
                        for position in positions:
                            instrument = db.instruments.find_by_symbol(position['symbol'])
                            if instrument:
                                account_data['positions'].append({
                                    'symbol': position['symbol'],
                                    'quantity': float(position['quantity']),
                                    'instrument': instrument
                                })

                        portfolio_data['accounts'].append(account_data)

                    logger.info(f"Debt Management: Loaded {len(portfolio_data['accounts'])} accounts")
                else:
                    logger.error(f"Debt Management: Job {job_id} not found")
                    return {
                        'statusCode': 404,
                        'body': json.dumps({'error': 'Job not found'})
                    }
            except Exception as e:
                logger.error(f"Debt Management: Error loading portfolio data: {e}")
                return {
                    'statusCode': 500,
                    'body': json.dumps({'error': f'Failed to load portfolio data: {str(e)}'})
                }

        logger.info(f"Debt Management: Processing job {job_id}")

        # Run the agent
        result = asyncio.run(run_debt_management_agent(job_id, portfolio_data, db))

        logger.info(f"Debt Management completed for job {job_id}: {result}")

        return {
            'statusCode': 200,
            'body': json.dumps(result)
        }

    except Exception as e:
        logger.error(f"Error in debt management orchestration handler: {e}", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({
                'success': False,
                'error': str(e)
            })
        }


def load_user_data(clerk_user_id: str) -> Dict[str, Any]:
    """Load user profile data from database."""
    try:
        user = db.users.find_by_clerk_id(clerk_user_id)
        if not user:
            raise ValueError(f"User {clerk_user_id} not found")
        
        # Get wellness questionnaire for additional context if available
        age = None
        employment_status = None
        try:
            questionnaire = db.client.query_one(
                "SELECT age, questionnaire_responses FROM wellness_questionnaire WHERE clerk_user_id = :user_id",
                db.client._build_parameters({'user_id': clerk_user_id})
            )
            if questionnaire:
                age = questionnaire.get("age")
                responses = questionnaire.get("questionnaire_responses", {})
                employment_status = responses.get("employment_status")
        except Exception:
            pass
        
        return {
            "clerk_user_id": clerk_user_id,
            "display_name": user.get("display_name", ""),
            "current_age": age or 40,
            "employment_status": employment_status
        }
    
    except Exception as e:
        logger.error(f"Error loading user data: {e}")
        return {
            "clerk_user_id": clerk_user_id,
            "current_age": 40
        }


@retry(
    retry=retry_if_exception_type(RateLimitError),
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=4, max=60),
    before_sleep=lambda retry_state: logger.info(f"Debt Management: Rate limit hit, retrying in {retry_state.next_action.sleep} seconds...")
)
async def process_debt_question(
    clerk_user_id: str,
    question: str,
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Process a debt management question."""
    try:
        # Load user data
        user_data = load_user_data(clerk_user_id)
        
        # Merge with provided context
        if context:
            user_data.update(context)
        
        # Create agent
        model, tools, task, agent_context = create_debt_management_agent(
            clerk_user_id=clerk_user_id,
            user_data=user_data,
            db=db
        )
        
        # Run agent
        with trace("Debt Management Agent"):
            agent = Agent[DebtManagementContext](
                name="Debt Management Agent",
                instructions=DEBT_MANAGEMENT_INSTRUCTIONS,
                model=model,
                tools=tools
            )
            
            # Format the question as input
            input_text = f"Client question: {question}\n\nPlease provide a comprehensive answer using the answer_debt_question tool with any available context."
            
            result = await Runner.run(
                agent,
                input=input_text,
                context=agent_context,
                max_turns=10
            )
            
            return {
                "success": True,
                "response": result.final_output,
                "question": question
            }
    
    except Exception as e:
        logger.error(f"Error processing debt question: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "question": question
        }


def lambda_handler(event, context):
    """
    Lambda handler for debt management questions.
    
    Supports two modes:
    1. Direct question mode:
    {
        "mode": "debt_management",
        "clerk_user_id": "user_xxx",
        "question": "Which debt should I pay off first?",
        "context": {
            "debts": [...],
            "monthly_payment": 500,
            "income": 5000,
            "expenses": {...}
        }
    }
    
    2. Orchestration mode (job-based, like charter):
    {
        "job_id": "uuid",
        "portfolio_data": {...}
    }
    """
    with observe():
        try:
            logger.info(f"Debt Management Lambda invoked with event: {json.dumps(event)[:500]}")
            
            # Check if this is orchestration mode (job-based) or direct question mode
            job_id = event.get("job_id")
            
            if job_id:
                # Orchestration mode - analyze user's debt situation from portfolio
                return handle_orchestration_mode(job_id, event, db)
            else:
                # Direct question mode
                mode = event.get("mode", "debt_management")
                
                if mode != "debt_management":
                    return {
                        'statusCode': 400,
                        'body': json.dumps({'error': f'Invalid mode: {mode}. Expected "debt_management" or provide job_id'})
                    }
                
                # Extract parameters
                clerk_user_id = event.get("clerk_user_id")
                question = event.get("question")
                context = event.get("context", {})
                
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
                
                logger.info(f"Processing debt management question for user {clerk_user_id}: {question}")
                
                # Process question
                result = asyncio.run(process_debt_question(clerk_user_id, question, context))
                
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
            logger.error(f"Debt Management Lambda handler error: {e}", exc_info=True)
            return {
                'statusCode': 500,
                'body': json.dumps({
                    'success': False,
                    'error': str(e)
                })
            }

