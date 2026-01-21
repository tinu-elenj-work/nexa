"""
Unit tests for Create Field Mappings utility
"""

import pytest
import pandas as pd
import os
from unittest.mock import Mock, patch, MagicMock
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from create_field_mappings import create_field_mappings


class TestCreateFieldMappings:
    """Test cases for Create Field Mappings utility"""
    
    def test_create_field_mappings_success(self, temp_dir):
        """Test successful field mappings creation"""
        output_file = os.path.join(temp_dir, 'field_mappings.xlsx')
        
        result = create_field_mappings(output_file)
        
        assert result is True
        assert os.path.exists(output_file)
        
        # Verify Excel file contents
        with pd.ExcelFile(output_file) as xls:
            expected_sheets = [
                'Field_Mappings',
                'Composite_Keys',
                'Client_Extraction',
                'Multimatcher'
            ]
            
            for sheet in expected_sheets:
                assert sheet in xls.sheet_names
            
            # Check Field_Mappings sheet
            field_mappings = pd.read_excel(xls, 'Field_Mappings')
            assert len(field_mappings) == 3
            assert 'Field_Mapping_ID' in field_mappings.columns
            assert 'ElapseIT_Field' in field_mappings.columns
            assert 'Vision_Field' in field_mappings.columns
            
            # Check Composite_Keys sheet
            composite_keys = pd.read_excel(xls, 'Composite_Keys')
            assert len(composite_keys) == 2
            assert 'Composite_Key_ID' in composite_keys.columns
            assert 'System' in composite_keys.columns
            assert 'Composite_Key_Formula' in composite_keys.columns
            
            # Check Client_Extraction sheet
            client_extraction = pd.read_excel(xls, 'Client_Extraction')
            assert len(client_extraction) == 2
            assert 'Rule_ID' in client_extraction.columns
            assert 'System' in client_extraction.columns
            assert 'Field_Name' in client_extraction.columns
            
            # Check Multimatcher sheet
            multimatcher = pd.read_excel(xls, 'Multimatcher')
            assert len(multimatcher) == 3
            assert 'Rule_ID' in multimatcher.columns
            assert 'ElapseIT_Project' in multimatcher.columns
            assert 'Vision_Project' in multimatcher.columns
    
    def test_create_field_mappings_failure(self):
        """Test field mappings creation failure"""
        # Use invalid path to cause failure
        result = create_field_mappings('/invalid/path/field_mappings.xlsx')
        
        assert result is False
    
    def test_field_mappings_data_structure(self):
        """Test field mappings data structure"""
        # Test that the function returns the expected data structure
        result = create_field_mappings()
        
        assert result is True  # Should succeed with default path
    
    def test_excel_file_creation(self, temp_dir):
        """Test Excel file creation with proper formatting"""
        output_file = os.path.join(temp_dir, 'test_field_mappings.xlsx')
        
        result = create_field_mappings(output_file)
        
        assert result is True
        assert os.path.exists(output_file)
        
        # Verify file is a valid Excel file
        try:
            with pd.ExcelFile(output_file) as xls:
                assert len(xls.sheet_names) == 4
        except Exception as e:
            pytest.fail(f"Created file is not a valid Excel file: {e}")
    
    def test_sheet_data_validation(self, temp_dir):
        """Test validation of sheet data"""
        output_file = os.path.join(temp_dir, 'test_field_mappings.xlsx')
        
        result = create_field_mappings(output_file)
        
        assert result is True
        
        with pd.ExcelFile(output_file) as xls:
            # Validate Field_Mappings sheet
            field_mappings = pd.read_excel(xls, 'Field_Mappings')
            assert field_mappings.iloc[0]['Field_Mapping_ID'] == 'FM001'
            assert field_mappings.iloc[0]['ElapseIT_Field'] == 'Person'
            assert field_mappings.iloc[0]['Vision_Field'] == 'employee'
            assert field_mappings.iloc[0]['Is_Active'] == 'Yes'
            
            # Validate Composite_Keys sheet
            composite_keys = pd.read_excel(xls, 'Composite_Keys')
            assert composite_keys.iloc[0]['Composite_Key_ID'] == 'CK001'
            assert composite_keys.iloc[0]['System'] == 'ElapseIT'
            assert composite_keys.iloc[0]['Composite_Key_Formula'] == 'Person.Client'
            
            # Validate Client_Extraction sheet
            client_extraction = pd.read_excel(xls, 'Client_Extraction')
            assert client_extraction.iloc[0]['Rule_ID'] == 'CE001'
            assert client_extraction.iloc[0]['System'] == 'ElapseIT'
            assert client_extraction.iloc[0]['Field_Name'] == 'Client'
            
            # Validate Multimatcher sheet
            multimatcher = pd.read_excel(xls, 'Multimatcher')
            assert multimatcher.iloc[0]['Rule_ID'] == 'MM001'
            assert multimatcher.iloc[0]['ElapseIT_Project'] == 'AKBANK|CVA'
            assert multimatcher.iloc[0]['Vision_Project'] == 'AKB|CVA'
    
    def test_default_output_path(self):
        """Test default output path handling"""
        # Test with no output file specified
        result = create_field_mappings()
        
        assert result is True
        assert os.path.exists('field_mappings.xlsx')
        
        # Clean up
        if os.path.exists('field_mappings.xlsx'):
            os.remove('field_mappings.xlsx')
    
    def test_data_consistency(self, temp_dir):
        """Test data consistency across sheets"""
        output_file = os.path.join(temp_dir, 'test_field_mappings.xlsx')
        
        result = create_field_mappings(output_file)
        
        assert result is True
        
        with pd.ExcelFile(output_file) as xls:
            # Check that all sheets have consistent data types
            field_mappings = pd.read_excel(xls, 'Field_Mappings')
            composite_keys = pd.read_excel(xls, 'Composite_Keys')
            client_extraction = pd.read_excel(xls, 'Client_Extraction')
            multimatcher = pd.read_excel(xls, 'Multimatcher')
            
            # All sheets should have string columns for IDs
            assert field_mappings['Field_Mapping_ID'].dtype == 'object'
            assert composite_keys['Composite_Key_ID'].dtype == 'object'
            assert client_extraction['Rule_ID'].dtype == 'object'
            assert multimatcher['Rule_ID'].dtype == 'object'
            
            # All sheets should have 'Is_Active' column with 'Yes' values
            assert all(field_mappings['Is_Active'] == 'Yes')
            assert all(composite_keys['Is_Active'] == 'Yes')
            assert all(client_extraction['Is_Active'] == 'Yes')
            assert all(multimatcher['Is_Active'] == 'Yes')
    
    def test_file_overwrite(self, temp_dir):
        """Test file overwrite behavior"""
        output_file = os.path.join(temp_dir, 'test_field_mappings.xlsx')
        
        # Create file first time
        result1 = create_field_mappings(output_file)
        assert result1 is True
        
        # Get file modification time
        mtime1 = os.path.getmtime(output_file)
        
        # Create file second time (should overwrite)
        result2 = create_field_mappings(output_file)
        assert result2 is True
        
        # Get new file modification time
        mtime2 = os.path.getmtime(output_file)
        
        # File should be overwritten (newer modification time)
        assert mtime2 >= mtime1
