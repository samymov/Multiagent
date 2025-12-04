"""
Assessor Agent Lambda Handler - supports both assessment and orchestration modes.
"""

import os
import json
import asyncio
import logging
from typing import Dict, Any, Optional

from agents import Agent, Runner, trace
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from litellm.exceptions import RateLimitError

try:
    from dotenv import load_dotenv
    load_dotenv(override=True)
except ImportError:
    pass

# Import database package
from src import Database

from templates import ASSESSMENT_INSTRUCTIONS, ORCHESTRATOR_INSTRUCTIONS
from agent import create_agent, handle_missing_instruments, load_portfolio_summary, AssessorContext
from market import update_instrument_prices
from observability import observe

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize database
db = Database()

@retry(
    retry=retry_if_exception_type(RateLimitError),
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=4, max=60),
    before_sleep=lambda retry_state: logger.info(f"Assessor: Rate limit hit, retrying in {retry_state.next_action.sleep} seconds...")
)
async def run_orchestrator(job_id: str) -> None:
    """Run the orchestrator agent to coordinate portfolio analysis."""
    try:
        # Update job status to running
        db.jobs.update_status(job_id, 'running')
        
        # Handle missing instruments first (non-agent pre-processing)
        await asyncio.to_thread(handle_missing_instruments, job_id, db)

        # Update instrument prices after tagging
        logger.info("Assessor: Updating instrument prices from market data")
        await asyncio.to_thread(update_instrument_prices, job_id, db)

        # Load portfolio summary (just statistics, not full data)
        portfolio_summary = await asyncio.to_thread(load_portfolio_summary, job_id, db)
        
        # Create agent with tools and context (orchestration mode)
        model, tools, task, context = create_agent(
            job_id=job_id,
            portfolio_summary=portfolio_summary,
            db=db,
            assessment_mode=False
        )
        
        # Run the orchestrator
        with trace("Assessor Orchestrator"):
            agent = Agent[AssessorContext](
                name="Assessor Agent",
                instructions=ORCHESTRATOR_INSTRUCTIONS,
                model=model,
                tools=tools
            )
            
            result = await Runner.run(
                agent,
                input=task,
                context=context,
                max_turns=20
            )
            
            # Mark job as completed after all agents finish
            db.jobs.update_status(job_id, "completed")
            logger.info(f"Assessor: Job {job_id} completed successfully")
            
    except Exception as e:
        logger.error(f"Assessor: Error in orchestration: {e}", exc_info=True)
        db.jobs.update_status(job_id, 'failed', error_message=str(e))
        raise


async def run_assessment(clerk_user_id: str, user_input: Optional[str] = None) -> Dict[str, Any]:
    """Run the assessment agent to conduct wellness survey."""
    try:
        logger.info(f"Assessor: Starting assessment for user {clerk_user_id}")
        
        # Create agent with tools and context (assessment mode)
        model, tools, task, context = create_agent(
            clerk_user_id=clerk_user_id,
            db=db,
            assessment_mode=True
        )
        
        # If user_input is provided, use it; otherwise start with the task
        input_text = user_input if user_input else task
        
        # Run the assessment agent
        with trace("Assessor Assessment"):
            agent = Agent[AssessorContext](
                name="Assessor Agent",
                instructions=ASSESSMENT_INSTRUCTIONS,
                model=model,
                tools=tools
            )
            
            result = await Runner.run(
                agent,
                input=input_text,
                context=context,
                max_turns=30  # More turns for conversation
            )
            
            logger.info(f"Assessor: Assessment completed for user {clerk_user_id}")
            return {
                "success": True,
                "output": result.final_output,
                "conversation_complete": True
            }
            
    except Exception as e:
        logger.error(f"Assessor: Error in assessment: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e)
        }


