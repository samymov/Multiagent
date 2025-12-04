"""
Assessor Agent - conducts user financial wellness assessment and orchestrates portfolio analysis.
"""

import os
import json
import boto3
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass

from agents import function_tool, RunContextWrapper
from agents.extensions.models.litellm_model import LitellmModel

logger = logging.getLogger()

# Initialize Lambda client
# Get region for Lambda client
aws_region = os.getenv('DEFAULT_AWS_REGION', os.getenv('AWS_REGION', 'us-east-1'))
lambda_client = boto3.client("lambda", region_name=aws_region)

# Lambda function names from environment
TAGGER_FUNCTION = os.getenv("TAGGER_FUNCTION", "samy-tagger")
REPORTER_FUNCTION = os.getenv("REPORTER_FUNCTION", "samy-reporter")
DEBT_MANAGEMENT_FUNCTION = os.getenv("DEBT_MANAGEMENT_FUNCTION", "samy-debt-management")
RETIREMENT_FUNCTION = os.getenv("RETIREMENT_FUNCTION", "samy-retirement")
MOCK_LAMBDAS = os.getenv("MOCK_LAMBDAS", "false").lower() == "true"


@dataclass
class AssessorContext:
    """Context for assessor agent tools."""
    job_id: Optional[str] = None
    clerk_user_id: Optional[str] = None
    assessment_mode: bool = False  # True for assessment, False for orchestration
    db: Optional[Any] = None  # Database connection


async def invoke_lambda_agent(
    agent_name: str, function_name: str, payload: Dict[str, Any]
) -> Dict[str, Any]:
    """Invoke a Lambda function for an agent."""

    # For local testing with mocked agents
    if MOCK_LAMBDAS:
        logger.info(f"[MOCK] Would invoke {agent_name} with payload: {json.dumps(payload)[:200]}")
        return {"success": True, "message": f"[Mock] {agent_name} completed", "mock": True}

    try:
        logger.info(f"Invoking {agent_name} Lambda: {function_name}")

        response = lambda_client.invoke(
            FunctionName=function_name,
            InvocationType="RequestResponse",
            Payload=json.dumps(payload),
        )

        result = json.loads(response["Payload"].read())

        # Unwrap Lambda response if it has the standard format
        if isinstance(result, dict) and "statusCode" in result and "body" in result:
            if isinstance(result["body"], str):
                try:
                    result = json.loads(result["body"])
                except json.JSONDecodeError:
                    result = {"message": result["body"]}
            else:
                result = result["body"]

        logger.info(f"{agent_name} completed successfully")
        return result

    except Exception as e:
        logger.error(f"Error invoking {agent_name}: {e}")
        return {"error": str(e)}


def handle_missing_instruments(job_id: str, db) -> None:
    """
    Check for and tag any instruments missing allocation data.
    This is done automatically before the agent runs.
    """
    logger.info("Assessor: Checking for instruments missing allocation data...")

    # Get job and portfolio data
    job = db.jobs.find_by_id(job_id)
    if not job:
        logger.error(f"Job {job_id} not found")
        return

    user_id = job["clerk_user_id"]
    accounts = db.accounts.find_by_user(user_id)

    missing = []
    for account in accounts:
        positions = db.positions.find_by_account(account["id"])
        for position in positions:
            instrument = db.instruments.find_by_symbol(position["symbol"])
            if instrument:
                has_allocations = bool(
                    instrument.get("allocation_regions")
                    and instrument.get("allocation_sectors")
                    and instrument.get("allocation_asset_class")
                )
                if not has_allocations:
                    missing.append(
                        {"symbol": position["symbol"], "name": instrument.get("name", "")}
                    )
            else:
                missing.append({"symbol": position["symbol"], "name": ""})

    if missing:
        logger.info(
            f"Assessor: Found {len(missing)} instruments needing classification: {[m['symbol'] for m in missing]}"
        )

        try:
            response = lambda_client.invoke(
                FunctionName=TAGGER_FUNCTION,
                InvocationType="RequestResponse",
                Payload=json.dumps({"instruments": missing}),
            )

            result = json.loads(response["Payload"].read())

            if isinstance(result, dict) and "statusCode" in result:
                if result["statusCode"] == 200:
                    logger.info(
                        f"Assessor: InstrumentTagger completed - Tagged {len(missing)} instruments"
                    )
                else:
                    logger.error(
                        f"Assessor: InstrumentTagger failed with status {result['statusCode']}"
                    )

        except Exception as e:
            logger.error(f"Assessor: Error tagging instruments: {e}")
    else:
        logger.info("Assessor: All instruments have allocation data")


