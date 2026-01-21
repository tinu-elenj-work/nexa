import pandas as pd

def create_field_mappings():
    """Create the field_mappings.xlsx file with configurable field mappings"""
    
    # Field Mappings sheet
    field_mappings_data = {
        'Field_Mapping_ID': ['FM001', 'FM002', 'FM003'],
        'ElapseIT_Field': ['Person', 'Project', 'Client'],
        'Vision_Field': ['employee', 'project', 'client'],
        'Description': [
            'Person/Employee field mapping',
            'Project field mapping', 
            'Client field mapping'
        ],
        'Is_Active': ['Yes', 'Yes', 'Yes']
    }
    
    # Composite Keys sheet
    composite_keys_data = {
        'Composite_Key_ID': ['CK001', 'CK002'],
        'System': ['ElapseIT', 'Vision'],
        'Composite_Key_Formula': ['Person.Client', 'employee.client'],
        'Description': [
            'ElapseIT composite key: Person + Client',
            'Vision composite key: employee + client'
        ],
        'Is_Active': ['Yes', 'Yes']
    }
    
    # Client Extraction sheet - Updated to use direct client fields
    client_extraction_data = {
        'Rule_ID': ['CE001', 'CE002'],
        'System': ['ElapseIT', 'Vision'],
        'Field_Name': ['Client', 'client'],
        'Extraction_Method': ['Direct field', 'Direct field'],
        'Extraction_Formula': ['Client', 'client'],
        'Description': [
            'Use Client field directly from ElapseIT data',
            'Use client field directly from Vision data'
        ],
        'Example_Input': ['AKBANK', 'AKB'],
        'Example_Output': ['AKBANK', 'AKB'],
        'Is_Active': ['Yes', 'Yes']
    }
    
    # Multimatcher sheet - for second pass project mapping
    multimatcher_data = {
        'Rule_ID': ['MM001', 'MM002', 'MM003'],
        'ElapseIT_Project': ['AKBANK|CVA', 'AKBANK|MINI', 'AKBANK|SUPP'],
        'Vision_Project': ['AKB|CHANGE|MX|FIX|CVA', 'AKB|RUN|MX|FIX|F2B', 'AKB|SUPP|MX|FIX|F2B'],
        'Description': [
            'Map AKBANK|CVA from ElapseIT to AKB|CHANGE|MX|FIX|CVA in Vision',
            'Map AKBANK|MINI from ElapseIT to AKB|RUN|MX|FIX|F2B in Vision',
            'Map AKBANK|SUPP from ElapseIT to AKB|SUPP|MX|FIX|F2B in Vision'
        ],
        'Is_Active': ['Yes', 'Yes', 'Yes']
    }
    
    # Instructions sheet
    instructions_data = {
        'Section': [
            'Field Mappings',
            'Field Mappings',
            'Field Mappings',
            'Composite Keys',
            'Composite Keys',
            'Client Extraction',
            'Client Extraction',
            'Multimatcher',
            'Multimatcher',
            'General Notes'
        ],
        'Instruction': [
            'Map ElapseIT Person field to Vision employee field',
            'Map ElapseIT Project field to Vision project field',
            'Map ElapseIT Client field to Vision client field',
            'ElapseIT composite key combines Person and Client fields',
            'Vision composite key combines employee and client fields',
            'ElapseIT uses Client field directly (no extraction needed)',
            'Vision uses client field directly (no extraction needed)',
            'Second pass: Break down MULTIMATCH entries into individual MATCH entries',
            'Map specific ElapseIT projects to specific Vision projects',
            'All mappings are configurable via this Excel file'
        ]
    }
    
    # Create Excel file with multiple sheets
    with pd.ExcelWriter('field_mappings.xlsx', engine='openpyxl') as writer:
        pd.DataFrame(field_mappings_data).to_excel(writer, sheet_name='Field_Mappings', index=False)
        pd.DataFrame(composite_keys_data).to_excel(writer, sheet_name='Composite_Keys', index=False)
        pd.DataFrame(client_extraction_data).to_excel(writer, sheet_name='Client_Extraction', index=False)
        pd.DataFrame(multimatcher_data).to_excel(writer, sheet_name='Multimatcher', index=False)
        pd.DataFrame(instructions_data).to_excel(writer, sheet_name='Instructions', index=False)
    
    print("field_mappings.xlsx created successfully!")
    print("\nSheets created:")
    print("- Field_Mappings: Maps field names between systems")
    print("- Composite_Keys: Defines composite key formulas")
    print("- Client_Extraction: Defines how to extract client information")
    print("- Multimatcher: Second pass project mapping rules")
    print("- Instructions: Usage instructions")

if __name__ == "__main__":
    create_field_mappings() 