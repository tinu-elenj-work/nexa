#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analyze Vision Excel Structure
Examines the Excel file to understand relationships between sheets
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

def analyze_excel_structure(filepath):
    """Analyze the Excel file structure and relationships"""
    
    print("=" * 70)
    print("📊 Analyzing Vision Excel File Structure")
    print("=" * 70)
    
    # Read Excel file
    xl = pd.ExcelFile(filepath)
    print(f"\n📋 Sheets found: {len(xl.sheet_names)}")
    for i, sheet in enumerate(xl.sheet_names, 1):
        print(f"   {i}. {sheet}")
    
    # Analyze key sheets
    key_sheets = ['clients', 'projects', 'allocations', 'employees', 'titles']
    
    print("\n" + "=" * 70)
    print("🔍 Analyzing Key Sheets and Relationships")
    print("=" * 70)
    
    sheets_data = {}
    
    for sheet_name in key_sheets:
        if sheet_name in xl.sheet_names:
            print(f"\n📄 Sheet: {sheet_name}")
            print("-" * 70)
            df = pd.read_excel(xl, sheet_name=sheet_name)
            sheets_data[sheet_name] = df
            
            print(f"   Rows: {len(df)}")
            print(f"   Columns: {list(df.columns)}")
            
            # Show sample data
            if len(df) > 0:
                print(f"\n   Sample data (first 3 rows):")
                print(df.head(3).to_string())
            
            # Check for RMB client
            if 'client' in sheet_name.lower() or 'Client' in df.columns:
                client_col = [col for col in df.columns if 'client' in col.lower() or 'name' in col.lower()]
                if client_col:
                    print(f"\n   Unique values in {client_col[0]}:")
                    unique_vals = df[client_col[0]].unique()[:10]
                    for val in unique_vals:
                        print(f"      - {val}")
                    if 'RMB' in str(df[client_col[0]].values):
                        rmb_count = df[df[client_col[0]].str.contains('RMB', case=False, na=False)].shape[0]
                        print(f"\n   ✅ Found {rmb_count} records with 'RMB' in client name")
    
    # Analyze relationships
    print("\n" + "=" * 70)
    print("🔗 Analyzing Relationships")
    print("=" * 70)
    
    if 'clients' in sheets_data:
        clients_df = sheets_data['clients']
        print("\n📊 Clients Sheet:")
        if 'Id' in clients_df.columns or 'id' in clients_df.columns:
            id_col = 'Id' if 'Id' in clients_df.columns else 'id'
            print(f"   Primary Key: {id_col}")
            print(f"   Total clients: {len(clients_df)}")
            
            # Check for RMB
            name_col = [col for col in clients_df.columns if 'name' in col.lower()][0] if any('name' in col.lower() for col in clients_df.columns) else None
            if name_col:
                rmb_clients = clients_df[clients_df[name_col].str.contains('RMB', case=False, na=False)]
                print(f"   RMB clients found: {len(rmb_clients)}")
                if len(rmb_clients) > 0:
                    print(f"   RMB Client IDs: {rmb_clients[id_col].tolist()}")
    
    if 'projects' in sheets_data:
        projects_df = sheets_data['projects']
        print("\n📊 Projects Sheet:")
        print(f"   Columns: {list(projects_df.columns)}")
        if 'Client Id' in projects_df.columns or 'client_id' in projects_df.columns:
            client_id_col = 'Client Id' if 'Client Id' in projects_df.columns else 'client_id'
            print(f"   Foreign Key to Clients: {client_id_col}")
            if 'clients' in sheets_data:
                clients_df = sheets_data['clients']
                id_col = 'Id' if 'Id' in clients_df.columns else 'id'
                name_col = [col for col in clients_df.columns if 'name' in col.lower()][0] if any('name' in col.lower() for col in clients_df.columns) else None
                if name_col:
                    rmb_clients = clients_df[clients_df[name_col].str.contains('RMB', case=False, na=False)]
                    if len(rmb_clients) > 0:
                        rmb_client_ids = rmb_clients[id_col].tolist()
                        rmb_projects = projects_df[projects_df[client_id_col].isin(rmb_client_ids)]
                        print(f"   Projects linked to RMB clients: {len(rmb_projects)}")
    
    if 'allocations' in sheets_data:
        allocations_df = sheets_data['allocations']
        print("\n📊 Allocations Sheet:")
        print(f"   Columns: {list(allocations_df.columns)}")
        # Check foreign keys
        fk_cols = [col for col in allocations_df.columns if 'id' in col.lower() or 'Id' in col]
        print(f"   Foreign Key columns: {fk_cols}")
    
    if 'employees' in sheets_data:
        employees_df = sheets_data['employees']
        print("\n📊 Employees Sheet:")
        print(f"   Columns: {list(employees_df.columns)}")
        if 'Id' in employees_df.columns or 'id' in employees_df.columns:
            id_col = 'Id' if 'Id' in employees_df.columns else 'id'
            print(f"   Primary Key: {id_col}")
            print(f"   Total employees: {len(employees_df)}")
    
    if 'titles' in sheets_data:
        titles_df = sheets_data['titles']
        print("\n📊 Titles Sheet:")
        print(f"   Columns: {list(titles_df.columns)}")
        if 'Simulation Id' in titles_df.columns or 'simulation_id' in titles_df.columns:
            sim_id_col = 'Simulation Id' if 'Simulation Id' in titles_df.columns else 'simulation_id'
            print(f"   Linked to simulation: {sim_id_col}")
    
    return sheets_data

if __name__ == "__main__":
    # Get absolute path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(script_dir))
    filepath = os.path.join(project_root, "output", "vision_data", "vision_extract_sim51_20251211_113107.xlsx")
    
    if not os.path.exists(filepath):
        print(f"ERROR: File not found: {filepath}")
        print("Please provide the correct path to the Excel file")
    else:
        print(f"Reading file: {filepath}")
        analyze_excel_structure(filepath)

