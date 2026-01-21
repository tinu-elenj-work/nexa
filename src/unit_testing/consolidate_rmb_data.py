#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Consolidate RMB Client Data
Extracts and combines all data related to RMB client from Vision Excel file
Produces a consolidated file with: projects, allocations, employees, titles
"""

import sys
import os
import pandas as pd
import warnings
from datetime import datetime

# Suppress warnings
warnings.filterwarnings('ignore')

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

def consolidate_rmb_data(input_filepath, output_filepath=None):
    """
    Consolidate all RMB client data from Vision Excel file.
    
    Args:
        input_filepath: Path to the input Vision Excel file
        output_filepath: Path for output file (auto-generated if None)
    
    Returns:
        str: Path to the output file
    """
    
    print("=" * 70)
    print("RMB Client Data Consolidation")
    print("=" * 70)
    
    # Read Excel file
    print(f"\nReading Excel file: {input_filepath}")
    xl = pd.ExcelFile(input_filepath)
    print(f"Sheets found: {xl.sheet_names}")
    
    # Read key sheets
    print("\nLoading sheets...")
    sheets_data = {}
    required_sheets = ['clients', 'projects', 'allocations', 'employees', 'salaries', 'titles', 'confidences']
    
    for sheet in required_sheets:
        if sheet in xl.sheet_names:
            # Read with original column names (they might be formatted)
            df = pd.read_excel(xl, sheet_name=sheet)
            # Normalize column names (handle both original and formatted)
            df.columns = df.columns.str.strip()
            sheets_data[sheet] = df
            print(f"  Loaded {sheet}: {len(df)} rows, {len(df.columns)} columns")
        else:
            print(f"  WARNING: Sheet '{sheet}' not found!")
    
    # Step 1: Find RMB client(s)
    print("\n" + "=" * 70)
    print("Step 1: Identifying RMB Client(s)")
    print("=" * 70)
    
    if 'clients' not in sheets_data:
        raise ValueError("Clients sheet not found!")
    
    clients_df = sheets_data['clients']
    
    # Find client ID column (could be 'Id', 'id', 'ID', etc.)
    client_id_col = None
    for col in ['Id', 'id', 'ID', 'client_id', 'Client Id', 'Client ID']:
        if col in clients_df.columns:
            client_id_col = col
            break
    
    # Find client name column
    client_name_col = None
    for col in ['Name', 'name', 'client_name', 'Client Name']:
        if col in clients_df.columns:
            client_name_col = col
            break
    
    if not client_id_col or not client_name_col:
        print(f"Available columns in clients sheet: {list(clients_df.columns)}")
        raise ValueError("Could not find client ID or name column!")
    
    print(f"Using columns: ID={client_id_col}, Name={client_name_col}")
    
    # Find RMB clients (case-insensitive search)
    rmb_clients = clients_df[
        clients_df[client_name_col].astype(str).str.contains('RMB', case=False, na=False)
    ]
    
    if len(rmb_clients) == 0:
        raise ValueError("No RMB client found in clients sheet!")
    
    print(f"Found {len(rmb_clients)} RMB client(s):")
    for idx, row in rmb_clients.iterrows():
        print(f"  - ID: {row[client_id_col]}, Name: {row[client_name_col]}")
    
    rmb_client_ids = rmb_clients[client_id_col].tolist()
    
    # Step 2: Filter projects for RMB clients
    print("\n" + "=" * 70)
    print("Step 2: Filtering Projects for RMB Clients")
    print("=" * 70)
    
    if 'projects' not in sheets_data:
        raise ValueError("Projects sheet not found!")
    
    projects_df = sheets_data['projects']
    
    # Find project-client relationship column
    project_client_id_col = None
    for col in ['Client Id', 'client_id', 'Client ID', 'clientId', 'ClientId']:
        if col in projects_df.columns:
            project_client_id_col = col
            break
    
    if not project_client_id_col:
        print(f"Available columns in projects sheet: {list(projects_df.columns)}")
        raise ValueError("Could not find client ID column in projects sheet!")
    
    print(f"Using column: {project_client_id_col}")
    
    rmb_projects = projects_df[projects_df[project_client_id_col].isin(rmb_client_ids)]
    print(f"Found {len(rmb_projects)} projects for RMB clients")
    
    if len(rmb_projects) == 0:
        print("WARNING: No projects found for RMB clients!")
        return None
    
    # Get project IDs
    project_id_col = None
    for col in ['Id', 'id', 'ID', 'project_id', 'Project Id', 'Project ID']:
        if col in projects_df.columns:
            project_id_col = col
            break
    
    if not project_id_col:
        raise ValueError("Could not find project ID column!")
    
    rmb_project_ids = rmb_projects[project_id_col].tolist()
    print(f"RMB Project IDs: {rmb_project_ids[:10]}{'...' if len(rmb_project_ids) > 10 else ''}")
    
    # Step 3: Filter allocations for RMB projects
    print("\n" + "=" * 70)
    print("Step 3: Filtering Allocations for RMB Projects")
    print("=" * 70)
    
    if 'allocations' not in sheets_data:
        raise ValueError("Allocations sheet not found!")
    
    allocations_df = sheets_data['allocations']
    
    # Find allocation-project relationship column
    allocation_project_id_col = None
    for col in ['Project Id', 'project_id', 'Project ID', 'projectId', 'ProjectId']:
        if col in allocations_df.columns:
            allocation_project_id_col = col
            break
    
    if not allocation_project_id_col:
        print(f"Available columns in allocations sheet: {list(allocations_df.columns)}")
        raise ValueError("Could not find project ID column in allocations sheet!")
    
    print(f"Using column: {allocation_project_id_col}")
    
    rmb_allocations = allocations_df[allocations_df[allocation_project_id_col].isin(rmb_project_ids)]
    print(f"Found {len(rmb_allocations)} allocations for RMB projects")
    
    # Get employee IDs from allocations
    allocation_employee_id_col = None
    for col in ['Employee Id', 'employee_id', 'Employee ID', 'employeeId', 'EmployeeId', 'Person Id', 'person_id']:
        if col in allocations_df.columns:
            allocation_employee_id_col = col
            break
    
    if allocation_employee_id_col:
        rmb_employee_ids = rmb_allocations[allocation_employee_id_col].dropna().unique().tolist()
        print(f"Found {len(rmb_employee_ids)} unique employees in RMB allocations")
    else:
        print("WARNING: Could not find employee ID column in allocations!")
        rmb_employee_ids = []
    
    # Step 4: Filter employees for RMB allocations
    print("\n" + "=" * 70)
    print("Step 4: Filtering Employees for RMB Allocations")
    print("=" * 70)
    
    if 'employees' not in sheets_data:
        raise ValueError("Employees sheet not found!")
    
    employees_df = sheets_data['employees']
    
    employee_id_col = None
    for col in ['Id', 'id', 'ID', 'employee_id', 'Employee Id', 'Employee ID']:
        if col in employees_df.columns:
            employee_id_col = col
            break
    
    if not employee_id_col:
        raise ValueError("Could not find employee ID column in employees sheet!")
    
    if rmb_employee_ids:
        rmb_employees = employees_df[employees_df[employee_id_col].isin(rmb_employee_ids)]
        print(f"Found {len(rmb_employees)} employees working on RMB projects")
    else:
        print("WARNING: No employee IDs found, including all employees")
        rmb_employees = employees_df.copy()
    
    # Step 5: Get latest titles from salaries table
    print("\n" + "=" * 70)
    print("Step 5: Loading Latest Titles from Salaries")
    print("=" * 70)
    
    if 'salaries' not in sheets_data:
        print("WARNING: Salaries sheet not found - cannot get employee titles")
        rmb_titles = pd.DataFrame()
        latest_salaries = pd.DataFrame()
    else:
        salaries_df = sheets_data['salaries']
        print(f"Loaded {len(salaries_df)} salary records")
        
        # Find employee_id column in salaries
        salary_employee_id_col = None
        for col in ['Employee Id', 'employee_id', 'Employee ID', 'employeeId', 'EmployeeId']:
            if col in salaries_df.columns:
                salary_employee_id_col = col
                break
        
        if not salary_employee_id_col:
            print("WARNING: Could not find employee_id column in salaries")
            rmb_titles = pd.DataFrame()
            latest_salaries = pd.DataFrame()
        else:
            # Filter salaries for RMB employees
            if rmb_employee_ids:
                rmb_salaries = salaries_df[salaries_df[salary_employee_id_col].isin(rmb_employee_ids)]
                print(f"Found {len(rmb_salaries)} salary records for RMB employees")
            else:
                rmb_salaries = salaries_df.copy()
                print("No employee IDs found, using all salaries")
            
            if len(rmb_salaries) > 0:
                # Find date column to determine "latest"
                salary_date_col = None
                for col in ['Start Date', 'start_date', 'Start', 'start']:
                    if col in rmb_salaries.columns:
                        salary_date_col = col
                        break
                
                if salary_date_col:
                    # Convert to datetime for sorting
                    rmb_salaries[salary_date_col] = pd.to_datetime(rmb_salaries[salary_date_col], errors='coerce')
                    
                    # Get latest salary record per employee (most recent start_date)
                    latest_salaries = rmb_salaries.sort_values(
                        by=[salary_employee_id_col, salary_date_col],
                        ascending=[True, False]  # Most recent date first
                    ).drop_duplicates(
                        subset=[salary_employee_id_col],
                        keep='first'  # Keep the first (most recent) record
                    )
                    print(f"Found {len(latest_salaries)} latest salary records (one per employee)")
                    
                    # Get title_id from latest salaries
                    salary_title_id_col = None
                    for col in ['Title Id', 'title_id', 'Title ID', 'titleId', 'TitleId']:
                        if col in latest_salaries.columns:
                            salary_title_id_col = col
                            break
                    
                    if salary_title_id_col:
                        # Get unique title_ids from latest salaries
                        title_ids = latest_salaries[salary_title_id_col].dropna().unique().tolist()
                        print(f"Found {len(title_ids)} unique title IDs in latest salaries")
                        
                        # Get titles from titles table
                        if 'titles' in sheets_data:
                            titles_df = sheets_data['titles']
                            title_id_col = None
                            for col in ['Id', 'id', 'ID', 'title_id', 'Title Id', 'Title ID']:
                                if col in titles_df.columns:
                                    title_id_col = col
                                    break
                            
                            if title_id_col and title_ids:
                                rmb_titles = titles_df[titles_df[title_id_col].isin(title_ids)]
                                print(f"Found {len(rmb_titles)} titles matching latest salary records")
                            else:
                                rmb_titles = pd.DataFrame()
                                print("WARNING: Could not match titles")
                        else:
                            rmb_titles = pd.DataFrame()
                            print("WARNING: Titles sheet not found")
                    else:
                        rmb_titles = pd.DataFrame()
                        print("WARNING: Could not find title_id column in salaries")
                else:
                    latest_salaries = pd.DataFrame()
                    rmb_titles = pd.DataFrame()
                    print("WARNING: Could not find date column in salaries to determine 'latest'")
            else:
                latest_salaries = pd.DataFrame()
                rmb_titles = pd.DataFrame()
                print("No salary records found for RMB employees")
    
    # Step 6: Consolidate all data into one sheet
    print("\n" + "=" * 70)
    print("Step 6: Consolidating All Data into One Sheet")
    print("=" * 70)
    
    # Start with allocations as the central table
    print("Starting with allocations as base table...")
    consolidated_df = rmb_allocations.copy()
    
    # Add source prefix to allocation columns
    allocation_prefix = 'Allocation|'
    allocation_col_mapping = {}
    allocation_key_cols = [allocation_project_id_col, allocation_employee_id_col] if allocation_employee_id_col else [allocation_project_id_col]
    
    for col in consolidated_df.columns:
        if col in allocation_key_cols:
            allocation_col_mapping[col] = f'key|{col}'
        else:
            allocation_col_mapping[col] = f'{allocation_prefix}{col}'
    
    consolidated_df = consolidated_df.rename(columns=allocation_col_mapping)
    print(f"  Base allocations: {len(consolidated_df)} rows")
    print(f"  Allocation columns prefixed with 'Allocation|' or 'key|'")
    
    # Join with projects to get project details
    if len(rmb_projects) > 0:
        print("Joining with projects...")
        # Prepare project columns with source prefix
        project_merge_col = f'key|{allocation_project_id_col}'  # Use the renamed key column
        project_id_col_for_merge = project_id_col
        
        # Rename project columns to add source prefix
        projects_to_merge = rmb_projects.copy()
        project_prefix = 'Project|'
        # Create mapping for column rename
        project_col_mapping = {}
        merge_key_renamed = None
        for col in projects_to_merge.columns:
            if col == project_id_col_for_merge:
                # This is the merge key - mark it as key
                merge_key_renamed = f'key|{col}'
                project_col_mapping[col] = merge_key_renamed
            else:
                project_col_mapping[col] = f'{project_prefix}{col}'
        
        projects_to_merge = projects_to_merge.rename(columns=project_col_mapping)
        
        # Merge
        consolidated_df = consolidated_df.merge(
            projects_to_merge,
            left_on=project_merge_col,
            right_on=merge_key_renamed,
            how='left',
            suffixes=('', '_project')
        )
        print(f"  After joining projects: {len(consolidated_df)} rows")
        print(f"  Added {len([c for c in consolidated_df.columns if c.startswith(project_prefix)])} project columns")
    
    # Join with clients to get client details
    if len(rmb_clients) > 0:
        print("Joining with clients...")
        # Get the client ID column from projects (after merge)
        client_id_from_projects = None
        # Try prefixed version first (Project|client_id)
        if f'{project_prefix}{project_client_id_col}' in consolidated_df.columns:
            client_id_from_projects = f'{project_prefix}{project_client_id_col}'
        # Try original column name
        elif project_client_id_col in consolidated_df.columns:
            client_id_from_projects = project_client_id_col
        
        if client_id_from_projects:
            # Prepare client columns with source prefix
            clients_to_merge = rmb_clients.copy()
            client_prefix = 'Client|'
            client_col_mapping = {}
            client_merge_key = None
            for col in clients_to_merge.columns:
                if col == client_id_col:
                    # This is the merge key - mark it as key
                    client_merge_key = f'key|{col}'
                    client_col_mapping[col] = client_merge_key
                else:
                    client_col_mapping[col] = f'{client_prefix}{col}'
            
            clients_to_merge = clients_to_merge.rename(columns=client_col_mapping)
            
            # Merge
            consolidated_df = consolidated_df.merge(
                clients_to_merge,
                left_on=client_id_from_projects,
                right_on=client_merge_key,
                how='left',
                suffixes=('', '_client')
            )
            print(f"  After joining clients: {len(consolidated_df)} rows")
            print(f"  Added {len([c for c in consolidated_df.columns if c.startswith(client_prefix)])} client columns")
        else:
            print(f"  WARNING: Could not find client ID column for merge")
            print(f"    Available columns: {[c for c in consolidated_df.columns if 'client' in c.lower() or 'id' in c.lower()][:10]}")
    
    # Join with confidences to get confidence details (via projects)
    if 'confidences' in sheets_data and len(rmb_projects) > 0:
        print("Joining with confidences...")
        # Get the confidence_id column from projects (after merge)
        confidence_id_from_projects = None
        # Try prefixed version first (Project|confidence_id)
        if f'{project_prefix}confidence_id' in consolidated_df.columns:
            confidence_id_from_projects = f'{project_prefix}confidence_id'
        # Try original column name
        elif 'confidence_id' in consolidated_df.columns:
            confidence_id_from_projects = 'confidence_id'
        
        if confidence_id_from_projects:
            confidences_df = sheets_data['confidences']
            # Find confidence ID and name columns
            confidence_id_col = None
            for col in ['Id', 'id', 'ID', 'confidence_id', 'Confidence Id', 'Confidence ID']:
                if col in confidences_df.columns:
                    confidence_id_col = col
                    break
            
            confidence_name_col = None
            for col in ['Name', 'name', 'confidence_name', 'Confidence Name']:
                if col in confidences_df.columns:
                    confidence_name_col = col
                    break
            
            if confidence_id_col:
                # Prepare confidence columns with source prefix
                # Only include the name column, not all columns
                confidences_to_merge = confidences_df[[confidence_id_col, confidence_name_col]].copy() if confidence_name_col else confidences_df[[confidence_id_col]].copy()
                confidence_prefix = 'Confidence|'
                confidence_col_mapping = {}
                confidence_merge_key = None
                for col in confidences_to_merge.columns:
                    if col == confidence_id_col:
                        # This is the merge key - mark it as key
                        confidence_merge_key = f'key|{col}'
                        confidence_col_mapping[col] = confidence_merge_key
                    elif col == confidence_name_col:
                        # This is the name column - rename to just "Confidence"
                        confidence_col_mapping[col] = 'Confidence'
                    else:
                        confidence_col_mapping[col] = f'{confidence_prefix}{col}'
                
                confidences_to_merge = confidences_to_merge.rename(columns=confidence_col_mapping)
                
                # Merge
                consolidated_df = consolidated_df.merge(
                    confidences_to_merge,
                    left_on=confidence_id_from_projects,
                    right_on=confidence_merge_key,
                    how='left',
                    suffixes=('', '_confidence')
                )
                print(f"  After joining confidences: {len(consolidated_df)} rows")
                if 'Confidence' in consolidated_df.columns:
                    print(f"  Added Confidence column (name) from confidences table")
                else:
                    print(f"  WARNING: Confidence column not found after merge")
                
                # Drop the merge key column if it exists (we don't need it in final output)
                if confidence_merge_key in consolidated_df.columns:
                    consolidated_df = consolidated_df.drop(columns=[confidence_merge_key])
                    print(f"  Removed merge key column: {confidence_merge_key}")
            else:
                print(f"  WARNING: Could not find confidence ID column in confidences sheet")
        else:
            print(f"  WARNING: Could not find confidence_id column from projects for merge")
            print(f"    Available columns: {[c for c in consolidated_df.columns if 'confidence' in c.lower() or 'project' in c.lower()][:10]}")
    
    # Join with employees to get employee details
    if rmb_employees is not None and len(rmb_employees) > 0:
        print("Joining with employees...")
        if allocation_employee_id_col:
            # Use the renamed key column from allocations
            employee_merge_col = f'key|{allocation_employee_id_col}'
            
            # Prepare employee columns with source prefix
            employees_to_merge = rmb_employees.copy()
            employee_prefix = 'Employee|'
            employee_col_mapping = {}
            employee_merge_key = None
            for col in employees_to_merge.columns:
                if col == employee_id_col:
                    # This is the merge key - mark it as key
                    employee_merge_key = f'key|{col}'
                    employee_col_mapping[col] = employee_merge_key
                else:
                    employee_col_mapping[col] = f'{employee_prefix}{col}'
            
            employees_to_merge = employees_to_merge.rename(columns=employee_col_mapping)
            
            # Merge
            consolidated_df = consolidated_df.merge(
                employees_to_merge,
                left_on=employee_merge_col,
                right_on=employee_merge_key,
                how='left',
                suffixes=('', '_employee')
            )
            print(f"  After joining employees: {len(consolidated_df)} rows")
            print(f"  Added {len([c for c in consolidated_df.columns if c.startswith(employee_prefix)])} employee columns")
        else:
            print(f"  WARNING: Could not find employee ID column for merge")
    
    # Join with latest salaries to get title_id, then join titles
    if latest_salaries is not None and len(latest_salaries) > 0:
        print("Joining with latest salaries to get title information...")
        
        # Find employee_id column in latest_salaries
        salary_employee_id_col_for_merge = None
        for col in ['Employee Id', 'employee_id', 'Employee ID', 'employeeId', 'EmployeeId']:
            if col in latest_salaries.columns:
                salary_employee_id_col_for_merge = col
                break
        
        if salary_employee_id_col_for_merge:
            # Prepare latest salaries columns with source prefix
            salaries_to_merge = latest_salaries.copy()
            salary_prefix = 'Salary|'
            salary_col_mapping = {}
            salary_merge_key = None
            for col in salaries_to_merge.columns:
                if col == salary_employee_id_col_for_merge:
                    # This is the merge key - use the same key format as employee merge
                    salary_merge_key = f'key|{col}'
                    salary_col_mapping[col] = salary_merge_key
                else:
                    salary_col_mapping[col] = f'{salary_prefix}{col}'
            
            salaries_to_merge = salaries_to_merge.rename(columns=salary_col_mapping)
            
            # Use employee merge key from consolidated_df
            employee_merge_col = f'key|{allocation_employee_id_col}' if allocation_employee_id_col else None
            
            if employee_merge_col and employee_merge_col in consolidated_df.columns:
                # Merge latest salaries
                consolidated_df = consolidated_df.merge(
                    salaries_to_merge,
                    left_on=employee_merge_col,
                    right_on=salary_merge_key,
                    how='left',
                    suffixes=('', '_salary')
                )
                print(f"  After joining latest salaries: {len(consolidated_df)} rows")
                
                # Now join titles using title_id from salaries
                if rmb_titles is not None and len(rmb_titles) > 0:
                    print("Joining with titles using title_id from latest salaries...")
                    
                    # Find title_id column in consolidated_df (from salaries merge)
                    salary_title_id_col_in_consolidated = None
                    for col in consolidated_df.columns:
                        if col.startswith('Salary|') and 'title' in col.lower() and 'id' in col.lower():
                            salary_title_id_col_in_consolidated = col
                            break
                    
                    if salary_title_id_col_in_consolidated:
                        print(f"  Found salary title ID column: {salary_title_id_col_in_consolidated}")
                        title_id_col_for_merge = None
                        for col in ['Id', 'id', 'ID', 'title_id', 'Title Id', 'Title ID']:
                            if col in rmb_titles.columns:
                                title_id_col_for_merge = col
                                break
                        
                        if title_id_col_for_merge:
                            # Prepare title columns with source prefix
                            titles_to_merge = rmb_titles.copy()
                            title_prefix = 'Title|'
                            title_col_mapping = {}
                            title_merge_key = None
                            for col in titles_to_merge.columns:
                                if col == title_id_col_for_merge:
                                    # This is the merge key - mark it as key
                                    title_merge_key = f'key|{col}'
                                    title_col_mapping[col] = title_merge_key
                                else:
                                    title_col_mapping[col] = f'{title_prefix}{col}'
                            
                            titles_to_merge = titles_to_merge.rename(columns=title_col_mapping)
                            
                            # Merge titles
                            consolidated_df = consolidated_df.merge(
                                titles_to_merge,
                                left_on=salary_title_id_col_in_consolidated,
                                right_on=title_merge_key,
                                how='left',
                                suffixes=('', '_title')
                            )
                            print(f"  After joining titles: {len(consolidated_df)} rows")
                            print(f"  Added {len([c for c in consolidated_df.columns if c.startswith(title_prefix)])} title columns")
                        else:
                            print(f"  WARNING: Could not find title ID column in titles sheet")
                    else:
                        print(f"  WARNING: Could not find title_id column from salaries in consolidated data")
                else:
                    print(f"  WARNING: No titles data available to join")
            else:
                print(f"  WARNING: Could not find employee merge column for salaries join")
        else:
            print(f"  WARNING: Could not find employee_id column in latest salaries")
    else:
        print("  WARNING: No latest salaries data available - cannot get titles")
    
    # Clean up duplicate key columns from merges (keep only one key|column per ID)
    print("Cleaning up duplicate key columns...")
    key_columns = [col for col in consolidated_df.columns if col.startswith('key|')]
    # Group by base ID name
    key_groups = {}
    for col in key_columns:
        base_id = col.split('|')[-1] if '|' in col else col
        if base_id not in key_groups:
            key_groups[base_id] = []
        key_groups[base_id].append(col)
    
    # Remove duplicates (keep the first occurrence)
    columns_to_drop = []
    for base_id, cols in key_groups.items():
        if len(cols) > 1:
            # Keep the first one, drop the rest
            columns_to_drop.extend(cols[1:])
    
    if columns_to_drop:
        consolidated_df = consolidated_df.drop(columns=columns_to_drop)
        print(f"  Removed {len(columns_to_drop)} duplicate key columns")
    
    # Reorder columns in specific order: Client|Name, Employee|Name, Title|Name, Project|Name, Project|Start Date, Project|End Date, Confidence, then all others
    print("Reordering columns in specified order...")
    
    # Define the required columns in exact order with pipe separator format
    required_columns = []
    column_mapping = {
        'Client|Name': ['Client|name', 'Client|Name', 'client|name', 'Client Name', 'client_name'],
        'Employee|Name': ['Employee|name', 'Employee|Name', 'employee|name', 'Employee Name', 
                         'Employee|first_name', 'Employee|last_name', 'employee_name'],
        'Title|Name': ['Title|name', 'Title|Name', 'title|name', 'Title Name', 'title_name'],
        'Project|Name': ['Project|name', 'Project|Name', 'project|name', 'Project Name', 'project_name'],
        'Project|Start Date': ['Project|start_date', 'Project|Start Date', 'Project|start', 'project|start_date', 
                              'Project Start', 'project_start', 'Project|Start'],
        'Project|End Date': ['Project|end_date', 'Project|End Date', 'Project|end', 'project|end_date',
                            'Project End', 'project_end', 'Project|End'],
        'Confidence': ['Confidence|name', 'Confidence|Name', 'confidence|name', 'Confidence', 'confidence',
                      'Project|confidence', 'Allocation|confidence', 'confidence_id', 'Confidence|name']
    }
    
    # Handle Employee Name - might be split into first_name and last_name
    employee_first_name_col = None
    employee_last_name_col = None
    employee_name_col = None
    
    # Check if we have a combined name column (look for exact format first)
    if 'Employee|Name' in consolidated_df.columns:
        employee_name_col = 'Employee|Name'
    elif 'Employee|name' in consolidated_df.columns:
        consolidated_df = consolidated_df.rename(columns={'Employee|name': 'Employee|Name'})
        employee_name_col = 'Employee|Name'
    else:
        # Check for other variations
        for col in consolidated_df.columns:
            if 'employee' in col.lower() and 'name' in col.lower() and 'first' not in col.lower() and 'last' not in col.lower():
                employee_name_col = col
                break
    
    # If no combined name, check for first_name and last_name
    if not employee_name_col:
        for col in consolidated_df.columns:
            if 'employee' in col.lower() and 'first' in col.lower() and 'name' in col.lower():
                employee_first_name_col = col
            elif 'employee' in col.lower() and 'last' in col.lower() and 'name' in col.lower():
                employee_last_name_col = col
    
    # Create combined Employee|Name if needed
    if not employee_name_col and employee_first_name_col and employee_last_name_col:
        consolidated_df['Employee|Name'] = (
            consolidated_df[employee_first_name_col].astype(str) + ' ' + 
            consolidated_df[employee_last_name_col].astype(str)
        ).str.strip()
        employee_name_col = 'Employee|Name'
        print(f"  Created combined Employee|Name from {employee_first_name_col} and {employee_last_name_col}")
    
    # Find each required column and normalize to exact format
    for target_name, possible_names in column_mapping.items():
        found = False
        found_col = None
        
        for possible_name in possible_names:
            if possible_name in consolidated_df.columns:
                found_col = possible_name
                found = True
                break
        
        # Special handling for Employee|Name
        if target_name == 'Employee|Name' and employee_name_col:
            if employee_name_col not in required_columns:
                found_col = employee_name_col
                found = True
        
        if found and found_col:
            # Rename the found column to match target format if different
            if found_col != target_name:
                consolidated_df = consolidated_df.rename(columns={found_col: target_name})
                print(f"  Renamed '{found_col}' to '{target_name}'")
            # Add to required columns list
            if target_name not in required_columns:
                required_columns.append(target_name)
        else:
            print(f"  WARNING: Could not find column for '{target_name}'")
            # Try case-insensitive search as fallback
            for col in consolidated_df.columns:
                # Normalize both for comparison
                target_normalized = target_name.lower().replace('|', '').replace('_', '').replace(' ', '')
                col_normalized = col.lower().replace('|', '').replace('_', '').replace(' ', '')
                if target_normalized in col_normalized or col_normalized in target_normalized:
                    if col not in required_columns:
                        # Rename to target format
                        consolidated_df = consolidated_df.rename(columns={col: target_name})
                        required_columns.append(target_name)
                        found = True
                        print(f"  Found and renamed '{col}' to '{target_name}'")
                        break
    
    # Ensure required columns are in the exact order specified
    exact_order = ['Client|Name', 'Employee|Name', 'Title|Name', 'Project|Name', 
                   'Project|Start Date', 'Project|End Date', 'Confidence']
    
    # Build final required columns list in exact order (only include if they exist)
    normalized_required = []
    for target_name in exact_order:
        if target_name in consolidated_df.columns:
            normalized_required.append(target_name)
    
    print(f"  Found {len(normalized_required)} of {len(exact_order)} required columns in exact order")
    for col in exact_order:
        status = "✓" if col in normalized_required else "✗"
        print(f"    {status} {col}")
    
    # Get all other columns (not in required list)
    other_columns = [col for col in consolidated_df.columns if col not in normalized_required]
    
    # Final order: Required columns first (in exact order), then all others
    final_column_order = normalized_required + other_columns
    
    # Only reorder if we have all columns
    if len(final_column_order) == len(consolidated_df.columns):
        consolidated_df = consolidated_df[final_column_order]
        print(f"  Reordered columns: {len(normalized_required)} priority columns, {len(other_columns)} other columns")
    else:
        print(f"  WARNING: Column count mismatch. Expected {len(consolidated_df.columns)}, got {len(final_column_order)}")
        # Still try to reorder with available columns
        available_final_order = [col for col in final_column_order if col in consolidated_df.columns]
        if len(available_final_order) == len(consolidated_df.columns):
            consolidated_df = consolidated_df[available_final_order]
            print(f"  Reordered with available columns only")
    
    # Sort by Project End date (oldest to newest)
    print("Sorting rows by Project End date (oldest to newest)...")
    project_end_col = None
    for col in consolidated_df.columns:
        if 'project' in col.lower() and 'end' in col.lower() and 'date' in col.lower():
            project_end_col = col
            break
    
    if project_end_col:
        # Convert to datetime if not already
        if consolidated_df[project_end_col].dtype == 'object':
            consolidated_df[project_end_col] = pd.to_datetime(consolidated_df[project_end_col], errors='coerce')
        
        # Sort: oldest to newest (ascending), with NaT/NaN at the end
        consolidated_df = consolidated_df.sort_values(
            by=project_end_col,
            ascending=True,
            na_position='last'
        )
        print(f"  Sorted by {project_end_col}")
        print(f"    Date range: {consolidated_df[project_end_col].min()} to {consolidated_df[project_end_col].max()}")
    else:
        print(f"  WARNING: Could not find Project End date column for sorting")
        print(f"    Available columns with 'project' and 'end': {[c for c in consolidated_df.columns if 'project' in c.lower() and 'end' in c.lower()]}")
    
    print(f"  Final consolidated table: {len(consolidated_df)} rows, {len(consolidated_df.columns)} columns")
    
    # Step 7: Create consolidated output file
    print("\n" + "=" * 70)
    print("Step 7: Creating Consolidated Output File")
    print("=" * 70)
    
    if output_filepath is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(script_dir))
        output_filepath = os.path.join(project_root, "output", "vision_data", f"RMB_Consolidated_{timestamp}.xlsx")
    
    # Ensure output directory exists
    output_dir = os.path.dirname(output_filepath)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    # Create Excel writer
    with pd.ExcelWriter(output_filepath, engine='openpyxl') as writer:
        # Write consolidated data
        consolidated_df.to_excel(writer, sheet_name='RMB_Consolidated', index=False)
        print(f"  Created sheet: RMB_Consolidated ({len(consolidated_df)} rows, {len(consolidated_df.columns)} columns)")
        
        # Create summary sheet
        summary_data = {
            'Category': ['RMB Clients', 'RMB Projects', 'RMB Allocations', 'RMB Employees', 'RMB Titles', 'Consolidated Rows'],
            'Count': [
                len(rmb_clients),
                len(rmb_projects),
                len(rmb_allocations),
                len(rmb_employees) if rmb_employees is not None else 0,
                len(rmb_titles) if rmb_titles is not None else 0,
                len(consolidated_df)
            ]
        }
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='Summary', index=False)
        print(f"  Created sheet: Summary")
    
    # Verify file was created
    if os.path.exists(output_filepath):
        file_size = os.path.getsize(output_filepath)
        print(f"\n" + "=" * 70)
        print("SUCCESS: Consolidated file created!")
        print("=" * 70)
        print(f"Output file: {output_filepath}")
        print(f"File size: {file_size:,} bytes")
        print(f"\nConsolidated Data Summary:")
        print(f"  - Total consolidated rows: {len(consolidated_df)}")
        print(f"  - Total columns: {len(consolidated_df.columns)}")
        print(f"\nSource Data Summary:")
        print(f"  - RMB Clients: {len(rmb_clients)}")
        print(f"  - RMB Projects: {len(rmb_projects)}")
        print(f"  - RMB Allocations: {len(rmb_allocations)}")
        print(f"  - RMB Employees: {len(rmb_employees) if rmb_employees is not None else 0}")
        print(f"  - RMB Titles: {len(rmb_titles) if rmb_titles is not None else 0}")
        print(f"\nThe consolidated sheet contains all data joined together:")
        print(f"  - Each row represents an allocation with full project, client,")
        print(f"    employee, and title details in a single row")
        return output_filepath
    else:
        print(f"\nERROR: File was not created: {output_filepath}")
        return None


def main():
    """Main function for command line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Consolidate RMB client data from Vision Excel file",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python consolidate_rmb_data.py
  python consolidate_rmb_data.py --input vision_extract_sim51.xlsx
  python consolidate_rmb_data.py --input vision_extract_sim51.xlsx --output rmb_data.xlsx
        """
    )
    
    parser.add_argument(
        '--input',
        type=str,
        default='vision_extract_sim51_20251211_113107.xlsx',
        help='Input Vision Excel file (default: vision_extract_sim51_20251211_113107.xlsx)'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        default=None,
        help='Output Excel file (default: auto-generated with timestamp)'
    )
    
    args = parser.parse_args()
    
    # Resolve input file path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(script_dir))
    
    if os.path.isabs(args.input):
        input_filepath = args.input
    else:
        # Try multiple possible locations
        possible_paths = [
            os.path.join(project_root, "output", "vision_data", args.input),
            os.path.join(project_root, args.input),
            args.input
        ]
        input_filepath = None
        for path in possible_paths:
            if os.path.exists(path):
                input_filepath = path
                break
        
        if not input_filepath:
            print(f"ERROR: Input file not found: {args.input}")
            print("Tried paths:")
            for path in possible_paths:
                print(f"  - {path}")
            return
    
    # Resolve output file path
    output_filepath = None
    if args.output:
        if os.path.isabs(args.output):
            output_filepath = args.output
        else:
            output_filepath = os.path.join(project_root, "output", "vision_data", args.output)
    
    # Run consolidation
    result = consolidate_rmb_data(input_filepath, output_filepath)
    
    if result:
        print(f"\n✅ Consolidation completed successfully!")
    else:
        print(f"\n❌ Consolidation failed!")


if __name__ == "__main__":
    main()

