"""
FastAPI backend for Samy Financial Advisor
Handles all API routes with Clerk JWT authentication
"""

import os
import json
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal
import uuid

from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, ValidationError
import boto3
from botocore.exceptions import ClientError
from mangum import Mangum
from dotenv import load_dotenv
from fastapi_clerk_auth import ClerkConfig, ClerkHTTPBearer, HTTPAuthorizationCredentials

from src import Database
from src.schemas import (
    UserCreate,
    AccountCreate,
    PositionCreate,
    JobCreate, JobUpdate,
    JobType, JobStatus
)
# Import CFPB scoring module
import sys
from pathlib import Path
api_dir = Path(__file__).parent
if str(api_dir) not in sys.path:
    sys.path.insert(0, str(api_dir))
from cfpb_scoring import calculate_cfpb_score, get_cfpb_rating

# Load environment variables
load_dotenv(override=True)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Samy Financial Advisor API",
    description="Backend API for AI-powered financial planning",
    version="1.0.0"
)

# CORS configuration
# Get origins from CORS_ORIGINS env var (comma-separated) or fall back to localhost
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom exception handlers for better error messages
@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    """Handle Pydantic validation errors with user-friendly messages"""
    return JSONResponse(
        status_code=422,
        content={"detail": "Invalid input data. Please check your request and try again."}
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions with improved messages"""
    # Map technical errors to user-friendly messages
    # But preserve custom messages if they're already user-friendly
    user_friendly_messages = {
        401: "Your session has expired. Please sign in again.",
        403: "You don't have permission to access this resource.",
        404: "The requested resource was not found.",
        429: "Too many requests. Please slow down and try again later.",
        500: "An internal error occurred. Please try again later.",
        503: "The service is temporarily unavailable. Please try again later."
    }

    # If the detail already contains helpful information (like migration instructions),
    # use it instead of the generic message
    if exc.detail and (
        "migration" in exc.detail.lower() or 
        "database" in exc.detail.lower() or
        len(exc.detail) > 50  # Custom messages are usually longer
    ):
        message = exc.detail
    else:
        message = user_friendly_messages.get(exc.status_code, exc.detail)
    
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": message}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected errors gracefully"""
    logger.error(f"Unexpected error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred. Our team has been notified."}
    )

# Initialize services
db = Database()

# SQS client for job queueing
sqs_client = boto3.client('sqs', region_name=os.getenv('DEFAULT_AWS_REGION', 'us-east-1'))
SQS_QUEUE_URL = os.getenv('SQS_QUEUE_URL', '')

# Clerk authentication setup (exactly like saas reference)
clerk_config = ClerkConfig(jwks_url=os.getenv("CLERK_JWKS_URL"))
clerk_guard = ClerkHTTPBearer(clerk_config)

async def get_current_user_id(creds: HTTPAuthorizationCredentials = Depends(clerk_guard)) -> str:
    """Extract user ID from validated Clerk token"""
    # The clerk_guard dependency already validated the token
    # creds.decoded contains the JWT payload
    user_id = creds.decoded["sub"]
    logger.info(f"Authenticated user: {user_id}")
    return user_id

# Request/Response models
class UserResponse(BaseModel):
    user: Dict[str, Any]
    created: bool

class UserUpdate(BaseModel):
    """Update user settings"""
    display_name: Optional[str] = None
    years_until_retirement: Optional[int] = None
    target_retirement_income: Optional[float] = None
    asset_class_targets: Optional[Dict[str, float]] = None
    region_targets: Optional[Dict[str, float]] = None

class AccountUpdate(BaseModel):
    """Update account"""
    account_name: Optional[str] = None
    account_purpose: Optional[str] = None
    cash_balance: Optional[float] = None

class PositionUpdate(BaseModel):
    """Update position"""
    quantity: Optional[float] = None

class AnalyzeRequest(BaseModel):
    analysis_type: str = Field(default="portfolio", description="Type of analysis to perform")
    options: Dict[str, Any] = Field(default_factory=dict, description="Analysis options")

class AnalyzeResponse(BaseModel):
    job_id: str
    message: str

# API Routes

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/api/user", response_model=UserResponse)
async def get_or_create_user(
    clerk_user_id: str = Depends(get_current_user_id),
    creds: HTTPAuthorizationCredentials = Depends(clerk_guard)
):
    """Get user or create if first time"""

    try:
        # Check if user exists
        user = db.users.find_by_clerk_id(clerk_user_id)

        if user:
            return UserResponse(user=user, created=False)

        # Create new user with defaults from JWT token
        token_data = creds.decoded
        display_name = token_data.get('name') or token_data.get('email', '').split('@')[0] or "New User"

        # Create user with ALL defaults in one operation
        user_data = {
            'clerk_user_id': clerk_user_id,
            'display_name': display_name,
            'years_until_retirement': 20,
            'target_retirement_income': 60000,
            'asset_class_targets': {"equity": 70, "fixed_income": 30},
            'region_targets': {"north_america": 50, "international": 50}
        }

        # Insert directly with all data
        created_clerk_id = db.users.db.insert('users', user_data, returning='clerk_user_id')

        # Fetch the created user
        created_user = db.users.find_by_clerk_id(clerk_user_id)
        logger.info(f"Created new user: {clerk_user_id}")

        return UserResponse(user=created_user, created=True)

    except Exception as e:
        logger.error(f"Error in get_or_create_user: {e}")
        raise HTTPException(status_code=500, detail="Failed to load user profile")

@app.put("/api/user")
async def update_user(user_update: UserUpdate, clerk_user_id: str = Depends(get_current_user_id)):
    """Update user settings"""

    try:
        # Get user
        user = db.users.find_by_clerk_id(clerk_user_id)

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Update user - users table uses clerk_user_id as primary key
        update_data = user_update.model_dump(exclude_unset=True)

        # Use the database client directly since users table has clerk_user_id as PK
        db.users.db.update(
            'users',
            update_data,
            "clerk_user_id = :clerk_user_id",
            {'clerk_user_id': clerk_user_id}
        )

        # Return updated user
        updated_user = db.users.find_by_clerk_id(clerk_user_id)
        return updated_user

    except Exception as e:
        logger.error(f"Error updating user: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/accounts")