def load_portfolio_summary(job_id: str, db) -> Dict[str, Any]:
    """Load basic portfolio summary statistics only."""
    try:
        job = db.jobs.find_by_id(job_id)
        if not job:
            raise ValueError(f"Job {job_id} not found")

        user_id = job["clerk_user_id"]
        user = db.users.find_by_clerk_id(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")

        accounts = db.accounts.find_by_user(user_id)
        
        # Calculate simple summary statistics
        total_value = 0.0
        total_positions = 0
        total_cash = 0.0
        
        for account in accounts:
            cash_balance = account.get("cash_balance") or 0
            total_cash += float(cash_balance)
            positions = db.positions.find_by_account(account["id"])
            total_positions += len(positions)
            
            # Add position values
            for position in positions:
                instrument = db.instruments.find_by_symbol(position["symbol"])
                if instrument:
                    current_price = instrument.get("current_price")
                    if current_price is not None:
                        try:
                            price = float(current_price)
                            quantity = float(position.get("quantity") or 0)
                            total_value += price * quantity
                        except (ValueError, TypeError) as e:
                            logger.warning(f"Assessor: Could not convert price/quantity for {position['symbol']}: {e}")
        
        total_value += total_cash
        
        # Return only summary statistics
        # Handle None values from database
        target_income = user.get("target_retirement_income")
        if target_income is None:
            target_income = 80000
        else:
            target_income = float(target_income)
        
        return {
            "total_value": total_value,
            "num_accounts": len(accounts),
            "num_positions": total_positions,
            "years_until_retirement": user.get("years_until_retirement") or 30,
            "target_retirement_income": target_income
        }

    except Exception as e:
        logger.error(f"Error loading portfolio summary: {e}")
        raise


# ============================================================================
# Orchestration Tools (for portfolio analysis)
# ============================================================================

async def invoke_reporter_internal(job_id: str) -> str:
    """
    Invoke the Report Writer Lambda to generate portfolio analysis narrative.

    Args:
        job_id: The job ID for the analysis

    Returns:
        Confirmation message
    """
    result = await invoke_lambda_agent("Reporter", REPORTER_FUNCTION, {"job_id": job_id})

    if "error" in result:
        return f"Reporter agent failed: {result['error']}"

    return "Reporter agent completed successfully. Portfolio analysis narrative has been generated and saved."


async def invoke_debt_management_internal(job_id: str) -> str:
    """
    Invoke the Debt Management Lambda to analyze debt situation and provide budgeting guidance.

    Args:
        job_id: The job ID for the analysis

    Returns:
        Confirmation message
    """
    result = await invoke_lambda_agent(
        "Debt Management", DEBT_MANAGEMENT_FUNCTION, {"job_id": job_id}
    )

    if "error" in result:
        return f"Debt Management agent failed: {result['error']}"

    return "Debt Management agent completed successfully. Debt analysis and budgeting recommendations have been generated."


async def invoke_retirement_internal(job_id: str) -> str:
    """
    Invoke the Retirement Specialist Lambda for retirement projections.

    Args:
        job_id: The job ID for the analysis

    Returns:
        Confirmation message
    """
    result = await invoke_lambda_agent("Retirement", RETIREMENT_FUNCTION, {"job_id": job_id})

    if "error" in result:
        return f"Retirement agent failed: {result['error']}"

    return "Retirement agent completed successfully. Retirement projections have been calculated and saved."


@function_tool
async def invoke_reporter(wrapper: RunContextWrapper[AssessorContext]) -> str:
    """Invoke the Report Writer agent to generate portfolio analysis narrative."""
    if not wrapper.context.job_id:
        return "Error: job_id is required for portfolio analysis"
    return await invoke_reporter_internal(wrapper.context.job_id)


@function_tool
async def invoke_debt_management(wrapper: RunContextWrapper[AssessorContext]) -> str:
    """Invoke the Debt Management agent to analyze debt situation and provide budgeting guidance."""
    if not wrapper.context.job_id:
        return "Error: job_id is required for debt analysis"
    return await invoke_debt_management_internal(wrapper.context.job_id)


@function_tool
async def invoke_retirement(wrapper: RunContextWrapper[AssessorContext]) -> str:
    """Invoke the Retirement Specialist agent for retirement projections."""
    if not wrapper.context.job_id:
        return "Error: job_id is required for portfolio analysis"
    return await invoke_retirement_internal(wrapper.context.job_id)


# ============================================================================
# Assessment Tools (for wellness survey)
# ============================================================================

@function_tool
async def save_assessment_responses(
    wrapper: RunContextWrapper[AssessorContext],
    responses: Dict[str, Any]
) -> str:
    """
    Save wellness assessment questionnaire responses to the database.
    
    Args:
        responses: Dictionary containing all questionnaire responses with keys:
            - age: string
            - employment_status: string
            - retirement_plan: string
            - financial_goals: list of strings
            - income_spending: string
            - emergency_savings: string
            - savings_cover: string
            - debts: list of strings
            - accounts: list of strings
            - financial_confidence: string
            - advisor: string
    
    Returns:
        Confirmation message with assessment ID
    """
    if not wrapper.context.clerk_user_id or not wrapper.context.db:
        return "Error: clerk_user_id and database connection required"
    
    try:
        db = wrapper.context.db
        clerk_user_id = wrapper.context.clerk_user_id
        
        # Convert age to int if possible
        age_int = None
        if isinstance(responses.get("age"), str) and responses["age"].strip().isdigit():
            age_int = int(responses["age"].strip())
        elif isinstance(responses.get("age"), (int, float)):
            age_int = int(responses["age"])
        
        questionnaire_data = {
            "clerk_user_id": clerk_user_id,
            "age": age_int,
            "questionnaire_responses": responses,
        }
        
        # Check if questionnaire exists
        try:
            existing = db.client.query_one(
                "SELECT id FROM wellness_questionnaire WHERE clerk_user_id = :user_id",
                db.client._build_parameters({'user_id': clerk_user_id})
            )
        except Exception:
            existing = None
        
        if existing:
            db.client.update(
                "wellness_questionnaire",
                questionnaire_data,
                "clerk_user_id = :user_id",
                {'user_id': clerk_user_id}
            )
            questionnaire_id = str(existing['id'])
        else:
            questionnaire_id = str(db.client.insert(
                "wellness_questionnaire",
                questionnaire_data,
                returning="id"
            ))
        
        return f"Assessment responses saved successfully. Assessment ID: {questionnaire_id}"
    
    except Exception as e:
        logger.error(f"Error saving assessment responses: {e}")
        return f"Error saving assessment: {str(e)}"


@function_tool
async def calculate_wellness_scores(
    wrapper: RunContextWrapper[AssessorContext],
    responses: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Calculate wellness scores based on questionnaire responses.
    
    Args:
        responses: Dictionary containing all questionnaire responses
    
    Returns:
        Dictionary with scores and recommendations
    """
    # Import scoring functions (these should be in a shared module)
    def score_take_control(responses: dict) -> float:
        score = 0
        spending = responses.get("income_spending", "")
        if spending == "I usually spend less than I earn":
            score += 40
        elif spending == "I usually spend as much as I earn":
            score += 25
        else:
            score += 10
        
        debts = responses.get("debts", [])
        if "None" in debts:
            score += 40
        elif len(debts) <= 2:
            score += 25
        else:
            score += 10
        
        goals = responses.get("financial_goals", [])
        if "Paying my bills" in goals:
            score += 10
        if "Catching up after a late payment" in goals:
            score += 5
        
        return min(score, 100)
    
    def score_prepare_unexpected(responses: dict) -> float:
        score = 0
        emergency = responses.get("emergency_savings", "")
        if emergency == "Entirely":
            score += 50
        elif emergency == "Confident":
            score += 30
        else:
            score += 10
        
        cover = responses.get("savings_cover", "")
        if cover == "More than 6 months of expenses":
            score += 50
        elif cover == "From 4 to 6 months of expenses":
            score += 30
        elif cover == "From 1 to 3 months of expenses":
            score += 15
        elif cover == "Less than 1 month of expenses":
            score += 5
        else:
            score += 0
        
        return min(score, 100)
    
    def score_progress_goals(responses: dict) -> float:
        score = 0
        goals = responses.get("financial_goals", [])
        for g in ["Saving for retirement", "Saving for education", "Saving for health care", "Saving for a big purchase, like a house or car"]:
            if g in goals:
                score += 15
        
        accounts = responses.get("accounts", [])
        score += min(len(accounts) * 5, 20)
        
        return min(score, 100)
    
    def score_long_term_security(responses: dict) -> float:
        score = 0
        retirement = responses.get("retirement_plan", "")
        if retirement == "more than 5 years from now":
            score += 40
        else:
            score += 20
        
        accounts = responses.get("accounts", [])
        if "Individual Retirement Account (IRA)" in accounts:
            score += 20
        if "Employer retirement plan" in accounts:
            score += 20
        if "General Investing" in accounts:
            score += 20
        
        return min(score, 100)
    
    # Calculate scores
    take_control = score_take_control(responses)
    prepare_unexpected = score_prepare_unexpected(responses)
    progress_goals = score_progress_goals(responses)
    long_term_security = score_long_term_security(responses)
    overall_score = (take_control + prepare_unexpected + progress_goals + long_term_security) / 4
    
    # Determine which agent to route to based on scores and goals
    recommended_agent = "goal-solver"  # Default
    financial_goals = responses.get("financial_goals", [])
    
    if "Saving for retirement" in financial_goals or long_term_security < 60:
        recommended_agent = "retirement-planning"
    elif "Preparing for emergencies" in financial_goals or prepare_unexpected < 60:
        recommended_agent = "emergency-savings"
    elif any("debt" in goal.lower() or "loan" in goal.lower() for goal in financial_goals):
        recommended_agent = "goal-solver"
    elif responses.get("employment_status") == "Retired":
        recommended_agent = "social-security"
    
    return {
        "overall_score": round(overall_score, 1),
        "take_control_score": round(take_control, 1),
        "prepare_unexpected_score": round(prepare_unexpected, 1),
        "progress_goals_score": round(progress_goals, 1),
        "long_term_security_score": round(long_term_security, 1),
        "recommended_agent": recommended_agent,
        "recommendation_reason": f"Based on your assessment, we recommend the {recommended_agent} agent to help address your financial needs."
    }


# ============================================================================
# Agent Routing Tools
# ============================================================================

@function_tool
async def route_to_goal_solver_agent(
    wrapper: RunContextWrapper[AssessorContext],
    reason: str
) -> str:
    """
    Route the user to the Goal Solver Agent for help with financial goals, debt management, and cash flow.
    
    Args:
        reason: Explanation of why this agent is recommended
    
    Returns:
        Confirmation message with routing information
    """
    return f"Routing to Goal Solver Agent. {reason} The Goal Solver Agent will help you set and achieve financial goals, manage debt, and optimize cash flow."


@function_tool
async def route_to_retirement_planning_agent(
    wrapper: RunContextWrapper[AssessorContext],
    reason: str
) -> str:
    """
    Route the user to the Retirement Planning Agent for retirement savings and planning.
    
    Args:
        reason: Explanation of why this agent is recommended
    
    Returns:
        Confirmation message with routing information
    """
    return f"Routing to Retirement Planning Agent. {reason} The Retirement Planning Agent will help you maximize your retirement savings and plan for your future."


@function_tool
async def route_to_emergency_savings_agent(
    wrapper: RunContextWrapper[AssessorContext],
    reason: str
) -> str:
    """
    Route the user to the Emergency Savings Agent for building emergency funds.
    
    Args:
        reason: Explanation of why this agent is recommended
    
    Returns:
        Confirmation message with routing information
    """
    return f"Routing to Emergency Savings Agent. {reason} The Emergency Savings Agent will help you build and maintain an emergency fund."


@function_tool
async def route_to_social_security_agent(
    wrapper: RunContextWrapper[AssessorContext],
    reason: str
) -> str:
    """
    Route the user to the Social Security Agent for Social Security planning and benefits.
    
    Args:
        reason: Explanation of why this agent is recommended
    
    Returns:
        Confirmation message with routing information
    """
    return f"Routing to Social Security Agent. {reason} The Social Security Agent will help you plan for Social Security benefits and retirement transition."


# ============================================================================
# Agent Creation
# ============================================================================

def create_agent(
    job_id: Optional[str] = None,
    portfolio_summary: Optional[Dict[str, Any]] = None,
    db: Optional[Any] = None,
    clerk_user_id: Optional[str] = None,
    assessment_mode: bool = False
):
    """Create the assessor agent with appropriate tools based on mode."""
    
    # Create context
    context = AssessorContext(
        job_id=job_id,
        clerk_user_id=clerk_user_id,
        assessment_mode=assessment_mode,
        db=db
    )

    # Get model configuration
    model_id = os.getenv("BEDROCK_MODEL_ID", "amazon.nova-pro-v1:0")
    bedrock_region = os.getenv("BEDROCK_REGION", "us-east-1")
    os.environ["AWS_REGION_NAME"] = bedrock_region
    os.environ["AWS_REGION"] = bedrock_region
    os.environ["AWS_DEFAULT_REGION"] = bedrock_region
    
    if model_id.startswith("us."):
        model_id = model_id[3:]
        logger.info(f"Assessor: Removed us. prefix from model ID, now: {model_id}")

    model = LitellmModel(model=f"bedrock/{model_id}")

    # Select tools based on mode
    if assessment_mode:
        # Assessment mode: wellness survey and routing
        tools = [
            save_assessment_responses,
            calculate_wellness_scores,
            route_to_goal_solver_agent,
            route_to_retirement_planning_agent,
            route_to_emergency_savings_agent,
            route_to_social_security_agent,
        ]
        task = "Conduct a financial wellness assessment by asking the user 11 questions about their financial situation, goals, and needs. After collecting all responses, calculate wellness scores and recommend the most appropriate agent to help them."
    else:
        # Orchestration mode: portfolio analysis
        tools = [
            invoke_reporter,
            invoke_debt_management,
            invoke_retirement,
        ]
        if portfolio_summary:
            task = f"""Job {job_id} has {portfolio_summary['num_positions']} positions.
Retirement: {portfolio_summary['years_until_retirement']} years.

Call the appropriate agents."""
        else:
            task = "Coordinate portfolio analysis by calling the appropriate agents."

    return model, tools, task, context
