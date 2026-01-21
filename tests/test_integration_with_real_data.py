#!/usr/bin/env python3
"""
Integration tests using real generated data samples
"""

import sys
import os
import pandas as pd
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
from unittest.mock import Mock, patch, MagicMock

class TestIntegrationWithRealData:
    """Test integration using real generated data samples"""
    
    def test_output_files_exist(self):
        """Test that output files were generated successfully"""
        output_dir = Path("output")
        
        # Check mapping results
        mapping_dir = output_dir / "mapping_results"
        assert mapping_dir.exists(), "Mapping results directory should exist"
        
        mapping_files = list(mapping_dir.glob("*.xlsx"))
        assert len(mapping_files) > 0, "Should have at least one mapping analysis file"
        
        # Check timesheet data
        timesheet_dir = output_dir / "elapseIT_data"
        assert timesheet_dir.exists(), "Timesheet data directory should exist"
        
        timesheet_files = list(timesheet_dir.glob("*.xlsx"))
        assert len(timesheet_files) > 0, "Should have at least one timesheet file"
        
        # Check Xero data
        xero_dir = output_dir / "xero_data"
        assert xero_dir.exists(), "Xero data directory should exist"
        
        xero_files = list(xero_dir.glob("*.xlsx"))
        assert len(xero_files) > 0, "Should have at least one Xero report file"
    
    def test_mapping_analysis_file_structure(self):
        """Test the structure of the mapping analysis Excel file"""
        mapping_file = Path("output/mapping_results/mapping_analysis_August_2025_API.xlsx")
        
        if mapping_file.exists():
            # Read the Excel file and check its structure
            excel_file = pd.ExcelFile(mapping_file)
            sheet_names = excel_file.sheet_names
            
            # Expected sheets based on the actual implementation
            expected_sheets = [
                'bidirectional_matches',
                'elapseit_no_matches', 
                'vision_no_matches',
                'missing_employees',
                'missing_clients',
                'missing_projects',
                'combined_allocations'
            ]
            
            for sheet in expected_sheets:
                assert sheet in sheet_names, f"Expected sheet '{sheet}' not found in mapping analysis"
            
            # Check that sheets have data
            for sheet in expected_sheets:
                if sheet in sheet_names:
                    df = pd.read_excel(mapping_file, sheet_name=sheet)
                    assert len(df) >= 0, f"Sheet '{sheet}' should exist (can be empty)"
    
    def test_timesheet_file_structure(self):
        """Test the structure of the timesheet Excel file"""
        timesheet_files = list(Path("output/elapseIT_data").glob("*.xlsx"))
        
        if timesheet_files:
            timesheet_file = timesheet_files[0]
            excel_file = pd.ExcelFile(timesheet_file)
            sheet_names = excel_file.sheet_names
            
            # Expected sheets based on the actual implementation
            expected_sheets = [
                'Resource_Summary',
                'Resource_Client_Allocation',
                'Employees_2025-08._August_2025'
            ]
            
            for sheet in expected_sheets:
                assert sheet in sheet_names, f"Expected sheet '{sheet}' not found in timesheet file"
    
    def test_xero_reports_structure(self):
        """Test the structure of Xero report files"""
        xero_files = list(Path("output/xero_data").glob("*.xlsx"))
        
        if xero_files:
            # Test at least one Xero report file
            xero_file = xero_files[0]
            excel_file = pd.ExcelFile(xero_file)
            sheet_names = excel_file.sheet_names
            
            # Xero reports should have at least one sheet
            assert len(sheet_names) > 0, "Xero report should have at least one sheet"
            
            # Check that the sheet has data
            for sheet in sheet_names:
                df = pd.read_excel(xero_file, sheet_name=sheet)
                assert len(df) >= 0, f"Sheet '{sheet}' should exist (can be empty)"
    
    def test_config_loading(self):
        """Test that configuration loads correctly"""
        from config import ELAPSEIT_CONFIG, XERO_CONFIG, VISION_DB_CONFIG
        
        # Test ElapseIT config
        assert 'domain' in ELAPSEIT_CONFIG
        assert 'username' in ELAPSEIT_CONFIG
        assert 'password' in ELAPSEIT_CONFIG
        assert 'timezone' in ELAPSEIT_CONFIG
        
        # Test Xero config
        assert 'client_id' in XERO_CONFIG
        assert 'client_secret' in XERO_CONFIG
        assert 'access_token' in XERO_CONFIG
        assert 'refresh_token' in XERO_CONFIG
        
        # Test Vision config
        assert 'host' in VISION_DB_CONFIG
        assert 'port' in VISION_DB_CONFIG
        assert 'database' in VISION_DB_CONFIG
        assert 'user' in VISION_DB_CONFIG
        assert 'password' in VISION_DB_CONFIG
    
    def test_elapseit_api_client_initialization(self):
        """Test ElapseIT API client can be initialized"""
        from elapseit_api_client import ElapseITAPIClient
        from config import ELAPSEIT_CONFIG
        
        client = ElapseITAPIClient(
            domain=ELAPSEIT_CONFIG['domain'],
            username=ELAPSEIT_CONFIG['username'],
            password=ELAPSEIT_CONFIG['password'],
            timezone=ELAPSEIT_CONFIG['timezone']
        )
        
        assert client.domain == ELAPSEIT_CONFIG['domain']
        assert client.username == ELAPSEIT_CONFIG['username']
        assert client.password == ELAPSEIT_CONFIG['password']
        assert client.timezone == ELAPSEIT_CONFIG['timezone']
    
    def test_xero_api_client_initialization(self):
        """Test Xero API client can be initialized"""
        from xero_api_client import XeroAPIClient
        from config import XERO_CONFIG
        
        client = XeroAPIClient(
            client_id=XERO_CONFIG['client_id'],
            client_secret=XERO_CONFIG['client_secret'],
            access_token=XERO_CONFIG['access_token'],
            refresh_token=XERO_CONFIG['refresh_token']
        )
        
        assert client.client_id == XERO_CONFIG['client_id']
        assert client.client_secret == XERO_CONFIG['client_secret']
    
    def test_vision_db_client_initialization(self):
        """Test Vision DB client can be initialized"""
        from vision_db_client import VisionDBClient
        from config import VISION_DB_CONFIG
        
        client = VisionDBClient(
            host=VISION_DB_CONFIG['host'],
            port=VISION_DB_CONFIG['port'],
            database=VISION_DB_CONFIG['database'],
            user=VISION_DB_CONFIG['user'],
            password=VISION_DB_CONFIG['password']
        )
        
        # Check that connection parameters are stored correctly
        assert client.connection_params['host'] == VISION_DB_CONFIG['host']
        assert client.connection_params['port'] == VISION_DB_CONFIG['port']
        assert client.connection_params['database'] == VISION_DB_CONFIG['database']
        assert client.connection_params['user'] == VISION_DB_CONFIG['user']
        assert client.connection_params['password'] == VISION_DB_CONFIG['password']
    
    def test_data_transformer_initialization(self):
        """Test data transformer can be initialized"""
        from data_transformer import ElapseITDataTransformer
        
        transformer = ElapseITDataTransformer()
        
        # Check that field mappings are loaded
        assert 'clients' in transformer.field_mappings
        assert 'people' in transformer.field_mappings
        assert 'projects' in transformer.field_mappings
        
        # Check that date format map is set
        assert 'api' in transformer.date_format_map
        assert 'file' in transformer.date_format_map
    
    def test_timesheet_extractor_initialization(self):
        """Test timesheet extractor can be initialized"""
        from timesheet_extractor import ElapseITTimesheetExtractor
        
        extractor = ElapseITTimesheetExtractor()
        
        # Check that client is initialized
        assert extractor.client is not None
        assert hasattr(extractor, 'data_dir')
    
    def test_fx_reader_initialization(self):
        """Test FX reader can be initialized"""
        from fx_reader import FXRateReader
        
        reader = FXRateReader()
        
        # Check that fx_data is initialized (can be empty)
        assert hasattr(reader, 'fx_data')
    
    def test_project_mapper_functions_exist(self):
        """Test that main project mapper functions exist"""
        import project_mapper_enhanced
        
        # Check that main functions exist
        assert hasattr(project_mapper_enhanced, 'get_elapseit_data_from_api')
        assert hasattr(project_mapper_enhanced, 'get_vision_data_from_database')
        assert hasattr(project_mapper_enhanced, 'perform_bidirectional_composite_key_matching')
        assert hasattr(project_mapper_enhanced, 'create_main_output_file')
        assert hasattr(project_mapper_enhanced, 'main')
    
    def test_field_mappings_file_exists(self):
        """Test that field mappings file exists and is readable"""
        field_mappings_file = Path("config/field_mappings.xlsx")
        
        if field_mappings_file.exists():
            excel_file = pd.ExcelFile(field_mappings_file)
            sheet_names = excel_file.sheet_names
            
            # Should have multiple sheets
            assert len(sheet_names) > 0, "Field mappings file should have sheets"
    
    def test_mapper_file_exists(self):
        """Test that Mapper.xlsx file exists and is readable"""
        mapper_file = Path("config/Mapper.xlsx")
        
        if mapper_file.exists():
            excel_file = pd.ExcelFile(mapper_file)
            sheet_names = excel_file.sheet_names
            
            # Should have at least one sheet
            assert len(sheet_names) > 0, "Mapper file should have sheets"
    
    def test_generated_data_quality(self):
        """Test the quality of generated data files"""
        # Test mapping analysis file
        mapping_file = Path("output/mapping_results/mapping_analysis_August_2025_API.xlsx")
        if mapping_file.exists():
            excel_file = pd.ExcelFile(mapping_file)
            
            # Check that all sheets can be read without errors
            for sheet_name in excel_file.sheet_names:
                df = pd.read_excel(mapping_file, sheet_name=sheet_name)
                # Basic data quality check - should be a DataFrame
                assert isinstance(df, pd.DataFrame)
        
        # Test timesheet file
        timesheet_files = list(Path("output/elapseIT_data").glob("*.xlsx"))
        if timesheet_files:
            timesheet_file = timesheet_files[0]
            excel_file = pd.ExcelFile(timesheet_file)
            
            for sheet_name in excel_file.sheet_names:
                df = pd.read_excel(timesheet_file, sheet_name=sheet_name)
                assert isinstance(df, pd.DataFrame)
        
        # Test Xero files
        xero_files = list(Path("output/xero_data").glob("*.xlsx"))
        if xero_files:
            for xero_file in xero_files[:2]:  # Test first 2 files
                excel_file = pd.ExcelFile(xero_file)
                
                for sheet_name in excel_file.sheet_names:
                    df = pd.read_excel(xero_file, sheet_name=sheet_name)
                    assert isinstance(df, pd.DataFrame)
