#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Table Extraction Configuration
Manages which tables to extract from Vision database and exclusion lists.
"""

# Tables currently being extracted (existing)
CURRENT_EXTRACTED_TABLES = [
    "allocations",
    "employees", 
    "projects",
    "clients",
    "confidences",
    "calendars",
    "calendar_holidays",
    "currencies",
    "exchange_rates",
    "office",
    "salaries"
]

# New tables found in database (not currently extracted)
NEW_TABLES_FOUND = [
    "alembic_version",
    "audit_logs", 
    "simulation",
    "simulation_approvals",
    "titles",
    "user_account"
]

# Tables to exclude from extraction (system tables, empty tables, etc.)
EXCLUDED_TABLES = [
    "alembic_version",  # Database migration version - not business data
    "simulation_approvals",  # Empty table (0 rows)
    "audit_logs",  # Audit trail data - excluded per user request
    "user_account",  # User account information - excluded per user request
]

# Tables that should be extracted (business-relevant tables)
BUSINESS_TABLES = [
    "simulation",  # Simulation metadata
    "titles",      # Job titles/positions
]

def get_all_available_tables():
    """Get all tables currently in the database"""
    return CURRENT_EXTRACTED_TABLES + NEW_TABLES_FOUND

def get_tables_to_extract():
    """Get the final list of tables to extract"""
    all_tables = get_all_available_tables()
    return [table for table in all_tables if table not in EXCLUDED_TABLES]

def get_excluded_tables():
    """Get list of excluded tables"""
    return EXCLUDED_TABLES

def get_new_business_tables():
    """Get new business-relevant tables that should be added to extraction"""
    return [table for table in NEW_TABLES_FOUND if table not in EXCLUDED_TABLES]

def print_extraction_summary():
    """Print a summary of the extraction configuration"""
    print("📊 Vision Database Table Extraction Configuration")
    print("=" * 60)
    
    print(f"\n✅ Currently Extracted Tables ({len(CURRENT_EXTRACTED_TABLES)}):")
    for table in CURRENT_EXTRACTED_TABLES:
        print(f"   - {table}")
    
    print(f"\n🆕 New Tables Found ({len(NEW_TABLES_FOUND)}):")
    for table in NEW_TABLES_FOUND:
        status = "❌ EXCLUDED" if table in EXCLUDED_TABLES else "✅ TO EXTRACT"
        print(f"   - {table} ({status})")
    
    print(f"\n🚫 Excluded Tables ({len(EXCLUDED_TABLES)}):")
    for table in EXCLUDED_TABLES:
        reason = "System table" if table == "alembic_version" else "Empty table" if table == "simulation_approvals" else "Other"
        print(f"   - {table} ({reason})")
    
    final_tables = get_tables_to_extract()
    print(f"\n📋 Final Extraction List ({len(final_tables)} tables):")
    for table in final_tables:
        status = "NEW" if table in NEW_TABLES_FOUND else "EXISTING"
        print(f"   - {table} ({status})")
    
    return final_tables

if __name__ == "__main__":
    print_extraction_summary()
