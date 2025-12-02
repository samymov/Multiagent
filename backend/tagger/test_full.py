#!/usr/bin/env python3
"""
Full test for Tagger agent via Lambda
"""

import os
import json
import boto3
from dotenv import load_dotenv

load_dotenv(override=True)

from src import Database

def test_tagger_lambda():
    """Test the Tagger agent via Lambda invocation"""
    
    db = Database()
    
    # Get region from environment or default to us-east-1
    aws_region = os.getenv('DEFAULT_AWS_REGION', os.getenv('AWS_REGION', 'us-east-1'))
    lambda_client = boto3.client('lambda', region_name=aws_region)
    
    # Test instruments that need tagging
    test_instruments = [
        {"symbol": "ARKK", "name": "ARK Innovation ETF"},
        {"symbol": "SOFI", "name": "SoFi Technologies Inc"},
        {"symbol": "TSLA", "name": "Tesla Inc"}
    ]
    
    print("Testing Tagger Lambda")
    print("=" * 60)
    print(f"Instruments to tag: {[i['symbol'] for i in test_instruments]}")
    
    # Invoke Lambda
    try:
        response = lambda_client.invoke(
            FunctionName='samy-tagger',
            InvocationType='RequestResponse',
            Payload=json.dumps({'instruments': test_instruments})
        )
        
        lambda_response = json.loads(response['Payload'].read())
        print(f"\nLambda Response: {json.dumps(lambda_response, indent=2)}")
        
        # Unwrap Lambda response format
        if isinstance(lambda_response, dict) and "statusCode" in lambda_response:
            if lambda_response["statusCode"] == 200:
                if isinstance(lambda_response.get("body"), str):
                    result = json.loads(lambda_response["body"])
                else:
                    result = lambda_response.get("body", {})
            else:
                print(f"\n❌ Lambda returned error status: {lambda_response['statusCode']}")
                print(f"   Body: {lambda_response.get('body', 'N/A')}")
                return
        else:
            result = lambda_response
        
        # Check for errors in the response
        if result.get('errors'):
            print(f"\n⚠️  Errors encountered:")
            for error in result['errors']:
                print(f"  - {error.get('symbol')}: {error.get('error')}")
        
        # Check if any instruments were tagged
        tagged_count = result.get('tagged', 0)
        if tagged_count == 0:
            print(f"\n⚠️  No instruments were tagged. This could mean:")
            print(f"  - The AI classification failed")
            print(f"  - The instruments couldn't be classified")
            print(f"  - Check CloudWatch logs for more details")
        else:
            print(f"\n✅ Successfully tagged {tagged_count} instrument(s)")
        
        # Check database for updated instruments
        print("\n✅ Checking database for tagged instruments:")
        for inst in test_instruments:
            instrument = db.instruments.find_by_symbol(inst['symbol'])
            if instrument:
                if instrument.get('allocation_asset_class'):
                    print(f"  ✅ {inst['symbol']}: Tagged successfully")
                    print(f"     Name: {instrument.get('name', 'N/A')}")
                    print(f"     Type: {instrument.get('instrument_type', 'N/A')}")
                    print(f"     Asset: {instrument.get('allocation_asset_class')}")
                    print(f"     Regions: {instrument.get('allocation_regions')}")
                else:
                    print(f"  ⚠️  {inst['symbol']}: Found in database but no allocations")
                    print(f"     This instrument exists but hasn't been classified yet")
            else:
                print(f"  ❌ {inst['symbol']}: Not found in database")
                print(f"     The tagger should create instruments, but this one wasn't created")
                
    except Exception as e:
        print(f"Error invoking Lambda: {e}")
    
    print("=" * 60)

if __name__ == "__main__":
    test_tagger_lambda()