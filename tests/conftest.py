"""
Pytest configuration and fixtures for Nexa test suite
"""

import pytest
import pandas as pd
import os
import tempfile
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, date
import json

# Test configuration
TEST_CONFIG = {
    'ELAPSEIT_CONFIG': {
        'domain': 'test-domain.com',
        'username': 'test@test.com',
        'password': 'test_password',
        'timezone': 'Europe/London'
    },
    'XERO_CONFIG': {
        'client_id': 'test_client_id',
        'client_secret': 'test_client_secret',
        'access_token': 'test_access_token',
        'refresh_token': 'test_refresh_token',
        'scopes': ['accounting.transactions', 'accounting.reports.read']
    },
    'VISION_DB_CONFIG': {
        'host': 'localhost',
        'port': 5432,
        'database': 'test_db',
        'user': 'test_user',
        'password': 'test_password'
    }
}

@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir

@pytest.fixture
def sample_elapseit_data():
    """Sample ElapseIT API response data"""
    return {
        'clients': [
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
        ],
        'people': [
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

@pytest.fixture
def sample_vision_data():
    """Sample Vision database data"""
    return {
        'allocations': pd.DataFrame([
            {
                'id': 1,
                'simulation_id': 28,
                'original_id': 3302,
                'employee_id': 3842,
                'project_id': 3189,
                'start_date': '2025-03-01',
                'end_date': '2026-01-31',
                'allocation_percent': 100,
                'rate': 0,
                'rate_type': None,
                'role': 'consultant',
                'created_at': '2025-06-24 14:32:40.779113+00',
                'updated_at': '2025-06-24 14:32:40.779115+00',
                'deleted_at': None,
                'promoted_at': None
            }
        ]),
        'clients': pd.DataFrame([
            {
                'id': 1,
                'name': 'Test Client',
                'code': 'CLI001',
                'created_at': '2023-01-01 00:00:00+00',
                'updated_at': '2024-01-01 00:00:00+00'
            }
        ]),
        'employees': pd.DataFrame([
            {
                'id': 1,
                'name': 'John Doe',
                'email': 'john.doe@test.com',
                'created_at': '2023-01-01 00:00:00+00',
                'updated_at': '2024-01-01 00:00:00+00'
            }
        ]),
        'projects': pd.DataFrame([
            {
                'id': 1,
                'name': 'Test Project',
                'client_id': 1,
                'created_at': '2023-01-01 00:00:00+00',
                'updated_at': '2024-01-01 00:00:00+00'
            }
        ])
    }

@pytest.fixture
def sample_xero_data():
    """Sample Xero API response data"""
    return {
        'organizations': [
            {
                'OrganisationID': 'test-org-id',
                'Name': 'Test Organization',
                'LegalName': 'Test Organization Ltd',
                'CountryCode': 'US',
                'BaseCurrency': 'USD',
                'OrganisationStatus': 'ACTIVE',
                'IsDemoCompany': False,
                'OrganisationEntityType': 'COMPANY',
                'RegistrationNumber': 'REG123',
                'TaxNumber': 'TAX123',
                'FinancialYearEndDay': 31,
                'FinancialYearEndMonth': 12,
                'SalesTaxBasis': 'ACCRUALS',
                'SalesTaxPeriod': 'MONTHLY',
                'DefaultSalesTax': 'Sales Tax',
                'DefaultPurchasesTax': 'Purchase Tax',
                'PeriodLockDate': '2023-01-01',
                'EndOfYearLockDate': '2023-12-31',
                'CreatedDateUTC': '2023-01-01T00:00:00Z',
                'Timezone': 'America/New_York',
                'OrganisationType': 'COMPANY',
                'ShortCode': 'TEST',
                'Edition': 'BUSINESS',
                'Class': 'BUSINESS',
                'Addresses': [
                    {
                        'AddressType': 'STREET',
                        'AddressLine1': '123 Test St',
                        'City': 'Test City',
                        'Region': 'Test State',
                        'PostalCode': '12345',
                        'Country': 'United States'
                    }
                ],
                'Phones': [
                    {
                        'PhoneType': 'DEFAULT',
                        'PhoneNumber': '+1234567890',
                        'PhoneAreaCode': '123',
                        'PhoneCountryCode': 'US'
                    }
                ],
                'ExternalLinks': [],
                'PaymentTerms': {},
                'OrganisationStatus': 'ACTIVE'
            }
        ],
        'accounts': [
            {
                'AccountID': 'test-account-id',
                'Code': '1000',
                'Name': 'Test Bank Account',
                'Type': 'BANK',
                'BankAccountNumber': '1234567890',
                'Status': 'ACTIVE',
                'Description': 'Test bank account',
                'BankAccountType': 'BANK',
                'CurrencyCode': 'USD',
                'TaxType': 'NONE',
                'EnablePaymentsToAccount': True,
                'ShowInExpenseClaims': True,
                'Class': 'ASSET',
                'SystemAccount': 'BANKCURRENCYGAIN',
                'ReportingCode': 'BANK',
                'ReportingCodeName': 'Bank',
                'HasAttachments': False
            }
        ]
    }

@pytest.fixture
def sample_fx_data():
    """Sample FX rate data"""
    return pd.DataFrame([
        {
            'Date': '2024-01-01',
            'From_Currency': 'USD',
            'To_Currency': 'ZAR',
            'Rate': 18.5
        },
        {
            'Date': '2024-01-01',
            'From_Currency': 'GBP',
            'To_Currency': 'ZAR',
            'Rate': 23.2
        },
        {
            'Date': '2024-01-01',
            'From_Currency': 'EUR',
            'To_Currency': 'ZAR',
            'Rate': 20.1
        }
    ])

@pytest.fixture
def mock_requests():
    """Mock requests module for API testing"""
    with patch('requests.post') as mock_post, \
         patch('requests.get') as mock_get:
        yield {
            'post': mock_post,
            'get': mock_get
        }

@pytest.fixture
def mock_psycopg2():
    """Mock psycopg2 for database testing"""
    with patch('psycopg2.connect') as mock_connect:
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn
        yield {
            'connect': mock_connect,
            'connection': mock_conn,
            'cursor': mock_cursor
        }

@pytest.fixture
def mock_xero_api():
    """Mock Xero API for testing"""
    with patch('xero_python.api_client.ApiClient') as mock_api_client, \
         patch('xero_python.accounting.AccountingApi') as mock_accounting_api, \
         patch('xero_python.identity.IdentityApi') as mock_identity_api:
        yield {
            'api_client': mock_api_client,
            'accounting_api': mock_accounting_api,
            'identity_api': mock_identity_api
        }
