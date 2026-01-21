#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Check Vision Database Tables
Compares current database tables with what's being extracted to identify new tables.
"""

import sys
import os
import pandas as pd
import warnings
import logging
import argparse
from datetime import datetime
from pathlib import Path

# Suppress pandas warnings about SQLAlchemy
warnings.filterwarnings('ignore', category=UserWarning, module='pandas')

# Suppress logging from vision_db_client
logging.getLogger('vision_db_client').setLevel(logging.ERROR)

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

# Import configuration from config file
from config import VISION_DB_CONFIG
from vision_db_client import VisionDBClient

# Import table extraction configuration from extractor script
from extract_vision_data_enhanced import CURRENT_EXTRACTED_TABLES, EXCLUDED_TABLES

def get_current_extracted_tables():
    """Get list of tables currently being extracted by the vision_data_extractor.py"""
    return CURRENT_EXTRACTED_TABLES.copy()

def diagnose_connection(client, verbose=False):
    """Diagnose database connection and schema issues"""
    if verbose:
        print("\n🔍 Connection Diagnostics")
        print("-" * 50)
    
    try:
        with client.get_connection() as conn:
            cursor = conn.cursor()
            
            # 1. Check current database
            cursor.execute("SELECT current_database()")
            current_db = cursor.fetchone()[0]
            
            # 2. Check current user
            cursor.execute("SELECT current_user")
            current_user = cursor.fetchone()[0]
            
            # 3. Check available schemas
            cursor.execute("""
                SELECT schema_name 
                FROM information_schema.schemata 
                WHERE schema_name NOT IN ('pg_catalog', 'information_schema', 'pg_toast')
                ORDER BY schema_name
            """)
            schemas = [row[0] for row in cursor.fetchall()]
            
            # 4. Check table count per schema
            schema_counts = {}
            for schema in schemas:
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM information_schema.tables 
                    WHERE table_schema = %s
                """, (schema,))
                count = cursor.fetchone()[0]
                if count > 0:
                    schema_counts[schema] = count
            
            # Only show diagnostics if there's an issue or verbose mode
            if verbose or current_db != VISION_DB_CONFIG['database']:
                print(f"   📊 Database: {current_db} (expected: {VISION_DB_CONFIG['database']})")
                if current_db != VISION_DB_CONFIG['database']:
                    print(f"   ⚠️  WARNING: Connected to different database!")
                print(f"   👤 User: {current_user}")
                print(f"   📁 Schemas: {', '.join(schemas) if schemas else 'None'}")
                for schema, count in schema_counts.items():
                    print(f"      - {schema}: {count} tables")
            
            return schemas, current_db
            
    except Exception as e:
        print(f"   ❌ Error during diagnostics: {e}")
        return [], None

