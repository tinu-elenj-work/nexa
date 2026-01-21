import pandas as pd
import os
from pathlib import Path
from datetime import datetime
import calendar
import re
import argparse

# Import our new API infrastructure
from elapseit_api_client import ElapseITAPIClient
from data_transformer import ElapseITDataTransformer
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from config import ELAPSEIT_CONFIG

def read_excel_file(file_path, sheet_name=0):
    """Read Excel file with error handling"""
    try:
        # Try to read the file
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        return df
    except PermissionError:
        print(f"Permission denied for {file_path}. Please close the file if it's open in Excel.")
        return None
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None

def read_csv_file(file_path):
    """Read CSV file with error handling"""
    # Try different encodings
    encodings_to_try = ['utf-8', 'utf-16', 'latin-1', 'cp1252', 'iso-8859-1']
    
    for encoding in encodings_to_try:
        try:
            df = pd.read_csv(file_path, encoding=encoding)
            return df
        except Exception as e:
            continue
    
    print(f"Error reading {file_path}: All encoding attempts failed")
    return None

def get_elapseit_data_from_api():
    """Retrieve ElapseIT data from API using our data transformer"""
    print("🌐 Retrieving ElapseIT data from API...")
    
    try:
        # Initialize API client
        client = ElapseITAPIClient(
            domain=ELAPSEIT_CONFIG['domain'],
            username=ELAPSEIT_CONFIG['username'],
            password=ELAPSEIT_CONFIG['password'],
            timezone=ELAPSEIT_CONFIG['timezone']
        )
        
        # Authenticate
        if not client.authenticate():
            print("❌ API authentication failed!")
            return None
        
        print("✅ API authentication successful!")
        
        # Retrieve all data types
        api_data = {}
        
        # Get clients
        print("📊 Retrieving clients...")
        clients = client.get_clients()
        if clients and len(clients) > 0:
            api_data['clients'] = pd.DataFrame(clients)
            print(f"   ✅ Retrieved {len(clients)} clients")
        else:
            print("   ❌ Failed to retrieve clients")
            return None
        
        # Get people
        print("👥 Retrieving people...")
        people = client.get_people()
        if people and len(people) > 0:
            api_data['people'] = pd.DataFrame(people)
            print(f"   ✅ Retrieved {len(people)} people")
        else:
            print("   ❌ Failed to retrieve people")
            return None
        
        # Get projects
        print("📋 Retrieving projects...")
        projects = client.get_projects()
        if projects and len(projects) > 0:
            api_data['projects'] = pd.DataFrame(projects)
            print(f"   ✅ Retrieved {len(projects)} projects")
        else:
            print("   ❌ Failed to retrieve projects")
            return None
        
        # Get allocations
        print("📊 Retrieving allocations...")
        allocations = client.get_allocations()
        if allocations and len(allocations) > 0:
            api_data['allocations'] = pd.DataFrame(allocations)
            print(f"   ✅ Retrieved {len(allocations)} allocations")
        else:
            print("   ❌ Failed to retrieve allocations")
            return None
        
        client.close()
        
        # Transform API data to match expected format
        print("\n🔄 Transforming API data to match expected format...")
        transformer = ElapseITDataTransformer()
        
        transformed_data = transformer.transform_api_data_to_file_format(
            api_data['allocations'],
            api_data['clients'],
            api_data['people'],
            api_data['projects'],
            duplicate_strategy='business_logic'
        )
        
        if not transformed_data or 'allocations' not in transformed_data:
            print("❌ API data transformation failed!")
            return None
        
        transformed_allocations = transformed_data['allocations']
        print(f"✅ API data transformed successfully!")
        print(f"   📊 Records: {len(transformed_allocations)}")
        print(f"   📋 Columns: {len(transformed_allocations.columns)}")
        
        # Debug: Print actual column names from transformer
        print(f"   🔍 Debug: Transformed columns: {list(transformed_allocations.columns)}")
        
        # The data transformer already produces the correct structure
        # Just use the transformed data directly
        print(f"   🔍 Debug: Using transformer output directly")
        
        return {
            'allocations': transformed_allocations,
            'clients': transformed_data['clients'],
            'people': transformed_data['people'],
            'projects': transformed_data['projects']
        }
        
    except Exception as e:
        print(f"❌ Error retrieving API data: {e}")
        import traceback
        traceback.print_exc()
        return None

def get_max_simulation_id():
    """Get the maximum available simulation ID from the Vision database"""
    try:
        from vision_db_client import create_vision_client
        
        print("🔍 Connecting to Vision database to detect maximum simulation ID...")
        
        # Create database client
        db_client = create_vision_client()
        if not db_client.test_connection():
            raise Exception("Failed to connect to Vision database")
        
        print("✅ Database connection successful, querying for maximum simulation ID...")
        
        # Get maximum simulation ID
        max_sim_id = db_client.get_max_simulation_id()
        print(f"🎯 Maximum simulation ID found: {max_sim_id}")
        return max_sim_id
        
    except Exception as e:
        print(f"⚠️  Warning: Could not get maximum simulation ID: {e}")
        print("   Falling back to default simulation ID: 28")
        return 28

def get_vision_data_from_database(start_date=None, end_date=None, simulation_id=None):
    """Get Vision data from PostgreSQL database instead of CSV files"""
    print("🗄️ Retrieving Vision data from database...")
    
    # If no simulation_id provided, get the maximum available one
    if simulation_id is None:
        print("🔍 No simulation ID provided, auto-detecting maximum available...")
        simulation_id = get_max_simulation_id()
        print(f"✅ Auto-detected simulation_id: {simulation_id}")
    else:
        print(f"🎯 Using provided simulation_id: {simulation_id}")
    
    try:
        from vision_db_client import create_vision_client
        
        # Create database client
        db_client = create_vision_client()
        if not db_client.test_connection():
            raise Exception("Failed to connect to Vision database")
        
        # Get data with simulation_id filter
        print(f"🔍 Querying database for simulation_id: {simulation_id}")
        allocations = db_client.get_allocations(start_date, end_date, simulation_id)
        
        print(f"📊 Retrieved (simulation_id={simulation_id}): {len(allocations)} allocations from database")
        
        # Transform to match the CSV format that the existing logic expects
        vision_allocations = allocations.copy()
        
        # Rename columns to match original CSV format expected by the existing logic
        column_mapping = {
            'employee_name': 'employee',
            'project_name': 'project', 
            'client_name': 'client',
            'start_date': 'project_start_date',  # Rename to match expected column name
            'end_date': 'project_end_date',      # Rename to match expected column name
            'allocation_percent': 'allocation_percent'
        }
        
        for old_col, new_col in column_mapping.items():
            if old_col in vision_allocations.columns:
                vision_allocations[new_col] = vision_allocations[old_col]
        
        # Ensure allocation_percent is in percentage format (0-100)
        if 'allocation_percent' in vision_allocations.columns:
            max_allocation = vision_allocations['allocation_percent'].max()
            if max_allocation <= 1.0:
                vision_allocations['allocation_percent'] = vision_allocations['allocation_percent'] * 100
        
        print("✅ Vision database data retrieved and formatted")
        return vision_allocations
        
    except Exception as e:
        print(f"❌ Error getting Vision data from database: {e}")
        raise

def get_elapseit_data_from_files():
    """Load ElapseIT data from existing CSV files"""
    print("📁 Loading ElapseIT data from CSV files...")
    
    try:
        # Read ElapseIT CSV files
        allocations_df = read_csv_file("../data/elapseIT_data/allocations.csv")
        clients_df = read_csv_file("../data/elapseIT_data/clients.csv")
        people_df = read_csv_file("../data/elapseIT_data/people.csv")
        projects_df = read_csv_file("../data/elapseIT_data/projects.csv")
        
        if all([allocations_df is not None, clients_df is not None, 
                people_df is not None, projects_df is not None]):
            print("✅ All ElapseIT CSV files loaded successfully")
            return {
                'allocations': allocations_df,
                'clients': clients_df,
                'people': people_df,
                'projects': projects_df
            }
        else:
            print("❌ Failed to load one or more ElapseIT CSV files")
            return None
            
    except Exception as e:
        print(f"❌ Error loading CSV data: {e}")
        return None

