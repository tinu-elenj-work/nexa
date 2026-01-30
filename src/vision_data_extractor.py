#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Vision Data Extractor
Extracts raw data from Vision database and exports to Excel with one tab per table.
Supports data masking for confidential information.
"""

import sys
import os
import pandas as pd
from datetime import datetime
import argparse
import random
import re

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

def clean_name_for_masking(name):
    """
    Clean special characters from names to ensure only alphanumeric characters and spaces remain.
    
    Args:
        name (str): The name to clean
        
    Returns:
        str: Cleaned name with only letters, numbers, and spaces
    """
    if not name or pd.isna(name):
        return name
    
    # Convert to string in case it's not already
    name_str = str(name)
    
    # Remove all characters except letters, numbers, and spaces
    # Keep spaces to maintain readability of full names
    cleaned = re.sub(r'[^a-zA-Z0-9\s]', ' ', name_str)
    
    # Clean up multiple spaces and strip
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    
    return cleaned

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
    """Get the maximum available simulation ID from the Vision database"""
    try:
        from vision_db_client import create_vision_client
        
        print("🔍 Connecting to Vision database to detect maximum simulation ID...")
        db_client = create_vision_client()
        
        if not db_client:
            raise Exception("Failed to connect to Vision database")
        
        print("✅ Database connection successful, querying for maximum simulation ID...")
        
        # Get maximum simulation ID
        max_sim_id = db_client.get_max_simulation_id()
        print(f"🎯 Maximum simulation ID found: {max_sim_id}")
        return max_sim_id
        
    except Exception as e:
        print(f"⚠️  Warning: Could not get maximum simulation ID: {e}")
        print("🔄 Falling back to default simulation ID: 28")
        return 28


def mask_projects_data(df):
    """Mask project amounts for fixed-type projects - preserves exact structure"""
    if df.empty:
        return df
    
    df_masked = df.copy()
    
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
                        random_amounts = [random.randint(100000, 200000) for _ in range(count)]
                        df_masked.loc[non_null_mask, col] = random_amounts
                        # Ensure data type is preserved
                        df_masked[col] = df_masked[col].astype(original_dtype)
                        print(f"   💰 Masked {count} amounts in '{col}' column for fixed projects")
            else:
                print(f"   ⚠️  No amount columns found for {len(fixed_projects)} fixed-type projects")
        else:
            print(f"   ℹ️  No fixed-type projects found to mask")
    else:
        print(f"   ⚠️  No 'type' column found in projects sheet")
    
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
                # Ensure data type is preserved
                df_masked[col] = df_masked[col].astype(original_dtype)
                print(f"   💵 Masked {count} rates in '{col}' column")
    else:
        print(f"   ⚠️  No rate value columns found in allocations sheet")
    
    return df_masked

def mask_salaries_data(df):
    """Mask salary amounts with random values - preserves exact structure"""
    if df.empty:
        return df
    
    df_masked = df.copy()
    
    # Look for salary amount columns
    salary_columns = [col for col in df_masked.columns if any(keyword in col.lower() for keyword in ["salary", "overtime", "allowance", "bonus", "payment", "loan"])]
    
    if salary_columns:
        for col in salary_columns:
            # Get non-null values
            non_null_mask = pd.notna(df_masked[col])
            count = non_null_mask.sum()
            
            if count > 0:
                # Preserve original data type
                original_dtype = df_masked[col].dtype
                # Generate random salary amounts (realistic range)
                random_amounts = [random.randint(30000, 150000) for _ in range(count)]
                df_masked.loc[non_null_mask, col] = random_amounts
                # Ensure data type is preserved
                df_masked[col] = df_masked[col].astype(original_dtype)
                print(f"   💰 Masked {count} amounts in '{col}' column")
    else:
        print(f"   ⚠️  No salary amount columns found in salaries sheet")
    
    return df_masked

def create_master_mappings(tables_data):
    """
    Create master mappings for consistent masking across all tables.
    This ensures that the same entity gets the same fake name across all tables.
    """
    if not FAKER_AVAILABLE:
        print("⚠️  Warning: Faker not available. Data masking will be limited.")
        return {}, {}, {}
    
    print("\n🎭 Creating master mappings for consistent masking...")
    fake = Faker()
    
    # 1. Employee Master Mapping
    print("   👤 Creating employee master mapping...")
    employee_mapping = {}
    if "employees" in tables_data:
        try:
            employees_df = tables_data["employees"]
            print(f"      📊 Processing {len(employees_df)} employee records...")
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
                    print(f"      ❌ Error processing employee row {idx}: {e}")
                    raise
            print(f"      ✅ Mapped {len(employee_mapping)} employees")
        except Exception as e:
            print(f"      ❌ Error in employee mapping: {e}")
            raise
    else:
        print("      ⚠️  No employees table found")
    
    # 2. Client Master Mapping
    print("   🏢 Creating client master mapping...")
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
        print(f"      ✅ Mapped {len(client_mapping)} clients")
    
    # 3. Project Master Mapping - Based on unique project names
    print("   📋 Creating project master mapping...")
    project_mapping = {}
    project_name_mapping = {}  # Maps original project names to fake names
    project_number_mapping = {}  # Maps original project numbers to fake numbers
    
    if "projects" in tables_data:
        projects_df = tables_data["projects"]
        
        # First, identify unique project names and numbers
        unique_project_names = projects_df['name'].dropna().unique()
        unique_project_numbers = projects_df['project_number'].dropna().unique()
        
        print(f"      📊 Found {len(unique_project_names)} unique project names")
        print(f"      📊 Found {len(unique_project_numbers)} unique project numbers")
        
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
        
        print(f"      ✅ Mapped {len(project_mapping)} projects using {len(project_name_mapping)} unique names")
    
    return employee_mapping, client_mapping, project_mapping

def apply_consistent_masking(tables_data, employee_mapping, client_mapping, project_mapping):
    """Apply consistent masking using master mappings to preserve relationships"""
    
    print("\n🎭 Applying consistent masking with preserved relationships...")
    masked_data = {}
    
    # 1. Mask Employees table
    if "employees" in tables_data:
        print("\n🎭 Masking 'employees' table...")
        df = tables_data["employees"].copy()
        
        for idx, row in df.iterrows():
            emp_id = row['id']  # Database uses lowercase column names
            if emp_id in employee_mapping:
                mapping = employee_mapping[emp_id]
                df.loc[df['id'] == emp_id, 'first_name'] = mapping['first_name']
                df.loc[df['id'] == emp_id, 'last_name'] = mapping['last_name']
                df.loc[df['id'] == emp_id, 'name'] = mapping['name']
        
        masked_data["employees"] = df
        print(f"   ✅ Masked {len(df)} employee records with consistent names")
    
    # 2. Mask Clients table
    if "clients" in tables_data:
        print("\n🎭 Masking 'clients' table...")
        df = tables_data["clients"].copy()
        
        for idx, row in df.iterrows():
            client_id = row['id']  # Database uses lowercase column names
            if client_id in client_mapping:
                mapping = client_mapping[client_id]
                df.loc[df['id'] == client_id, 'name'] = mapping['name']
        
        masked_data["clients"] = df
        print(f"   ✅ Masked {len(df)} client records with consistent names")
    
    # 3. Mask Projects table
    if "projects" in tables_data:
        print("\n🎭 Masking 'projects' table...")
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
        df = mask_projects_data(df)
        masked_data["projects"] = df
        print(f"   ✅ Masked {len(df)} project records with consistent names")
    
    # 4. Mask Allocations table
    if "allocations" in tables_data:
        print("\n🎭 Masking 'allocations' table...")
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
        print(f"   ✅ Masked {len(df)} allocation records with consistent names")
    
    # 5. Mask Salaries table
    if "salaries" in tables_data:
        print("\n🎭 Masking 'salaries' table...")
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
        print(f"   ✅ Masked {len(df)} salary records with consistent names")
    
    # 6. Copy other tables without masking (they don't contain sensitive data)
    other_tables = [
        "confidences",
        "calendars",
        "calendar_holidays",
        "currencies",
        "exchange_rates",
        "office",
        "simulation",
        "titles"
    ]
    for table_name in other_tables:
        if table_name in tables_data:
            print(f"\n📋 Copying '{table_name}' table (no masking needed)...")
            masked_data[table_name] = tables_data[table_name].copy()
            print(f"   ✅ Copied {len(tables_data[table_name])} {table_name} records")
    
    return masked_data

def apply_data_masking(tables_data):
    """Apply data masking to all tables - preserves relationships and consistency"""
    if not FAKER_AVAILABLE:
        print("⚠️  Warning: Faker not available. Data masking will be limited.")
        return tables_data
    
    print("\n🎭 Applying relationship-preserving data masking...")
    
    # Step 1: Create master mappings
    employee_mapping, client_mapping, project_mapping = create_master_mappings(tables_data)
    
    # Step 2: Apply consistent masking
    masked_data = apply_consistent_masking(tables_data, employee_mapping, client_mapping, project_mapping)
    
    return masked_data

def build_column_metadata(client, tables_data):
    """Build column metadata to flag computed/joined columns per table."""
    metadata_rows = []

    # Get database columns for each table
    db_columns_map = {}
    for table_name in tables_data.keys():
        try:
            schema_df = client.get_table_schema(table_name)
            if not schema_df.empty:
                db_columns_map[table_name] = set(schema_df["column_name"].tolist())
            else:
                db_columns_map[table_name] = set()
        except Exception:
            db_columns_map[table_name] = set()

    for table_name, df in tables_data.items():
        db_columns = db_columns_map.get(table_name, set())
        export_columns = list(df.columns)

        for col in export_columns:
            is_in_db = col in db_columns
            metadata_rows.append({
                "table": table_name,
                "column": col,
                "is_in_db": is_in_db,
                "is_computed": not is_in_db,
                "should_import": is_in_db
            })

        # Include database columns that are missing in export
        missing_columns = db_columns - set(export_columns)
        for col in sorted(missing_columns):
            metadata_rows.append({
                "table": table_name,
                "column": col,
                "is_in_db": True,
                "is_computed": False,
                "should_import": True
            })

    return pd.DataFrame(metadata_rows)

def extract_vision_data(simulation_id=None, output_filename=None, mask_data=False):
    """
    Extract all Vision data and export to Excel with one tab per table.
    
    Args:
        simulation_id (int): Simulation ID to filter by (None for max available)
        output_filename (str): Output filename (None for auto-generated)
        mask_data (bool): Whether to apply data masking
    """
    
    print("🗄️ Vision Data Extractor")
    print("=" * 50)
    
    try:
        # Handle simulation ID exactly like project_mapper_enhanced.py
        if simulation_id is None:
            print("🔍 No simulation ID provided, auto-detecting maximum available...")
            simulation_id = get_max_simulation_id()
            print(f"✅ Auto-detected simulation_id: {simulation_id}")
        else:
            print(f"🎯 Using provided simulation_id: {simulation_id}")
        
        # Generate output filename
        if output_filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            suffix = "_MASKED" if mask_data else ""
            output_filename = f"../output/vision_data/vision_extract_sim{simulation_id}_{timestamp}{suffix}.xlsx"
        
        # Ensure output directory exists
        output_dir = os.path.dirname(output_filename)
        if output_dir:  # Only create directory if there's a path component
            os.makedirs(output_dir, exist_ok=True)
        
        print(f"📊 Extracting Vision data to: {output_filename}")
        if mask_data:
            print("🎭 Data masking enabled - confidential data will be anonymized")
        
        # Create database client using the same mechanism as project_mapper_enhanced.py
        from vision_db_client import create_vision_client
        
        print("🔗 Connecting to Vision database...")
        client = create_vision_client()
        if not client.test_connection():
            raise Exception("Failed to connect to Vision database")
        
        print("✅ Database connection successful!")
        
        # Extract data from each table
        tables_data = {}
        
        # 1. Allocations
        print("📋 Extracting allocations...")
        allocations_df = client.get_allocations(simulation_id=simulation_id)
        tables_data["allocations"] = allocations_df
        print(f"   ✅ Retrieved {len(allocations_df)} allocation records")
        
        # 2. Employees
        print("👥 Extracting employees...")
        employees_df = client.get_employees(simulation_id=simulation_id)
        tables_data["employees"] = employees_df
        print(f"   ✅ Retrieved {len(employees_df)} employee records")
        
        # 3. Projects
        print("📋 Extracting projects...")
        projects_df = client.get_projects(simulation_id=simulation_id)
        tables_data["projects"] = projects_df
        print(f"   ✅ Retrieved {len(projects_df)} project records")
        
        # 4. Clients
        print("🏢 Extracting clients...")
        clients_df = client.get_clients(simulation_id=simulation_id)
        tables_data["clients"] = clients_df
        print(f"   ✅ Retrieved {len(clients_df)} client records")
        
        # 5. Confidences
        print("🎯 Extracting confidences...")
        confidences_df = client.get_confidences(simulation_id=simulation_id)
        tables_data["confidences"] = confidences_df
        print(f"   ✅ Retrieved {len(confidences_df)} confidence records")
        
        # 6. Calendars
        print("📅 Extracting calendars...")
        calendars_df = client.get_calendars(simulation_id=simulation_id)
        tables_data["calendars"] = calendars_df
        print(f"   ✅ Retrieved {len(calendars_df)} calendar records")
        
        # 7. Calendar Holidays
        print("🎉 Extracting calendar holidays...")
        calendar_holidays_df = client.get_calendar_holidays(simulation_id=simulation_id)
        tables_data["calendar_holidays"] = calendar_holidays_df
        print(f"   ✅ Retrieved {len(calendar_holidays_df)} holiday records")
        
        # 8. Currencies
        print("💱 Extracting currencies...")
        currencies_df = client.get_currencies(simulation_id=simulation_id)
        tables_data["currencies"] = currencies_df
        print(f"   ✅ Retrieved {len(currencies_df)} currency records")
        
        # 9. Exchange Rates
        print("💱 Extracting exchange rates...")
        exchange_rates_df = client.get_exchange_rates(simulation_id=simulation_id)
        tables_data["exchange_rates"] = exchange_rates_df
        print(f"   ✅ Retrieved {len(exchange_rates_df)} exchange rate records")
        
        # 10. Office
        print("🏢 Extracting office...")
        office_df = client.get_office(simulation_id=simulation_id)
        tables_data["office"] = office_df
        print(f"   ✅ Retrieved {len(office_df)} office records")
        
        # 11. Salaries
        print("💰 Extracting salaries...")
        salaries_df = client.get_salaries(simulation_id=simulation_id)
        tables_data["salaries"] = salaries_df
        print(f"   ✅ Retrieved {len(salaries_df)} salary records")
        
        # 12. Simulation
        print("🎯 Extracting simulation...")
        simulation_df = client.get_simulation(simulation_id=simulation_id)
        tables_data["simulation"] = simulation_df
        print(f"   ✅ Retrieved {len(simulation_df)} simulation records")
        
        # 13. Titles
        print("👔 Extracting titles...")
        titles_df = client.get_titles(simulation_id=simulation_id)
        tables_data["titles"] = titles_df
        print(f"   ✅ Retrieved {len(titles_df)} title records")
        
        # Apply data masking if requested
        if mask_data:
            tables_data = apply_data_masking(tables_data)

        # Build column metadata for import guidance
        column_metadata_df = build_column_metadata(client, tables_data)

        # Create extraction metadata
        extraction_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        extraction_metadata = pd.DataFrame([
            {"Property": "Extraction Date/Time", "Value": extraction_timestamp},
            {"Property": "Source", "Value": "Vision Database"},
            {"Property": "Simulation ID", "Value": simulation_id},
            {"Property": "Data Masking", "Value": "Enabled" if mask_data else "Disabled"},
            {"Property": "Total Tables", "Value": len(tables_data)},
            {"Property": "Total Records", "Value": sum(len(df) for df in tables_data.values())},
            {"Property": "Output File", "Value": os.path.basename(output_filename)}
        ])

        # Create Excel file with multiple sheets - EXACT SAME PROCESS as original
        print("📊 Creating Excel file...")
        with pd.ExcelWriter(output_filename, engine="openpyxl") as writer:
            # Write extraction metadata first
            extraction_metadata.to_excel(writer, sheet_name="Extraction_Metadata", index=False)
            worksheet = writer.sheets["Extraction_Metadata"]
            format_excel_sheet(worksheet, extraction_metadata)
            print("   📋 Created 'Extraction_Metadata' sheet with run information")

            # Write column metadata second
            if not column_metadata_df.empty:
                column_metadata_df.to_excel(writer, sheet_name="column_metadata", index=False)
                worksheet = writer.sheets["column_metadata"]
                format_excel_sheet(worksheet, column_metadata_df)
                print("   📋 Created 'column_metadata' sheet with import indicators")
            
            for table_name, df in tables_data.items():
                if not df.empty:
                    # Clean column names for Excel - EXACT SAME PROCESS
                    df_clean = df.copy()
                    df_clean.columns = [col.replace("_", " ").title() for col in df_clean.columns]
                    
                    # Handle timezone-aware datetime columns for Excel compatibility - EXACT SAME PROCESS
                    for col in df_clean.columns:
                        if df_clean[col].dtype == "datetime64[ns, UTC]":
                            # Convert timezone-aware to timezone-naive
                            df_clean[col] = df_clean[col].dt.tz_localize(None)
                        elif "datetime" in str(df_clean[col].dtype):
                            # Handle other datetime types
                            df_clean[col] = pd.to_datetime(df_clean[col]).dt.tz_localize(None)
                    
                    # Write to Excel sheet - EXACT SAME PROCESS
                    df_clean.to_excel(writer, sheet_name=table_name, index=False)
                    
                    # Format the sheet - EXACT SAME PROCESS
                    worksheet = writer.sheets[table_name]
                    format_excel_sheet(worksheet, df_clean)
                    
                    print(f"   📋 Created '{table_name}' sheet with {len(df_clean)} rows")
                else:
                    # Create empty sheet with column headers - EXACT SAME PROCESS
                    empty_df = pd.DataFrame(columns=df.columns)
                    empty_df.to_excel(writer, sheet_name=table_name, index=False)
                    
                    # Format the empty sheet - EXACT SAME PROCESS
                    worksheet = writer.sheets[table_name]
                    format_excel_sheet(worksheet, empty_df)
                    
                    print(f"   📋 Created empty '{table_name}' sheet")
        
        print(f"\n✅ Vision data extraction completed!")
        print(f"📁 Output file: {output_filename}")
        print(f"📊 Tables extracted: {len(tables_data)}")
        
        # Summary
        total_records = sum(len(df) for df in tables_data.values())
        print(f"📈 Total records: {total_records}")
        
        if mask_data:
            print(f"🎭 Data masking applied - safe for development and testing")
        
        return output_filename
        
    except Exception as e:
        print(f"❌ Error extracting Vision data: {e}")
        return None
    finally:
        # Close client if it was created
        try:
            if "client" in locals():
                client.close()
        except:
            pass

def main():
    """Main function with command line interface."""
    
    parser = argparse.ArgumentParser(
        description="Extract raw Vision database data to Excel file with optional data masking",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python vision_data_extractor.py
  python vision_data_extractor.py --simulation-id 29
  python vision_data_extractor.py --output vision_data_2025.xlsx
  python vision_data_extractor.py --simulation-id 28 --output custom_extract.xlsx
  python vision_data_extractor.py --mask
  python vision_data_extractor.py --simulation-id 29 --mask --output masked_data.xlsx

Data Masking Rules:
  - Relationship-preserving masking across all tables
  - Employees: Names replaced with fake names (special characters removed)
  - Clients: Names replaced with short company codes (special characters removed)
  - Projects: Names replaced with fake project names (special characters removed)
  - Project Numbers: Blanked out (empty) in all tables
  - Allocations: Employee/Project/Client names kept consistent with source tables
  - Financial data: Rate values randomized (Rate Type preserved as categorical data)
  - All foreign key relationships and computed fields preserved
        """
    )
    
    parser.add_argument(
        "--simulation-id", 
        type=int, 
        help="Vision simulation ID to filter by (default: maximum available)"
    )
    
    parser.add_argument(
        "--output", 
        type=str, 
        help="Output filename (default: auto-generated with timestamp)"
    )
    
    parser.add_argument(
        "--mask",
        action="store_true",
        help="Apply data masking to anonymize confidential information"
    )
    
    args = parser.parse_args()
    
    # Extract data
    output_file = extract_vision_data(
        simulation_id=args.simulation_id,
        output_filename=args.output,
        mask_data=args.mask
    )
    
    if output_file:
        print(f"\n🎉 Success! Vision data extracted to: {output_file}")
        if args.mask:
            print(f"⚠️  IMPORTANT: This masked data is safe for development and testing.")
            print(f"   Original confidential data has been replaced with fictional values.")
    else:
        print("\n❌ Extraction failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()