def lambda_handler(event, context):
    """
    Lambda handler for both assessment and orchestration modes.
    
    Assessment mode (from API):
    {
        "mode": "assessment",
        "clerk_user_id": "user_xxx",
        "user_input": "optional user message"
    }
    
    Orchestration mode (from SQS):
    {
        "Records": [
            {
                "body": "job_id"
            }
        ]
    }
    or
    {
        "job_id": "job_xxx"
    }
    """
    # Wrap entire handler with observability context
    with observe():
        try:
            logger.info(f"Assessor Lambda invoked with event: {json.dumps(event)[:500]}")

            # Check if this is assessment mode
            if event.get("mode") == "assessment":
                clerk_user_id = event.get("clerk_user_id")
                if not clerk_user_id:
                    return {
                        'statusCode': 400,
                        'body': json.dumps({'error': 'clerk_user_id required for assessment mode'})
                    }
                
                user_input = event.get("user_input")
                logger.info(f"Assessor: Starting assessment for user {clerk_user_id}")
                
                result = asyncio.run(run_assessment(clerk_user_id, user_input))
                
                return {
                    'statusCode': 200 if result.get("success") else 500,
                    'body': json.dumps(result)
                }
            
            # Otherwise, orchestration mode
            # Extract job_id from SQS message
            if 'Records' in event and len(event['Records']) > 0:
                # SQS message
                job_id = event['Records'][0]['body']
                if isinstance(job_id, str) and job_id.startswith('{'):
                    # Body might be JSON
                    try:
                        body = json.loads(job_id)
                        job_id = body.get('job_id', job_id)
                    except json.JSONDecodeError:
                        pass
            elif 'job_id' in event:
                # Direct invocation
                job_id = event['job_id']
            else:
                logger.error("No job_id found in event")
                return {
                    'statusCode': 400,
                    'body': json.dumps({'error': 'No job_id provided for orchestration mode'})
                }

            logger.info(f"Assessor: Starting orchestration for job {job_id}")

            # Run the orchestrator
            asyncio.run(run_orchestrator(job_id))

            return {
                'statusCode': 200,
                'body': json.dumps({
                    'success': True,
                    'message': f'Analysis completed for job {job_id}'
                })
            }

        except Exception as e:
            logger.error(f"Assessor: Error in lambda handler: {e}", exc_info=True)
            return {
                'statusCode': 500,
                'body': json.dumps({
                    'success': False,
                    'error': str(e)
                })
            }

# For local testing
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "assessment":
        # Test assessment mode
        test_user_id = "test_user_assessor_local"
        
        user = db.users.find_by_clerk_id(test_user_id)
        if not user:
            from src.schemas import UserCreate
            print(f"Creating test user: {test_user_id}")
            user_create = UserCreate(clerk_user_id=test_user_id, display_name="Test Assessor User")
            db.users.create(user_create.model_dump(), returning='clerk_user_id')
        
        test_event = {
            'mode': 'assessment',
            'clerk_user_id': test_user_id,
            'user_input': None
        }
        
        result = lambda_handler(test_event, None)
        print(json.dumps(result, indent=2))
    else:
        # Test orchestration mode
        test_user_id = "test_user_assessor_local"
        
        from src.schemas import UserCreate, JobCreate
        
        user = db.users.find_by_clerk_id(test_user_id)
        if not user:
            print(f"Creating test user: {test_user_id}")
            user_create = UserCreate(clerk_user_id=test_user_id, display_name="Test Assessor User")
            db.users.create(user_create.model_dump(), returning='clerk_user_id')

        # Create a test job
        print("Creating test job...")
        job_create = JobCreate(
            clerk_user_id=test_user_id,
            job_type='portfolio_analysis',
            request_payload={
                'analysis_type': 'comprehensive',
                'test': True
            }
        )
        
        job = db.jobs.create(job_create.model_dump())
        job_id = job
        
        print(f"Created test job: {job_id}")
        
        # Test the handler
        test_event = {
            'job_id': job_id
        }
        
        result = lambda_handler(test_event, None)
        print(json.dumps(result, indent=2))
