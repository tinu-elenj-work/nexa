#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced Vision Data Extractor
Extracts Vision data with configurable table inclusion/exclusion lists.
Automatically detects new tables and applies exclusion rules.
"""

import sys
import os
import pandas as pd
from datetime import datetime
import argparse
import random

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from config import VISION_DB_CONFIG
from vision_db_client import VisionDBClient

# Import Faker for data masking
try:
    from faker import Faker
    FAKER_AVAILABLE = True
except ImportError:
    FAKER_AVAILABLE = False
    print("Warning: Faker not available. Install with: pip install faker")

# Table extraction configuration
CURRENT_EXTRACTED_TABLES = [
    "allocations", "employees", "projects", "clients", "confidences",
    "calendars", "calendar_holidays", "currencies", "exchange_rates",
    "office", "salaries", "simulation", "titles"
]

# Tables to exclude from extraction
EXCLUDED_TABLES = [
    "alembic_version",  # Database migration version - not business data
    "simulation_approvals",  # Empty table (0 rows)
    "audit_logs",  # Audit trail data - excluded per user request
    "user_account",  # User account information - excluded per user request
]

def clean_name_for_masking(name):
    """Clean special characters from names for data masking"""
    if not name or pd.isna(name):
        return name
    
    import re
    name_str = str(name)
    cleaned = re.sub(r'[^a-zA-Z0-9\s]', ' ', name_str)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned

def mask_projects_data(df, client_mapping=None):
    """Mask project names and amounts - preserves exact structure"""
    if df.empty:
        return df
    
    df_masked = df.copy()
    
    # Handle project name masking with client name replacement
    name_columns = [col for col in df_masked.columns if any(keyword in col.lower() for keyword in ["name", "title", "description"])]
    
    if name_columns and client_mapping and 'client_id' in df_masked.columns:
        for col in name_columns:
            # Get non-null values
            non_null_mask = pd.notna(df_masked[col])
            count = non_null_mask.sum()
            
            if count > 0:
                # Replace client name portion in pipe-delimited names
                for idx in df_masked[non_null_mask].index:
                    original_name = df_masked.loc[idx, col]
                    client_id = df_masked.loc[idx, 'client_id']
                    
                    if client_id in client_mapping:
                        # Get the fake client name
                        fake_client_name = client_mapping[client_id]['name']
                        
                        # Split by pipe and replace first part
                        name_parts = str(original_name).split('|')
                        if len(name_parts) > 1:
                            # Replace first part with fake client name
                            name_parts[0] = fake_client_name
                            df_masked.loc[idx, col] = '|'.join(name_parts)
                        else:
                            # If no pipe delimiter, just use fake client name
                            df_masked.loc[idx, col] = fake_client_name
                    else:
                        # Fallback to random project name
                        df_masked.loc[idx, col] = f"Project_{random.randint(1000, 9999)}"
                
                print(f"      Masked {count} {col} values with client names")
    
    # Check if Type column exists and has fixed projects
    if "type" in df_masked.columns:
        fixed_projects = df_masked[df_masked["type"] == "fixed"]
        
        if not fixed_projects.empty:
            # Look for amount-related columns
            amount_columns = [col for col in df_masked.columns if any(keyword in col.lower() for keyword in ["amount", "value", "budget", "cost", "price"])]
            
            if amount_columns:
                for col in amount_columns:
                    # Generate random amounts for fixed projects
                    mask = df_masked["type"] == "fixed"
                    non_null_mask = mask & pd.notna(df_masked[col])
                    count = non_null_mask.sum()
                    
                    if count > 0:
                        # Preserve original data type
                        original_dtype = df_masked[col].dtype
                        # Generate random amounts (realistic project range)
                        random_amounts = [random.randint(50000, 500000) for _ in range(count)]
                        df_masked.loc[non_null_mask, col] = random_amounts
                        # Convert back to original dtype
                        df_masked[col] = df_masked[col].astype(original_dtype)
                        print(f"      Masked {count} {col} values for fixed projects")
    
    return df_masked

def mask_allocations_data(df):
    """Mask allocation rates with random values - preserves exact structure"""
    if df.empty:
        return df
    
    df_masked = df.copy()
    
    # Look for rate value columns (not rate type columns)
    rate_columns = [col for col in df_masked.columns if "rate" in col.lower() and "type" not in col.lower()]
    
    if rate_columns:
        for col in rate_columns:
            # Get non-null values
            non_null_mask = pd.notna(df_masked[col])
            count = non_null_mask.sum()
            
            if count > 0:
                # Preserve original data type
                original_dtype = df_masked[col].dtype
                # Generate random rates
                random_rates = [random.randint(100000, 200000) for _ in range(count)]
                df_masked.loc[non_null_mask, col] = random_rates
                # Convert back to original dtype
                df_masked[col] = df_masked[col].astype(original_dtype)
                print(f"      [MASK] Masked {count} {col} values")
    
    return df_masked

def mask_salaries_data(df):
    """Mask salary amounts with random values - preserves exact structure"""
    if df.empty:
        return df
    
    df_masked = df.copy()
    
    # Look for salary amount columns (including cost_to_company)
    salary_columns = [col for col in df_masked.columns if any(keyword in col.lower() for keyword in ["salary", "overtime", "allowance", "bonus", "payment", "loan", "cost_to_company"])]
    
    if salary_columns:
        for col in salary_columns:
            # Get non-null values
            non_null_mask = pd.notna(df_masked[col])
            count = non_null_mask.sum()
            
            if count > 0:
                # Preserve original data type
                original_dtype = df_masked[col].dtype
                
                # Generate random amounts based on column type
                if "cost_to_company" in col.lower():
                    # Cost to company is typically higher than base salary
                    random_amounts = [random.randint(50000, 200000) for _ in range(count)]
                else:
                    # Regular salary amounts
                    random_amounts = [random.randint(30000, 150000) for _ in range(count)]
                
                df_masked.loc[non_null_mask, col] = random_amounts
                # Convert back to original dtype
                df_masked[col] = df_masked[col].astype(original_dtype)
                print(f"      [MASK] Masked {count} {col} values")
    
    return df_masked

def create_master_mappings(tables_data):
    """
    Create master mappings for consistent masking across all tables.
    This ensures that the same entity gets the same fake name across all tables.
    """
    if not FAKER_AVAILABLE:
        print("[WARNING]  Warning: Faker not available. Data masking will be limited.")
        return {}, {}, {}
    
    print("\n[MASK] Creating master mappings for consistent masking...")
    fake = Faker()
    
    # 1. Employee Master Mapping
    print("    Creating employee master mapping...")
    employee_mapping = {}
    if "employees" in tables_data:
        try:
            employees_df = tables_data["employees"]
            print(f"      [DATA] Processing {len(employees_df)} employee records...")
            for idx, row in employees_df.iterrows():
                try:
                    emp_id = row['id']  # Database uses lowercase column names
                    if emp_id not in employee_mapping:
                        first_name = clean_name_for_masking(fake.first_name())
                        last_name = clean_name_for_masking(fake.last_name())
                        full_name = f"{first_name} {last_name}"
                        employee_mapping[emp_id] = {
                            'first_name': first_name,
                            'last_name': last_name,
                            'name': full_name
                        }
                except Exception as e:
                    print(f"      [ERROR] Error processing employee row {idx}: {e}")
                    raise
            print(f"      [OK] Mapped {len(employee_mapping)} employees")
        except Exception as e:
            print(f"      [ERROR] Error in employee mapping: {e}")
            raise
    else:
        print("      [WARNING]  No employees table found")
    
    # 2. Client Master Mapping
    print("    Creating client master mapping...")
    client_mapping = {}
    if "clients" in tables_data:
        clients_df = tables_data["clients"]
        for idx, row in clients_df.iterrows():
            client_id = row['id']  # Database uses lowercase column names
            if client_id not in client_mapping:
                # Generate short company codes similar to original format
                company_name = clean_name_for_masking(fake.company())
                # Extract first letters of each word to create short code
                words = company_name.split()
                short_code = ''.join([word[0].upper() for word in words if word])[:3]
                if len(short_code) < 2:
                    short_code = company_name[:3].upper()
                client_mapping[client_id] = {
                    'name': short_code,
                    'full_name': company_name
                }
        print(f"      [OK] Mapped {len(client_mapping)} clients")
    
    # 3. Project Master Mapping - Based on unique project names
    print("   [LIST] Creating project master mapping...")
    project_mapping = {}
    project_name_mapping = {}  # Maps original project names to fake names
    project_number_mapping = {}  # Maps original project numbers to fake numbers
    
    if "projects" in tables_data:
        projects_df = tables_data["projects"]
        
        # First, identify unique project names and numbers
        unique_project_names = projects_df['name'].dropna().unique()
        unique_project_numbers = projects_df['project_number'].dropna().unique()
        
        print(f"      [DATA] Found {len(unique_project_names)} unique project names")
        print(f"      [DATA] Found {len(unique_project_numbers)} unique project numbers")
        
        # Create mappings for unique project names
        for orig_name in unique_project_names:
            if orig_name not in project_name_mapping:
                # Generate project name in similar format to original
                # Extract client code from original name (first part before |)
                if '|' in orig_name:
                    client_code = orig_name.split('|')[0]
                else:
                    client_code = 'UNK'
                
                # Find project type from any project with this name
                sample_project = projects_df[projects_df['name'] == orig_name].iloc[0]
                project_type = sample_project.get('type', 'FIX')
                
                project_name = f"{client_code}|{clean_name_for_masking(fake.word().upper())}|{clean_name_for_masking(fake.word().upper())}|{project_type}|{clean_name_for_masking(fake.word().upper())}"
                project_name_mapping[orig_name] = project_name
        
        # Create mappings for unique project numbers - blank them out
        for orig_number in unique_project_numbers:
            if orig_number not in project_number_mapping:
                project_number_mapping[orig_number] = ""  # Blank out project numbers
        
        # Now create project mapping by ID using the name/number mappings
        for idx, row in projects_df.iterrows():
            project_id = row['id']
            if project_id not in project_mapping:
                orig_name = row['name']
                orig_number = row['project_number']
                
                project_mapping[project_id] = {
                    'name': project_name_mapping.get(orig_name, orig_name),
                    'number': project_number_mapping.get(orig_number, orig_number)
                }
        
        print(f"      [OK] Mapped {len(project_mapping)} projects using {len(project_name_mapping)} unique names")
    
    return employee_mapping, client_mapping, project_mapping

def apply_consistent_masking(tables_data, employee_mapping, client_mapping, project_mapping):
    """Apply consistent masking using master mappings to preserve relationships"""
    
    print("\n[MASK] Applying consistent masking with preserved relationships...")
    masked_data = {}
    
    # 1. Mask Employees table
    if "employees" in tables_data:
        print("\n[MASK] Masking 'employees' table...")
        df = tables_data["employees"].copy()
        
        for idx, row in df.iterrows():
            emp_id = row['id']  # Database uses lowercase column names
            if emp_id in employee_mapping:
                mapping = employee_mapping[emp_id]
                df.loc[df['id'] == emp_id, 'first_name'] = mapping['first_name']
                df.loc[df['id'] == emp_id, 'last_name'] = mapping['last_name']
                df.loc[df['id'] == emp_id, 'name'] = mapping['name']
        
        masked_data["employees"] = df
        print(f"   [OK] Masked {len(df)} employee records with consistent names")
    
    # 2. Mask Clients table
    if "clients" in tables_data:
        print("\n[MASK] Masking 'clients' table...")
        df = tables_data["clients"].copy()
        
        for idx, row in df.iterrows():
            client_id = row['id']  # Database uses lowercase column names
            if client_id in client_mapping:
                mapping = client_mapping[client_id]
                df.loc[df['id'] == client_id, 'name'] = mapping['name']
        
        masked_data["clients"] = df
        print(f"   [OK] Masked {len(df)} client records with consistent names")
    
    # 3. Mask Projects table
    if "projects" in tables_data:
        print("\n[MASK] Masking 'projects' table...")
        df = tables_data["projects"].copy()
        
        for idx, row in df.iterrows():
            project_id = row['id']  # Database uses lowercase column names
            client_id = row['client_id']
            
            if project_id in project_mapping:
                mapping = project_mapping[project_id]
                df.loc[df['id'] == project_id, 'name'] = mapping['name']
                df.loc[df['id'] == project_id, 'project_number'] = mapping['number']
            
            if client_id in client_mapping:
                mapping = client_mapping[client_id]
                df.loc[df['id'] == project_id, 'client_name'] = mapping['name']
        
        # Also mask project amounts for fixed-type projects
        df = mask_projects_data(df, client_mapping)
        masked_data["projects"] = df
        print(f"   [OK] Masked {len(df)} project records with consistent names")
    
    # 4. Mask Allocations table
    if "allocations" in tables_data:
        print("\n[MASK] Masking 'allocations' table...")
        df = tables_data["allocations"].copy()
        
        for idx, row in df.iterrows():
            emp_id = row['employee_id']  # Database uses lowercase column names
            project_id = row['project_id']
            
            # Apply employee mapping
            if emp_id in employee_mapping:
                mapping = employee_mapping[emp_id]
                df.loc[df['employee_id'] == emp_id, 'first_name'] = mapping['first_name']
                df.loc[df['employee_id'] == emp_id, 'last_name'] = mapping['last_name']
                df.loc[df['employee_id'] == emp_id, 'employee_name'] = mapping['name']
            
            # Apply project mapping - inherit from projects table
            if project_id in project_mapping:
                mapping = project_mapping[project_id]
                df.loc[df['project_id'] == project_id, 'project_name'] = mapping['name']
                df.loc[df['project_id'] == project_id, 'project_number'] = mapping['number']
            
            # Apply client mapping (get client from project)
            if project_id in project_mapping and 'projects' in tables_data:
                # Find the client for this project
                project_row = tables_data['projects'][tables_data['projects']['id'] == project_id]
                if not project_row.empty:
                    client_id = project_row.iloc[0]['client_id']
                    if client_id in client_mapping:
                        mapping = client_mapping[client_id]
                        df.loc[df['project_id'] == project_id, 'client_name'] = mapping['name']
        
        # Also mask allocation rates
        df = mask_allocations_data(df)
        masked_data["allocations"] = df
        print(f"   [OK] Masked {len(df)} allocation records with consistent names")
    
    # 5. Mask Salaries table
    if "salaries" in tables_data:
        print("\n[MASK] Masking 'salaries' table...")
        df = tables_data["salaries"].copy()
        
        for idx, row in df.iterrows():
            emp_id = row['employee_id']  # Database uses lowercase column names
            
            # Apply employee mapping
            if emp_id in employee_mapping:
                mapping = employee_mapping[emp_id]
                df.loc[df['employee_id'] == emp_id, 'first_name'] = mapping['first_name']
                df.loc[df['employee_id'] == emp_id, 'last_name'] = mapping['last_name']
                df.loc[df['employee_id'] == emp_id, 'employee_name'] = mapping['name']
        
        # Also mask salary amounts
        df = mask_salaries_data(df)
        masked_data["salaries"] = df
        print(f"   [OK] Masked {len(df)} salary records with consistent names")
    
    # 6. Copy other tables without masking (they don't contain sensitive data)
    other_tables = ["confidences", "calendars", "calendar_holidays", "currencies", "exchange_rates", "office", "simulation", "titles"]
    for table_name in other_tables:
        if table_name in tables_data:
            print(f"\n[LIST] Copying '{table_name}' table (no masking needed)...")
            masked_data[table_name] = tables_data[table_name].copy()
            print(f"   [OK] Copied {len(tables_data[table_name])} {table_name} records")
    
    return masked_data

def apply_data_masking(tables_data):
    """Apply data masking to all tables - preserves relationships and consistency"""
    if not FAKER_AVAILABLE:
        print("[WARNING]  Warning: Faker not available. Data masking will be limited.")
        return tables_data
    
    print("\n[MASK] Applying relationship-preserving data masking...")
    
    # Step 1: Create master mappings
    employee_mapping, client_mapping, project_mapping = create_master_mappings(tables_data)
    
    # Step 2: Apply consistent masking
    masked_data = apply_consistent_masking(tables_data, employee_mapping, client_mapping, project_mapping)
    
    return masked_data

def format_excel_sheet(worksheet, df):
    """Format Excel sheet with auto-sized columns and proper styling"""
    from openpyxl.styles import Font, PatternFill
    
    # Auto-size all columns
    for column in worksheet.columns:
        max_length = 0
        column_letter = column[0].column_letter
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = min(max_length + 2, 50)  # Cap at 50 characters
        worksheet.column_dimensions[column_letter].width = adjusted_width
    
    # Format header row
    for cell in worksheet[1]:
        cell.font = Font(bold=True)
        cell.fill = PatternFill(start_color="CCCCCC", end_color="CCCCCC", fill_type="solid")

def get_max_simulation_id():
    """Get the maximum available simulation ID from the database"""
    try:
        from vision_db_client import create_vision_client
        client = create_vision_client()
        
        if not client.test_connection():
            print("   [ERROR] Failed to connect to Vision database")
            return 28
        
        max_id = client.get_max_simulation_id()
        print(f"   [OK] Found maximum simulation_id: {max_id}")
        return max_id
        
    except Exception as e:
        print(f"   [ERROR] Error getting maximum simulation ID: {e}")
        print("   Falling back to default simulation ID: 28")
        return 28

def detect_new_tables():
    """Detect new tables in the database that are not currently extracted"""
    try:
        from vision_db_client import create_vision_client
        client = create_vision_client()
        
        if not client.test_connection():
            print("[ERROR] Failed to connect to Vision database")
            return []
        
        # Get all tables from database
        all_tables = client.get_table_list()
        
        # Find new tables (not in current extraction list and not excluded)
        new_tables = []
        for table in all_tables:
            if table not in CURRENT_EXTRACTED_TABLES and table not in EXCLUDED_TABLES:
                new_tables.append(table)
        
        return new_tables, all_tables
        
    except Exception as e:
        print(f"[ERROR] Error detecting new tables: {e}")
        return [], []

def extract_vision_data_enhanced(simulation_id=None, output_filename=None, mask_data=False, include_new_tables=True):
    """
    Extract Vision data with enhanced table detection and exclusion handling.
    
    Args:
        simulation_id (int): Simulation ID to filter by (None for max available)
        output_filename (str): Output filename (None for auto-generated)
        mask_data (bool): Whether to apply data masking
        include_new_tables (bool): Whether to include newly detected tables
    """
    
    print("Enhanced Vision Data Extractor")
    print("=" * 50)
    
    try:
        # Handle simulation ID
        if simulation_id is None:
            print("[DETECT] No simulation ID provided, auto-detecting maximum available...")
            simulation_id = get_max_simulation_id()
            print(f"[OK] Auto-detected simulation_id: {simulation_id}")
        else:
            print(f"[TARGET] Using provided simulation_id: {simulation_id}")
        
        # Detect new tables if requested
        new_tables = []
        all_tables = []
        if include_new_tables:
            print("\n[DETECT] Detecting new tables in database...")
            new_tables, all_tables = detect_new_tables()
            
            if new_tables:
                print(f"    Found {len(new_tables)} new tables: {', '.join(new_tables)}")
                print("   These will be included in the extraction.")
            else:
                print("   [OK] No new tables found - using current extraction list")
        else:
            print("\n[SKIP]  Skipping new table detection - using current extraction list only")
        
        # Generate output filename (same pattern as original vision_data_extractor.py)
        if output_filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            suffix = "_MASKED" if mask_data else ""
            # Get absolute path relative to project root
            script_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(script_dir)
            output_filename = os.path.join(project_root, "output", "vision_data", f"vision_extract_sim{simulation_id}_{timestamp}{suffix}.xlsx")
        else:
            # If custom filename provided, make it absolute if it's relative
            if not os.path.isabs(output_filename):
                script_dir = os.path.dirname(os.path.abspath(__file__))
                project_root = os.path.dirname(script_dir)
                output_filename = os.path.join(project_root, output_filename.lstrip("./"))
        
        # Ensure output directory exists
        output_dir = os.path.dirname(output_filename)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        print(f"\n[DATA] Extracting Vision data to: {output_filename}")
        if mask_data:
            print("[MASK] Data masking enabled - confidential data will be anonymized")
        
        # Create database client
        from vision_db_client import create_vision_client
        
        print("\n Connecting to Vision database...")
        client = create_vision_client()
        if not client.test_connection():
            raise Exception("Failed to connect to Vision database")
        
        print("[OK] Database connection successful!")
        
        # Extract data from each table
        tables_data = {}
        
        # Define extraction methods for each table
        extraction_methods = {
            "allocations": lambda: client.get_allocations(simulation_id=simulation_id),
            "employees": lambda: client.get_employees(simulation_id=simulation_id),
            "projects": lambda: client.get_projects(simulation_id=simulation_id),
            "clients": lambda: client.get_clients(simulation_id=simulation_id),
            "confidences": lambda: client.get_confidences(simulation_id=simulation_id),
            "calendars": lambda: client.get_calendars(simulation_id=simulation_id),
            "calendar_holidays": lambda: client.get_calendar_holidays(simulation_id=simulation_id),
            "currencies": lambda: client.get_currencies(simulation_id=simulation_id),
            "exchange_rates": lambda: client.get_exchange_rates(simulation_id=simulation_id),
            "office": lambda: client.get_office(simulation_id=simulation_id),
            "salaries": lambda: client.get_salaries(simulation_id=simulation_id),
            "simulation": lambda: client.get_simulation(simulation_id=simulation_id),
            "titles": lambda: client.get_titles(simulation_id=simulation_id),
        }
        
        # Extract data from all tables (existing + new)
        all_extraction_tables = CURRENT_EXTRACTED_TABLES + new_tables
        
        for table_name in all_extraction_tables:
            if table_name in extraction_methods:
                print(f"[LIST] Extracting {table_name}...")
                try:
                    df = extraction_methods[table_name]()
                    tables_data[table_name] = df
                    print(f"   [OK] Retrieved {len(df)} {table_name} records")
                except Exception as e:
                    print(f"   [ERROR] Error extracting {table_name}: {e}")
                    tables_data[table_name] = pd.DataFrame()  # Empty DataFrame as fallback
            else:
                print(f"[WARNING]  No extraction method defined for {table_name} - skipping")
        
        # Apply data masking if requested
        if mask_data:
            print("\n[MASK] Applying data masking...")
            tables_data = apply_data_masking(tables_data)
        
        # Create Excel file with multiple sheets
        print("\n[DATA] Creating Excel file...")
        with pd.ExcelWriter(output_filename, engine="openpyxl") as writer:
            
            for table_name, df in tables_data.items():
                if not df.empty:
                    # Clean column names for Excel
                    df_clean = df.copy()
                    df_clean.columns = [col.replace("_", " ").title() for col in df_clean.columns]
                    
                    # Handle timezone-aware datetime columns for Excel compatibility
                    for col in df_clean.columns:
                        if df_clean[col].dtype == "datetime64[ns, UTC]":
                            df_clean[col] = df_clean[col].dt.tz_localize(None)
                        elif "datetime" in str(df_clean[col].dtype):
                            df_clean[col] = pd.to_datetime(df_clean[col]).dt.tz_localize(None)
                    
                    # Write to Excel sheet
                    df_clean.to_excel(writer, sheet_name=table_name, index=False)
                    
                    # Format the sheet
                    worksheet = writer.sheets[table_name]
                    format_excel_sheet(worksheet, df_clean)
                    
                    print(f"   [OK] Created sheet: {table_name} ({len(df_clean)} rows)")
                else:
                    print(f"   [WARNING]  Skipped empty sheet: {table_name}")
        
        # Verify file was created
        if os.path.exists(output_filename):
            file_size = os.path.getsize(output_filename)
            print(f"\n[OK] Vision data extraction completed!")
            print(f"✅ Output file: {output_filename}")
            print(f"📊 File size: {file_size:,} bytes")
            print(f"📋 Total tables extracted: {len([t for t in tables_data.values() if not t.empty])}")
        else:
            print(f"\n[ERROR] File was not created: {output_filename}")
            print(f"⚠️  Check permissions and disk space")
        
        if new_tables:
            print(f" New tables included: {', '.join(new_tables)}")
        
        return output_filename
        
    except Exception as e:
        print(f"[ERROR] Error during extraction: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Main function for command line usage"""
    parser = argparse.ArgumentParser(description="Enhanced Vision Data Extractor")
    parser.add_argument("--simulation-id", type=int, help="Simulation ID to extract (default: auto-detect)")
    parser.add_argument("--output", help="Output filename (default: auto-generated)")
    parser.add_argument("--mask", action="store_true", help="Apply data masking")
    parser.add_argument("--no-new-tables", action="store_true", help="Don't include newly detected tables")
    
    args = parser.parse_args()
    
    extract_vision_data_enhanced(
        simulation_id=args.simulation_id,
        output_filename=args.output,
        mask_data=args.mask,
        include_new_tables=not args.no_new_tables
    )

if __name__ == "__main__":
    main()