def filter_projects_by_month(projects_df, resourcing_df, month_year="July 2025"):
    """Filter projects and resourcing data for a specific month"""
    
    print(f"\n{'='*60}")
    print(f"FILTERING PROJECTS FOR {month_year.upper()}")
    print(f"{'='*60}")
    
    # Parse month and year
    month_name, year_str = month_year.split()
    
    # Handle abbreviated month names
    month_abbrev_to_full = {
        'jan': 'January', 'feb': 'February', 'mar': 'March', 'apr': 'April',
        'may': 'May', 'jun': 'June', 'jul': 'July', 'aug': 'August',
        'sep': 'September', 'oct': 'October', 'nov': 'November', 'dec': 'December'
    }
    
    # Convert abbreviation to full name if needed
    month_name_lower = month_name.lower()
    if month_name_lower in month_abbrev_to_full:
        month_name = month_abbrev_to_full[month_name_lower]
    
    month_num = list(calendar.month_name).index(month_name)
    year = int(year_str)
    
    # Create date range for the month
    start_date = pd.Timestamp(year, month_num, 1)
    end_date = pd.Timestamp(year, month_num, calendar.monthrange(year, month_num)[1])
    
    print(f"📅 Date range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    
    # Convert date columns to datetime for comparison
    # Check if this is Vision data (has project_start_date) or ElapseIT data (has From Date)
    if 'project_start_date' in projects_df.columns:
        # This is Vision data
        projects_df['project_start_date'] = pd.to_datetime(projects_df['project_start_date'], errors='coerce')
        projects_df['project_end_date'] = pd.to_datetime(projects_df['project_end_date'], errors='coerce')
        
        # Filter Vision projects for the month
        vision_filtered = projects_df[
            (projects_df['project_start_date'] <= end_date) & 
            (projects_df['project_end_date'] >= start_date)
        ].copy()
    else:
        # This is ElapseIT data (already processed)
        vision_filtered = projects_df.copy()
    
    # Convert ElapseIT date columns
    resourcing_df['From Date'] = pd.to_datetime(resourcing_df['From Date'], errors='coerce')
    resourcing_df['To Date'] = pd.to_datetime(resourcing_df['To Date'], errors='coerce')
    
    # Filter ElapseIT resourcing for the month
    resourcing_filtered = resourcing_df[
        (resourcing_df['From Date'] <= end_date) & 
        (resourcing_df['To Date'] >= start_date)
    ].copy()
    
    print(f"📊 FILTERED PROJECTS:")
    print(f"  Vision projects in {month_year}: {len(vision_filtered)}")
    print(f"  ElapseIT allocations in {month_year}: {len(resourcing_filtered)}")
    
    return vision_filtered, resourcing_filtered

def create_client_mapping(mapper_df):
    """Create a mapping dictionary from the mapper file"""
    mapping = {}
    
    for _, row in mapper_df.iterrows():
        elapseit_client = str(row['ElapseIT']).strip()
        vision_client = str(row['Vision']).strip()
        override = str(row['Override']).strip() if pd.notna(row['Override']) else None
        
        if override and override != 'nan':
            # Use override if provided
            mapping[elapseit_client] = override
        elif vision_client and vision_client != 'nan' and vision_client != '0':
            # Use Vision mapping
            mapping[elapseit_client] = vision_client
        # No else clause - if no mapping is defined, don't add to mapping dict
    
    return mapping

def process_elapseit_csv_data(allocations_df, clients_df, people_df, projects_df):
    """Process ElapseIT CSV data into the format expected by existing logic"""
    
    print(f"\n{'='*60}")
    print(f"PROCESSING ELAPSEIT CSV DATA")
    print(f"{'='*60}")
    
    # Filter out archived records
    allocations_df = allocations_df[allocations_df['IsArchived'] == False] if 'IsArchived' in allocations_df.columns else allocations_df
    people_df = people_df[people_df['IsArchived'] == False] if 'IsArchived' in people_df.columns else people_df
    projects_df = projects_df[projects_df['IsArchived'] == False] if 'IsArchived' in projects_df.columns else projects_df
    
    # Filter out resigned employees (HasLicense = FALSE)
    print(f"  🔍 Debug: People columns: {list(people_df.columns)}")
    print(f"  🔍 Debug: HasLicense values: {people_df['HasLicense'].value_counts() if 'HasLicense' in people_df.columns else 'Column not found'}")
    
    active_people_df = people_df[people_df['HasLicense'] == True] if 'HasLicense' in people_df.columns else people_df
    print(f"  Filtered out {len(people_df) - len(active_people_df)} resigned employees (HasLicense = FALSE)")
    
    # Create a set of active employee names for filtering allocations
    active_employee_names = set()
    for _, person in active_people_df.iterrows():
        full_name = f"{person.get('FirstName', '')} {person.get('LastName', '')}".strip()
        active_employee_names.add(full_name)
    
    print(f"  🔍 Debug: Active employee names count: {len(active_employee_names)}")
    print(f"  🔍 Debug: Sample active names: {list(active_employee_names)[:5]}")
    
    # Filter allocations to only include active employees
    print(f"  🔍 Debug: Allocation columns: {list(allocations_df.columns)}")
    
    # Check if this is transformed API data or original CSV data
    if 'Person.FirstName' in allocations_df.columns and 'Person.LastName' in allocations_df.columns:
        # This is transformed API data with the expected structure
        print(f"  🔍 Debug: Using transformed API data structure")
        print(f"  🔍 Debug: Sample allocation names: {allocations_df[['Person.FirstName', 'Person.LastName']].head(5).apply(lambda x: f'{x.iloc[0]} {x.iloc[1]}'.strip(), axis=1).tolist()}")
        first_name_col = 'Person.FirstName'
        last_name_col = 'Person.LastName'
    elif 'Person' in allocations_df.columns:
        # This is the enhanced mapper's custom structure
        print(f"  🔍 Debug: Using enhanced mapper structure")
        print(f"  🔍 Debug: Sample allocation names: {allocations_df['Person'].head(5).tolist()}")
        # For this structure, we need to extract first/last names from the Person column
        # We'll handle this in the processing loop
        first_name_col = 'Person'
        last_name_col = 'Person'
    else:
        print(f"  ❌ Unexpected column structure")
        print(f"  🔍 Available columns: {list(allocations_df.columns)}")
        return pd.DataFrame()
    
    # Filter allocations based on the detected structure
    if first_name_col == 'Person' and last_name_col == 'Person':
        # For the enhanced mapper structure, filter by the Person column directly
        active_allocations_df = allocations_df[
            allocations_df['Person'].isin(active_employee_names)
        ]
    else:
        # For the transformed API structure, filter by concatenated names
        active_allocations_df = allocations_df[
            allocations_df.apply(lambda row: f"{row.get(first_name_col, '')} {row.get(last_name_col, '')}".strip() in active_employee_names, axis=1)
        ]
    print(f"  Filtered allocations from {len(allocations_df)} to {len(active_allocations_df)} (active employees only)")
    
    # Create a processed dataframe that matches the expected format
    print(f"  🔄 Processing {len(active_allocations_df)} allocation records...")
    
    # Use vectorized operations for better performance instead of iterating
    processed_df = active_allocations_df.copy()
    
    # Create person name column based on the structure
    if first_name_col == 'Person' and last_name_col == 'Person':
        # Enhanced mapper structure - already have 'Person' column
        pass  # No change needed
    else:
        # Transformed API structure - combine first and last names
        processed_df['Person'] = (processed_df[first_name_col].astype(str) + ' ' + processed_df[last_name_col].astype(str)).str.strip()
    
    # Get project and client info based on the structure
    if 'Project.Code' in processed_df.columns and 'Project.Name' in processed_df.columns:
        # Transformed API structure - already have project and client info
        processed_df['Project'] = processed_df['Project.Name']
        processed_df['Client'] = processed_df['Client.Name']
    else:
        # Enhanced mapper structure - need to extract from existing columns
        # For now, use the existing values as-is (this would need optimization for file-based approach)
        pass
    
    # Get date range based on the structure
    if 'StartDate' in processed_df.columns and 'EndDate' in processed_df.columns:
        # Transformed API structure
        processed_df['From Date'] = processed_df['StartDate']
        processed_df['To Date'] = processed_df['EndDate']
    # else: Enhanced mapper structure already has 'From Date' and 'To Date'
    
    # Get hours and days based on the structure
    if 'HoursPerDay' in processed_df.columns and 'BusinessDays' in processed_df.columns:
        # Transformed API structure - already have these columns
        pass
    else:
        # Enhanced mapper structure
        processed_df['HoursPerDay'] = processed_df.get('Hours Per Day', 0)
        processed_df['BusinessDays'] = processed_df.get('Business Days', 0)
    
    # Keep only the expected columns in the correct format
    expected_columns = ['Person', 'Project', 'Client', 'From Date', 'To Date', 'HoursPerDay', 'BusinessDays']
    available_expected_columns = [col for col in expected_columns if col in processed_df.columns]
    processed_df = processed_df[available_expected_columns]
    
    print(f"✅ Processed {len(processed_df)} ElapseIT allocations")
    print(f"  Unique people: {processed_df['Person'].nunique()}")
    print(f"  Unique projects: {processed_df['Project'].nunique()}")
    print(f"  Unique clients: {processed_df['Client'].nunique()}")
    
    return processed_df

def process_vision_csv_data(allocations_df, clients_df, employees_df, projects_df):
    """Process Vision CSV data into the format expected by existing logic"""
    
    print(f"\n{'='*60}")
    print(f"PROCESSING VISION CSV DATA")
    print(f"{'='*60}")
    
    # Filter out archived records
    allocations_df = allocations_df[allocations_df['deleted_at'].isna()] if 'deleted_at' in allocations_df.columns else allocations_df
    employees_df = employees_df[employees_df['deleted_at'].isna()] if 'deleted_at' in employees_df.columns else employees_df
    projects_df = projects_df[projects_df['deleted_at'].isna()] if 'deleted_at' in projects_df.columns else projects_df
    
    # Create a processed dataframe that matches the expected format
    processed_data = []
    
    for _, allocation in allocations_df.iterrows():
        # Get employee info
        employee_id = allocation.get('employee_id', '')
        employee_info = employees_df[employees_df['id'] == employee_id]
        
        if not employee_info.empty:
            employee = employee_info.iloc[0]
            employee_name = f"{employee.get('first_name', '')} {employee.get('last_name', '')}".strip()
        else:
            employee_name = f"Unknown Employee {employee_id}"
        
        # Get project info
        project_id = allocation.get('project_id', '')
        project_info = projects_df[projects_df['id'] == project_id]
        
        if not project_info.empty:
            project = project_info.iloc[0]
            project_name = project.get('name', '')
            
            # Get client info
            client_id = project.get('client_id', '')
            client_info = clients_df[clients_df['id'] == client_id]
            
            if not client_info.empty:
                client = client_info.iloc[0]
                client_name = client.get('name', '')
            else:
                client_name = f"Unknown Client {client_id}"
        else:
            project_name = f"Unknown Project {project_id}"
            client_name = f"Unknown Client"
        
        # Get date range
        start_date = allocation.get('start_date', '')
        end_date = allocation.get('end_date', '')
        
        # Create row in expected format
        processed_data.append({
            'employee': employee_name,
            'project': project_name,
            'client': client_name,
            'project_start_date': start_date,
            'project_end_date': end_date,
            'allocation_percent': allocation.get('allocation_percent', 0)
        })
    
    processed_df = pd.DataFrame(processed_data)
    
    print(f"✅ Processed {len(processed_df)} Vision allocations")
    print(f"  Unique employees: {processed_df['employee'].nunique()}")
    print(f"  Unique projects: {processed_df['project'].nunique()}")
    print(f"  Unique clients: {processed_df['client'].nunique()}")
    
    return processed_df

def perform_bidirectional_composite_key_matching(elapseit_df, vision_df, client_mapping, field_mappings_config=None, elapseit_data=None):
    """Perform bidirectional composite key matching using configurable field mappings"""
    
    print(f"\n{'='*60}")
    print(f"BIDIRECTIONAL COMPOSITE KEY MATCHING")
    print(f"{'='*60}")
    
    # Use configurable field mappings or fall back to hardcoded defaults
    if field_mappings_config:
        field_mappings = field_mappings_config['field_mappings']
        composite_keys = field_mappings_config['composite_keys']
        client_extraction_rules = field_mappings_config['client_extraction_rules']
        
        # Get field names from mappings
        elapseit_person_field = list(field_mappings.keys())[0]  # First mapping is Person
        vision_employee_field = list(field_mappings.values())[0]  # First mapping is employee
        elapseit_project_field = list(field_mappings.keys())[1]  # Second mapping is Project
        vision_project_field = list(field_mappings.values())[1]  # Second mapping is project
        
        # Get composite key formulas
        elapseit_composite_formula = composite_keys.get('ElapseIT', 'Person.Client')
        vision_composite_formula = composite_keys.get('Vision', 'employee.client')
        
        print(f"✅ Using configurable field mappings")
        print(f"  ElapseIT Person Field: {elapseit_person_field}")
        print(f"  Vision Employee Field: {vision_employee_field}")
        print(f"  ElapseIT Composite Formula: {elapseit_composite_formula}")
        print(f"  Vision Composite Formula: {vision_composite_formula}")
    else:
        # Fall back to hardcoded defaults
        elapseit_person_field = 'Person'
        vision_employee_field = 'employee'
        elapseit_project_field = 'Project'
        vision_project_field = 'project'
        elapseit_composite_formula = 'Person.Client'
        vision_composite_formula = 'employee.client'
        
        print(f"⚠️  Using hardcoded field mappings")
    
    # Step 1: Create composite keys
    print("\nStep 1: Creating composite keys...")
    
    # Extract client from Project field using configurable rules or default
    if field_mappings_config and 'ElapseIT' in client_extraction_rules:
        # Use configurable client extraction
        extraction_rule = client_extraction_rules['ElapseIT']
        if extraction_rule['method'] == 'Split by pipe delimiter':
            elapseit_df['Client'] = elapseit_df[elapseit_project_field].astype(str).str.split('|').str[0]
        print(f"ℹ️  Using configurable client extraction: {extraction_rule['method']}")
    else:
        # Default client extraction
        elapseit_df['Client'] = elapseit_df[elapseit_project_field].astype(str).str.split('|').str[0]
        print("ℹ️  Using default client extraction (split by pipe delimiter)")
    
    # Create composite keys using configurable formulas
    if field_mappings_config:
        # Parse composite key formula and create the key
        elapseit_parts = elapseit_composite_formula.split('.')
        vision_parts = vision_composite_formula.split('.')
        
        # ElapseIT composite key
        elapseit_df['Composite_Key'] = (
            elapseit_df[elapseit_parts[0]].astype(str) + '.' + 
            elapseit_df[elapseit_parts[1]].astype(str)
        )
        
        # Vision composite key
        vision_df['Composite_Key'] = (
            vision_df[vision_parts[0]].astype(str) + '.' + 
            vision_df[vision_parts[1]].astype(str)
        )
    else:
        # Default composite key creation
        elapseit_df['Composite_Key'] = elapseit_df[elapseit_person_field].astype(str) + '.' + elapseit_df['Client'].astype(str)
        vision_df['Composite_Key'] = vision_df[vision_employee_field].astype(str) + '.' + vision_df['client'].astype(str)
    
    print(f"  ElapseIT unique composite keys: {elapseit_df['Composite_Key'].nunique()}")
    print(f"  Vision unique composite keys: {vision_df['Composite_Key'].nunique()}")
    
    # Step 2: Create mapped composite keys using client mapping
    print("\nStep 2: Creating mapped composite keys using client mapping...")
    
    # ElapseIT → Vision mapping (using extracted client)
    elapseit_df['Mapped_Composite_Key'] = elapseit_df[elapseit_person_field].astype(str) + '.' + elapseit_df['Client'].map(client_mapping).astype(str)
    
    # Vision → ElapseIT mapping (reverse mapping)
    # Handle cases where multiple keys map to the same value by choosing the most appropriate one
    reverse_client_mapping = {}
    for k, v in client_mapping.items():
        if v not in reverse_client_mapping:
            # Prefer keys without spaces (e.g., "D360" over "D360 Bank")
            reverse_client_mapping[v] = k
        elif ' ' not in k and ' ' in reverse_client_mapping[v]:
            # If current key has no spaces and existing key has spaces, prefer the one without spaces
            reverse_client_mapping[v] = k
        elif len(k) < len(reverse_client_mapping[v]):
            # If current key is shorter, prefer it
            reverse_client_mapping[v] = k
    
    vision_df['Mapped_Composite_Key'] = vision_df[vision_employee_field].astype(str) + '.' + vision_df['client'].map(reverse_client_mapping).astype(str)
    
    # Step 3: Perform bidirectional matching
    print("\nStep 3: Performing bidirectional matching...")
    
    # ElapseIT → Vision matches
    elapseit_to_vision = {}
    for _, row in elapseit_df.iterrows():
        mapped_key = row['Mapped_Composite_Key']
        if pd.notna(mapped_key):
            matching_vision = vision_df[vision_df['Composite_Key'] == mapped_key]
            if not matching_vision.empty:
                elapseit_to_vision[row['Composite_Key']] = matching_vision['Composite_Key'].tolist()
    
    # Vision → ElapseIT matches
    vision_to_elapseit = {}
    for _, row in vision_df.iterrows():
        mapped_key = row['Mapped_Composite_Key']
        if pd.notna(mapped_key):
            matching_elapseit = elapseit_df[elapseit_df['Composite_Key'] == mapped_key]
            if not matching_elapseit.empty:
                vision_to_elapseit[row['Composite_Key']] = matching_elapseit['Composite_Key'].tolist()
    
    # Step 4: Analyze results
    print("\nStep 4: Analyzing bidirectional matches...")
    
    # Find bidirectional matches (both ways match)
    bidirectional_matches = []
    seen_combinations = set()
    for elapseit_key, vision_matches in elapseit_to_vision.items():
        for vision_key in vision_matches:
            # Check if this vision key also maps back to the elapseit key
            if vision_key in vision_to_elapseit and elapseit_key in vision_to_elapseit[vision_key]:
                # Only add if we haven't seen this combination before
                combination = f"{elapseit_key}|{vision_key}"
                if combination not in seen_combinations:
                    seen_combinations.add(combination)
                    bidirectional_matches.append({
                        'elapseit_key': elapseit_key,
                        'vision_key': vision_key,
                        'match_type': 'bidirectional'
                    })
    
    # Find one-way matches
    elapseit_only_matches = []
    for elapseit_key, vision_matches in elapseit_to_vision.items():
        for vision_key in vision_matches:
            # Check if this is NOT a bidirectional match
            if not any(match['elapseit_key'] == elapseit_key and match['vision_key'] == vision_key 
                      for match in bidirectional_matches):
                elapseit_only_matches.append({
                    'elapseit_key': elapseit_key,
                    'vision_key': vision_key,
                    'match_type': 'elapseit_to_vision_only'
                })
    
    vision_only_matches = []
    for vision_key, elapseit_matches in vision_to_elapseit.items():
        for elapseit_key in elapseit_matches:
            # Check if this is NOT a bidirectional match
            if not any(match['elapseit_key'] == elapseit_key and match['vision_key'] == vision_key 
                      for match in bidirectional_matches):
                vision_only_matches.append({
                    'elapseit_key': elapseit_key,
                    'vision_key': vision_key,
                    'match_type': 'vision_to_elapseit_only'
                })
    
    # Find entries with no matches
    elapseit_keys_with_matches = set()
    for match in bidirectional_matches + elapseit_only_matches:
        elapseit_keys_with_matches.add(match['elapseit_key'])
    
    vision_keys_with_matches = set()
    for match in bidirectional_matches + vision_only_matches:
        vision_keys_with_matches.add(match['vision_key'])
    
    # Filter out BACKLOG ALLOCATIONS from elapseit_no_matches (these are leave adjustments)
    all_elapseit_keys = set(elapseit_df['Composite_Key'].unique())
    backlog_keys = set()
    for key in all_elapseit_keys:
        if 'BACKLOG ALLOCATIONS' in key:
            backlog_keys.add(key)
    
    elapseit_no_matches = (all_elapseit_keys - elapseit_keys_with_matches) - backlog_keys
    vision_no_matches = set(vision_df['Composite_Key'].unique()) - vision_keys_with_matches
    
    return {
        'bidirectional_matches': bidirectional_matches,
        'elapseit_only_matches': elapseit_only_matches,
        'vision_only_matches': vision_only_matches,
        'elapseit_no_matches': list(elapseit_no_matches),
        'vision_no_matches': list(vision_no_matches),
        'elapseit_df': elapseit_df,
        'vision_df': vision_df,
        'elapseit_data': elapseit_data
    }





def print_bidirectional_summary(results, month_year, employee_filter=None):
    """Print summary of bidirectional matching results"""
    
    print(f"\n{'='*60}")
    if employee_filter:
        print(f"BIDIRECTIONAL MATCHING SUMMARY FOR {month_year.upper()} - EMPLOYEE: {employee_filter}")
    else:
        print(f"BIDIRECTIONAL MATCHING SUMMARY FOR {month_year.upper()}")
    print(f"{'='*60}")
    
    bidirectional_matches = results['bidirectional_matches']
    elapseit_only_matches = results['elapseit_only_matches']
    vision_only_matches = results['vision_only_matches']
    elapseit_no_matches = results['elapseit_no_matches']
    vision_no_matches = results['vision_no_matches']
    
    print(f"📊 EXACT MATCHING STATISTICS:")
    if employee_filter:
        print(f"  👤 Employee Filter: {employee_filter}")
    print(f"  ✅ Bidirectional exact matches: {len(bidirectional_matches)}")
    print(f"  ⚠️  ElapseIT→Vision only: {len(elapseit_only_matches)}")
    print(f"  ⚠️  Vision→ElapseIT only: {len(vision_only_matches)}")
    print(f"  ❌ ElapseIT no matches: {len(elapseit_no_matches)} (excluding BACKLOG ALLOCATIONS)")
    print(f"  ❌ Vision no matches: {len(vision_no_matches)}")
    
    if bidirectional_matches:
        print(f"\n✅ TOP BIDIRECTIONAL EXACT MATCHES ({len(bidirectional_matches)}):")
        for i, match in enumerate(bidirectional_matches[:10], 1):
            elapseit_parts = match['elapseit_key'].split('.')
            vision_parts = match['vision_key'].split('.')
            print(f"  {i:2d}. {elapseit_parts[0]} ({elapseit_parts[1]}) ↔ {vision_parts[0]} ({vision_parts[1]})")
        if len(bidirectional_matches) > 10:
            print(f"     ... and {len(bidirectional_matches) - 10} more exact matches")

def read_field_mappings(file_path="../config/field_mappings.xlsx"):
    """Read field mappings from the configurable Excel file"""
    try:
        # Read field mappings
        field_mappings_df = pd.read_excel(file_path, sheet_name='Field_Mappings')
        composite_keys_df = pd.read_excel(file_path, sheet_name='Composite_Keys')
        client_extraction_df = pd.read_excel(file_path, sheet_name='Client_Extraction')
        multimatcher_df = pd.read_excel(file_path, sheet_name='Multimatcher')
        
        # Create field mapping dictionary
        field_mappings = {}
        for _, row in field_mappings_df.iterrows():
            if row['Is_Active'] == 'Yes':
                field_mappings[row['ElapseIT_Field']] = row['Vision_Field']
        
        # Get composite keys (all active ones)
        composite_keys = {}
        for _, row in composite_keys_df.iterrows():
            if row['Is_Active'] == 'Yes':
                composite_keys[row['System']] = row['Composite_Key_Formula']
        
        # Get client extraction rules
        client_extraction_rules = {}
        for _, row in client_extraction_df.iterrows():
            if row['Is_Active'] == 'Yes':
                client_extraction_rules[row['System']] = {
                    'field': row['Field_Name'],
                    'method': row['Extraction_Method'],
                    'formula': row['Extraction_Formula']
                }
        
        # Get multimatcher rules
        multimatcher_rules = []
        for _, row in multimatcher_df.iterrows():
            if row['Is_Active'] == 'Yes':
                multimatcher_rules.append({
                    'elapseit_project': row['ElapseIT_Project'],
                    'vision_project': row['Vision_Project'],
                    'description': row['Description']
                })
        
        return {
            'field_mappings': field_mappings,
            'composite_keys': composite_keys,
            'client_extraction_rules': client_extraction_rules,
            'multimatcher_rules': multimatcher_rules
        }
    except Exception as e:
        print(f"⚠️  Warning: Could not read field mappings from {file_path}: {e}")
        print("Using default hardcoded mappings...")
        return None

def perform_second_pass_multimatcher_mapping(bidirectional_data, multimatcher_rules):
    """Perform second pass mapping using multimatcher rules to break down MULTIMATCH entries"""
    
    print(f"\n🔄 PERFORMING SECOND PASS MULTIMATCHER MAPPING")
    print(f"{'='*60}")
    
    if not multimatcher_rules:
        print("⚠️  No multimatcher rules found. Skipping second pass.")
        return bidirectional_data
    
    print(f"📋 Found {len(multimatcher_rules)} multimatcher rules")
    
    # Create a lookup dictionary for quick rule matching
    rule_lookup = {}
    for rule in multimatcher_rules:
        rule_lookup[rule['elapseit_project']] = rule['vision_project']
    
    print(f"🔍 Rule lookup created with {len(rule_lookup)} mappings")
    
    # Process each MULTIMATCH entry
    new_entries = []
    processed_multimatches = 0
    entries_to_remove = []
    
    for i, entry in enumerate(bidirectional_data):
        if entry['Status'] == 'MULTIMATCH':
            processed_multimatches += 1
            print(f"\n📊 Processing MULTIMATCH entry: {entry['ElapseIT_Person']} - {entry['ElapseIT_Client']}")
            
            # Split the dash-delimited project lists
            elapseit_projects = entry['ElapseIT_Project'].split('-')
            vision_projects = entry['Vision_project'].split('-')
            
            print(f"  ElapseIT projects: {elapseit_projects}")
            print(f"  Vision projects: {vision_projects}")
            
            # Track which projects are mapped
            mapped_projects = []
            unmapped_projects = []
            
            # Create individual MATCH entries for each rule match
            for elapseit_project in elapseit_projects:
                if elapseit_project in rule_lookup:
                    vision_project = rule_lookup[elapseit_project]
                    print(f"  ✅ Rule match: {elapseit_project} → {vision_project}")
                    
                    # Create new entry with single project match
                    new_entry = entry.copy()
                    new_entry['ElapseIT_Project'] = elapseit_project
                    new_entry['Vision_project'] = vision_project
                    new_entry['Status'] = 'MATCH (Multimatcher)'
                    new_entries.append(new_entry)
                    mapped_projects.append(elapseit_project)
                else:
                    print(f"  ⚠️  No rule found for: {elapseit_project}")
                    unmapped_projects.append(elapseit_project)
            
            # Check if all projects are mapped
            if len(unmapped_projects) == 0:
                print(f"  🎯 All projects mapped! Removing original MULTIMATCH entry.")
                entries_to_remove.append(i)
            else:
                print(f"  ⚠️  Some projects unmapped: {unmapped_projects}. Keeping original MULTIMATCH entry.")
    
    print(f"\n📊 SECOND PASS SUMMARY:")
    print(f"  Processed MULTIMATCH entries: {processed_multimatches}")
    print(f"  Created new MATCH entries: {len(new_entries)}")
    print(f"  Removed MULTIMATCH entries: {len(entries_to_remove)}")
    
    # Remove the original MULTIMATCH entries that were fully mapped
    final_data = [entry for i, entry in enumerate(bidirectional_data) if i not in entries_to_remove]
    
    # Add the new MATCH entries
    final_data.extend(new_entries)
    
    return final_data

def print_detailed_matching_commentary(results, client_mapping, debug=False, field_mappings_config=None):
    """Print detailed commentary on the matching process"""
    
    if not debug:
        return
    
    print(f"\n{'='*80}")
    print("DETAILED MATCHING COMMENTARY")
    print(f"{'='*80}")
    
    # Bidirectional matches commentary
    if results['bidirectional_matches']:
        print(f"\n🎯 BIDIRECTIONAL MATCHES ({len(results['bidirectional_matches'])} found):")
        print("-" * 80)
        print("No.,ElapseIT Person,ElapseIT Client,Vision Employee,Vision Client,ElapseIT Projects,Vision Projects,Status")
        print("-" * 80)
        
        # Sort by client, project, employee
        sorted_matches = []
        for match in results['bidirectional_matches']:
            elapseit_parts = match['elapseit_key'].split('.')
            vision_parts = match['vision_key'].split('.')
            
            elapseit_person = elapseit_parts[0]
            elapseit_client = elapseit_parts[1]
            vision_employee = vision_parts[0]
            vision_client = vision_parts[1]
            
            # Get project information from the dataframes
            elapseit_projects = results['elapseit_df'][
                (results['elapseit_df']['Person'] == elapseit_person) & 
                (results['elapseit_df']['Client'] == elapseit_client)
            ]['Project'].unique()
            elapseit_project_list = '-'.join(sorted(elapseit_projects)) if len(elapseit_projects) > 0 else 'No projects'
            
            vision_projects = results['vision_df'][
                (results['vision_df']['employee'] == vision_employee) & 
                (results['vision_df']['client'] == vision_client)
            ]['project'].unique()
            vision_project_list = '-'.join(sorted(vision_projects)) if len(vision_projects) > 0 else 'No projects'
            
            # Create sort key: client, project, employee
            sort_key = (elapseit_client, elapseit_project_list, elapseit_person)
            
            sorted_matches.append({
                'sort_key': sort_key,
                'data': (elapseit_person, elapseit_client, vision_employee, vision_client, 
                        elapseit_project_list, vision_project_list)
            })
        
        # Sort by client, project, employee
        sorted_matches.sort(key=lambda x: x['sort_key'])
        
        for i, match in enumerate(sorted_matches, 1):
            elapseit_person, elapseit_client, vision_employee, vision_client, elapseit_project_list, vision_project_list = match['data']
            
            # Determine status based on number of projects
            elapseit_project_count = len([p for p in elapseit_project_list.split('-') if p != 'No projects'])
            vision_project_count = len([p for p in vision_project_list.split('-') if p != 'No projects'])
            
            if elapseit_project_count > 1 or vision_project_count > 1:
                status = "✅ MULTIMATCH"
            else:
                status = "✅ MATCH"
            
            print(f"{i},{elapseit_person},{elapseit_client},{vision_employee},{vision_client},{elapseit_project_list},{vision_project_list},{status}")
    
    # Second pass multimatcher commentary
    if field_mappings_config and 'multimatcher_rules' in field_mappings_config:
        # Create the same data structure as in create_main_output_file
        bidirectional_data = []
        for match in results['bidirectional_matches']:
            elapseit_parts = match['elapseit_key'].split('.')
            vision_parts = match['vision_key'].split('.')
            
            elapseit_person = elapseit_parts[0]
            elapseit_client = elapseit_parts[1]
            vision_employee = vision_parts[0]
            vision_client = vision_parts[1]
            
            # Get project information from the dataframes
            elapseit_projects = results['elapseit_df'][
                (results['elapseit_df']['Person'] == elapseit_person) & 
                (results['elapseit_df']['Client'] == elapseit_client)
            ]['Project'].unique()
            elapseit_project_list = '-'.join(sorted(elapseit_projects)) if len(elapseit_projects) > 0 else 'No projects'
            
            vision_projects = results['vision_df'][
                (results['vision_df']['employee'] == vision_employee) & 
                (results['vision_df']['client'] == vision_client)
            ]['project'].unique()
            vision_project_list = '-'.join(sorted(vision_projects)) if len(vision_projects) > 0 else 'No projects'
            
            # Determine status based on number of projects
            elapseit_project_count = len([p for p in elapseit_project_list.split('-') if p != 'No projects'])
            vision_project_count = len([p for p in vision_project_list.split('-') if p != 'No projects'])
            
            if elapseit_project_count > 1 or vision_project_count > 1:
                status = "MULTIMATCH"
            else:
                status = "MATCH"
            
            bidirectional_data.append({
                'ElapseIT_Person': elapseit_person,
                'ElapseIT_Client': elapseit_client,
                'ElapseIT_Project': elapseit_project_list,
                'Vision_employee': vision_employee,
                'Vision_client': vision_client,
                'Vision_project': vision_project_list,
                'Status': status
            })
        
        # Apply second pass multimatcher mapping
        second_pass_data = perform_second_pass_multimatcher_mapping(bidirectional_data, field_mappings_config['multimatcher_rules'])
        
        # Show only the new MATCH (Multimatcher) entries
        multimatcher_entries = [entry for entry in second_pass_data if entry['Status'] == 'MATCH (Multimatcher)']
        
        if multimatcher_entries:
            print(f"\n🔄 MATCH (MULTIMATCHER) ENTRIES ({len(multimatcher_entries)} found):")
            print("-" * 80)
            print("No.,ElapseIT Person,ElapseIT Client,Vision Employee,Vision Client,ElapseIT Project,Vision Project,Status")
            print("-" * 80)
            print("")
            
            for i, entry in enumerate(multimatcher_entries, 1):
                print(f"{i},{entry['ElapseIT_Person']},{entry['ElapseIT_Client']},{entry['Vision_employee']},{entry['Vision_client']},{entry['ElapseIT_Project']},{entry['Vision_project']},{entry['Status']}")
        else:
            print(f"\n🔄 MATCH (MULTIMATCHER) ENTRIES (0 found):")
            print("-" * 80)
            print("No entries created.")
    
    # ElapseIT no matches commentary
    if results['elapseit_no_matches']:
        print(f"\n❌ ELAPSEIT NO MATCHES ({len(results['elapseit_no_matches'])} entries):")
        print("-" * 80)
        print("No.,ElapseIT Person,ElapseIT Client,Mapped Vision Client,ElapseIT Projects,Status")
        print("-" * 80)
        print("")
        
        # Sort by client, project, employee
        sorted_no_matches = []
        for key in results['elapseit_no_matches']:
            parts = key.split('.')
            person = parts[0]
            client = parts[1]
            mapped_client = client_mapping.get(client, client)
            
            # Get ElapseIT projects for this person/client combination
            elapseit_projects = results['elapseit_df'][
                (results['elapseit_df']['Person'] == person) & 
                (results['elapseit_df']['Client'] == client)
            ]['Project'].unique()
            elapseit_project_list = '-'.join(sorted(elapseit_projects)) if len(elapseit_projects) > 0 else 'No projects'
            
            # Create sort key: client, project, employee
            sort_key = (client, elapseit_project_list, person)
            
            sorted_no_matches.append({
                'sort_key': sort_key,
                'data': (person, client, mapped_client, elapseit_project_list)
            })
        
        # Sort by client, project, employee
        sorted_no_matches.sort(key=lambda x: x['sort_key'])
        
        for i, entry in enumerate(sorted_no_matches, 1):
            person, client, mapped_client, elapseit_project_list = entry['data']
            print(f"{i},{person},{client},{mapped_client},{elapseit_project_list},❌ NO MATCH")
    
    # Vision no matches commentary
    if results['vision_no_matches']:
        print(f"\n❌ VISION NO MATCHES ({len(results['vision_no_matches'])} entries):")
        print("-" * 80)
        print("No.,Vision Employee,Vision Client,Mapped ElapseIT Client,Vision Projects,Status")
        print("-" * 80)
        print("")
        
        # Sort by client, project, employee
        sorted_vision_no_matches = []
        for key in results['vision_no_matches']:
            parts = key.split('.')
            employee = parts[0]
            client = parts[1]
            
            # Try to find reverse mapping
            reverse_mapped_client = None
            for elapseit_client, vision_client in client_mapping.items():
                if vision_client == client:
                    reverse_mapped_client = elapseit_client
                    break
            
            # Get Vision projects for this employee/client combination
            vision_projects = results['vision_df'][
                (results['vision_df']['employee'] == employee) & 
                (results['vision_df']['client'] == client)
            ]['project'].unique()
            vision_project_list = '-'.join(sorted(vision_projects)) if len(vision_projects) > 0 else 'No projects'
            
            # Create sort key: client, project, employee
            sort_key = (client, vision_project_list, employee)
            
            sorted_vision_no_matches.append({
                'sort_key': sort_key,
                'data': (employee, client, reverse_mapped_client or 'No mapping', vision_project_list)
            })
        
        # Sort by client, project, employee
        sorted_vision_no_matches.sort(key=lambda x: x['sort_key'])
        
        for i, entry in enumerate(sorted_vision_no_matches, 1):
            employee, client, reverse_mapped_client, vision_project_list = entry['data']
            print(f"{i},{employee},{client},{reverse_mapped_client},{vision_project_list},❌ NO MATCH")

def format_excel_sheet(worksheet, df):
    """Format Excel sheet with auto-sized columns and proper styling"""
    from openpyxl.styles import Font, PatternFill
    
    # Auto-size all columns
    for column in worksheet.columns:
        max_length = 0
        column_letter = column[0].column_letter
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = min(max_length + 2, 50)  # Cap at 50 characters
        worksheet.column_dimensions[column_letter].width = adjusted_width
    
    # Format header row
    for cell in worksheet[1]:
        cell.font = Font(bold=True)
        cell.fill = PatternFill(start_color="CCCCCC", end_color="CCCCCC", fill_type="solid")

def create_main_output_file(results, elapseit_df, vision_df, client_mapping, month_year, field_mappings_config=None, employee_filter=None, output_filename=None):
    """Create the main output Excel file with all analysis results"""
    
    # Create filename with employee filter if specified
    if output_filename:
        output_file = f"../output/mapping_results/{output_filename}"
    elif employee_filter:
        safe_employee_name = employee_filter.replace(' ', '_').replace('/', '_').replace('\\', '_')
        output_file = f"../output/mapping_results/mapping_analysis_{month_year.replace(' ', '_')}_{safe_employee_name}.xlsx"
    else:
        output_file = f"../output/mapping_results/mapping_analysis_{month_year.replace(' ', '_')}.xlsx"
    
    # Ensure output directory exists
    import os
    output_dir = os.path.dirname(output_file)
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"\n📊 Creating main output Excel file: {output_file}")
    
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        
        # 1. Bidirectional matches - show joined ElapseIT and Vision data with MULTIMATCH concept
        if results['bidirectional_matches']:
            print(f"  📋 Creating 'bidirectional_matches' sheet with {len(results['bidirectional_matches'])} matches")
            bidirectional_data = []
            
            for match in results['bidirectional_matches']:
                # Get ElapseIT data for this key
                elapseit_rows = elapseit_df[elapseit_df['Composite_Key'] == match['elapseit_key']]
                # Get Vision data for this key
                vision_rows = vision_df[vision_df['Composite_Key'] == match['vision_key']]
                
                if not elapseit_rows.empty and not vision_rows.empty:
                    # Get unique projects for both systems
                    elapseit_projects = sorted(elapseit_rows['Project'].unique())
                    vision_projects = sorted(vision_rows['project'].unique())
                    
                    # Create dash-delimited project lists
                    elapseit_project_list = '-'.join(elapseit_projects) if elapseit_projects else 'No projects'
                    vision_project_list = '-'.join(vision_projects) if vision_projects else 'No projects'
                    
                    # Determine status based on number of projects
                    elapseit_project_count = len([p for p in elapseit_project_list.split('-') if p != 'No projects'])
                    vision_project_count = len([p for p in vision_project_list.split('-') if p != 'No projects'])
                    
                    if elapseit_project_count > 1 or vision_project_count > 1:
                        status = "MULTIMATCH"
                    else:
                        status = "MATCH"
                    
                    # Create consolidated row using first ElapseIT and Vision rows
                    combined_row = {}
                    
                    # Define the desired column order
                    elapseit_columns = ['Person', 'Project', 'Client', 'From Date', 'To Date', 'HoursPerDay', 'BusinessDays', 'Composite_Key', 'Mapped_Composite_Key']
                    vision_columns = ['employee', 'project', 'client', 'project_start_date', 'project_end_date', 'allocation_percent', 'Composite_Key', 'Mapped_Composite_Key']
                    
                    # Add ElapseIT data with prefix in proper order
                    for col in elapseit_columns:
                        if col in elapseit_rows.columns:
                            if col == 'Project':
                                combined_row[f'ElapseIT_{col}'] = elapseit_project_list
                            else:
                                combined_row[f'ElapseIT_{col}'] = elapseit_rows.iloc[0][col]
                    
                    # Add Vision data with prefix in proper order
                    for col in vision_columns:
                        if col in vision_rows.columns:
                            if col == 'project':
                                combined_row[f'Vision_{col}'] = vision_project_list
                            else:
                                combined_row[f'Vision_{col}'] = vision_rows.iloc[0][col]
                    
                    # Add status column
                    combined_row['Status'] = status
                    
                    bidirectional_data.append(combined_row)
            
            # Apply second pass multimatcher mapping if rules are available
            if field_mappings_config and 'multimatcher_rules' in field_mappings_config:
                print(f"  🔄 Applying second pass multimatcher mapping...")
                bidirectional_data = perform_second_pass_multimatcher_mapping(
                    bidirectional_data, 
                    field_mappings_config['multimatcher_rules']
                )
            
            if bidirectional_data:
                bidirectional_df = pd.DataFrame(bidirectional_data)
                
                # Define the desired column order - grouped logically
                desired_columns = [
                    # ElapseIT core fields
                    'ElapseIT_Person', 'ElapseIT_Client', 'ElapseIT_Project',
                    # Vision core fields  
                    'Vision_employee', 'Vision_client', 'Vision_project',
                    # ElapseIT additional fields
                    'ElapseIT_From Date', 'ElapseIT_To Date', 'ElapseIT_HoursPerDay', 'ElapseIT_BusinessDays',
                    'ElapseIT_Composite_Key', 'ElapseIT_Mapped_Composite_Key',
                    # Vision additional fields
                    'Vision_project_start_date', 'Vision_project_end_date', 'Vision_allocation_percent',
                    'Vision_Composite_Key', 'Vision_Mapped_Composite_Key',
                    # Status (at the end)
                    'Status'
                ]
                
                # Reorder columns to match desired order (only include columns that exist)
                available_columns = [col for col in desired_columns if col in bidirectional_df.columns]
                bidirectional_df = bidirectional_df[available_columns]
                
                # Sort by ElapseIT_Client, ElapseIT_Project, ElapseIT_Person (if columns exist)
                sort_columns = ['ElapseIT_Client', 'ElapseIT_Project', 'ElapseIT_Person']
                available_sort_columns = [col for col in sort_columns if col in bidirectional_df.columns]
                if available_sort_columns:
                    bidirectional_df = bidirectional_df.sort_values(available_sort_columns)
                bidirectional_df.to_excel(writer, sheet_name='bidirectional_matches', index=False)
                
                # Format the bidirectional_matches sheet
                worksheet = writer.sheets['bidirectional_matches']
                format_excel_sheet(worksheet, bidirectional_df)
        
        # 2. ElapseIT no matches - show only ElapseIT data with MULTIMATCH concept
        if results['elapseit_no_matches']:
            print(f"  📋 Creating 'elapseit_no_matches' sheet with {len(results['elapseit_no_matches'])} entries")
            elapseit_no_data = []
            
            for key in results['elapseit_no_matches']:
                # Get ElapseIT data for this key
                elapseit_rows = elapseit_df[elapseit_df['Composite_Key'] == key]
                
                if not elapseit_rows.empty:
                    # Get unique projects
                    elapseit_projects = sorted(elapseit_rows['Project'].unique())
                    elapseit_project_list = '-'.join(elapseit_projects) if elapseit_projects else 'No projects'
                    
                    # Determine status based on number of projects
                    elapseit_project_count = len([p for p in elapseit_project_list.split('-') if p != 'No projects'])
                    
                    if elapseit_project_count > 1:
                        status = "MULTIMATCH"
                    else:
                        status = "NO MATCH"
                    
                    # Create consolidated row using first row
                    row_data = {}
                    
                    # Define the desired column order for ElapseIT
                    elapseit_columns = ['Person', 'Project', 'Client', 'From Date', 'To Date', 'HoursPerDay', 'BusinessDays', 'Composite_Key', 'Mapped_Composite_Key']
                    
                    # Add ElapseIT data with prefix in proper order
                    for col in elapseit_columns:
                        if col in elapseit_rows.columns:
                            if col == 'Project':
                                row_data[f'ElapseIT_{col}'] = elapseit_project_list
                            else:
                                row_data[f'ElapseIT_{col}'] = elapseit_rows.iloc[0][col]
                    
                    # Add status column
                    row_data['Status'] = status
                    
                    elapseit_no_data.append(row_data)
            
            if elapseit_no_data:
                elapseit_no_df = pd.DataFrame(elapseit_no_data)
                
                # Define the desired column order for ElapseIT no matches
                desired_columns = [
                    'ElapseIT_Person', 'ElapseIT_Project', 'ElapseIT_Client', 'ElapseIT_From Date', 
                    'ElapseIT_To Date', 'ElapseIT_HoursPerDay', 'ElapseIT_BusinessDays', 
                    'ElapseIT_Composite_Key', 'ElapseIT_Mapped_Composite_Key', 'Status'
                ]
                
                # Reorder columns to match desired order (only include columns that exist)
                available_columns = [col for col in desired_columns if col in elapseit_no_df.columns]
                elapseit_no_df = elapseit_no_df[available_columns]
                
                # Sort by ElapseIT_Client, ElapseIT_Project, ElapseIT_Person (if columns exist)
                sort_columns = ['ElapseIT_Client', 'ElapseIT_Project', 'ElapseIT_Person']
                available_sort_columns = [col for col in sort_columns if col in elapseit_no_df.columns]
                if available_sort_columns:
                    elapseit_no_df = elapseit_no_df.sort_values(available_sort_columns)
                elapseit_no_df.to_excel(writer, sheet_name='elapseit_no_matches', index=False)
                
                # Format the elapseit_no_matches sheet
                worksheet = writer.sheets['elapseit_no_matches']
                format_excel_sheet(worksheet, elapseit_no_df)
        
        # 3. Vision no matches - show only Vision data with MULTIMATCH concept
        if results['vision_no_matches']:
            print(f"  📋 Creating 'vision_no_matches' sheet with {len(results['vision_no_matches'])} entries")
            vision_no_data = []
            
            for key in results['vision_no_matches']:
                # Get Vision data for this key
                vision_rows = vision_df[vision_df['Composite_Key'] == key]
                
                if not vision_rows.empty:
                    # Get unique projects
                    vision_projects = sorted(vision_rows['project'].unique())
                    vision_project_list = '-'.join(vision_projects) if vision_projects else 'No projects'
                    
                    # Determine status based on number of projects
                    vision_project_count = len([p for p in vision_project_list.split('-') if p != 'No projects'])
                    
                    if vision_project_count > 1:
                        status = "MULTIMATCH"
                    else:
                        status = "NO MATCH"
                    
                    # Create consolidated row using first row
                    row_data = {}
                    
                    # Define the desired column order for Vision
                    vision_columns = ['employee', 'project', 'client', 'project_start_date', 'project_end_date', 'allocation_percent', 'Composite_Key', 'Mapped_Composite_Key']
                    
                    # Add Vision data with prefix in proper order
                    for col in vision_columns:
                        if col in vision_rows.columns:
                            if col == 'project':
                                row_data[f'Vision_{col}'] = vision_project_list
                            else:
                                row_data[f'Vision_{col}'] = vision_rows.iloc[0][col]
                    
                    # Add status column
                    row_data['Status'] = status
                    
                    vision_no_data.append(row_data)
            
            if vision_no_data:
                vision_no_df = pd.DataFrame(vision_no_data)
                
                # Define the desired column order for Vision no matches
                desired_columns = [
                    'Vision_employee', 'Vision_project', 'Vision_client', 'Vision_project_start_date',
                    'Vision_project_end_date', 'Vision_allocation_percent', 'Vision_Composite_Key', 
                    'Vision_Mapped_Composite_Key', 'Status'
                ]
                
                # Reorder columns to match desired order (only include columns that exist)
                available_columns = [col for col in desired_columns if col in vision_no_df.columns]
                vision_no_df = vision_no_df[available_columns]
                
                # Sort by Vision_client, Vision_project, Vision_employee (if columns exist)
                sort_columns = ['Vision_client', 'Vision_project', 'Vision_employee']
                available_sort_columns = [col for col in sort_columns if col in vision_no_df.columns]
                if available_sort_columns:
                    vision_no_df = vision_no_df.sort_values(available_sort_columns)
                vision_no_df.to_excel(writer, sheet_name='vision_no_matches', index=False)
                
                # Format the vision_no_matches sheet
                worksheet = writer.sheets['vision_no_matches']
                format_excel_sheet(worksheet, vision_no_df)
        
        # 4. Missing Employees sheet
        missing_employees_data = generate_missing_employees_data(results, client_mapping, month_year, employee_filter)
        if missing_employees_data:
            missing_employees_df = pd.DataFrame(missing_employees_data)
            # Sort by System, Employee, Project
            missing_employees_df = missing_employees_df.sort_values(['System', 'Employee', 'Project'])
            missing_employees_df.to_excel(writer, sheet_name='missing_employees', index=False)
            
            # Format the missing_employees sheet
            worksheet = writer.sheets['missing_employees']
            format_excel_sheet(worksheet, missing_employees_df)
            print(f"  📋 Created 'missing_employees' sheet with {len(missing_employees_data)} entries")
        else:
            # Create empty dataframe with columns
            empty_employees_df = pd.DataFrame(columns=['System', 'Employee', 'Project', 'Status', 'Month'])
            empty_employees_df.to_excel(writer, sheet_name='missing_employees', index=False)
            
            # Format the empty missing_employees sheet
            worksheet = writer.sheets['missing_employees']
            format_excel_sheet(worksheet, empty_employees_df)
            print(f"  📋 Created empty 'missing_employees' sheet")
        
        # 5. Missing Clients sheet
        missing_clients_data = generate_missing_clients_data(results, client_mapping, month_year, employee_filter)
        if missing_clients_data:
            missing_clients_df = pd.DataFrame(missing_clients_data)
            # Sort by System, Client
            missing_clients_df = missing_clients_df.sort_values(['System', 'Client'])
            missing_clients_df.to_excel(writer, sheet_name='missing_clients', index=False)
            
            # Format the missing_clients sheet
            worksheet = writer.sheets['missing_clients']
            format_excel_sheet(worksheet, missing_clients_df)
            print(f"  📋 Created 'missing_clients' sheet with {len(missing_clients_data)} entries")
        else:
            # Create empty dataframe with columns
            empty_clients_df = pd.DataFrame(columns=['System', 'Client', 'Status', 'Month'])
            empty_clients_df.to_excel(writer, sheet_name='missing_clients', index=False)
            
            # Format the empty missing_clients sheet
            worksheet = writer.sheets['missing_clients']
            format_excel_sheet(worksheet, empty_clients_df)
            print(f"  📋 Created empty 'missing_clients' sheet")
        
        # 6. Missing Projects sheet
        missing_projects_data = generate_missing_projects_data(results, month_year, employee_filter)
        if missing_projects_data:
            missing_projects_df = pd.DataFrame(missing_projects_data)
            # Sort by System, Project
            missing_projects_df = missing_projects_df.sort_values(['System', 'Project'])
            missing_projects_df.to_excel(writer, sheet_name='missing_projects', index=False)
            
            # Format the missing_projects sheet
            worksheet = writer.sheets['missing_projects']
            format_excel_sheet(worksheet, missing_projects_df)
            print(f"  📋 Created 'missing_projects' sheet with {len(missing_projects_data)} entries")
        else:
            # Create empty dataframe with columns
            empty_projects_df = pd.DataFrame(columns=['System', 'Project', 'Status', 'Month'])
            empty_projects_df.to_excel(writer, sheet_name='missing_projects', index=False)
            
            # Format the empty missing_projects sheet
            worksheet = writer.sheets['missing_projects']
            format_excel_sheet(worksheet, empty_projects_df)
            print(f"  📋 Created empty 'missing_projects' sheet")
        
        # 7. Combined Allocations sheet - Human-readable data from both systems
        combined_allocations_data = generate_combined_allocation_data(results, elapseit_df, vision_df, client_mapping, month_year, employee_filter)
        if combined_allocations_data:
            combined_allocations_df = pd.DataFrame(combined_allocations_data)
            # Sort by System, Client, Project, Person/Employee
            combined_allocations_df = combined_allocations_df.sort_values(['System', 'Client', 'Project', 'Person/Employee'])
            combined_allocations_df.to_excel(writer, sheet_name='combined_allocations', index=False)
            
            # Format the combined_allocations sheet
            worksheet = writer.sheets['combined_allocations']
            format_excel_sheet(worksheet, combined_allocations_df)
            print(f"  📋 Created 'combined_allocations' sheet with {len(combined_allocations_data)} entries")
        else:
            # Create empty dataframe with columns
            empty_allocations_df = pd.DataFrame(columns=['System', 'Client', 'Project', 'Person/Employee', 'Mapped_Client', 'From_Date', 'To_Date', 'Hours_Per_Day', 'Business_Days', 'Allocation_Type', 'Month'])
            empty_allocations_df.to_excel(writer, sheet_name='combined_allocations', index=False)
            
            # Format the empty combined_allocations sheet
            worksheet = writer.sheets['combined_allocations']
            format_excel_sheet(worksheet, empty_allocations_df)
            print(f"  📋 Created empty 'combined_allocations' sheet")
    
    print(f"✅ Main output Excel file created: {output_file}")

