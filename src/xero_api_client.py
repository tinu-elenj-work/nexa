"""
Xero API Client

This module provides a client for connecting to and querying the Xero API.
It handles OAuth2 authentication and provides methods for extracting data
that can be mapped to Vision database structures.
"""

import os
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timezone
import json

from xero_python.api_client import ApiClient, Configuration
from xero_python.api_client.oauth2 import OAuth2Token
from xero_python.accounting import AccountingApi
from xero_python.project import ProjectApi
from xero_python.identity import IdentityApi
from xero_python.exceptions import AccountingBadRequestException, ApiException


class XeroAPIClient:
    """Client for connecting to and querying the Xero API."""
    
    def __init__(self, client_id: str, client_secret: str, access_token: str = None, refresh_token: str = None):
        """
        Initialize the Xero API client.
        
        Args:
            client_id: Xero app client ID
            client_secret: Xero app client secret
            access_token: OAuth2 access token (optional, can be set later)
            refresh_token: OAuth2 refresh token (optional, for token refresh)
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.current_token_set = None
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Initialize API client
        self.api_client = ApiClient(
            Configuration(
                debug=False,
                oauth2_token=OAuth2Token(
                    client_id=client_id,
                    client_secret=client_secret
                ),
            ),
            pool_threads=1,
        )
        
        # Set up token getter/setter functions first
        @self.api_client.oauth2_token_getter
        def obtain_xero_oauth2_token():
            return self.current_token_set
        
        @self.api_client.oauth2_token_saver
        def store_xero_oauth2_token(token):
            self.current_token_set = token
        
        # Store tokens if provided
        if access_token:
            token_set = {
                "access_token": access_token,
                "token_type": "Bearer",
                "expires_in": 1800,  # 30 minutes
                "scope": ["accounting.transactions", "accounting.transactions.read", "accounting.reports.read", 
                         "accounting.contacts", "accounting.contacts.read", "accounting.settings.read", 
                         "projects", "projects.read", "offline_access"]
            }
            if refresh_token:
                token_set["refresh_token"] = refresh_token
            self.current_token_set = token_set
            self.api_client.set_oauth2_token(token_set)
        
        # Initialize API instances
        self.accounting_api = AccountingApi(self.api_client)
        self.project_api = ProjectApi(self.api_client)
        self.identity_api = IdentityApi(self.api_client)
        
        self._tenant_id = None
    
    def set_token(self, access_token: str, refresh_token: str = None, expires_in: int = 1800):
        """
        Set OAuth2 tokens for API access.
        
        Args:
            access_token: OAuth2 access token
            refresh_token: OAuth2 refresh token (optional)
            expires_in: Token expiry time in seconds (default 30 minutes)
        """
        token_set = {
            "access_token": access_token,
            "token_type": "Bearer",
            "expires_in": expires_in
        }
        if refresh_token:
            token_set["refresh_token"] = refresh_token
            
        self.current_token_set = token_set
        self.api_client.set_oauth2_token(token_set)
        self.logger.info("Xero API tokens updated successfully")
    
    def refresh_token(self):
        """Refresh the OAuth2 access token using the refresh token."""
        try:
            self.api_client.refresh_oauth2_token()
            self.logger.info("Xero API token refreshed successfully")
        except Exception as e:
            self.logger.error(f"Failed to refresh Xero API token: {e}")
            raise
    
    def get_tenant_id(self) -> str:
        """Get the Xero tenant ID for API calls."""
        if not self._tenant_id:
            try:
                connections = self.identity_api.get_connections()
                if connections and len(connections) > 0:
                    self._tenant_id = connections[0].tenant_id
                    self.logger.info(f"Retrieved Xero tenant ID: {self._tenant_id}")
                else:
                    raise Exception("No Xero connections found")
            except Exception as e:
                self.logger.error(f"Failed to get Xero tenant ID: {e}")
                raise
        return self._tenant_id
    
    def get_contacts(self, where: str = None, order: str = None) -> List[Dict[str, Any]]:
        """
        Retrieve contacts from Xero accounting API.
        
        Args:
            where: OData filter expression
            order: Order by expression
            
        Returns:
            List of contact dictionaries
        """
        try:
            tenant_id = self.get_tenant_id()
            response = self.accounting_api.get_contacts(
                xero_tenant_id=tenant_id,
                where=where,
                order=order
            )
            
            contacts = []
            if response.contacts:
                for contact in response.contacts:
                    contact_dict = {
                        'contact_id': contact.contact_id,
                        'name': contact.name,
                        'first_name': contact.first_name,
                        'last_name': contact.last_name,
                        'email_address': contact.email_address,
                        'contact_number': contact.contact_number,
                        'contact_status': contact.contact_status,
                        'is_supplier': contact.is_supplier,
                        'is_customer': contact.is_customer,
                        'account_number': contact.account_number,
                        'tax_number': contact.tax_number,
                        'bank_account_details': contact.bank_account_details,
                        'updated_date_utc': contact.updated_date_utc.isoformat() if contact.updated_date_utc else None
                    }
                    
                    # Add address information if available
                    if contact.addresses:
                        address = contact.addresses[0]  # Take first address
                        contact_dict.update({
                            'address_line1': address.address_line1,
                            'address_line2': address.address_line2,
                            'city': address.city,
                            'region': address.region,
                            'postal_code': address.postal_code,
                            'country': address.country
                        })
                    
                    # Add phone information if available
                    if contact.phones:
                        for phone in contact.phones:
                            if phone.phone_type == 'DEFAULT':
                                contact_dict['phone_number'] = phone.phone_number
                                break
                    
                    contacts.append(contact_dict)
            
            self.logger.info(f"Retrieved {len(contacts)} contacts from Xero")
            return contacts
            
        except AccountingBadRequestException as e:
            self.logger.error(f"Xero API error retrieving contacts: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Error retrieving contacts: {e}")
            raise
    
    def get_employees(self) -> List[Dict[str, Any]]:
        """
        Retrieve employees from Xero accounting API.
        
        Returns:
            List of employee dictionaries
        """
        try:
            tenant_id = self.get_tenant_id()
            response = self.accounting_api.get_employees(xero_tenant_id=tenant_id)
            
            employees = []
            if response.employees:
                for employee in response.employees:
                    employee_dict = {
                        'employee_id': employee.employee_id,
                        'first_name': employee.first_name,
                        'last_name': employee.last_name,
                        'display_name': employee.display_name,
                        'email': employee.email,
                        'status': employee.status,
                        'updated_date_utc': employee.updated_date_utc.isoformat() if employee.updated_date_utc else None
                    }
                    employees.append(employee_dict)
            
            self.logger.info(f"Retrieved {len(employees)} employees from Xero")
            return employees
            
        except AccountingBadRequestException as e:
            self.logger.error(f"Xero API error retrieving employees: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Error retrieving employees: {e}")
            raise
    
    def get_projects(self, project_ids: List[str] = None) -> List[Dict[str, Any]]:
        """
        Retrieve projects from Xero projects API.
        
        Args:
            project_ids: List of specific project IDs to retrieve (optional)
            
        Returns:
            List of project dictionaries
        """
        try:
            tenant_id = self.get_tenant_id()
            response = self.project_api.get_projects(
                xero_tenant_id=tenant_id,
                project_ids=project_ids
            )
            
            projects = []
            if response.items:
                for project in response.items:
                    project_dict = {
                        'project_id': project.project_id,
                        'contact_id': project.contact_id,
                        'name': project.name,
                        'status': project.status,
                        'minutes_logged': project.minutes_logged,
                        'minutes_to_be_invoiced': project.minutes_to_be_invoiced,
                        'deadline_utc': project.deadline_utc.isoformat() if project.deadline_utc else None,
                        'currency_code': str(project.currency_code) if project.currency_code else None
                    }
                    
                    # Add amount information if available
                    if project.total_task_amount:
                        project_dict['total_task_amount'] = float(project.total_task_amount.value) if project.total_task_amount.value else 0
                    if project.total_expense_amount:
                        project_dict['total_expense_amount'] = float(project.total_expense_amount.value) if project.total_expense_amount.value else 0
                    if project.estimate_amount:
                        project_dict['estimate_amount'] = float(project.estimate_amount.value) if project.estimate_amount.value else 0
                    
                    projects.append(project_dict)
            
            self.logger.info(f"Retrieved {len(projects)} projects from Xero")
            return projects
            
        except ApiException as e:
            self.logger.error(f"Xero API error retrieving projects: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Error retrieving projects: {e}")
            raise
    
    def get_project_users(self, project_id: str) -> List[Dict[str, Any]]:
        """
        Retrieve users assigned to a specific project.
        
        Args:
            project_id: The Xero project ID
            
        Returns:
            List of project user dictionaries
        """
        try:
            tenant_id = self.get_tenant_id()
            response = self.project_api.get_project_users(
                xero_tenant_id=tenant_id,
                project_id=project_id
            )
            
            users = []
            if response.items:
                for user in response.items:
                    user_dict = {
                        'user_id': user.user_id,
                        'name': user.name,
                        'email': user.email
                    }
                    users.append(user_dict)
            
            self.logger.info(f"Retrieved {len(users)} users for project {project_id}")
            return users
            
        except ApiException as e:
            self.logger.error(f"Xero API error retrieving project users: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Error retrieving project users: {e}")
            raise
    
    def get_time_entries(self, project_id: str = None, user_id: str = None, 
                        date_after_utc: datetime = None, date_before_utc: datetime = None) -> List[Dict[str, Any]]:
        """
        Retrieve time entries from Xero projects API.
        
        Args:
            project_id: Filter by project ID (optional)
            user_id: Filter by user ID (optional)
            date_after_utc: Filter entries after this date (optional)
            date_before_utc: Filter entries before this date (optional)
            
        Returns:
            List of time entry dictionaries
        """
        try:
            tenant_id = self.get_tenant_id()
            response = self.project_api.get_time_entries(
                xero_tenant_id=tenant_id,
                project_id=project_id,
                user_id=user_id,
                date_after_utc=date_after_utc,
                date_before_utc=date_before_utc
            )
            
            time_entries = []
            if response.items:
                for entry in response.items:
                    entry_dict = {
                        'time_entry_id': entry.time_entry_id,
                        'user_id': entry.user_id,
                        'project_id': entry.project_id,
                        'task_id': entry.task_id,
                        'date_utc': entry.date_utc.isoformat() if entry.date_utc else None,
                        'start_utc': entry.start_utc.isoformat() if entry.start_utc else None,
                        'end_utc': entry.end_utc.isoformat() if entry.end_utc else None,
                        'description': entry.description,
                        'duration': entry.duration
                    }
                    time_entries.append(entry_dict)
            
            self.logger.info(f"Retrieved {len(time_entries)} time entries from Xero")
            return time_entries
            
        except ApiException as e:
            self.logger.error(f"Xero API error retrieving time entries: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Error retrieving time entries: {e}")
            raise
    
    def get_invoices(self, contact_ids: List[str] = None, statuses: List[str] = None,
                    if_modified_since: datetime = None) -> List[Dict[str, Any]]:
        """
        Retrieve invoices from Xero accounting API.
        
        Args:
            contact_ids: Filter by contact IDs (optional)
            statuses: Filter by invoice statuses (optional)
            if_modified_since: Only return invoices modified since this date (optional)
            
        Returns:
            List of invoice dictionaries
        """
        try:
            tenant_id = self.get_tenant_id()
            response = self.accounting_api.get_invoices(
                xero_tenant_id=tenant_id,
                contact_ids=contact_ids,
                statuses=statuses,
                if_modified_since=if_modified_since
            )
            
            invoices = []
            if response.invoices:
                for invoice in response.invoices:
                    invoice_dict = {
                        'invoice_id': invoice.invoice_id,
                        'invoice_number': invoice.invoice_number,
                        'contact_id': invoice.contact.contact_id if invoice.contact else None,
                        'type': invoice.type,
                        'status': invoice.status,
                        'date': invoice.date.isoformat() if invoice.date else None,
                        'due_date': invoice.due_date.isoformat() if invoice.due_date else None,
                        'sub_total': float(invoice.sub_total) if invoice.sub_total else 0,
                        'total_tax': float(invoice.total_tax) if invoice.total_tax else 0,
                        'total': float(invoice.total) if invoice.total else 0,
                        'amount_due': float(invoice.amount_due) if invoice.amount_due else 0,
                        'amount_paid': float(invoice.amount_paid) if invoice.amount_paid else 0,
                        'amount_credited': float(invoice.amount_credited) if invoice.amount_credited else 0,
                        'currency_code': invoice.currency_code,
                        'updated_date_utc': invoice.updated_date_utc.isoformat() if invoice.updated_date_utc else None
                    }
                    invoices.append(invoice_dict)
            
            self.logger.info(f"Retrieved {len(invoices)} invoices from Xero")
            return invoices
            
        except AccountingBadRequestException as e:
            self.logger.error(f"Xero API error retrieving invoices: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Error retrieving invoices: {e}")
            raise
    
    @classmethod
    def from_config(cls, config_dict: Dict[str, str]) -> 'XeroAPIClient':
        """
        Create XeroAPIClient instance from configuration dictionary.
        
        Args:
            config_dict: Dictionary containing Xero API credentials
            
        Returns:
            Configured XeroAPIClient instance
        """
        return cls(
            client_id=config_dict.get('XERO_CLIENT_ID'),
            client_secret=config_dict.get('XERO_CLIENT_SECRET'),
            access_token=config_dict.get('XERO_ACCESS_TOKEN'),
            refresh_token=config_dict.get('XERO_REFRESH_TOKEN')
        )
    
    def get_accounts(self, where: str = None, order: str = None) -> List[Dict[str, Any]]:
        """
        Retrieve chart of accounts from Xero.
        
        Args:
            where: OData filter expression
            order: Order by expression
            
        Returns:
            List of account dictionaries
        """
        try:
            tenant_id = self.get_tenant_id()
            response = self.accounting_api.get_accounts(
                xero_tenant_id=tenant_id,
                where=where,
                order=order
            )
            
            accounts = []
            if response.accounts:
                for account in response.accounts:
                    account_dict = {
                        'account_id': account.account_id,
                        'code': account.code,
                        'name': account.name,
                        'type': account.type,
                        'tax_type': account.tax_type,
                        'status': account.status,
                        'description': account.description,
                        'class': getattr(account, 'class', None),
                        'system_account': getattr(account, 'system_account', None),
                        'enable_payments_to_account': getattr(account, 'enable_payments_to_account', None),
                        'show_in_expense_claims': getattr(account, 'show_in_expense_claims', None),
                        'currency_code': getattr(account, 'currency_code', None),
                        'reporting_code': getattr(account, 'reporting_code', None),
                        'reporting_code_name': getattr(account, 'reporting_code_name', None),
                        'has_attachments': getattr(account, 'has_attachments', None),
                        'updated_date_utc': account.updated_date_utc.isoformat() if account.updated_date_utc else None
                    }
                    accounts.append(account_dict)
            
            self.logger.info(f"Retrieved {len(accounts)} accounts from Xero")
            return accounts
            
        except AccountingBadRequestException as e:
            self.logger.error(f"Xero API error retrieving accounts: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Error retrieving accounts: {e}")
            raise

    def get_bank_transactions(self, if_modified_since: datetime = None, 
                             where: str = None, order: str = None, page: int = None) -> List[Dict[str, Any]]:
        """
        Retrieve bank transactions from Xero.
        
        Args:
            if_modified_since: Filter transactions modified since this date
            where: OData filter expression
            order: Order by expression
            page: Page number for pagination
            
        Returns:
            List of bank transaction dictionaries
        """
        try:
            tenant_id = self.get_tenant_id()
            response = self.accounting_api.get_bank_transactions(
                xero_tenant_id=tenant_id,
                if_modified_since=if_modified_since,
                where=where,
                order=order,
                page=page
            )
            
            transactions = []
            if response.bank_transactions:
                for txn in response.bank_transactions:
                    txn_dict = {
                        'bank_transaction_id': txn.bank_transaction_id,
                        'type': txn.type,
                        'status': txn.status,
                        'date': txn.date.isoformat() if txn.date else None,
                        'reference': txn.reference,
                        'currency_code': txn.currency_code,
                        'currency_rate': float(txn.currency_rate) if txn.currency_rate else None,
                        'url': txn.url,
                        'status_attribute_string': txn.status_attribute_string,
                        'total': float(txn.total) if txn.total else 0,
                        'sub_total': float(txn.sub_total) if txn.sub_total else 0,
                        'total_tax': float(txn.total_tax) if txn.total_tax else 0,
                        'has_attachments': txn.has_attachments,
                        'updated_date_utc': txn.updated_date_utc.isoformat() if txn.updated_date_utc else None
                    }
                    
                    # Add contact information if available
                    if txn.contact:
                        txn_dict.update({
                            'contact_id': txn.contact.contact_id,
                            'contact_name': txn.contact.name
                        })
                    
                    # Add bank account information if available
                    if txn.bank_account:
                        txn_dict.update({
                            'bank_account_id': txn.bank_account.account_id,
                            'bank_account_name': txn.bank_account.name,
                            'bank_account_code': txn.bank_account.code
                        })
                    
                    transactions.append(txn_dict)
            
            self.logger.info(f"Retrieved {len(transactions)} bank transactions from Xero")
            return transactions
            
        except AccountingBadRequestException as e:
            self.logger.error(f"Xero API error retrieving bank transactions: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Error retrieving bank transactions: {e}")
            raise

    @classmethod
    def from_env(cls) -> 'XeroAPIClient':
        """
        Create XeroAPIClient instance from environment variables.
        
        Expected environment variables:
        - XERO_CLIENT_ID
        - XERO_CLIENT_SECRET
        - XERO_ACCESS_TOKEN (optional)
        - XERO_REFRESH_TOKEN (optional)
        
        Returns:
            Configured XeroAPIClient instance
        """
        return cls(
            client_id=os.getenv('XERO_CLIENT_ID'),
            client_secret=os.getenv('XERO_CLIENT_SECRET'),
            access_token=os.getenv('XERO_ACCESS_TOKEN'),
            refresh_token=os.getenv('XERO_REFRESH_TOKEN')
        )
