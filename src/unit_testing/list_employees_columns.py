#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
List Employees Table Columns
Queries the Vision database to show all columns in the employees table
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

def list_employees_columns():
    """List all columns in the employees table"""
    
    print("=" * 70)
    print("Employees Table Schema - Vision Database")
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
        
        # Get table schema
        print("\nFetching employees table schema...")
        schema_df = client.get_table_schema('employees')
        
        if schema_df.empty:
            print("ERROR: Could not retrieve schema for employees table")
            return
        
        print(f"\nFound {len(schema_df)} columns in employees table:")
        print("=" * 70)
        
        # Display columns with details
        for idx, row in schema_df.iterrows():
            col_name = row.get('column_name', 'N/A')
            data_type = row.get('data_type', 'N/A')
            is_nullable = row.get('is_nullable', 'N/A')
            column_default = row.get('column_default', 'N/A')
            
            print(f"\n{idx + 1}. {col_name}")
            print(f"   Type: {data_type}")
            print(f"   Nullable: {is_nullable}")
            if column_default and str(column_default) != 'None':
                print(f"   Default: {column_default}")
        
        # Also get a sample row to see actual data
        print("\n" + "=" * 70)
        print("Sample Data (first row):")
        print("=" * 70)
        
        sample_df = client.get_table_sample('employees', 1)
        if not sample_df.empty:
            print(f"\nColumns with data:")
            for col in sample_df.columns:
                value = sample_df[col].iloc[0]
                value_str = str(value) if pd.notna(value) else 'NULL'
                if len(value_str) > 50:
                    value_str = value_str[:50] + '...'
                print(f"  {col}: {value_str}")
        else:
            print("No data found in employees table")
        
        # Summary
        print("\n" + "=" * 70)
        print("Summary")
        print("=" * 70)
        print(f"Total columns: {len(schema_df)}")
        print(f"\nColumn names:")
        col_names = schema_df['column_name'].tolist()
        for i, col in enumerate(col_names, 1):
            print(f"  {i}. {col}")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    list_employees_columns()