def generate_missing_employees_data(results, client_mapping, month_year, employee_filter=None):
    """Generate missing employees data for the main output"""
    missing_employees_data = []
    
    # Get the dataframes
    elapseit_df = results['elapseit_df']
    vision_df = results['vision_df']
    
    # Get complete employee lists from both systems (not just those with allocations)
    vision_employees_df = None
    elapseit_people_df = None
    
    # For API+DB mode, extract from existing data; for CSV mode, read files
    if 'elapseit_data' in results and 'people' in results['elapseit_data']:
        elapseit_people_df = results['elapseit_data']['people']
        print(f"  Using ElapseIT people data from API/processed data")
    else:
        elapseit_people_df = read_csv_file("../data/elapseIT_data/people.csv")
        if elapseit_people_df is not None:
            print(f"  Using ElapseIT people data from CSV file")
    
    # For Vision employees, get full employee list from database or CSV
    if 'elapseit_data' in results:
        # API+DB mode: get employees from database
        from vision_db_client import create_vision_client
        vision_client = create_vision_client()
        if vision_client and vision_client.test_connection():
            # Get simulation_id from results
            simulation_id = results.get('simulation_id', 28)  # Default to 28
            vision_employees_df = vision_client.get_employees(simulation_id)
            print(f"  Using Vision employee data from database (simulation_id={simulation_id})")
        else:
            print(f"  Failed to connect to Vision database, skipping missing employees analysis")
            return []
    else:
        # CSV mode: read from file
        vision_employees_df = read_csv_file("../data/vision_data/employees.csv")
        if vision_employees_df is not None:
            print(f"  Using Vision employee data from CSV file")
    
    if vision_employees_df is not None and elapseit_people_df is not None:
        # Parse the month of interest to get the start date
        month_year = month_year.strip()
        month_parts = month_year.split()
        if len(month_parts) == 2:
            month_name = month_parts[0]
            year = int(month_parts[1])
            
            # Convert month name to number
            month_abbrev_to_full = {
                'Jan': 'January', 'Feb': 'February', 'Mar': 'March', 'Apr': 'April',
                'May': 'May', 'Jun': 'June', 'Jul': 'July', 'Aug': 'August',
                'Sep': 'September', 'Oct': 'October', 'Nov': 'November', 'Dec': 'December'
            }
            
            if month_name in month_abbrev_to_full:
                month_name = month_abbrev_to_full[month_name]
            
            # Get the first day of the month of interest
            month_start_date = pd.to_datetime(f"{month_name} 1, {year}")
            
            # Get all Vision employees (excluding those with end date prior to month of interest)
            vision_employees = set()
            for _, row in vision_employees_df.iterrows():
                if pd.isna(row['deleted_at']):  # Only active employees
                    # Check if employee has an end date and if it's before the month of interest
                    end_date = row.get('end_date')
                    if pd.isna(end_date) or pd.to_datetime(end_date) >= month_start_date:
                        full_name = f"{row['first_name']} {row['last_name']}".strip()
                        vision_employees.add(full_name)
            
            # Get all ElapseIT people (excluding those with end date prior to month of interest)
            elapseit_employees = set()
            for _, row in elapseit_people_df.iterrows():
                if not row['IsArchived']:  # Only active people
                    # Check if person has an end date and if it's before the month of interest
                    # Note: ElapseIT might not have end_date field, so we'll check if it exists
                    if 'end_date' in row and pd.notna(row['end_date']):
                        end_date = pd.to_datetime(row['end_date'])
                        if end_date >= month_start_date:
                            # SECOND PASS: Exclude employees where HasLicense is FALSE (resigned employees)
                            if row.get('HasLicense', True):  # Default to True if field doesn't exist
                                full_name = f"{row['FirstName']} {row['LastName']}".strip()
                                elapseit_employees.add(full_name)
                    else:
                        # No end date, so include them (but still check HasLicense)
                        # SECOND PASS: Exclude employees where HasLicense is FALSE (resigned employees)
                        if row.get('HasLicense', True):  # Default to True if field doesn't exist
                            full_name = f"{row['FirstName']} {row['LastName']}".strip()
                            elapseit_employees.add(full_name)
            
            # Vision employees not in ElapseIT
            vision_only_employees = vision_employees - elapseit_employees
            for employee in sorted(vision_only_employees):
                # Get all projects for this employee from Vision (filtered data)
                employee_projects = vision_df[vision_df['employee'] == employee]['project'].unique()
                project_list = ', '.join(sorted(employee_projects)) if len(employee_projects) > 0 else 'No allocations in current month'
                
                missing_employees_data.append({
                    'System': 'Vision',
                    'Employee': employee,
                    'Project': project_list,
                    'Status': 'Found in Vision but not in ElapseIT',
                    'Month': month_year
                })
            
            # ElapseIT employees not in Vision
            elapseit_only_employees = elapseit_employees - vision_employees
            for employee in sorted(elapseit_only_employees):
                # SECOND PASS: Exclude 'BACKLOG ALLOCATIONS' (leave adjustments)
                if employee != 'BACKLOG ALLOCATIONS':
                    # Get all projects for this employee from ElapseIT (filtered data)
                    employee_projects = elapseit_df[elapseit_df['Person'] == employee]['Project'].unique()
                    project_list = ', '.join(sorted(employee_projects)) if len(employee_projects) > 0 else 'No allocations in current month'
                    
                    missing_employees_data.append({
                        'System': 'ElapseIT',
                        'Employee': employee,
                        'Project': project_list,
                        'Status': 'Found in ElapseIT but not in Vision',
                        'Month': month_year
                    })
    
    return missing_employees_data

