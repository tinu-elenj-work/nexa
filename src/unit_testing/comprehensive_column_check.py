#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive Column Extraction Check
Verifies that ALL columns from ALL tables are being extracted correctly.
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

def comprehensive_column_check():
    """Comprehensive check of ALL columns being extracted from ALL tables"""
    print("🔍 COMPREHENSIVE Column Extraction Check")
    print("=" * 80)
    
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
        
        print(f"\n📋 Checking {len(extracted_tables)} tables for complete column extraction...")
        
        all_issues = []
        total_missing = 0
        
        for table_name in extracted_tables:
            print(f"\n{'='*60}")
            print(f"🔍 TABLE: {table_name.upper()}")
            print(f"{'='*60}")
            
            # Get actual schema from database
            actual_schema = client.get_table_schema(table_name)
            if actual_schema.empty:
                print(f"   ❌ Could not get schema for {table_name}")
                all_issues.append(f"{table_name}: Could not get schema")
                continue
            
            actual_columns = set(actual_schema['column_name'].tolist())
            print(f"   📊 Database schema has {len(actual_columns)} columns")
            
            # Get sample data to see what's actually being extracted
            try:
                # Use the appropriate extraction method
                if table_name == "allocations":
                    sample_data = client.get_allocations(simulation_id=30)
                elif table_name == "employees":
                    sample_data = client.get_employees(simulation_id=30)
                elif table_name == "projects":
                    sample_data = client.get_projects(simulation_id=30)
                elif table_name == "clients":
                    sample_data = client.get_clients(simulation_id=30)
                elif table_name == "confidences":
                    sample_data = client.get_confidences(simulation_id=30)
                elif table_name == "calendars":
                    sample_data = client.get_calendars(simulation_id=30)
                elif table_name == "calendar_holidays":
                    sample_data = client.get_calendar_holidays(simulation_id=30)
                elif table_name == "currencies":
                    sample_data = client.get_currencies(simulation_id=30)
                elif table_name == "exchange_rates":
                    sample_data = client.get_exchange_rates(simulation_id=30)
                elif table_name == "office":
                    sample_data = client.get_office(simulation_id=30)
                elif table_name == "salaries":
                    sample_data = client.get_salaries(simulation_id=30)
                elif table_name == "simulation":
                    sample_data = client.get_simulation(simulation_id=30)
                elif table_name == "titles":
                    sample_data = client.get_titles(simulation_id=30)
                else:
                    sample_data = client.get_table_sample(table_name, 1)
                
                if sample_data.empty:
                    print(f"   ⚠️  No data found in {table_name}")
                    continue
                
                extracted_columns = set(sample_data.columns.tolist())
                print(f"   📤 Currently extracting {len(extracted_columns)} columns")
                
                # Find missing columns
                missing_columns = actual_columns - extracted_columns
                extra_columns = extracted_columns - actual_columns
                
                if missing_columns:
                    print(f"   ❌ MISSING {len(missing_columns)} columns:")
                    for col in sorted(missing_columns):
                        col_info = actual_schema[actual_schema['column_name'] == col].iloc[0]
                        print(f"      - {col} ({col_info['data_type']}, nullable: {col_info['is_nullable']})")
                    all_issues.append(f"{table_name}: Missing {len(missing_columns)} columns: {sorted(missing_columns)}")
                    total_missing += len(missing_columns)
                else:
                    print(f"   ✅ All database columns are being extracted")
                
                if extra_columns:
                    print(f"   ℹ️  EXTRA {len(extra_columns)} columns (computed/joined): {sorted(extra_columns)}")
                
                # Show detailed column comparison
                print(f"\n   📋 DETAILED COLUMN COMPARISON:")
                print(f"   {'Column Name':<25} {'DB Schema':<8} {'Extracted':<8} {'Type':<20}")
                print(f"   {'-'*25} {'-'*8} {'-'*8} {'-'*20}")
                
                all_columns = sorted(actual_columns | extracted_columns)
                for col in all_columns:
                    in_schema = "✅" if col in actual_columns else "❌"
                    in_extracted = "✅" if col in extracted_columns else "❌"
                    
                    if col in actual_columns:
                        col_info = actual_schema[actual_schema['column_name'] == col].iloc[0]
                        col_type = col_info['data_type']
                    else:
                        col_type = "N/A"
                    
                    status = ""
                    if col in actual_columns and col not in extracted_columns:
                        status = " ❌ MISSING"
                    elif col not in actual_columns and col in extracted_columns:
                        status = " ℹ️  EXTRA"
                    elif col in actual_columns and col in extracted_columns:
                        status = " ✅ OK"
                    
                    print(f"   {col:<25} {in_schema:<8} {in_extracted:<8} {col_type:<20}{status}")
                
            except Exception as e:
                print(f"   ❌ Error extracting {table_name}: {e}")
                all_issues.append(f"{table_name}: Extraction error - {e}")
        
        # Summary
        print(f"\n{'='*80}")
        print(f"📊 COMPREHENSIVE SUMMARY")
        print(f"{'='*80}")
        print(f"   Tables checked: {len(extracted_tables)}")
        print(f"   Total missing columns: {total_missing}")
        print(f"   Tables with issues: {len(all_issues)}")
        
        if all_issues:
            print(f"\n❌ ISSUES FOUND:")
            for issue in all_issues:
                print(f"   - {issue}")
        else:
            print(f"\n✅ ALL TABLES ARE EXTRACTING ALL COLUMNS CORRECTLY!")
        
        return all_issues, total_missing
        
    except Exception as e:
        print(f"❌ Error in comprehensive check: {e}")
        import traceback
        traceback.print_exc()
        return None, None

if __name__ == "__main__":
    issues, missing_count = comprehensive_column_check()

