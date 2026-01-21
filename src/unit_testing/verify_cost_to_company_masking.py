#!/usr/bin/env python3
"""
Verify that cost_to_company column is being masked with the correct range
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

import pandas as pd
from vision_db_client import VisionDBClient
from config import VISION_DB_CONFIG

def verify_cost_to_company_masking():
    """Verify that cost_to_company masking is working correctly"""
    
    print("Verifying cost_to_company masking...")
    print("=" * 50)
    
    try:
        # Connect to database
        client = VisionDBClient(VISION_DB_CONFIG)
        
        # Get original salaries data
        print("1. Getting original salaries data...")
        original_salaries = client.get_salaries(simulation_id=30)
        print(f"   Retrieved {len(original_salaries)} salary records")
        
        if 'cost_to_company' in original_salaries.columns:
            print(f"   cost_to_company column found!")
            print(f"   Original cost_to_company range: {original_salaries['cost_to_company'].min()} - {original_salaries['cost_to_company'].max()}")
            print(f"   Non-null cost_to_company values: {original_salaries['cost_to_company'].notna().sum()}")
            
            # Show sample of original values
            sample_original = original_salaries[['employee_id', 'cost_to_company']].head(5)
            print(f"\n   Sample original cost_to_company values:")
            print(sample_original.to_string(index=False))
            
        else:
            print("   cost_to_company column not found in salaries table")
            print(f"   Available columns: {list(original_salaries.columns)}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    verify_cost_to_company_masking()