def get_all_tables_from_all_schemas(client, schemas):
    """Get all tables from all available schemas"""
    all_tables = []
    schema_tables = {}
    
    try:
        with client.get_connection() as conn:
            cursor = conn.cursor()
            
            for schema in schemas:
                cursor.execute("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = %s
                    ORDER BY table_name
                """, (schema,))
                tables = [row[0] for row in cursor.fetchall()]
                if tables:
                    schema_tables[schema] = tables
                    all_tables.extend(tables)
            
    except Exception as e:
        print(f"   ❌ Error getting tables from schemas: {e}")
    
    return all_tables, schema_tables

def get_table_columns(client, table_name):
    """Get all columns for a specific table"""
    try:
        schema_df = client.get_table_schema(table_name)
        if not schema_df.empty:
            return set(schema_df['column_name'].tolist())
    except Exception as e:
        print(f"   ⚠️  Error getting columns for {table_name}: {e}")
    return set()

def get_columns_from_excel(excel_filepath):
    """Get columns from an existing Excel extraction file"""
    column_info = {}
    
    try:
        if not os.path.exists(excel_filepath):
            print(f"   ❌ Excel file not found: {excel_filepath}")
            return column_info
        
        print(f"   📂 Reading columns from: {os.path.basename(excel_filepath)}")
        excel_file = pd.ExcelFile(excel_filepath)
        
        for sheet_name in excel_file.sheet_names:
            # Normalize sheet name (lowercase, remove spaces)
            normalized_name = sheet_name.lower().strip()
            
            # Read just the header row to get columns
            df = pd.read_excel(excel_filepath, sheet_name=sheet_name, nrows=0)
            columns = set(df.columns.tolist())
            
            if columns:
                column_info[normalized_name] = columns
                print(f"      ✅ {sheet_name}: {len(columns)} columns")
        
        return column_info
        
    except Exception as e:
        print(f"   ❌ Error reading Excel file: {e}")
        return column_info

def check_table_columns(client, current_tables, all_tables_base, excel_filepath=None):
    """Check columns for all extracted tables and compare with Excel if provided"""
    print(f"\n📊 Checking Columns for Extracted Tables...")
    print("-" * 50)
    
    column_info = {}
    excel_column_info = {}
    
    # Get columns from database
    db_column_info = {}
    if client:
        for table in sorted(current_tables):
            if table not in all_tables_base:
                continue  # Skip missing tables
            
            columns = get_table_columns(client, table)
            if columns:
                db_column_info[table] = columns
                print(f"   ✅ {table}: {len(columns)} columns (database)")
    
    # Get columns from Excel file if provided
    if excel_filepath:
        print(f"\n   📂 Comparing with Excel file columns...")
        excel_column_info = get_columns_from_excel(excel_filepath)
    
    # Compare database columns with Excel columns to find new columns
    if db_column_info and excel_column_info:
        print(f"\n🔍 Comparing Database vs Excel Columns...")
        print("-" * 50)
        
        new_columns_found = False
        for table in sorted(current_tables):
            if table not in db_column_info:
                continue
            
            db_cols = db_column_info[table]
            excel_cols = excel_column_info.get(table, set())
            
            # Normalize column names for comparison (case-insensitive, handle spaces/underscores)
            def normalize_col_name(name):
                """Normalize column name for comparison"""
                return name.lower().strip().replace(' ', '_').replace('-', '_')
            
            db_cols_normalized = {normalize_col_name(col): col for col in db_cols}
            excel_cols_normalized = {normalize_col_name(col): col for col in excel_cols}
            
            new_cols_normalized = set(db_cols_normalized.keys()) - set(excel_cols_normalized.keys())
            missing_cols_normalized = set(excel_cols_normalized.keys()) - set(db_cols_normalized.keys())
            
            if new_cols_normalized:
                new_columns_found = True
                # Find original case column names
                new_cols_original = [db_cols_normalized[norm] for norm in sorted(new_cols_normalized)]
                print(f"   🆕 {table}: {len(new_cols_original)} NEW columns in database:")
                for col in new_cols_original:
                    print(f"      + {col}")
            
            if missing_cols_normalized:
                # Find original case column names
                missing_cols_original = [excel_cols_normalized[norm] for norm in sorted(missing_cols_normalized)]
                print(f"   ⚠️  {table}: {len(missing_cols_original)} columns in Excel but not in database:")
                for col in missing_cols_original:
                    print(f"      - {col} (likely computed/joined column)")
        
        if not new_columns_found:
            print(f"   ✅ No new columns found - Excel matches database schema")
    
    # Return database columns if available, otherwise Excel columns
    return db_column_info if db_column_info else excel_column_info

def check_vision_tables(excel_filepath=None):
    """Check for new tables in Vision database
    
    Args:
        excel_filepath: Optional path to Excel file to analyze columns from
    """
    print("🔍 Vision Database Table Checker")
    print("=" * 50)
    
    client = None
    
    try:
        # Create database client using config
        print("🔗 Connecting to Vision database...")
        client = VisionDBClient(
            host=VISION_DB_CONFIG['host'],
            port=VISION_DB_CONFIG['port'],
            database=VISION_DB_CONFIG['database'],
            user=VISION_DB_CONFIG['user'],
            password=VISION_DB_CONFIG['password']
        )
        
        if not client.test_connection():
            print("❌ Failed to connect to Vision database")
            print("   Please check:")
            print("   - Network connectivity")
            print("   - Database credentials in config/config.py")
            print("   - Database server is running")
            
            # If Excel file provided, we can still analyze columns
            if excel_filepath:
                print(f"\n📂 Will analyze columns from Excel file instead...")
            else:
                return None, None, None, None
        else:
            print(f"✅ Connected to {VISION_DB_CONFIG['database']} as {VISION_DB_CONFIG['user']}")
        
        # Run connection diagnostics (only show if there's an issue)
        schemas = []
        current_db = None
        if client:
            schemas, current_db = diagnose_connection(client, verbose=False)
        
        # Get all tables from database (try public schema first)
        all_tables = []
        schema_tables = {}
        all_tables_base = []
        
        if client:
            print(f"\n📋 Scanning database tables...")
            all_tables = client.get_table_list()
            
            # If no tables in public schema, check all schemas
            if len(all_tables) == 0:
                all_tables, schema_tables = get_all_tables_from_all_schemas(client, schemas)
                
                if len(all_tables) == 0:
                    print("   ❌ No tables found in any schema!")
                    print("   Possible issues:")
                    print("   - Wrong database selected")
                    print("   - User doesn't have SELECT permissions")
                    print("   - Tables are in a different database")
                    if not excel_filepath:
                        return None, None, None, None
                else:
                    print(f"   Found {len(all_tables)} tables across schemas")
            
            if all_tables:
                print(f"   Found {len(all_tables)} tables")
            
            # Normalize table names (remove schema prefix if present for comparison)
            # Store both full name and base name for display
            table_map = {}  # base_name -> full_name
            for table in all_tables:
                if '.' in table:
                    base_name = table.split('.')[-1]
                    table_map[base_name] = table
                else:
                    table_map[table] = table
            
            all_tables_base = list(table_map.keys())
        else:
            # No database connection, use Excel file sheets as table list
            if excel_filepath:
                print(f"\n📋 Scanning Excel file for tables...")
                try:
                    excel_file = pd.ExcelFile(excel_filepath)
                    all_tables_base = [sheet.lower().strip() for sheet in excel_file.sheet_names]
                    print(f"   Found {len(all_tables_base)} sheets in Excel file")
                except Exception as e:
                    print(f"   ❌ Error reading Excel file: {e}")
                    return None, None, None, None
        
        # Get currently extracted tables
        current_tables = get_current_extracted_tables()
        print(f"\n📊 Currently Extracting ({len(current_tables)} tables):")
        for table in sorted(current_tables):
            exists = table in all_tables_base
            status = "✅" if exists else "❌"
            print(f"   {status} {table}")
        
        # Show excluded tables (only if they exist)
        excluded_existing = [t for t in EXCLUDED_TABLES if t in all_tables_base]
        if excluded_existing:
            print(f"\n🚫 Excluded Tables ({len(excluded_existing)}):")
            for table in sorted(excluded_existing):
                print(f"   ⛔ {table}")
        
        # Find new tables (not in current extraction and not excluded)
        new_tables = [table for table in all_tables_base if table not in current_tables and table not in EXCLUDED_TABLES]
        
        if new_tables:
            print(f"\n🆕 New Tables Not Being Extracted ({len(new_tables)}):")
            for table in new_tables:
                print(f"   ⚠️  {table}")
        else:
            print("\n✅ All available tables are being extracted or excluded")
        
        # Check for missing tables (tables we extract but don't exist in DB)
        missing_tables = [table for table in current_tables if table not in all_tables_base]
        if missing_tables:
            print(f"\n⚠️  Missing Tables ({len(missing_tables)}):")
            print(f"   Tables configured for extraction but not found in database:")
            for table in missing_tables:
                print(f"   ❌ {table}")
        
        # Summary
        print(f"\n{'='*50}")
        print(f"📊 Summary")
        print(f"{'='*50}")
        print(f"   Total tables in database:     {len(all_tables_base)}")
        print(f"   Currently extracting:         {len(current_tables)}")
        print(f"   Excluded tables:              {len(EXCLUDED_TABLES)}")
        print(f"   New tables (not extracted):   {len(new_tables)}")
        print(f"   Missing tables:               {len(missing_tables)}")
        
        # Connection health check summary
        if len(missing_tables) == len(current_tables):
            print(f"\n⚠️  CONNECTION ISSUE DETECTED:")
            print(f"   All {len(current_tables)} extracted tables are missing from database.")
            print(f"   Check: config/config.py database settings")
        
        # Check columns for extracted tables
        column_info = check_table_columns(client, current_tables, all_tables_base, excel_filepath)
        
        if column_info:
            print(f"\n📋 Column Summary:")
            print("-" * 50)
            total_columns = sum(len(cols) for cols in column_info.values())
            print(f"   Total columns across all tables: {total_columns}")
            
            # Show columns for each table (if user wants details)
            print(f"\n📝 Columns by Table:")
            for table in sorted(column_info.keys()):
                cols = sorted(column_info[table])
                print(f"   {table} ({len(cols)} columns):")
                # Show first 10 columns, then "... and X more" if there are more
                if len(cols) <= 10:
                    for col in cols:
                        print(f"      - {col}")
                else:
                    for col in cols[:10]:
                        print(f"      - {col}")
                    print(f"      ... and {len(cols) - 10} more columns")
        
        return new_tables, all_tables_base, current_tables, column_info
        
    except Exception as e:
        print(f"❌ Error checking tables: {e}")
        return None, None, None, None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Check Vision database tables and columns')
    parser.add_argument('--excel', type=str, help='Path to Excel extraction file to analyze columns from')
    args = parser.parse_args()
    
    # Resolve Excel file path if provided
    excel_filepath = None
    if args.excel:
        if os.path.isabs(args.excel):
            excel_filepath = args.excel
        else:
            # Try relative to script directory, then project root
            script_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(os.path.dirname(script_dir))
            
            # Try multiple possible locations
            possible_paths = [
                os.path.join(project_root, args.excel),
                os.path.join(project_root, "output", "vision_data", args.excel),
                os.path.join(script_dir, args.excel),
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    excel_filepath = path
                    break
            
            if not excel_filepath:
                print(f"⚠️  Excel file not found: {args.excel}")
                print(f"   Tried: {possible_paths}")
                excel_filepath = args.excel  # Use as-is, let the function handle the error
    
    new_tables, all_tables, current_tables, column_info = check_vision_tables(excel_filepath=excel_filepath)
