"""
Retirement Specialist Agent Lambda Handler
"""

import os
import json
import asyncio
import logging
from typing import Dict, Any
from datetime import datetime

from agents import Agent, Runner, trace
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from litellm.exceptions import RateLimitError


class AgentTemporaryError(Exception):
    """Temporary error that should trigger retry"""
    pass

try:
    from dotenv import load_dotenv
    load_dotenv(override=True)
except ImportError:
    pass

# Import database package
from src import Database

from templates import RETIREMENT_INSTRUCTIONS, RETIREMENT_PLANNING_INSTRUCTIONS
from agent import create_agent
from retirement_planning_agent import create_retirement_planning_agent, RetirementPlanningContext
from observability import observe

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def get_user_preferences(job_id: str) -> Dict[str, Any]:
    """Load user preferences from database."""
    try:
        db = Database()
        
        # Get the job to find the user
        job = db.jobs.find_by_id(job_id)
        if job and job.get('clerk_user_id'):
            # Get user preferences
            user = db.users.find_by_clerk_id(job['clerk_user_id'])
            if user:
                # Handle None values from database
                target_income = user.get('target_retirement_income')
                if target_income is None:
                    target_income = 80000
                else:
                    target_income = float(target_income)
                
                return {
                    'years_until_retirement': user.get('years_until_retirement') or 30,
                    'target_retirement_income': target_income,
                    'current_age': 40  # Default for now
                }
    except Exception as e:
        logger.warning(f"Could not load user data: {e}. Using defaults.")
    
    return {
        'years_until_retirement': 30,
        'target_retirement_income': 80000.0,
        'current_age': 40
    }

@retry(
    retry=retry_if_exception_type((RateLimitError, AgentTemporaryError, TimeoutError, asyncio.TimeoutError)),
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=4, max=60),
    before_sleep=lambda retry_state: logger.info(f"Retirement: Temporary error, retrying in {retry_state.next_action.sleep} seconds...")
)
async def run_retirement_agent(job_id: str, portfolio_data: Dict[str, Any]) -> Dict[str, Any]:
    """Run the retirement specialist agent."""
    
    # Get user preferences
    user_preferences = get_user_preferences(job_id)
    
    # Initialize database
    db = Database()
    
    # Create agent (simplified - no tools or context)
    model, tools, task = create_agent(job_id, portfolio_data, user_preferences, db)
    
    # Run agent (simplified - no context)
    with trace("Retirement Agent"):
        agent = Agent(
            name="Retirement Specialist",
            instructions=RETIREMENT_INSTRUCTIONS,
            model=model,
            tools=tools  # Empty list now
        )
        
        try:
            result = await Runner.run(
                agent,
                input=task,
                max_turns=20
            )
        except (TimeoutError, asyncio.TimeoutError) as e:
            logger.warning(f"Retirement agent timeout: {e}")
            raise AgentTemporaryError(f"Timeout during agent execution: {e}")
        except Exception as e:
            error_str = str(e).lower()
            if "timeout" in error_str or "throttled" in error_str:
                logger.warning(f"Retirement temporary error: {e}")
                raise AgentTemporaryError(f"Temporary error: {e}")
            raise  # Re-raise non-retryable errors
        
        # Save the analysis to database
        retirement_payload = {
            'analysis': result.final_output,
            'generated_at': datetime.utcnow().isoformat(),
            'agent': 'retirement'
        }
        
        success = db.jobs.update_retirement(job_id, retirement_payload)
        
        if not success:
            logger.error(f"Failed to save retirement analysis for job {job_id}")
        
        return {
            'success': success,
            'message': 'Retirement analysis completed' if success else 'Analysis completed but failed to save',
            'final_output': result.final_output
        }