def generate_missing_clients_data(results, client_mapping, month_year, employee_filter=None):
    """Generate missing clients data for the main output"""
    missing_clients_data = []
    
    # Get the dataframes
    elapseit_df = results['elapseit_df']
    vision_df = results['vision_df']
    
    # Read the clients data for true client comparison - adapt for API+DB mode
    elapseit_clients_df = None
    vision_clients_df = None
    vision_projects_df = None
    
    # For ElapseIT: Try to get from the processed data first, fallback to CSV
    if 'elapseit_data' in results and 'clients' in results['elapseit_data']:
        elapseit_clients_df = results['elapseit_data']['clients']
    else:
        elapseit_clients_df = read_csv_file("../data/elapseIT_data/clients.csv")
    
    # For Vision: Try to get from database, fallback to CSV
    if 'elapseit_data' in results:  # API+DB mode
        # Get full client and project lists from database
        from vision_db_client import create_vision_client
        vision_client = create_vision_client()
        if vision_client and vision_client.test_connection():
            simulation_id = results.get('simulation_id', 28)
            vision_clients_df = vision_client.get_clients(simulation_id)
            vision_projects_df = vision_client.get_projects(simulation_id)
        else:
            # Fallback to CSV
            vision_clients_df = read_csv_file("../data/vision_data/clients.csv")
            vision_projects_df = read_csv_file("../data/vision_data/projects.csv")
    else:
        # CSV mode
        vision_clients_df = read_csv_file("../data/vision_data/clients.csv")
        vision_projects_df = read_csv_file("../data/vision_data/projects.csv")
    
    if elapseit_clients_df is not None and vision_clients_df is not None:
        # Filter out archived clients (IsArchived=TRUE) as these represent clients created in error
        elapseit_clients_df = elapseit_clients_df[elapseit_clients_df['IsArchived'] == False] if 'IsArchived' in elapseit_clients_df.columns else elapseit_clients_df
        vision_clients_df = vision_clients_df[vision_clients_df['IsArchived'] == False] if 'IsArchived' in vision_clients_df.columns else vision_clients_df
        
        # Get all clients from both systems (after filtering archived clients)
        elapseit_clients = set(elapseit_clients_df['Name'].unique())
        vision_clients = set(vision_clients_df['name'].unique())
        
        # Map ElapseIT clients to Vision clients using Nexa
        mapped_elapseit_clients = set()
        for elapseit_client in elapseit_clients:
            mapped_client = client_mapping.get(elapseit_client, elapseit_client)
            mapped_elapseit_clients.add(mapped_client)
        
        # For ElapseIT clients not in Vision, we need to check if their mapped Vision client exists
        elapseit_only_clients = set()
        for elapseit_client in elapseit_clients:
            mapped_vision_client = client_mapping.get(elapseit_client, elapseit_client)
            if mapped_vision_client not in vision_clients:
                elapseit_only_clients.add(elapseit_client)
        
        # For Vision clients not in ElapseIT, we need to check if any ElapseIT client maps to them
        # OR if the Vision client exists in ElapseIT with the same name (no mapping needed)
        vision_only_clients = set()
        for vision_client in vision_clients:
            # Check if any ElapseIT client maps to this Vision client
            has_mapping = False
            for elapseit_client, mapped_client in client_mapping.items():
                if mapped_client == vision_client and elapseit_client in elapseit_clients:
                    has_mapping = True
                    break
            
            # Also check if the Vision client exists in ElapseIT with the same name (no mapping needed)
            if vision_client in elapseit_clients:
                has_mapping = True
                
            if not has_mapping:
                # Only include this client if it has projects
                if vision_projects_df is not None:
                    # Check if this client has any projects
                    if 'client_id' in vision_projects_df.columns and 'id' in vision_clients_df.columns:
                        # Database mode with proper relationships
                        client_info = vision_clients_df[vision_clients_df['name'] == vision_client]
                        if not client_info.empty:
                            client_id = client_info.iloc[0]['id']
                            client_projects = vision_projects_df[vision_projects_df['client_id'] == client_id]
                            if len(client_projects) > 0:
                                vision_only_clients.add(vision_client)
                    else:
                        # CSV mode fallback
                        vision_only_clients.add(vision_client)
        
        # Vision clients not in ElapseIT (after mapping) - SECOND PASS CHECK
        for client in sorted(vision_only_clients):
            # Second pass: Check if this Vision client has any projects and running projects in the current month
            has_projects = False
            has_running_projects = False
            
            # Get all projects for this client from Vision data (filtered for current month)
            client_projects = vision_df[vision_df['client'] == client]
            
            if not client_projects.empty:
                has_projects = True
                # Check if any of these projects are running in the current month
                # A project is running if it has allocations in the current month
                running_projects = client_projects[client_projects['employee'].notna()]
                has_running_projects = len(running_projects) > 0
            
            # If no projects found in filtered data, check the unfiltered projects data
            if not has_projects:
                # Check the unfiltered projects data to check if this client has any projects
                if vision_projects_df is not None and 'client_id' in vision_projects_df.columns and 'id' in vision_clients_df.columns:
                    # Find the client ID for this client
                    client_info = vision_clients_df[vision_clients_df['name'] == client]
                    if not client_info.empty:
                        client_id = client_info.iloc[0]['id']
                        # Check if this client has any projects in the unfiltered data
                        client_projects_unfiltered = vision_projects_df[vision_projects_df['client_id'] == client_id]
                        has_projects = len(client_projects_unfiltered) > 0
            
            # Determine the status based on whether there are projects and running projects
            if has_projects:
                if has_running_projects:
                    # Client has running projects in current month but doesn't exist in ElapseIT
                    # Check if this client exists in ElapseIT (after mapping)
                    has_elapseit_mapping = False
                    for elapseit_client, mapped_client in client_mapping.items():
                        if mapped_client == client and elapseit_client in elapseit_clients:
                            has_elapseit_mapping = True
                            break
                    
                    # Also check if the Vision client exists in ElapseIT with the same name (no mapping needed)
                    if client in elapseit_clients:
                        has_elapseit_mapping = True
                    
                    if has_elapseit_mapping:
                        status = "Found in Vision but not in ElapseIT (after mapping)"
                    else:
                        status = "Create in ElapseIT"
                else:
                    # Client has projects but no running projects in current month
                    status = "Project not currently running"
            else:
                # Check if this client exists in ElapseIT (after mapping)
                # If it doesn't exist in ElapseIT at all, it should be "Create in ElapseIT"
                # If it exists but has no running projects, it's "Found in Vision but not in ElapseIT (after mapping)"
                
                # Check if any ElapseIT client maps to this Vision client
                has_elapseit_mapping = False
                for elapseit_client, mapped_client in client_mapping.items():
                    if mapped_client == client and elapseit_client in elapseit_clients:
                        has_elapseit_mapping = True
                        break
                
                # Also check if the Vision client exists in ElapseIT with the same name (no mapping needed)
                if client in elapseit_clients:
                    has_elapseit_mapping = True
                
                if has_elapseit_mapping:
                    status = "Found in Vision but not in ElapseIT (after mapping)"
                else:
                    status = "Create in ElapseIT"
        
            missing_clients_data.append({
                'System': 'Vision',
                'Client': client,
                'Status': status,
                'Month': month_year
            })
        
        # ElapseIT clients not in Vision (after mapping)
        for client in sorted(elapseit_only_clients):
            missing_clients_data.append({
                'System': 'ElapseIT',
                'Client': client,
                'Status': 'Found in ElapseIT but not in Vision (after mapping)',
                'Month': month_year
            })
    
    return missing_clients_data

