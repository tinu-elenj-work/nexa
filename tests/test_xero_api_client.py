"""
Unit tests for Xero API Client
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from xero_api_client import XeroAPIClient


class TestXeroAPIClient:
    """Test cases for Xero API Client"""
    
    def test_init(self):
        """Test client initialization"""
        client = XeroAPIClient(
            client_id='test_client_id',
            client_secret='test_client_secret',
            access_token='test_access_token',
            refresh_token='test_refresh_token'
        )
        
        assert client.client_id == 'test_client_id'
        assert client.client_secret == 'test_client_secret'
        assert client.access_token == 'test_access_token'
        assert client.refresh_token == 'test_refresh_token'
        assert client.tenant_id is None
    
    @patch('xero_python.api_client.ApiClient')
    def test_get_api_client(self, mock_api_client_class):
        """Test API client creation"""
        mock_api_client = Mock()
        mock_api_client_class.return_value = mock_api_client
        
        client = XeroAPIClient(
            client_id='test_client_id',
            client_secret='test_client_secret'
        )
        
        result = client.get_api_client()
        
        assert result == mock_api_client
        mock_api_client_class.assert_called_once()
    
    @patch('xero_python.identity.IdentityApi')
    @patch('xero_python.api_client.ApiClient')
    def test_get_organizations_success(self, mock_api_client_class, mock_identity_api_class):
        """Test successful organizations retrieval"""
        # Mock API client
        mock_api_client = Mock()
        mock_api_client_class.return_value = mock_api_client
        
        # Mock identity API
        mock_identity_api = Mock()
        mock_identity_api_class.return_value = mock_identity_api
        
        # Mock response
        mock_response = Mock()
        mock_response.organizations = [
            Mock(
                organisation_id='test-org-id',
                name='Test Organization',
                legal_name='Test Organization Ltd',
                country_code='US',
                base_currency='USD'
            )
        ]
        mock_identity_api.get_connections.return_value = mock_response
        
        client = XeroAPIClient(
            client_id='test_client_id',
            client_secret='test_client_secret',
            access_token='test_access_token'
        )
        
        result = client.get_organizations()
        
        assert result is not None
        assert len(result) == 1
        assert result[0]['OrganisationID'] == 'test-org-id'
        assert result[0]['Name'] == 'Test Organization'
    
    @patch('xero_python.identity.IdentityApi')
    @patch('xero_python.api_client.ApiClient')
    def test_get_organizations_exception(self, mock_api_client_class, mock_identity_api_class):
        """Test organizations retrieval with exception"""
        # Mock API client
        mock_api_client = Mock()
        mock_api_client_class.return_value = mock_api_client
        
        # Mock identity API
        mock_identity_api = Mock()
        mock_identity_api_class.return_value = mock_identity_api
        mock_identity_api.get_connections.side_effect = Exception("API Error")
        
        client = XeroAPIClient(
            client_id='test_client_id',
            client_secret='test_client_secret',
            access_token='test_access_token'
        )
        
        result = client.get_organizations()
        
        assert result is None
    
    @patch('xero_python.accounting.AccountingApi')
    @patch('xero_python.api_client.ApiClient')
    def test_get_accounts_success(self, mock_api_client_class, mock_accounting_api_class):
        """Test successful accounts retrieval"""
        # Mock API client
        mock_api_client = Mock()
        mock_api_client_class.return_value = mock_api_client
        
        # Mock accounting API
        mock_accounting_api = Mock()
        mock_accounting_api_class.return_value = mock_accounting_api
        
        # Mock response
        mock_response = Mock()
        mock_response.accounts = [
            Mock(
                account_id='test-account-id',
                code='1000',
                name='Test Bank Account',
                type='BANK',
                status='ACTIVE'
            )
        ]
        mock_accounting_api.get_accounts.return_value = mock_response
        
        client = XeroAPIClient(
            client_id='test_client_id',
            client_secret='test_client_secret',
            access_token='test_access_token',
            tenant_id='test-tenant-id'
        )
        
        result = client.get_accounts()
        
        assert result is not None
        assert len(result) == 1
        assert result[0]['AccountID'] == 'test-account-id'
        assert result[0]['Name'] == 'Test Bank Account'
    
    @patch('xero_python.accounting.AccountingApi')
    @patch('xero_python.api_client.ApiClient')
    def test_get_balance_sheet_success(self, mock_api_client_class, mock_accounting_api_class):
        """Test successful balance sheet retrieval"""
        # Mock API client
        mock_api_client = Mock()
        mock_api_client_class.return_value = mock_api_client
        
        # Mock accounting API
        mock_accounting_api = Mock()
        mock_accounting_api_class.return_value = mock_accounting_api
        
        # Mock response
        mock_response = Mock()
        mock_response.reports = [
            Mock(
                report_id='test-report-id',
                report_name='BalanceSheet',
                report_date='2023-12-31',
                rows=[
                    Mock(
                        row_type='Header',
                        cells=[
                            Mock(value='Account'),
                            Mock(value='Amount')
                        ]
                    ),
                    Mock(
                        row_type='Section',
                        cells=[
                            Mock(value='Assets'),
                            Mock(value='100000')
                        ]
                    )
                ]
            )
        ]
        mock_accounting_api.get_report_balance_sheet.return_value = mock_response
        
        client = XeroAPIClient(
            client_id='test_client_id',
            client_secret='test_client_secret',
            access_token='test_access_token',
            tenant_id='test-tenant-id'
        )
        
        result = client.get_balance_sheet('2023-12-31')
        
        assert result is not None
        assert len(result) == 1
        assert result[0]['ReportName'] == 'BalanceSheet'
        assert result[0]['ReportDate'] == '2023-12-31'
    
    @patch('xero_python.accounting.AccountingApi')
    @patch('xero_python.api_client.ApiClient')
    def test_get_profit_loss_success(self, mock_api_client_class, mock_accounting_api_class):
        """Test successful profit and loss retrieval"""
        # Mock API client
        mock_api_client = Mock()
        mock_api_client_class.return_value = mock_api_client
        
        # Mock accounting API
        mock_accounting_api = Mock()
        mock_accounting_api_class.return_value = mock_accounting_api
        
        # Mock response
        mock_response = Mock()
        mock_response.reports = [
            Mock(
                report_id='test-report-id',
                report_name='ProfitAndLoss',
                report_date='2023-12-31',
                rows=[
                    Mock(
                        row_type='Header',
                        cells=[
                            Mock(value='Account'),
                            Mock(value='Amount')
                        ]
                    ),
                    Mock(
                        row_type='Section',
                        cells=[
                            Mock(value='Revenue'),
                            Mock(value='50000')
                        ]
                    )
                ]
            )
        ]
        mock_accounting_api.get_report_profit_and_loss.return_value = mock_response
        
        client = XeroAPIClient(
            client_id='test_client_id',
            client_secret='test_client_secret',
            access_token='test_access_token',
            tenant_id='test-tenant-id'
        )
        
        result = client.get_profit_loss('2023-01-01', '2023-12-31')
        
        assert result is not None
        assert len(result) == 1
        assert result[0]['ReportName'] == 'ProfitAndLoss'
    
    @patch('xero_python.accounting.AccountingApi')
    @patch('xero_python.api_client.ApiClient')
    def test_get_trial_balance_success(self, mock_api_client_class, mock_accounting_api_class):
        """Test successful trial balance retrieval"""
        # Mock API client
        mock_api_client = Mock()
        mock_api_client_class.return_value = mock_api_client
        
        # Mock accounting API
        mock_accounting_api = Mock()
        mock_accounting_api_class.return_value = mock_accounting_api
        
        # Mock response
        mock_response = Mock()
        mock_response.reports = [
            Mock(
                report_id='test-report-id',
                report_name='TrialBalance',
                report_date='2023-12-31',
                rows=[
                    Mock(
                        row_type='Header',
                        cells=[
                            Mock(value='Account'),
                            Mock(value='Debit'),
                            Mock(value='Credit')
                        ]
                    )
                ]
            )
        ]
        mock_accounting_api.get_report_trial_balance.return_value = mock_response
        
        client = XeroAPIClient(
            client_id='test_client_id',
            client_secret='test_client_secret',
            access_token='test_access_token',
            tenant_id='test-tenant-id'
        )
        
        result = client.get_trial_balance('2023-12-31')
        
        assert result is not None
        assert len(result) == 1
        assert result[0]['ReportName'] == 'TrialBalance'
    
    @patch('xero_python.accounting.AccountingApi')
    @patch('xero_python.api_client.ApiClient')
    def test_get_invoices_success(self, mock_api_client_class, mock_accounting_api_class):
        """Test successful invoices retrieval"""
        # Mock API client
        mock_api_client = Mock()
        mock_api_client_class.return_value = mock_api_client
        
        # Mock accounting API
        mock_accounting_api = Mock()
        mock_accounting_api_class.return_value = mock_accounting_api
        
        # Mock response
        mock_response = Mock()
        mock_response.invoices = [
            Mock(
                invoice_id='test-invoice-id',
                invoice_number='INV-001',
                type='ACCREC',
                status='AUTHORISED',
                date='2023-01-01',
                due_date='2023-01-31',
                total=1000.0,
                amount_due=1000.0,
                amount_paid=0.0,
                contact=Mock(
                    contact_id='test-contact-id',
                    name='Test Customer'
                )
            )
        ]
        mock_accounting_api.get_invoices.return_value = mock_response
        
        client = XeroAPIClient(
            client_id='test_client_id',
            client_secret='test_client_secret',
            access_token='test_access_token',
            tenant_id='test-tenant-id'
        )
        
        result = client.get_invoices()
        
        assert result is not None
        assert len(result) == 1
        assert result[0]['InvoiceID'] == 'test-invoice-id'
        assert result[0]['InvoiceNumber'] == 'INV-001'
        assert result[0]['Total'] == 1000.0
    
    def test_convert_report_to_dataframe(self):
        """Test report conversion to DataFrame"""
        client = XeroAPIClient(
            client_id='test_client_id',
            client_secret='test_client_secret'
        )
        
        mock_report = Mock()
        mock_report.report_id = 'test-report-id'
        mock_report.report_name = 'TestReport'
        mock_report.report_date = '2023-12-31'
        mock_report.rows = [
            Mock(
                row_type='Header',
                cells=[
                    Mock(value='Account'),
                    Mock(value='Amount')
                ]
            ),
            Mock(
                row_type='Section',
                cells=[
                    Mock(value='Assets'),
                    Mock(value='100000')
                ]
            ),
            Mock(
                row_type='SummaryRow',
                cells=[
                    Mock(value='Total Assets'),
                    Mock(value='100000')
                ]
            )
        ]
        
        result = client.convert_report_to_dataframe(mock_report)
        
        assert result is not None
        assert len(result) == 2  # Header row excluded
        assert result.iloc[0]['Account'] == 'Assets'
        assert result.iloc[0]['Amount'] == '100000'
    
    def test_convert_report_to_dataframe_empty(self):
        """Test report conversion with empty report"""
        client = XeroAPIClient(
            client_id='test_client_id',
            client_secret='test_client_secret'
        )
        
        mock_report = Mock()
        mock_report.report_id = 'test-report-id'
        mock_report.report_name = 'TestReport'
        mock_report.report_date = '2023-12-31'
        mock_report.rows = []
        
        result = client.convert_report_to_dataframe(mock_report)
        
        assert result is not None
        assert len(result) == 0
    
    def test_convert_organization_to_dict(self):
        """Test organization conversion to dictionary"""
        client = XeroAPIClient(
            client_id='test_client_id',
            client_secret='test_client_secret'
        )
        
        mock_org = Mock()
        mock_org.organisation_id = 'test-org-id'
        mock_org.name = 'Test Organization'
        mock_org.legal_name = 'Test Organization Ltd'
        mock_org.country_code = 'US'
        mock_org.base_currency = 'USD'
        mock_org.organisation_status = 'ACTIVE'
        mock_org.is_demo_company = False
        mock_org.organisation_entity_type = 'COMPANY'
        mock_org.registration_number = 'REG123'
        mock_org.tax_number = 'TAX123'
        mock_org.financial_year_end_day = 31
        mock_org.financial_year_end_month = 12
        mock_org.sales_tax_basis = 'ACCRUALS'
        mock_org.sales_tax_period = 'MONTHLY'
        mock_org.default_sales_tax = 'Sales Tax'
        mock_org.default_purchases_tax = 'Purchase Tax'
        mock_org.period_lock_date = '2023-01-01'
        mock_org.end_of_year_lock_date = '2023-12-31'
        mock_org.created_date_utc = '2023-01-01T00:00:00Z'
        mock_org.timezone = 'America/New_York'
        mock_org.organisation_type = 'COMPANY'
        mock_org.short_code = 'TEST'
        mock_org.edition = 'BUSINESS'
        mock_org.class_ = 'BUSINESS'
        mock_org.addresses = []
        mock_org.phones = []
        mock_org.external_links = []
        mock_org.payment_terms = {}
        mock_org.organisation_status = 'ACTIVE'
        
        result = client.convert_organization_to_dict(mock_org)
        
        assert result is not None
        assert result['OrganisationID'] == 'test-org-id'
        assert result['Name'] == 'Test Organization'
        assert result['LegalName'] == 'Test Organization Ltd'
        assert result['CountryCode'] == 'US'
        assert result['BaseCurrency'] == 'USD'
    
    def test_convert_account_to_dict(self):
        """Test account conversion to dictionary"""
        client = XeroAPIClient(
            client_id='test_client_id',
            client_secret='test_client_secret'
        )
        
        mock_account = Mock()
        mock_account.account_id = 'test-account-id'
        mock_account.code = '1000'
        mock_account.name = 'Test Bank Account'
        mock_account.type = 'BANK'
        mock_account.bank_account_number = '1234567890'
        mock_account.status = 'ACTIVE'
        mock_account.description = 'Test bank account'
        mock_account.bank_account_type = 'BANK'
        mock_account.currency_code = 'USD'
        mock_account.tax_type = 'NONE'
        mock_account.enable_payments_to_account = True
        mock_account.show_in_expense_claims = True
        mock_account.class_ = 'ASSET'
        mock_account.system_account = 'BANKCURRENCYGAIN'
        mock_account.reporting_code = 'BANK'
        mock_account.reporting_code_name = 'Bank'
        mock_account.has_attachments = False
        
        result = client.convert_account_to_dict(mock_account)
        
        assert result is not None
        assert result['AccountID'] == 'test-account-id'
        assert result['Code'] == '1000'
        assert result['Name'] == 'Test Bank Account'
        assert result['Type'] == 'BANK'
        assert result['Status'] == 'ACTIVE'
    
    def test_convert_invoice_to_dict(self):
        """Test invoice conversion to dictionary"""
        client = XeroAPIClient(
            client_id='test_client_id',
            client_secret='test_client_secret'
        )
        
        mock_contact = Mock()
        mock_contact.contact_id = 'test-contact-id'
        mock_contact.name = 'Test Customer'
        
        mock_invoice = Mock()
        mock_invoice.invoice_id = 'test-invoice-id'
        mock_invoice.invoice_number = 'INV-001'
        mock_invoice.reference = 'REF-001'
        mock_invoice.type = 'ACCREC'
        mock_invoice.status = 'AUTHORISED'
        mock_invoice.date = '2023-01-01'
        mock_invoice.due_date = '2023-01-31'
        mock_invoice.line_amount_types = 'Exclusive'
        mock_invoice.sub_total = 909.09
        mock_invoice.total_tax = 90.91
        mock_invoice.total = 1000.0
        mock_invoice.total_discount = 0.0
        mock_invoice.amount_due = 1000.0
        mock_invoice.amount_paid = 0.0
        mock_invoice.amount_credited = 0.0
        mock_invoice.currency_code = 'USD'
        mock_invoice.currency_rate = 1.0
        mock_invoice.line_items = []
        mock_invoice.contact = mock_contact
        mock_invoice.updated_date_utc = '2023-01-01T00:00:00Z'
        mock_invoice.has_attachments = False
        
        result = client.convert_invoice_to_dict(mock_invoice)
        
        assert result is not None
        assert result['InvoiceID'] == 'test-invoice-id'
        assert result['InvoiceNumber'] == 'INV-001'
        assert result['Type'] == 'ACCREC'
        assert result['Status'] == 'AUTHORISED'
        assert result['Total'] == 1000.0
        assert result['ContactName'] == 'Test Customer'