async def list_accounts(clerk_user_id: str = Depends(get_current_user_id)):
    """List user's accounts"""

    try:
        # Get accounts for user
        accounts = db.accounts.find_by_user(clerk_user_id)
        return accounts

    except Exception as e:
        logger.error(f"Error listing accounts: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/accounts")
async def create_account(account: AccountCreate, clerk_user_id: str = Depends(get_current_user_id)):
    """Create new account"""

    try:
        # Verify user exists
        user = db.users.find_by_clerk_id(clerk_user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Create account
        account_id = db.accounts.create_account(
            clerk_user_id=clerk_user_id,
            account_name=account.account_name,
            account_purpose=account.account_purpose,
            cash_balance=getattr(account, 'cash_balance', Decimal('0'))
        )

        # Return created account
        created_account = db.accounts.find_by_id(account_id)
        return created_account

    except Exception as e:
        logger.error(f"Error creating account: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/accounts/{account_id}")
async def update_account(account_id: str, account_update: AccountUpdate, clerk_user_id: str = Depends(get_current_user_id)):
    """Update account"""

    try:
        # Verify account belongs to user
        account = db.accounts.find_by_id(account_id)
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")

        # Verify ownership - accounts table stores clerk_user_id directly
        if account.get('clerk_user_id') != clerk_user_id:
            raise HTTPException(status_code=403, detail="Not authorized")

        # Update account
        update_data = account_update.model_dump(exclude_unset=True)
        db.accounts.update(account_id, update_data)

        # Return updated account
        updated_account = db.accounts.find_by_id(account_id)
        return updated_account

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating account: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/accounts/{account_id}")
async def delete_account(account_id: str, clerk_user_id: str = Depends(get_current_user_id)):
    """Delete an account and all its positions"""

    try:
        # Verify account belongs to user
        account = db.accounts.find_by_id(account_id)
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")

        # Verify ownership - accounts table stores clerk_user_id directly
        if account.get('clerk_user_id') != clerk_user_id:
            raise HTTPException(status_code=403, detail="Not authorized")

        # Delete all positions first (due to foreign key constraint)
        positions = db.positions.find_by_account(account_id)
        for position in positions:
            db.positions.delete(position['id'])

        # Delete the account
        db.accounts.delete(account_id)

        return {"message": "Account deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting account: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/accounts/{account_id}/positions")
async def list_positions(account_id: str, clerk_user_id: str = Depends(get_current_user_id)):
    """Get positions for account"""

    try:
        # Verify account belongs to user
        account = db.accounts.find_by_id(account_id)
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")

        # Verify ownership - accounts table stores clerk_user_id directly
        if account.get('clerk_user_id') != clerk_user_id:
            raise HTTPException(status_code=403, detail="Not authorized")

        positions = db.positions.find_by_account(account_id)

        # Format positions with instrument data for frontend
        formatted_positions = []
        for pos in positions:
            # Get full instrument data
            instrument = db.instruments.find_by_symbol(pos['symbol'])
            formatted_positions.append({
                **pos,
                'instrument': instrument
            })

        return {"positions": formatted_positions}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing positions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/positions")
async def create_position(position: PositionCreate, clerk_user_id: str = Depends(get_current_user_id)):
    """Create position"""

    try:
        # Verify account belongs to user
        account = db.accounts.find_by_id(position.account_id)
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")

        # Verify ownership - accounts table stores clerk_user_id directly
        if account.get('clerk_user_id') != clerk_user_id:
            raise HTTPException(status_code=403, detail="Not authorized")

        # Check if instrument exists, if not create it
        instrument = db.instruments.find_by_symbol(position.symbol.upper())
        if not instrument:
            logger.info(f"Creating new instrument: {position.symbol.upper()}")
            # Create a basic instrument entry with default allocations
            # Import the schema from database
            from src.schemas import InstrumentCreate

            # Determine type based on common patterns
            symbol_upper = position.symbol.upper()
            if len(symbol_upper) <= 5 and symbol_upper.isalpha():
                instrument_type = "stock"
            else:
                instrument_type = "etf"

            # Create instrument with basic default allocations
            # These can be updated later by the tagger agent
            new_instrument = InstrumentCreate(
                symbol=symbol_upper,
                name=f"{symbol_upper} - User Added",  # Basic name, can be updated later
                instrument_type=instrument_type,
                current_price=Decimal("0.00"),  # Price will be updated by background processes
                allocation_regions={"north_america": 100.0},  # Default to 100% NA
                allocation_sectors={"other": 100.0},  # Default to 100% other
                allocation_asset_class={"equity": 100.0} if instrument_type == "stock" else {"fixed_income": 100.0}
            )

            db.instruments.create_instrument(new_instrument)

        # Add position
        position_id = db.positions.add_position(
            account_id=position.account_id,
            symbol=position.symbol.upper(),
            quantity=position.quantity
        )

        # Return created position
        created_position = db.positions.find_by_id(position_id)
        return created_position

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating position: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/positions/{position_id}")
async def update_position(position_id: str, position_update: PositionUpdate, clerk_user_id: str = Depends(get_current_user_id)):
    """Update position"""

    try:
        # Get position and verify ownership
        position = db.positions.find_by_id(position_id)
        if not position:
            raise HTTPException(status_code=404, detail="Position not found")

        account = db.accounts.find_by_id(position['account_id'])
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")

        # Verify ownership - accounts table stores clerk_user_id directly
        if account.get('clerk_user_id') != clerk_user_id:
            raise HTTPException(status_code=403, detail="Not authorized")

        # Update position
        update_data = position_update.model_dump(exclude_unset=True)
        db.positions.update(position_id, update_data)

        # Return updated position
        updated_position = db.positions.find_by_id(position_id)
        return updated_position

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating position: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/positions/{position_id}")
async def delete_position(position_id: str, clerk_user_id: str = Depends(get_current_user_id)):
    """Delete position"""

    try:
        # Get position and verify ownership
        position = db.positions.find_by_id(position_id)
        if not position:
            raise HTTPException(status_code=404, detail="Position not found")

        account = db.accounts.find_by_id(position['account_id'])
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")

        # Verify ownership - accounts table stores clerk_user_id directly
        if account.get('clerk_user_id') != clerk_user_id:
            raise HTTPException(status_code=403, detail="Not authorized")

        db.positions.delete(position_id)
        return {"message": "Position deleted"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting position: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/instruments")
async def list_instruments(clerk_user_id: str = Depends(get_current_user_id)):
    """Get all available instruments for autocomplete"""

    try:
        instruments = db.instruments.find_all()
        # Return simplified list for autocomplete
        return [
            {
                "symbol": inst["symbol"],
                "name": inst["name"],
                "instrument_type": inst["instrument_type"],
                "current_price": float(inst["current_price"]) if inst.get("current_price") else None
            }
            for inst in instruments
        ]
    except Exception as e:
        logger.error(f"Error fetching instruments: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/analyze", response_model=AnalyzeResponse)
async def trigger_analysis(request: AnalyzeRequest, clerk_user_id: str = Depends(get_current_user_id)):
    """Trigger portfolio analysis"""

    try:
        # Get user
        user = db.users.find_by_clerk_id(clerk_user_id)

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Create job
        job_id = db.jobs.create_job(
            clerk_user_id=clerk_user_id,
            job_type="portfolio_analysis",
            request_payload=request.model_dump()
        )

        # Get the created job
        job = db.jobs.find_by_id(job_id)

        # Send to SQS
        if SQS_QUEUE_URL:
            message = {
                'job_id': str(job_id),
                'clerk_user_id': clerk_user_id,
                'analysis_type': request.analysis_type,
                'options': request.options
            }

            sqs_client.send_message(
                QueueUrl=SQS_QUEUE_URL,
                MessageBody=json.dumps(message)
            )
            logger.info(f"Sent analysis job to SQS: {job_id}")
        else:
            logger.warning("SQS_QUEUE_URL not configured, job created but not queued")

        return AnalyzeResponse(
            job_id=str(job_id),
            message="Analysis started. Check job status for results."
        )

    except Exception as e:
        logger.error(f"Error triggering analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/jobs/{job_id}")
async def get_job_status(job_id: str, clerk_user_id: str = Depends(get_current_user_id)):
    """Get job status and results"""

    try:
        # Get job
        job = db.jobs.find_by_id(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")

        # Verify job belongs to user - jobs table stores clerk_user_id directly
        if job.get('clerk_user_id') != clerk_user_id:
            raise HTTPException(status_code=403, detail="Not authorized")

        return job

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting job status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/jobs")
async def list_jobs(clerk_user_id: str = Depends(get_current_user_id)):
    """List user's analysis jobs"""

    try:
        # Get jobs for this user (with higher limit to avoid missing recent jobs)
        user_jobs = db.jobs.find_by_user(clerk_user_id, limit=100)
        # Sort by created_at descending (most recent first)
        user_jobs.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        return {"jobs": user_jobs}

    except Exception as e:
        logger.error(f"Error listing jobs: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/reset-accounts")
async def reset_accounts(clerk_user_id: str = Depends(get_current_user_id)):
    """Delete all accounts for the current user"""

    try:
        # Get user
        user = db.users.find_by_clerk_id(clerk_user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Get all accounts for user
        accounts = db.accounts.find_by_user(clerk_user_id)

        # Delete each account (positions will cascade delete)
        deleted_count = 0
        for account in accounts:
            try:
                # Positions are deleted automatically via CASCADE
                db.accounts.delete(account['id'])
                deleted_count += 1
            except Exception as e:
                logger.warning(f"Could not delete account {account['id']}: {e}")

        return {
            "message": f"Deleted {deleted_count} account(s)",
            "accounts_deleted": deleted_count
        }

    except Exception as e:
        logger.error(f"Error resetting accounts: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/populate-test-data")
async def populate_test_data(clerk_user_id: str = Depends(get_current_user_id)):
    """Populate test data for the current user"""

    try:
        # Get user
        user = db.users.find_by_clerk_id(clerk_user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Define missing instruments that might not be in the database
        missing_instruments = {
            "AAPL": {
                "name": "Apple Inc.",
                "type": "stock",
                "current_price": 195.89,
                "allocation_regions": {"north_america": 100},
                "allocation_sectors": {"technology": 100},
                "allocation_asset_class": {"equity": 100}
            },
            "AMZN": {
                "name": "Amazon.com Inc.",
                "type": "stock",
                "current_price": 178.35,
                "allocation_regions": {"north_america": 100},
                "allocation_sectors": {"consumer_discretionary": 100},
                "allocation_asset_class": {"equity": 100}
            },
            "NVDA": {
                "name": "NVIDIA Corporation",
                "type": "stock",
                "current_price": 522.74,
                "allocation_regions": {"north_america": 100},
                "allocation_sectors": {"technology": 100},
                "allocation_asset_class": {"equity": 100}
            },
            "MSFT": {
                "name": "Microsoft Corporation",
                "type": "stock",
                "current_price": 430.82,
                "allocation_regions": {"north_america": 100},
                "allocation_sectors": {"technology": 100},
                "allocation_asset_class": {"equity": 100}
            },
            "GOOGL": {
                "name": "Alphabet Inc. Class A",
                "type": "stock",
                "current_price": 173.69,
                "allocation_regions": {"north_america": 100},
                "allocation_sectors": {"technology": 100},
                "allocation_asset_class": {"equity": 100}
            },
        }

        # Check and add missing instruments
        for symbol, info in missing_instruments.items():
            existing = db.instruments.find_by_symbol(symbol)
            if not existing:
                try:
                    from src.schemas import InstrumentCreate

                    instrument_data = InstrumentCreate(
                        symbol=symbol,
                        name=info["name"],
                        instrument_type=info["type"],
                        current_price=Decimal(str(info["current_price"])),
                        allocation_regions=info["allocation_regions"],
                        allocation_sectors=info["allocation_sectors"],
                        allocation_asset_class=info["allocation_asset_class"]
                    )
                    db.instruments.create_instrument(instrument_data)
                    logger.info(f"Added missing instrument: {symbol}")
                except Exception as e:
                    logger.warning(f"Could not add instrument {symbol}: {e}")

        # Create accounts with test data
        accounts_data = [
            {
                "name": "401k Long-term",
                "purpose": "Primary retirement savings account with employer match",
                "cash": 5000.00,
                "positions": [
                    ("SPY", 150),   # S&P 500 ETF
                    ("VTI", 100),   # Total Stock Market ETF
                    ("BND", 200),   # Bond ETF
                    ("QQQ", 75),    # Nasdaq ETF
                    ("IWM", 50),    # Small Cap ETF
                ]
            },
            {
                "name": "Roth IRA",
                "purpose": "Tax-free retirement growth account",
                "cash": 2500.00,
                "positions": [
                    ("VTI", 80),    # Total Stock Market ETF
                    ("VXUS", 60),   # International Stock ETF
                    ("VNQ", 40),    # Real Estate ETF
                    ("GLD", 25),    # Gold ETF
                    ("TLT", 30),    # Long-term Treasury ETF
                    ("VIG", 45),    # Dividend Growth ETF
                ]
            },
            {
                "name": "Brokerage Account",
                "purpose": "Taxable investment account for individual stocks",
                "cash": 10000.00,
                "positions": [
                    ("TSLA", 15),   # Tesla
                    ("AAPL", 50),   # Apple
                    ("AMZN", 10),   # Amazon
                    ("NVDA", 25),   # Nvidia
                    ("MSFT", 30),   # Microsoft
                    ("GOOGL", 20),  # Google
                ]
            }
        ]

        created_accounts = []
        for account_data in accounts_data:
            # Create account
            account_id = db.accounts.create_account(
                clerk_user_id=clerk_user_id,
                account_name=account_data["name"],
                account_purpose=account_data["purpose"],
                cash_balance=Decimal(str(account_data["cash"]))
            )

            # Add positions
            for symbol, quantity in account_data["positions"]:
                try:
                    db.positions.add_position(
                        account_id=account_id,
                        symbol=symbol,
                        quantity=Decimal(str(quantity))
                    )
                except Exception as e:
                    logger.warning(f"Could not add position {symbol}: {e}")

            created_accounts.append(account_id)

        # Get all accounts with their positions for summary
        all_accounts = []
        for account_id in created_accounts:
            account = db.accounts.find_by_id(account_id)
            positions = db.positions.find_by_account(account_id)
            account['positions'] = positions
            all_accounts.append(account)

        return {
            "message": "Test data populated successfully",
            "accounts_created": len(created_accounts),
            "accounts": all_accounts
        }

    except Exception as e:
        logger.error(f"Error populating test data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Wellness Questionnaire Models - CFPB Financial Well-Being Scale
class WellnessQuestionnaireRequest(BaseModel):
    """New questionnaire format matching Streamlit questions"""
    age: str
    employment_status: str
    retirement_plan: str
    financial_goals: List[str]
    income_spending: str
    emergency_savings: str
    savings_cover: str
    debts: List[str]
    accounts: List[str]
    financial_confidence: str
    advisor: str

def calculate_wellness_scores_old(questionnaire_data: dict) -> dict:
    """Calculate wellness scores based on questionnaire responses"""
    
    # Pillar 1: Take Control of Finances (0-100)
    take_control_score = 0
    if questionnaire_data.get('savingsRate'):
        savings_rate = float(questionnaire_data['savingsRate'])
        if savings_rate >= 20:
            take_control_score += 40
        elif savings_rate >= 10:
            take_control_score += 30
        elif savings_rate >= 5:
            take_control_score += 20
        else:
            take_control_score += 10
    
    if questionnaire_data.get('hasBudget'):
        take_control_score += 25
    if questionnaire_data.get('tracksSpending'):
        take_control_score += 25
    
    # Bonus for good savings habits
    if questionnaire_data.get('savingsRate', 0) >= 15:
        take_control_score += 10
    
    take_control_score = min(100, take_control_score)
    
    # Pillar 2: Prepare for the Unexpected (0-100)
    prepare_unexpected_score = 0
    emergency_months = float(questionnaire_data.get('emergencyFundMonths', 0) or 0)
    if emergency_months >= 6:
        prepare_unexpected_score += 40
    elif emergency_months >= 3:
        prepare_unexpected_score += 30
    elif emergency_months >= 1:
        prepare_unexpected_score += 20
    else:
        prepare_unexpected_score += 10
    
    if questionnaire_data.get('hasHealthInsurance'):
        prepare_unexpected_score += 20
    if questionnaire_data.get('hasLifeInsurance'):
        prepare_unexpected_score += 20
    if questionnaire_data.get('hasDisabilityInsurance'):
        prepare_unexpected_score += 20
    
    prepare_unexpected_score = min(100, prepare_unexpected_score)
    
    # Pillar 3: Make Progress Toward Goals (0-100)
    goals_progress_score = 0
    if questionnaire_data.get('hasFinancialGoals'):
        goals_progress_score += 30
        
        goal_types = questionnaire_data.get('goalTypes', [])
        if isinstance(goal_types, list):
            goals_progress_score += min(30, len(goal_types) * 10)
        
        progress = float(questionnaire_data.get('progressOnGoals', 0) or 0)
        goals_progress_score += min(40, progress * 0.4)
    else:
        goals_progress_score = 20  # Base score for not having goals
    
    goals_progress_score = min(100, goals_progress_score)
    
    # Pillar 4: Long-Term Security (0-100)
    long_term_security_score = 0
    
    contribution_rate = float(questionnaire_data.get('retirementContributionRate', 0) or 0)
    if contribution_rate >= 15:
        long_term_security_score += 30
    elif contribution_rate >= 10:
        long_term_security_score += 25
    elif contribution_rate >= 5:
        long_term_security_score += 20
    else:
        long_term_security_score += 10
    
    retirement_balance = float(questionnaire_data.get('retirementAccountBalance', 0) or 0)
    years_until_retirement = int(questionnaire_data.get('yearsUntilRetirement', 0) or 0)
    
    # Score based on retirement balance relative to years until retirement
    if years_until_retirement > 0 and retirement_balance > 0:
        # Rough calculation: should have ~1x salary saved by 30, 3x by 40, etc.
        # Simplified: $50k per year until retirement is a good target
        target_balance = years_until_retirement * 50000
        if retirement_balance >= target_balance:
            long_term_security_score += 40
        elif retirement_balance >= target_balance * 0.5:
            long_term_security_score += 30
        elif retirement_balance >= target_balance * 0.25:
            long_term_security_score += 20
        else:
            long_term_security_score += 10
    else:
        long_term_security_score += 10
    
    if questionnaire_data.get('hasRetirementPlan'):
        long_term_security_score += 20
    
    long_term_security_score = min(100, long_term_security_score)
    
    # Overall score is average of all pillars
    overall_score = (
        take_control_score +
        prepare_unexpected_score +
        goals_progress_score +
        long_term_security_score
    ) / 4
    
    # Define pillar details
    def get_rating(score: float) -> str:
        if score >= 80:
            return "Excellent"
        elif score >= 70:
            return "Very Good"
        elif score >= 60:
            return "Good"
        elif score >= 50:
            return "Fair"
        else:
            return "Needs Improvement"
    
    pillars = [
        {
            "name": "Take Control of Finances",
            "score": round(take_control_score, 1),
            "rating": get_rating(take_control_score),
            "description": "Measures day-to-day money management, including budgeting, spending habits, and saving rate.",
            "improvementTip": "You're doing great! Continue maintaining your spending habits and savings rate." if take_control_score >= 80 else "Consider creating a monthly budget and tracking your spending to improve your financial control.",
            "color": "#10B981"  # Green
        },
        {
            "name": "Prepare for the Unexpected",
            "score": round(prepare_unexpected_score, 1),
            "rating": get_rating(prepare_unexpected_score),
            "description": "Evaluates readiness for financial emergencies and unexpected expenses through emergency funds and insurance.",
            "improvementTip": "Your emergency preparedness is excellent! Maintain your emergency fund and consider adequate insurance." if prepare_unexpected_score >= 80 else "Build an emergency fund covering 3-6 months of expenses and review your insurance coverage.",
            "color": "#209DD7"  # Blue
        },
        {
            "name": "Make Progress Toward Goals",
            "score": round(goals_progress_score, 1),
            "rating": get_rating(goals_progress_score),
            "description": "Tracks progress toward defined financial goals, such as saving for a home or education.",
            "improvementTip": "Set specific financial goals with clear timelines and create a plan to achieve them." if goals_progress_score < 70 else "Great progress! Keep tracking your goals and adjust your plan as needed.",
            "color": "#FFB707"  # Yellow
        },
        {
            "name": "Long-Term Security",
            "score": round(long_term_security_score, 1),
            "rating": get_rating(long_term_security_score),
            "description": "Assesses readiness for retirement and long-term financial stability through investments and retirement planning.",
            "improvementTip": "Review your retirement strategy to ensure you're on track for your desired retirement age." if long_term_security_score < 80 else "Excellent retirement planning! Continue contributing regularly to your retirement accounts.",
            "color": "#753991"  # Purple
        }
    ]
    
    return {
        "overall_score": round(overall_score, 1),
        "take_control_score": round(take_control_score, 1),
        "prepare_unexpected_score": round(prepare_unexpected_score, 1),
        "goals_progress_score": round(goals_progress_score, 1),
        "long_term_security_score": round(long_term_security_score, 1),
        "pillars": pillars
    }

# Scoring functions matching Streamlit code
def score_take_control(responses: dict) -> float:
    """Calculate Take Control of Finances score (0-100)"""
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
    """Calculate Prepare for the Unexpected score (0-100)"""
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
    """Calculate Make Progress Toward Goals score (0-100)"""
    score = 0
    
    goals = responses.get("financial_goals", [])
    for g in ["Saving for retirement", "Saving for education", "Saving for health care", "Saving for a big purchase, like a house or car"]:
        if g in goals:
            score += 15
    
    accounts = responses.get("accounts", [])
    score += min(len(accounts) * 5, 20)  # up to 20 points for accounts
    
    return min(score, 100)

def score_long_term_security(responses: dict) -> float:
    """Calculate Long-Term Security score (0-100)"""
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

@app.post("/api/wellness/questionnaire")
async def submit_wellness_questionnaire(
    data: WellnessQuestionnaireRequest,
    clerk_user_id: str = Depends(get_current_user_id)
):
    """Submit wellness questionnaire and calculate scores using Streamlit scoring logic"""
    try:
        # Validate required fields
        if not data.age or not data.age.strip():
            raise HTTPException(status_code=422, detail="Age is required")
        if not data.employment_status or not data.employment_status.strip():
            raise HTTPException(status_code=422, detail="Employment status is required")
        if not data.retirement_plan or not data.retirement_plan.strip():
            raise HTTPException(status_code=422, detail="Retirement plan is required")
        if not data.financial_goals or len(data.financial_goals) == 0:
            raise HTTPException(status_code=422, detail="At least one financial goal is required")
        if not data.income_spending or not data.income_spending.strip():
            raise HTTPException(status_code=422, detail="Income spending information is required")
        if not data.emergency_savings or not data.emergency_savings.strip():
            raise HTTPException(status_code=422, detail="Emergency savings information is required")
        if not data.savings_cover or not data.savings_cover.strip():
            raise HTTPException(status_code=422, detail="Savings cover information is required")
        if not data.debts or len(data.debts) == 0:
            raise HTTPException(status_code=422, detail="At least one debt type is required (or select 'None')")
        if not data.accounts or len(data.accounts) == 0:
            raise HTTPException(status_code=422, detail="At least one account type is required (or select 'None of the above')")
        if not data.financial_confidence or not data.financial_confidence.strip():
            raise HTTPException(status_code=422, detail="Financial confidence is required")
        if not data.advisor or not data.advisor.strip():
            raise HTTPException(status_code=422, detail="Advisor information is required")
        
        # Convert to dict for scoring functions
        responses = {
            "age": data.age.strip(),
            "employment_status": data.employment_status.strip(),
            "retirement_plan": data.retirement_plan.strip(),
            "financial_goals": data.financial_goals,
            "income_spending": data.income_spending.strip(),
            "emergency_savings": data.emergency_savings.strip(),
            "savings_cover": data.savings_cover.strip(),
            "debts": data.debts,
            "accounts": data.accounts,
            "financial_confidence": data.financial_confidence.strip(),
            "advisor": data.advisor.strip(),
        }
        
        # Calculate pillar scores
        take_control = score_take_control(responses)
        prepare_unexpected = score_prepare_unexpected(responses)
        progress_goals = score_progress_goals(responses)
        long_term_security = score_long_term_security(responses)
        
        # Overall score is average of all pillars
        overall_score = (take_control + prepare_unexpected + progress_goals + long_term_security) / 4
        
        # Define pillar details with ratings and colors matching Streamlit code
        def get_rating(score: float) -> str:
            """Get rating based on score: Excellent (80+), Good (60-79), Fair (40-59), Poor (<40)"""
            if score >= 80:
                return "Excellent"
            elif score >= 60:
                return "Good"
            elif score >= 40:
                return "Fair"
            else:
                return "Poor"
        
        def get_rating_color(rating: str) -> str:
            """Get color for rating"""
            colors = {
                "Excellent": "#2E7D32",  # Green
                "Good": "#1976D2",       # Blue
                "Fair": "#F9A825",       # Yellow
                "Poor": "#D32F2F"        # Red
            }
            return colors.get(rating, "#888")
        
        def get_bg_color(rating: str) -> str:
            """Get background color for pillar card"""
            colors = {
                "Excellent": "#E6F4EA",  # Light green
                "Good": "#E6F4FA",       # Light blue
                "Fair": "#FFF7E6",       # Light yellow
                "Poor": "#FFEBEE"        # Light red
            }
            return colors.get(rating, "#F5F5F5")
        
        # Pillar descriptions and tips matching Streamlit code
        pillar_descriptions = {
            "Take Control of Finances": "This score measures how well you manage your money day-to-day, including budgeting, spending habits, and saving rate.",
            "Prepare for the Unexpected": "This score evaluates your readiness for financial emergencies and unexpected expenses through emergency funds and insurance.",
            "Progress Toward Goals": "This score tracks how well you're progressing toward your defined financial goals, such as saving for a home or education.",
            "Long-Term Security": "This score assesses your readiness for retirement and long-term financial stability through investments and retirement planning.",
        }
        
        pillar_tips = {
            "Take Control of Finances": "You're doing great! Continue maintaining your spending habits and savings rate.",
            "Prepare for the Unexpected": "Your emergency preparedness is excellent! Maintain your emergency fund and consider adequate insurance.",
            "Progress Toward Goals": "Set specific financial goals with clear timelines and create a plan to achieve them.",
            "Long-Term Security": "Review your retirement strategy to ensure you're on track for your desired retirement age.",
        }
        
        # Create pillars array with proper formatting
        pillars = [
            {
                "name": "Take Control of Finances",
                "score": round(take_control, 1),
                "rating": get_rating(take_control),
                "description": pillar_descriptions["Take Control of Finances"],
                "improvementTip": pillar_tips["Take Control of Finances"],
                "color": get_rating_color(get_rating(take_control)),
                "bgColor": get_bg_color(get_rating(take_control))
            },
            {
                "name": "Prepare for the Unexpected",
                "score": round(prepare_unexpected, 1),
                "rating": get_rating(prepare_unexpected),
                "description": pillar_descriptions["Prepare for the Unexpected"],
                "improvementTip": pillar_tips["Prepare for the Unexpected"],
                "color": get_rating_color(get_rating(prepare_unexpected)),
                "bgColor": get_bg_color(get_rating(prepare_unexpected))
            },
            {
                "name": "Progress Toward Goals",
                "score": round(progress_goals, 1),
                "rating": get_rating(progress_goals),
                "description": pillar_descriptions["Progress Toward Goals"],
                "improvementTip": pillar_tips["Progress Toward Goals"],
                "color": get_rating_color(get_rating(progress_goals)),
                "bgColor": get_bg_color(get_rating(progress_goals))
            },
            {
                "name": "Long-Term Security",
                "score": round(long_term_security, 1),
                "rating": get_rating(long_term_security),
                "description": pillar_descriptions["Long-Term Security"],
                "improvementTip": pillar_tips["Long-Term Security"],
                "color": get_rating_color(get_rating(long_term_security)),
                "bgColor": get_bg_color(get_rating(long_term_security))
            }
        ]
        
        # Save questionnaire to database (convert to JSON for storage)
        try:
            # Validate age can be converted to int
            age_int = None
            if data.age.strip().isdigit():
                age_int = int(data.age.strip())
            elif data.age.strip():
                raise HTTPException(status_code=422, detail=f"Invalid age value: {data.age}")
            
            questionnaire_data = {
                "clerk_user_id": clerk_user_id,
                "age": age_int,
                "questionnaire_responses": responses,  # Store as dict - database client will cast to JSONB
            }
            
            logger.info(f"Saving questionnaire for user {clerk_user_id}")
            
            # Check if questionnaire exists
            try:
                existing = db.client.query_one(
                    "SELECT id FROM wellness_questionnaire WHERE clerk_user_id = :user_id",
                    db.client._build_parameters({'user_id': clerk_user_id})
                )
            except ClientError as query_error:
                error_code = query_error.response.get('Error', {}).get('Code', '')
                error_msg = query_error.response.get('Error', {}).get('Message', str(query_error))
                logger.error(f"Database ClientError - Code: {error_code}, Message: {error_msg}")
                
                if "does not exist" in error_msg or "relation" in error_msg.lower() or "wellness_questionnaire" in error_msg.lower() or error_code == "BadRequestException":
                    logger.error(f"Database table wellness_questionnaire does not exist: {error_msg}")
                    raise HTTPException(
                        status_code=503,
                        detail="Wellness feature not available. Database migration required. Please run: cd backend/database && uv run run_migrations.py"
                    )
                raise HTTPException(status_code=500, detail=f"Database query error: {error_msg}")
            except Exception as query_error:
                error_msg = str(query_error)
                error_type = type(query_error).__name__
                logger.error(f"Database query error - Type: {error_type}, Error: {error_msg}")
                
                if "does not exist" in error_msg or "relation" in error_msg.lower() or "wellness_questionnaire" in error_msg.lower():
                    logger.error(f"Database table wellness_questionnaire does not exist: {error_msg}")
                    raise HTTPException(
                        status_code=503,
                        detail="Database migration required: The wellness_questionnaire table does not exist. Please run the database migration: cd backend/database && uv run run_migrations.py"
                    )
                raise
            
            if existing:
                # Update existing questionnaire
                logger.info(f"Updating existing questionnaire for user {clerk_user_id}")
                db.client.update(
                    "wellness_questionnaire",
                    questionnaire_data,
                    "clerk_user_id = :user_id",
                    {'user_id': clerk_user_id}
                )
                questionnaire_id = str(existing['id'])  # Ensure it's a string UUID
            else:
                # Insert new questionnaire
                logger.info(f"Inserting new questionnaire for user {clerk_user_id}")
                questionnaire_id = str(db.client.insert(
                    "wellness_questionnaire",
                    questionnaire_data,
                    returning="id"
                ))  # Ensure it's a string UUID
        except HTTPException:
            # Re-raise HTTP exceptions
            raise
        except Exception as db_error:
            error_msg = str(db_error)
            error_type = type(db_error).__name__
            logger.error(f"Database error saving questionnaire - Type: {error_type}, Error: {error_msg}", exc_info=True)
            
            if "does not exist" in error_msg or "relation" in error_msg.lower() or "wellness_questionnaire" in error_msg.lower():
                raise HTTPException(
                    status_code=503,
                    detail="Wellness feature not available. Database migration required. Please run: cd backend/database && uv run run_migrations.py"
                )
            raise HTTPException(status_code=500, detail=f"Database error: {error_msg}")
        
        # Save scores
        try:
            # Ensure questionnaire_id is a string UUID
            questionnaire_id_str = str(questionnaire_id) if questionnaire_id else None
            
            scores_db_data = {
                "clerk_user_id": clerk_user_id,
                "questionnaire_id": questionnaire_id_str,  # Ensure it's a string for UUID detection
                "overall_score": Decimal(str(round(overall_score, 1))),
                "take_control_score": Decimal(str(round(take_control, 1))),
                "prepare_unexpected_score": Decimal(str(round(prepare_unexpected, 1))),
                "goals_progress_score": Decimal(str(round(progress_goals, 1))),
                "long_term_security_score": Decimal(str(round(long_term_security, 1))),
                "pillar_details": pillars,  # Store as dict - database client will cast to JSONB
            }
            
            logger.info(f"Saving wellness scores for user {clerk_user_id}, questionnaire_id: {questionnaire_id}")
            
            # Check if score exists
            try:
                existing_score = db.client.query_one(
                    "SELECT id FROM wellness_scores WHERE clerk_user_id = :user_id",
                    db.client._build_parameters({'user_id': clerk_user_id})
                )
            except ClientError as query_error:
                error_code = query_error.response.get('Error', {}).get('Code', '')
                error_msg = query_error.response.get('Error', {}).get('Message', str(query_error))
                logger.error(f"Database ClientError - Code: {error_code}, Message: {error_msg}")
                
                if "does not exist" in error_msg or "relation" in error_msg.lower() or "wellness_scores" in error_msg.lower() or error_code == "BadRequestException":
                    logger.error(f"Database table wellness_scores does not exist: {error_msg}")
                    raise HTTPException(
                        status_code=503,
                        detail="Database migration required: The wellness_scores table does not exist. Please run the database migration: cd backend/database && uv run run_migrations.py"
                    )
                raise HTTPException(status_code=500, detail=f"Database query error: {error_msg}")
            except Exception as query_error:
                error_msg = str(query_error)
                error_type = type(query_error).__name__
                logger.error(f"Database query error - Type: {error_type}, Error: {error_msg}")
                
                if "does not exist" in error_msg or "relation" in error_msg.lower() or "wellness_scores" in error_msg.lower():
                    logger.error(f"Database table wellness_scores does not exist: {error_msg}")
                    raise HTTPException(
                        status_code=503,
                        detail="Database migration required: The wellness_scores table does not exist. Please run the database migration: cd backend/database && uv run run_migrations.py"
                    )
                raise
            
            if existing_score:
                # Update existing score
                logger.info(f"Updating existing wellness score for user {clerk_user_id}")
                db.client.update(
                    "wellness_scores",
                    scores_db_data,
                    "clerk_user_id = :user_id",
                    {'user_id': clerk_user_id}
                )
            else:
                # Insert new score
                logger.info(f"Inserting new wellness score for user {clerk_user_id}")
                db.client.insert(
                    "wellness_scores",
                    scores_db_data
                )
        except HTTPException:
            # Re-raise HTTP exceptions
            raise
        except Exception as db_error:
            error_msg = str(db_error)
            error_type = type(db_error).__name__
            logger.error(f"Database error saving scores - Type: {error_type}, Error: {error_msg}", exc_info=True)
            
            if "does not exist" in error_msg or "relation" in error_msg.lower() or "wellness_scores" in error_msg.lower():
                raise HTTPException(
                    status_code=503,
                    detail="Wellness feature not available. Database migration required. Please run: cd backend/database && uv run run_migrations.py"
                )
            raise HTTPException(status_code=500, detail=f"Database error saving scores: {error_msg}")
        
        # Calculate NBA recommendations
        def get_nba_recommendations(responses: dict) -> list:
            """Get Next Best Actions based on questionnaire responses"""
            nba_map = {
                "Saving for retirement": "MATCH_1_NBA_1",
                "Reducing credit card debt": "DEBT_1_NBA_1",
                "Preparing for emergencies": "ES_1_NBA_1",
                "Paying off Student loans": "DEBT_1_NBA_3",
                "Saving for health care": "ES_2_NBA_1",
                "Saving for education": "ES_NBA_1",
                "Saving for a big purchase, like a house or car": "CASHFLOW_1_NBA_1",
                "Catching up after a late payment": "DEBT_1_NBA_4",
                "Paying my bills": "CASHFLOW_1_NBA_1"
            }
            
            recommended_nbas = []
            for goal in responses.get("financial_goals", []):
                nba = nba_map.get(goal)
                if nba and nba not in recommended_nbas:
                    recommended_nbas.append(nba)
            
            # Fallback to category-based NBAs if needed
            if not recommended_nbas:
                employment = responses.get("employment_status")
                retirement_timing = responses.get("retirement_plan")
                if employment == "Retired":
                    recommended_nbas = ["CASHFLOW_1_NBA_1", "DEBT_1_NBA_1", "DEBT_1_NBA_4"]
                elif retirement_timing == "in the next 5 years":
                    recommended_nbas = ["CASHFLOW_1_NBA_1", "MATCH_1_NBA_1", "MATCH_1_NBA_3"]
                else:
                    recommended_nbas = ["CASHFLOW_1_NBA_1", "MATCH_1_NBA_1", "MATCH_1_NBA_3"]
            
            return recommended_nbas
        
        def map_nba_to_agent(nba_code: str) -> dict:
            """Map NBA code to agent route and information"""
            # Map NBA codes to agents
            nba_to_agent = {
                "CASHFLOW_1_NBA_1": {
                    "agent": "goal-solver",
                    "name": "Goal Solver Agent",
                    "icon": "💰",
                    "description": "Set and achieve your financial goals"
                },
                "MATCH_1_NBA_1": {
                    "agent": "retirement-planning",
                    "name": "Retirement Planning Agent",
                    "icon": "📈",
                    "description": "Maximize your retirement savings"
                },
                "MATCH_1_NBA_3": {
                    "agent": "retirement-planning",
                    "name": "Retirement Planning Agent",
                    "icon": "📈",
                    "description": "Maximize your retirement savings"
                },
                "DEBT_1_NBA_1": {
                    "agent": "goal-solver",
                    "name": "Goal Solver Agent",
                    "icon": "💳",
                    "description": "Manage and reduce debt"
                },
                "DEBT_1_NBA_4": {
                    "agent": "goal-solver",
                    "name": "Goal Solver Agent",
                    "icon": "💳",
                    "description": "Manage and reduce debt"
                },
                "DEBT_1_NBA_3": {
                    "agent": "goal-solver",
                    "name": "Goal Solver Agent",
                    "icon": "🎓",
                    "description": "Pay off student loans"
                },
                "ES_1_NBA_1": {
                    "agent": "emergency-savings",
                    "name": "Emergency Savings Agent",
                    "icon": "🛟",
                    "description": "Build emergency savings"
                },
                "ES_2_NBA_1": {
                    "agent": "emergency-savings",
                    "name": "Emergency Savings Agent",
                    "icon": "🛟",
                    "description": "Build emergency savings"
                },
                "ES_NBA_1": {
                    "agent": "goal-solver",
                    "name": "Goal Solver Agent",
                    "icon": "🎯",
                    "description": "Set financial goals"
                },
                "SS_1_NBA_1": {
                    "agent": "social-security",
                    "name": "Social Security Agent",
                    "icon": "🧓",
                    "description": "Plan for Social Security benefits"
                },
                "RSP_2_NBA_1": {
                    "agent": "social-security",
                    "name": "Social Security Agent",
                    "icon": "🏖️",
                    "description": "Plan your retirement lifestyle"
                }
            }
            
            return nba_to_agent.get(nba_code, {
                "agent": "goal-solver",
                "name": "Goal Solver Agent",
                "icon": "💰",
                "description": "Get personalized financial guidance"
            })
        
        # Get NBA recommendations
        nba_codes = get_nba_recommendations(responses)
        
        # Map to agents and deduplicate
        nba_recommendations = []
        seen_agents = set()
        for nba_code in nba_codes:
            agent_info = map_nba_to_agent(nba_code)
            agent_key = agent_info["agent"]
            if agent_key not in seen_agents:
                seen_agents.add(agent_key)
                nba_recommendations.append({
                    "nba_code": nba_code,
                    "agent_route": f"/agents/{agent_info['agent']}",
                    "agent_name": agent_info["name"],
                    "icon": agent_info["icon"],
                    "description": agent_info["description"]
                })
        
        return {
            "message": "Questionnaire submitted successfully",
            "overall_score": round(overall_score, 1),
            "pillars": pillars,
            "nba_recommendations": nba_recommendations
        }
        
    except ValidationError as e:
        logger.error(f"Validation error in wellness questionnaire: {e}", exc_info=True)
        raise HTTPException(status_code=422, detail=f"Invalid questionnaire data: {str(e)}")
    except HTTPException:
        # Re-raise HTTP exceptions as-is (these already have proper error messages)
        raise
    except Exception as e:
        logger.error(f"Error submitting wellness questionnaire: {e}", exc_info=True)
        error_detail = str(e)
        error_type = type(e).__name__
        
        # Check if it's a database-related error
        if "does not exist" in error_detail or "relation" in error_detail.lower() or "wellness_questionnaire" in error_detail.lower() or "wellness_scores" in error_detail.lower():
            error_detail = "Database tables not found. Please run database migrations: cd backend/database && uv run run_migrations.py"
        elif "DatabaseErrorException" in error_type or "Database" in error_type:
            error_detail = f"Database error: {error_detail}"
        elif "KeyError" in error_type:
            error_detail = f"Missing required data: {error_detail}"
        elif "AttributeError" in error_type:
            error_detail = f"Configuration error: {error_detail}"
        
        logger.error(f"Full error details - Type: {error_type}, Detail: {error_detail}")
        logger.error(f"Full traceback:", exc_info=True)
        raise HTTPException(status_code=500, detail=error_detail)

@app.get("/api/wellness/score")
async def get_wellness_score(clerk_user_id: str = Depends(get_current_user_id)):
    """Get the user's wellness score"""
    try:
        # Check if table exists first (in case migration hasn't been run)
        try:
            score_data = db.client.query_one(
                "SELECT * FROM wellness_scores WHERE clerk_user_id = :user_id",
                db.client._build_parameters({'user_id': clerk_user_id})
            )
        except Exception as table_error:
            error_msg = str(table_error)
            if "does not exist" in error_msg or "relation" in error_msg.lower():
                logger.error(f"Wellness scores table does not exist. Migration may not have been run: {error_msg}")
                raise HTTPException(
                    status_code=503, 
                    detail="Database migration required: The wellness_scores table does not exist. Please run: cd backend/database && uv run run_migrations.py"
                )
            raise
        
        if not score_data:
            raise HTTPException(status_code=404, detail="Wellness score not found. Please complete the questionnaire first.")
        
        pillars = json.loads(score_data.get("pillar_details", "[]"))
        
        # Format updated_at timestamp
        updated_at = score_data.get("updated_at")
        if isinstance(updated_at, datetime):
            last_updated = updated_at.isoformat()
        elif isinstance(updated_at, str):
            last_updated = updated_at
        else:
            last_updated = str(updated_at)
        
        return {
            "overallScore": float(score_data["overall_score"]),
            "pillars": pillars,
            "lastUpdated": last_updated
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting wellness score: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to load wellness score: {str(e)}")

# Lambda handler
handler = Mangum(app)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)