def generate_missing_projects_data(results, month_year, employee_filter=None):
    """Generate missing projects data for the main output"""
    missing_projects_data = []
    
    # Get the dataframes
    elapseit_df = results['elapseit_df']
    vision_df = results['vision_df']
    
    # Get unique projects from both systems
    elapseit_projects = set(elapseit_df['Project'].unique())
    vision_projects = set(vision_df['project'].unique())
    
    # Vision projects not in ElapseIT
    vision_only_projects = vision_projects - elapseit_projects
    for project in sorted(vision_only_projects):
        missing_projects_data.append({
            'System': 'Vision',
            'Project': project,
            'Status': 'Found in Vision but not in ElapseIT',
            'Month': month_year
        })
    
    # ElapseIT projects not in Vision
    elapseit_only_projects = elapseit_projects - vision_projects
    for project in sorted(elapseit_only_projects):
        missing_projects_data.append({
            'System': 'ElapseIT',
            'Project': project,
            'Status': 'Found in ElapseIT but not in Vision',
            'Month': month_year
        })
    
    return missing_projects_data

def filter_data_by_employee(elapseit_df, vision_df, employee_name):
    """Filter dataframes to include only data for a specific employee"""
    if not employee_name:
        return elapseit_df, vision_df
    
    print(f"  🔍 Filtering data for employee: {employee_name}")
    
    # Filter ElapseIT data
    filtered_elapseit_df = elapseit_df[elapseit_df['Person'] == employee_name].copy()
    print(f"    ElapseIT entries for {employee_name}: {len(filtered_elapseit_df)}")
    
    # Filter Vision data
    filtered_vision_df = vision_df[vision_df['employee'] == employee_name].copy()
    print(f"    Vision entries for {employee_name}: {len(filtered_vision_df)}")
    
    return filtered_elapseit_df, filtered_vision_df

