"""
Unit tests for Xero Reports Extractor
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

# Import the main module
import get_xero_reports


class TestGetXeroReports:
    """Test cases for Xero Reports Extractor"""
    
    def test_parse_date_string_valid_formats(self):
        """Test date parsing with valid formats"""
        # Test various valid date formats
        test_cases = [
            ("June 2025", date(2025, 6, 30)),
            ("2025-06-30", date(2025, 6, 30)),
            ("31 December 2024", date(2024, 12, 31)),
            ("2024-12-31", date(2024, 12, 31)),
            ("January 2024", date(2024, 1, 31)),
            ("Feb 2024", date(2024, 2, 29)),  # Leap year
        ]
        
        for date_str, expected in test_cases:
            result = get_xero_reports.parse_date_string(date_string=date_str)
            assert result == expected, f"Failed for input: {date_str}"
    
    def test_parse_date_string_invalid_formats(self):
        """Test date parsing with invalid formats"""
        invalid_cases = [
            "invalid-date",
            "13th month 2024",
            "32 January 2024",
            "not a date",
            ""
        ]
        
        for date_str in invalid_cases:
            with pytest.raises(ValueError):
                get_xero_reports.parse_date_string(date_string=date_str)
    
    def test_parse_date_string_none(self):
        """Test date parsing with None input"""
        result = get_xero_reports.parse_date_string(date_string=None)
        assert result == date.today()
    
    def test_get_financial_year_end(self):
        """Test financial year end calculation"""
        # Test with February end
        result = get_xero_reports.get_financial_year_end(date(2025, 6, 30), 2)
        assert result == "FEB26"
        
        # Test with December end
        result = get_xero_reports.get_financial_year_end(date(2024, 12, 31), 12)
        assert result == "DEC24"
        
        # Test with March end
        result = get_xero_reports.get_financial_year_end(date(2024, 3, 31), 3)
        assert result == "MAR24"
    
    def test_get_company_code(self):
        """Test company code mapping"""
        # Test known company mappings
        assert get_xero_reports.get_company_code("Elenjical Solutions (Pty) Ltd") == "SA"
        assert get_xero_reports.get_company_code("Elenjical Solutions MA (USD)") == "MA"
        assert get_xero_reports.get_company_code("Elenjical Solutions Private Limited") == "IND"
        assert get_xero_reports.get_company_code("Elenjical Solutions International Limited") == "UK"
        
        # Test unknown company
        assert get_xero_reports.get_company_code("Unknown Company") == "UNK"
    
    @patch('xero_api_client.XeroAPIClient')
    def test_get_organizations_success(self, mock_client_class):
        """Test successful organizations retrieval"""
        mock_client = Mock()
        mock_client.get_organizations.return_value = [
            {
                'OrganisationID': 'test-org-id',
                'Name': 'Test Organization',
                'LegalName': 'Test Organization Ltd',
                'CountryCode': 'US',
                'BaseCurrency': 'USD'
            }
        ]
        mock_client_class.return_value = mock_client
        
        result = get_xero_reports.get_organizations()
        
        assert result is not None
        assert len(result) == 1
        assert result[0]['Name'] == 'Test Organization'
        mock_client.get_organizations.assert_called_once()
    
    @patch('xero_api_client.XeroAPIClient')
    def test_get_organizations_failure(self, mock_client_class):
        """Test organizations retrieval failure"""
        mock_client = Mock()
        mock_client.get_organizations.return_value = None
        mock_client_class.return_value = mock_client
        
        result = get_xero_reports.get_organizations()
        
        assert result is None
    
    @patch('xero_api_client.XeroAPIClient')
    def test_get_accounts_success(self, mock_client_class):
        """Test successful accounts retrieval"""
        mock_client = Mock()
        mock_client.get_accounts.return_value = [
            {
                'AccountID': 'test-account-id',
                'Code': '1000',
                'Name': 'Test Bank Account',
                'Type': 'BANK',
                'Status': 'ACTIVE'
            }
        ]
        mock_client_class.return_value = mock_client
        
        result = get_xero_reports.get_accounts('test-tenant-id')
        
        assert result is not None
        assert len(result) == 1
        assert result[0]['Name'] == 'Test Bank Account'
        mock_client.get_accounts.assert_called_once()
    
    @patch('xero_api_client.XeroAPIClient')
    def test_get_balance_sheet_success(self, mock_client_class):
        """Test successful balance sheet retrieval"""
        mock_client = Mock()
        mock_client.get_balance_sheet.return_value = [
            {
                'ReportName': 'BalanceSheet',
                'ReportDate': '2023-12-31',
                'Rows': [
                    {'RowType': 'Header', 'Cells': [{'Value': 'Account'}, {'Value': 'Amount'}]},
                    {'RowType': 'Section', 'Cells': [{'Value': 'Assets'}, {'Value': '100000'}]}
                ]
            }
        ]
        mock_client_class.return_value = mock_client
        
        result = get_xero_reports.get_balance_sheet('test-tenant-id', '2023-12-31')
        
        assert result is not None
        assert len(result) == 1
        assert result[0]['ReportName'] == 'BalanceSheet'
        mock_client.get_balance_sheet.assert_called_once_with('2023-12-31')
    
    @patch('xero_api_client.XeroAPIClient')
    def test_get_profit_loss_success(self, mock_client_class):
        """Test successful profit and loss retrieval"""
        mock_client = Mock()
        mock_client.get_profit_loss.return_value = [
            {
                'ReportName': 'ProfitAndLoss',
                'ReportDate': '2023-12-31',
                'Rows': [
                    {'RowType': 'Header', 'Cells': [{'Value': 'Account'}, {'Value': 'Amount'}]},
                    {'RowType': 'Section', 'Cells': [{'Value': 'Revenue'}, {'Value': '50000'}]}
                ]
            }
        ]
        mock_client_class.return_value = mock_client
        
        result = get_xero_reports.get_profit_loss('test-tenant-id', '2023-01-01', '2023-12-31')
        
        assert result is not None
        assert len(result) == 1
        assert result[0]['ReportName'] == 'ProfitAndLoss'
        mock_client.get_profit_loss.assert_called_once_with('2023-01-01', '2023-12-31')
    
    @patch('xero_api_client.XeroAPIClient')
    def test_get_trial_balance_success(self, mock_client_class):
        """Test successful trial balance retrieval"""
        mock_client = Mock()
        mock_client.get_trial_balance.return_value = [
            {
                'ReportName': 'TrialBalance',
                'ReportDate': '2023-12-31',
                'Rows': [
                    {'RowType': 'Header', 'Cells': [{'Value': 'Account'}, {'Value': 'Debit'}, {'Value': 'Credit'}]}
                ]
            }
        ]
        mock_client_class.return_value = mock_client
        
        result = get_xero_reports.get_trial_balance('test-tenant-id', '2023-12-31')
        
        assert result is not None
        assert len(result) == 1
        assert result[0]['ReportName'] == 'TrialBalance'
        mock_client.get_trial_balance.assert_called_once_with('2023-12-31')
    
    @patch('xero_api_client.XeroAPIClient')
    def test_get_invoices_success(self, mock_client_class):
        """Test successful invoices retrieval"""
        mock_client = Mock()
        mock_client.get_invoices.return_value = [
            {
                'InvoiceID': 'test-invoice-id',
                'InvoiceNumber': 'INV-001',
                'Type': 'ACCREC',
                'Status': 'AUTHORISED',
                'Total': 1000.0,
                'ContactName': 'Test Customer'
            }
        ]
        mock_client_class.return_value = mock_client
        
        result = get_xero_reports.get_invoices('test-tenant-id')
        
        assert result is not None
        assert len(result) == 1
        assert result[0]['InvoiceNumber'] == 'INV-001'
        mock_client.get_invoices.assert_called_once()
    
    def test_convert_report_to_dataframe(self):
        """Test report conversion to DataFrame"""
        mock_report = {
            'ReportName': 'TestReport',
            'ReportDate': '2023-12-31',
            'Rows': [
                {'RowType': 'Header', 'Cells': [{'Value': 'Account'}, {'Value': 'Amount'}]},
                {'RowType': 'Section', 'Cells': [{'Value': 'Assets'}, {'Value': '100000'}]},
                {'RowType': 'SummaryRow', 'Cells': [{'Value': 'Total Assets'}, {'Value': '100000'}]}
            ]
        }
        
        result = get_xero_reports.convert_report_to_dataframe(mock_report)
        
        assert result is not None
        assert len(result) == 2  # Header row excluded
        assert result.iloc[0]['Account'] == 'Assets'
        assert result.iloc[0]['Amount'] == '100000'
    
    def test_convert_report_to_dataframe_empty(self):
        """Test report conversion with empty report"""
        mock_report = {
            'ReportName': 'TestReport',
            'ReportDate': '2023-12-31',
            'Rows': []
        }
        
        result = get_xero_reports.convert_report_to_dataframe(mock_report)
        
        assert result is not None
        assert len(result) == 0
    
    def test_save_report_to_excel(self, temp_dir):
        """Test saving report to Excel"""
        # Create test data
        report_data = pd.DataFrame([
            {'Account': 'Assets', 'Amount': '100000'},
            {'Account': 'Liabilities', 'Amount': '50000'}
        ])
        
        output_file = os.path.join(temp_dir, 'test_report.xlsx')
        
        result = get_xero_reports.save_report_to_excel(report_data, output_file, 'Test Report', '2023-12-31')
        
        assert result is True
        assert os.path.exists(output_file)
        
        # Verify Excel file contents
        with pd.ExcelFile(output_file) as xls:
            assert 'Test Report' in xls.sheet_names
            df = pd.read_excel(xls, 'Test Report')
            assert len(df) == 2
            assert df.iloc[0]['Account'] == 'Assets'
    
    def test_save_report_to_excel_failure(self):
        """Test saving report to Excel with failure"""
        report_data = pd.DataFrame([{'Account': 'Assets', 'Amount': '100000'}])
        
        # Use invalid path to cause failure
        result = get_xero_reports.save_report_to_excel(report_data, '/invalid/path/test.xlsx', 'Test Report', '2023-12-31')
        
        assert result is False
    
    @patch('fx_reader.FXRateReader')
    def test_apply_fx_rates_success(self, mock_fx_class):
        """Test successful FX rate application"""
        mock_fx = Mock()
        mock_fx.get_fx_rate.return_value = 18.5
        mock_fx_class.return_value = mock_fx
        
        # Create test data with different currencies
        report_data = pd.DataFrame([
            {'Account': 'Bank USD', 'Amount': '1000', 'Currency': 'USD'},
            {'Account': 'Bank ZAR', 'Amount': '18500', 'Currency': 'ZAR'},
            {'Account': 'Bank GBP', 'Amount': '500', 'Currency': 'GBP'}
        ])
        
        result = get_xero_reports.apply_fx_rates(report_data, 'ZAR')
        
        assert result is not None
        assert 'Amount_ZAR' in result.columns
        assert 'FX_Rate' in result.columns
        
        # Check that FX rates were applied
        usd_row = result[result['Currency'] == 'USD'].iloc[0]
        assert usd_row['Amount_ZAR'] == 18500  # 1000 * 18.5
        assert usd_row['FX_Rate'] == 18.5
        
        # ZAR should remain unchanged
        zar_row = result[result['Currency'] == 'ZAR'].iloc[0]
        assert zar_row['Amount_ZAR'] == 18500
        assert zar_row['FX_Rate'] == 1.0
    
    @patch('fx_reader.FXRateReader')
    def test_apply_fx_rates_no_fx_data(self, mock_fx_class):
        """Test FX rate application when no FX data available"""
        mock_fx = Mock()
        mock_fx.get_fx_rate.return_value = None
        mock_fx_class.return_value = mock_fx
        
        report_data = pd.DataFrame([
            {'Account': 'Bank USD', 'Amount': '1000', 'Currency': 'USD'}
        ])
        
        result = get_xero_reports.apply_fx_rates(report_data, 'ZAR')
        
        assert result is not None
        assert 'Amount_ZAR' in result.columns
        assert 'FX_Rate' in result.columns
        
        # Should have original amount when FX rate not available
        usd_row = result[result['Currency'] == 'USD'].iloc[0]
        assert usd_row['Amount_ZAR'] == 1000
        assert pd.isna(usd_row['FX_Rate'])
    
    @patch('get_xero_reports.get_organizations')
    @patch('get_xero_reports.get_accounts')
    @patch('get_xero_reports.get_balance_sheet')
    @patch('get_xero_reports.get_profit_loss')
    @patch('get_xero_reports.get_trial_balance')
    @patch('get_xero_reports.get_invoices')
    @patch('get_xero_reports.convert_report_to_dataframe')
    @patch('get_xero_reports.apply_fx_rates')
    @patch('get_xero_reports.save_report_to_excel')
    def test_extract_all_reports_success(self, mock_save, mock_fx, mock_convert, 
                                       mock_invoices, mock_trial, mock_pl, mock_bs, 
                                       mock_accounts, mock_orgs):
        """Test successful extraction of all reports"""
        # Mock all dependencies
        mock_orgs.return_value = [
            {'OrganisationID': 'test-org-id', 'Name': 'Test Organization', 'BaseCurrency': 'USD'}
        ]
        mock_accounts.return_value = [{'AccountID': 'test-account', 'Name': 'Test Account'}]
        mock_bs.return_value = [{'ReportName': 'BalanceSheet', 'ReportDate': '2023-12-31', 'Rows': []}]
        mock_pl.return_value = [{'ReportName': 'ProfitAndLoss', 'ReportDate': '2023-12-31', 'Rows': []}]
        mock_trial.return_value = [{'ReportName': 'TrialBalance', 'ReportDate': '2023-12-31', 'Rows': []}]
        mock_invoices.return_value = [{'InvoiceID': 'test-invoice', 'InvoiceNumber': 'INV-001'}]
        
        mock_convert.return_value = pd.DataFrame([{'Account': 'Test', 'Amount': '1000'}])
        mock_fx.return_value = pd.DataFrame([{'Account': 'Test', 'Amount': '1000', 'Amount_ZAR': '18500'}])
        mock_save.return_value = True
        
        result = get_xero_reports.extract_all_reports('2023-12-31')
        
        assert result is True
        
        # Verify all functions were called
        mock_orgs.assert_called_once()
        mock_accounts.assert_called_once()
        mock_bs.assert_called_once()
        mock_pl.assert_called_once()
        mock_trial.assert_called_once()
        mock_invoices.assert_called_once()
        mock_convert.assert_called()
        mock_fx.assert_called()
        mock_save.assert_called()
    
    @patch('get_xero_reports.get_organizations')
    def test_extract_all_reports_no_organizations(self, mock_orgs):
        """Test report extraction when no organizations found"""
        mock_orgs.return_value = None
        
        result = get_xero_reports.extract_all_reports('2023-12-31')
        
        assert result is False
    
    @patch('get_xero_reports.get_organizations')
    def test_extract_all_reports_empty_organizations(self, mock_orgs):
        """Test report extraction when organizations list is empty"""
        mock_orgs.return_value = []
        
        result = get_xero_reports.extract_all_reports('2023-12-31')
        
        assert result is False
    
    def test_main_function_success(self):
        """Test main function with valid date"""
        with patch('get_xero_reports.extract_all_reports', return_value=True) as mock_extract:
            with patch('sys.argv', ['get_xero_reports.py', 'June 2025']):
                result = get_xero_reports.main()
                assert result == 0
                mock_extract.assert_called_once()
    
    def test_main_function_no_date(self):
        """Test main function with no date provided"""
        with patch('get_xero_reports.extract_all_reports', return_value=True) as mock_extract:
            with patch('sys.argv', ['get_xero_reports.py']):
                result = get_xero_reports.main()
                assert result == 0
                mock_extract.assert_called_once()
    
    def test_main_function_invalid_date(self):
        """Test main function with invalid date"""
        with patch('sys.argv', ['get_xero_reports.py', 'invalid-date']):
            result = get_xero_reports.main()
            assert result == 1
    
    def test_main_function_extraction_failure(self):
        """Test main function with extraction failure"""
        with patch('get_xero_reports.extract_all_reports', return_value=False) as mock_extract:
            with patch('sys.argv', ['get_xero_reports.py', 'June 2025']):
                result = get_xero_reports.main()
                assert result == 1
                mock_extract.assert_called_once()
