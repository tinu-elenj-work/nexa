#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Check Salaries Table Structure
Examines the salaries table to see how titles are stored
"""

import sys
import os
import pandas as pd
import warnings

# Suppress warnings
warnings.filterwarnings('ignore')

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from config import VISION_DB_CONFIG
from vision_db_client import VisionDBClient

def check_salaries_structure():
    """Check salaries table structure and title relationship"""
    
    print("=" * 70)
    print("Salaries Table Structure - Vision Database")
    print("=" * 70)
    
    try:
        # Create database client
        print("\nConnecting to Vision database...")
        client = VisionDBClient(
            host=VISION_DB_CONFIG['host'],
            port=VISION_DB_CONFIG['port'],
            database=VISION_DB_CONFIG['database'],
            user=VISION_DB_CONFIG['user'],
            password=VISION_DB_CONFIG['password']
        )
        
        if not client.test_connection():
            print("ERROR: Failed to connect to Vision database")
            return
        
        print("Connected successfully!")
        
        # Get salaries table schema
        print("\nFetching salaries table schema...")
        schema_df = client.get_table_schema('salaries')
        
        if schema_df.empty:
            print("ERROR: Could not retrieve schema for salaries table")
            return
        
        print(f"\nFound {len(schema_df)} columns in salaries table:")
        print("=" * 70)
        
        # Display columns with details
        for idx, row in schema_df.iterrows():
            col_name = row.get('column_name', 'N/A')
            data_type = row.get('data_type', 'N/A')
            is_nullable = row.get('is_nullable', 'N/A')
            
            title_related = '*** TITLE RELATED!' if 'title' in col_name.lower() else ''
            print(f"\n{idx + 1}. {col_name} {title_related}")
            print(f"   Type: {data_type}")
            print(f"   Nullable: {is_nullable}")
        
        # Get sample data
        print("\n" + "=" * 70)
        print("Sample Data from Salaries Table (10 rows):")
        print("=" * 70)
        
        sample_df = client.get_table_sample('salaries', 10)
        if not sample_df.empty:
            print(f"\n{sample_df.to_string()}")
            
            # Check for title column
            title_cols = [col for col in sample_df.columns if 'title' in col.lower()]
            if title_cols:
                print(f"\nTitle-related columns found: {title_cols}")
                print(f"\nUnique titles in sample:")
                for col in title_cols:
                    unique_titles = sample_df[col].dropna().unique()
                    print(f"  {col}: {unique_titles[:10]}")
        
        # Check relationship to employees
        print("\n" + "=" * 70)
        print("Checking Employee Relationship")
        print("=" * 70)
        
        employee_id_cols = [col for col in schema_df['column_name'] if 'employee' in col.lower() or col == 'id']
        print(f"Employee-related columns: {employee_id_cols}")
        
        # Check for date columns to determine "latest"
        date_cols = [col for col in schema_df['column_name'] if 'date' in col.lower() or 'start' in col.lower() or 'end' in col.lower()]
        print(f"Date/Time columns (for determining 'latest'): {date_cols}")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_salaries_structure()

