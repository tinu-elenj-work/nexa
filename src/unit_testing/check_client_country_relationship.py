#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Check Client-Country Relationship
Examines how clients are linked to countries through the database schema.
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

def check_client_country_relationship():
    """Check how clients are linked to countries"""
    print("🔍 Client-Country Relationship Analysis")
    print("=" * 60)
    
    try:
        # Create database client
        print("🔗 Connecting to Vision database...")
        client = VisionDBClient(**VISION_DB_CONFIG)
        
        if not client.test_connection():
            print("❌ Failed to connect to Vision database")
            return
        
        print("✅ Database connection successful!")
        
        # Check clients table structure
        print(f"\n📋 Clients table structure:")
        clients_schema = client.get_table_schema("clients")
        print(f"   Columns: {sorted(clients_schema['column_name'].tolist())}")
        
        # Check office table structure
        print(f"\n📋 Office table structure:")
        office_schema = client.get_table_schema("office")
        print(f"   Columns: {sorted(office_schema['column_name'].tolist())}")
        
        # Get sample data to see the relationship
        print(f"\n📊 Sample clients data:")
        clients_df = client.get_clients(simulation_id=30)
        print(f"   Columns: {sorted(clients_df.columns.tolist())}")
        print(f"   Sample records:")
        print(clients_df[['id', 'name', 'office_id']].head())
        
        print(f"\n📊 Sample office data:")
        office_df = client.get_office(simulation_id=30)
        print(f"   Columns: {sorted(office_df.columns.tolist())}")
        print(f"   Sample records:")
        print(office_df[['id', 'name', 'country', 'location']].head())
        
        # Check if there's a direct relationship
        print(f"\n🔗 Checking client-office relationship:")
        if 'office_id' in clients_df.columns and 'id' in office_df.columns:
            # Join clients with offices to see the relationship
            joined_df = clients_df.merge(office_df, left_on='office_id', right_on='id', how='left', suffixes=('_client', '_office'))
            print(f"   Joined columns: {sorted(joined_df.columns.tolist())}")
            print(f"   Sample joined data:")
            print(joined_df[['name_client', 'name_office', 'country', 'location']].head())
            
            # Check if all clients have office assignments
            clients_with_office = joined_df[joined_df['name_office'].notna()]
            print(f"\n📊 Relationship summary:")
            print(f"   Total clients: {len(clients_df)}")
            print(f"   Clients with office: {len(clients_with_office)}")
            print(f"   Clients without office: {len(clients_df) - len(clients_with_office)}")
            
            # Show unique countries
            unique_countries = joined_df['country'].dropna().unique()
            print(f"   Unique countries: {sorted(unique_countries)}")
            
        else:
            print("   ❌ Cannot establish relationship - missing office_id in clients or id in office")
        
        # Check if there are any other tables that might link clients to countries
        print(f"\n🔍 Checking for other potential country relationships:")
        
        # Check if there are any foreign key relationships
        print(f"\n📋 Checking foreign key relationships...")
        with client.get_connection() as conn:
            cursor = conn.cursor()
            
            # Check foreign keys for clients table
            cursor.execute("""
                SELECT 
                    tc.table_name, 
                    kcu.column_name, 
                    ccu.table_name AS foreign_table_name,
                    ccu.column_name AS foreign_column_name 
                FROM 
                    information_schema.table_constraints AS tc 
                    JOIN information_schema.key_column_usage AS kcu
                      ON tc.constraint_name = kcu.constraint_name
                      AND tc.table_schema = kcu.table_schema
                    JOIN information_schema.constraint_column_usage AS ccu
                      ON ccu.constraint_name = tc.constraint_name
                      AND ccu.table_schema = tc.table_schema
                WHERE tc.constraint_type = 'FOREIGN KEY' 
                AND tc.table_name = 'clients'
            """)
            fk_results = cursor.fetchall()
            print(f"   Foreign keys for clients table:")
            for fk in fk_results:
                print(f"     {fk[1]} -> {fk[2]}.{fk[3]}")
            
            # Check foreign keys for office table
            cursor.execute("""
                SELECT 
                    tc.table_name, 
                    kcu.column_name, 
                    ccu.table_name AS foreign_table_name,
                    ccu.column_name AS foreign_column_name 
                FROM 
                    information_schema.table_constraints AS tc 
                    JOIN information_schema.key_column_usage AS kcu
                      ON tc.constraint_name = kcu.constraint_name
                      AND tc.table_schema = kcu.table_schema
                    JOIN information_schema.constraint_column_usage AS ccu
                      ON ccu.constraint_name = tc.constraint_name
                      AND ccu.table_schema = tc.table_schema
                WHERE tc.constraint_type = 'FOREIGN KEY' 
                AND tc.table_name = 'office'
            """)
            fk_results = cursor.fetchall()
            print(f"   Foreign keys for office table:")
            for fk in fk_results:
                print(f"     {fk[1]} -> {fk[2]}.{fk[3]}")
        
    except Exception as e:
        print(f"❌ Error checking client-country relationship: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_client_country_relationship()

