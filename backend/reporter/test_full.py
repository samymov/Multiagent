#!/usr/bin/env python3
"""
Full test for Reporter agent via Lambda
"""

import os
import json
import boto3
import time
from dotenv import load_dotenv

load_dotenv(override=True)

from src import Database
from src.schemas import JobCreate

def test_reporter_lambda():
    """Test the Reporter agent via Lambda invocation"""
    
    db = Database()
    
    # Get region from environment or default to us-east-1
    aws_region = os.getenv('DEFAULT_AWS_REGION', os.getenv('AWS_REGION', 'us-east-1'))
    lambda_client = boto3.client('lambda', region_name=aws_region)
    
    # Create test job
    test_user_id = "test_user_001"
    
    job_create = JobCreate(
        clerk_user_id=test_user_id,
        job_type="portfolio_analysis",
        request_payload={"analysis_type": "test", "test": True}
    )
    job_id = db.jobs.create(job_create.model_dump())
    
    print(f"Testing Reporter Lambda with job {job_id}")
    print("=" * 60)
    
    # Invoke Lambda
    try:
        response = lambda_client.invoke(
            FunctionName='samy-reporter',
            InvocationType='RequestResponse',
            Payload=json.dumps({'job_id': job_id})
        )
        
        result = json.loads(response['Payload'].read())
        print(f"Lambda Response: {json.dumps(result, indent=2)}")
        
        # Unwrap Lambda response format
        if isinstance(result, dict) and "statusCode" in result:
            if result["statusCode"] == 200:
                if isinstance(result.get("body"), str):
                    lambda_body = json.loads(result["body"])
                else:
                    lambda_body = result.get("body", {})
            else:
                print(f"\n❌ Lambda returned error status: {result['statusCode']}")
                print(f"   Body: {result.get('body', 'N/A')}")
                return
        else:
            lambda_body = result
        
        # Check database for results
        time.sleep(2)  # Give it a moment
        job = db.jobs.find_by_id(job_id)
        
        if job and job.get('report_payload'):
            print("\n✅ Report generated successfully!")
            report_payload = job['report_payload']
            
            # Handle report_payload - it might be a dict with 'content' or 'analysis' key, or a string
            if isinstance(report_payload, dict):
                # Try to find the actual report content
                report_content = report_payload.get('content') or report_payload.get('analysis') or report_payload.get('final_output') or str(report_payload)
            else:
                report_content = str(report_payload)
            
            # Show preview
            if isinstance(report_content, str) and len(report_content) > 500:
                print(f"Report preview (first 500 chars):\n{report_content[:500]}...")
            else:
                print(f"Report content:\n{report_content}")
        else:
            print("\n❌ No report found in database")
            
    except Exception as e:
        print(f"Error invoking Lambda: {e}")
    
    print("=" * 60)

if __name__ == "__main__":
    test_reporter_lambda()