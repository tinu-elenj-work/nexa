"""
Unit tests for Project Mapper Enhanced (Main Application)
"""

import pytest
import pandas as pd
from unittest.mock import Mock, patch, MagicMock
import sys
import os
import argparse

# Add src and project root to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Import the main application
import project_mapper_enhanced


class TestProjectMapperEnhanced:
    """Test cases for Project Mapper Enhanced"""
    
    def test_read_excel_file_success(self, temp_dir):
        """Test successful Excel file reading"""
        # Create test Excel file
        test_file = os.path.join(temp_dir, 'test.xlsx')
        df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
        df.to_excel(test_file, index=False)
        
        result = project_mapper_enhanced.read_excel_file(test_file)
        
        assert result is not None
        assert len(result) == 3
        assert list(result.columns) == ['A', 'B']
    
    def test_read_excel_file_not_found(self):
        """Test Excel file reading when file doesn't exist"""
        result = project_mapper_enhanced.read_excel_file('nonexistent.xlsx')
        
        assert result is None
    
    def test_read_csv_file_success(self, temp_dir):
        """Test successful CSV file reading"""
        # Create test CSV file
        test_file = os.path.join(temp_dir, 'test.csv')
        df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
        df.to_csv(test_file, index=False)
        
        result = project_mapper_enhanced.read_csv_file(test_file)
        
        assert result is not None
        assert len(result) == 3
        assert list(result.columns) == ['A', 'B']
    
    def test_read_csv_file_encoding_issues(self, temp_dir):
        """Test CSV file reading with encoding issues"""
        # Create test CSV file with special characters
        test_file = os.path.join(temp_dir, 'test.csv')
        with open(test_file, 'w', encoding='utf-16') as f:
            f.write('A,B\n1,2\n3,4\n')
        
        result = project_mapper_enhanced.read_csv_file(test_file)
        
        assert result is not None
        assert len(result) == 2
    
    def test_read_csv_file_not_found(self):
        """Test CSV file reading when file doesn't exist"""
        result = project_mapper_enhanced.read_csv_file('nonexistent.csv')
        
        assert result is None
    
    @patch('elapseit_api_client.ElapseITAPIClient')
    @patch('data_transformer.ElapseITDataTransformer')
    def test_get_elapseit_data_from_api_success(self, mock_transformer_class, mock_client_class):
        """Test successful ElapseIT data retrieval from API"""
        # Mock API client
        mock_client = Mock()
        mock_client.get_all_data.return_value = {
            'clients': [{'ID': 1, 'Name': 'Test Client'}],
            'people': [{'ID': 1, 'FirstName': 'John'}],
            'projects': [{'ID': 1, 'Name': 'Test Project'}],
            'allocations': [{'ID': 1, 'ProjectID': 1}]
        }
        mock_client_class.return_value = mock_client
        
        # Mock transformer
        mock_transformer = Mock()
        mock_transformer.transform_all_data.return_value = {
            'clients': [{'ID': 1, 'Name': 'Test Client'}],
            'people': [{'ID': 1, 'FirstName': 'John'}],
            'projects': [{'ID': 1, 'Name': 'Test Project'}],
            'allocations': [{'ID': 1, 'ProjectID': 1}]
        }
        mock_transformer_class.return_value = mock_transformer
        
        result = project_mapper_enhanced.get_elapseit_data_from_api()
        
        assert result is not None
        assert 'clients' in result
        assert 'people' in result
        assert 'projects' in result
        assert 'allocations' in result
        
        mock_client.get_all_data.assert_called_once()
        mock_transformer.transform_all_data.assert_called_once()
    
    @patch('elapseit_api_client.ElapseITAPIClient')
    def test_get_elapseit_data_from_api_failure(self, mock_client_class):
        """Test ElapseIT data retrieval failure"""
        mock_client = Mock()
        mock_client.get_all_data.return_value = None
        mock_client_class.return_value = mock_client
        
        result = project_mapper_enhanced.get_elapseit_data_from_api()
        
        assert result is None
    
    @patch('vision_db_client.VisionDBClient')
    def test_get_vision_data_from_db_success(self, mock_client_class):
        """Test successful Vision data retrieval from database"""
        mock_client = Mock()
        mock_client.get_all_data.return_value = {
            'allocations': pd.DataFrame([{'id': 1, 'employee_id': 1, 'project_id': 1}]),
            'clients': pd.DataFrame([{'id': 1, 'name': 'Test Client'}]),
            'employees': pd.DataFrame([{'id': 1, 'name': 'John Doe'}]),
            'projects': pd.DataFrame([{'id': 1, 'name': 'Test Project'}])
        }
        mock_client_class.return_value = mock_client
        
        result = project_mapper_enhanced.get_vision_data_from_db()
        
        assert result is not None
        assert 'allocations' in result
        assert 'clients' in result
        assert 'employees' in result
        assert 'projects' in result
        
        mock_client.get_all_data.assert_called_once()
    
    @patch('vision_db_client.VisionDBClient')
    def test_get_vision_data_from_db_failure(self, mock_client_class):
        """Test Vision data retrieval failure"""
        mock_client = Mock()
        mock_client.get_all_data.return_value = None
        mock_client_class.return_value = mock_client
        
        result = project_mapper_enhanced.get_vision_data_from_db()
        
        assert result is None
    
    def test_get_vision_data_from_csv_success(self, temp_dir):
        """Test successful Vision data retrieval from CSV files"""
        # Create test CSV files
        data_dir = os.path.join(temp_dir, 'vision_data')
        os.makedirs(data_dir, exist_ok=True)
        
        # Create test CSV files
        allocations_df = pd.DataFrame([{'id': 1, 'employee_id': 1, 'project_id': 1}])
        clients_df = pd.DataFrame([{'id': 1, 'name': 'Test Client'}])
        employees_df = pd.DataFrame([{'id': 1, 'name': 'John Doe'}])
        projects_df = pd.DataFrame([{'id': 1, 'name': 'Test Project'}])
        
        allocations_df.to_csv(os.path.join(data_dir, 'allocations.csv'), index=False)
        clients_df.to_csv(os.path.join(data_dir, 'clients.csv'), index=False)
        employees_df.to_csv(os.path.join(data_dir, 'employees.csv'), index=False)
        projects_df.to_csv(os.path.join(data_dir, 'projects.csv'), index=False)
        
        with patch('os.path.exists', return_value=True):
            result = project_mapper_enhanced.get_vision_data_from_csv(data_dir)
        
        assert result is not None
        assert 'allocations' in result
        assert 'clients' in result
        assert 'employees' in result
        assert 'projects' in result
        
        assert len(result['allocations']) == 1
        assert len(result['clients']) == 1
        assert len(result['employees']) == 1
        assert len(result['projects']) == 1
    
    def test_get_vision_data_from_csv_missing_files(self, temp_dir):
        """Test Vision data retrieval with missing CSV files"""
        data_dir = os.path.join(temp_dir, 'vision_data')
        os.makedirs(data_dir, exist_ok=True)
        
        with patch('os.path.exists', return_value=False):
            result = project_mapper_enhanced.get_vision_data_from_csv(data_dir)
        
        assert result is None
    
    def test_create_composite_key(self):
        """Test composite key creation"""
        # Test with valid data
        result = project_mapper_enhanced.create_composite_key('John Doe', 'Test Client')
        assert result == 'John Doe.Test Client'
        
        # Test with None values
        result = project_mapper_enhanced.create_composite_key(None, 'Test Client')
        assert result == 'None.Test Client'
        
        result = project_mapper_enhanced.create_composite_key('John Doe', None)
        assert result == 'John Doe.None'
        
        # Test with both None
        result = project_mapper_enhanced.create_composite_key(None, None)
        assert result == 'None.None'
    
    def test_perform_bidirectional_matching(self):
        """Test bidirectional matching logic"""
        # Create test data
        elapseit_data = pd.DataFrame([
            {'Person': 'John Doe', 'Client': 'Client A', 'Project': 'Project 1', 'Hours': 8.0},
            {'Person': 'Jane Smith', 'Client': 'Client B', 'Project': 'Project 2', 'Hours': 6.0}
        ])
        
        vision_data = pd.DataFrame([
            {'employee': 'John Doe', 'client': 'Client A', 'project': 'Project 1', 'hours': 8.0},
            {'Person': 'Bob Wilson', 'Client': 'Client C', 'Project': 'Project 3', 'Hours': 4.0}
        ])
        
        result = project_mapper_enhanced.perform_bidirectional_matching(elapseit_data, vision_data)
        
        assert 'matches' in result
        assert 'elapseit_no_matches' in result
        assert 'vision_no_matches' in result
        
        # Should have 1 match (John Doe + Client A + Project 1)
        assert len(result['matches']) == 1
        # Should have 1 ElapseIT entry without match (Jane Smith)
        assert len(result['elapseit_no_matches']) == 1
        # Should have 1 Vision entry without match (Bob Wilson)
        assert len(result['vision_no_matches']) == 1
    
    def test_analyze_missing_employees(self):
        """Test missing employees analysis"""
        elapseit_people = pd.DataFrame([
            {'FirstName': 'John', 'LastName': 'Doe', 'Email': 'john@test.com'},
            {'FirstName': 'Jane', 'LastName': 'Smith', 'Email': 'jane@test.com'}
        ])
        
        vision_employees = pd.DataFrame([
            {'name': 'John Doe', 'email': 'john@test.com'},
            {'FirstName': 'Bob', 'LastName': 'Wilson', 'Email': 'bob@test.com'}
        ])
        
        result = project_mapper_enhanced.analyze_missing_employees(elapseit_people, vision_employees)
        
        assert 'missing_in_vision' in result
        assert 'missing_in_elapseit' in result
        
        # Jane Smith should be missing in Vision
        assert len(result['missing_in_vision']) == 1
        assert result['missing_in_vision'].iloc[0]['FirstName'] == 'Jane'
        
        # Bob Wilson should be missing in ElapseIT
        assert len(result['missing_in_elapseit']) == 1
        assert result['missing_in_elapseit'].iloc[0]['FirstName'] == 'Bob'
    
    def test_analyze_missing_clients(self):
        """Test missing clients analysis"""
        elapseit_clients = pd.DataFrame([
            {'Name': 'Client A', 'Code': 'CLI001'},
            {'Name': 'Client B', 'Code': 'CLI002'}
        ])
        
        vision_clients = pd.DataFrame([
            {'name': 'Client A', 'code': 'CLI001'},
            {'Name': 'Client C', 'Code': 'CLI003'}
        ])
        
        result = project_mapper_enhanced.analyze_missing_clients(elapseit_clients, vision_clients)
        
        assert 'missing_in_vision' in result
        assert 'missing_in_elapseit' in result
        
        # Client B should be missing in Vision
        assert len(result['missing_in_vision']) == 1
        assert result['missing_in_vision'].iloc[0]['Name'] == 'Client B'
        
        # Client C should be missing in ElapseIT
        assert len(result['missing_in_elapseit']) == 1
        assert result['missing_in_elapseit'].iloc[0]['Name'] == 'Client C'
    
    def test_analyze_missing_projects(self):
        """Test missing projects analysis"""
        elapseit_projects = pd.DataFrame([
            {'Name': 'Project A', 'ClientName': 'Client A'},
            {'Name': 'Project B', 'ClientName': 'Client B'}
        ])
        
        vision_projects = pd.DataFrame([
            {'name': 'Project A', 'client_name': 'Client A'},
            {'Name': 'Project C', 'ClientName': 'Client C'}
        ])
        
        result = project_mapper_enhanced.analyze_missing_projects(elapseit_projects, vision_projects)
        
        assert 'missing_in_vision' in result
        assert 'missing_in_elapseit' in result
        
        # Project B should be missing in Vision
        assert len(result['missing_in_vision']) == 1
        assert result['missing_in_vision'].iloc[0]['Name'] == 'Project B'
        
        # Project C should be missing in ElapseIT
        assert len(result['missing_in_elapseit']) == 1
        assert result['missing_in_elapseit'].iloc[0]['Name'] == 'Project C'
    
    def test_create_combined_allocations(self):
        """Test combined allocations creation"""
        elapseit_allocations = pd.DataFrame([
            {'Person': 'John Doe', 'Client': 'Client A', 'Project': 'Project 1', 'Hours': 8.0}
        ])
        
        vision_allocations = pd.DataFrame([
            {'employee': 'John Doe', 'client': 'Client A', 'project': 'Project 1', 'hours': 8.0}
        ])
        
        result = project_mapper_enhanced.create_combined_allocations(elapseit_allocations, vision_allocations)
        
        assert result is not None
        assert len(result) == 2  # One from each system
        assert 'System' in result.columns
        assert 'ElapseIT' in result['System'].values
        assert 'Vision' in result['System'].values
    
    def test_export_to_excel(self, temp_dir):
        """Test Excel export functionality"""
        # Create test data
        analysis_results = {
            'matches': pd.DataFrame([{'Person': 'John Doe', 'Client': 'Client A'}]),
            'elapseit_no_matches': pd.DataFrame([{'Person': 'Jane Smith', 'Client': 'Client B'}]),
            'vision_no_matches': pd.DataFrame([{'employee': 'Bob Wilson', 'client': 'Client C'}]),
            'missing_employees': {
                'missing_in_vision': pd.DataFrame([{'FirstName': 'Jane', 'LastName': 'Smith'}]),
                'missing_in_elapseit': pd.DataFrame([{'FirstName': 'Bob', 'LastName': 'Wilson'}])
            },
            'missing_clients': {
                'missing_in_vision': pd.DataFrame([{'Name': 'Client B'}]),
                'missing_in_elapseit': pd.DataFrame([{'Name': 'Client C'}])
            },
            'missing_projects': {
                'missing_in_vision': pd.DataFrame([{'Name': 'Project B'}]),
                'missing_in_elapseit': pd.DataFrame([{'Name': 'Project C'}])
            },
            'combined_allocations': pd.DataFrame([{'Person': 'John Doe', 'System': 'ElapseIT'}])
        }
        
        output_file = os.path.join(temp_dir, 'test_analysis.xlsx')
        
        result = project_mapper_enhanced.export_to_excel(analysis_results, output_file, 'August 2025')
        
        assert result is True
        assert os.path.exists(output_file)
        
        # Verify Excel file contents
        with pd.ExcelFile(output_file) as xls:
            expected_sheets = [
                'bidirectional_matches',
                'elapseit_no_matches',
                'vision_no_matches',
                'missing_employees_vision',
                'missing_employees_elapseit',
                'missing_clients_vision',
                'missing_clients_elapseit',
                'missing_projects_vision',
                'missing_projects_elapseit',
                'combined_allocations'
            ]
            
            for sheet in expected_sheets:
                assert sheet in xls.sheet_names
    
    def test_export_to_excel_failure(self):
        """Test Excel export failure"""
        analysis_results = {
            'matches': pd.DataFrame(),
            'elapseit_no_matches': pd.DataFrame(),
            'vision_no_matches': pd.DataFrame(),
            'missing_employees': {'missing_in_vision': pd.DataFrame(), 'missing_in_elapseit': pd.DataFrame()},
            'missing_clients': {'missing_in_vision': pd.DataFrame(), 'missing_in_elapseit': pd.DataFrame()},
            'missing_projects': {'missing_in_vision': pd.DataFrame(), 'missing_in_elapseit': pd.DataFrame()},
            'combined_allocations': pd.DataFrame()
        }
        
        # Use invalid path to cause failure
        result = project_mapper_enhanced.export_to_excel(analysis_results, '/invalid/path/test.xlsx', 'August 2025')
        
        assert result is False
    
    @patch('project_mapper_enhanced.get_elapseit_data_from_api')
    @patch('project_mapper_enhanced.get_vision_data_from_db')
    @patch('project_mapper_enhanced.perform_bidirectional_matching')
    @patch('project_mapper_enhanced.analyze_missing_employees')
    @patch('project_mapper_enhanced.analyze_missing_clients')
    @patch('project_mapper_enhanced.analyze_missing_projects')
    @patch('project_mapper_enhanced.create_combined_allocations')
    @patch('project_mapper_enhanced.export_to_excel')
    def test_main_analysis_workflow_success(self, mock_export, mock_combined, mock_projects, 
                                          mock_clients, mock_employees, mock_matching, 
                                          mock_vision, mock_elapseit):
        """Test successful main analysis workflow"""
        # Mock all dependencies
        mock_elapseit.return_value = {
            'clients': pd.DataFrame([{'Name': 'Client A'}]),
            'people': pd.DataFrame([{'FirstName': 'John'}]),
            'projects': pd.DataFrame([{'Name': 'Project A'}]),
            'allocations': pd.DataFrame([{'Person': 'John Doe'}])
        }
        
        mock_vision.return_value = {
            'clients': pd.DataFrame([{'name': 'Client A'}]),
            'employees': pd.DataFrame([{'name': 'John Doe'}]),
            'projects': pd.DataFrame([{'name': 'Project A'}]),
            'allocations': pd.DataFrame([{'employee': 'John Doe'}])
        }
        
        mock_matching.return_value = {
            'matches': pd.DataFrame([{'Person': 'John Doe'}]),
            'elapseit_no_matches': pd.DataFrame(),
            'vision_no_matches': pd.DataFrame()
        }
        
        mock_employees.return_value = {
            'missing_in_vision': pd.DataFrame(),
            'missing_in_elapseit': pd.DataFrame()
        }
        
        mock_clients.return_value = {
            'missing_in_vision': pd.DataFrame(),
            'missing_in_elapseit': pd.DataFrame()
        }
        
        mock_projects.return_value = {
            'missing_in_vision': pd.DataFrame(),
            'missing_in_elapseit': pd.DataFrame()
        }
        
        mock_combined.return_value = pd.DataFrame([{'Person': 'John Doe'}])
        mock_export.return_value = True
        
        # Test the main workflow
        result = project_mapper_enhanced.main_analysis_workflow('August 2025', use_api=True)
        
        assert result is True
        
        # Verify all functions were called
        mock_elapseit.assert_called_once()
        mock_vision.assert_called_once()
        mock_matching.assert_called_once()
        mock_employees.assert_called_once()
        mock_clients.assert_called_once()
        mock_projects.assert_called_once()
        mock_combined.assert_called_once()
        mock_export.assert_called_once()
    
    @patch('project_mapper_enhanced.get_elapseit_data_from_api')
    def test_main_analysis_workflow_elapseit_failure(self, mock_elapseit):
        """Test main analysis workflow with ElapseIT data failure"""
        mock_elapseit.return_value = None
        
        result = project_mapper_enhanced.main_analysis_workflow('August 2025', use_api=True)
        
        assert result is False
    
    @patch('project_mapper_enhanced.get_elapseit_data_from_api')
    @patch('project_mapper_enhanced.get_vision_data_from_db')
    def test_main_analysis_workflow_vision_failure(self, mock_vision, mock_elapseit):
        """Test main analysis workflow with Vision data failure"""
        mock_elapseit.return_value = {
            'clients': pd.DataFrame([{'Name': 'Client A'}]),
            'people': pd.DataFrame([{'FirstName': 'John'}]),
            'projects': pd.DataFrame([{'Name': 'Project A'}]),
            'allocations': pd.DataFrame([{'Person': 'John Doe'}])
        }
        mock_vision.return_value = None
        
        result = project_mapper_enhanced.main_analysis_workflow('August 2025', use_api=True)
        
        assert result is False
