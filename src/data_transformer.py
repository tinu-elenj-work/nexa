#!/usr/bin/env python3
"""
Nexa - Enhanced Data Transformation Layer for ElapseIT API
Standardizes API output to match expected file format
"""

import pandas as pd
from datetime import datetime
import re
from typing import Dict, List, Optional, Tuple, Any

class ElapseITDataTransformer:
    """Transforms ElapseIT API data to match expected file format"""
    
    def __init__(self):
        """Initialize the transformer with configuration"""
        self.date_format_map = {
            'api': '%Y-%m-%dT%H:%M:%SZ',
            'file': '%Y-%b-%d'
        }
        
        # Column mapping for each data type
        self.field_mappings = {
            'clients': {
                'ID': 'ID',
                'Code': 'Code',
                'Name': 'Name',
                'Address': 'Address',
                'City': 'City',
                'State': 'State',
                'Zipcode': 'Zipcode',
                'Country': 'Country',
                'IsArchived': 'IsArchived',
                'ArchivedDate': 'ArchivedDate',
                'VatNumber': 'VatNumber',
                'RegistrationNumber': 'RegistrationNumber',
                'OtherLegalDetails': 'OtherLegalDetails',
                'BankName': 'BankName',
                'AccountNumber': 'AccountNumber',
                'OtherBankDetails': 'OtherBankDetails',
                'InvoiceDueDateDays': 'InvoiceDueDateDays'
            },
            'people': {
                'ID': 'ID',
                'FirstName': 'FirstName',
                'LastName': 'LastName',
                'Email': 'Email',
                'IsContractor': 'IsContractor',
                'MobilePhone': 'MobilePhone',
                'OfficePhone': 'OfficePhone',
                'WeeklyWorkingHours': 'WeeklyWorkingHours',
                'IsArchived': 'IsArchived',
                'ArchivedDate': 'ArchivedDate',
                'HasLicense': 'HasLicense',
                # API-specific mappings
                'JobTitleID': 'JobTitle',
                'DepartmentID': 'Department',
                'LocationID': 'Location',
                'CreatedDate': 'StartedDate',
                'HasLogin': 'HasAccount',
                'CompanyRoleID': 'AccessLevel',
                'Title': 'Skills'  # Approximate mapping
            },
            'projects': {
                'ID': 'ID',
                'Code': 'Code',
                'Name': 'Name',
                'Description': 'Description',
                'StartDate': 'StartDate',
                'EndDate': 'EndDate',
                'GoingLiveDate': 'GoingLiveDate',
                'Status': 'Status',
                'TimesheetAccessType': 'TimesheetAccessType',
                'TimesheetApprovalType': 'TimesheetApprovalType',
                'IsArchived': 'IsArchived',
                'ArchivedDate': 'ArchivedDate',
                'Currency': 'Currency',
                'BudgetInHours': 'BudgetInHours',
                'DefaultDailyRate': 'DefaultDailyRate',
                'DefaultDailyRateRemote': 'DefaultDailyRateRemote',
                'IsDailyRate': 'IsDailyRate',
                'ClientID': 'Client.Code',  # Will need enrichment
                # Missing fields that need defaults
                'ProjectType': 'Standard',
                'BudgetInMoney': 0,
                'DefaultHourlyRate': 0,
                'DefaultHourlyRateRemote': 0,
                'CompletionPercentage': 0,
                'ActualLoggedHours': 0,
                'ExpectedLoggedHours': 0
            }
        }
    
    def standardize_data_types(self, df: pd.DataFrame, data_type: str) -> pd.DataFrame:
        """Standardize data types to match file format expectations"""
        print(f"   🔧 Standardizing data types for {data_type}...")
        
        result_df = df.copy()
        
        if data_type == 'clients':
            # Convert Code to string (file format expects this as text)
            if 'Code' in result_df.columns:
                result_df['Code'] = result_df['Code'].astype(str)
                print(f"      ✅ Code: converted to string")
            
            # Convert AccountNumber to string
            if 'AccountNumber' in result_df.columns:
                result_df['AccountNumber'] = result_df['AccountNumber'].fillna('').astype(str)
                print(f"      ✅ AccountNumber: converted to string")
                
        elif data_type == 'people':
            # Convert WeeklyWorkingHours to int
            if 'WeeklyWorkingHours' in result_df.columns:
                result_df['WeeklyWorkingHours'] = pd.to_numeric(result_df['WeeklyWorkingHours'], errors='coerce').fillna(40).astype(int)
                print(f"      ✅ WeeklyWorkingHours: converted to int")
                
        elif data_type == 'projects':
            # Convert BudgetInHours to float
            if 'BudgetInHours' in result_df.columns:
                result_df['BudgetInHours'] = pd.to_numeric(result_df['BudgetInHours'], errors='coerce')
                print(f"      ✅ BudgetInHours: converted to numeric")
            
            # Convert Description to string
            if 'Description' in result_df.columns:
                result_df['Description'] = result_df['Description'].fillna('').astype(str)
                print(f"      ✅ Description: converted to string")
                
        elif data_type == 'allocations':
            # Convert Project.Code to string
            if 'Project.Code' in result_df.columns:
                result_df['Project.Code'] = result_df['Project.Code'].astype(str)
                print(f"      ✅ Project.Code: converted to string")
        
        return result_df

    def transform_dates(self, df: pd.DataFrame, date_columns: List[str]) -> pd.DataFrame:
        """Transform API date format to file date format"""
        print("   🔄 Transforming date formats...")
        
        transformed_df = df.copy()
        
        for col in date_columns:
            if col in transformed_df.columns:
                try:
                    # Handle different date formats
                    transformed_df[col] = pd.to_datetime(
                        transformed_df[col], 
                        errors='coerce'
                    )
                    
                    # Convert to file format (YYYY-Mon-DD)
                    transformed_df[col] = transformed_df[col].dt.strftime('%Y-%b-%d')
                    
                    print(f"      ✅ {col}: ISO → Abbreviated format")
                except Exception as e:
                    print(f"      ⚠️  {col}: Date transformation failed - {e}")
        
        return transformed_df

    def transform_clients(self, clients_df: pd.DataFrame) -> pd.DataFrame:
        """Transform clients data to match file format"""
        print("   🔄 Transforming clients data...")
        
        # Expected columns in file format
        expected_columns = [
            'Code', 'Name', 'Address', 'City', 'State', 'Zipcode', 'Country',
            'IsArchived', 'ArchivedDate', 'VatNumber', 'RegistrationNumber',
            'OtherLegalDetails', 'BankName', 'AccountNumber', 'OtherBankDetails',
            'InvoiceDueDateDays'
        ]
        
        result_df = pd.DataFrame()
        
        for col in expected_columns:
            if col in clients_df.columns:
                result_df[col] = clients_df[col]
            else:
                # Set default values for missing columns
                if col in ['AccountNumber', 'BankName', 'OtherBankDetails']:
                    result_df[col] = ''
                elif col == 'InvoiceDueDateDays':
                    result_df[col] = 30  # Default payment terms
                else:
                    result_df[col] = None
        
        # Standardize data types
        result_df = self.standardize_data_types(result_df, 'clients')
        
        print(f"      ✅ Transformed {len(result_df)} client records")
        return result_df

    def transform_people(self, people_df: pd.DataFrame) -> pd.DataFrame:
        """Transform people data to match file format"""
        print("   🔄 Transforming people data...")
        
        # Expected columns in file format
        expected_columns = [
            'CompanyID', 'FirstName', 'LastName', 'Email', 'JobTitle', 'AccessLevel',
            'HasLicense', 'HasAccount', 'IsContractor', 'MobilePhone', 'OfficePhone',
            'StartedDate', 'WeeklyWorkingHours', 'IsArchived', 'ArchivedDate',
            'Location', 'Department', 'Skills'
        ]
        
        result_df = pd.DataFrame()
        
        for col in expected_columns:
            if col in people_df.columns:
                result_df[col] = people_df[col]
            else:
                # Map from API fields or set defaults
                if col == 'CompanyID':
                    result_df[col] = 1  # Default company
                elif col == 'JobTitle':
                    result_df[col] = people_df.get('Title', 'Employee')
                elif col == 'AccessLevel':
                    result_df[col] = 'Standard'
                elif col == 'HasLicense':
                    # Check if HasLicense exists in API data, default to True for active employees
                    result_df[col] = people_df.get('HasLicense', True)
                elif col == 'HasAccount':
                    result_df[col] = people_df.get('HasLogin', False)
                elif col == 'StartedDate':
                    result_df[col] = people_df.get('CreatedDate', None)
                elif col == 'Location':
                    result_df[col] = 'Office'  # Default location
                elif col == 'Department':
                    result_df[col] = 'General'  # Default department
                elif col == 'Skills':
                    result_df[col] = ''  # Empty skills
                else:
                    result_df[col] = None
        
        # Transform dates
        result_df = self.transform_dates(result_df, ['StartedDate', 'ArchivedDate'])
        
        # Standardize data types
        result_df = self.standardize_data_types(result_df, 'people')
        
        print(f"      ✅ Transformed {len(result_df)} people records")
        return result_df

    def transform_projects(self, projects_df: pd.DataFrame, clients_df: pd.DataFrame) -> pd.DataFrame:
        """Transform projects data to match file format"""
        print("   🔄 Transforming projects data...")
        
        # Expected columns in file format
        expected_columns = [
            'Code', 'Name', 'Description', 'ProjectType', 'StartDate', 'EndDate',
            'GoingLiveDate', 'Status', 'TimesheetAccessType', 'TimesheetApprovalType',
            'IsArchived', 'ArchivedDate', 'Currency', 'BudgetInHours', 'BudgetInMoney',
            'DefaultHourlyRate', 'DefaultDailyRate', 'DefaultHourlyRateRemote',
            'DefaultDailyRateRemote', 'IsDailyRate', 'Client.Code', 'Client.Name',
            'CompletionPercentage', 'ActualLoggedHours', 'ExpectedLoggedHours',
            'PO-CODE1', 'PO-CODE2', 'PO-CODE3', 'PO-CODE4', 'PO-CODE5', 'PO-CODE6'
        ]
        
        result_df = pd.DataFrame()
        
        # Add client information
        enriched_df = projects_df.copy()
        if 'ClientID' in enriched_df.columns and 'ID' in clients_df.columns:
            enriched_df = enriched_df.merge(
                clients_df[['ID', 'Code', 'Name']],
                left_on='ClientID',
                right_on='ID',
                how='left',
                suffixes=('', '_Client')
            )
            enriched_df['Client.Code'] = enriched_df['Code_Client']
            enriched_df['Client.Name'] = enriched_df['Name_Client']
        
        for col in expected_columns:
            if col in enriched_df.columns:
                result_df[col] = enriched_df[col]
            else:
                # Set default values for missing columns
                if col == 'ProjectType':
                    result_df[col] = 'Standard'
                elif col in ['BudgetInMoney', 'DefaultHourlyRate', 'DefaultHourlyRateRemote']:
                    result_df[col] = 0.0
                elif col in ['CompletionPercentage', 'ActualLoggedHours', 'ExpectedLoggedHours']:
                    result_df[col] = 0
                elif col.startswith('PO-CODE'):
                    result_df[col] = ''
                elif col in ['Client.Code', 'Client.Name'] and col not in enriched_df.columns:
                    result_df[col] = ''
                else:
                    result_df[col] = None
        
        # Transform dates
        result_df = self.transform_dates(result_df, ['StartDate', 'EndDate', 'GoingLiveDate', 'ArchivedDate'])
        
        # Standardize data types
        result_df = self.standardize_data_types(result_df, 'projects')
        
        print(f"      ✅ Transformed {len(result_df)} project records")
        return result_df

    def enrich_allocations_with_related_data(
        self, 
        allocations_df: pd.DataFrame,
        clients_df: pd.DataFrame,
        people_df: pd.DataFrame,
        projects_df: pd.DataFrame
    ) -> pd.DataFrame:
        """Enrich allocations with client, person, and project information"""
        print("   🔄 Enriching allocations with related data...")
        print(f"      📊 Allocation columns: {list(allocations_df.columns)}")
        print(f"      📊 People columns: {list(people_df.columns)[:10]}...")  # Show first 10
        print(f"      📊 Projects columns: {list(projects_df.columns)[:10]}...")  # Show first 10
        
        enriched_df = allocations_df.copy()
        
        # Add person information
        if 'PersonID' in enriched_df.columns and 'ID' in people_df.columns:
            print(f"      🔗 Joining {len(enriched_df)} allocations with {len(people_df)} people...")
            enriched_df = enriched_df.merge(
                people_df[['ID', 'FirstName', 'LastName']], 
                left_on='PersonID', 
                right_on='ID', 
                how='left',
                suffixes=('', '_Person')
            )
            # Map to expected column names
            enriched_df['Person.FirstName'] = enriched_df['FirstName']
            enriched_df['Person.LastName'] = enriched_df['LastName']
            print(f"      ✅ Added person information (found {enriched_df['Person.FirstName'].notna().sum()} matches)")
        else:
            print(f"      ⚠️  Cannot join people: PersonID in allocations: {'PersonID' in enriched_df.columns}, ID in people: {'ID' in people_df.columns}")
        
        # Add project information
        if 'ProjectID' in enriched_df.columns and 'ID' in projects_df.columns:
            print(f"      🔗 Joining {len(enriched_df)} allocations with {len(projects_df)} projects...")
            enriched_df = enriched_df.merge(
                projects_df[['ID', 'Name', 'Code', 'ClientID']], 
                left_on='ProjectID', 
                right_on='ID', 
                how='left',
                suffixes=('', '_Project')
            )
            # Map to expected column names  
            enriched_df['Project.Name'] = enriched_df['Name']
            enriched_df['Project.Code'] = enriched_df['Code']
            print(f"      ✅ Added project information (found {enriched_df['Project.Name'].notna().sum()} matches)")
        else:
            print(f"      ⚠️  Cannot join projects: ProjectID in allocations: {'ProjectID' in enriched_df.columns}, ID in projects: {'ID' in projects_df.columns}")
        
        # Add client information through project relationship
        if 'ClientID' in enriched_df.columns and 'ID' in clients_df.columns:
            print(f"      🔗 Joining {len(enriched_df)} allocations with {len(clients_df)} clients...")
            enriched_df = enriched_df.merge(
                clients_df[['ID', 'Name', 'Code']], 
                left_on='ClientID', 
                right_on='ID', 
                how='left',
                suffixes=('', '_Client')
            )
            # Map to expected column names
            enriched_df['Client.Name'] = enriched_df['Name_Client']
            enriched_df['Client.Code'] = enriched_df['Code_Client']
            print(f"      ✅ Added client information (found {enriched_df['Client.Name'].notna().sum()} matches)")
        else:
            print(f"      ⚠️  Cannot join clients: ClientID in enriched: {'ClientID' in enriched_df.columns}, ID in clients: {'ID' in clients_df.columns}")
        
        return enriched_df

    def create_expected_allocation_columns(self, enriched_df: pd.DataFrame) -> pd.DataFrame:
        """Create the exact columns expected by the allocations file format"""
        print("   🔄 Creating expected allocation column structure...")
        
        # Define the expected columns based on file format analysis
        expected_columns = [
            'StartDate',
            'EndDate', 
            'HoursPerDay',
            'BusinessDays',
            'Person.FirstName',
            'Person.LastName',
            'Project.Code',
            'Project.Name',
            'Client.Code',
            'Client.Name',
            'ProjectPhase.Code',
            'ProjectPhase.Name',
            'ProjectActivity.Name',
            'ProjectActivity.IsBillable'
        ]
        
        # Create a new dataframe with expected columns
        result_df = pd.DataFrame()
        
        for col in expected_columns:
            if col in enriched_df.columns:
                result_df[col] = enriched_df[col]
                print(f"      ✅ {col}: mapped directly")
            else:
                # Try to find alternative column names or provide defaults
                if col == 'Person.FirstName' and 'FirstName' in enriched_df.columns:
                    result_df[col] = enriched_df['FirstName']
                    print(f"      ✅ {col}: mapped from FirstName")
                elif col == 'Person.LastName' and 'LastName' in enriched_df.columns:
                    result_df[col] = enriched_df['LastName']
                    print(f"      ✅ {col}: mapped from LastName")
                elif col == 'Project.Code' and 'Code' in enriched_df.columns:
                    result_df[col] = enriched_df['Code']
                    print(f"      ✅ {col}: mapped from Code")
                elif col == 'Project.Name' and 'Name' in enriched_df.columns:
                    result_df[col] = enriched_df['Name']
                    print(f"      ✅ {col}: mapped from Name")
                elif col == 'Client.Code' and 'Code_Client' in enriched_df.columns:
                    result_df[col] = enriched_df['Code_Client']
                    print(f"      ✅ {col}: mapped from Code_Client")
                elif col == 'Client.Name' and 'Name_Client' in enriched_df.columns:
                    result_df[col] = enriched_df['Name_Client']
                    print(f"      ✅ {col}: mapped from Name_Client")
                else:
                    # Fill with default values
                    if 'Date' in col:
                        result_df[col] = pd.NaT
                    elif col in ['ProjectPhase.Code', 'ProjectPhase.Name', 'ProjectActivity.Name']:
                        result_df[col] = ''  # Empty string for missing phase/activity info
                    elif col == 'ProjectActivity.IsBillable':
                        result_df[col] = True  # Default to billable
                    elif 'Hours' in col or 'Days' in col:
                        result_df[col] = 0
                    else:
                        result_df[col] = ''
                    
                    print(f"      ⚠️  {col}: filled with default value")
        
        return result_df

    def handle_duplicates(self, df: pd.DataFrame, strategy: str = 'business_logic') -> pd.DataFrame:
        """Handle duplicate records based on specified strategy"""
        print(f"   🔄 Handling duplicates using strategy: {strategy}")
        
        total_records = len(df)
        
        if strategy == 'business_logic':
            # For allocations, remove duplicates based on business keys
            business_keys = ['StartDate', 'EndDate', 'Person.FirstName', 'Person.LastName', 'Project.Code']
            available_keys = [col for col in business_keys if col in df.columns]
            
            if len(available_keys) >= 3:
                duplicate_count = df.duplicated(subset=available_keys).sum()
                if duplicate_count > 0:
                    print(f"      📊 Found {duplicate_count} duplicates out of {total_records} records")
                    result_df = df.drop_duplicates(subset=available_keys, keep='first')
                    print(f"      ✅ Removed duplicates based on business keys: {available_keys}")
                else:
                    print(f"      ✅ No duplicates found")
                    result_df = df
            else:
                duplicate_count = df.duplicated().sum()
                if duplicate_count > 0:
                    print(f"      📊 Found {duplicate_count} duplicates out of {total_records} records")
                    result_df = df.drop_duplicates(keep='first')
                    print(f"      ✅ Fallback: kept first occurrence of each duplicate")
                else:
                    print(f"      ✅ No duplicates found")
                    result_df = df
        else:
            result_df = df
            print(f"      ✅ No duplicate handling applied")
        
        final_records = len(result_df)
        if final_records != total_records:
            print(f"      📊 Final record count: {final_records} (removed {total_records - final_records})")
        
        return result_df

    def validate_transformation(self, original_df: pd.DataFrame, transformed_df: pd.DataFrame, data_type: str = 'allocations') -> Dict:
        """Validate the transformation results"""
        print("   🔍 Validating transformation...")
        
        if data_type == 'allocations':
            expected_columns = [
                'StartDate', 'EndDate', 'HoursPerDay', 'BusinessDays',
                'Person.FirstName', 'Person.LastName', 'Project.Code', 'Project.Name',
                'Client.Code', 'Client.Name', 'ProjectPhase.Code', 'ProjectPhase.Name',
                'ProjectActivity.Name', 'ProjectActivity.IsBillable'
            ]
        else:
            expected_columns = list(transformed_df.columns)
        
        validation_results = {
            'original_records': len(original_df),
            'transformed_records': len(transformed_df),
            'record_loss': len(original_df) - len(transformed_df),
            'expected_columns': len(expected_columns),
            'actual_columns': len(transformed_df.columns),
            'missing_columns': [],
            'data_quality_issues': []
        }
        
        # Check for missing expected columns
        for col in expected_columns:
            if col not in transformed_df.columns:
                validation_results['missing_columns'].append(col)
        
        # Check data quality
        for col in transformed_df.columns:
            null_percentage = transformed_df[col].isnull().sum() / len(transformed_df)
            if null_percentage > 0.5:  # More than 50% nulls
                validation_results['data_quality_issues'].append(f"{col}: {null_percentage:.1%} null values")
        
        # Print validation summary
        print(f"      📊 Validation Summary:")
        print(f"         Records: {validation_results['original_records']} → {validation_results['transformed_records']}")
        print(f"         Columns: {validation_results['actual_columns']}/{validation_results['expected_columns']}")
        
        if validation_results['missing_columns']:
            print(f"         ⚠️  Missing columns: {validation_results['missing_columns']}")
        
        if validation_results['data_quality_issues']:
            print(f"         ⚠️  Data quality issues: {validation_results['data_quality_issues']}")
        
        return validation_results

    def transform_api_data_to_file_format(
        self,
        allocations_df: pd.DataFrame,
        clients_df: pd.DataFrame,
        people_df: pd.DataFrame,
        projects_df: pd.DataFrame,
        duplicate_strategy: str = 'business_logic'
    ) -> Dict[str, pd.DataFrame]:
        """Complete transformation from API format to file format"""
        print("🚀 Starting Comprehensive API to File Format Transformation")
        print("=" * 60)
        
        try:
            # Transform each data type
            transformed_data = {}
            
            # Transform clients
            print("\n📊 TRANSFORMING CLIENTS")
            print("-" * 40)
            transformed_clients = self.transform_clients(clients_df)
            transformed_data['clients'] = transformed_clients
            
            # Transform people  
            print("\n📊 TRANSFORMING PEOPLE")
            print("-" * 40)
            transformed_people = self.transform_people(people_df)
            transformed_data['people'] = transformed_people
            
            # Transform projects
            print("\n📊 TRANSFORMING PROJECTS")
            print("-" * 40)
            transformed_projects = self.transform_projects(projects_df, transformed_clients)
            transformed_data['projects'] = transformed_projects
            
            # Transform allocations
            print("\n📊 TRANSFORMING ALLOCATIONS")
            print("-" * 40)
            
            # Step 1: Transform dates
            date_columns = ['StartDate', 'EndDate']
            transformed_df = self.transform_dates(allocations_df, date_columns)
            
            # Step 2: Enrich with related data (use original API data for joining)
            enriched_df = self.enrich_allocations_with_related_data(
                transformed_df, clients_df, people_df, projects_df
            )
            
            # Step 3: Create expected column structure
            result_df = self.create_expected_allocation_columns(enriched_df)
            
            # Step 4: Standardize data types
            result_df = self.standardize_data_types(result_df, 'allocations')
            
            # Step 5: Handle duplicates
            result_df = self.handle_duplicates(result_df, duplicate_strategy)
            
            # Step 6: Validate transformation
            validation_results = self.validate_transformation(allocations_df, result_df, 'allocations')
            
            transformed_data['allocations'] = result_df
            
            print(f"\n✅ Comprehensive transformation completed successfully!")
            print(f"   📊 Clients: {len(transformed_data['clients'])} records")
            print(f"   📊 People: {len(transformed_data['people'])} records") 
            print(f"   📊 Projects: {len(transformed_data['projects'])} records")
            print(f"   📊 Allocations: {len(transformed_data['allocations'])} records")
            
            return transformed_data
            
        except Exception as e:
            print(f"❌ Transformation failed: {e}")
            import traceback
            traceback.print_exc()
            return {}

def main():
    """Test the data transformer"""
    print("🧪 Testing Enhanced ElapseIT Data Transformer")
    print("=" * 50)
    
    # This is a test function - in practice, this would be called from other scripts
    transformer = ElapseITDataTransformer()
    
    print("✅ Transformer initialized successfully")
    print("📋 Available methods:")
    print("   - transform_dates()")
    print("   - transform_clients()")
    print("   - transform_people()")
    print("   - transform_projects()")
    print("   - enrich_allocations_with_related_data()")
    print("   - create_expected_allocation_columns()")
    print("   - handle_duplicates()")
    print("   - validate_transformation()")
    print("   - transform_api_data_to_file_format()")
    
    print("\n🔧 Usage:")
    print("   transformer = ElapseITDataTransformer()")
    print("   transformed_data = transformer.transform_api_data_to_file_format(")
    print("       allocations_df, clients_df, people_df, projects_df")
    print("   )")

if __name__ == "__main__":
    main()