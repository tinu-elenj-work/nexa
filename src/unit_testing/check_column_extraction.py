#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Check Column Extraction
Verifies that all columns are being extracted for each table in Vision database.
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

def check_column_extraction():
    """Check if all columns are being extracted for each table"""
    print("🔍 Vision Database Column Extraction Check")
    print("=" * 60)
    
    try:
        # Create database client
        print("🔗 Connecting to Vision database...")
        client = VisionDBClient(**VISION_DB_CONFIG)
        
        if not client.test_connection():
            print("❌ Failed to connect to Vision database")
            return
        
        print("✅ Database connection successful!")
        
        # Tables being extracted
        extracted_tables = [
            "allocations", "employees", "projects", "clients", "confidences",
            "calendars", "calendar_holidays", "currencies", "exchange_rates",
            "office", "salaries", "simulation", "titles"
        ]
        
        print(f"\n📋 Checking {len(extracted_tables)} tables for column completeness...")
        
        for table_name in extracted_tables:
            print(f"\n🔍 Checking table: {table_name}")
            print("-" * 40)
            
            # Get actual schema from database
            actual_schema = client.get_table_schema(table_name)
            if actual_schema.empty:
                print(f"   ❌ Could not get schema for {table_name}")
                continue
            
            actual_columns = set(actual_schema['column_name'].tolist())
            print(f"   📊 Database has {len(actual_columns)} columns: {sorted(actual_columns)}")
            
            # Get sample data to see what's actually being extracted
            sample_data = client.get_table_sample(table_name, 1)
            if sample_data.empty:
                print(f"   ⚠️  No data found in {table_name}")
                continue
            
            extracted_columns = set(sample_data.columns.tolist())
            print(f"   📤 Currently extracting {len(extracted_columns)} columns: {sorted(extracted_columns)}")
            
            # Find missing columns
            missing_columns = actual_columns - extracted_columns
            extra_columns = extracted_columns - actual_columns
            
            if missing_columns:
                print(f"   ❌ MISSING {len(missing_columns)} columns: {sorted(missing_columns)}")
            else:
                print(f"   ✅ All database columns are being extracted")
            
            if extra_columns:
                print(f"   ⚠️  EXTRA {len(extra_columns)} columns (computed/joined): {sorted(extra_columns)}")
            
            # Show column details
            print(f"   📋 Column details:")
            for _, col in actual_schema.iterrows():
                col_name = col['column_name']
                data_type = col['data_type']
                is_nullable = col['is_nullable']
                status = "✅" if col_name in extracted_columns else "❌"
                print(f"      {status} {col_name} ({data_type}, nullable: {is_nullable})")
        
        print(f"\n📊 Summary:")
        print(f"   Tables checked: {len(extracted_tables)}")
        
    except Exception as e:
        print(f"❌ Error checking column extraction: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_column_extraction()
