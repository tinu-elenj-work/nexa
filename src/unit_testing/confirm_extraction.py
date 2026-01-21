#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Vision Data Extraction Confirmation
Interactive script to confirm which tables to extract before proceeding.
"""

import sys
import os
from table_extraction_config import (
    get_tables_to_extract, 
    get_excluded_tables, 
    get_new_business_tables,
    print_extraction_summary
)

def confirm_extraction():
    """Interactive confirmation of table extraction"""
    print("🔍 Vision Database Extraction Confirmation")
    print("=" * 60)
    
    # Show current configuration
    final_tables = print_extraction_summary()
    
    new_business_tables = get_new_business_tables()
    excluded_tables = get_excluded_tables()
    
    print(f"\n📝 Summary:")
    print(f"   • Total tables to extract: {len(final_tables)}")
    print(f"   • New tables being added: {len(new_business_tables)}")
    print(f"   • Tables excluded: {len(excluded_tables)}")
    
    if new_business_tables:
        print(f"\n🆕 New tables that will be added to extraction:")
        for table in new_business_tables:
            print(f"   + {table}")
    
    print(f"\n❓ Do you want to proceed with extracting these {len(final_tables)} tables?")
    print("   This will update the vision_data_extractor.py to include the new tables.")
    
    while True:
        response = input("\n   Enter 'y' to proceed, 'n' to cancel, or 'm' to modify exclusions: ").lower().strip()
        
        if response == 'y':
            print("\n✅ Confirmed! Proceeding with extraction...")
            return True, final_tables
        elif response == 'n':
            print("\n❌ Extraction cancelled by user.")
            return False, []
        elif response == 'm':
            print("\n🔧 Modification options:")
            print("   1. Add table to exclusions")
            print("   2. Remove table from exclusions")
            print("   3. View current exclusions")
            print("   4. Continue with current settings")
            
            mod_choice = input("   Enter choice (1-4): ").strip()
            
            if mod_choice == '1':
                table_to_exclude = input("   Enter table name to exclude: ").strip()
                if table_to_exclude in final_tables:
                    print(f"   ⚠️  Note: {table_to_exclude} will be excluded from extraction")
                    print("   You'll need to manually update the exclusion list in table_extraction_config.py")
                else:
                    print(f"   ❌ Table '{table_to_exclude}' not found in extraction list")
            elif mod_choice == '2':
                table_to_include = input("   Enter table name to include: ").strip()
                if table_to_include in get_excluded_tables():
                    print(f"   ⚠️  Note: {table_to_include} will be included in extraction")
                    print("   You'll need to manually update the exclusion list in table_extraction_config.py")
                else:
                    print(f"   ❌ Table '{table_to_include}' not found in exclusion list")
            elif mod_choice == '3':
                print(f"\n   Current exclusions: {', '.join(get_excluded_tables())}")
            elif mod_choice == '4':
                continue
            else:
                print("   ❌ Invalid choice")
        else:
            print("   ❌ Please enter 'y', 'n', or 'm'")

if __name__ == "__main__":
    proceed, tables = confirm_extraction()
    if proceed:
        print(f"\n🎯 Ready to extract {len(tables)} tables!")
    else:
        print("\n👋 Extraction cancelled.")