async def process_retirement_question(
    clerk_user_id: str,
    question: str,
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Process a retirement planning question in conversational mode."""
    try:
        # Load user data
        user_data = get_user_preferences_from_id(clerk_user_id)
        
        # Load portfolio data if available
        portfolio_data = {}
        try:
            db = Database()
            accounts = db.accounts.find_by_user(clerk_user_id)
            portfolio_data = {
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
                            'quantity': float(position.get('quantity', 0)),
                            'instrument': instrument
                        })
                portfolio_data['accounts'].append(account_data)
        except Exception as e:
            logger.warning(f"Could not load portfolio data: {e}")
        
        # Merge with provided context
        if context:
            user_data.update(context)
        
        # Create agent
        model, tools, task, agent_context = create_retirement_planning_agent(
            clerk_user_id=clerk_user_id,
            portfolio_data=portfolio_data,
            user_data=user_data,
            db=db
        )
        
        # Run agent
        with trace("Retirement Planning Agent"):
            agent = Agent[RetirementPlanningContext](
                name="Retirement Planning Agent",
                instructions=RETIREMENT_PLANNING_INSTRUCTIONS,
                model=model,
                tools=tools
            )
            
            # Format the question as input
            input_text = f"Client question: {question}\n\nPlease provide a comprehensive answer using the answer_retirement_question tool with any available context."
            
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
        logger.error(f"Error processing retirement question: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "question": question
        }


def get_user_preferences_from_id(clerk_user_id: str) -> Dict[str, Any]:
    """Load user preferences from clerk_user_id."""
    try:
        db = Database()
        user = db.users.find_by_clerk_id(clerk_user_id)
        if user:
            target_income = user.get('target_retirement_income')
            if target_income is None:
                target_income = 80000
            else:
                target_income = float(target_income)
            
            return {
                'years_until_retirement': user.get('years_until_retirement') or 30,
                'target_retirement_income': target_income,
                'current_age': 40  # Default, could be loaded from wellness questionnaire
            }
    except Exception as e:
        logger.warning(f"Could not load user data: {e}. Using defaults.")
    
    return {
        'years_until_retirement': 30,
        'target_retirement_income': 80000.0,
        'current_age': 40
    }


def lambda_handler(event, context):
    """
    Lambda handler supporting both orchestration mode and direct question mode.

    Orchestration mode (job-based):
    {
        "job_id": "uuid",
        "portfolio_data": {...}  # Optional, will load from DB if not provided
    }
    
    Direct question mode:
    {
        "mode": "retirement_planning",
        "clerk_user_id": "user_xxx",
        "question": "Am I on track for retirement?",
        "context": {
            "current_age": 45,
            "years_until_retirement": 20,
            "target_retirement_income": 100000
        }
    }
    """
    # Wrap entire handler with observability context
    with observe() as observability:
        try:
            logger.info(f"Retirement Lambda invoked with event: {json.dumps(event)[:500]}")

            # Parse event
            if isinstance(event, str):
                event = json.loads(event)

            # Check if this is direct question mode or orchestration mode
            job_id = event.get('job_id')
            mode = event.get('mode', 'orchestration')
            
            if mode == 'retirement_planning' and not job_id:
                # Direct question mode
                clerk_user_id = event.get('clerk_user_id')
                question = event.get('question')
                question_context = event.get('context', {})
                
                if not clerk_user_id:
                    return {
                        'statusCode': 400,
                        'body': json.dumps({'error': 'clerk_user_id is required for question mode'})
                    }
                
                if not question:
                    return {
                        'statusCode': 400,
                        'body': json.dumps({'error': 'question is required for question mode'})
                    }
                
                logger.info(f"Processing retirement planning question for user {clerk_user_id}: {question}")
                
                # Process question
                result = asyncio.run(process_retirement_question(clerk_user_id, question, question_context))
                
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
            
            # Orchestration mode (existing functionality)
            if not job_id:
                return {
                    'statusCode': 400,
                    'body': json.dumps({'error': 'job_id is required for orchestration mode'})
                }

            portfolio_data = event.get('portfolio_data')
            if not portfolio_data:
                # Try to load from database
                logger.info(f"Retirement Loading portfolio data for job {job_id}")
                try:
                    import sys
                    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
                    from src import Database

                    db = Database()
                    job = db.jobs.find_by_id(job_id)
                    if job:
                        if observability:
                            observability.create_event(
                                name="Retirement Started!", status_message="OK"
                            )
                        
                        # portfolio_data = job.get('request_payload', {}).get('portfolio_data', {})
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
                            # Handle None values safely
                            cash_balance = account.get('cash_balance') or 0
                            
                            account_data = {
                                'id': account['id'],
                                'name': account['account_name'],
                                'type': account.get('account_type', 'investment'),
                                'cash_balance': float(cash_balance),
                                'positions': []
                            }

                            positions = db.positions.find_by_account(account['id'])
                            for position in positions:
                                instrument = db.instruments.find_by_symbol(position['symbol'])
                                if instrument:
                                    # Handle None values safely
                                    quantity = position.get('quantity') or 0
                                    account_data['positions'].append({
                                        'symbol': position['symbol'],
                                        'quantity': float(quantity),
                                        'instrument': instrument
                                    })

                            portfolio_data['accounts'].append(account_data)

                        logger.info(f"Retirement: Loaded {len(portfolio_data['accounts'])} accounts with positions")
                    else:
                        logger.error(f"Retirement: Job {job_id} not found")
                        return {
                            'statusCode': 404,
                            'body': json.dumps({'error': f'Job {job_id} not found'})
                        }
                except Exception as e:
                    logger.error(f"Could not load portfolio from database: {e}")
                    return {
                        'statusCode': 400,
                        'body': json.dumps({'error': 'No portfolio data provided'})
                    }

            logger.info(f"Retirement: Processing job {job_id}")

            # Run the agent
            result = asyncio.run(run_retirement_agent(job_id, portfolio_data))

            logger.info(f"Retirement completed for job {job_id}")

            return {
                'statusCode': 200,
                'body': json.dumps(result)
            }

        except Exception as e:
            logger.error(f"Error in retirement: {e}", exc_info=True)
            return {
                'statusCode': 500,
                'body': json.dumps({
                    'success': False,
                    'error': str(e)
                })
            }

# For local testing
if __name__ == "__main__":
    test_event = {
        "job_id": "test-retirement-123",
        "portfolio_data": {
            "accounts": [
                {
                    "name": "401(k)",
                    "type": "retirement",
                    "cash_balance": 10000,
                    "positions": [
                        {
                            "symbol": "SPY",
                            "quantity": 100,
                            "instrument": {
                                "name": "SPDR S&P 500 ETF",
                                "current_price": 450,
                                "allocation_asset_class": {"equity": 100}
                            }
                        },
                        {
                            "symbol": "BND",
                            "quantity": 100,
                            "instrument": {
                                "name": "Vanguard Total Bond Market ETF",
                                "current_price": 75,
                                "allocation_asset_class": {"fixed_income": 100}
                            }
                        }
                    ]
                }
            ]
        }
    }
    
    result = lambda_handler(test_event, None)
    print(json.dumps(result, indent=2))