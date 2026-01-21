"""
Unit tests for ElapseIT Data Transformer
"""

import pytest
import pandas as pd
from datetime import datetime
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from data_transformer import ElapseITDataTransformer


class TestElapseITDataTransformer:
    """Test cases for ElapseIT Data Transformer"""
    
    def test_init(self):
        """Test transformer initialization"""
        transformer = ElapseITDataTransformer()
        
        assert transformer.date_format_map['api'] == '%Y-%m-%dT%H:%M:%SZ'
        assert transformer.date_format_map['file'] == '%Y-%b-%d'
        assert 'clients' in transformer.field_mappings
        assert 'people' in transformer.field_mappings
        assert 'projects' in transformer.field_mappings
        assert 'allocations' in transformer.field_mappings
    
    def test_parse_date_api_format(self):
        """Test API date parsing"""
        transformer = ElapseITDataTransformer()
        
        # Test valid API date
        result = transformer.parse_date('2023-01-01T00:00:00Z')
        assert result == '2023-Jan-01'
        
        # Test invalid date
        result = transformer.parse_date('invalid-date')
        assert result == 'invalid-date'
        
        # Test None
        result = transformer.parse_date(None)
        assert result is None
    
    def test_parse_date_file_format(self):
        """Test file date parsing"""
        transformer = ElapseITDataTransformer()
        
        # Test valid file date
        result = transformer.parse_date('2023-Jan-01')
        assert result == '2023-Jan-01'
        
        # Test with different format
        transformer.date_format_map['file'] = '%Y-%m-%d'
        result = transformer.parse_date('2023-01-01')
        assert result == '2023-01-01'
    
    def test_transform_clients(self):
        """Test client data transformation"""
        transformer = ElapseITDataTransformer()
        
        api_data = [
            {
                'ID': 1,
                'Code': 'CLI001',
                'Name': 'Test Client',
                'Address': '123 Test St',
                'City': 'Test City',
                'State': 'Test State',
                'Zipcode': '12345',
                'Country': 'Test Country',
                'IsArchived': False,
                'ArchivedDate': None,
                'VatNumber': 'VAT123',
                'RegistrationNumber': 'REG123',
                'OtherLegalDetails': 'Legal details',
                'BankName': 'Test Bank',
                'AccountNumber': 'ACC123',
                'OtherBankDetails': 'Bank details',
                'InvoiceDueDateDays': 30
            }
        ]
        
        result = transformer.transform_clients(api_data)
        
        assert result is not None
        assert len(result) == 1
        assert result[0]['ID'] == 1
        assert result[0]['Code'] == 'CLI001'
        assert result[0]['Name'] == 'Test Client'
        assert result[0]['IsArchived'] == False
        assert result[0]['ArchivedDate'] is None
    
    def test_transform_clients_empty(self):
        """Test client transformation with empty data"""
        transformer = ElapseITDataTransformer()
        
        result = transformer.transform_clients([])
        
        assert result == []
    
    def test_transform_people(self):
        """Test people data transformation"""
        transformer = ElapseITDataTransformer()
        
        api_data = [
            {
                'ID': 1,
                'FirstName': 'John',
                'LastName': 'Doe',
                'Email': 'john.doe@test.com',
                'IsContractor': False,
                'MobilePhone': '+1234567890',
                'OfficePhone': '+0987654321',
                'Address': '456 Employee St',
                'City': 'Employee City',
                'State': 'Employee State',
                'Zipcode': '54321',
                'Country': 'Employee Country',
                'IsArchived': False,
                'ArchivedDate': None,
                'EmployeeNumber': 'EMP001',
                'Department': 'IT',
                'Position': 'Developer',
                'ManagerID': None,
                'HireDate': '2023-01-01T00:00:00Z',
                'TerminationDate': None,
                'Salary': 50000,
                'Currency': 'USD',
                'TimeZone': 'America/New_York',
                'Language': 'en',
                'Culture': 'en-US',
                'DateFormat': 'MM/dd/yyyy',
                'TimeFormat': '12h',
                'WeekStartDay': 1,
                'IsActive': True,
                'LastLoginDate': '2024-01-01T00:00:00Z',
                'CreatedDate': '2023-01-01T00:00:00Z',
                'UpdatedDate': '2024-01-01T00:00:00Z'
            }
        ]
        
        result = transformer.transform_people(api_data)
        
        assert result is not None
        assert len(result) == 1
        assert result[0]['ID'] == 1
        assert result[0]['FirstName'] == 'John'
        assert result[0]['LastName'] == 'Doe'
        assert result[0]['Email'] == 'john.doe@test.com'
        assert result[0]['IsContractor'] == False
        assert result[0]['IsActive'] == True
    
    def test_transform_projects(self):
        """Test project data transformation"""
        transformer = ElapseITDataTransformer()
        
        api_data = [
            {
                'ID': 1,
                'Code': 'PROJ001',
                'Name': 'Test Project',
                'Description': 'Test project description',
                'ClientID': 1,
                'ClientName': 'Test Client',
                'ProjectManagerID': 1,
                'ProjectManagerName': 'John Doe',
                'StartDate': '2023-01-01T00:00:00Z',
                'EndDate': '2023-12-31T00:00:00Z',
                'Budget': 100000,
                'Currency': 'USD',
                'Status': 'Active',
                'Priority': 'High',
                'IsArchived': False,
                'ArchivedDate': None,
                'CreatedDate': '2023-01-01T00:00:00Z',
                'UpdatedDate': '2024-01-01T00:00:00Z'
            }
        ]
        
        result = transformer.transform_projects(api_data)
        
        assert result is not None
        assert len(result) == 1
        assert result[0]['ID'] == 1
        assert result[0]['Code'] == 'PROJ001'
        assert result[0]['Name'] == 'Test Project'
        assert result[0]['ClientID'] == 1
        assert result[0]['Status'] == 'Active'
        assert result[0]['IsArchived'] == False
    
    def test_transform_allocations(self):
        """Test allocation data transformation"""
        transformer = ElapseITDataTransformer()
        
        api_data = [
            {
                'ID': 1,
                'ProjectID': 1,
                'ProjectName': 'Test Project',
                'ClientID': 1,
                'ClientName': 'Test Client',
                'PersonID': 1,
                'PersonName': 'John Doe',
                'StartDate': '2023-01-01T00:00:00Z',
                'EndDate': '2023-12-31T00:00:00Z',
                'AllocationPercent': 100,
                'Rate': 100,
                'RateType': 'hourly',
                'Role': 'Developer',
                'IsActive': True,
                'CreatedDate': '2023-01-01T00:00:00Z',
                'UpdatedDate': '2024-01-01T00:00:00Z'
            }
        ]
        
        result = transformer.transform_allocations(api_data)
        
        assert result is not None
        assert len(result) == 1
        assert result[0]['ID'] == 1
        assert result[0]['ProjectID'] == 1
        assert result[0]['PersonID'] == 1
        assert result[0]['AllocationPercent'] == 100
        assert result[0]['Rate'] == 100
        assert result[0]['RateType'] == 'hourly'
        assert result[0]['IsActive'] == True
    
    def test_transform_all_data(self):
        """Test complete data transformation"""
        transformer = ElapseITDataTransformer()
        
        api_data = {
            'clients': [
                {
                    'ID': 1,
                    'Code': 'CLI001',
                    'Name': 'Test Client',
                    'IsArchived': False,
                    'ArchivedDate': None,
                    'VatNumber': 'VAT123',
                    'RegistrationNumber': 'REG123',
                    'OtherLegalDetails': 'Legal details',
                    'BankName': 'Test Bank',
                    'AccountNumber': 'ACC123',
                    'OtherBankDetails': 'Bank details',
                    'InvoiceDueDateDays': 30,
                    'Address': '123 Test St',
                    'City': 'Test City',
                    'State': 'Test State',
                    'Zipcode': '12345',
                    'Country': 'Test Country'
                }
            ],
            'people': [
                {
                    'ID': 1,
                    'FirstName': 'John',
                    'LastName': 'Doe',
                    'Email': 'john.doe@test.com',
                    'IsContractor': False,
                    'IsArchived': False,
                    'ArchivedDate': None,
                    'EmployeeNumber': 'EMP001',
                    'Department': 'IT',
                    'Position': 'Developer',
                    'ManagerID': None,
                    'HireDate': '2023-01-01T00:00:00Z',
                    'TerminationDate': None,
                    'Salary': 50000,
                    'Currency': 'USD',
                    'TimeZone': 'America/New_York',
                    'Language': 'en',
                    'Culture': 'en-US',
                    'DateFormat': 'MM/dd/yyyy',
                    'TimeFormat': '12h',
                    'WeekStartDay': 1,
                    'IsActive': True,
                    'LastLoginDate': '2024-01-01T00:00:00Z',
                    'CreatedDate': '2023-01-01T00:00:00Z',
                    'UpdatedDate': '2024-01-01T00:00:00Z',
                    'MobilePhone': '+1234567890',
                    'OfficePhone': '+0987654321',
                    'Address': '456 Employee St',
                    'City': 'Employee City',
                    'State': 'Employee State',
                    'Zipcode': '54321',
                    'Country': 'Employee Country'
                }
            ],
            'projects': [
                {
                    'ID': 1,
                    'Code': 'PROJ001',
                    'Name': 'Test Project',
                    'Description': 'Test project description',
                    'ClientID': 1,
                    'ClientName': 'Test Client',
                    'ProjectManagerID': 1,
                    'ProjectManagerName': 'John Doe',
                    'StartDate': '2023-01-01T00:00:00Z',
                    'EndDate': '2023-12-31T00:00:00Z',
                    'Budget': 100000,
                    'Currency': 'USD',
                    'Status': 'Active',
                    'Priority': 'High',
                    'IsArchived': False,
                    'ArchivedDate': None,
                    'CreatedDate': '2023-01-01T00:00:00Z',
                    'UpdatedDate': '2024-01-01T00:00:00Z'
                }
            ],
            'allocations': [
                {
                    'ID': 1,
                    'ProjectID': 1,
                    'ProjectName': 'Test Project',
                    'ClientID': 1,
                    'ClientName': 'Test Client',
                    'PersonID': 1,
                    'PersonName': 'John Doe',
                    'StartDate': '2023-01-01T00:00:00Z',
                    'EndDate': '2023-12-31T00:00:00Z',
                    'AllocationPercent': 100,
                    'Rate': 100,
                    'RateType': 'hourly',
                    'Role': 'Developer',
                    'IsActive': True,
                    'CreatedDate': '2023-01-01T00:00:00Z',
                    'UpdatedDate': '2024-01-01T00:00:00Z'
                }
            ]
        }
        
        result = transformer.transform_all_data(api_data)
        
        assert result is not None
        assert 'clients' in result
        assert 'people' in result
        assert 'projects' in result
        assert 'allocations' in result
        
        assert len(result['clients']) == 1
        assert len(result['people']) == 1
        assert len(result['projects']) == 1
        assert len(result['allocations']) == 1
        
        assert result['clients'][0]['Name'] == 'Test Client'
        assert result['people'][0]['FirstName'] == 'John'
        assert result['projects'][0]['Name'] == 'Test Project'
        assert result['allocations'][0]['AllocationPercent'] == 100
    
    def test_transform_all_data_empty(self):
        """Test data transformation with empty data"""
        transformer = ElapseITDataTransformer()
        
        api_data = {
            'clients': [],
            'people': [],
            'projects': [],
            'allocations': []
        }
        
        result = transformer.transform_all_data(api_data)
        
        assert result is not None
        assert result['clients'] == []
        assert result['people'] == []
        assert result['projects'] == []
        assert result['allocations'] == []
    
    def test_transform_all_data_partial(self):
        """Test data transformation with partial data"""
        transformer = ElapseITDataTransformer()
        
        api_data = {
            'clients': [
                {
                    'ID': 1,
                    'Code': 'CLI001',
                    'Name': 'Test Client',
                    'IsArchived': False,
                    'ArchivedDate': None,
                    'VatNumber': 'VAT123',
                    'RegistrationNumber': 'REG123',
                    'OtherLegalDetails': 'Legal details',
                    'BankName': 'Test Bank',
                    'AccountNumber': 'ACC123',
                    'OtherBankDetails': 'Bank details',
                    'InvoiceDueDateDays': 30,
                    'Address': '123 Test St',
                    'City': 'Test City',
                    'State': 'Test State',
                    'Zipcode': '12345',
                    'Country': 'Test Country'
                }
            ],
            'people': [],
            'projects': [],
            'allocations': []
        }
        
        result = transformer.transform_all_data(api_data)
        
        assert result is not None
        assert len(result['clients']) == 1
        assert result['people'] == []
        assert result['projects'] == []
        assert result['allocations'] == []
    
    def test_field_mapping_consistency(self):
        """Test that field mappings are consistent"""
        transformer = ElapseITDataTransformer()
        
        # Check that all required fields are mapped
        required_client_fields = [
            'ID', 'Code', 'Name', 'Address', 'City', 'State', 'Zipcode', 
            'Country', 'IsArchived', 'ArchivedDate', 'VatNumber', 
            'RegistrationNumber', 'OtherLegalDetails', 'BankName', 
            'AccountNumber', 'OtherBankDetails', 'InvoiceDueDateDays'
        ]
        
        for field in required_client_fields:
            assert field in transformer.field_mappings['clients']
        
        required_people_fields = [
            'ID', 'FirstName', 'LastName', 'Email', 'IsContractor', 
            'MobilePhone', 'OfficePhone', 'Address', 'City', 'State', 
            'Zipcode', 'Country', 'IsArchived', 'ArchivedDate', 
            'EmployeeNumber', 'Department', 'Position', 'ManagerID', 
            'HireDate', 'TerminationDate', 'Salary', 'Currency', 
            'TimeZone', 'Language', 'Culture', 'DateFormat', 'TimeFormat', 
            'WeekStartDay', 'IsActive', 'LastLoginDate', 'CreatedDate', 'UpdatedDate'
        ]
        
        for field in required_people_fields:
            assert field in transformer.field_mappings['people']
    
    def test_date_parsing_edge_cases(self):
        """Test date parsing with edge cases"""
        transformer = ElapseITDataTransformer()
        
        # Test empty string
        result = transformer.parse_date('')
        assert result == ''
        
        # Test malformed date
        result = transformer.parse_date('2023-13-45T25:70:80Z')
        assert result == '2023-13-45T25:70:80Z'
        
        # Test different timezone format
        result = transformer.parse_date('2023-01-01T00:00:00+00:00')
        assert result == '2023-Jan-01'
