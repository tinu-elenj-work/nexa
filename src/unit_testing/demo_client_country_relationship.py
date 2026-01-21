#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Demo Client-Country Relationship
Shows how clients are linked to countries through offices.
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

def demo_client_country_relationship():
    """Demonstrate the client-country relationship"""
    print("🔗 Client-Country Relationship Demo")
    print("=" * 60)
    
    try:
        # Create database client
        print("🔗 Connecting to Vision database...")
        client = VisionDBClient(**VISION_DB_CONFIG)
        
        if not client.test_connection():
            print("❌ Failed to connect to Vision database")
            return
        
        print("✅ Database connection successful!")
        
        # Get clients with office information
        print(f"\n📊 Getting clients with office and country information...")
        
        query = """
        SELECT 
            c.id as client_id,
            c.name as client_name,
            c.office_id,
            o.name as office_name,
            o.country,
            o.location
        FROM clients c
        LEFT JOIN office o ON c.office_id = o.id
        WHERE c.simulation_id = %s
        ORDER BY c.name
        """
        
        with client.get_connection() as conn:
            df = pd.read_sql_query(query, conn, params=[30])
        
        print(f"   Found {len(df)} clients")
        print(f"\n📋 Client-Office-Country mapping:")
        print(f"   {'Client Name':<25} {'Office':<20} {'Country':<15} {'Location'}")
        print(f"   {'-'*25} {'-'*20} {'-'*15} {'-'*20}")
        
        for _, row in df.head(10).iterrows():
            client_name = str(row['client_name'])[:24]
            office_name = str(row['office_name'])[:19] if pd.notna(row['office_name']) else 'N/A'
            country = str(row['country'])[:14] if pd.notna(row['country']) else 'N/A'
            location = str(row['location'])[:19] if pd.notna(row['location']) else 'N/A'
            print(f"   {client_name:<25} {office_name:<20} {country:<15} {location}")
        
        # Show unique countries
        unique_countries = df['country'].dropna().unique()
        print(f"\n🌍 Unique countries found: {sorted(unique_countries)}")
        
        # Show relationship summary
        clients_with_office = df[df['office_name'].notna()]
        clients_without_office = df[df['office_name'].isna()]
        
        print(f"\n📊 Relationship Summary:")
        print(f"   Total clients: {len(df)}")
        print(f"   Clients with office: {len(clients_with_office)}")
        print(f"   Clients without office: {len(clients_without_office)}")
        
        if len(clients_without_office) > 0:
            print(f"\n⚠️  Clients without office assignment:")
            for _, row in clients_without_office.iterrows():
                print(f"   - {row['client_name']} (ID: {row['client_id']})")
        
        return df
        
    except Exception as e:
        print(f"❌ Error demonstrating client-country relationship: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    demo_client_country_relationship()