def generate_combined_allocation_data(results, elapseit_df, vision_df, client_mapping, month_year, employee_filter=None):
    """Generate combined allocation data showing human-readable data from both systems"""
    combined_data = []
    
    print(f"  📋 Creating 'combined_allocations' sheet with detailed allocation data")
    
    # Process ElapseIT allocations
    for _, row in elapseit_df.iterrows():
        person = row['Person']
        client = row['Client']
        project = row['Project']
        from_date = row['From Date']
        to_date = row['To Date']
        hours_per_day = row['HoursPerDay']
        business_days = row['BusinessDays']
        
        # Get mapped Vision client
        mapped_vision_client = client_mapping.get(client, client)
        
        combined_data.append({
            'System': 'ElapseIT',
            'Client': client,
            'Project': project,
            'Person/Employee': person,
            'Mapped_Client': mapped_vision_client,
            'From_Date': from_date,
            'To_Date': to_date,
            'Hours_Per_Day': hours_per_day,
            'Business_Days': business_days,
            'Allocation_Type': 'Hours',
            'Month': month_year
        })
    
    # Process Vision allocations
    for _, row in vision_df.iterrows():
        employee = row['employee']
        client = row['client']
        project = row['project']
        start_date = row['project_start_date']
        end_date = row['project_end_date']
        allocation_percent = row['allocation_percent']
        
        # Get mapped ElapseIT client
        reverse_mapped_client = None
        for elapseit_client, vision_client in client_mapping.items():
            if vision_client == client:
                reverse_mapped_client = elapseit_client
                break
        
        combined_data.append({
            'System': 'Vision',
            'Client': client,
            'Project': project,
            'Person/Employee': employee,
            'Mapped_Client': reverse_mapped_client or 'No mapping',
            'From_Date': start_date,
            'To_Date': end_date,
            'Hours_Per_Day': allocation_percent,
            'Business_Days': 'N/A',
            'Allocation_Type': 'Percentage',
            'Month': month_year
        })
    
    return combined_data

