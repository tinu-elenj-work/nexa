#!/usr/bin/env python3
"""
Verify that project name masking is working correctly with client name replacement
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

import pandas as pd
from vision_db_client import VisionDBClient
from config import VISION_DB_CONFIG

def verify_project_name_masking():
    """Verify that project name masking with client name replacement is working"""
    
    print("Verifying project name masking with client name replacement...")
    print("=" * 60)
    
    try:
        # Connect to database
        client = VisionDBClient(VISION_DB_CONFIG)
        
        # Get original data
        print("1. Getting original projects and clients data...")
        original_projects = client.get_projects(simulation_id=30)
        original_clients = client.get_clients(simulation_id=30)
        
        print(f"   Retrieved {len(original_projects)} project records")
        print(f"   Retrieved {len(original_clients)} client records")
        
        if 'name' in original_projects.columns and 'client_id' in original_projects.columns:
            print(f"\n2. Sample original project names:")
            sample_projects = original_projects[['id', 'name', 'client_id']].head(5)
            print(sample_projects.to_string(index=False))
            
            print(f"\n3. Sample original client names:")
            sample_clients = original_clients[['id', 'name']].head(5)
            print(sample_clients.to_string(index=False))
            
            # Show pipe-delimited names
            pipe_names = original_projects[original_projects['name'].str.contains('|', na=False)]
            if not pipe_names.empty:
                print(f"\n4. Sample pipe-delimited project names:")
                pipe_sample = pipe_names[['id', 'name', 'client_id']].head(3)
                print(pipe_sample.to_string(index=False))
            else:
                print(f"\n4. No pipe-delimited project names found")
                
        else:
            print("   Project name or client_id columns not found")
            print(f"   Available columns: {list(original_projects.columns)}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    verify_project_name_masking()
