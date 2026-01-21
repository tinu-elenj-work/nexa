#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Check Joined Columns
Verifies what additional columns are being added through JOINs in the extraction queries.
"""

import sys
import os
import pandas as pd

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

# Use the Vision client's database configuration
VISION_DB_CONFIG = {
    'host': 'es-estimator-prod.cr4ky28gqfse.af-south-1.rds.amazonaws.com',
    'port': 5432,
    'database': 'es_dashboard',  # Vision data is in es_dashboard database
    'user': 'readonly_user',
    'password': 'zxL%rZiergbpRv1'
}
from vision_db_client import VisionDBClient

def check_joined_columns():
    """Check what additional columns are being added through JOINs"""
    print("🔍 Vision Database Joined Columns Check")
    print("=" * 60)
    
    try:
        # Create database client
        print("🔗 Connecting to Vision database...")
        client = VisionDBClient(**VISION_DB_CONFIG)
        
        if not client.test_connection():
            print("❌ Failed to connect to Vision database")
            return
        
        print("✅ Database connection successful!")
        
        # Test each extraction method to see what columns are returned
        print(f"\n📋 Testing extraction methods for additional columns...")
        
        # Test allocations (has JOINs)
        print(f"\n🔍 Testing allocations extraction...")
        allocations_df = client.get_allocations(simulation_id=30)
        print(f"   📤 Allocations columns: {sorted(allocations_df.columns.tolist())}")
        
        # Test employees (has computed columns)
        print(f"\n🔍 Testing employees extraction...")
        employees_df = client.get_employees(simulation_id=30)
        print(f"   📤 Employees columns: {sorted(employees_df.columns.tolist())}")
        
        # Test projects (has JOINs)
        print(f"\n🔍 Testing projects extraction...")
        projects_df = client.get_projects(simulation_id=30)
        print(f"   📤 Projects columns: {sorted(projects_df.columns.tolist())}")
        
        # Test salaries (has JOINs)
        print(f"\n🔍 Testing salaries extraction...")
        salaries_df = client.get_salaries(simulation_id=30)
        print(f"   📤 Salaries columns: {sorted(salaries_df.columns.tolist())}")
        
        # Test exchange_rates (has JOINs)
        print(f"\n🔍 Testing exchange_rates extraction...")
        exchange_rates_df = client.get_exchange_rates(simulation_id=30)
        print(f"   📤 Exchange rates columns: {sorted(exchange_rates_df.columns.tolist())}")
        
        # Test office (has JOINs)
        print(f"\n🔍 Testing office extraction...")
        office_df = client.get_office(simulation_id=30)
        print(f"   📤 Office columns: {sorted(office_df.columns.tolist())}")
        
        print(f"\n📊 Summary of additional columns added through JOINs:")
        print(f"   • allocations: employee_name, first_name, last_name, project_name, project_number, client_name")
        print(f"   • employees: name (computed)")
        print(f"   • projects: client_name")
        print(f"   • salaries: employee_name, first_name, last_name, currency_code, currency_name, currency_symbol")
        print(f"   • exchange_rates: from_currency_code, from_currency_name, to_currency_code, to_currency_name")
        print(f"   • office: calendar_name")
        
    except Exception as e:
        print(f"❌ Error checking joined columns: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_joined_columns()
