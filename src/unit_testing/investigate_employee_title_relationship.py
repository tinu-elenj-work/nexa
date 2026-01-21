#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Investigate Employee-Title Relationship
Examines the database to find how employees relate to titles
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

def investigate_relationship():
    """Investigate the relationship between employees and titles"""
    
    print("=" * 70)
    print("Investigating Employee-Title Relationship")
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
        
        # 1. Check titles table structure
        print("\n" + "=" * 70)
        print("1. Titles Table Structure")
        print("=" * 70)
        
        titles_schema = client.get_table_schema('titles')
        if not titles_schema.empty:
            print(f"\nTitles table has {len(titles_schema)} columns:")
            for idx, row in titles_schema.iterrows():
                col_name = row.get('column_name', 'N/A')
                data_type = row.get('data_type', 'N/A')
                is_nullable = row.get('is_nullable', 'N/A')
                print(f"  {idx + 1}. {col_name} ({data_type}, nullable: {is_nullable})")
        
        # 2. Get sample data from both tables
        print("\n" + "=" * 70)
        print("2. Sample Data from Titles Table")
        print("=" * 70)
        
        titles_sample = client.get_table_sample('titles', 5)
        if not titles_sample.empty:
            print(f"\nSample titles data ({len(titles_sample)} rows):")
            print(titles_sample.to_string())
        
        print("\n" + "=" * 70)
        print("3. Sample Data from Employees Table")
        print("=" * 70)
        
        employees_sample = client.get_table_sample('employees', 5)
        if not employees_sample.empty:
            print(f"\nSample employees data ({len(employees_sample)} rows):")
            print(employees_sample.to_string())
        
        # 3. Check for common columns
        print("\n" + "=" * 70)
        print("4. Common Columns Analysis")
        print("=" * 70)
        
        titles_cols = set(titles_schema['column_name'].tolist()) if not titles_schema.empty else set()
        employees_schema = client.get_table_schema('employees')
        employees_cols = set(employees_schema['column_name'].tolist()) if not employees_schema.empty else set()
        
        common_cols = titles_cols.intersection(employees_cols)
        print(f"\nCommon columns between employees and titles: {common_cols}")
        
        # 4. Check if there's a relationship through allocations
        print("\n" + "=" * 70)
        print("5. Checking Allocations Table for Title Relationship")
        print("=" * 70)
        
        allocations_schema = client.get_table_schema('allocations')
        if not allocations_schema.empty:
            print(f"\nAllocations table columns:")
            for idx, row in allocations_schema.iterrows():
                col_name = row.get('column_name', 'N/A')
                data_type = row.get('data_type', 'N/A')
                if 'title' in col_name.lower():
                    print(f"  *** {col_name} ({data_type}) - TITLE RELATED!")
                else:
                    print(f"  {idx + 1}. {col_name} ({data_type})")
        
        # 5. Check for foreign key relationships
        print("\n" + "=" * 70)
        print("6. Checking Foreign Key Relationships")
        print("=" * 70)
        
        with client.get_connection() as conn:
            cursor = conn.cursor()
            
            # Check foreign keys for employees table
            cursor.execute("""
                SELECT
                    tc.table_name, 
                    kcu.column_name, 
                    ccu.table_name AS foreign_table_name,
                    ccu.column_name AS foreign_column_name 
                FROM information_schema.table_constraints AS tc 
                JOIN information_schema.key_column_usage AS kcu
                  ON tc.constraint_name = kcu.constraint_name
                JOIN information_schema.constraint_column_usage AS ccu
                  ON ccu.constraint_name = tc.constraint_name
                WHERE tc.constraint_type = 'FOREIGN KEY' 
                  AND tc.table_name = 'employees'
            """)
            fk_results = cursor.fetchall()
            
            if fk_results:
                print("\nForeign keys FROM employees table:")
                for row in fk_results:
                    print(f"  {row[1]} -> {row[2]}.{row[3]}")
            else:
                print("\nNo foreign keys found FROM employees table")
            
            # Check foreign keys for titles table
            cursor.execute("""
                SELECT
                    tc.table_name, 
                    kcu.column_name, 
                    ccu.table_name AS foreign_table_name,
                    ccu.column_name AS foreign_column_name 
                FROM information_schema.table_constraints AS tc 
                JOIN information_schema.key_column_usage AS kcu
                  ON tc.constraint_name = kcu.constraint_name
                JOIN information_schema.constraint_column_usage AS ccu
                  ON ccu.constraint_name = tc.constraint_name
                WHERE tc.constraint_type = 'FOREIGN KEY' 
                  AND tc.table_name = 'titles'
            """)
            fk_results = cursor.fetchall()
            
            if fk_results:
                print("\nForeign keys FROM titles table:")
                for row in fk_results:
                    print(f"  {row[1]} -> {row[2]}.{row[3]}")
            else:
                print("\nNo foreign keys found FROM titles table")
            
            # Check if any table references employees or titles
            cursor.execute("""
                SELECT
                    tc.table_name, 
                    kcu.column_name, 
                    ccu.table_name AS foreign_table_name,
                    ccu.column_name AS foreign_column_name 
                FROM information_schema.table_constraints AS tc 
                JOIN information_schema.key_column_usage AS kcu
                  ON tc.constraint_name = kcu.constraint_name
                JOIN information_schema.constraint_column_usage AS ccu
                  ON ccu.constraint_name = tc.constraint_name
                WHERE tc.constraint_type = 'FOREIGN KEY' 
                  AND (ccu.table_name = 'employees' OR ccu.table_name = 'titles')
            """)
            fk_results = cursor.fetchall()
            
            if fk_results:
                print("\nForeign keys TO employees or titles:")
                for row in fk_results:
                    print(f"  {row[0]}.{row[1]} -> {row[2]}.{row[3]}")
        
        # 6. Check if titles are linked through simulation_id
        print("\n" + "=" * 70)
        print("7. Checking Simulation ID Relationship")
        print("=" * 70)
        
        if 'simulation_id' in titles_cols and 'simulation_id' in employees_cols:
            print("\nBoth tables have simulation_id - checking if they share values...")
            
            with client.get_connection() as conn:
                cursor = conn.cursor()
                
                # Get unique simulation_ids from both tables
                cursor.execute("SELECT DISTINCT simulation_id FROM employees WHERE simulation_id IS NOT NULL")
                employee_sim_ids = [row[0] for row in cursor.fetchall()]
                
                cursor.execute("SELECT DISTINCT simulation_id FROM titles WHERE simulation_id IS NOT NULL")
                title_sim_ids = [row[0] for row in cursor.fetchall()]
                
                common_sim_ids = set(employee_sim_ids).intersection(set(title_sim_ids))
                
                print(f"  Employees simulation_ids: {sorted(employee_sim_ids)}")
                print(f"  Titles simulation_ids: {sorted(title_sim_ids)}")
                print(f"  Common simulation_ids: {sorted(common_sim_ids)}")
                
                if common_sim_ids:
                    print(f"\n  Both tables share simulation_ids - they may be related through simulation context")
        
        # 7. Check allocations for title relationship
        print("\n" + "=" * 70)
        print("8. Checking Allocations for Title Columns")
        print("=" * 70)
        
        allocations_sample = client.get_table_sample('allocations', 3)
        if not allocations_sample.empty:
            print(f"\nAllocations sample data:")
            print(allocations_sample.to_string())
            
            title_related_cols = [col for col in allocations_sample.columns if 'title' in col.lower()]
            if title_related_cols:
                print(f"\n  Found title-related columns in allocations: {title_related_cols}")
            else:
                print(f"\n  No title-related columns found in allocations")
        
        # Summary
        print("\n" + "=" * 70)
        print("Summary")
        print("=" * 70)
        print("\nFindings:")
        print("1. Employees table columns:", sorted(employees_cols))
        print("2. Titles table columns:", sorted(titles_cols))
        print("3. Common columns:", sorted(common_cols))
        
        if 'simulation_id' in common_cols:
            print("\n4. Both tables have simulation_id - relationship may be through simulation context")
        
        if not common_cols or 'simulation_id' not in common_cols:
            print("\n5. No direct foreign key relationship found between employees and titles")
            print("   Titles may be reference data linked through simulation_id or another mechanism")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    investigate_relationship()

