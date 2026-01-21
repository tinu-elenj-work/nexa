"""
Unit tests for Timesheet Extractor
"""

import pytest
import pandas as pd
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, date
import sys
import os

# Add src and project root to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from timesheet_extractor import ElapseITTimesheetExtractor


class TestElapseITTimesheetExtractor:
    """Test cases for ElapseIT Timesheet Extractor"""
    
    @patch('elapseit_api_client.ElapseITAPIClient')
    def test_init(self, mock_api_client_class):
        """Test extractor initialization"""
        mock_client = Mock()
        mock_api_client_class.return_value = mock_client
        
        extractor = ElapseITTimesheetExtractor()
        
        assert extractor.client == mock_client
        assert extractor.data_dir == "elapseIT_data"
        assert extractor.archive_dir == "elapseIT_data/archive"
        mock_api_client_class.assert_called_once()
    
    def test_parse_date_range_valid(self):
        """Test valid date range parsing"""
        extractor = ElapseITTimesheetExtractor()
        
        # Test with start and end dates
        start_date, end_date = extractor.parse_date_range("2024-01-01", "2024-01-31")
        
        assert start_date == date(2024, 1, 1)
        assert end_date == date(2024, 1, 31)
    
    def test_parse_date_range_month_year(self):
        """Test date range parsing with month and year"""
        extractor = ElapseITTimesheetExtractor()
        
        # Test with month and year
        start_date, end_date = extractor.parse_date_range("January 2024")
        
        assert start_date == date(2024, 1, 1)
        assert end_date == date(2024, 1, 31)
    
    def test_parse_date_range_year_only(self):
        """Test date range parsing with year only"""
        extractor = ElapseITTimesheetExtractor()
        
        # Test with year only
        start_date, end_date = extractor.parse_date_range("2024")
        
        assert start_date == date(2024, 1, 1)
        assert end_date == date(2024, 12, 31)
    
    def test_parse_date_range_invalid(self):
        """Test date range parsing with invalid input"""
        extractor = ElapseITTimesheetExtractor()
        
        # Test with invalid input
        with pytest.raises(ValueError):
            extractor.parse_date_range("invalid-date")
    
    def test_get_month_columns(self):
        """Test month columns generation"""
        extractor = ElapseITTimesheetExtractor()
        
        start_date = date(2024, 1, 1)
        end_date = date(2024, 3, 31)
        
        columns = extractor.get_month_columns(start_date, end_date)
        
        expected_columns = ['January 2024', 'February 2024', 'March 2024']
        assert columns == expected_columns
    
    def test_get_month_columns_single_month(self):
        """Test month columns generation for single month"""
        extractor = ElapseITTimesheetExtractor()
        
        start_date = date(2024, 1, 1)
        end_date = date(2024, 1, 31)
        
        columns = extractor.get_month_columns(start_date, end_date)
        
        expected_columns = ['January 2024']
        assert columns == expected_columns
    
    def test_get_month_columns_cross_year(self):
        """Test month columns generation across years"""
        extractor = ElapseITTimesheetExtractor()
        
        start_date = date(2023, 12, 1)
        end_date = date(2024, 2, 29)
        
        columns = extractor.get_month_columns(start_date, end_date)
        
        expected_columns = ['December 2023', 'January 2024', 'February 2024']
        assert columns == expected_columns
    
    def test_group_timesheet_data_by_client(self):
        """Test timesheet data grouping by client"""
        extractor = ElapseITTimesheetExtractor()
        
        timesheet_data = [
            {
                'PersonName': 'John Doe',
                'ClientName': 'Client A',
                'AllocationName': 'Project Alpha',
                'Date': '2024-01-15',
                'Hours': 8.0
            },
            {
                'PersonName': 'Jane Smith',
                'ClientName': 'Client A',
                'AllocationName': 'Project Alpha',
                'Date': '2024-01-15',
                'Hours': 6.0
            },
            {
                'PersonName': 'John Doe',
                'ClientName': 'Client B',
                'AllocationName': 'Project Beta',
                'Date': '2024-01-15',
                'Hours': 4.0
            }
        ]
        
        month_columns = ['January 2024']
        result = extractor.group_timesheet_data_by_client(timesheet_data, month_columns)
        
        assert result is not None
        assert len(result) == 3  # 3 unique combinations
        
        # Check that data is properly grouped
        client_a_alpha = result[(result['Client_Name'] == 'Client A') & 
                               (result['Allocation_Name'] == 'Project Alpha')]
        assert len(client_a_alpha) == 2  # John Doe and Jane Smith
        
        # Check total hours
        total_hours = client_a_alpha['January 2024'].sum()
        assert total_hours == 14.0  # 8.0 + 6.0
    
    def test_group_timesheet_data_by_resource(self):
        """Test timesheet data grouping by resource"""
        extractor = ElapseITTimesheetExtractor()
        
        timesheet_data = [
            {
                'PersonName': 'John Doe',
                'ClientName': 'Client A',
                'AllocationName': 'Project Alpha',
                'Date': '2024-01-15',
                'Hours': 8.0
            },
            {
                'PersonName': 'John Doe',
                'ClientName': 'Client B',
                'AllocationName': 'Project Beta',
                'Date': '2024-01-15',
                'Hours': 4.0
            },
            {
                'PersonName': 'Jane Smith',
                'ClientName': 'Client A',
                'AllocationName': 'Project Alpha',
                'Date': '2024-01-15',
                'Hours': 6.0
            }
        ]
        
        month_columns = ['January 2024']
        result = extractor.group_timesheet_data_by_resource(timesheet_data, month_columns)
        
        assert result is not None
        assert len(result) == 3  # 3 unique combinations
        
        # Check that data is properly grouped by resource
        john_doe = result[result['Resource_Name'] == 'John Doe']
        assert len(john_doe) == 2  # Client A and Client B
        
        # Check total hours for John Doe
        total_hours = john_doe['January 2024'].sum()
        assert total_hours == 12.0  # 8.0 + 4.0
    
    def test_create_excel_report(self, temp_dir):
        """Test Excel report creation"""
        extractor = ElapseITTimesheetExtractor()
        
        # Create test data
        client_data = pd.DataFrame([
            {
                'Client_Name': 'Client A',
                'Allocation_Name': 'Project Alpha',
                'Resource_Name': 'John Doe',
                'January 2024': 8.0,
                'Total_Hours': 8.0
            }
        ])
        
        resource_data = pd.DataFrame([
            {
                'Resource_Name': 'John Doe',
                'Client_Name': 'Client A',
                'Allocation_Name': 'Project Alpha',
                'January 2024': 8.0,
                'Total_Hours': 8.0
            }
        ])
        
        output_file = os.path.join(temp_dir, 'test_timesheet_report.xlsx')
        
        result = extractor.create_excel_report(
            client_data, resource_data, output_file, 
            '2024-01-01', '2024-01-31'
        )
        
        assert result is True
        assert os.path.exists(output_file)
        
        # Verify Excel file contents
        with pd.ExcelFile(output_file) as xls:
            assert 'Client_Allocation_Resource' in xls.sheet_names
            assert 'Resource_Client_Allocation' in xls.sheet_names
            
            # Check client sheet
            client_sheet = pd.read_excel(xls, 'Client_Allocation_Resource')
            assert len(client_sheet) == 1
            assert client_sheet.iloc[0]['Client_Name'] == 'Client A'
            
            # Check resource sheet
            resource_sheet = pd.read_excel(xls, 'Resource_Client_Allocation')
            assert len(resource_sheet) == 1
            assert resource_sheet.iloc[0]['Resource_Name'] == 'John Doe'
    
    def test_create_excel_report_failure(self, temp_dir):
        """Test Excel report creation failure"""
        extractor = ElapseITTimesheetExtractor()
        
        # Create test data
        client_data = pd.DataFrame()
        resource_data = pd.DataFrame()
        
        # Use invalid path to cause failure
        output_file = '/invalid/path/test_timesheet_report.xlsx'
        
        result = extractor.create_excel_report(
            client_data, resource_data, output_file, 
            '2024-01-01', '2024-01-31'
        )
        
        assert result is False
    
    @patch.object(ElapseITTimesheetExtractor, 'parse_date_range')
    @patch.object(ElapseITTimesheetExtractor, 'get_month_columns')
    @patch.object(ElapseITTimesheetExtractor, 'group_timesheet_data_by_client')
    @patch.object(ElapseITTimesheetExtractor, 'group_timesheet_data_by_resource')
    @patch.object(ElapseITTimesheetExtractor, 'create_excel_report')
    def test_extract_timesheet_data_success(self, mock_create_report, mock_group_resource, 
                                          mock_group_client, mock_get_columns, mock_parse_range):
        """Test successful timesheet data extraction"""
        # Mock dependencies
        mock_parse_range.return_value = (date(2024, 1, 1), date(2024, 1, 31))
        mock_get_columns.return_value = ['January 2024']
        mock_group_client.return_value = pd.DataFrame([{'Client_Name': 'Client A'}])
        mock_group_resource.return_value = pd.DataFrame([{'Resource_Name': 'John Doe'}])
        mock_create_report.return_value = True
        
        # Mock API client
        extractor = ElapseITTimesheetExtractor()
        extractor.client.get_timesheet_records.return_value = [
            {
                'PersonName': 'John Doe',
                'ClientName': 'Client A',
                'AllocationName': 'Project Alpha',
                'Date': '2024-01-15',
                'Hours': 8.0
            }
        ]
        
        result = extractor.extract_timesheet_data('2024-01-01', '2024-01-31')
        
        assert result is True
        extractor.client.get_timesheet_records.assert_called_once_with('2024-01-01', '2024-01-31')
        mock_parse_range.assert_called_once_with('2024-01-01', '2024-01-31')
        mock_get_columns.assert_called_once()
        mock_group_client.assert_called_once()
        mock_group_resource.assert_called_once()
        mock_create_report.assert_called_once()
    
    @patch.object(ElapseITTimesheetExtractor, 'parse_date_range')
    def test_extract_timesheet_data_invalid_date(self, mock_parse_range):
        """Test timesheet extraction with invalid date range"""
        mock_parse_range.side_effect = ValueError("Invalid date")
        
        extractor = ElapseITTimesheetExtractor()
        
        result = extractor.extract_timesheet_data('invalid-date')
        
        assert result is False
    
    @patch.object(ElapseITTimesheetExtractor, 'parse_date_range')
    def test_extract_timesheet_data_api_failure(self, mock_parse_range):
        """Test timesheet extraction with API failure"""
        mock_parse_range.return_value = (date(2024, 1, 1), date(2024, 1, 31))
        
        extractor = ElapseITTimesheetExtractor()
        extractor.client.get_timesheet_records.return_value = None
        
        result = extractor.extract_timesheet_data('2024-01-01', '2024-01-31')
        
        assert result is False
    
    def test_archive_existing_files(self, temp_dir):
        """Test archiving of existing files"""
        extractor = ElapseITTimesheetExtractor()
        
        # Create test directories
        data_dir = os.path.join(temp_dir, 'elapseIT_data')
        archive_dir = os.path.join(temp_dir, 'elapseIT_data', 'archive')
        os.makedirs(data_dir, exist_ok=True)
        os.makedirs(archive_dir, exist_ok=True)
        
        # Create test file
        test_file = os.path.join(data_dir, 'timesheets_20240101_to_20240131_120000.xlsx')
        with open(test_file, 'w') as f:
            f.write('test content')
        
        # Update extractor paths
        extractor.data_dir = data_dir
        extractor.archive_dir = archive_dir
        
        result = extractor.archive_existing_files()
        
        assert result is True
        assert not os.path.exists(test_file)  # Original file should be moved
        assert os.path.exists(os.path.join(archive_dir, 'legacy_120000_timesheets_20240101_to_20240131_120000.xlsx'))
    
    def test_archive_existing_files_no_files(self, temp_dir):
        """Test archiving when no files exist"""
        extractor = ElapseITTimesheetExtractor()
        
        # Create test directories
        data_dir = os.path.join(temp_dir, 'elapseIT_data')
        archive_dir = os.path.join(temp_dir, 'elapseIT_data', 'archive')
        os.makedirs(data_dir, exist_ok=True)
        os.makedirs(archive_dir, exist_ok=True)
        
        # Update extractor paths
        extractor.data_dir = data_dir
        extractor.archive_dir = archive_dir
        
        result = extractor.archive_existing_files()
        
        assert result is True  # Should succeed even with no files
    
    def test_get_output_filename(self):
        """Test output filename generation"""
        extractor = ElapseITTimesheetExtractor()
        
        filename = extractor.get_output_filename('2024-01-01', '2024-01-31')
        
        assert filename.startswith('timesheets_20240101_to_20240131_')
        assert filename.endswith('.xlsx')
        assert len(filename) == len('timesheets_20240101_to_20240131_') + 6 + len('.xlsx')
    
    def test_validate_date_range(self):
        """Test date range validation"""
        extractor = ElapseITTimesheetExtractor()
        
        # Valid range
        assert extractor.validate_date_range(date(2024, 1, 1), date(2024, 1, 31)) is True
        
        # Invalid range (start after end)
        assert extractor.validate_date_range(date(2024, 1, 31), date(2024, 1, 1)) is False
        
        # Same date (valid)
        assert extractor.validate_date_range(date(2024, 1, 1), date(2024, 1, 1)) is True