def main():
    """Main function to analyze all three files and create mappings"""
    
    print("🚀 Enhanced Project Mapping Analysis with API Support")
    print("=" * 60)
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Enhanced Project Mapping Analysis with API Support')
    parser.add_argument('--month', type=str, default="July 2025", help='Month to analyze (e.g., "July 2025")')
    parser.add_argument('--debug', action='store_true', help='Enable debug output (skips Excel file creation)')
    parser.add_argument('--employee', type=str, help='Filter output to specific employee (e.g., "John Smith")')
    parser.add_argument('--quiet', action='store_true', help='Suppress verbose output')
    parser.add_argument('--csv', action='store_true', help='Use CSV files instead of ElapseIT API')
    parser.add_argument('--vision-csv', action='store_true', help='Use CSV files instead of Vision PostgreSQL database')
    parser.add_argument('--simulation-id', type=int, help='Vision simulation ID to filter by (default: maximum available)')
    args = parser.parse_args()
    
    print(f"🔧 Configuration:")
    print(f"   ElapseIT Source: {'📁 CSV Files' if args.csv else '🌐 API'}")
    print(f"   Vision Source: {'📁 CSV Files' if args.vision_csv else '🗄️ PostgreSQL DB'}")
    if not args.vision_csv:
        if args.simulation_id:
            print(f"   Simulation ID: {args.simulation_id}")
        else:
            print(f"   Simulation ID: Auto-detect (maximum available)")
    print(f"   Month: {args.month}")
    print(f"   Debug Mode: {'✅ Enabled' if args.debug else '❌ Disabled'}")
    if args.employee:
        print(f"   Employee Filter: {args.employee}")
    
    # Read field mappings configuration
    print("\n📋 Reading field mappings configuration...")
    field_mappings_config = read_field_mappings()
    
    # Get ElapseIT data (either from API or files)
    if args.csv:
        elapseit_data = get_elapseit_data_from_files()
    else:
        elapseit_data = get_elapseit_data_from_api()
    
    if elapseit_data is None:
        print("❌ Failed to retrieve ElapseIT data. Exiting.")
        return
    
    # Read Vision data (from database or CSV files)
    if args.vision_csv:
        print("\n📁 Reading Vision data from CSV files...")
        vision_allocations_df = read_csv_file("../data/vision_data/allocations.csv")
        vision_clients_df = read_csv_file("../data/vision_data/clients.csv")
        vision_employees_df = read_csv_file("../data/vision_data/employees.csv")
        vision_projects_df = read_csv_file("../data/vision_data/projects.csv")
    else:
        sim_id_display = args.simulation_id if args.simulation_id else "auto-detect"
        print(f"\n🗄️ Reading Vision data from database (simulation_id={sim_id_display})...")
        # Calculate date range for database query
        import datetime as dt
        date_obj = dt.datetime.strptime(args.month, "%B %Y")
        month = date_obj.month
        year = date_obj.year
        start_date = f"{year}-{month:02d}-01"
        end_date = f"{year}-{month + 1:02d}-01" if month < 12 else f"{year + 1}-01-01"
        
        print(f"📅 Date range for query: {start_date} to {end_date}")
        vision_allocations_df = get_vision_data_from_database(start_date, end_date, args.simulation_id)
        # For database mode, we don't need separate client/employee/project files as they're joined in the query
        vision_clients_df = None
        vision_employees_df = None  
        vision_projects_df = None
    
    # Read Mapper file
    mapper_df = read_excel_file("../config/Mapper.xlsx")
    
    # Check if all required data was read successfully
    vision_data_ok = vision_allocations_df is not None
    if args.vision_csv:
        # For CSV mode, we need all files
        vision_data_ok = (vision_data_ok and vision_clients_df is not None and
                         vision_employees_df is not None and vision_projects_df is not None)
    
    if vision_data_ok and mapper_df is not None:
        
        print("✅ All required files read successfully")
        
        # Print data structure analysis
        print("\n" + "="*50)
        print("DATA STRUCTURE ANALYSIS")
        print("="*50)
        print(f"Vision Allocations: {len(vision_allocations_df)} rows, {len(vision_allocations_df.columns)} columns")
        if args.vision_csv:
            print(f"Vision Clients: {len(vision_clients_df)} rows, {len(vision_clients_df.columns)} columns")
            print(f"Vision Employees: {len(vision_employees_df)} rows, {len(vision_employees_df.columns)} columns")
            print(f"Vision Projects: {len(vision_projects_df)} rows, {len(vision_projects_df.columns)} columns")
        else:
            # Get the actual simulation ID that was used (will be set later in results)
            sim_id_display = args.simulation_id if args.simulation_id else "auto-detect"
            print(f"Vision data source: PostgreSQL database (simulation_id={sim_id_display})")
        print(f"ElapseIT Allocations: {len(elapseit_data['allocations'])} rows, {len(elapseit_data['allocations'].columns)} columns")
        print(f"ElapseIT Clients: {len(elapseit_data['clients'])} rows, {len(elapseit_data['clients'].columns)} columns")
        print(f"ElapseIT People: {len(elapseit_data['people'])} rows, {len(elapseit_data['people'].columns)} columns")
        print(f"ElapseIT Projects: {len(elapseit_data['projects'])} rows, {len(elapseit_data['projects'].columns)} columns")
        print(f"Mapper: {len(mapper_df)} rows, {len(mapper_df.columns)} columns")
        
        # Process the data
        print("\n🔄 Processing data...")
        elapseit_df = process_elapseit_csv_data(
            elapseit_data['allocations'], 
            elapseit_data['clients'], 
            elapseit_data['people'], 
            elapseit_data['projects']
        )
        if args.vision_csv:
            # For CSV mode, process the separate files
            vision_df = process_vision_csv_data(
                vision_allocations_df, 
                vision_clients_df, 
                vision_employees_df, 
                vision_projects_df
            )
        else:
            # For database mode, the data is already joined and formatted
            vision_df = vision_allocations_df
        
        # Create client mapping
        client_mapping = create_client_mapping(mapper_df)
        
        month_year = args.month
        
        # Filter projects by month
        print(f"\n{'='*60}")
        print(f"FILTERING PROJECTS FOR {month_year.upper()}")
        print(f"{'='*60}")
        
        vision_df, elapseit_df = filter_projects_by_month(vision_df, elapseit_df, month_year)
        
        # Filter by employee if specified
        if args.employee:
            elapseit_df, vision_df = filter_data_by_employee(elapseit_df, vision_df, args.employee)
        
        # Perform bidirectional composite key matching
        results = perform_bidirectional_composite_key_matching(elapseit_df, vision_df, client_mapping, field_mappings_config, elapseit_data)
        
        # Add simulation_id to results for downstream functions
        if not args.vision_csv:
            # If no simulation_id was provided, we need to get the actual one used
            if args.simulation_id:
                results['simulation_id'] = args.simulation_id
                print(f"📋 Using provided simulation_id: {args.simulation_id}")
            else:
                # Get the actual simulation_id that was used (auto-detected)
                actual_sim_id = get_max_simulation_id()
                results['simulation_id'] = actual_sim_id
                print(f"📋 Using auto-detected simulation_id: {actual_sim_id}")
        
        # Print detailed matching commentary if debug mode is enabled
        print_detailed_matching_commentary(results, client_mapping, args.debug, field_mappings_config)
        
        # Create main output file (skip if debug mode is enabled)
        if not args.debug:
            # Use different filename for CSV mode to avoid overwriting API/DB results
            if args.csv or args.vision_csv:
                output_filename = f"mapping_analysis_{month_year.replace(' ', '_')}_CSV.xlsx"
            else:
                output_filename = f"mapping_analysis_{month_year.replace(' ', '_')}_API.xlsx"
            create_main_output_file(results, elapseit_df, vision_df, client_mapping, month_year, field_mappings_config, args.employee, output_filename)
        else:
            print(f"\n📋 Skipping Excel output file creation (debug mode enabled)")
        
        # Print summary
        print_bidirectional_summary(results, month_year, args.employee)
        
        print(f"\n{'='*60}")
        print(f"ANALYSIS COMPLETE")
        print(f"{'='*60}")
        print(f"Data Source: {'ElapseIT CSV Files' if args.csv else 'ElapseIT API'}")
        if not args.vision_csv:
            actual_sim_id = results.get('simulation_id', 'Unknown')
            print(f"Vision Simulation ID: {actual_sim_id}")
        print(f"Primary method: Bidirectional composite key matching")
        print(f"Month analyzed: {month_year}")
        if args.employee:
            print(f"Employee filter: {args.employee}")
        print(f"Exact matches found: {len(results['bidirectional_matches'])}")
        print(f"Vision-only entries: {len(results['vision_no_matches'])}")
        print(f"ElapseIT-only entries: {len(results['elapseit_no_matches'])}")
        print(f"Client mappings: {len(client_mapping)}")
        print(f"\nResults saved to 'output/mapping_results' folder")
        
    else:
        print("❌ Error: Could not read one or more required files")
        print("Please ensure all required files are present:")
        if args.vision_csv:
            print("- data/vision_data/allocations.csv")
            print("- data/vision_data/clients.csv")
            print("- data/vision_data/employees.csv")
            print("- data/vision_data/projects.csv")
        else:
            print("- Valid Vision database connection in config.py")
        print("- config/Mapper.xlsx")
        if args.csv:
            print("- data/elapseIT_data/allocations.csv")
            print("- data/elapseIT_data/clients.csv")
            print("- data/elapseIT_data/people.csv")
            print("- data/elapseIT_data/projects.csv")
        else:
            print("- Valid ElapseIT API credentials in config.py")
            print("- Internet connection for API access")

if __name__ == "__main__":
    main() 